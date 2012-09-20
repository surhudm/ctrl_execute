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
from datetime import datetime
import lsst.pex.config as pexConfig
from string import Template
import eups

# This class takes template files and substitutes the values for the given
# keys, writing a new file generated from the template.
#
class TemplateWriter:

    #
    # given a input template, take the keys from the key/values in the config
    # object and substitute the values, and write those to the output file.
    #
    def rewrite(self, input, output, pairs):
        fpInput = open(input, 'r')
        fpOutput = open(output, 'w')

        while True:
            line = fpInput.readline()
            if len(line) == 0:
                break

            # replace the user defined names
            for name in pairs:
                key = "$"+name
                val = str(pairs[name])
                line = line.replace(key, val)
            fpOutput.write(line)
        fpInput.close()
        fpOutput.close()

class AllocatedPlatformConfig(pexConfig.Config):
    queueName = pexConfig.Field("default root working for directories",str, default=None)
    emailNotification = pexConfig.Field("local scratch directory",str, default="yes") 
    outputLogName = pexConfig.Field("output log filename", str, default="nodeset.out")
    errorLogName = pexConfig.Field("error log filename", str, default="nodeset.err")
    eupsPath = pexConfig.Field("eups path", str, default=None)

class AllocationConfig(pexConfig.Config):
    platform = pexConfig.ConfigField("platform allocation", AllocatedPlatformConfig)

class Allocator(object):
    def __init__(self, opts):

        self.opts = opts

        self.commandLineDefaults = {}

        self.commandLineDefaults["NODE_COUNT"] = self.opts.nodeCount
        self.commandLineDefaults["SLOTS"] = self.opts.slots
        self.commandLineDefaults["WALLCLOCK"] = self.opts.maximumWallClock


        nodeSetName = self.opts.nodeSet
        if nodeSetName is None:
            nodeSetName = self.createNodeSetName()

        self.outputFileName = "/tmp/alloc_%s.pbs" % (nodeSetName)
        
    def createNodeSetName(self):
        # TODO: change this to an incrementing name, based on a 'save pid' typ
        # of file in the ~/.lsst directory.
        now = datetime.now()
        nodeSetName = "%s_%02d_%02d%02d_%02d%02d%02d" % (os.getlogin(), now.year, now.month, now.day, now.hour, now.minute, now.second)
        return nodeSetName


    def load(self, name):
        resolvedName = EnvString.resolve(name)
        configuration = AllocationConfig()
        configuration.load(resolvedName)
        self.defaults = {}
        self.defaults["QUEUE_NAME"] = configuration.platform.defaultRoot)
        tempLocalScratch = Template(configuration.platform.localScratch)
        self.defaults["LOCAL_SCRATCH"] = tempLocalScratch.substitute(USER_HOME=self.commandLineDefaults["USER_HOME"])
        print 'self.defaults["LOCAL_SCRATCH"] = ', self.defaults["LOCAL_SCRATCH"]
        
        #self.defaults["LOCAL_SCRATCH"] = EnvString.resolve(configuration.platform.localScratch)
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
        
        if self.opts.verbose == True:
            print "writing new configuration to ",self.outputFileName
        template.rewrite(resolvedInputName, self.outputFileName, substitutes)
        return self.outputFileName

    def isVerbose(self):
        return self.opts.verbose

    def getParameter(self,value):
        val = self.commandLineDefaults[value]
        if val == None:
            val =  self.defaults[value]
        return val

    def getNodeSetName(self):
        return self.nodeSetName
