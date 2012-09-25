#!/usr/bin/env python
# 
# LSST Data Management System
# Copyright 2008, 2009, 2010 LSST Corporation.
# 
# This product includes software developed by the
# LSST Project (http://www.lsst.org/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the LSST License Statement and 
# the GNU General Public License along with this program.  If not, 
# see <http://www.lsstcorp.org/LegalNotices/>.
#

from __future__ import with_statement
import sys, os, os.path, shutil, subprocess
import optparse, traceback, time
from datetime import datetime
import lsst.pex.config as pexConfig
from string import Template
from TemplateWriter import TemplateWriter
from CondorConfig import CondorConfig
from CondorInfoConfig import CondorInfoConfig
import eups
from EnvString import EnvString

class Configurator(object):
    def __init__(self, opts):
        self.opts = opts

        self.defaults = {}

        configFileName = "$HOME/.lsst/condor-info.py"
        fileName = EnvString.resolve(configFileName)

        condorInfoConfig = CondorInfoConfig()
        condorInfoConfig.load(fileName)

        self.platform = self.opts.platform


        # Look up the user's name and home directory in the $HOME//.lsst/condor-info.py file
        # If the platform is lsst, and the user_name or user_home is not in there, then default to
        # user running this command and the value of $HOME, respectively.
        user_name = None
        user_home = None
        for name in condorInfoConfig.platform.keys():
            if name == self.platform:
                user_name = condorInfoConfig.platform[name].user.name
                user_home = condorInfoConfig.platform[name].user.home

        if self.platform == "lsst":
            if user_name is None:
                user_name = os.getlogin()
            if user_home is None:
                user_home = os.getenv('HOME')

        if user_name is None:
            raise RuntimeError("error: %s does not specify user name for platform %s" % (configFileName, self.platform))
        if user_home is None:
            raise RuntimeError("error: %s does not specify user home for platform %s" % (configFileName, self.platform))
        
            

        self.commandLineDefaults = {}
        self.commandLineDefaults["USER_NAME"] = user_name
        self.commandLineDefaults["USER_HOME"] = user_home
        
        self.commandLineDefaults["DEFAULT_ROOT"]  = self.opts.defaultRoot
        self.commandLineDefaults["LOCAL_SCRATCH"] = self.opts.localScratch
        self.commandLineDefaults["DATA_DIRECTORY"] = self.opts.dataDirectory
        self.commandLineDefaults["IDS_PER_JOB"] = self.opts.idsPerJob
        if self.opts.nodeSet is None:
            self.commandLineDefaults["NODE_SET"] = ""
        else:
            self.commandLineDefaults["NODE_SET"] = self.opts.nodeSet
        self.commandLineDefaults["INPUT_DATA_FILE"] = self.opts.inputDataFile
        self.commandLineDefaults["FILE_SYSTEM_DOMAIN"] = self.opts.fileSystemDomain
        self.commandLineDefaults["EUPS_PATH"] = self.opts.eupsPath

        # override user name, if given
        if self.opts.user_name is not None:
            self.commandLineDefaults["USER_NAME"] = self.opts.user_name
        
        # override user home, if given
        if self.opts.user_home is not None:
            self.commandLineDefaults["USER_HOME"] = self.opts.user_home

        if self.opts.runid is not None:
            self.runid = self.opts.runid
        else:
            self.runid = self.createRunId()
        
        self.commandLineDefaults["COMMAND"] = self.opts.command
        if self.commandLineDefaults["INPUT_DATA_FILE"] is not None:
            self.commandLineDefaults["COMMAND"] = self.commandLineDefaults["COMMAND"]+" ${id_option}"

        self.outputFileName = "/tmp/%s_config.py" % (self.runid)
        
    def getGenericConfigFileName(self):
        executePkgDir = eups.productDir("ctrl_execute")
        genericConfigName = None
        if (self.opts.setup == None) and (self.platform == "lsst"):
            genericConfigName = os.path.join(executePkgDir, "etc", "templates", "config_with_getenv.py.template")
        else:
            genericConfigName = os.path.join(executePkgDir, "etc", "templates", "config_with_setups.py.template")
        return genericConfigName

    def createRunId(self):
        now = datetime.now()
        runid = "%s_%02d_%02d%02d_%02d%02d%02d" % (os.getlogin(), now.year, now.month, now.day, now.hour, now.minute, now.second)
        return runid

    def getSetupPackages(self):
        e = eups.Eups()
        setupProducts = e.getSetupProducts()
        a = ""

        # create a new list will all products and versions
        allProducts = {}
        for i in setupProducts:
            allProducts[i.name] = i.version

        # replace any existing products that we saw on the command line, adding
        # them if they're not already there.
        if self.opts.setup is not None:
            for i, pkg in enumerate(self.opts.setup):
                name = pkg[0]
                version = pkg[1]
                print "name = %s, version = %s" % (name, version)
                allProducts[name] = version

        # write out all products, except those that are setup locally.
        for name in allProducts:
            version = allProducts[name]
            if version.startswith("LOCAL:") == False:
                a = a + "setup -j %s %s\\n\\\n" % (name, version)
        return a

    def load(self, name):
        resolvedName = EnvString.resolve(name)
        configuration = CondorConfig()
        configuration.load(resolvedName)
        self.defaults = {}
        
        tempDefaultRoot = Template(configuration.platform.defaultRoot)
        self.defaults["DEFAULT_ROOT"] = tempDefaultRoot.substitute(USER_NAME=self.commandLineDefaults["USER_NAME"])
        #self.defaults["DEFAULT_ROOT"] = EnvString.resolve(configuration.platform.defaultRoot)
        #tempLocalScratch = Template(configuration.platform.localScratch)
        #self.defaults["LOCAL_SCRATCH"] = tempLocalScratch.substitute(USER_HOME=self.commandLineDefaults["USER_HOME"])
        
        self.defaults["LOCAL_SCRATCH"] = EnvString.resolve(configuration.platform.localScratch)
        self.defaults["IDS_PER_JOB"] = configuration.platform.idsPerJob
        self.defaults["DATA_DIRECTORY"] = EnvString.resolve(configuration.platform.dataDirectory)
        self.defaults["FILE_SYSTEM_DOMAIN"] = configuration.platform.fileSystemDomain
        self.defaults["EUPS_PATH"] = configuration.platform.eupsPath
        # TODO:  Change this to do it the eups way when the new package
        # issue is resolved.
        #platform_dir = "$CTRL_PLATFORM_"+self.opts.platform.upper()+"_DIR"
        #platform_dir = EnvString.resolve(platform_dir)
        platform_dir = eups.productDir("ctrl_platform_"+self.opts.platform)
        self.defaults["PLATFORM_DIR"] = platform_dir

    def createConfiguration(self, input):
        resolvedInputName = EnvString.resolve(input)
        if self.opts.verbose == True:
            print "creating configuration using ",resolvedInputName
        template = TemplateWriter()
        substitutes = self.defaults.copy()
        for key in self.commandLineDefaults:
            val = self.commandLineDefaults[key]
            if val is not None:
                substitutes[key] = self.commandLineDefaults[key]

        substitutes["CTRL_EXECUTE_SETUP_PACKAGES"] = self.getSetupPackages()
        
        if self.opts.verbose == True:
            print "writing new configuration to ",self.outputFileName
        template.rewrite(resolvedInputName, self.outputFileName, substitutes)
        return self.outputFileName

    def isVerbose(self):
        return self.opts.verbose

    def getParameter(self,value):
        if value in self.commandLineDefaults:
            return self.commandLineDefaults[value]
        if value in self.defaults:
            return self.defaults[value]
        return None

    def getRunid(self):
        return self.runid
