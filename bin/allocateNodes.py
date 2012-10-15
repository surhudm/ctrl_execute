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


import sys, os, os.path
import optparse
import eups
import lsst.pex.config as pexConfig
from lsst.ctrl.execute.allocator import Allocator
from lsst.ctrl.execute.allocatorParser import AllocatorParser
from string import Template

def main():
    p = AllocatorParser(sys.argv)
    platform = p.getPlatform()

    creator = Allocator(platform, p.getOpts())

    platformPkgDir = eups.productDir("ctrl_platform_"+platform)
    if platformPkgDir is not None:
        configName = os.path.join(platformPkgDir, "etc", "config", "pbsConfig.py")
    else:
        print "ctrl_platform_%s was not found." % platform
        sys.exit(10)
    
    execConfigName = os.path.join(platformPkgDir, "etc", "config", "execConfig.py")

    if creator.load(execConfigName) == False:
        raise RuntimeError("Couldn't find execConfig.py file for platform: %s" % platform)

    if creator.loadPBS(configName) == False:
        raise RuntimeError("Couldn't find pbsConfig.py file for platform: %s" % platform)

    verbose = creator.isVerbose()

    
    pbsName = os.path.join(platformPkgDir, "etc", "templates", "generic.pbs.template")
    generatedPBSFile = creator.createPBSFile(pbsName)

    condorFile = os.path.join(platformPkgDir, "etc", "templates", "glidein_condor_config.template")
    generatedCondorConfigFile = creator.createCondorConfigFile(condorFile)

    scratchDirParam = creator.getScratchDirectory()
    template = Template(scratchDirParam)
    scratchDir = template.substitute(USER_HOME=creator.getUserHome())
    
    hostName = creator.getHostName()

    utilityPath = creator.getUtilityPath()

    cmd = "scp %s %s:%s/%s" % (generatedPBSFile, hostName, scratchDir, os.path.basename(generatedPBSFile))
    if verbose:
        print cmd
    exitCode = runCommand(cmd, verbose)
    if exitCode != 0:
        print "error running scp to %s." % hostName
        sys.exit(exitCode)

    cmd = "scp %s %s:%s/%s" % (generatedCondorConfigFile, hostName, scratchDir, os.path.basename(generatedCondorConfigFile))
    if verbose:
        print cmd
    exitCode = runCommand(cmd, verbose)
    if exitCode != 0:
        print "error running scp to %s." % hostName
        sys.exit(exitCode)

    cmd = "ssh %s %s/qsub %s/%s" % (hostName, utilityPath, scratchDir, os.path.basename(generatedPBSFile))
    if verbose:
        print cmd
    exitCode = runCommand(cmd, verbose)
    if exitCode != 0:
        print "error running ssh to %s." % hostName
        sys.exit(exitCode)

    nodes = creator.getNodes()
    slots = creator.getSlots()
    wallClock = creator.getWallClock()
    nodeString = ""
    if int(nodes) > 1:
        nodeString = "s"
    print "nodes ",nodes
    print "nodeString ",nodeString
    print "%s node%s will be allocated on %s with %s slots per node and maximum time limit of %s" % (nodes, nodeString, platform, slots, wallClock)
    print "Node set name:"
    print creator.getNodeSetName()
    sys.exit(0)

def runCommand(cmd, verbose):
    cmd_split = cmd.split()
    pid = os.fork()
    if not pid:
        sys.stdin.close()
        sys.stdout.close()
        sys.stderr.close()
        os.close(0)
        os.close(1)
        os.close(2)
        os.execvp(cmd_split[0], cmd_split)
    pid, status = os.wait()
    exitCode = (status & 0xff00)  >> 8
    return exitCode

if __name__ == "__main__":
    main()
