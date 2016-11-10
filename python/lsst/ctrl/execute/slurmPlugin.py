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

from __future__ import print_function
from builtins import str
from builtins import object
import os
import pwd
from datetime import datetime
from string import Template
from lsst.ctrl.execute import envString
from lsst.ctrl.execute.allocationConfig import AllocationConfig
from lsst.ctrl.execute.condorConfig import CondorConfig
from lsst.ctrl.execute.condorInfoConfig import CondorInfoConfig
from lsst.ctrl.execute.templateWriter import TemplateWriter
from lsst.ctrl.execute.seqFile import SeqFile

from lsst.ctrl.execute.plugin import Plugin


class slurmPlugin(Plugin):

    def submit(self, creator, platform, platformPkgDir):
        remoteCopyCmd = "/usr/bin/cp"
    
        configName = os.path.join(platformPkgDir, "etc", "config", "slurmConfig.py")
    
        creator.loadSlurm(configName) # XXX - change to use a plug-in
        verbose = creator.isVerbose()
    
        userName = creator.getUserName()
        hostName = creator.getHostName()
        scratchDirParam = creator.getScratchDirectory()
    
        template = Template(scratchDirParam)
        scratchDir = template.substitute(USER_HOME=creator.getUserHome())
    
        #
        # Steps - run command to allocate nodes; in PBS this requires writing a PBS file and submitting 
        # it; with slurm, it's a command line option
        #
    
        slurmName = os.path.join(platformPkgDir, "etc", "templates", "generic.slurm.template")
        generatedSlurmFile = creator.createSubmitFile(slurmName)
    
        condorFile = os.path.join(platformPkgDir, "etc", "templates", "glidein_condor_config.template")
        generatedCondorConfigFile = creator.createCondorConfigFile(condorFile)
    
        allocationName = os.path.join(platformPkgDir, "etc", "templates", "allocation.sh.template")
        allocationFile = creator.createAllocationFile(allocationName)
    
        # run the salloc command
    
        cmd = "sbatch %s" % generatedSlurmFile
        exitCode = self.runCommand(cmd, verbose)
        if exitCode != 0:
            print("error running %s" % cmd)
            sys.exit(exitCode)
    
        nodes = creator.getNodes()
        slots = creator.getSlots()
        wallClock = creator.getWallClock()
    
        nodeString = ""
        if int(nodes) > 1:
            nodeString = "s"
        print("%s node%s will be allocated on %s with %s slots per node and maximum time limit of %s" %
              (nodes, nodeString, platform, slots, wallClock))
        print("Node set name:")
        print(creator.getNodeSetName())
