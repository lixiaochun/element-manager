# Element Manager Automate Installation Manual

**Version 1.0**
**March 28, 2018**
**Copyright(c) 2018 Nippon Telegraph and Telephone Corporation**

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

1.3. Expressional Conventions
------------------------

There are certain expressions and text styles conventionally used in
this document. Please make yourself clear about the items below before
going on through the document.

**\[XX XX\]** - bold letters surrounded by square brackets

This means the command to be entered in Linux.

**X \[Enter\]** - bold letter and \"\[Enter\]\"

> In this case, you need to enter the letters within brackets and press
> the Enter key in the console screen.

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

Table 1-1 Included Accessories

| \#      | Folder Structure  | | | File Name    | Descriprion | Remarks |
|---------|---------|---------|---------|---------|---------|---------|
| 1.      | em      | \-      | \-      | \-      | \-      | \-      |
| 2.      |         | bin     |         | em      | Resource Agent | In-Advance DL from GitHub  |
| 3.      |         |         |         | em_ctl.sh | EM Start-up Script      | In-Advance DL from GitHub  |
| 4.      |         |         |         | EmMonitor.py | Alive Monitor Client   | In-Advance DL from GitHub  |
| 5.      |         |         |         | controller_status.sh | Controller Status Information<br> Acquisition Script | In-Advance DL from GitHub  |
| 6.      |         | lib     |         | MsfEmMain.py | Main Module    | In-Advance DL from GitHub  |
| 7.      |         |         |         | GlobalModule.py | Global Module  | In-Advance DL from GitHub  |
| 8.      |         |         |         | EmCommonLog.py | EM Common Log Module      | In-Advance DL from GitHub  |
| 9.      |         |         |         | EmSetPATH.py | PYTHONPATH Configuration Module for EM | In-Advance DL from GitHub  |
| 10.      |         |         |         | EmLoggingFormatter.py | Log Formater Module for EM     | In-Advance DL from GitHub  |
| 11.      |         |         |         | \__init__.py | Initialization Module | In-Advance DL from GitHub  |
| 12.      |         |         | CommonDriver | EmCommonDriver.py | Driver Common Part Module  | In-Advance DL from GitHub  |
| 13.      |         |         |         | \__init__.py | Initialization Module | In-Advance DL from GitHub  |
| 14.      |         |         | Config  | EmConfigManagement.py | Configuration Management Module | In-Advance DL from GitHub  |
| 15.      |         |         |         | \__init__.py | Initialization Module | In-Advance DL from GitHub  |
| 16.      |         |         | DB      | EmDBControl.py | DB Control Module      | In-Advance DL from GitHub  |
| 17.      |         |         |         | \__init__.py | Initialization Module | In-Advance DL from GitHub  |
| 18.      |         |         | DriverUtility | EmDriverCommonUtilityDB.py | Driver Common Utility (DB) Module  | In-Advance DL from GitHub  |
| 19.      |         |         |         | EmDriverCommonUtilityLog.py | Driver Common Utility (Log) Module  | In-Advance DL from GitHub  |
| 20.      |         |         |         | \__init__.py | Initialization Module | In-Advance DL from GitHub  |
| 21.      |         |         | Netconf Serve | EmNetconfServer.py | EM Netconf Server Module      | In-Advance DL from GitHub  |
| 22.      |         |         |         | \__init__.py | Initialization Module | In-Advance DL from GitHub  |
| 23.      |         |         | OrderflowControl | EmOrderflowControl.py | Order Flow Control Module   | In-Advance DL from GitHub  |
| 24.      |         |         |         | \__init__.py | Initialization Module | In-Advance DL from GitHub  |
| 25.      |         |         | Protocol | EmNetconfProtocol.py | For-device Protocol Process Module | In-Advance DL from GitHub  |
| 26.      |         |         |         | EmCLIProtocol.py | Protocol Processing (CLI) Module for Devices | In-Advance DL from GitHub  |
| 27.      |         |         |         | \__init__.py | Initialization Module | In-Advance DL from GitHub  |
| 28.      |         |         | RestScenario | EmControllerLogGet.py | Controller Log Acquisition Scenario | In-Advance DL from GitHub  |
| 29.      |         |         |         | EmControllerStatusGet.py | Controller Status Acquisition Scenario | In-Advance DL from GitHub  |
| 30.      |         |         |         | EmSeparateRestScenario.py | REST Individual Scenario Module    | In-Advance DL from GitHub  |
| 31.      |         |         |         | \__init__.py | Initialization Module | In-Advance DL from GitHub  |
| 32.      |         |         | RestServer | EmRestServer.py | REST Server Module    | In-Advance DL from GitHub  |
| 33.      |         |         |         | \__init__.py | Initialization Module | In-Advance DL from GitHub  |
| 34.      |         |         | Scenario | EmBLeafDelete.py | B-Leaf Deletion Scenario  | In-Advance DL from GitHub  |
| 35.      |         |         |         | EmBLeafMerge.py | B-Leaf Generation Scenario  | In-Advance DL from GitHub  |
| 36.      |         |         |         | EmBLeafScenario.py | B-Leaf Scenario Modulef  | In-Advance DL from GitHub  |
| 37.      |         |         |         | EmBLeafUpdate.py | B-Leaf Update Scenario  | In-Advance DL from GitHub  |
| 38.      |         |         |         | EmBreakoutIFDelete.py | BreakoutIF Deletion Scenario | In-Advance DL from GitHub  |
| 39.      |         |         |         | EmBreakoutIFMerge.py | BreakoutIF Registration Scenario | In-Advance DL from GitHub  |
| 40.      |         |         |         | EmCeLagDelete.py | LAG Deletion Scenario for CE     | In-Advance DL from GitHub  |
| 41.      |         |         |         | EmCeLagMerge.py | LAG Addition Scenario for CE     | In-Advance DL from GitHub  |
| 42.      |         |         |         | EmClusterLinkDelete.py | Inter-Claster Link I/F Deletion Scenario | In-Advance DL from GitHub  |
| 43.      |         |         |         | EmClusterLinkMerge.py | Inter-Claster Link I/F Addition Scenario | In-Advance DL from GitHub  |
| 44.      |         |         |         | EmDeleteScenario.py | Resource Deletion Scenario Module | In-Advance DL from GitHub  |
| 45.      |         |         |         | EmInternalLinkDelete.py | Internal Link Delete Scenario | In-Advance DL from GitHub  |
| 46.      |         |         |         | EmInternalLinkMerge.py | Internal Link Merge Scenario | In-Advance DL from GitHub  |
| 47.      |         |         |         | EmL2SliceEvpnControl.py | L2 Slice EVPN Control Scenario | In-Advance DL from GitHub  |
| 48.      |         |         |         | EmL2SliceDelete.py | L2 Slice Deletion Scenario      | In-Advance DL from GitHub  |
| 49.      |         |         |         | EmL2SliceGet.py | L2 Slice Information Adjustment Scenario      | In-Advance DL from GitHub  |
| 50.      |         |         |         | EmL2SliceMerge.py | L2 Slice Addition Scenario      | In-Advance DL from GitHub  |
| 51.      |         |         |         | EmL2SliceUpdate.py | L2 Slice Update Scenario      | In-Advance DL from GitHub  |
| 52.      |         |         |         | EmL3SliceDelete.py | L3 Slice Deletion Scenario      | In-Advance DL from GitHub  |
| 53.      |         |         |         | EmL3SliceGet.py | L3 Slice Information Adjustment Scenario      | In-Advance DL from GitHub  |
| 54.      |         |         |         | EmL3SliceMerge.py | L3 Slice Addition Scenario      | In-Advance DL from GitHub  |
| 55.      |         |         |         | EmL3SliceUpdate.py | L3 Slice Update Scenario      | In-Advance DL from GitHub  |
| 56.      |         |         |         | EmLeafDelete.py | Leaf Deletion Scenario    | In-Advance DL from GitHub  |
| 57.      |         |         |         | EmLeafMerge.py | Leaf Addition Scenario    | In-Advance DL from GitHub  |
| 58.      |         |         |         | EmMergeScenario.py | Resource Addition Scenario Module | In-Advance DL from GitHub  |
| 59.      |         |         |         | EmRecover.py | Recover Node Scenario | In-Advance DL from GitHub  |
| 60.      |         |         |         | EmRecoverNode.py | Recover Node Scenario | In-Advance DL from GitHub  |
| 61.      |         |         |         | EmRecoverService.py | Recover Node Scenario | In-Advance DL from GitHub  |
| 62.      |         |         |         | EmSpineDelete.py | Spine Deletion Scenario   | In-Advance DL from GitHub  |
| 63.      |         |         |         | EmSpineMerge.py | Spine Addition Scenario   | In-Advance DL from GitHub  |
| 64.      |         |         |         | EmSeparateScenario.py | Individual Scenario Module | In-Advance DL from GitHub  |
| 65.      |         |         |         | \__init__.py | Initialization Module | In-Advance DL from GitHub  |
| 66.      |         |         | SeparateDriver | CiscoDriver.py | Cisco (5001, 5011) Driver Module       | In-Advance DL from GitHub  |
| 67.      |         |         |         | CiscoDriver5501.py | Cisco 5501 Driver Module       | In-Advance DL from GitHub  |
| 68.      |         |         |         | EmRecoverUtil.py | Recover Node Utility       | In-Advance DL from GitHub  |
| 69.      |         |         |         | JuniperDriver5100.py | Juniper 5100 Driver Module       | In-Advance DL from GitHub  |
| 70.      |         |         |         | JuniperDriver5200.py | Juniper 5200 Driver Module       | In-Advance DL from GitHub  |
| 71.      |         |         |         | JuniperDriverMX240.py | J Company Core Router Driver Module       | In-Advance DL from GitHub  |
| 72.      |         |         |         | OcNOSDriver.py | OcNOS Driver Module   | In-Advance DL from GitHub  |
| 73.      |         |         |         | EmSeparateDriver.py | Driver Individual Module  | In-Advance DL from GitHub  |
| 74.      |         |         |         | \__init__.py | Initialization Module | In-Advance DL from GitHub  |
| 75.      |         |         | SystemUtility | EmSysCommonUtilityDB.py | System Common (DB) Utility Module  | In-Advance DL from GitHub  |
| 76.      |         |         |         | \__init__.py | Initialization Module | In-Advance DL from GitHub  |
| 77.      |         | conf    |         | conf_driver.conf | Driver Individual Part Operational Configuration File  | In-Advance DL from GitHub  |
| 78.      |         |         |         | conf_if_process.conf | I/F Process Part Operational Configuration File     | In-Advance DL from GitHub  |
| 79.      |         |         |         | conf_scenario.conf | Scenario Individual Part Operational Configuration File | In-Advance DL from GitHub  |
| 80.      |         |         |         | conf_sys_common.conf | EM Common Configuration File      | In-Advance DL from GitHub  |
| 81.      |         |         |         | conf_separate_driver_cisco.conf | Cisco Driver Operation Configuration File       | In-Advance DL from GitHub  |
| 82.      |         |         |         | conf_if_process_rest.conf | REST Server Operation Configuration FileT    | In-Advance DL from GitHub  |
| 83.      |         |         |         | conf_scenario_rest.conf | REST Scenario Individual Part Operation Configuration File    | In-Advance DL from GitHub  |
| 84.      |         |         |         | Cisco.conf | QoS of Cisco Driver Operation Configuration File    | In-Advance DL from GitHub  |
| 85.      |         |         |         | Juniper.conf | QoS of Juniper Driver Operation Configuration File    | In-Advance DL from GitHub  |
| 86.      |         |         |         | OcNOS.conf | QoS of OcNOS Driver Operation Configuration File    | In-Advance DL from GitHub  |
| 87.      |         | installer | \-      | \-      | \-      | \-      |
| 88.      |         |         |         | whl_package.tar | In-use Python Library Package  | In-Advance DL from GitHub  |
| 89.      |         |         |         | paramiko-2.0.2-py2.py3-none-any.whl | In-use Python Library Package  | In-Advance DL |
| 90.      |         |         |         | psycopg2-2.6.2-cp27-cp27mu-linux_x86_64.whl | In-use Python Library Package  | In-Advance DL |
| 91.      |         |         |         | pip-8.1.2.tar.gz | PIP Command for Python Library Install     | In-Advance DL |
| 92.      |         |         |         | setuptools-28.6.0.tar.gz | pip Dependent Package     | In-Advance DL |
| 93.      |         |         | dhcp.v4.2.5 | dhcp-4.2.5-42.el7.centos.x86_64.rpm | DHCP Installation Package    | In-Advance DL |
| 94.      |         |         | ntp.v4.2 | autogen-libopts-5.18-5.el7.x86_64.rpm | NTP Installation Package     | In-Advance DL |
| 95.      |         |         |         | ntpdate-4.2.6p5-22.el7.centos.x86_64.rpm | NTP Installation Package     | In-Advance DL |
| 96.      |         |         |         | ntp-4.2.6p5-22.el7.centos.x86_64.rpm | NTP Installation Package     | In-Advance DL |
| 97.      |         |         | postgresql.v9.3.13 | postgresql93-9.3.13-1PGDG.rhel7.x86_64.rpm | PostgreSQL Installation Package | In-Advance DL |
| 98.      |         |         |         | postgresql93-contrib-9.3.13-1PGDG.rhel7.x86_64.rpm | PostgreSQL Installation Package | In-Advance DL |
| 99.      |         |         |         | postgresql93-devel-9.3.13-1PGDG.rhel7.x86_64.rpm | PostgreSQL Installation Package | In-Advance DL |
| 100.      |         |         |         | postgresql93-libs-9.3.13-1PGDG.rhel7.x86_64.rpm | PostgreSQL Installation Package | In-Advance DL |
| 101.      |         |         |         | postgresql93-server-9.3.13-1PGDG.rhel7.x86_64.rpm | PostgreSQL Installation Package | In-Advance DL |
| 102.      |         |         |         | uuid-1.6.2-26.el7.x86_64.rpm | PostgreSQL Dependent Package | In-Advance DL |
| 103.      |         |         |         | libxslt-1.1.28-5.el7.x86_64.rpm | PostgreSQL Dependent Package | In-Advance DL |
| 104.      |         |         | pacemaker.v1.1.14-1.1 | pacemaker-1.1.14-1.el7.x86_64.rpm | Pacemaker Installation Package | In-Advance DL |
| 105.      |         |         |         | corosync-2.3.5-1.el7.x86_64.rpm | Corosync Installation Package | In-Advance DL |
| 106.      |         |         |         | crmsh-2.1.5-1.el7.x86_64.rpm | crm Command Installation Package     | In-Advance DL |
| 107.      |         |         |         | cluster-glue-1.0.12-2.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 108.      |         |         |         | cluster-glue-libs-1.0.12-2.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 109.      |         |         |         | corosynclib-2.3.5-1.el7.x86_64.rpm | Corosync Dependent Package | In-Advance DL |
| 110.      |         |         |         | ipmitool-1.8.13-9.el7_2.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 111.      |         |         |         | libqb-1.0-1.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 112.      |         |         |         | libtool-ltdl-2.4.2-21.el7_2.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 113.      |         |         |         | libxslt-1.1.28-5.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 114.      |         |         |         | libyaml-0.1.4-11.el7_0.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 115.      |         |         |         | lm_sensors-libs-3.3.4-11.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 116.      |         |         |         | nano-2.3.1-10.el7.x86_64.rpm | crm Dependent Package     | In-Advance DL |
| 117.      |         |         |         | net-snmp-agent-libs-5.7.2-24.el7_2.1.x86_64.rpm | Corosync Dependent Package | In-Advance DL |
| 118.      |         |         |         | net-snmp-libs-5.7.2-24.el7_2.1.x86_64.rpm | Corosync Dependent Package | In-Advance DL |
| 119.      |         |         |         | openhpi-libs-3.4.0-2.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 120.      |         |         |         | OpenIPMI-libs-2.0.19-11.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 121.      |         |         |         | OpenIPMI-modalias-2.0.19-11.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 122.      |         |         |         | pacemaker-cli-1.1.14-1.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 123.      |         |         |         | pacemaker-cluster-libs-1.1.14-1.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 124.      |         |         |         | pacemaker-libs-1.1.14-1.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 125.      |         |         |         | pacemaker-all-1.1.14-1.1.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 126.      |         |         |         | perl-5.16.3-286.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 127.      |         |         |         | perl-Carp-1.26-244.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 128.      |         |         |         | perl-constant-1.27-2.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 129.      |         |         |         | perl-Encode-2.51-7.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 130.      |         |         |         | perl-Exporter-5.68-3.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 131.      |         |         |         | perl-File-Path-2.09-2.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 132.      |         |         |         | perl-File-Temp-0.23.01-3.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 133.      |         |         |         | perl-Filter-1.49-3.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 134.      |         |         |         | perl-Getopt-Long-2.40-2.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 135.      |         |         |         | perl-HTTP-Tiny-0.033-3.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 136.      |         |         |         | perl-libs-5.16.3-286.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 137.      |         |         |         | perl-macros-5.16.3-286.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 138.      |         |         |         | perl-parent-0.225-244.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 139.      |         |         |         | perl-PathTools-3.40-5.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 140.      |         |         |         | perl-Pod-Escapes-1.04-286.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 141.      |         |         |         | perl-podlators-2.5.1-3.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 142.      |         |         |         | perl-Pod-Perldoc-3.20-4.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 143.      |         |         |         | perl-Pod-Simple-3.28-4.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 144.      |         |         |         | perl-Pod-Usage-1.63-3.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 145.      |         |         |         | perl-Scalar-List-Utils-1.27-248.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 146.      |         |         |         | perl-Socket-2.010-3.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 147.      |         |         |         | perl-Storable-2.45-3.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 148.      |         |         |         | perl-Text-ParseWords-3.29-4.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 149.      |         |         |         | perl-threads-1.87-4.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 150.      |         |         |         | perl-threads-shared-1.43-6.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 151.      |         |         |         | perl-TimeDate-2.30-2.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 152.      |         |         |         | perl-Time-HiRes-1.9725-3.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 153.      |         |         |         | perl-Time-Local-1.2300-2.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 154.      |         |         |         | pm_crmgen-2.1-1.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 155.      |         |         |         | pm_diskd-2.2-1.el7.x86_64.rpm | Diskd RA Package   | In-Advance DL |
| 156.      |         |         |         | pm_extras-2.2-1.el7.x86_64.rpm | VIPCheck RA Package | In-Advance DL |
| 157.      |         |         |         | pm_logconv-cs-2.2-1.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 158.      |         |         |         | psmisc-22.20-9.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 159.      |         |         |         | pssh-2.3.1-5.el7.noarch.rpm | crm Dependent Package     | In-Advance DL |
| 160.      |         |         |         | python-dateutil-1.5-7.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 161.      |         |         |         | python-lxml-3.2.1-4.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 162.      |         |         |         | resource-agents-3.9.7-1.2.6f56.el7.x86_64.rpm | Standard RA Package Incl. Virtual IPRA | In-Advance DL |
| 163.      |         |         | sysstat-11.6.0-1 | sysstat-11.6.0-1.x86_64.rpm | Sysstat Installation Package | In-Advance DL |
| 164.      |         |         | flask-0.12.2 | Flask-0.12.2-py2.py3-none-any.whl | Flask Installation Package   | In-Advance DL |
| 165.      |         |         |         | click-6.7-py2.py3-none-any.whl | Flask Dependent Package   | In-Advance DL |
| 166.      |         |         |         | itsdangerous-0.24.tar.gz | Flask Dependent Package   | In-Advance DL |
| 167.      |         |         |         | Jinja2-2.9.6-py2.py3-none-any.whl | Flask Dependent Package   | In-Advance DL |
| 168.      |         |         |         | MarkupSafe-1.0.tar.gz | Flask Dependent Package   | In-Advance DL |
| 169.      |         |         |         | Werkzeug-0.12.2-py2.py3-none-any.whl | Flask Dependent Package   | In-Advance DL |
| 170.      |         | script  | \-        | \-      | \-      | \-      |
| 171.      |         |         |         | pm_crmgen_env.xls | Resource Agent Configuration File | In-Advance DL |
| 172.      |         |         |         | create_table.sql | Table Creation Script   | In-Advance DL from GitHub  |
| 173.      |         |         |         | drop_table.sql | Table Deletion Script   | In-Advance DL from GitHub  |
| 174.    | Ansible |         |         |           |               |         |
| 175.    |       |         |         | ansible-2.4.2.0-2.el7.noarch.rpm | Ansible Installation Package   | In-Advance DL  |
| 176.    |       |         |         | PyYAML-3.10-11.el7.x86_64.rpm | Ansible Dependent Package   | In-Advance DL  |
| 177.    |       |         |         | libyaml-0.1.4-11.el7_0.x86_64.rpm | Ansible Dependent Package   | In-Advance DL  |
| 178.    |       |         |         | openssl-1.0.2k-8.el7.x86_64.rpm | Ansible Dependent Package   | In-Advance DL  |
| 179.    |       |         |         | openssl-libs-1.0.2k-8.el7.x86_64.rpm | Ansible Dependent Package   | In-Advance DL  |
| 180.    |       |         |         | python-babel-0.9.6-8.el7.noarch.rpm | Ansible Dependent Package   | In-Advance DL  |
| 181.    |       |         |         | python-backports-1.0-8.el7.x86_64.rpm | Ansible Dependent Package   | In-Advance DL  |
| 182.    |       |         |         | python-backports-ssl_match_hostname-3.4.0.2-4.el7.noarch.rpm | Ansible Dependent Package   | In-Advance DL  |
| 183.    |       |         |         | python-cffi-1.6.0-5.el7.x86_64.rpm | Ansible Dependent Package   | In-Advance DL  |
| 184.    |       |         |         | python-enum34-1.0.4-1.el7.noarch.rpm | Ansible Dependent Package   | In-Advance DL  |
| 185.    |       |         |         | python-httplib2-0.9.2-1.el7.noarch.rpm | Ansible Dependent Package   | In-Advance DL  |
| 186.    |       |         |         | python-idna-2.4-1.el7.noarch.rpm | Ansible Dependent Package   | In-Advance DL  |
| 187.    |       |         |         | python-ipaddress-1.0.16-2.el7.noarch.rpm | Ansible Dependent Package   | In-Advance DL  |
| 188.    |       |         |         | python-jinja2-2.7.2-2.el7.noarch.rpm | Ansible Dependent Package   | In-Advance DL  |
| 189.    |       |         |         | python-markupsafe-0.11-10.el7.x86_64.rpm | Ansible Dependent Package   | In-Advance DL  |
| 190.    |       |         |         | python-paramiko-2.1.1-2.el7.noarch.rpm | Ansible Dependent Package   | In-Advance DL  |
| 191.    |       |         |         | python-passlib-1.6.5-2.el7.noarch.rpm | Ansible Dependent Package   | In-Advance DL  |
| 192.    |       |         |         | python-ply-3.4-11.el7.noarch.rpm | Ansible Dependent Package   | In-Advance DL  |
| 193.    |       |         |         | python-python-pycparser-2.14-1.el7.noarch.rpm | Ansible Dependent Package   | In-Advance DL  |
| 194.    |       |         |         | python-setuptools-0.9.8-7.el7.noarch.rpm | Ansible Dependent Package   | In-Advance DL  |
| 195.    |       |         |         | python-six-1.9.0-2.el7.noarch.rpm | Ansible Dependent Package   | In-Advance DL  |
| 196.    |       |         |         | python2-cryptography-1.7.2-1.el7.x86_64.rpm | Ansible Dependent Package   | In-Advance DL  |
| 197.    |       |         |         | python2-jmespath-0.9.0-3.el7.noarch.rpm | Ansible Dependent Package   | In-Advance DL  |
| 198.    |       |         |         | python2-pyasn1-0.1.9-7.el7.noarch.rpm | Ansible Dependent Package   | In-Advance DL  |
| 199.    |       |         |         | sshpass-1.06-2.el7.x86_64.rpm | Ansible Dependent Package   | In-Advance DL  |



