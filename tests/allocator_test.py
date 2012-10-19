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
import eups
import os.path
import time
from lsst.ctrl.execute.allocator import Allocator
from lsst.ctrl.execute.allocatorParser import AllocatorParser

def setup():
    test1_args = ["allocator_test",
            "test_platform",
            "-n","64",
            "-s","12",
            "-m","00:30:00",
            "-N","test_set",
            "-q","normal",
            "-e","yes",
            "-O","outlog",
            "-E","errlog",
            "-v",
            ]
    executePkgDir = eups.productDir("ctrl_execute")
    fileName = os.path.join(executePkgDir, "tests", "testfiles", "allocator-info1.cfg")
    alp = AllocatorParser(test1_args)
    opts = alp.getOpts()
    al = Allocator("lsst", opts, fileName)
    return al

def test1(al):

    filename1 = al.createUniqueFileName()
    time.sleep(1)
    filename2 = al.createUniqueFileName()
    assert filename1 != filename2

def test2(al):
    executePkgDir = eups.productDir("ctrl_execute")
    path = os.path.join(executePkgDir, "tests","testfiles", "config_condor.cfg")
    al.load(path)

    fileName = os.path.join(executePkgDir, "tests", "testfiles", "config_allocation.cfg")

    nodeSetName1 = al.loadPBS(fileName)

def test3(al):
    assert al.isVerbose()

def test4(al):
    executePkgDir = eups.productDir("ctrl_execute")
    path = os.path.join(executePkgDir, "tests","testfiles", "config_condor.cfg")
    al.load(path)
    fileName = os.path.join(executePkgDir, "tests", "testfiles", "config_allocation.cfg")
    nodeSetName1 = al.loadPBS(fileName)
    assert al.getHostName() == "bighost.lsstcorp.org"
    assert al.getUtilityPath() == "/bin"
    assert al.getScratchDirectory() == "/tmp"
    assert al.getNodeSetName() == "test_set"
    assert al.getNodes() == "64"
    assert al.getSlots() == "12"
    assert al.getWallClock() == "00:30:00"
    assert al.getParameter("NODE_COUNT") == "64"
    assert al.getParameter("KAZOO") == None

if __name__ == "__main__":
    test1(setup())
    test2(setup())
    test3(setup())
    test4(setup())
