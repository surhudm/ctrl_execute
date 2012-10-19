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
from lsst.ctrl.execute.allocationConfig import AllocationConfig

def test1():
    executePkgDir = eups.productDir("ctrl_execute")
    path = os.path.join(executePkgDir, "tests", "testfiles", "config_allocation.cfg")
    config = AllocationConfig()

    assert config.platform.queue == None
    assert config.platform.email == None
    assert config.platform.scratchDirectory == None
    assert config.platform.loginHostName == None
    assert config.platform.utilityPath == None

    config.load(path)

    assert config.platform.queue == "normal"
    assert config.platform.email == "#PBS mail -be"
    assert config.platform.scratchDirectory == "/tmp"
    assert config.platform.loginHostName == "bighost.lsstcorp.org"
    assert config.platform.utilityPath == "/bin"

if __name__ == "__main__":
    test1()