### 2.1.1. Hardware Operating environment

It is recommended to operate the software on the following Linux
computer environment.

Table 2-1 Recommended Hardware Configuration

| No.  | Computer      | Minimum Configuration                |
|------|---------------|--------------------------------------|
| 1.   | OS            | CentOS7.2 x86\_64                    |
| 2.   | CPU           | IntelR XeonR CPU E5-2420 v2 @2.20GHz <br> 6 Core/12 Thread or greater |
| 3.   | Memory        | 32GB or larger                       |
| 4.   | HD Free Space | 500G or larger                       |
| 5.   | NIC           | More than 1 port                     |

### 2.1.2. Software Operating environment
If you install this application by the internet using a proxy server,
you need to confirm that target servers are able to accsess the internet by https and http protcol.
Also assume that wget has already been installed as a package.


## 3. Installation of Controller Server

The instructions described in this section must be performed by the root
user unless any specific user is specified.

**&lt;Execution Host: ACT/SBY/DB&gt;**

Create a working folder where the files generated in the process of
installation are located.

(It will be deleted when the installation of Controller Server is
completed.)

**\[mkdir \~/setup\] \[Enter\]**

> Locate the em folder which is configured as described in \"1.5
> Configuration of the Included Accessories \" above in the working
> folder.

3.1. Ansible Installation
--------------------------

