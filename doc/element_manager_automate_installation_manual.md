# Element Manager Automate Installation Manual

**Version 1.0**
**June 27, 2019**
**Copyright(c) 2019 Nippon Telegraph and Telephone Corporation**

## 1. Introduction

1.1. Objective
---------

This document is the installation manual for the EM Module included in
the Element Manager (hereafter referred to as \"EM\").
Please read this manual carefully before using the software.

1.2. Scope of Application
--------------------

The scope of this document is for the operation of the components of EM
Module of Controller.

The subjects other than that are not covered in this document.

This manual supports both redundant and non-redundant EM systems.
The EM system is composed of the EM server and the DB server.
The EM server supports both the redundant and non-redundant configuration.
The DB server supports only the non-redundant configuration.
In this manual, you need the server (Ansible server) on which automatic install script is running in addition to the servers which consists of the EM system.

Figure 1-1 illustrates the image of each configuration.

![Figure 1-1 Figure 1-1 The image of EM system configuration.](img/Fig_1_1_EM.png "Fig1-1")<br>
Figure 1-1 The image of EM system configuration.

1.3. Expressional Conventions
------------------------

There are certain expressions and text styles conventionally used in
this document. Please make yourself clear about the items below before
going on through the document.

**\<Execution Host: XXX\>** - bold letters surrounded by triangle brackets

This means ther server XXX executing commands. 
XXX is the following. 

　Ansible : Ansible server<br>
　ACT : EM ACT server<br>
　SBY : EM SBY server<br>
　DB  : DB server

**\[XX XX\]** - bold letters surrounded by square brackets

This means the command to be entered in Linux.

**X \[Enter\]** - bold letter and \"\[Enter\]\"

> In this case, you need to enter the letters within brackets and press
> the Enter key in the console screen.

**\$EM_HOME**

You need to replace with the same value as em_path in Table 3-1 vars Files.

1.4. Trademark Notice
----------------

All company names and product names mentioned in this document are
registered trademarks or trademarks of their respective companies.

**LinuxR**

The registered trademark or the trademark of Linus Torvalds in the U.S.
and other countries

**PostgreSQLR**

The trademark of PostgreSQL in the U.S. and other countries

1.5. Configuration of the Included Accessories
-----------------------------------------

The \"Table-1-1 Included Accessories\" below illustrates the required
items to follow the installation instructions in this document.

For the items described as \"in-advance DL\", you must download and
prepare them prior to implementing the installation in this document
at no internet connection.
Then, place the acquired files under the em folder of the target server (created in Chapter 3)
so that they are the same as the following file structure.

Table 1-1 Included Accessories

| Folder  |Structure   |       |         | File Name    | Descriprion | Remarks |
|---------|---------|---------|---------|---------|---------|---------|
| em      | \-      | \-      | \-      | \-      | \-      | \-      |
|         |         |         |         | whl_package.tar | In-use Python Library Package  | In-Advance DL from GitHub  |
|         |         |         |         | paramiko-2.0.2-py2.py3-none-any.whl | In-use Python Library Package  | In-Advance DL |
|         |         |         |         | psycopg2-2.6.2-cp27-cp27mu-linux_x86_64.whl | In-use Python Library Package  | In-Advance DL |
|         |         |         |         | pip-8.1.2.tar.gz | PIP Command for Python Library Install     | In-Advance DL |
|         |         |         |         | requests-2.20.1-py2.py3-none-any.whl    | Library for Python(requests) installation   | In-Advance DL |
|         |         |         |         | urllib3-1.24.1-py2.py3-none-any.whl     | requests Dependent Package        | In-Advance DL |
|         |         |         |         | idna-2.7-py2.py3-none-any.whl           | requests Dependent Package        | In-Advance DL |
|         |         |         |         | chardet-3.0.4-py2.py3-none-any.whl      | requests Dependent Package        | In-Advance DL |
|         |         |         |         | certifi-2018.10.15-py2.py3-none-any.whl | requests Dependent Package        | In-Advance DL |
|         |         |         |         | setuptools-28.6.0.tar.gz | pip Dependent Package     | In-Advance DL |
|         | bin     |         |         | em      | Resource Agent | In-Advance DL from GitHub  |
|         |         |         |         | em_ctl.sh | EM Start-up Script      | In-Advance DL from GitHub  |
|         |         |         |         | EmMonitor.py | Alive Monitor Client   | In-Advance DL from GitHub  |
|         |         |         |         | controller_status.sh     | Controller Status Information<br> Acquisition Script | In-Advance DL from GitHub  |
|         |         |         |         | check_resource_lock.sh   | Pacemaker Resource Status Monitor Script | In-Advance DL from GitHub  |
|         |         |         |         | resource_lock_release.sh | Pacemaker Resource Move Permission Script | In-Advance DL from GitHub  |
|         |         |         |         | controller_switch.sh     | Controller Switch-over Script | In-Advance DL from GitHub  |
|         | lib     |         |         | MsfEmMain.py | Main Module    | In-Advance DL from GitHub  |
|         |         |         |         | GlobalModule.py | Global Module  | In-Advance DL from GitHub  |
|         |         |         |         | EmCommonLog.py | EM Common Log Module      | In-Advance DL from GitHub  |
|         |         |         |         | EmSetPATH.py | PYTHONPATH Configuration Module for EM | In-Advance DL from GitHub  |
|         |         |         |         | EmLoggingTool.py | Log Formater Module for EM     | In-Advance DL from GitHub  |
|         |         |         |         | PluginLoader.py | Plugin Control Module for EM     | In-Advance DL from GitHub  |
|         |         |         |         | \__init__.py | Initialization Module | In-Advance DL from GitHub  |
|         |         | CgwshUtility |    | CgwshDeviceConfigManagement.py| Device utility file for CGW-SH(Config Mgt)  | In-Advance DL from GitHub  |
|         |         |         |         | EmCgwshDeviceUtilityDB.py     | Device utility file for CGW-SH(DB) | In-Advance DL from GitHub  |
|         |         |         |         | \__init__.py | Initialization Module | In-Advance DL from GitHub  |
|         |         | CommonDriver |    | EmCommonDriver.py | Driver Common Part Module  | In-Advance DL from GitHub  |
|         |         |         |         | \__init__.py | Initialization Module | In-Advance DL from GitHub  |
|         |         | Config  |         | EmConfigManagement.py | Configuration Management Module | In-Advance DL from GitHub  |
|         |         |         |         | \__init__.py | Initialization Module | In-Advance DL from GitHub  |
|         |         | ControllerLogNotify  |         | ControllerLogNotify.py | Controller Log Notification Module | In-Advance DL from GitHub  |
|         |         |         |         | \__init__.py | Initialization Module | In-Advance DL from GitHub  |
|         |         | ControllerStatusGet  |         | EmControllerStatusGetExecutor.py | Module for controller status Periodic notification Executer | In-Advance DL from GitHub  |
|         |         |         |         | EmControllerStatusGetManager.py | Manager module for controller status Periodic notification | In-Advance DL from GitHub  |
|         |         |         |         | EmControllerStatusGetTimeKeep.py | Module for time management to get controller status | In-Advance DL from GitHub  |
|         |         |         |         | \__init__.py | Initialization Module | In-Advance DL from GitHub  |
|         |         | DB      |         | EmDBControl.py | DB Control Module      | In-Advance DL from GitHub  |
|         |         |         |         | \__init__.py | Initialization Module | In-Advance DL from GitHub  |
|         |         | DriverUtility |   | EmDriverCommonUtilityDB.py    | Driver Common Utility (DB) Module  | In-Advance DL from GitHub  |
|         |         |         |         | EmDriverCommonUtilityLog.py   | Driver Common Utility (Log) Module  | In-Advance DL from GitHub  |
|         |         |         |         | AuditConfigManagement.py      | Config Audit Management Module  | In-Advance DL from GitHub  |
|         |         |         |         | ConfigAuditDriverUtility.py   | Driver Utility(Audit) Module  | In-Advance DL from GitHub  |
|         |         |         |         | EmDifflib.py                  | Difflib Module for EM | In-Advance DL from GitHub  |
|         |         |         |         | CgwshDeviceDriverUtilityDB.py | Utility(DB) File for CGW-SH device driver | In-Advance DL from GitHub  |
|         |         |         |         | \__init__.py | Initialization Module | In-Advance DL from GitHub  |
|         |         | EmStartPlugin |   | EmPluginCgwshDeviceControl.py | Plugin for increase/decrease CGW-SH device | In-Advance DL from GitHub  |
|         |         | Netconf Server |  | EmNetconfServer.py   | EM Netconf Server Module      | In-Advance DL from GitHub  |
|         |         |         |         | EmNetconfResponse.py | Netconf ResponseModule | In-Advance DL from GitHub  |
|         |         |         |         | \__init__.py | Initialization Module | In-Advance DL from GitHub  |
|         |         |         | NcsPluginCreateResponse | NcsPluginCreateResponseMSF.py | Netconf Response Plugin for MSF | In-Advance DL from GitHub  |
|         |         | OrderflowControl |         | EmOrderflowControl.py | Order Flow Control Module   | In-Advance DL from GitHub  |
|         |         |         | OfcPluginMessage | \__init__.py | Initialization Module | In-Advance DL from GitHub  |
|         |         |         |         | OfcPluginMSF.py   | Message Analysis Plugin Module for MSF normal Service | In-Advance DL from GitHub  |
|         |         |         |         | OfcPluginCGWSH.py | Message Analysis Plugin for CGWSH | In-Advance DL from GitHub  |
|         |         | PeriodicProcessing |  | EmPeriodicProcessing.py     | Periodic Process Management Module | In-Advance DL from GitHub  |
|         |         |         |         | EmPeriodicProcessingTimeKeep.py | Periodic Process Time Management Module | In-Advance DL from GitHub  |
|         |         |         |         | \__init__.py | Initialization Module | In-Advance DL from GitHub  |
|         |         | Protocol |        | EmNetconfProtocol.py | For-device Protocol Process Module | In-Advance DL from GitHub  |
|         |         |         |         | EmCLIProtocol.py | Protocol Processing (CLI) Module for Devices | In-Advance DL from GitHub  |
|         |         |         |         | EmNetconfClient.py | Ncclient Original implementation processing module | In-Advance DL from GitHub  |
|         |         |         |         | CumulusCLIProtocol.py | Protocol Processing (CLI) Module for Devices (Cumulus) | In-Advance DL from GitHub  |
|         |         |         |         | EmCLIProtocolBase.py | Protocol Processing (CLI) Module for Devices (Base) | In-Advance DL from GitHub  |
|         |         |         |         | CgwshDriverCLIProtocol.py | Protocol Processing(CLI) Module for CGW-SH driver(ASR,NVR) | In-Advance DL from GitHub  |
|         |         |         |         | NVRDriverCLIProtocol.py   | Protocol Processing(CLI) Module for NVR driver | In-Advance DL from GitHub  |
|         |         |         |         | \__init__.py | Initialization Module | In-Advance DL from GitHub  |
|         |         | RestScenario |    | EmControllerLogGet.py | Controller Log Acquisition Scenario | In-Advance DL from GitHub  |
|         |         |         |         | EmControllerStatusGet.py | Controller Status Acquisition Scenario | In-Advance DL from GitHub  |
|         |         |         |         | EmSeparateRestScenario.py | REST Individual Scenario Module    | In-Advance DL from GitHub  |
|         |         |         |         | EmControllerSwitch.py  | Controller Switch-over Scenario | In-Advance DL from GitHub  |
|         |         |         |         | EmDeviceConfigAudit.py | Device Config-Audit Scenario    | In-Advance DL from GitHub  |
|         |         |         |         | \__init__.py | Initialization Module | In-Advance DL from GitHub  |
|         |         | RestServer |      | EmRestServer.py | REST Server Module    | In-Advance DL from GitHub  |
|         |         |         |         | \__init__.py | Initialization Module | In-Advance DL from GitHub  |
|         |         | Scenario |        | EmACLFilterDelete.py | ACL Filter Deletion Scenario  | In-Advance DL from GitHub  |
|         |         |         |         | EmACLFilterMerge.py | ACL Filter Generation Scenario  | In-Advance DL from GitHub  |
|         |         |         |         | EmBLeafDelete.py | B-Leaf Deletion Scenario  | In-Advance DL from GitHub  |
|         |         |         |         | EmBLeafMerge.py | B-Leaf Generation Scenario  | In-Advance DL from GitHub  |
|         |         |         |         | EmBLeafScenario.py | B-Leaf Scenario Modulef  | In-Advance DL from GitHub  |
|         |         |         |         | EmBLeafUpdate.py | B-Leaf Update Scenario  | In-Advance DL from GitHub  |
|         |         |         |         | EmBreakoutIFDelete.py | BreakoutIF Deletion Scenario | In-Advance DL from GitHub  |
|         |         |         |         | EmBreakoutIFMerge.py | BreakoutIF Registration Scenario | In-Advance DL from GitHub  |
|         |         |         |         | EmCeLagDelete.py | LAG Deletion Scenario for CE     | In-Advance DL from GitHub  |
|         |         |         |         | EmCeLagMerge.py | LAG Addition Scenario for CE     | In-Advance DL from GitHub  |
|         |         |         |         | EmCeLagUpdate.py | LAG Update Scenario for CE     | In-Advance DL from GitHub  |
|         |         |         |         | EmClusterLinkDelete.py | Inter-Claster Link I/F Deletion Scenario | In-Advance DL from GitHub  |
|         |         |         |         | EmClusterLinkMerge.py | Inter-Claster Link I/F Addition Scenario | In-Advance DL from GitHub  |
|         |         |         |         | EmDeleteScenario.py | Resource Deletion Scenario Module | In-Advance DL from GitHub  |
|         |         |         |         | EmDeviceDelete.py | MSF device Deletion Scenario Module | In-Advance DL from GitHub  |
|         |         |         |         | EmDeviceInfoUpdate.py | Device Information Update Scenario Module | In-Advance DL from GitHub  |
|         |         |         |         | EmDeviceMerge.py | MSF device Addition Scenario Modulee | In-Advance DL from GitHub  |
|         |         |         |         | EmIfConditionUpdate.py | IF Open/Close Scenario Modulee | In-Advance DL from GitHub  |
|         |         |         |         | EmInternalLinkDelete.py | Internal Link Delete Scenario | In-Advance DL from GitHub  |
|         |         |         |         | EmInternalLinkMerge.py | Internal Link Merge Scenario | In-Advance DL from GitHub  |
|         |         |         |         | EmInternalLinkUpdate.py | Internal Link Update Scenario | In-Advance DL from GitHub  |
|         |         |         |         | EmL2SliceEvpnControl.py | L2 Slice EVPN Control Scenario | In-Advance DL from GitHub  |
|         |         |         |         | EmL2SliceDelete.py | L2 Slice Deletion Scenario      | In-Advance DL from GitHub  |
|         |         |         |         | EmL2SliceGet.py | L2 Slice Information Adjustment Scenario      | In-Advance DL from GitHub  |
|         |         |         |         | EmL2SliceMerge.py | L2 Slice Addition Scenario      | In-Advance DL from GitHub  |
|         |         |         |         | EmL2SliceUpdate.py | L2 Slice Update Scenario      | In-Advance DL from GitHub  |
|         |         |         |         | EmL3SliceDelete.py | L3 Slice Deletion Scenario      | In-Advance DL from GitHub  |
|         |         |         |         | EmL3SliceGet.py | L3 Slice Information Adjustment Scenario      | In-Advance DL from GitHub  |
|         |         |         |         | EmL3SliceMerge.py | L3 Slice Addition Scenario      | In-Advance DL from GitHub  |
|         |         |         |         | EmL3SliceUpdate.py | L3 Slice Update Scenario      | In-Advance DL from GitHub  |
|         |         |         |         | EmLeafDelete.py | Leaf Deletion Scenario    | In-Advance DL from GitHub  |
|         |         |         |         | EmLeafMerge.py | Leaf Addition Scenario    | In-Advance DL from GitHub  |
|         |         |         |         | EmMergeScenario.py | Resource Addition Scenario Module | In-Advance DL from GitHub  |
|         |         |         |         | EmRecover.py | Recover Node Scenario | In-Advance DL from GitHub  |
|         |         |         |         | EmRecoverNode.py | Recover Node Scenario | In-Advance DL from GitHub  |
|         |         |         |         | EmRecoverService.py | Recover Node Scenario | In-Advance DL from GitHub  |
|         |         |         |         | EmSpineDelete.py | Spine Deletion Scenario   | In-Advance DL from GitHub  |
|         |         |         |         | EmSpineMerge.py | Spine Addition Scenario   | In-Advance DL from GitHub  |
|         |         |         |         | EmSeparateScenario.py | Individual Scenario Module | In-Advance DL from GitHub  |
|         |         |         |         | \__init__.py | Initialization Module | In-Advance DL from GitHub  |
|         |         |         | CGW-SH  |                                   | Folder for storing CGW-SH Scenario                           | In-Advance DL from GitHub  |
|         |         |         |         | EmCgwshCustomerUniRouteDelete.py  | Individual Scenario for individual UNI Static Route Deletion in Cgwsh Service | In-Advance DL from GitHub  |
|         |         |         |         | EmCgwshCustomerUniRouteMerge.py   | Individual Scenario for individual UNI Static Route Addition in Cgwsh Service | In-Advance DL from GitHub  |
|         |         |         |         | EmCgwshPPPDelete.py               | Individual Scenario for individual PPP Deletion in Cgwsh Service | In-Advance DL from GitHub  |
|         |         |         |         | EmCgwshPPPMerge.py                | Individual Scenario for individual PPP Addition in Cgwsh Service | In-Advance DL from GitHub  |
|         |         |         |         | EmCgwshServiceBase.py             | Base Scenario Class for Cgwsh Service  | In-Advance DL from GitHub  |
|         |         |         |         | EmCgwshServiceFlavor.py           | Scenario Flavor Classfor Cgwsh Service | In-Advance DL from GitHub  |
|         |         |         |         | EmCgwshServiceManagementDelete.py | Individual Scenario for Service Deletion in Cgwsh Service | In-Advance DL from GitHub  |
|         |         |         |         | EmCgwshServiceManagementMerge.py  | Individual Scenario for New Service Registration in Cgwsh Service | In-Advance DL from GitHub  |
|         |         |         |         | EmCgwshTunnelDelete.py   | Individual Scenario for Tunnel Deletion in Cgwsh Service | In-Advance DL from GitHub  |
|         |         |         |         | EmCgwshTunnelMerge.py    | Individual Scenario for Tunnel Addition in Cgwsh Service | In-Advance DL from GitHub  |
|         |         |         |         | EmCgwshUniRouteDelete.py | Individual Scenario for UNI Static Route Deletion in Cgwsh Service | In-Advance DL from GitHub  |
|         |         |         |         | EmCgwshUniRouteMerge.py  | Individual Scenario for UNI Static Route Addition in Cgwsh Service | In-Advance DL from GitHub  |
|         |         | SeparateDriver |  | BeluganosDriver.py | Beluganos Driver Module       | In-Advance DL from GitHub  |
|         |         |         |         | CiscoDriver.py | Cisco (5001, 5011) Driver Module       | In-Advance DL from GitHub  |
|         |         |         |         | CiscoDriver5501.py | Cisco 5501 Driver Module       | In-Advance DL from GitHub  |
|         |         |         |         | CLIDriver.py | CLI Driver Module       | In-Advance DL from GitHub  |
|         |         |         |         | CumulusDriver.py | Cumulus Driver Module       | In-Advance DL from GitHub  |
|         |         |         |         | JuniperDriver5100.py | Juniper 5100 Driver Module       | In-Advance DL from GitHub  |
|         |         |         |         | JuniperDriver5110.py | Juniper 5110 Driver Module       | In-Advance DL from GitHub  |
|         |         |         |         | JuniperDriver5200.py | Juniper 5200 Driver Module       | In-Advance DL from GitHub  |
|         |         |         |         | JuniperDriverMX240.py | J Company Core Router Driver Module       | In-Advance DL from GitHub  |
|         |         |         |         | OcNOSDriver.py | OcNOS Driver Module   | In-Advance DL from GitHub  |
|         |         |         |         | EmSeparateDriver.py | Driver Individual Module  | In-Advance DL from GitHub  |
|         |         |         |         | ASRSetParameterECDB.py | Config Parameter Module File for Cisco ASR driver | In-Advance DL from GitHub  |
|         |         |         |         | CgwshDeviceDriverSetParameterECDB.py | Config Parameter Module File for Cgwsh driver | In-Advance DL from GitHub  |
|         |         |         |         | CgwshDriverBase.py | Cgwsh Driver(Base) Module File | In-Advance DL from GitHub  |
|         |         |         |         | CiscoDriverASR1002_X.py | Cisco ASR 1002-X Driver File | In-Advance DL from GitHub  |
|         |         |         |         | DriverSetParameterECDB.py | Config Parameter Module File for driver | In-Advance DL from GitHub  |
|         |         |         |         | NVRSetParameterECDB.py | Config Parameter Module File for Yamaha NVR driver | In-Advance DL from GitHub  |
|         |         |         |         | YamahaDriverNVR510.py | Yamaha NVR 510 Driver File | In-Advance DL from GitHub  |
|         |         |         |         | \__init__.py | Initialization Module | In-Advance DL from GitHub  |
|         |         |         | ASRDriverParts | ASRDriverConfigBase.py | Config Parts Module for ASR driver | In-Advance DL from GitHub  |
|         |         |         |         | BGP.py | BGP Config Parts Module for ASR driver | In-Advance DL from GitHub  |
|         |         |         |         | InterfaceBase.py | IF Base Config Parts Module for ASR driver | In-Advance DL from GitHub  |
|         |         |         |         | ShowCommand.py | Show Command Parts Module for ASR driver | In-Advance DL from GitHub  |
|         |         |         |         | StaticRoute.py | Static Route Config Parts Module for ASR driver | In-Advance DL from GitHub  |
|         |         |         |         | TunnelInterface.py | Tunnel Interface Config Parts Module for ASR driver | In-Advance DL from GitHub  |
|         |         |         |         | UNIInterface.py | UNI Interface Config Parts Module for ASR driver | In-Advance DL from GitHub  |
|         |         |         |         | UNOInterface.py | UNO Interface Config Parts Module for ASR driver | In-Advance DL from GitHub  |
|         |         |         |         | VRF.py | VRF Config Parts Module for ASR driver | In-Advance DL from GitHub  |
|         |         |         |         | \__init__.py | Initialization Module | In-Advance DL from GitHub  |
|         |         |         | NVRDriverParts | DefaultGateway.py | Default Gateway Config Parts Module for NVR Driver | In-Advance DL from GitHub  |
|         |         |         |         | Filtering.py | Filtering Config Parts Module for NVR Driver | In-Advance DL from GitHub  |
|         |         |         |         | Interface.py | Interface Config Parts Module for NVR Driver | In-Advance DL from GitHub  |
|         |         |         |         | NVRDriverConfigBase.py | Config Parts Module for NVR Driver | In-Advance DL from GitHub  |
|         |         |         |         | PPPoE.py | PPPoE Config Parts Module for NVR Driver | In-Advance DL from GitHub  |
|         |         |         |         | ShowCommand.py | Show Command Parts Module for NVR Driver | In-Advance DL from GitHub  |
|         |         |         |         | StaticRoute.py | Static Route Config Parts Module for NVR Driver | In-Advance DL from GitHub  |
|         |         |         |         | \__init__.py | Initialization Module | In-Advance DL from GitHub  |
|         |         |         | RecoverUtility | EmRecoverUtilBase.py | Recover Node Utility Module (base)  | In-Advance DL from GitHub  |
|         |         |         |         | EmRecoverUtilACL.py | Recover Node Utility Module (ACL Filter)  | In-Advance DL from GitHub  |
|         |         |         |         | EmRecoverUtilBLeaf.py | Recover Node Utility Module (B-Leaf)  | In-Advance DL from GitHub  |
|         |         |         |         | EmRecoverUtilCeLag.py | Recover Node Utility Module (CE LAG)  | In-Advance DL from GitHub  |
|         |         |         |         | EmRecoverUtilClusterLink.py | Recover Node Utility Module (Inter-Claster Link)  | In-Advance DL from GitHub  |
|         |         |         |         | EmRecoverUtilL2Slice.py | Recover Node Utility Module (L2 Slice)  | In-Advance DL from GitHub  |
|         |         |         |         | EmRecoverUtilL3Slice.py | Recover Node Utility Module (L3 Slice)  | In-Advance DL from GitHub  |
|         |         |         |         | EmRecoverUtilLeaf.py | Recover Node Utility Module (Leaf)  | In-Advance DL from GitHub  |
|         |         |         |         | EmRecoverUtilIfCondition.py | Recover Node Utility Module (IF Open/Close)  | In-Advance DL from GitHub  |
|         |         |         |         | \__init__.py | Initialization Module | In-Advance DL from GitHub  |
|         |         | SystemUtility |   | EmSysCommonUtilityDB.py | System Common (DB) Utility Module  | In-Advance DL from GitHub  |
|         |         |         |         | \__init__.py | Initialization Module | In-Advance DL from GitHub  |
|         | conf    |         |         | conf_driver.conf | Driver Individual Part Operational Configuration File  | In-Advance DL from GitHub  |
|         |         |         |         | conf_if_process.conf | I/F Process Part Operational Configuration File     | In-Advance DL from GitHub  |
|         |         |         |         | conf_scenario.conf | Scenario Individual Part Operational Configuration File | In-Advance DL from GitHub  |
|         |         |         |         | conf_sys_common.conf | EM Common Configuration File      | In-Advance DL from GitHub  |
|         |         |         |         | conf_separate_driver_cisco.conf | Cisco Driver Operation Configuration File       | In-Advance DL from GitHub  |
|         |         |         |         | conf_if_process_rest.conf | REST Server Operation Configuration FileT    | In-Advance DL from GitHub  |
|         |         |         |         | conf_scenario_rest.conf | REST Scenario Individual Part Operation Configuration File    | In-Advance DL from GitHub  |
|         |         |         |         | conf_service.conf | Service Definition Configuration FileT    | In-Advance DL from GitHub  |
|         |         |         |         | conf_internal_link_vlan.conf | OS (Requires VLAN ID on internal link) specification Configuration File    | In-Advance DL from GitHub  |
|         |         |         |         | Beluganos.conf | QoS of Beluganos Driver Operation Configuration File    | In-Advance DL from GitHub  |
|         |         |         |         | Cumulus.conf | QoS of Cumulus Driver Operation Configuration File    | In-Advance DL from GitHub  |
|         |         |         |         | Cisco.conf | QoS of Cisco Driver Operation Configuration File    | In-Advance DL from GitHub  |
|         |         |         |         | Juniper.conf | QoS of Juniper Driver Operation Configuration File    | In-Advance DL from GitHub  |
|         |         |         |         | OcNOS.conf | QoS of OcNOS Driver Operation Configuration File    | In-Advance DL from GitHub  |
|         |         |         |         | conf_act_threshold.conf               | ACT Threshold Configuration File    | In-Advance DL from GitHub  |
|         |         |         |         | conf_standby_threshold.conf           | SBY Threshold Configuration File    | In-Advance DL from GitHub  |
|         |         | cgwsh_device |    | conf_asr_device_sample1.conf          | Configuration File for CGW-SH Device Setting Management    | In-Advance DL from GitHub  |
|         |         |         |         | conf_nvr_device_sample1.conf          | Configuration File for CGW-SH Device Setting Management    | In-Advance DL from GitHub  |
|         |         | conf_audit |      | conf_asr_audit_exclusion.conf         | Configuration File for execluded string during Config-Audit execution (ASR)   | In-Advance DL from GitHub  |
|         |         |         |         | conf_nvr_audit_exclusion.conf         | Configuration File for execluded string during Config-Audit execution (NVR)   | In-Advance DL from GitHub  |
|         |         |         |         | conf_qfx5110_audit_exclusion.conf     | Configuration File for execluded string during Config-Audit execution (QFX5110 non-IRB)   | In-Advance DL from GitHub  |
|         |         |         |         | conf_qfx5110_irb_audit_exclusion.conf | Configuration File for execluded string during Config-Audit execution (QFX5110 IRB)   | In-Advance DL from GitHub  |
|         | file_update |     |         | db_env                   | Environment Configuration File | In-Advance DL from GitHub |
|         |         |         |         | db_schema_update.sh      | DB Schema Update Script        | In-Advance DL from GitHub |
|         |         |         |         | MSF2017_MSF2018B.sh      | Script for Update DB Schema from MSF2017 to MSF2018B        | In-Advance DL from GitHub |
|         |         |         |         | MSF2017_to_MSF2018B.sql  | DB Schema Update SQL (MSF2017 to MSF2018B)        | In-Advance DL from GitHub |
|         |         |         |         | MSF2018A_MSF2018B.sh     | Script for Update DB Schema from MSF2018A to MSF2018B        | In-Advance DL from GitHub |
|         |         |         |         | MSF2018A_to_MSF2018B.sql | DB Schema Update SQL (MSF2018A to MSF2018B)          | In-Advance DL from GitHub |
|         |         |         |         | db_backup.sh             | DB Backup Script               | In-Advance DL from GitHub |
|         |         |         |         | db_restore.sh            | DB Restore Script              | In-Advance DL from GitHub |
|         |         |         |         | em_file_upgrade.sh  | Binary Update Script        | In-Advance DL from GitHub |
|         |         |         |         | file_oldparam_env  | Parameter Definition File taken-over from Binary File | In-Advance DL from GitHub |
|         | installer |       |         | |     |  |
|         |         | dhcp.v4.2.5 |     | dhcp-4.2.5-42.el7.centos.x86_64.rpm | DHCP Installation Package    | In-Advance DL |
|         |         | chrony.v3.2 |     | chrony-3.2-2.el7.x86_64.rpm | chrony Installation Package     | In-Advance DL |
|         |         |         |         | libseccomp-2.3.1-3.el7.x86_64.rpm | chrony Installation Package     | In-Advance DL |
|         |    | postgresql.v9.3.13  |  | postgresql93-9.3.13-1PGDG.rhel7.x86_64.rpm | PostgreSQL Installation Package | In-Advance DL |
|         |         |         |         | postgresql93-contrib-9.3.13-1PGDG.rhel7.x86_64.rpm | PostgreSQL Installation Package | In-Advance DL |
|         |         |         |         | postgresql93-devel-9.3.13-1PGDG.rhel7.x86_64.rpm | PostgreSQL Installation Package | In-Advance DL |
|         |         |         |         | postgresql93-libs-9.3.13-1PGDG.rhel7.x86_64.rpm | PostgreSQL Installation Package | In-Advance DL |
|         |         |         |         | postgresql93-server-9.3.13-1PGDG.rhel7.x86_64.rpm | PostgreSQL Installation Package | In-Advance DL |
|         |         |         |         | uuid-1.6.2-26.el7.x86_64.rpm | PostgreSQL Dependent Package | In-Advance DL |
|         |         |         |         | libxslt-1.1.28-5.el7.x86_64.rpm | PostgreSQL Dependent Package | In-Advance DL |
|         |  | pacemaker.v1.1.14-1.1 |  | pacemaker-1.1.14-1.el7.x86_64.rpm | Pacemaker Installation Package | In-Advance DL |
|         |         |         |         | corosync-2.3.5-1.el7.x86_64.rpm | Corosync Installation Package | In-Advance DL |
|         |         |         |         | crmsh-2.1.5-1.el7.x86_64.rpm | crm Command Installation Package     | In-Advance DL |
|         |         |         |         | cluster-glue-1.0.12-2.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | cluster-glue-libs-1.0.12-2.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | corosynclib-2.3.5-1.el7.x86_64.rpm | Corosync Dependent Package | In-Advance DL |
|         |         |         |         | ipmitool-1.8.13-9.el7_2.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | libqb-1.0-1.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | libtool-ltdl-2.4.2-21.el7_2.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | libxslt-1.1.28-5.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | libyaml-0.1.4-11.el7_0.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | lm_sensors-libs-3.3.4-11.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | nano-2.3.1-10.el7.x86_64.rpm | crm Dependent Package     | In-Advance DL |
|         |         |         |         | net-snmp-agent-libs-5.7.2-24.el7_2.1.x86_64.rpm | Corosync Dependent Package | In-Advance DL |
|         |         |         |         | net-snmp-libs-5.7.2-24.el7_2.1.x86_64.rpm | Corosync Dependent Package | In-Advance DL |
|         |         |         |         | openhpi-libs-3.4.0-2.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | OpenIPMI-libs-2.0.19-11.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | OpenIPMI-modalias-2.0.19-11.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | pacemaker-cli-1.1.14-1.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | pacemaker-cluster-libs-1.1.14-1.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | pacemaker-libs-1.1.14-1.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | pacemaker-all-1.1.14-1.1.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | perl-5.16.3-286.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | perl-Carp-1.26-244.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | perl-constant-1.27-2.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | perl-Encode-2.51-7.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | perl-Exporter-5.68-3.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | perl-File-Path-2.09-2.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | perl-File-Temp-0.23.01-3.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | perl-Filter-1.49-3.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | perl-Getopt-Long-2.40-2.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | perl-HTTP-Tiny-0.033-3.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | perl-libs-5.16.3-286.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | perl-macros-5.16.3-286.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | perl-parent-0.225-244.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | perl-PathTools-3.40-5.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | perl-Pod-Escapes-1.04-286.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | perl-podlators-2.5.1-3.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | perl-Pod-Perldoc-3.20-4.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | perl-Pod-Simple-3.28-4.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | perl-Pod-Usage-1.63-3.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | perl-Scalar-List-Utils-1.27-248.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | perl-Socket-2.010-3.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | perl-Storable-2.45-3.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | perl-Text-ParseWords-3.29-4.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | perl-threads-1.87-4.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | perl-threads-shared-1.43-6.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | perl-TimeDate-2.30-2.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | perl-Time-HiRes-1.9725-3.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | perl-Time-Local-1.2300-2.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | pm_crmgen-2.1-1.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | pm_diskd-2.2-1.el7.x86_64.rpm | Diskd RA Package   | In-Advance DL |
|         |         |         |         | pm_extras-2.2-1.el7.x86_64.rpm | VIPCheck RA Package | In-Advance DL |
|         |         |         |         | pm_logconv-cs-2.2-1.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | psmisc-22.20-9.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | pssh-2.3.1-5.el7.noarch.rpm | crm Dependent Package     | In-Advance DL |
|         |         |         |         | python-dateutil-1.5-7.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | python-lxml-3.2.1-4.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
|         |         |         |         | resource-agents-3.9.7-1.2.6f56.el7.x86_64.rpm | Standard RA Package Incl. Virtual IPRA | In-Advance DL |
|         | | sysstat-11.6.0-1 |        | sysstat-11.6.0-1.x86_64.rpm | Sysstat Installation Package | In-Advance DL |
|         |         |         |         | lm_sensors-libs-3.3.4-11.el7.x86_64.rpm | Sysstat Dependent Package | In-Advance DL |
|         |         | flask-0.12.2 |    | Flask-0.12.2-py2.py3-none-any.whl | Flask Installation Package   | In-Advance DL |
|         |         |         |         | click-6.7-py2.py3-none-any.whl | Flask Dependent Package   | In-Advance DL |
|         |         |         |         | itsdangerous-0.24.tar.gz | Flask Dependent Package   | In-Advance DL |
|         |         |         |         | Jinja2-2.9.6-py2.py3-none-any.whl | Flask Dependent Package   | In-Advance DL |
|         |         |         |         | MarkupSafe-1.0.tar.gz | Flask Dependent Package   | In-Advance DL |
|         |         |         |         | Werkzeug-0.12.2-py2.py3-none-any.whl | Flask Dependent Package   | In-Advance DL |
|         |         |         |         | Flask_Cors-3.0.6-py2.py3-none-any.whl | Package corresponding to CORS | In-Advance DL |
|         |  | expect-5.45-14 |         | expect-5.45-14.el7_1.x86_64.rpm | expect Installation Package   | In-Advance DL |
|         |         |         |         | tcl-8.5.13-8.el7.x86_64.rpm | expect Dependent Package   | In-Advance DL |
|         |   | bc-1.06.95-13 |         | bc-1.06.95-13.el7.x86_64.rpm      | bc Installation Package   | In-Advance DL |
|         | script  | \-        | \-      | \-      | \-      | \-      |
|         |         |         |         | pm_crmgen_env.xls | Resource Agent Configuration File | In-Advance DL |
|         |         |         |         | create_table.sql | Table Creation Script   | In-Advance DL from GitHub  |
|         |         |         |         | delete_data.sql  | DB Record Deletion Script | In-Advance DL from GitHub  |
|         |         |         |         | drop_table.sql   | Table Deletion Script   | In-Advance DL from GitHub  |
|         |         | delete_deviceconfigurationinfo | |  |    |   |
|         |         |         |         | delete_deviceconfigurationinfo_record.sh | Script for DB and device config information record deletion   | In-Advance DL from GitHub  |
|         |         |         | sql_files | | |  |
|         |         |         |         | delete_recode.sql  | SQL File for DB and device config information record deletion | In-Advance DL from GitHub  |
|         |         |         |         | get_table_size.sql | SQL File for table size acquisition | In-Advance DL from GitHub  |
| Ansible |         |         |         |           |               |         |
|         |         |         |         | ansible-2.4.2.0-2.el7.noarch.rpm | Ansible Installation Package   | In-Advance DL  |
|         |         |         |         | PyYAML-3.10-11.el7.x86_64.rpm | Ansible Dependent Package   | In-Advance DL  |
|         |         |         |         | libyaml-0.1.4-11.el7_0.x86_64.rpm | Ansible Dependent Package   | In-Advance DL  |
|         |         |         |         | openssl-1.0.2k-8.el7.x86_64.rpm | Ansible Dependent Package   | In-Advance DL  |
|         |         |         |         | openssl-libs-1.0.2k-8.el7.x86_64.rpm | Ansible Dependent Package   | In-Advance DL  |
|         |         |         |         | python-babel-0.9.6-8.el7.noarch.rpm | Ansible Dependent Package   | In-Advance DL  |
|         |         |         |         | python-backports-1.0-8.el7.x86_64.rpm | Ansible Dependent Package   | In-Advance DL  |
|         |         |         |         | python-backports-ssl_match_hostname-3.4.0.2-4.el7.noarch.rpm | Ansible Dependent Package   | In-Advance DL  |
|         |         |         |         | python-cffi-1.6.0-5.el7.x86_64.rpm | Ansible Dependent Package   | In-Advance DL  |
|         |         |         |         | python-enum34-1.0.4-1.el7.noarch.rpm | Ansible Dependent Package   | In-Advance DL  |
|         |         |         |         | python-httplib2-0.9.2-1.el7.noarch.rpm | Ansible Dependent Package   | In-Advance DL  |
|         |         |         |         | python-idna-2.4-1.el7.noarch.rpm | Ansible Dependent Package   | In-Advance DL  |
|         |         |         |         | python-ipaddress-1.0.16-2.el7.noarch.rpm | Ansible Dependent Package   | In-Advance DL  |
|         |         |         |         | python-jinja2-2.7.2-2.el7.noarch.rpm | Ansible Dependent Package   | In-Advance DL  |
|         |         |         |         | python-markupsafe-0.11-10.el7.x86_64.rpm | Ansible Dependent Package   | In-Advance DL  |
|         |         |         |         | python-paramiko-2.1.1-2.el7.noarch.rpm | Ansible Dependent Package   | In-Advance DL  |
|         |         |         |         | python-passlib-1.6.5-2.el7.noarch.rpm | Ansible Dependent Package   | In-Advance DL  |
|         |         |         |         | python-ply-3.4-11.el7.noarch.rpm | Ansible Dependent Package   | In-Advance DL  |
|         |         |         |         | python-python-pycparser-2.14-1.el7.noarch.rpm | Ansible Dependent Package   | In-Advance DL  |
|         |         |         |         | python-setuptools-0.9.8-7.el7.noarch.rpm | Ansible Dependent Package   | In-Advance DL  |
|         |         |         |         | python-six-1.9.0-2.el7.noarch.rpm | Ansible Dependent Package   | In-Advance DL  |
|         |         |         |         | python2-cryptography-1.7.2-1.el7.x86_64.rpm | Ansible Dependent Package   | In-Advance DL  |
|         |         |         |         | python2-jmespath-0.9.0-3.el7.noarch.rpm | Ansible Dependent Package   | In-Advance DL  |
|         |         |         |         | python2-pyasn1-0.1.9-7.el7.noarch.rpm | Ansible Dependent Package   | In-Advance DL  |
|         |         |         |         | sshpass-1.06-2.el7.x86_64.rpm | Ansible Dependent Package   | In-Advance DL  |

### 2.1.1. Hardware Operating environment

It is recommended to operate the software on the following Linux
computer environment.

Table 2-1 Recommended Hardware Configuration

| No.  | Computer      | Minimum Configuration                |
|------|---------------|--------------------------------------|
| 1.   | OS            | CentOS7.2 x86\_64 \*                    |
| 2.   | CPU           | IntelR XeonR CPU E5-2420 v2 @2.20GHz <br> 6 Core/12 Thread or greater |
| 3.   | Memory        | 32GB or larger                       |
| 4.   | HD Free Space | 500G or larger                       |
| 5.   | NIC           | More than 1 port                     |

\* : You need to install it from CentOS-7-x86_64-DVD-1511.iso file.

### 2.1.2. Software Operating environment
Assume that firewalld has already been installed as a package.
If you install this application by the internet using a proxy server, 
you need to confirm that target servers are able to accsess the internet by https and http protcol.
Also assume that wget has already been installed as a package.


## 3. Installation of Controller Server

The instructions described in this section must be performed by the root
user unless any specific user is specified.

**&lt;Execution Host: Ansible&gt;**

Create a working folder where the files generated in the process of
installation are located.

(It will be deleted when the installation of Controller Server is
completed.)

**\[mkdir \~/setup\] \[Enter\]**

In case of non-connected Internet environment,
locate the em folder which is configured as described in \"1.5
Configuration of the Included Accessories \" above in the working
folder. (The Ansible folder is unnecessary.)<br>

3.1. Ansible Installation
--------------------------

**&lt;Execution Host: Ansible&gt;**

Before Installation, place the rpm files in Ansible installation destination server.
The placement targets are the files under the Anslbile folder described in \"1.5 Configuration of the Included Accessories \".<br>
(Locations: /root/setup/Ansible)

Execute the following command to install Ansible.

**\[cd /root/setup/Ansible\] \[Enter\]**

**\[rpm -Uvh \*rpm\] \[Enter\]**


3.2. Controller Server Installation
--------------------------

### 3.2.1. Prepare Installation

### 3.2.1.1. Deploy SSH key

**&lt;Execution Host: Ansible&gt;**

Generate the SSH authentication key with the following command.

**\[ssh -keygen -t rsa\] \[Enter\]**

After that, copy the generated key to the target servers.

**\[scp \~/.ssh/id_rsa.pub root@$REMOTE_IP:\~\] \[Enter\]**

($REMOTE_IP: IP of the install target server (EM or DB))

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command on each server.

Check whether the directory for locating SSH key is available or not. 

**\[ls /root/.ssh/\] \[Enter\]**

If it is not available, login to the host(your server) to be executed by using SSH to create the directory for locating SSH key.

**\[ssh root@localhost\] \[Enter\]**

Locate the SSH key in the designated place.

**\[cd /root/.ssh/\] \[Enter\]**

**\[touch authorized_keys\] \[Enter\]**

**\[chmod 600 authorized_keys\] \[Enter\]**

**\[cat ~/id_rsa.pub >> authorized_keys\] \[Enter\]**

**\[rm ~/id_rsa.pub\] \[Enter\]**


### 3.2.1.2. Deploy Instllation Files

**&lt;Execution Host: Ansible&gt;**

Before Installation, place the playbook file in Ansible installation destination server.<br>
A set of Playbooks can be download at the URL below.

> Download URL : https://github.com/multi-service-fabric/element-controller/tree/master/playbook <br>

(Locations: /root/setup/playbook/)<br>
If you do not use the Internet connection, place rpm files for install.


#### 3.2.1.3. Edit playbook
Write the IP information of EM and DB to the host file (/root/setup/playbook/EM/hosts) which use by playbook.
Also, put the yml files which has environmental information for each server to the vars folder (/root/setup/playbook/EM/vars/).


##### 3.2.1.3.1. Edit host file
Figure 3-1 shows the configuration example for file : /root/setup/playbook/EM/hosts.

![Figure 3-1 Figure 3-1 An example of hosts configuration.](img/Fig_3_1_EM.png "Fig3-1")<br>
Figure 3-1 An example of hosts configuration.

##### 3.2.1.3.2. Deploy vars file
The follwing are the files located within /root/setup/playbook/EM/vars/.<br>
 Table 3-1 lists the setting values for configuration

On the variables of which the recommened value are decribed in column “description”,
You can set the recommended values, if you do not need to set any specific values.

EM ACT server configuration file：em1.yml(See column“EM”in table 3-1)<br>
EM SBY server configuration file：em2.yml(See column“EM in table 3-1)<br>
DB server configuration file：db1.yml(See column“DB in table 3-1)<br>
Common configuration file：common.yml(See column“Common in table 3-1)


Table 3-1 vars Parameter

| name                | Description                                                                                                                                                                                                  | EM | DB | Common |
|---------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----|----|--------|
| rpm_path            | In the case of using network connection, the path of installing file location. <br> In the case of no network connection, it is installing files path in the Ansible server.(Recommendation: /root/setup/em) | × | × |   ○   |
| em_path             | The path of EM location. (Recommendation: /opt/em).                                                                                                                                                          | ○ | × |   ×   |
| download_flag       | Parameter for determining whether to acquire a file from the Internet or place it on an Ansible server. <br> If True, use the Internet connection.                                                           | ○ | ○ |   ×   |
| log_path            | Relative path of EM log file output destination. <br> (Recommendation: logs/em/log)                                                                                                                          | ○ | × |   ×   |
| installing_em_path  | The path of EM source folder location in Ansible Server. <br> (Recommendation: /root/setup/em)                                                                                                               | ○ | × |   ×   |
| db_address          | DB server IP address.                                                                                                                                                                                        | ○ | ○ |   ×   |
| db_name             | DB name.  (Recommendation: msf_em_1)                                                                                                                                                                         | ○ | ○ |   ×   |
| em_physical_address | EM physical IP address.                                                                                                                                                                                      | ○ | × |   ×   |
| ec_rest_address     | EC REST IP address.                                                                                                                                                                                          | ○ | × |   ×   |
| ec_rest_port        | EC REST port. (Recommendation: 18080)                                                                                                                                                                        | ○ | × |   ×   |
| em_listening_address| EM netconf, REST IP address.                                                                                                                                                                                 | ○ | × |   ×   |
| em_netconf_port     | EM netconf port. (Recommendation: 831)                                                                                                                                                                       | ○ | × |   ×   |                                                                                                                                                                                        | ○ | × |   ×   |
| em_rest_port        | EM REST port. (Recommendation: 8080)                                                                                                                                                                         | ○ | × |   ×   |
| controller_cidr     | The network name of the server that the DB allows for connections. (CIDR)                                                                                                                                    | ○ | ○ |   ×   |
| ntp_server_address  | NTP server address.                                                                                                                                                                                          | ○ | × |   ×   |
| ha_flag             | Flag indicating whether to implement redundancy. In the case of truth it is implemented.                                                                                                                     | ○ | × |   ×   |
| act_address         | Inter connect IP address for act server. (When ha_flag is False, it is set to none)                                                                                                                          | ○ | ○ |   ×   |
| act_node_name       | Name for act server. (When ha_flag is False, it is set to none)                                                                                                                                              | ○ | ○ |   ×   |
| sby_address         | Inter connect IP address for stand-by server. (When ha_flag is False, it is set to none)                                                                                                                     | ○ | ○ |   ×   |
| sby_node_name       | Name for stand-by server. (When ha_flag is False, it is set to none)                                                                                                                                         | ○ | ○ |   ×   |
| cluster_name        | Cluster name (When ha_flag is False, it is set to none) <br> (Recommendation: em_cluster)                                                                                                                    | ○ | ○ |   ×   |
| oppo_login_address  | Log-in address of opposite controller. (When ha_flag is False, it is set to none)                                                                                                                            | ○ | × |   ×   |
| oppo_usrname        | Log-in user name of opposite controller. (When ha_flag is False, it is set to none)                                                                                                                          | ○ | × |   ×   |
| oppo_password       | Log-in password of opposite controller. (When ha_flag is False, it is set to none)                                                                                                                           | ○ | × |   ×   |
| install_flag        | When setting the DB, it decides whether to install PostgreSQL. <br> In case of True, execute installation.                                                                                                   | × | ○ |   ×   |

#### 3.2.1.4. Delete existing DB
If the same name DB (db_name specified in the vars file) already exists in the installation DB server, it is necessary to delete it beforehand.

**&lt;Execution Host: DB&gt;**

Execute the following command and delete DB with postgres user.

**\[su - postgres\] \[Enter\]**

**\[dropdb \[DB name\]\] \[Enter\]**

### 3.2.2. Execute Installation
**&lt;Execution Host: Ansible&gt;**

Execute the following command to install this application.

**\[cd /root/setup/playbook/EM] \[Enter\]**

**\[ansible-playbook em.yml -i hosts\] \[Enter\]**


### 3.2.3. Edit Configuration

#### 3.2.3.1. Edit of EM configure file
The settings required for the operation (IP,port,file path etc...) are automatically replaced with the parameters at the time of installation.

If you want to change other setting, you need to fix it by hand.

Change the EM Module configuration file by use of the following command.

**\[vi \$EM\_HOME/conf/\[File Name\]\] \[Enter\]**

\* See "element_manager_configuration_specifications" for changed config.

On the Configuration File for CGW-SH Device Setting Management, the sample configuration file is located.

In accordance with your environment, edit this sample file and change the file name by using the following commands.

**\[vi $EM_HOME/conf/cgwsh_device/conf_asr_device_sample1.conf\] \[Enter\]**

**\[vi $EM_HOME/conf/cgwsh_device/conf_nvr_device_sample1.conf\] \[Enter\]**

**\[mv $EM_HOME/conf/cgwsh_device/conf_asr_device_sample1.conf $EM_HOME/conf/cgwsh_device/conf_asr_device_CGW-SHdevice(ASR)device.conf\] \[Enter\]**

**\[mv $EM_HOME/conf/cgwsh_device/conf_nvr_device_sample1.conf $EM_HOME/conf/cgwsh_device/conf_nvr_device_CGW-SHdevice(NVR)device.conf\] \[Enter\]**

\* The file name after the modification is an example.<br>
\* See "element_manager_configuration_specifications" for changed config.

#### 3.2.3.2. Making of crm File

**&lt;Execution Host: ACT&gt;**

Edit the pm\_crmgen\_env.xls file, which has the configuration of resource
agent in the included accessories, for updating the necessary
information, then convert it to a csv file and locate in the home folder
of the active system.

Execute the following command at the folder where you locate the csv
file to convert it into a crm file that is used for registering it to
the resource agent.

**\[pm\_crmgen -o \$EM\_HOME/conf/crm\_conf.crm (located csv file name).csv\] \[Enter\]**

If the conversion completes successfully, nothing will be displayed in
the screen but in case anything went wrong with the csv file, the
location to be amended would be displayed.

*1.  Make sure to acquire the file “pm_crmgen_env.xls” from the following URL.<br>
URL : https://github.com/linux-ha-japan/pm_crmgen-1.0/blob/master/pm_crmgen_env.xls <br>
See sheet : pm_crmgen_environment definition(1.1)

In addition, please follow the procedures shown below (Figure 3-2 Cluster property to Figure 3-11 Resource activation order restriction.)  when editing the file “pm_crmgen_env.xls”.<br>
Moreover, add new lines to the original file when required.<br>

Since the following values in the figure are examples, you need to change the value.<br>
You should replace the following bold text with the values in Table 3-1 vars Parameter.

EM_CONTROL_SHELL (Figure 3-5) : __em_path__/bin/em_ctl.sh (absolute path)<br>
device (Figure 3-6) : Target physical volumes of disk check<br>
target_ip (Figure 3-7) : The same value as __em_listening_address__.<br>
ip (Figure 3-8) : The same value as __em_listening_address__.<br>
nic (Figure 3-8) : Name of the NIC to which the virtual IP address is assigned.<br>
cidr_netmask (Figure 3-8) : The same value as __controller_cidr__.<br>
Value of line which score is 200.(Figure 3-9) : The same value as __act_node_name__.<br>
Value of line which score is 100.(Figure 3-9) : The same value as __sby_node_name__.<br>

![Figure 3-2 Cluster property](img/Fig_3_2_EM.png "Fig3-2")<br>
Figure 3-2 Cluster property

![Figure 3-3 Resource default](img/Fig_3_3_EM.png "Fig3-3")<br>
Figure 3-3 Resource default

![Figure 3-4 Resource structure](img/Fig_3_4_EM.png "Fig3-4")<br>
Figure 3-4 Resource structure

![Figure 3-5 Primitive resource (id=prmEM)](img/Fig_3_5_EM.png "Fig3-5")<br>
Figure 3-5 Primitive resource (id=prmEM)

![Figure 3-6 Primitive resource (id=prmDiskd)](img/Fig_3_6_EM.png "Fig3-6")<br>
Figure 3-6 Primitive resource (id=prmDiskd)

![Figure 3-7 Primitive resource (id=vipCheck)](img/Fig_3_7_EM.png "Fig3-7")<br>
Figure 3-7 Primitive resource (id=vipCheck)

![Figure 3-8 Primitive resource (id=prmIP)](img/Fig_3_8_EM.png "Fig3-8")<br>
Figure 3-8 Primitive resource (id=prmIP)

![Figure 3-9 Resource location restriction](img/Fig_3_9_EM.png "Fig3-9")<br>
Figure 3-9 Resource location restriction

![Figure 3-10 Resource colocation restriction](img/Fig_3_10_EM.png "Fig3-10")<br>
Figure 3-10 Resource colocation restriction

![Figure 3-11 Resource activation order restriction](img/Fig_3_11_EM.png "Fig3-11")<br>
Figure 3-11 Resource activation order restriction

#### 3.2.3.3. Injection of crm File

**&lt;Execution Host: ACT&gt;**

With the following commend, register the resource agent.

**\[crm configure load update \$EM\_HOME/conf/crm\_conf.crm\] \[Enter\]**

If the injection completes successfully, nothing will be displayed in
the screen. So you need to check the result by following the next
instruction. (\*Although a message which says the configured number of
seconds for VIPcheck is shorter than the default, you can ignore it and
keep on going.)

If there is any critical error in the configuration, a warning with the
location of the error will be displayed and you will be prompted to
answer with Y/N whether you want to keep the injection going or not.
When this warning is displayed, there must be errors in the
configuration, and you should answer it by entering \[N\] \[Enter\].

#### 3.2.3.4. Registration of periodic executed tool for deleting device config information records
**&lt;Execution Host: DB&gt;**

You need to set by using cron in order that delete_deviceconfigurationinfo_record.sh is periodically executed.

Execute the following command to open the configuration file for cron.

**\[crontab -u root -e\] \[Enter\]**

The editor will start up after the above command is executed.<br>
See below for the setting method. 

(For setting crontab) <br>
     m h d M X exec <br>
     [note] m:minute, h:hour,d:day, M:Month,X:day of the week exec: executing command <br>
     The command designated in "exec" is executed at the designated time. <br>
     In case of \*, all values to be designated are executed. <br>
     In case of \*/z, in the range of the values which can be designated, the command is executed at Z intervals. 
     (Example) <br>
     In case of \*/20 \* \* \* \* exec, <br>
     "exec" is executed at 20 minutes intervals("m" can be set beween 0 and 59)


(Example 1) In case the executing interval is one month, <br>
   0 0 1 \*/1 \* /root/em_config_delete/delete_deviceconfigurationinfo_record.sh <br>
   If  you change the months for the interval, you can change “/1” in example 1. <br>

(Example 2) In case the executing interval is 7 days, <br>
   0 0 \*/7 \* \* /root/em_config_delete/delete_deviceconfigurationinfo_record.sh <br>
   If  you change the months for the interval, you can change “/7” in example 2. <br>


3.3. Confirm Setting
------------------

#### 3.3.1. Confirmation of Python Library Installation

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command to view the list of installed libraries
and the version of each library.

**\[pip list\] \[Enter\]**

If the installation of each library has been completed successfully,
the following information will be displayed in the list.


alembic

Babel

certifi

cffi

chardet

click

cryptography

debtcollector

decorator

enum34

Flask

Flask-Cors

funcsigs

idna

iniparse

ipaddress

iso8601

itsdangerous

Jinja2

lxml

Mako

MarkupSafe

monotonic

ncclient

netaddr

netconf

netifaces

oslo.config

oslo.context

oslo.db

oslo.i18n

oslo.utils

paramiko

pbr

positional

psycopg2

pyasn1

pycparser

pyparsing

python-editor

pytz

requests

rfc3986

setuptools

six

SQLAlchemy

sqlalchemy-migrate

sqlparse

sshutil

stevedore

Tempita

urllib3

Werkzeug

wrapt

xmltodict


### 3.3.2. Confirmation of PIP Installation

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command to confirm the version.

**\[pip \--version\] \[Enter\]**

If the installation has been completed successfully, the following
message will be displayed.

> pip 8.1.2 from /usr/lib/python2.7/site-packages/pip-8.1.2-py2.7.egg
> (python 2.7)


### 3.3.3. Confirmation of firewall configuration

Confirm the current configuration by executing the following command
(especially for the highlighted section).

**\[firewall-cmd \--list-all\] \[Enter\]**

**&lt;Execution Host: ACT/SBY/DB&gt;**

>public (default, active)
>
>interfaces:
>
>sources:
>
>services: dhcpv6-client ntp `high-availability` ssh
>
>ports: `830/tcp` `8080/tcp`
>
>masquerade: no
>
>forward-ports:
>
>icmp-blocks:
>
>rich rules:

**&lt;Execution Host: DB&gt;**

>public (default, active)
>
>interfaces:
>
>sources:
>
>services: dhcpv6-client ssh
>
>ports: `5432/tcp`
>
>masquerade: no
>
>forward-ports:
>
>icmp-blocks:
>
>rich rules:


### 3.3.4. Confirmation of Chrony behavior

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command to confirm the synchronization with the
NTP server.

**\[chronyc sources\] \[Enter\]**

&lt;The output example of successful synchronization&gt;

| MS Name/IP address  Stratum  Poll  Reach  LastRx  Last sample                                |
| -------------------------------------------------------------------------------------------- |
| \^\*   xxx.xxx.xxx.xxx         6     6   377     50    -1897ns\[-2575ns\] \+/\-   11ms       |


### 3.3.5. Confirmation of pacemaker operation

#### 3.3.5.1. Confirmation of Installation of Pacemaker

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command to confirm the version of Corosync.

**\[corosync -version\] \[Enter\]**

If the installation has been completed successfully, the following
message will be displayed.

> Corosync Cluster Engine, version \'2.3.5\'
>
> Copyright (c) 2006-2009 Red Hat, Inc.

Execute the following command to confirm the version of Pacemaker.

**\[crmadmin \--version\] \[Enter\]**

If the installation has been completed successfully, the following
message will be displayed.

> Pacemaker 1.1.14-1.el7
>
> Written by Andrew Beekhof

Execute the following command to confirm the version of crm.

**\[crm \--version\] \[Enter\]**

If the installation has been completed successfully, the following
message will be displayed.

> 2.1.5-1.el7 (Build unknown)

Execute the following command to confirm the resource agent which is
going to be used is actually installed.

**\[ls /lib/ocf/resource.d/pacemaker/\] \[Enter\]**

If the installation has been completed successfully, the following
message will be displayed.

> diskd

Execute the following command to confirm the resource agent which is
going to be used is actually installed.

**\[ls /lib/ocf/resource.d/heartbeat/\] \[Enter\]**

If the installation has been completed successfully, the following
message will be displayed.

> VIPcheck、IPaddr2

Confirm the configuration of the hosts

**\[ping "Stand-by Host Name"\] \[Enter\]**

> PING "Stand-by Host Name" (IP address for the stand-by
> interconnection) 56(84) bytes of data.
>
> 64 bytes from "Stand-by Host Name" (IP address for the stand-by
> interconnection): icmp\_seq=1 ttl=64 time=0.166 ms

**\[ping "Active Host Name"\] \[Enter\]**

> PING "Active Host Name" (IP address for the active interconnection)
> 56(84) bytes of data.
>
> 64 bytes from "Active Host Name" (IP address for the active
> interconnection): icmp\_seq=1 ttl=64 time=0.166 ms

In case the IP address and the Host Name are not displayed like this,
review the configuration at /etc/hosts.

#### 3.3.5.2. Confirmation of the Inter-node Communication Status

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command to confirm the status of inter-node
communication by use of \"corosync-cfgtool -s\" command.

This task must be performed both at the active and the stand-by nodes.

**\[corosync-cfgtool -s\] \[Enter\]**

If the cluster is started successfully, the following message will be
displayed in the screen.

When the \"status\" is \"active\" and \"no faults\", the communication
is working properly.

> Printing ring status.
>
> Local node ID (1 or 2)
>
> RING ID 0
>
> id = (IP address of the Active or Stand-by system)
>
> status = ring 0 active with no faults

#### 3.3.5.3. Confirmation of the Result of Injection

**&lt;Execution Host\: ACT or SBY&gt;**

Confirm the operational status of resource agent with the following
command.


**\[crm\_mon -fA -1\] \[Enter\]**

If it injected successfully, a message will be displayed as follows.

> Last updated: WDW MMM DD HH:MM:SS YYYY Last change: WDW MMM DD
> HH:MM:SS YYYY by root via cibadmin on (Active Node Name or Stand-by
> Node Name)
>
> Stack: corosync
>
> Current DC: (Active Node Name or Stand-by Node Name) (version
> 1.1.14-1.el7-70404b0) - partition with quorum
>
> 2 nodes and 4 resources configured
>
> Online: \[(Active Node Name) (Stand-by Node Name)\]
>
> Resource Group: grpEC
>
> vipCheck (VIPcheck): Started (Active Node Name))
>
> prmIP (IPaddr2): Started (Active Node Name)
>
> prmEM (em): Started (Active Node Name)
>
> Clone Set: clnDiskd \[prmDiskd\]
>
> Started: \[(Active Node Name) (Stand-by Node Name)\]
>
> Node Attribute:
>
> \* Node (Active Node Name)
>
> \+ diskcheck\_status\_internal : normal
>
> \* Node (Stand-by Node Name)
>
> \+ diskcheck\_status\_internal : normal
>
> Migration Summary:
>
> \* Node (Active Node Name)
>
> \* Node (Stand-by Node Name)
> Summary:
>
> \* Node (Active Node Name)
>
> \* Node (Stand-by Node Name)

### 3.3.6. Confirmation of sysstat(sar) installation

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command to show the installed rpms and their versions.

**\[rpm -qa | grep -e sysstat\] \[Enter\]**

If the installation has been completed successfully, the following message in the list will be displayed.

> sysstat-11.6.0-1.x86_64

### 3.3.7. Confirmation of expect installation

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command to show the installed rpms and their versions.

**\[rpm -qa | grep -e expect -e tcl-8.5.13\] \[Enter\]**

If the installation has been completed successfully, the following message in the list will be displayed.

> tcl-8.5.13-8.el7.x86_64
>
> expect-5.45-14.el7_1.x86_64

### 3.3.8. Confirmation of bc installation

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command to show the installed rpms and their versions.

**\[rpm -qa | grep -e bc-1.06\] \[Enter\]**

If the installation has been completed successfully, the following message in the list will be displayed.

> bc-1.06.95-13.el7.x86_64

