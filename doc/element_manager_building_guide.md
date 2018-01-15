## element Manager building guide

**Version 1.0**
**December 26, 2017**
**Copyright(c) 2017 Nippon Telegraph and Telephone Corporation**

This text describes how to generate pyc files from py files.

### files

|No.|files|Description|
|:----|:----|:----|
|1|pyc_create.sh|Script file|
|2|src/|Target py files; See **directories**|
|3|pyc_file/|Directory of output destination of generated pyc file|
|4|pyc_file_bk/|Backup of pyc_file|

- create pyc files from py files under src/ that is in the same directory as pyc_create.sh.
- When starting EM, it is necessary to correct the following description in `em_ctl.sh`.

~~~console
lib/MsfEmMain.py -> lib/MsfEmMain.pyc
bin/EmMonitor.py -> bin/EmMonitor.pyc
~~~

### execute
~~~console
sh pyc_create.sh
~~~

### directories
```
・★src/
  |--bin
  |  |--EmMonitor.py
  |--lib
  |  |--CommonDriver
  |  |  |--EmCommonDriver.py
  |  |  |--__init__.py
  |  |--Config
  |  |  |--EmConfigManagement.py
  |  |  |--__init__.py
  |  |--DB
  |  |  |--EmDBControl.py
  |  |  |--__init__.py
  |  |--DriverUtility
  |  |  |--EmDriverCommonUtilityDB.py
  |  |  |--EmDriverCommonUtilityLog.py
  |  |  |--__init__.py
  |  |--EmCommonLog.py
  |  |--EmLoggingTool.py
  |  |--EmSetPATH.py
  |  |--GlobalModule.py
  |  |--MsfEmMain.py
  |  |--NetconfServer
  |  |  |--EmNetconfServer.py
  |  |  |--__init__.py
  |  |--OrderflowControl
  |  |  |--EmOrderflowControl.py
  |  |  |--__init__.py
  |  |--Protocol
  |  |  |--EmCLIProtocol.py
  |  |  |--EmNetconfProtocol.py
  |  |  |--__init__.py
  |  |--RestScenario
  |  |  |--EmControllerLogGet.py
  |  |  |--EmControllerStatusGet.py
  |  |  |--EmSeparateRestScenario.py
  |  |  |--__init__.py
  |  |--RestServer
  |  |  |--EmRestServer.py
  |  |  |--__init__.py
  |  |--Scenario
  |  |  |--EmBLeafDelete.py
  |  |  |--EmBLeafMerge.py
  |  |  |--EmBLeafScenario.py
  |  |  |--EmBLeafUpdate.py
  |  |  |--EmBreakoutIFDelete.py
  |  |  |--EmBreakoutIFMerge.py
  |  |  |--EmCeLagDelete.py
  |  |  |--EmCeLagMerge.py
  |  |  |--EmClusterLinkDelete.py
  |  |  |--EmClusterLinkMerge.py
  |  |  |--EmDeleteScenario.py
  |  |  |--EmInternalLinkDelete.py
  |  |  |--EmInternalLinkMerge.py
  |  |  |--EmL2SliceDelete.py
  |  |  |--EmL2SliceEvpnControl.py
  |  |  |--EmL2SliceGet.py
  |  |  |--EmL2SliceMerge.py
  |  |  |--EmL3SliceDelete.py
  |  |  |--EmL3SliceGet.py
  |  |  |--EmL3SliceMerge.py
  |  |  |--EmL3SliceUpdate.py
  |  |  |--EmLeafDelete.py
  |  |  |--EmLeafMerge.py
  |  |  |--EmMergeScenario.py
  |  |  |--EmSeparateScenario.py
  |  |  |--EmSpineDelete.py
  |  |  |--EmSpineMerge.py
  |  |  |--__init__.py
  |  |--SeparateDriver
  |  |  |--CiscoDriver.py
  |  |  |--CiscoDriver5501.py
  |  |  |--EmSeparateDriver.py
  |  |  |--JuniperDriver5100.py
  |  |  |--JuniperDriver5200.py
  |  |  |--JuniperDriverMX240.py
  |  |  |--OcNOSDriver.py
  |  |  |--__init__.py
  |  |--SystemUtility
  |  |  |--EmSysCommonUtilityDB.py
  |  |  |--__init__.py
  |  |--__init__.py
```
