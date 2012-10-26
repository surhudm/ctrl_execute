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
import sys
import os.path
import time
import filecmp
import unittest
from lsst.ctrl.execute.allocator import Allocator
from lsst.ctrl.execute.allocatorParser import AllocatorParser

class TestAllocator(unittest.TestCase):

    def verboseArgs(self):
        argv = ["allocator_test",
                "test_platform",
                "-n","64",
                "-s","12",
                "-m","00:30:00",
                "-N","test_set",
                "-q","normal",
                "-e",
                "-O","outlog",
                "-E","errlog",
                "-v",
                ]
        return argv
    
    def regularArgs(self):
        argv = ["allocator_test",
                "test_platform",
                "-n","64",
                "-s","12",
                "-m","00:30:00",
                "-N","test_set",
                "-q","normal",
                "-e",
                "-O","outlog",
                "-E","errlog",
                ]
        return argv

    def subSetup(self):
        fileName = os.path.join("tests", "testfiles", "allocator-info1.cfg")
        alp = AllocatorParser(sys.argv[0])
        args = alp.getArgs()
        al = Allocator("lsst", args, fileName)
        return al

    def test1(self):
        sys.argv = self.verboseArgs()
        al = self.subSetup()
    
        identifier1 = al.createUniqueIdentifier()
        time.sleep(1)
        identifier2 = al.createUniqueIdentifier()
        self.assertTrue(identifier1 != identifier2)
    
    
    def test2(self):
        sys.argv = self.verboseArgs()
        al = self.subSetup()   
        
        path = os.path.join("tests","testfiles", "config_condor.cfg")
        al.load(path)
        fileName = os.path.join("tests", "testfiles", "config_allocation.cfg")
        al.loadPbs(fileName)
        self.assertTrue(al.getHostName() == "bighost.lsstcorp.org")
        self.assertTrue(al.getUtilityPath() == "/bin")
        self.assertTrue(al.getScratchDirectory() == "/tmp")
        self.assertTrue(al.getNodeSetName() == "test_set")
        self.assertTrue(al.getNodes() == 64)
        self.assertTrue(al.getSlots() == 12)
        self.assertTrue(al.getWallClock() == "00:30:00")
        self.assertTrue(al.getParameter("NODE_COUNT") == 64)
        self.assertTrue(al.getParameter("KAZOO") == None)
        self.assertTrue(al.isVerbose())

    def test3(self):
        sys.argv = self.regularArgs()
        al = self.subSetup()   

        path = os.path.join("tests","testfiles", "config_condor.cfg")
        al.load(path)
        fileName = os.path.join("tests", "testfiles", "config_allocation.cfg")
        al.loadPbs(fileName)
        pbsName = os.path.join("tests", "testfiles", "generic.pbs.template")
        compare = os.path.join("tests", "testfiles", "generic.pbs.txt")
        generatedPbsFile = al.createPbsFile(pbsName)

        self.assertTrue(filecmp.cmp(compare,generatedPbsFile))
        condorFile = os.path.join("tests", "testfiles", "glidein_condor_config.template")
        compare = os.path.join("tests", "testfiles", "glidein_condor_config.txt")
        generatedCondorConfigFile = al.createCondorConfigFile(condorFile)
        self.assertTrue(filecmp.cmp(compare,generatedCondorConfigFile))
        os.remove(generatedCondorConfigFile)
        os.remove(generatedPbsFile)


if __name__ == "__main__":
    unittest.main()
