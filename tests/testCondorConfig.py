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
import os.path
from lsst.ctrl.execute.condorConfig import CondorConfig


class TestCondorConfig(unittest.TestCase):
    def setUp(self):
        self.config = CondorConfig()
    
    def test1(self):
        assert self.config.platform.defaultRoot == None
        assert self.config.platform.localScratch == None
        assert self.config.platform.dataDirectory == None
        assert self.config.platform.fileSystemDomain == None
        assert self.config.platform.eupsPath == None
        assert self.config.platform.defaultRoot == None
    
    def test2(self):
        path = os.path.join("tests","testfiles", "config_condor.cfg")
        self.config.load(path)
    
        assert self.config.platform.defaultRoot == "/usr"
        assert self.config.platform.localScratch == "/tmp"
        assert self.config.platform.dataDirectory == "/tmp/data"
        assert self.config.platform.fileSystemDomain == "lsstcorp.org"
        assert self.config.platform.eupsPath == "/var/tmp"
    
if __name__ == "__main__":
    unittest.main()
