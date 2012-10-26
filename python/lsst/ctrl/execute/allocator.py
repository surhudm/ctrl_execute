#!/usr/bin/env python

# 
# LSST Data Management System
# Copyright 2008-2012 LSST Corporation.
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

import os
import lsst.pex.config as pexConfig
from datetime import datetime
from string import Template
from lsst.ctrl.execute import envString
from lsst.ctrl.execute.allocationConfig import AllocationConfig
from lsst.ctrl.execute.condorConfig import CondorConfig
from lsst.ctrl.execute.condorInfoConfig import CondorInfoConfig
from lsst.ctrl.execute.templateWriter import TemplateWriter
from lsst.ctrl.execute.seqFile import SeqFile

class Allocator(object):
    """A class which consolidates allocation pex_config information with override
    information (obtained from the command line) and produces a PBS file using
    these values.
    """
    def __init__(self, platform, opts, configFileName):
        """Constructor
        @param platform: target platform for PBS submission
        @param opts: options to override
        """
        self.opts = opts
        self.defaults = {}

        fileName = envString.resolve(configFileName)

        condorInfoConfig = CondorInfoConfig()
        condorInfoConfig.load(fileName)

        self.platform = platform


        # Look up the user's name and home directory in the 
        # $HOME/.lsst/condor-info.py file
        # If the platform is lsst, and the user_name or user_home 
        # is not in there, then default to user running this 
        # command and the value of $HOME, respectively.
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
        """Creates the next "node_set" name, using the remote user name and
        a stored sequence number.
        @return the new node_set name
        """
        s = SeqFile("$HOME/.lsst/node-set.seq")
        n = s.nextSeq()
        nodeSetName = "%s_%d" % (self.defaults["USER_NAME"], n)
        return nodeSetName
        
    def createUniqueFileName(self):
        """Creates a unique file name, based on the user's name and the time
        at which this method is invoked.
        @return the new file name
        """
        now = datetime.now()
        # This naming scheme follows the conventions used for creating RUNID
        # names.
        fileName = "%s_%02d_%02d%02d_%02d%02d%02d" % (os.getlogin(), now.year, now.month, now.day, now.hour, now.minute, now.second)
        return fileName

    def load(self, name):
        """Loads all values from configuration and command line overrides into
        data structures suitable for use by the TemplateWriter object.
        @return True on success, False if the platform to allocate can not be found.
        """
        resolvedName = envString.resolve(name)
        configuration = CondorConfig()
        configuration.load(resolvedName)
        self.defaults["LOCAL_SCRATCH"] = envString.resolve(configuration.platform.localScratch)

    def loadPbs(self, name):
        """Loads all values from configuration and command line overrides into
        data structures suitable for use by the TemplateWriter object.
        @return True on success, False if the platform to allocate can not be found.
        """
        resolvedName = envString.resolve(name)
        configuration = AllocationConfig()
        if not os.path.exists(resolvedName):
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
        if not os.path.exists(configDir):
            os.mkdirs(configDir)

        self.pbsFileName = os.path.join(configDir, "alloc_%s.pbs" % uniqueFileName)

        self.condorConfigFileName = os.path.join(configDir, "condor_%s.config" % uniqueFileName)

        self.defaults["GENERATED_CONFIG"] = os.path.basename(self.condorConfigFileName)
        return True

    def createPbsFile(self, input):
        """Creates a PBS file using the file "input" as a Template
        @return the newly created file
        """
        outfile = self.createFile(input, self.pbsFileName)
        if self.opts.verbose:
            print "wrote new PBS file to %s" %  outfile
        return outfile

    def createCondorConfigFile(self, input):
        """Creates a Condor config file using the file "input" as a Template
        @return the newly created file
        """
        outfile = self.createFile(input, self.condorConfigFileName)
        if self.opts.verbose:
            print "wrote new condor_config file to %s" %  outfile
        return outfile

    def createFile(self, input, output):
        """Creates a new file, using "input" as a Template, and writes the
        new file to output. 
        @return the newly created file
        """
        resolvedInputName = envString.resolve(input)
        if self.opts.verbose:
            print "creating file using %s" % resolvedInputName
        template = TemplateWriter()
        # Uses the associative arrays of "defaults" and "commandLineDefaults"
        # to write out the new file from the template.  
        # The commandLineDefaults override values in "defaults"
        substitutes = self.defaults.copy()
        for key in self.commandLineDefaults:
            val = self.commandLineDefaults[key]
            if val is not None:
                substitutes[key] = self.commandLineDefaults[key]
        template.rewrite(resolvedInputName, output, substitutes)
        return output


    def isVerbose(self):
        """Status of the verbose flag
        @return True if the flag was set, False otherwise
        """
        return self.opts.verbose

    def getUserName(self):
        """Accessor for USER_NAME
        @return the value of USER_NAME
        """
        return self.getParameter("USER_NAME")

    def getUserHome(self):
        """Accessor for USER_HOME
        @return the value of USER_HOME
        """
        return self.getParameter("USER_HOME")

    def getHostName(self):
        """Accessor for HOST_NAME
        @return the value of HOST_NAME
        """
        return self.getParameter("HOST_NAME")

    def getUtilityPath(self):
        """Accessor for UTILITY_PATH
        @return the value of UTILITY_PATH
        """
        return self.getParameter("UTILITY_PATH")

    def getScratchDirectory(self):
        """Accessor for SCRATCH_DIR
        @return the value of SCRATCH_DIR
        """
        return self.getParameter("SCRATCH_DIR")

    def getNodeSetName(self):
        """Accessor for NODE_SET
        @return the value of NODE_SET
        """
        return self.getParameter("NODE_SET")

    def getNodes(self):
        """Accessor for NODE_COUNT
        @return the value of NODE_COUNT
        """
        return self.getParameter("NODE_COUNT")

    def getSlots(self):
        """Accessor for SLOTS
        @return the value of SLOTS
        """
        return self.getParameter("SLOTS")

    def getWallClock(self):
        """Accessor for WALL_CLOCK
        @return the value of WALL_CLOCK
        """
        return self.getParameter("WALL_CLOCK")


    def getParameter(self,value):
        """Accessor for generic value
        @return None if value is not set.  Otherwise, use the command line override (if set), or the default Config value
        """
        if value in self.commandLineDefaults:
            return self.commandLineDefaults[value]
        if value in self.defaults:
            return self.defaults[value]
        return None
