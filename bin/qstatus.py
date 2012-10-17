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
import sys, os, os.path, shutil, subprocess, string
import lsst.pex.config as pexConfig
from lsst.ctrl.execute.EnvString import EnvString
from lsst.ctrl.execute.AllocationConfig import AllocationConfig
from lsst.ctrl.execute.CondorInfoConfig import CondorInfoConfig
import eups

def runCommand(cmd):
    cmd_split = cmd.split()
    pid = os.fork()
    if not pid:
        os.execvp(cmd_split[0], cmd_split)
    pid, status = os.wait()
    exitCode = (status & 0xff00)  >> 8
    return exitCode

if __name__ == "__main__":  
    platform = sys.argv[1]
    configFileName = "$HOME/.lsst/condor-info.py"
    fileName = EnvString.resolve(configFileName)

    condorInfoConfig = CondorInfoConfig()
    condorInfoConfig.load(fileName)

    platformPkgDir = eups.productDir("ctrl_platform_"+platform)
    if platformPkgDir is not None:
        configName = os.path.join(platformPkgDir, "etc", "config", "pbsConfig.py")
    else:
        raise RuntimeError("ctrl_platform_%s was not found.  Is it setup?" % platform)

    allocationConfig = AllocationConfig()
    allocationConfig.load(configName)

    hostName = allocationConfig.platform.loginHostName
    utilityPath = allocationConfig.platform.utilityPath
    userName = condorInfoConfig.platform[platform].user.name
    # default to doing a status for the user, otherwise, pass the args to qstat
    if len(sys.argv) == 2:
        cmd = "ssh %s@%s %s/qstat -u%s" % (userName, hostName, utilityPath, userName)
    else:
        cmd = "ssh %s@%s %s/qstat %s" % (userName, hostName, utilityPath, string.join(sys.argv[2:]))
    exitCode = runCommand(cmd)
    if exitCode != 0:
        sys.exit(exitCode)
    sys.exit(0)
