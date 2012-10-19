#!/usr/bin/env python
import eups
import os.path
from lsst.ctrl.execute.condorConfig import CondorConfig

def test1():
    executePkgDir = eups.productDir("ctrl_execute")
    path = os.path.join(executePkgDir, "tests","config_condor.cfg")
    config = CondorConfig()

    assert config.platform.defaultRoot == None
    assert config.platform.localScratch == None
    assert config.platform.dataDirectory == None
    assert config.platform.fileSystemDomain == None
    assert config.platform.eupsPath == None

    config.load(path)

    assert config.platform.defaultRoot == "/usr"
    assert config.platform.localScratch == "/tmp"
    assert config.platform.dataDirectory == "/tmp/data"
    assert config.platform.fileSystemDomain == "lsstcorp.org"
    assert config.platform.eupsPath == "/var/tmp"

if __name__ == "__main__":
    test1()
