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

class Allocator(object):
    def __init__(self, opts):

        self.opts = opts

        self.commandLineDefaults = {}

        self.commandLineDefaults["NODE_COUNT"] = self.opts.nodeCount
        self.commandLineDefaults["SLOTS"] = self.opts.slots
        self.commandLineDefaults["WALL_CLOCK"] = self.opts.maximumWallClock

        self.commandLineDefaults["QUEUE"] = self.opts.queueName
        self.commandLineDefaults["EMAIL_NOTIFICATION"] = self.opts.emailNotification

        self.defaults["NODE_SET"] = self.opts.nodeSet
        if self.defaults["NODE_SET"] is None:
            self.defaults["NODE_SET"] = self.createNodeSetName()

        if self.opts.outputLog is not None:
            self.defaults["OUTPUT_LOG"] = self.opts.outputLog
        else:
            self.defaults["OUTPUT_LOG"] = "%s.out" % nodeSetName

        if self.opts.errorLog is not None:
            self.defaults["ERROR_LOG"] = self.opts.errorLog
        else:
            self.defaults["ERROR_LOG"] = "%s.err" % nodeSetName

        self.outputFileName = "/tmp/alloc_%s.pbs" % (nodeSetName)
        
    def createNodeSetName(self):
        # TODO: change this to an incrementing name, based on a 'save pid' type
        # of file in the ~/.lsst directory.
        now = datetime.now()
        nodeSetName = "%s_%02d_%02d%02d_%02d%02d%02d" % (os.getlogin(), now.year, now.month, now.day, now.hour, now.minute, now.second)
        return nodeSetName


    def load(self, name):
        resolvedName = EnvString.resolve(name)
        configuration = AllocationConfig()
        configuration.load(resolvedName)

        self.defaults = {}
        self.defaults["QUEUE"] = configuration.platform.queue
        self.defaults["EMAIL_NOTIFICATION"] = configuration.platform.emailNotification
        self.defaults["HOST_NAME"] = configuration.platform.loginHostName
        self.defaults["SCRATCH_DIR"] = configuration.platform.scratchDir

    def createPBSFile(self, input):
        resolvedInputName = EnvString.resolve(input)
        if self.opts.verbose == True:
            print "creating PBS file using ",resolvedInputName
        template = TemplateWriter()
        substitutes = self.defaults.copy()
        for key in self.commandLineDefaults:
            val = self.commandLineDefaults[key]
            if val is not None:
                substitutes[key] = self.commandLineDefaults[key]
        
        if self.opts.verbose == True:
            print "writing new PBS file to ",self.outputFileName
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
