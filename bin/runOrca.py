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
from lsst.ctrl.execute.Configurator import Configurator
from lsst.ctrl.execute.RunOrcaParser import RunOrcaParser
import eups

def main():
    p = RunOrcaParser(sys.argv)
    opts = p.getOpts()
    creator = Configurator(opts)

    platformPkgDir = eups.productDir("ctrl_platform_"+creator.platform)
    if platformPkgDir is not None:
        configName = os.path.join(platformPkgDir, "etc", "config", "execConfig.py")
    else:
        raise RuntimeError("Can't find platform specific config for %s" % creator.platform)
    

    #configName = "$CTRL_EXECUTE_DIR/etc/configs/%s_config.py" % creator.platform
    creator.load(configName)

    
    executePkgDir = eups.productDir("ctrl_execute")
    genericConfigName = os.path.join(executePkgDir, "etc", "templates", "generic_config.py.template")
    generatedConfigFile = creator.createConfiguration(genericConfigName)

    runid = creator.getRunid()

    print "runid for this run is ",runid

    # TODO: allow -L and -V on this command line
    cmd = "orca.py %s %s" % (generatedConfigFile, runid)
    cmd_split = cmd.split()
    pid = os.fork()
    if not pid:
        sys.stdin.close()
        sys.stdout.close()
        sys.stderr.close()
        if creator.isVerbose == False:
            os.close(0)
            os.close(1)
            os.close(2)
        os.execvp(cmd_split[0], cmd_split)
    os.wait()[0]

if __name__ == "__main__":
    main()
