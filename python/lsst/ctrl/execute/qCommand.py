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

import eups
import sys, os, os.path, string
import lsst.pex.config as pexConfig
from lsst.ctrl.execute.envString import EnvString
from lsst.ctrl.execute.allocationConfig import AllocationConfig
from lsst.ctrl.execute.condorInfoConfig import CondorInfoConfig

class QCommand(object):
    """A class which wraps qsub-style commands for execution
    """

    def __init__(self, platform):

        self.remoteLoginCmd = "/usr/bin/gsissh" # can handle both grid-proxy and ssh logins
        self.remoteCopyCmd = "/usr/bin/gsiscp" # can handle both grid-proxy and ssh copies
    
        configFileName = "$HOME/.lsst/condor-info.py"
        fileName = EnvString.resolve(configFileName)
    
        condorInfoConfig = CondorInfoConfig()
        condorInfoConfig.load(fileName)
    
        platformPkgDir = eups.productDir("ctrl_platform_"+platform)
        if platformPkgDir is not None:
            configName = os.path.join(platformPkgDir, "etc", "config", "pbsConfig.py")
        else:
            print "ctrl_platform_%s was not found.  Is it setup?" % platform
            sys.exit(10)
    
        allocationConfig = AllocationConfig()
        allocationConfig.load(configName)
    
        self.userName = condorInfoConfig.platform[platform].user.name

        self.hostName = allocationConfig.platform.loginHostName
        self.utilityPath = allocationConfig.platform.utilityPath

    def runCommand(self, command):
        """Execute the command line
        """
        cmd_split = command.split()
        pid = os.fork()
        if not pid:
            os.execvp(cmd_split[0], cmd_split)
        pid, status = os.wait()
        exitCode = (status & 0xff00)  >> 8
        return exitCode
