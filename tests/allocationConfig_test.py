#!/usr/bin/env python
import eups
import os.path
from lsst.ctrl.execute.allocationConfig import AllocationConfig

def test1():
    executePkgDir = eups.productDir("ctrl_execute")
    path = os.path.join(executePkgDir, "tests","config_allocation.cfg")
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
