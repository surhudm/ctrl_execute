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
import unittest
import sys
import os.path
import time
from lsst.ctrl.execute.configurator import Configurator
from lsst.ctrl.execute.runOrcaParser import RunOrcaParser

class TestConfigurator(unittest.TestCase):
    def getRemoteArgs(self):
        sys.argv = ["configurator_test",
                "-p", "bigboxes",
                "-c",'"echo hello"',
                "-i","$CTRL_EXECUTE_DIR/tests/testfiles/inputfile",
                "-e","/tmp",
                "-n","test_set",
                "-j","16",
                "-v",
                ]
        return sys.argv
    
    def getLocalArgs(self):
        sys.argv = ["configurator_test",
                "-p", "lsst",
                "-c",'"echo hello"',
                "-i","$CTRL_EXECUTE_DIR/tests/testfiles/inputfile",
                "-e","/tmp2",
                "-n","test_set2",
                "-j","12",
                ]
        return sys.argv
    
    def getLocalWithSetupArgs(self):
        sys.argv = ["configurator_test",
                "-p", "lsst",
                "-c",'"echo hello"',
                "-i","$CTRL_EXECUTE_DIR/tests/testfiles/inputfile",
                "-e","/tmp2",
                "-n","test_set2",
                "-j","12",
                "--setup","fake_package", "1.0",
                ]
        return sys.argv
    
    
    def setup(self,args):
        fileName = os.path.join("tests", "testfiles", "allocator-info1.py")
        rop = RunOrcaParser(args[0])
        args = rop.getArgs()
        configurator = Configurator(args, fileName)
        return configurator
    
    def test1(self):
        configurator = self.setup(self.getRemoteArgs())
        self.assertTrue(configurator.isVerbose())
        self.assertTrue(configurator.getParameter("EUPS_PATH") == "/tmp")
        self.assertTrue(configurator.getParameter("USER_NAME") == "thx1138")
        self.assertTrue(configurator.getParameter("USER_HOME") == "/home/thx1138")
    
    def test2(self):
        configurator = self.setup(self.getLocalArgs())
        self.assertTrue(configurator.isVerbose() == False)
        self.assertTrue(configurator.getParameter("EUPS_PATH") == "/tmp2")
        self.assertTrue(configurator.getParameter("USER_NAME") == "c3po")
        self.assertTrue(configurator.getParameter("USER_HOME") == "/lsst/home/c3po")
        self.assertTrue(configurator.getParameter("NODE_SET") == "test_set2")
        self.assertTrue(configurator.getParameter("KAZOO") == None)
    
    def test3(self):
        configurator = self.setup(self.getRemoteArgs())
        testname = "config_with_setups.py.template"
        print configurator.getGenericConfigFileName()
        self.assertTrue(os.path.basename(configurator.getGenericConfigFileName()) == testname)
    
    def test4(self):
        configurator = self.setup(self.getLocalArgs())
        testname = "config_with_getenv.py.template"
        self.assertTrue(os.path.basename(configurator.getGenericConfigFileName()) == testname)
    
    def test5(self):
        configurator = self.setup(self.getLocalWithSetupArgs())
        testname = "config_with_setups.py.template"
        self.assertTrue(os.path.basename(configurator.getGenericConfigFileName()) == testname)
    
    def test6(self):
        configurator = self.setup(self.getRemoteArgs())
        runId1 = configurator.createRunId()
        time.sleep(1)
        runId2 = configurator.createRunId()
        self.assertTrue(runId1 != runId2)
        self.assertTrue(runId2 == configurator.getRunId())
    
    def test7(self):
        configurator = self.setup(self.getRemoteArgs())
        self.assertTrue(configurator.getSetupPackages() != None)
    

if __name__ == "__main__":
    unittest.main()
