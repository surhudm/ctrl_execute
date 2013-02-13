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
import os

from lsst.ctrl.execute.dagIdInfoExtractor import DagIdInfoExtractor

class TestDagIdInfo(unittest.TestCase):

    def test1(self):
        filename = os.path.join("tests","testfiles", "test.diamond.dag")
        extractor = DagIdInfoExtractor()
        line = extractor.extract("A1", filename)
        self.assertTrue(line == "run=1033 filter=r camcol=2 field=229")
        line = extractor.extract("A3", filename)
        self.assertTrue(line == "run=1033 filter=i camcol=2 field=47")
        line = extractor.extract("A17", filename)
        self.assertTrue(line == "run=1033 filter=r camcol=2 field=229 run=1033 filter=i camcol=2 field=47")
        line = extractor.extract("B1", filename)
        self.assertTrue(line == None)
    

if __name__ == "__main__":
    unittest.main()