**&lt;Execution Host: Ansible&gt;**

Before Installation, place the rpm files in Ansible installation destination server.
(Locations: /root/setup/em/installer/ansible)

Execute the following command to install Ansible.

**\[cd /root/setup/em/installer/ansible\] \[Enter\]**

**\[rpm -Uvh \*rpm\] \[Enter\]**


3.2. Controller Server Installation
--------------------------

### 3.2.1. Prepare Installation

### 3.2.1.1. Deploy SSH key

**&lt;Execution Host: Ansible&gt;**

Generate the SSH authentication key with the following command.

**\[ssh -keygen -t rsa\] \[Enter\]**

After that, copy the generated key to the target servers.

**\[scp ~/.ssh/id_rsa.pub root@$REMOTE_IP:~\] \[Enter\]**

($REMOTE_IP: IP of the install target server)

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command on each server.

**\[cd /root/.ssh/\] \[Enter\]**

**\[touch authorized_keys\] \[Enter\]**

**\[chmod 600 authorized_keys\] \[Enter\]**

**\[cat ~/id_rsa.pub >> authorized_keys\] \[Enter\]**

**\[rm ~/id_rsa.pub\] \[Enter\]**


### 3.2.1.2. Deploy Instllation Files

**&lt;Execution Host: Ansible&gt;**

