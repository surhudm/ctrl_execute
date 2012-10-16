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
import re, sys, os, os.path, shutil, subprocess
import optparse, traceback, time
import lsst.pex.config as pexConfig
import eups
from datetime import datetime
from string import Template
from EnvString import EnvString
from AllocationConfig import AllocationConfig
from CondorConfig import CondorConfig
from CondorInfoConfig import CondorInfoConfig
from TemplateWriter import TemplateWriter
from SeqFile import SeqFile

class Allocator(object):
    def __init__(self, platform, opts):

        self.opts = opts
        self.defaults = {}

        configFileName = "$HOME/.lsst/condor-info.py"
        fileName = EnvString.resolve(configFileName)

        condorInfoConfig = CondorInfoConfig()
        condorInfoConfig.load(fileName)

        self.platform = platform


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

        self.defaults["USER_NAME"] = user_name
        self.defaults["USER_HOME"] = user_home

        self.commandLineDefaults = {}

        self.commandLineDefaults["NODE_COUNT"] = self.opts.nodeCount
        self.commandLineDefaults["SLOTS"] = self.opts.slots
        self.commandLineDefaults["WALL_CLOCK"] = self.opts.maximumWallClock

        self.commandLineDefaults["QUEUE"] = self.opts.queue
        if self.opts.email == "no":
            self.commandLineDefaults["EMAIL_NOTIFICATION"] = "#"

    def createNodeSetName(self):
        s = SeqFile("$HOME/.lsst/node-set.seq")
        n = s.nextSeq()
        nodeSetName = "%s_%d" % (self.defaults["USER_NAME"], n)
        return nodeSetName
        
    def createUniqueFileName(self):
        now = datetime.now()
        fileName = "%s_%02d_%02d%02d_%02d%02d%02d" % (os.getlogin(), now.year, now.month, now.day, now.hour, now.minute, now.second)
        return fileName

    def load(self, name):
        resolvedName = EnvString.resolve(name)
        configuration = CondorConfig()
        configuration.load(resolvedName)
        self.defaults["LOCAL_SCRATCH"] = EnvString.resolve(configuration.platform.localScratch)

    def loadPBS(self, name):
        resolvedName = EnvString.resolve(name)
        configuration = AllocationConfig()
        if os.path.exists(resolvedName) == False:
            print "%s was not found." % resolvedName
            return False
        configuration.load(resolvedName)

        self.defaults["QUEUE"] = configuration.platform.queue
        self.defaults["EMAIL_NOTIFICATION"] = configuration.platform.email
        self.defaults["HOST_NAME"] = configuration.platform.loginHostName

        template = Template(configuration.platform.scratchDirectory)
        scratchDir = template.substitute(USER_HOME=self.getUserHome())
        self.defaults["SCRATCH_DIR"] = scratchDir

        self.defaults["UTILITY_PATH"] = configuration.platform.utilityPath

        if self.opts.nodeSet is None:
            self.defaults["NODE_SET"] = self.createNodeSetName()
        else:
            self.defaults["NODE_SET"] = self.opts.nodeSet

        nodeSetName = self.defaults["NODE_SET"]

        if self.opts.outputLog is not None:
            self.defaults["OUTPUT_LOG"] = self.opts.outputLog
        else:
            self.defaults["OUTPUT_LOG"] = "%s.out" % nodeSetName

        if self.opts.errorLog is not None:
            self.defaults["ERROR_LOG"] = self.opts.errorLog
        else:
            self.defaults["ERROR_LOG"] = "%s.err" % nodeSetName

        uniqueFileName = self.createUniqueFileName()

        # write these pbs and config files to {LOCAL_DIR}/configs
        configDir = os.path.join(self.defaults["LOCAL_SCRATCH"], "configs")
        if os.path.exists(configDir) == False:
            os.mkdir(configDir)

        self.pbsFileName = os.path.join(configDir, "alloc_%s.pbs" % uniqueFileName)

        self.condorConfigFileName = os.path.join(configDir, "condor_%s.config" % uniqueFileName)

        self.defaults["GENERATED_CONFIG"] = os.path.basename(self.condorConfigFileName)
        return True

    def createPBSFile(self, input):
        outfile = self.createFile(input, self.pbsFileName)
        if self.opts.verbose == True:
            print "wrote new PBS file to %s" %  outfile
        return outfile

    def createCondorConfigFile(self, input):
        outfile = self.createFile(input, self.condorConfigFileName)
        if self.opts.verbose == True:
            print "wrote new condor_config file to %s" %  outfile
        return outfile

    def createFile(self, input, output):
        resolvedInputName = EnvString.resolve(input)
        if self.opts.verbose == True:
            print "creating PBS file using %s" % resolvedInputName
        template = TemplateWriter()
        substitutes = self.defaults.copy()
        for key in self.commandLineDefaults:
            val = self.commandLineDefaults[key]
            if val is not None:
                substitutes[key] = self.commandLineDefaults[key]
        template.rewrite(resolvedInputName, output, substitutes)
        return output



    def isVerbose(self):
        return self.opts.verbose

    def getUserName(self):
        return self.getParameter("USER_NAME")

    def getUserHome(self):
        return self.getParameter("USER_HOME")

    def getHostName(self):
        return self.getParameter("HOST_NAME")

    def getUtilityPath(self):
        return self.getParameter("UTILITY_PATH")

    def getScratchDirectory(self):
        return self.getParameter("SCRATCH_DIR")

    def getNodeSetName(self):
        return self.getParameter("NODE_SET")

    def getNodes(self):
        return self.getParameter("NODE_COUNT")

    def getSlots(self):
        return self.getParameter("SLOTS")

    def getWallClock(self):
        return self.getParameter("WALL_CLOCK")


    def getParameter(self,value):
        if value in self.commandLineDefaults:
            return self.commandLineDefaults[value]
        if value in self.defaults:
            return self.defaults[value]
        return None
