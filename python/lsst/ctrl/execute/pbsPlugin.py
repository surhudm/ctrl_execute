#!/usr/bin/env python

#
# LSST Data Management System
# Copyright 2008-2016 LSST Corporation.
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
import sys
from string import Template

from lsst.ctrl.execute.allocator import Allocator


class PbsPlugin(Allocator):

    def submit(self, platform, platformPkgDir):
        # This have specific paths to prevent abitrary binaries from being
        # executed. The "gsi"* utilities are configured to use either grid
        # proxies or ssh, automatically.
        remoteLoginCmd = "/usr/bin/ssh"
        remoteCopyCmd = "/usr/bin/scp"

        configName = os.path.join(platformPkgDir, "etc", "config", "pbsConfig.py")

        self.loadPbs(configName)
        verbose = self.isVerbose()

        pbsName = os.path.join(platformPkgDir, "etc", "templates", "generic.pbs.template")
        generatedPbsFile = self.createSubmitFile(pbsName)

        condorFile = os.path.join(platformPkgDir, "etc", "templates", "glidein_condor_config.template")
        generatedCondorConfigFile = self.createCondorConfigFile(condorFile)

        allocationName = os.path.join(platformPkgDir, "etc", "templates", "allocation.sh.template")
        self.createAllocationFile(allocationName)

        scratchDirParam = self.getScratchDirectory()
        template = Template(scratchDirParam)
        scratchDir = template.substitute(USER_HOME=self.getUserHome())

        userName = self.getUserName()
        hostName = self.getHostName()

        utilityPath = self.getUtilityPath()

        #
        # execute copy of PBS file to XSEDE node
        #
        cmd = "%s %s %s@%s:%s/%s" % (remoteCopyCmd, generatedPbsFile, userName,
                                     hostName, scratchDir, os.path.basename(generatedPbsFile))
        if verbose:
            print(cmd)
        exitCode = self.runCommand(cmd, verbose)
        if exitCode != 0:
            print("error running %s to %s." % (remoteCopyCmd, hostName))
            sys.exit(exitCode)

        #
        # execute copy of Condor config file to XSEDE node
        #
        cmd = "%s %s %s@%s:%s/%s" % (remoteCopyCmd, generatedCondorConfigFile, userName,
                                     hostName, scratchDir, os.path.basename(generatedCondorConfigFile))
        if verbose:
            print(cmd)
        exitCode = self.runCommand(cmd, verbose)
        if exitCode != 0:
            print("error running %s to %s." % (remoteCopyCmd, hostName))
            sys.exit(exitCode)

        #
        # execute qsub command on XSEDE node to perform Condor glide-in
        #
        cmd = "%s %s@%s %s/qsub %s/%s" % (remoteLoginCmd, userName, hostName,
                                          utilityPath, scratchDir, os.path.basename(generatedPbsFile))
        if verbose:
            print(cmd)
        exitCode = self.runCommand(cmd, verbose)
        if exitCode != 0:
            print("error running %s to %s." % (remoteLoginCmd, hostName))
            sys.exit(exitCode)

        self.printNodeSetInfo()

    def loadPbs(self, name):
        configuration = self.loadAllocationConfig(name, "pbs")
        template = Template(configuration.platform.scratchDirectory)
        scratchDir = template.substitute(USER_HOME=self.getUserHome())
        self.defaults["SCRATCH_DIR"] = scratchDir

        allocationConfig = self.loadAllocationConfig(name, "pbs")
        self.allocationFileName = os.path.join(self.configDir, "allocation_%s.sh" % self.uniqueIdentifier)
        self.defaults["GENERATED_ALLOCATE_SCRIPT"] = os.path.basename(self.allocationFileName)

    def createAllocationFile(self, input):
        """Creates Allocation script file using the file "input" as a Template

        Returns
        -------
        outfile : `str`
            The newly created file name
        """
        outfile = self.createFile(input, self.allocationFileName)
        if self.opts.verbose:
            print("wrote new allocation script file to %s" % outfile)
        os.chmod(outfile, 0o755)
        return outfile