Before Installation, place the playbook file in Ansible installation destination server.
(Locations: /root/setup/playbook/)

If you do not use the Internet connection, place rpm files(Table 1-1 #88-169) for install.
(Locations: same as "rpm_path" (Table 3-1))

#### 3.2.1.3. Edit playbook
Write the IP information of EM and DB to the host file which use by playbook.
Also, put the yml files which has environmental information for each server to the vars folder.


##### 3.2.1.3.1. Edit host file
Write the DB server name in \[DB:children\].

Write the EM server name in \[EM:children\].

And linking IP for above server name.

example)
> [DB:children]
>
> db1
>
> db2
> 	
> [EM:children]
>
> em1
>
> em2
>
> [db1]
>
> 192.168.0.73
>
> [db2]
>
> 192.168.0.74
>
> [em1]
>
> 192.168.0.75
>
> [em2]
>
> 192.168.0.76


##### 3.2.1.3.2. Deploy vars file
Place tha information files defined by the host.
The meaning of each parameter is described below.

Table 3-1 vars Parameter

| name                | Description                          | EM | DB |
|---------------------|--------------------------------------|----|----|
| rpm_path            | In the case of using network connection, the path of rpm file location. <br> In the case of no network connection, it is rpm files path in the Ansible server. (default:/root/setup/em)| ○ | ○ |
| em_path             | In the case of using network connection, the path of deploying the EM installation file location. <br> In the case of no network connection, it is EM installation files path (Including DB scripts). (defalult:/opt/em)| ○ | ○ |
| download_flag       | Parameter for determining whether to acquire a file from the Internet or place it on an Ansible server. <br> If True, use the Internet connection. | ○ | ○ |
| log_path            | Relative path of EM log file output destination.(defalut:logs/em/log) | ○ | × |
| em_conf_path        | The path of EM config file location. <br> (defalut:/root/setup/em) | ○ | × |
|installing_em_path|The path of EM installing files(script, lib, conf, bin) (default:/root/setup/em)| ○ | × |
| db_address          | DB server IP address.                | ○ | ○ |
| db_name             | DB name.                             | ○ | ○ |
| em_physical_address | EM physical IP address.              | ○ | × |
| ec_rest_address     | EC REST IP address.                  | ○ | × |
| ec_rest_port        | EC REST port.                        | ○ | × |
| em_netconf_address  | EM netconf IP address.               | ○ | × |
| em_netconf_port     | EM netconf port.                     | ○ | × |
| em_rest_address     | EM REST IP address.                  | ○ | × |
| em_rest_port        | EM REST port.                        | ○ | × |
| controller_cidr     | The network name of the server that the DB allows for connections. (CIDR) | ○ | ○ |
| ntp_server_address  | NTP server address.                  | ○ | × |
| ha_flag             | Flag indicating whether to implement redundancy. In the case of truth it is implemented. | ○ | ○ |
| act_address         | IP address for act server. (When ha_flag is False, it is set to none) | ○ | ○ |
| act_node_name       | Name for act server. (When ha_flag is False, it is set to none) | ○ | ○ |
| sby_address         | IP address for stand-by server. (When ha_flag is False, it is set to none) | ○ | ○ |
| sby_node_name       | Name for stand-by server. (When ha_flag is False, it is set to none) | ○ | ○ |
| cluster_name        | Cluster name (When ha_flag is False, it is set to none) | ○ | ○ |
| install_flag        | When setting the DB, it decides whether to install PostgreSQL. | × | ○ |


