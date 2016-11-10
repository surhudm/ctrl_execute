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


from __future__ import print_function
import sys
import os
import shutil
import lsst.utils
from lsst.ctrl.execute.allocator import Allocator
from lsst.ctrl.execute.allocatorParser import AllocatorParser
from string import Template


def main():
    """Allocates Condor glide-in nodes a scheduler on a remote Node.
    """

    # UNKNOWN_PLATFORM_EXIT_CODE = 10
    # MISSING_PBS_CONFIG_EXIT_CODE = 20

    p = AllocatorParser(sys.argv[0])
    platform = p.getPlatform()

    creator = Allocator(platform, p.getArgs(), "$HOME/.lsst/condor-info.py")

    platformPkgDir = lsst.utils.getPackageDir("ctrl_platform_"+platform)
    execConfigName = os.path.join(platformPkgDir, "etc", "config", "execConfig.py")


    creator.load(execConfigName)

    if creator.getScheduler() == "slurm":
        submitViaSlurm(creator, platform, platformPkgDir)
    elif creator.getScheduler() == "pbs":
        submitViaPBS(creator, platform, platformPkgDir)
    else:
        print("unknown scheduler: %s" % creator.getScheduler())
        return

def submitViaSlurm(creator, platform, platformPkgDir):
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

    slurmName = os.path.join(platformPkgDir, "etc", "templates", "generic.slurm.template")
    generatedSlurmFile = creator.createSubmitFile(slurmName)

    condorFile = os.path.join(platformPkgDir, "etc", "templates", "glidein_condor_config.template")
    generatedCondorConfigFile = creator.createCondorConfigFile(condorFile)

    allocationName = os.path.join(platformPkgDir, "etc", "templates", "allocation.sh.template")
    allocationFile = creator.createAllocationFile(allocationName)

    #dst = os.path.join(scratchDir, os.path.basename(generatedCondorConfigFile))
    #shutil.copyfile(generatedCondorConfigFile, dst)

    # run the salloc command

    cmd = "sbatch %s" % generatedSlurmFile
    exitCode = runCommand(cmd, verbose)
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
    sys.exit(0)
        

    return

def submitViaPBS(creator, platform, platformPkgDir):
    # This have specific paths to prevent abitrary binaries from being
    # executed. The "gsi"* utilities are configured to use either grid proxies
    # or ssh, automatically.
    remoteLoginCmd = "/usr/bin/gsissh"
    remoteCopyCmd = "/usr/bin/gsiscp"

    configName = os.path.join(platformPkgDir, "etc", "config", "pbsConfig.py")
    creator.loadPbs(configName)

    verbose = creator.isVerbose()

    pbsName = os.path.join(platformPkgDir, "etc", "templates", "generic.pbs.template")
    generatedPbsFile = creator.createPbsFile(pbsName)

    condorFile = os.path.join(platformPkgDir, "etc", "templates", "glidein_condor_config.template")
    generatedCondorConfigFile = creator.createCondorConfigFile(condorFile)

    scratchDirParam = creator.getScratchDirectory()
    template = Template(scratchDirParam)
    scratchDir = template.substitute(USER_HOME=creator.getUserHome())
    userName = creator.getUserName()

    hostName = creator.getHostName()

    utilityPath = creator.getUtilityPath()

    #
    # execute copy of PBS file to XSEDE node
    #
    cmd = "%s %s %s@%s:%s/%s" % (remoteCopyCmd, generatedPbsFile, userName,
                                 hostName, scratchDir, os.path.basename(generatedPbsFile))
    if verbose:
        print(cmd)
    exitCode = runCommand(cmd, verbose)
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
    exitCode = runCommand(cmd, verbose)
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
    exitCode = runCommand(cmd, verbose)
    if exitCode != 0:
        print("error running %s to %s." % (remoteLoginCmd, hostName))
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
    sys.exit(0)


def runCommand(cmd, verbose):
    cmd_split = cmd.split()
    pid = os.fork()
    if not pid:
        # Methods of file transfer and login may
        # produce different output, depending on how
        # the "gsi" utilities are used.  The user can
        # either use grid proxies or ssh, and gsiscp/gsissh
        # does the right thing.  Since the output will be
        # different in either case anything potentially parsing this
        # output (like drpRun), would have to go through extra
        # steps to deal with this output, and which ultimately
        # end up not being useful.  So we optinally close the i/o output
        # of the executing command down.
        #
        # stdin/stdio/stderr is treated specially
        # by python, so we have to close down
        # both the python objects and the
        # underlying c implementations
        if not verbose:
            # close python i/o
            sys.stdin.close()
            sys.stdout.close()
            sys.stderr.close()
            # close C's i/o
            os.close(0)
            os.close(1)
            os.close(2)
        os.execvp(cmd_split[0], cmd_split)
    pid, status = os.wait()
    # high order bits are status, low order bits are signal.
    exitCode = (status & 0xff00) >> 8
    return exitCode

if __name__ == "__main__":
    main()
