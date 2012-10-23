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
from lsst.ctrl.execute.configurator import Configurator
from lsst.ctrl.execute.runOrcaParser import RunOrcaParser

def getRemoteArgs():
    args = ["configurator_test",
            "-p", "bigboxes",
            "-c","echo hello",
            "-i","$CTRL_EXECUTE/tests/testfiles/inputfile",
            "-e","/tmp",
            "-n","test_set",
            "-j","16",
            "-v",
            ]
    return args

def getLocalArgs():
    args = ["configurator_test",
            "-p", "lsst",
            "-c","echo hello",
            "-i","$CTRL_EXECUTE/tests/testfiles/inputfile",
            "-e","/tmp2",
            "-n","test_set2",
            "-j","12",
            ]
    return args

def getLocalWithSetupArgs():
    args = ["configurator_test",
            "-p", "lsst",
            "-c","echo hello",
            "-i","$CTRL_EXECUTE/tests/testfiles/inputfile",
            "-e","/tmp2",
            "-n","test_set2",
            "-j","12",
            "--setup","fake_package", "1.0",
            ]
    return args


def setup(args):
    executePkgDir = eups.productDir("ctrl_execute")
    fileName = os.path.join(executePkgDir, "tests", "testfiles", "allocator-info1.cfg")
    rop = RunOrcaParser(args)
    opts = rop.getOpts()
    configurator = Configurator(opts, fileName)
    return configurator

def test1():
    configurator = setup(getRemoteArgs())
    assert configurator.isVerbose()
    assert configurator.getParameter("EUPS_PATH") == "/tmp"
    assert configurator.getParameter("USER_NAME") == "thx1138"
    assert configurator.getParameter("USER_HOME") == "/home/thx1138"

def test2():
    configurator = setup(getLocalArgs())
    assert configurator.isVerbose() == False
    assert configurator.getParameter("EUPS_PATH") == "/tmp2"
    assert configurator.getParameter("USER_NAME") == "c3po"
    assert configurator.getParameter("USER_HOME") == "/lsst/home/c3po"
    assert configurator.getParameter("NODE_SET") == "test_set2"
    assert configurator.getParameter("KAZOO") == None

def test3():
    configurator = setup(getRemoteArgs())
    executePkgDir = eups.productDir("ctrl_execute")
    testname = os.path.join(executePkgDir,"etc","templates","config_with_setups.py.template")
    assert configurator.getGenericConfigFileName() == testname

def test4():
    configurator = setup(getLocalArgs())
    executePkgDir = eups.productDir("ctrl_execute")
    testname = os.path.join(executePkgDir,"etc","templates","config_with_getenv.py.template")
    assert configurator.getGenericConfigFileName() == testname

def test5():
    configurator = setup(getLocalWithSetupArgs())
    executePkgDir = eups.productDir("ctrl_execute")
    testname = os.path.join(executePkgDir,"etc","templates","config_with_setups.py.template")
    assert configurator.getGenericConfigFileName() == testname

def test6():
    configurator = setup(getRemoteArgs())
    runId1 = configurator.createRunId()
    time.sleep(1)
    runId2 = configurator.createRunId()
    assert runId1 != runId2
    assert runId2 == configurator.getRunId()

def test7():
    configurator = setup(getRemoteArgs())
    assert configurator.getSetupPackages() != None
    

if __name__ == "__main__":
    test1()
    test2()
    test3()
    test4()
    test5()
    test6()
    test7()