### 3.2.2. Execute Installation
**&lt;Execution Host: Ansible&gt;**

Execute the following command to install this application.

**\[ansible-playbook em.yml -i hosts\] \[Enter\]**


### 3.2.3. Edit Configuration

#### 3.2.3.1. Edit of EM configure file
The settings required for the operation (IP,port,file path etc...) are automatically replaced with the parameters at the time of installation.

If you want to change other setting, you need to fix it by hand.

Change the EM Module configuration file by use of the following command.

**\[vi \$EM\_HOME/conf/\[File Name\]\] \[Enter\]**

For the "File Name" above, the followings will be inserted.

・conf\_sys\_common.conf

・conf\_scenario.conf

・conf\_if\_process.conf

・conf\_driver.conf

・conf\_separate\_driver\_cisco.conf

・conf\_if\_process\_rest.conf

・conf\_scenario\_rest.conf

Please refer to "element\_manager\_configuration\_specifications.md" for the
details of the change.


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

3.3. Confirm Setting
------------------

#### 3.3.1. Confirmation of Python Library Installation

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command to view the list of installed libraries
and the version of each library.

**\[pip list\] \[Enter\]**

> If the installation of each library has been completed successfully,
> the following information will be displayed in the list.

alembic (0.8.8)

Babel (2.3.4)

