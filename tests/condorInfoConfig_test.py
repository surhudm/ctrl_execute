#!/usr/bin/env python
import eups
import os.path
from lsst.ctrl.execute.condorInfoConfig import CondorInfoConfig

def test1():
    executePkgDir = eups.productDir("ctrl_execute")
    path = os.path.join(executePkgDir, "tests","config_condorInfo.cfg")
    config = CondorInfoConfig()

    config.load(path)

    assert config.platform["test1"].user.name == "test1"
    assert config.platform["test1"].user.home == "/home/test1"
    assert config.platform["test2"].user.name == "test2"
    assert config.platform["test2"].user.home == "/home/test2"

if __name__ == "__main__":
    test1()
