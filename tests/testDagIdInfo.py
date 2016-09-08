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

import os
import sys
import unittest
from subprocess import Popen, PIPE


class TestDagIdInfo(unittest.TestCase):

    def executeCommand(self, cmd):
        p = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        return stdout

    def test1(self):
        exe = sys.executable
        execPath = os.path.join("bin.src", "dagIdInfo.py")
        filename = os.path.join("tests", "testfiles", "test.diamond.dag")

        stdout = self.executeCommand("%s %s A1 %s" % (exe, execPath, filename))
        self.assertTrue(stdout == "run=1033 filter=r camcol=2 field=229\n")

        stdout = self.executeCommand("%s %s A3 %s" % (exe, execPath, filename))
        self.assertTrue(stdout == "run=1033 filter=i camcol=2 field=47\n")

        stdout = self.executeCommand("%s %s A17 %s" % (exe, execPath, filename))
        self.assertTrue(stdout == "run=1033 filter=r camcol=2 field=229 run=1033 filter=i camcol=2 field=47\n")

        stdout = self.executeCommand("%s %s B1 %s" % (exe, execPath, filename))
        self.assertTrue(stdout == "")

if __name__ == "__main__":
    unittest.main()