cffi (1.8.3)

cryptography (1.5.2)

debtcollector (1.8.0)

decorator (3.4.0)

enum34 (1.1.6)

funcsigs (1.0.2)

idna (2.1)

ipaddress (1.0.17)

iso8601 (0.1.11)

lxml (3.6.4)

Mako (1.0.4)

MarkupSafe (0.23)

monotonic (1.2)

ncclient (0.5.2)

netaddr (0.7.18)

netconf (0.4.1)

netifaces (0.10.5)

oslo.config (3.17.0)

oslo.context (2.9.0)

oslo.db (4.13.3)

oslo.i18n (3.9.0)

oslo.utils (3.16.0)

paramiko (2.0.2)

pbr (1.10.0)

positional (1.1.1)

psycopg2 (2.6.2)

pyasn1 (0.1.9)

pycparser (2.14)

pyparsing (2.1.9)

python-editor (1.0.1)

pytz (2016.7)

rfc3986 (0.4.1)

setuptools (28.6.0)

six (1.9.0)

SQLAlchemy (1.0.15)

sqlalchemy-migrate (0.10.0)

sqlparse (0.2.1)

sshutil (0.9.7)

stevedore (1.17.1)

Tempita (0.5.2)

wrapt (1.10.8)

xmltodict (0.10.2)


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

**&lt;Execution Host: ACT/SBY&gt;**

>public (default, active)
>
>interfaces:
>
>sources:
>
>services: dhcpv6-client `high-availability` ssh
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


### 3.3.4. Confirmation of ntp operation

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command to reboot the NTP.

**\[systemctl restart ntpd.service\] \[Enter\]**

**\[systemctl enable ntpd.service\] \[Enter\]**

Execute the following command to confirm the synchronization with the
NTP server.

**\[ntpq -p\] \[Enter\]**

&lt;The output example of successful synchronization&gt;

| remote refid st t when poll reach delay offset jitter               |
| ------------------------------------------------------------------- |
| \*xxx.xxx.xxx.xxx LOCAL(0) 11 u 55 64 377 0.130 -0.017 0.017        |


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

> Execute the following command to confirm the status of inter-node
> communication by use of \"corosync-cfgtool -s\" command.
>
> This task must be performed both at the active and the stand-by nodes.
>
> **\[corosync-cfgtool -s\] \[Enter\]**
>
> If the cluster is started successfully, the following message will be
> displayed in the screen.
>
> When the \"status\" is \"active\" and \"no faults\", the communication
> is working properly.
>
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
