# Element Manager Installation Manual

**Version 1.0**
**December 26, 2017**
**Copyright(c) 2017 Nippon Telegraph and Telephone Corporation**

1. Introduction
============

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
prepare them prior to implementing the installation in this document.

Table 1-1 Included Accessories

| \#      | Folder Structure  | | | File Name    | Descriprion | Remarks |
|---------|---------|---------|---------|---------|---------|---------|
| 1.      | em      | \-      | \-      | \-      | \-      | \-      |
| 2.      |         | bin     |         | em      | Resource Agent | \-      |
| 3.      |         |         |         | em_ctl.sh | EM Start-up Script      | \-      |
| 4.      |         |         |         | EmMonitor.py | Alive Monitor Client   | \-      |
| 5.      |         |         |         | controller_status.sh | Controller Status Information<br> Acquisition Script |         |
| 6.      |         | lib     |         | MsfEmMain.py | Main Module    | \-      |
| 7.      |         |         |         | GlobalModule.py | Global Module  | \-      |
| 8.      |         |         |         | EmCommonLog.py | EM Common Log Module      | \-      |
| 9.      |         |         |         | EmSetPATH.py | PYTHONPATH Configuration Module for EM | \-      |
| 10.      |         |         |         | EmLoggingFormatter.py | Log Formater Module for EM     | \-      |
| 11.      |         |         |         | \__init__.py | Initialization Module | \-      |
| 12.      |         |         | CommonDriver | EmCommonDriver.py | Driver Common Part Module  | \-      |
| 13.      |         |         |         | \__init__.py | Initialization Module | \-      |
| 14.      |         |         | Config  | EmConfigManagement.py | Configuration Management Module | \-      |
| 15.      |         |         |         | \__init__.py | Initialization Module | \-      |
| 16.      |         |         | DB      | EmDBControl.py | DB Control Module      | \-      |
| 17.      |         |         |         | \__init__.py | Initialization Module | \-      |
| 18.      |         |         | DriverUtility | EmDriverCommonUtilityDB.py | Driver Common Utility (DB) Module  | \-      |
| 19.      |         |         |         | EmDriverCommonUtilityLog.py | Driver Common Utility (Log) Module  | \-      |
| 20.      |         |         |         | \__init__.py | Initialization Module | \-      |
| 21.      |         |         | Netconf Serve | EmNetconfServer.py | EM Netconf Server Module      | \-      |
| 22.      |         |         |         | \__init__.py | Initialization Module | \-      |
| 23.      |         |         | OrderflowControl | EmOrderflowControl.py | Order Flow Control Module   | \-      |
| 24.      |         |         |         | \__init__.py | Initialization Module | \-      |
| 25.      |         |         | Protocol | EmNetconfProtocol.py | For-device Protocol Process Module | \-      |
| 26.      |         |         |         | EmCLIProtocol.pyr | Protocol Processing (CLI) Module for Devices | \-      |
| 27.      |         |         |         | \__init__.py | Initialization Module | \-      |
| 28.      |         |         | RestScenario | EmControllerLogGet.py | Controller Log Acquisition Scenario | \-      |
| 29.      |         |         |         | EmControllerStatusGet.py | Controller Status Acquisition Scenario | \-      |
| 30.      |         |         |         | EmSeparateRestScenario.py | REST Individual Scenario Module    | \-      |
| 31.      |         |         |         | \__init__.py | Initialization Module | \-      |
| 32.      |         |         | RestServer | EmRestServer.py | REST Server Module    | \-      |
| 33.      |         |         |         | \__init__.py | Initialization Module | \-      |
| 34.      |         |         | Scenario | EmBLeafDelete.py | B-Leaf Deletion Scenario  | \-      |
| 35.      |         |         |         | EmBLeafMerge.py | B-Leaf Generation Scenario  | \-      |
| 36.      |         |         |         | EmBLeafScenario.py | B-Leaf Scenario Modulef  | \-      |
| 37.      |         |         |         | EmBLeafUpdate.py | B-Leaf Update Scenario  | \-      |
| 38.      |         |         |         | EmBreakoutIFDelete.py | BreakoutIF Deletion Scenario | \-      |
| 39.      |         |         |         | EmBreakoutIFMerge.py | BreakoutIF Registration Scenario | \-      |
| 40.      |         |         |         | EmCeLagDelete.py | LAG Deletion Scenario for CE     | \-      |
| 41.      |         |         |         | EmCeLagMerge.py | LAG Addition Scenario for CE     | \-      |
| 42.      |         |         |         | EmClusterLinkDelete.py | Inter-Claster Link I/F Deletion Scenario | \-      |
| 43.      |         |         |         | EmClusterLinkMerge.py | Inter-Claster Link I/F Addition Scenario | \-      |
| 44.      |         |         |         | EmDeleteScenario.py | Resource Deletion Scenario Module | \-      |
| 45.      |         |         |         | EmInternalLinkDelete.py | Internal Link Delete Scenario | \-    |
| 46.      |         |         |         | EmInternalLinkMerge.py | Internal Link Merge Scenario | \-    |
| 47.      |         |         |         | EmL2SliceEvpnControl.py | L2 Slice EVPN Control Scenario | \-     |
| 48.      |         |         |         | EmL2SliceDelete.py | L2 Slice Deletion Scenario      | \-      |
| 49.      |         |         |         | EmL2SliceGet.py | L2 Slice Information Adjustment Scenario      | \-      |
| 50.      |         |         |         | EmL2SliceMerge.py | L2 Slice Addition Scenario      | \-      |
| 51.      |         |         |         | EmL3SliceDelete.py | L3 Slice Deletion Scenario      | \-      |
| 52.      |         |         |         | EmL3SliceGet.py | L3 Slice Information Adjustment Scenario      | \-      |
| 53.      |         |         |         | EmL3SliceMerge.py | L3 Slice Addition Scenario      | \-      |
| 54.      |         |         |         | EmLeafDelete.py | Leaf Deletion Scenario    | \-      |
| 55.      |         |         |         | EmLeafMerge.py | Leaf Addition Scenario    | \-      |
| 56.      |         |         |         | EmMergeScenario.py | Resource Addition Scenario Module | \-      |
| 57.      |         |         |         | EmSpineDelete.py | Spine Deletion Scenario   | \-      |
| 58.      |         |         |         | EmSpineMerge.py | Spine Addition Scenario   | \-      |
| 59.      |         |         |         | EmSeparateScenario.py | Individual Scenario Module | \-      |
| 60.      |         |         |         | \__init__.py | Initialization Module | \-      |
| 61.      |         |         | SeparateDriver | CiscoDriver.py | Cisco (5001, 5011) Driver Module       | \-      |
| 62.      |         |         |         | CiscoDriver5501.py | Cisco 5501 Driver Module       | \-      |
| 63.      |         |         |         | JuniperDriver5100.py | Juniper 5100 Driver Module       | \-      |
| 64.      |         |         |         | JuniperDriver5200.py | Juniper 5200 Driver Module       | \-      |
| 65.      |         |         |         | JuniperDriverMX240.py | J Company Core Router Driver Module       | \-      |
| 66.      |         |         |         | OcNOSDriver.py | OcNOS Driver Module   | \-      |
| 67.      |         |         |         | EmSeparateDriver.py | Driver Individual Module  | \-      |
| 68.      |         |         |         | \__init__.py | Initialization Module | \-      |
| 69.      |         |         | SystemUtility | EmSysCommonUtilityDB.py | System Common (DB) Utility Module  | \-      |
| 70.      |         |         |         | \__init__.py | Initialization Module | \-      |
| 71.      |         | conf    |         | conf_driver.conf | Driver Individual Part Operational Configuration File  | \-      |
| 72.      |         |         |         | conf_if_process.conf | I/F Process Part Operational Configuration File     | \-      |
| 73.      |         |         |         | conf_scenario.conf | Scenario Individual Part Operational Configuration File | \-      |
| 74.      |         |         |         | conf_sys_common.conf | EM Common Configuration File      | \-      |
| 75.      |         |         |         | conf_separate_driver_cisco.conf | Cisco Driver Operation Configuration File       | \-      |
| 76.      |         |         |         | conf_if_process_rest.conf | REST Server Operation Configuration FileT    | \-      |
| 77.      |         |         |         | conf_scenario_rest.conf | REST Scenario Individual Part Operation Configuration File    | \-      |
| 78.      |         | installer | \-      | \-      | \-      | \-      |
| 79.      |         |         |         | whl_package.tar | In-use Python Library Package  | In-Advance DL |
| 80.      |         |         |         | pip-8.1.2.tar.gz | PIP Command for Python Library Install     | In-Advance DL |
| 81.      |         |         |         | setuptools-28.6.0.tar.gz | pip Dependent Package     | In-Advance DL |
| 82.      |         |         | dhcp.v4.2.5 | dhcp-4.2.5-42.el7.centos.x86_64.rpm | DHCP Installation Package    | In-Advance DL |
| 83.      |         |         | ntp.v4.2 | autogen-libopts-5.18-5.el7.x86_64.rpm | NTP Installation Package     | In-Advance DL |
| 84.      |         |         |         | ntpdate-4.2.6p5-22.el7.centos.x86_64.rpme | NTP Installation Package     | In-Advance DL |
| 85.      |         |         |         | ntp-4.2.6p5-22.el7.centos.x86_64.rpm | NTP Installation Package     | In-Advance DL |
| 86.      |         |         | postgresql.v9.3.13 | postgresql93-9.3.13-1PGDG.rhel7.x86_64.rpm | PostgreSQL Installation Package | In-Advance DL |
| 87.      |         |         |         | postgresql93-contrib-9.3.13-1PGDG.rhel7.x86_64.rpm | PostgreSQL Installation Package | In-Advance DL |
| 88.      |         |         |         | postgresql93-devel-9.3.13-1PGDG.rhel7.x86_64.rpm | PostgreSQL Installation Package | In-Advance DL |
| 89.      |         |         |         | postgresql93-libs-9.3.13-1PGDG.rhel7.x86_64.rpm | PostgreSQL Installation Package | In-Advance DL |
| 90.      |         |         |         | postgresql93-server-9.3.13-1PGDG.rhel7.x86_64.rpm | PostgreSQL Installation Package | In-Advance DL |
| 91.      |         |         |         | uuid-1.6.2-26.el7.x86_64.rpm | PostgreSQL Dependent Package | In-Advance DL |
| 92.      |         |         |         | libxslt-1.1.28-5.el7.x86_64.rpm | PostgreSQL Dependent Package | In-Advance DL |
| 93.      |         |         | pacemaker.v1.1.14-1.1 | pacemaker-1.1.14-1.el7.x86_64.rpm | Pacemaker Installation Package | In-Advance DL |
| 94.      |         |         |         | corosync-2.3.5-1.el7.x86_64.rpm | Corosync Installation Package | In-Advance DL |
| 95.      |         |         |         | crmsh-2.1.5-1.el7.x86_64.rpm | crm Command Installation Package     | In-Advance DL |
| 96.      |         |         |         | cluster-glue-1.0.12-2.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 97.      |         |         |         | cluster-glue-libs-1.0.12-2.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 98.      |         |         |         | corosynclib-2.3.5-1.el7.x86_64.rpm | Corosync Dependent Package | In-Advance DL |
| 99.      |         |         |         | ipmitool-1.8.13-9.el7_2.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 100.      |         |         |         | libqb-1.0-1.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 101.      |         |         |         | libtool-ltdl-2.4.2-21.el7_2.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 102.      |         |         |         | libxslt-1.1.28-5.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 103.      |         |         |         | libyaml-0.1.4-11.el7_0.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 104.      |         |         |         | lm_sensors-libs-3.3.4-11.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 105.      |         |         |         | nano-2.3.1-10.el7.x86_64.rpm | crm Dependent Package     | In-Advance DL |
| 106.      |         |         |         | net-snmp-agent-libs-5.7.2-24.el7_2.1.x86_64.rpm | Corosync Dependent Package | In-Advance DL |
| 107.      |         |         |         | net-snmp-libs-5.7.2-24.el7_2.1.x86_64.rpm | Corosync Dependent Package | In-Advance DL |
| 108.      |         |         |         | openhpi-libs-3.4.0-2.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 109.      |         |         |         | OpenIPMI-libs-2.0.19-11.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 110.      |         |         |         | OpenIPMI-modalias-2.0.19-11.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 111.      |         |         |         | pacemaker-cli-1.1.14-1.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 112.      |         |         |         | pacemaker-cluster-libs-1.1.14-1.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 113.      |         |         |         | pacemaker-libs-1.1.14-1.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 114.      |         |         |         | pacemaker-all-1.1.14-1.1.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 115.      |         |         |         | perl-5.16.3-286.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 116.      |         |         |         | perl-Carp-1.26-244.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 117.      |         |         |         | perl-constant-1.27-2.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 118.      |         |         |         | perl-Encode-2.51-7.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 119.      |         |         |         | perl-Exporter-5.68-3.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 120.      |         |         |         | perl-File-Path-2.09-2.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 121.      |         |         |         | perl-File-Temp-0.23.01-3.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 122.      |         |         |         | perl-Filter-1.49-3.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 123.      |         |         |         | perl-Getopt-Long-2.40-2.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 124.      |         |         |         | perl-HTTP-Tiny-0.033-3.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 125.      |         |         |         | perl-libs-5.16.3-286.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 126.      |         |         |         | perl-macros-5.16.3-286.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 127.      |         |         |         | perl-parent-0.225-244.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 128.      |         |         |         | perl-PathTools-3.40-5.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 129.      |         |         |         | perl-Pod-Escapes-1.04-286.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 130.      |         |         |         | perl-podlators-2.5.1-3.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 131.      |         |         |         | perl-Pod-Perldoc-3.20-4.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 132.      |         |         |         | perl-Pod-Simple-3.28-4.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 133.      |         |         |         | perl-Pod-Usage-1.63-3.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 134.      |         |         |         | perl-Scalar-List-Utils-1.27-248.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 135.      |         |         |         | perl-Socket-2.010-3.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 136.      |         |         |         | perl-Storable-2.45-3.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 137.      |         |         |         | perl-Text-ParseWords-3.29-4.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 138.      |         |         |         | perl-threads-1.87-4.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 139.      |         |         |         | perl-threads-shared-1.43-6.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 140.      |         |         |         | perl-TimeDate-2.30-2.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 141.      |         |         |         | perl-Time-HiRes-1.9725-3.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 142.      |         |         |         | perl-Time-Local-1.2300-2.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 143.      |         |         |         | pm_crmgen-2.1-1.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 144.      |         |         |         | pm_diskd-2.2-1.el7.x86_64.rpm | Diskd RA Package   | In-Advance DL |
| 145.      |         |         |         | pm_extras-2.2-1.el7.x86_64.rpm | VIPCheck RA Package | In-Advance DL |
| 146.      |         |         |         | pm_logconv-cs-2.2-1.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 147.      |         |         |         | psmisc-22.20-9.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 148.      |         |         |         | pssh-2.3.1-5.el7.noarch.rpm | crm Dependent Package     | In-Advance DL |
| 149.      |         |         |         | python-dateutil-1.5-7.el7.noarch.rpm | Pacemaker Dependent Package | In-Advance DL |
| 150.      |         |         |         | python-lxml-3.2.1-4.el7.x86_64.rpm | Pacemaker Dependent Package | In-Advance DL |
| 151.      |         |         |         | resource-agents-3.9.7-1.2.6f56.el7.x86_64.rpm | Standard RA Package Incl. Virtual IPRA | In-Advance DL |
| 152.      |         |         |         | pacemaker_install.sh | Package Installer | In-Advance DL |
| 153.      |         |         | sysstat-11.6.0-1 | sysstat-11.6.0-1.x86_64.rpm | Sysstat Installation Package | In-Advance DL |
| 154.      |         |         | flask-0.12.2 | Flask-0.12.2-py2.py3-none-any.whl | Flask Installation Package   | In-Advance DL |
| 155.      |         |         |         | click-6.7-py2.py3-none-any.whl | Flask Dependent Package   | In-Advance DL |
| 156.      |         |         |         | itsdangerous-0.24.tar.gz | Flask Dependent Package   | In-Advance DL |
| 157.      |         |         |         | Jinja2-2.9.6-py2.py3-none-any.whl | Flask Dependent Package   | In-Advance DL |
| 158.      |         |         |         | MarkupSafe-1.0.tar.gz | Flask Dependent Package   | In-Advance DL |
| 159.      |         |         |         | Werkzeug-0.12.2-py2.py3-none-any.whl | Flask Dependent Package   | In-Advance DL |
| 160.      |         | script  | \-        | \-      | \-      | \-      |
| 161.      |         |         |         | ra_config.xlsx | Resource Agent Configuration File | \-      |
| 162.      |         |         |         | create_table.sql | Table Creation Script   | \-      |
| 163.      |         |         |         | drop_table.sql | Table Deletion Script   | \-      |


2. Operational Environment
=======================

2.1. EM Module Start-up Server of Controller
-------------------------------------------

It is recommended to operate the software on the following Linux
computer environment.

Table 2-1 Recommended Hardware Configuration

| No.  | Computer      | Minimum Configuration                  |
|------|---------------|----------------------------------------|
| 1.   | OS            | CentOS7.2 x86\_64                      |
| 2.   | CPU           | IntelR XeonR CPU E5-2420 v2 @ 2.20 GHz 12 Core |
| 3.   | Memory        | 32G or larger                          |
| 4.   | HD Free Space | 500G or larger                         |
| 5.   | NIC           | More than 1 port                       |

3. Installation of Controller Server
=====================================

3.1. Environmental Installation
--------------------------

**&lt;Execution Host: ACT/SBY&gt;**

Create a working folder where files are located during the installation.

(This folder should be removed when the environmental Installation
completes.)

**\[mkdir \~/setup\] \[Enter\]**

Then locate the em folder in the included accessory in the working
folder.

### 3.1.1. Firewall Configuration

#### 3.1.1.1. Firewall Confirmation

**&lt;Execution Host: DB/ACT/SBY&gt;**

> Check if the firewall has been already configured.
>
> **\[firewall-cmd \--state\] \[Enter\]**
>
> If the firewall has already been configured, the following message
> will be displayed in the screen.
>
> running
>
> In this case, keep following the instructions from 3.1.1.2 to 3.1.1.7.
>
> If the firewall is not installed or is not started, the following
> message will be displayed in the screen.
>
> (In case the firewall is not started) not running
>
> (In case the firewall is not installed) bash: firewall-cmd: command
> not found
>
> In these cases, the instructions from 3.1.1.2 to 3.1.1.7 can be
> ignored.

#### 3.1.1.2. Permit the Connection of Netconf Request (EC, Start-up Notification)

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command to permit the connection from the port
used in Netconf Request.

In case installing two or more EM\'s in a same server, set a different
port for every entity in the configuration file and execute the
following command for every port. (Replace the highlighted section with
the appropriate port number.)

(The specified port numbers in this document are default values. You can
change the numbers in accordance with your configuration.)

**\[firewall-cmd \--permanent \--add-port=830/tcp\] \[Enter\]**

#### 3.1.1.3. Permit the Connection of REST Request (EC)

**&lt;Execution Host: DB&gt;**

Execute the following command to permit the connection from the port
used in REST Request.

In case installing two or more EM\'s in a same server, set a different
port for every entity in the configuration file and execute the
following command for every port. (Replace the highlighted section with
the appropriate port number.)

**\[firewall-cmd \--permanent \--add-port=8080/tcp\] \[Enter\]**

#### 3.1.1.4. Permit the Connection of PostgreSQL

**&lt;Execution Host: DB&gt;**

Execute the following command to permit the connection from the port
used in PostgreSQL.

**\[firewall-cmd \--permanent \--add-port=5432/tcp\] \[Enter\]**

#### 3.1.1.5. Permit the Connection of PNTP

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command to permit the connection from the port
used in NTP.

**\[firewall-cmd \--permanent \--add-service=ntp\] \[Enter\]**

**\
**

#### 3.1.1.6. Permit the Connection of Pacemaker/Corosync

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command to permit the connection from the port
used in Pacemaker/Corosync.

> **\[firewall-cmd \--permanent \--add-service=high-availability\]
> \[Enter\]**

#### 3.1.1.7. Final Configuration of the Firewall

**&lt;Execution Host: ACT/SBY&gt;**

> Once having completed the 3.1.1 Firewall Configuration above, execute
> the following command to reflect the configuration.

**\[firewall-cmd \--reload\] \[Enter\]**

**\[systemctl restart firewalld\] \[Enter\]**

Confirm the current configuration by executing the following command
(especially for the highlighted section).

**\[firewall-cmd \--list-all\] \[Enter\]**

public (default, active)

interfaces: eth0 eth1

sources:

services: dhcpv6-client ntp ssh high-availability

ports: 830/tcp 8080/tcp

masquerade: no

forward-ports:

icmp-blocks:

rich rules:

**&lt;Execution Host: DB&gt;**

Also at the DB side, execute the following command to reflect the
configuration.

**\[firewall-cmd \--reload\] \[Enter\]**

**\[systemctl restart firewalld\] \[Enter\]**

Confirm the current configuration by executing the following command
(especially for the highlighted section).

**\[firewall-cmd \--list-all\] \[Enter\]**

public (default, active)

interfaces:

sources:

services: ssh

ports: 5432/tcp

masquerade: no

forward-ports:

icmp-blocks:

rich rules:

### 3.1.2. Installation and Configuration of Pacemaker

#### 3.1.2.1. Installation of pacemaker

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command to launch the installer and install.

**\[cd \~/setup/em/installer/pacemaker.v1.1.14-1.1\] \[Enter\]**

**\[sh pacemaker\_install.sh\] \[Enter\]**

> Note: Although you will be warned that there is no key with the
> message \"Warning: pssh-2.3.1-5.el7.noarch.rpm: header V3 RSA/SHA256
> Signature, Key ID 352c64e5: NOKEY\" displayed in the screen during the
> installation, the installation process keeps going on and you can
> ignore it.

#### 3.1.2.2. Confirmation of Installation of Pacemaker

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

Execute the following command to confirm the resource agent that is
going to be used is actually installed.

**\[ls /lib/ocf/resource.d/pacemaker/\] \[Enter\]**

If the installation has been completed successfully, the following
message will be displayed.

> diskd

Execute the following command to confirm the resource agent that is
going to be used is actually installed.

**\[ls /lib/ocf/resource.d/heartbeat/\] \[Enter\]**

If the installation has been completed successfully, the following
message will be displayed.

> VIPcheck、IPAddr2

#### 3.1.2.3. Configuration of the Host

**&lt;Execution Host: ACT/SBY&gt;**

> Register the node's hosts used in the active system and the stand-by
> system.
>
> Perform this task both at the active node and the stand-by node.
>
> Execute the following command to open the hosts file.

**\[vi /etc/hosts\] \[Enter\]**

> In the edit mode, add the following lines to the end of the file.
>
> **(IP Address for the Stand-by Interconnection) (Stand-by Host Name)**
>
> **(IP Address for the Active Interconnecction) (Active Host Name)**
>
> Then restart in order to enable the configuration of the Hosts.
>
> **\[reboot\] \[Enter\]**

#### 3.1.2.4. Node Authentication

> Execute the following command to create corosync.com for running
> pacemaker.
>
> **\[vi /etc/corosync/corosync.conf\] \[Enter\]**
>
> The content of the file should be as follows.

totem {

version: 2

secauth: off

cluster\_name: (Cluster Name to be configured)

transport: udpu

}

nodelist {

node {

ring0\_addr: (Active Node Name)

nodeid: 1

}

node {

ring0\_addr: (Stand-by Node Name)

nodeid: 2

}

}

quorum {

provider: corosync\_votequorum

two\_node: 1

}

logging {

to\_logfile: yes

logfile: /var/log/cluster/corosync.log

to\_syslog: yes

}

#### 3.1.2.5. Launch Pacemaker

**&lt;Execution Host: ACT&gt;**

> Execute the following command to run Pacemaker.
>
> **\[systemctl start pacemaker\] \[Enter\]**

#### 3.1.2.6. Confirmation of the Inter-node Communication Status

**&lt;Execution Host: ACT/SBY&gt;**

> Execute the following command to confirm the status of inter-node
> communication via corosync.
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

#### 3.1.2.7. Confirmation of Cluster Status

**&lt;Execution Host: ACT or SBY&gt;**

> Execute the following command to confirm the status of the cluster.
>
> This task can be performed at either the Active or the Stand-by
> system.
>
> **\[crm\_mon --fA -1\] \[Enter\]**
>
> After entering the command, the cluster status will be displayed in
> the screen. A warning message about STONITH, which looks like below
> will be also displayed on top of the screen.
>
> Cluster name: (Cluster Name having been set)
>
> WARNING: no stonith devices and stonith-enabled is not false
>
> Last updated: Thu Oct 13 02:06:57 2016 Last change: Thu Oct 13
> 02:06:49 2016
>
> Since STONITH is not available in the environment this time, set
> "false" for the enablement of STONITH.
>
> **\[crm configure property stonith-enabled ="false"\] \[Enter\]**
>
> Confirm the cluster status for one last time.
>
> **\[crm\_mon --fA -1\] \[Enter\]**
>
> After entering the command, the cluster status will be displayed in
> the screen. If it is configured properly, the screen message will be
> looked like below.

Last updated: WDW MMM DD HH:MM:DD YYYY Last change: WDW MMM DD HH:MM:DD
YYYY by root via cibadmin on (Active Node Name)

Stack: corosync

Current DC: (Active Node Name) (version 1.1.14-1.el7-70404b0) -
partition with quorum

2 nodes and 0 resources configured

Online: \[(Active Node Name) (Stand-by Node Name)\]

Node Attributes:

\* Node (Active Node Name):

\* Node (Stand-by Node Name):

Migration Summary:

\* Node (Active Node Name):

\* Node (Stand-by Node Name):

#### 3.1.2.8. Enable pacemaker/corosync Services

**&lt;Execution Host: ACT/SBY&gt;**

> Execute the following command to enable corosync and pacemaker
> services for enabling the auto start of both services after the
> reboot.
>
> This task must be performed both at the active and the stand-by nodes.
>
> **\[systemctl enable pacemaker\] \[Enter\]**
>
> **\[systemctl enable corosync\] \[Enter\]**

### 3.1.3. Installation and Configuration of Python Library

#### 3.1.3.1. Installation of setup-tools

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command to install setup-tools.

**\[cd \~/setup/em/installer/\] \[Enter\]**

**\[tar zxvf setuptools-28.6.0.tar.gz\] \[Enter\]**

**\[cd setuptools-28.6.0\] \[Enter\]**

**\[python setup.py install\] \[Enter\]**

#### 3.1.3.2. Installation of PIP

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command to install PIP.

**\[cd \~/setup/em/installer/\] \[Enter\]**

> **\[tar zxvf pip-8.1.2.tar.gz\] \[Enter\]**
>
> **\[cd pip-8.1.2\] \[Enter\]**
>
> **\[python setup.py install\] \[Enter\]**

#### 3.1.3.3. Confirmation of PIP Installation

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command to confirm the version.

**\[pip \--version\] \[Enter\]**

If the installation has been completed successfully, the following
message will be displayed.

pip 8.1.2 from /usr/lib/python2.7/site-packages/pip-8.1.2-py2.7.egg
(python 2.7)

#### 3.1.3.4. Installation of Python Library

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command to extend the package.

**\[cd \~/setup/em/installer/\] \[Enter\]**

**\[tar xvf whl\_package.tar\] \[Enter\]**

Execute the following command to navigate to the folder of the extended
package.

**\[cd whl\_package\] \[Enter\]**

Execute the following command to install the library.

**\[pip install \--use-wheel \--no-index \--find-links=.
netconf-0.4.1-py2-none-any.whl\] \[Enter\]**

**\[pip install \--use-wheel \--no-index \--find-links=.
ncclient-0.5.2-py2-none-any.whl\] \[Enter\]**

**\[pip install \--use-wheel \--no-index \--find-links=.
oslo.db-4.13.3-py2.py3-none-any.whl\] \[Enter\]**

**\[pip install \--use-wheel \--no-index \--find-links=**.
**xmltodict-0.10.2-py2-none-any.whl\] \[Enter\]**

**\[pip install \--use-wheel \--no-index \--find-links=**.
**psycopg2-2.6.2-cp27-cp27mu-linux\_x86\_64.whl\] \[Enter\]**

**\
**

#### 3.1.3.5. Confirmation of Python Library Installation

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

### 3.1.4. Installation and Configuration of NTP

#### 3.1.4.1. Installation

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command to install ntp.

**\[cd \~/setup/em/installer/ntp.v4.2/\] \[Enter\]**

**\[rpm -ivh autogen-libopts-5.18-5.el7.x86\_64.rpm\] \[Enter\]**

**\[rpm -ivh ntpdate-4.2.6p5-22.el7.centos.x86\_64.rpm\] \[Enter\]**

**\[rpm -ivh ntp-4.2.6p5-22.el7.centos.x86\_64.rpm\] \[Enter\]**

#### 3.1.4.2. Making of drift File

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command to make a blank drift file.

**\[touch /var/lib/ntp/drift\] \[Enter\]**

#### 3.1.4.3. Change of the NTP Configuration File

**&lt;Execution Host: ACT/SBY&gt;**

Add the following lines (**the highlighted section**) to the NTP
configuration file (/etc/ntp.conf) as the root user.

**\[vi /etc/ntp.conf\] \[Enter\]**

...

restrict default nomodify notrap nopeer noquery

**restrict default ignore**

...

\#restrict 192.168.1.0 mask 255.255.255.0 nomodify notrap

**restrict xxx.xxx.xxx.xxx noquery nomodify**

**server xxx.xxx.xxx.xxx iburst**

...

#### 3.1.4.4. Synchronization with NTP Server

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command to confirm that NTP is not running.

**\[systemctl status ntpd.service\] \[Enter\]**

&lt;Output in case NTP is not running&gt;

...

Active: inactive (dead)

...

&lt;Output in case NTP is running&gt;

...

Active: active (running)

...

In case NTP is running, execute the following command to stop the NTP.

**\[systemctl stop ntpd.service\] \[Enter\]**

Synchronize the time with NTP server (IP address: xxx.xxx.xxx.xxx).

**\[ntpdate xxx.xxx.xxx.xxx\] \[Enter\]**

#### 3.1.4.5. Restart of the NTP

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command to restart NTP.

**\[systemctl restart ntpd.service\] \[Enter\]**

**\[systemctl enable ntpd.service\] \[Enter\]**

Execute the following command to confirm the synchronization with NTP
server.

**\[ntpq -p\] \[Enter\]**

&lt;output example when the synchronization established successfully &gt;

| remote refid st t when poll reach delay offset jitter               |
|---------------------------------------------------------------------|
| \*xxx.xxx.xxx.xxx LOCAL(0) 11 u 55 64 377 0.130 -0.017 0.017        |

### 3.1.5. Installation and Configuration of PostgreSQL

#### 3.1.5.1. Installation

**&lt;Execution Host: DB/ACT/SBY&gt;**

Execute the following command to install postgresql.

**\[cd \~/setup/em/installer/postgresql.v9.3.13\] \[Enter\]**

**\[rpm -ivh libxslt-1.1.28-5.el7.x86\_64.rpm\] \[Enter\]**

**\[rpm -ivh uuid-1.6.2-26.el7.x86\_64.rpm\] \[Enter\]**

**\[rpm -ivh postgresql93-libs-9.3.13-1PGDG.rhel7.x86\_64.rpm\]
\[Enter\]**

**\[rpm -ivh postgresql93-9.3.13-1PGDG.rhel7.x86\_64.rpm\] \[Enter\]**

**\[rpm -ivh postgresql93-server-9.3.13-1PGDG.rhel7.x86\_64.rpm\]
\[Enter\]**

**\[rpm -ivh postgresql93-devel-9.3.13-1PGDG.rhel7.x86\_64.rpm\]
\[Enter\]**

**\[rpm -ivh postgresql93-contrib-9.3.13-1PGDG.rhel7.x86\_64.rpm\]
\[Enter\]**

#### 3.1.5.2. Change the PostgreSQL Configuration

**&lt;Execution Host: DB&gt;**

Change the configuration as follows.

**\[vi /var/lib/pgsql/.bash\_profile\] \[Enter\] (Modify or add the
highlighted section)**

PGDATA=/usr/local/pgsql/9.3/data

export PGDATA

export PATH=\$PATH:/usr/pgsql-9.3/bin

**\[source /var/lib/pgsql/.bash\_profile\] \[Enter\]**

#### 3.1.5.3. Making of Data Base and Granting Permissions

**&lt;Execution Host: DB&gt;**

Execute the following command to make the installation folder of the
Data Base.

**\[cd /usr/local/\] \[Enter\]**

**\[mkdir -pm 777 /usr/local/pgsql/9.3\] \[Enter\]**

**\[chown -R postgres:postgres pgsql\] \[Enter\]**

Execute the following command as a postgres user to make the Data Base.

-   Making of Data Base Folder

> **\[su - postgres\] \[Enter\]**
>
> **\[cd /usr/local/pgsql/9.3/\] \[Enter\]**
>
> **\[mkdir -m 700 data\] \[Enter\]**

-   Initialization of the Data Base

> **\[initdb \--encoding=UTF8 \--no-locale
> \--pgdata=/usr/local/pgsql/9.3/data \--auth=ident\] \[Enter\]**
>
> After the command execution, confirm the output looked like below.
>
> The files belonging to this database system will be owned by user
> \"postgres\".
>
> This user must also own the server process.
>
> The database cluster will be initialized with locale \"C\".
>
> The default text search configuration will be set to \"english\".
>
> Data page checksums are disabled.
>
> fixing permissions on existing directory /usr/local/pgsql/9.3/data
> \... ok
>
> creating subdirectories \... ok
>
> selecting default max\_connections \... 100
>
> selecting default shared\_buffers \... 128MB
>
> creating configuration files \... ok
>
> creating template1 database in /usr/local/pgsql/9.3/data/base/1 \...
> ok
>
> initializing pg\_authid \... ok
>
> initializing dependencies \... ok
>
> creating system views \... ok
>
> loading system objects\' descriptions \... ok
>
> creating collations \... ok
>
> creating conversions \... ok
>
> creating dictionaries \... ok
>
> setting privileges on built-in objects \... ok
>
> creating information schema \... ok
>
> loading PL/pgSQL server-side language \... ok
>
> vacuuming database template1 \... ok
>
> copying template1 to template0 \... ok
>
> copying template1 to postgres \... ok
>
> syncing data to disk \... ok
>
> Success. You can now start the database server using:
>
> postgres -D /usr/local/pgsql/9.3/data
>
> or
>
> pg\_ctl -D /usr/local/pgsql/9.3/data -l logfile start

-   Making of the Data Base

> **\[pg\_ctl -D /usr/local/pgsql/9.3/data -l logfile start\]
> \[Enter\]**
>
> After the execution, "server starting" will be displayed in the
> screen.
>
> **\[psql -c \"alter user postgres with password \'\'\"\] \[Enter\]**
>
> After the execution, "ALTER ROLE" will be displayed in the screen.
>
> **\[psql\] \[Enter\]**
>
> **\[create role root login createdb password \'\';\] \[Enter\]**
>
> After the execution, "CREATE ROLE" will be displayed in the screen.
>
> **\[\\q\] \[Enter\]**
>
> **\[pg\_ctl -D /usr/local/pgsql/9.3/data -l logfile stop\] \[Enter\]**
>
> After the execution, the following message will be displayed in the
> screen.
>
> waiting for server to shut down\.... done
>
> server stopped
>
> **\[exit\] \[Enter\]**

Execute the following command as the root user.

**\[chkconfig postgresql-9.3 on\] \[Enter\]**

**\[systemctl daemon-reload\] \[Enter\]**

#### 3.1.5.4. Change of the Data Base Configuration

**&lt;Execution Host: DB&gt;**

Change the configuration as follows.

**\[vi /usr/local/pgsql/9.3/data/postgresql.conf\] \[Enter\]**

**Before Change**

\--

\#listen\_addresses = \'localhost\'

\#port = 5432

\--

**After Change**

\--

listen\_addresses = \'**\***\'

port = 5432

\--

> Change the configuration as follows. (Replace **the highlighted
> section** with the server segment to permit.)

**\[vi /usr/local/pgsql/9.3/data/pg\_hba.conf\] \[Enter\]**

Before Change

\--

\# TYPE DATABASE USER ADDRESS METHOD

\# \"local\" is for Unix domain socket connections only

local all all peer

\# IPv4 local connections:

host all all 127.0.0.1/32 ident

\# IPv6 local connections:

host all all ::1/128 ident

\# Allow replication connections from localhost, by a user with the

\# replication privilege.

\#local replication postgres peer

\#host replication postgres 127.0.0.1/32 ident

\#host replication postgres ::1/128 ident

After Change

\--

\# TYPE DATABASE USER ADDRESS METHOD

\# \"local\" is for Unix domain socket connections only

**\#**local all all peer

\# IPv4 local connections:

**\#**host all all 127.0.0.1/32 ident

\# IPv6 local connections:

**\#**host all all ::1/128 ident

\# Allow replication connections from localhost, by a user with the

\# replication privilege.

\#local replication postgres peer

\#host replication postgres 127.0.0.1/32 ident

\#host replication postgres ::1/128 ident

local all postgres peer

local all all trust

host all all **192.168.53.0/24** trust

host all all 127.0.0.1/32 trust

Change the configuration as follows. (Modify the highlighted section.)

**\[vi /usr/lib/systemd/system/postgresql-9.3.service\] \[Enter\]**

\--

\# Location of database directory

Environment=PGDATA=/usr/local/pgsql/9.3/data/

\--

#### 3.1.5.5. Restart the Data Base

**&lt;Execution Host: DB&gt;**

Execute the following command as a postgres user.

**\[systemctl daemon-reload\] \[Enter\]**

**\[systemctl start postgresql-9.3\] \[Enter\]**

Execute the following command to confirm the running of postgres.

**\[systemctl status postgresql-9.3\] \[Enter\]**

The following message will be displayed after the command. Check the
highlighted (red letters) comments below.

> Active: active (running) **&lt;- Make sure it is "running".**
>
> CGroup: /system.slice/postgresql-9.3.service
>
> tq\*\*\*\*\* /usr/pgsql-9.3/bin/postgres -D /usr/local/pgsql/9.3/data
> **&lt;- Make sure that the folder just created is specified. **

[[]{#_Toc500159207 .anchor}]{#_Toc499552704 .anchor}

### 3.1.6. Installation of sysstat(sar)

#### 3.1.6.1. Installation

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command to install sysstat.

**\[cd \~/setup/em/installer/sysstat-11.6.0-1\] \[Enter\]**

**\[rpm -ihv sysstat-11.6.0-1.x86\_64.rpm\] \[Enter\]**

### 3.1.7. Installation of Flask

#### 3.1.7.1. Installation

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command to install flask.

**\[cd \~/setup/em/installer/flask-0.12.2\] \[Enter\]**

**\[pip install click-6.7-py2.py3-none-any.whl\] \[Enter\]**

**\[pip install itsdangerous-0.24.tar.gz\] \[Enter\]**

**\[pip install Jinja2-2.9.6-py2.py3-none-any.whl\] \[Enter\]**

**\[pip install MarkupSafe-1.0.tar.gz\] \[Enter\]**

**\[pip install Werkzeug-0.12.2-py2.py3-none-any.whl\] \[Enter\]**

**\[pip install Flask-0.12.2-py2.py3-none-any.whl\] \[Enter\]**

\* Installation must be done in the above order.

3.2. Installation of EM Module
-------------------------

Hereafter, the written expression \"\$EM\_HOME\" represents any location
path specified by the user.

The following is an example for making /opt/em the installation
directory.

**\[export EM\_HOME=/opt/em\] \[Enter\]**

### 3.2.1. Locating the Library

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command to locate the library file which is in the
included accessories.

**\[mkdir -p \$EM\_HOME/lib\] \[Enter\]**

**\[cp -r \~/setup/em/EmModule/lib/\* \$EM\_HOME/lib/\] \[Enter\]**

Grant executional privilege to the located file with the following
steps.

**\[chmod 777 \$EM\_HOME/lib/MsfEmMain.py\] \[Enter\]**

### 3.2.2. Locating the Configuration File

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command to locate the configuration file which is
in the included accessories.

**\[mkdir -p \$EM\_HOME/conf\] \[Enter\]**

**\[cp -r \~/setup/em**/**EmModule/conf/\* \$EM\_HOME/conf/\]
\[Enter\]**

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

\*Please modify configuration values based on your installed server.

Please refer to "Appendix\_Configuration Specifications.xlsx" for the
details of the change.

### 3.2.3. Locating the Startup Shell

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command to locate the startup shell file which is
in the included accessories.

**\[mkdir -p \$EM\_HOME/bin\] \[Enter\]**

**\[cp -r \~/setup/em/EmModule/bin/\* \$EM\_HOME/bin/\] \[Enter\]**

Grant executional privilege to the located file in accordance with the
following steps.

**\[cd \$EM\_HOME/bin\] \[Enter\]**

**\[chmod 777 em\_ctl.sh\] \[Enter\]**

**\[chmod 777 controller\_status.sh\] \[Enter\]**

### 3.2.4. Making of Log Folder

**&lt;Execution Host: ACT/SBY&gt;**

> Make the folder for logging by use of the following command.

**\[mkdir -p \$EM\_HOME/logs/em/log\] \[Enter\]**

### 3.2.5. Making of Schema

**&lt;Execution Host: DB&gt;**

Make the schema by use of the following command.

**\[createdb "Schema Name"\] \[Enter\]**

Make a table in the schema by use of the following command.

**\[cd \~/setup/em/script/\] \[Enter\]**

**\[psql "Schema Name" &lt; create\_table.sql\] \[Enter\]**

### 3.2.6. Configuration of Monitoring Account for Resource Agent

**&lt;Execution Host: ACT/SBY&gt;**

Set the IP address, connecting user name and password for EM monitoring
to the startup script.

Modify the configuration definition of startup script by use of the
following command.

**\[cd \$EM\_HOME/bin\] \[Enter\]**

**\[vi em\_ctl.sh\] \[Enter\]**

Edit the following lines. (Modify the highlighted section.)

&lt;Before Change&gt;

> \# Environmental Definition
>
> \# Set information to access EM from the monitoring module
>
> \# Login User Name for EM
>
> USERNAME=\"root\"
>
> \# Loging Password for EM
>
> PASSWORD=\"\"
>
> \# Waiting IP Address for EM
>
> IPV4=\"127.0.0.1\"
>
> \# Waiting Port for EM
>
> PORT=830

&lt;After Change&gt;

> \# Environmental Definition
>
> \# Set information to access EM from the monitoring module
>
> \# Login User Name for EM
>
> USERNAME = "(User Name that has been set to the Account at
> conf\_if\_process.conf of EM)"
>
> \# Login Password for EM
>
> PASSWORD = "(Password that has been set to the Password at
> conf\_if\_process.conf of EM)"
>
> \# Waiting IP Address for EM
>
> IPV4 = "(IP Address that has been set to the Netconf\_server\_address
> at conf\_if\_process.conf of EM)"
>
> PORT = "(Port Number that has been set to the Port\_number at
> conf\_if\_process.conf of EM)"

Save it when you have completed the edit.

### 3.2.7. Configuration of Environment Variables

**&lt;Execution Host: ACT/SBY&gt;**

Open the file to register environment variables by use of the following
command.

**\[vi /root/.bash\_profile\] \[Enter\]**

Add the following lines in the end of the file.

> PYTHONPATH=""
>
> PYTHONPATH=\"\$PYTHONPATH:/lib/ocf/resource.d/heartbeat\"
>
> export PYTHONPATH

Change the PATH environment variable as follows.

&lt;Before Change&gt;

> PATH=\$PATH:\$HOME/bin

&lt;After Change&gt; ( Add the highlighted section.)

> PATH=\$PATH:\$HOME/bin:\$EMTOPPATH/bin:/usr/bin/python

Save and close the file when you have completed the addition.

3.3. Registration and Configuration of the Resource Agent
----------------------------------------------------

### 3.3.1. Locating the Resource Agent

**&lt;Execution Host: ACT/SBY&gt;**

Copy the EM resource agent from the startup shell folder of EM
installation folder to the default resource agent folder.

> **\[cp \$EM\_HOME/bin/em /lib/ocf/resource.d/heartbeat/\] \[Enter\]**

Then grant execution privilege to the copied EM resource agent.

> **\[cd /lib/ocf/resource.d/heartbeat/\] \[Enter\]**
>
> **\[chmod 775 em\] \[Enter\]**

### 3.3.2. Making of crm File

**&lt;Execution Host: ACT&gt;**

Create a working folder to locate files. (It should be removed when the
configuration completes.)

**\[mkdir \~/setup\] \[Enter\]**

Edit the ra\_config.xlsx file, which has the configuration of resource
agent in the included accessories, for updating the necessary
information, then convert it to a csv file and locate in the working
folder.

Execute the following command at the folder where you locate the csv
file to convert it into a crm file that is used for registering it to
the resource agent.

> **\[pm\_crmgen -o crm\_conf.crm (located csv file name).csv\]
> \[Enter\]**

If the conversion completes successfully, nothing will be displayed in
the screen but in case anything went wrong with the csv file, the
location to be amended would be displayed.

### 3.3.3. Injection of crm File

**&lt;Execution Host: ACT&gt;**

> With the following commend, register the resource agent.
>
> **\[crm configure load update crm\_conf.crm\] \[Enter\]**

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

### 3.3.4. Confirmation of the Result of Injection

**&lt;Execution Host: ACT or SBY&gt;**

Confirm the operational status of resource agent with the following
command.

> **\[crm\_mon --fA -1\] \[Enter\]**

If it injected successfully, a message will be displayed as follows.

Last updated: WDW MMM DD HH:MM:SS YYYY Last change: WDW MMM DD HH:MM:SS
YYYY by root via cibadmin on (Active Node Name or Stand-by Node Name)

Stack: corosync

Current DC: (Active Node Name or Stand-by Node Name) (version
1.1.14-1.el7-70404b0) - partition with quorum

2 nodes and 6 resources configured

Online: \[(Active Node Name) (Stand-by Node Name)\]

Resource Group: grpEC

vipCheck (ocf::heartbeat:VIPcheck): Started (Active Node Name)

prmIP (ocf::heartbeat:IPaddr2): Started (Active Node Name)

prmEC (ocf::heartbeat:ec): Started (Active Node Name)

prmSNMPTrapd (ocf::heartbeat:snmptrapd): Started (Active Node Name)

Clone Set: clnDiskd \[prmDiskd\]

Started: \[(Active Node Name) (Stand-by Node Name)\]

Node Attributes:

\* Node (Active Node Name):

\+ diskcheck\_status\_internal : normal

\* Node (Stand-by Node Name):

\+ diskcheck\_status\_internal : normal

Migration Summary:

\* Node (Active Node Name):

\* Node Stand-by Node Name):
(0.7.18)

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

### 3.1.4. Installation and Configuration of NTP

#### 3.1.4.1. Installation

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command to install ntp.

**\[cd \~/setup/em/installer/ntp.v4.2/\] \[Enter\]**

**\[rpm -ivh autogen-libopts-5.18-5.el7.x86\_64.rpm\] \[Enter\]**

**\[rpm -ivh ntpdate-4.2.6p5-22.el7.centos.x86\_64.rpm\] \[Enter\]**

**\[rpm -ivh ntp-4.2.6p5-22.el7.centos.x86\_64.rpm\] \[Enter\]**

#### 3.1.4.2. Making of drift File

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command to make a blank drift file.

**\[touch /var/lib/ntp/drift\] \[Enter\]**

#### 3.1.4.3. Change of the NTP Configuration File

**&lt;Execution Host: ACT/SBY&gt;**

Add the following lines (**the highlighted section**) to the NTP
configuration file (/etc/ntp.conf) as the root user.

**\[vi /etc/ntp.conf\] \[Enter\]**

...

restrict default nomodify notrap nopeer noquery

**restrict default ignore**

...

\#restrict 192.168.1.0 mask 255.255.255.0 nomodify notrap

**restrict xxx.xxx.xxx.xxx noquery nomodify**

**server xxx.xxx.xxx.xxx iburst**

...

#### 3.1.4.4. Synchronization with NTP Server

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command to confirm that NTP is not running.

**\[systemctl status ntpd.service\] \[Enter\]**

&lt;Output in case NTP is not running&gt;

...

Active: inactive (dead)

...

&lt;Output in case NTP is running&gt;

...

Active: active (running)

...

In case NTP is running, execute the following command to stop the NTP.

**\[systemctl stop ntpd.service\] \[Enter\]**

Synchronize the time with NTP server (IP address: xxx.xxx.xxx.xxx).

**\[ntpdate xxx.xxx.xxx.xxx\] \[Enter\]**

#### 3.1.4.5. Restart of the NTP

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command to restart NTP.

**\[systemctl restart ntpd.service\] \[Enter\]**

**\[systemctl enable ntpd.service\] \[Enter\]**

Execute the following command to confirm the synchronization with NTP
server.

**\[ntpq -p\] \[Enter\]**

&lt;output example when the synchronization established successfully &gt;

| remote refid st t when poll reach delay offset jitter               |
|---------------------------------------------------------------------|
| \*xxx.xxx.xxx.xxx LOCAL(0) 11 u 55 64 377 0.130 -0.017 0.017        |

### 3.1.5. Installation and Configuration of PostgreSQL

#### 3.1.5.1. Installation

**&lt;Execution Host: DB/ACT/SBY&gt;**

Execute the following command to install postgresql.

**\[cd \~/setup/em/installer/postgresql.v9.3.13\] \[Enter\]**

**\[rpm -ivh libxslt-1.1.28-5.el7.x86\_64.rpm\] \[Enter\]**

**\[rpm -ivh uuid-1.6.2-26.el7.x86\_64.rpm\] \[Enter\]**

**\[rpm -ivh postgresql93-libs-9.3.13-1PGDG.rhel7.x86\_64.rpm\]
\[Enter\]**

**\[rpm -ivh postgresql93-9.3.13-1PGDG.rhel7.x86\_64.rpm\] \[Enter\]**

**\[rpm -ivh postgresql93-server-9.3.13-1PGDG.rhel7.x86\_64.rpm\]
\[Enter\]**

**\[rpm -ivh postgresql93-devel-9.3.13-1PGDG.rhel7.x86\_64.rpm\]
\[Enter\]**

**\[rpm -ivh postgresql93-contrib-9.3.13-1PGDG.rhel7.x86\_64.rpm\]
\[Enter\]**

#### 3.1.5.2. Change the PostgreSQL Configuration

**&lt;Execution Host: DB&gt;**

Change the configuration as follows.

**\[vi /var/lib/pgsql/.bash\_profile\] \[Enter\] (Modify or add the
highlighted section)**

PGDATA=/usr/local/pgsql/9.3/data

export PGDATA

export PATH=\$PATH:/usr/pgsql-9.3/bin

**\[source /var/lib/pgsql/.bash\_profile\] \[Enter\]**

#### 3.1.5.3. Making of Data Base and Granting Permissions

**&lt;Execution Host: DB&gt;**

Execute the following command to make the installation folder of the
Data Base.

**\[cd /usr/local/\] \[Enter\]**

**\[mkdir -pm 777 /usr/local/pgsql/9.3\] \[Enter\]**

**\[chown -R postgres:postgres pgsql\] \[Enter\]**

Execute the following command as a postgres user to make the Data Base.

-   Making of Data Base Folder

> **\[su - postgres\] \[Enter\]**
>
> **\[cd /usr/local/pgsql/9.3/\] \[Enter\]**
>
> **\[mkdir -m 700 data\] \[Enter\]**

-   Initialization of the Data Base

> **\[initdb \--encoding=UTF8 \--no-locale
> \--pgdata=/usr/local/pgsql/9.3/data \--auth=ident\] \[Enter\]**
>
> After the command execution, confirm the output looked like below.
>
> The files belonging to this database system will be owned by user
> \"postgres\".
>
> This user must also own the server process.
>
> The database cluster will be initialized with locale \"C\".
>
> The default text search configuration will be set to \"english\".
>
> Data page checksums are disabled.
>
> fixing permissions on existing directory /usr/local/pgsql/9.3/data
> \... ok
>
> creating subdirectories \... ok
>
> selecting default max\_connections \... 100
>
> selecting default shared\_buffers \... 128MB
>
> creating configuration files \... ok
>
> creating template1 database in /usr/local/pgsql/9.3/data/base/1 \...
> ok
>
> initializing pg\_authid \... ok
>
> initializing dependencies \... ok
>
> creating system views \... ok
>
> loading system objects\' descriptions \... ok
>
> creating collations \... ok
>
> creating conversions \... ok
>
> creating dictionaries \... ok
>
> setting privileges on built-in objects \... ok
>
> creating information schema \... ok
>
> loading PL/pgSQL server-side language \... ok
>
> vacuuming database template1 \... ok
>
> copying template1 to template0 \... ok
>
> copying template1 to postgres \... ok
>
> syncing data to disk \... ok
>
> Success. You can now start the database server using:
>
> postgres -D /usr/local/pgsql/9.3/data
>
> or
>
> pg\_ctl -D /usr/local/pgsql/9.3/data -l logfile start

-   Making of the Data Base

> **\[pg\_ctl -D /usr/local/pgsql/9.3/data -l logfile start\]
> \[Enter\]**
>
> After the execution, "server starting" will be displayed in the
> screen.
>
> **\[psql -c \"alter user postgres with password \'\'\"\] \[Enter\]**
>
> After the execution, "ALTER ROLE" will be displayed in the screen.
>
> **\[psql\] \[Enter\]**
>
> **\[create role root login createdb password \'\';\] \[Enter\]**
>
> After the execution, "CREATE ROLE" will be displayed in the screen.
>
> **\[\\q\] \[Enter\]**
>
> **\[pg\_ctl -D /usr/local/pgsql/9.3/data -l logfile stop\] \[Enter\]**
>
> After the execution, the following message will be displayed in the
> screen.
>
> waiting for server to shut down\.... done
>
> server stopped
>
> **\[exit\] \[Enter\]**

Execute the following command as the root user.

**\[chkconfig postgresql-9.3 on\] \[Enter\]**

**\[systemctl daemon-reload\] \[Enter\]**

#### 3.1.5.4. Change of the Data Base Configuration

**&lt;Execution Host: DB&gt;**

Change the configuration as follows.

**\[vi /usr/local/pgsql/9.3/data/postgresql.conf\] \[Enter\]**

**Before Change**

\--

\#listen\_addresses = \'localhost\'

\#port = 5432

\--

**After Change**

\--

listen\_addresses = \'**\***\'

port = 5432

\--

> Change the configuration as follows. (Replace **the highlighted
> section** with the server segment to permit.)

**\[vi /usr/local/pgsql/9.3/data/pg\_hba.conf\] \[Enter\]**

Before Change

\--

\# TYPE DATABASE USER ADDRESS METHOD

\# \"local\" is for Unix domain socket connections only

local all all peer

\# IPv4 local connections:

host all all 127.0.0.1/32 ident

\# IPv6 local connections:

host all all ::1/128 ident

\# Allow replication connections from localhost, by a user with the

\# replication privilege.

\#local replication postgres peer

\#host replication postgres 127.0.0.1/32 ident

\#host replication postgres ::1/128 ident

After Change

\--

\# TYPE DATABASE USER ADDRESS METHOD

\# \"local\" is for Unix domain socket connections only

**\#**local all all peer

\# IPv4 local connections:

**\#**host all all 127.0.0.1/32 ident

\# IPv6 local connections:

**\#**host all all ::1/128 ident

\# Allow replication connections from localhost, by a user with the

\# replication privilege.

\#local replication postgres peer

\#host replication postgres 127.0.0.1/32 ident

\#host replication postgres ::1/128 ident

local all postgres peer

local all all trust

host all all **192.168.53.0/24** trust

host all all 127.0.0.1/32 trust

Change the configuration as follows. (Modify the highlighted section.)

**\[vi /usr/lib/systemd/system/postgresql-9.3.service\] \[Enter\]**

\--

\# Location of database directory

Environment=PGDATA=/usr/local/pgsql/9.3/data/

\--

#### 3.1.5.5. Restart the Data Base

**&lt;Execution Host: DB&gt;**

Execute the following command as a postgres user.

**\[systemctl daemon-reload\] \[Enter\]**

**\[systemctl start postgresql-9.3\] \[Enter\]**

Execute the following command to confirm the running of postgres.

**\[systemctl status postgresql-9.3\] \[Enter\]**

The following message will be displayed after the command. Check the
highlighted (red letters) comments below.

> Active: active (running) **&lt;- Make sure it is "running".**
>
> CGroup: /system.slice/postgresql-9.3.service
>
> tq\*\*\*\*\* /usr/pgsql-9.3/bin/postgres -D /usr/local/pgsql/9.3/data
> **&lt;- Make sure that the folder just created is specified. **

[[]{#_Toc500159207 .anchor}]{#_Toc499552704 .anchor}

### 3.1.6. Installation of sysstat(sar)

#### 3.1.6.1. Installation

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command to install sysstat.

**\[cd \~/setup/em/installer/sysstat-11.6.0-1\] \[Enter\]**

**\[rpm -ihv sysstat-11.6.0-1.x86\_64.rpm\] \[Enter\]**

### 3.1.7. Installation of Flask

#### 3.1.7.1. Installation

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command to install flask.

**\[cd \~/setup/em/installer/flask-0.12.2\] \[Enter\]**

**\[pip install click-6.7-py2.py3-none-any.whl\] \[Enter\]**

**\[pip install itsdangerous-0.24.tar.gz\] \[Enter\]**

**\[pip install Jinja2-2.9.6-py2.py3-none-any.whl\] \[Enter\]**

**\[pip install MarkupSafe-1.0.tar.gz\] \[Enter\]**

**\[pip install Werkzeug-0.12.2-py2.py3-none-any.whl\] \[Enter\]**

**\[pip install Flask-0.12.2-py2.py3-none-any.whl\] \[Enter\]**

\* Installation must be done in the above order.

3.2. Installation of EM Module
-------------------------

Hereafter, the written expression \"\$EM\_HOME\" represents any location
path specified by the user.

The following is an example for making /opt/em the installation
directory.

**\[export EM\_HOME=/opt/em\] \[Enter\]**

### 3.2.1. Locating the Library

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command to locate the library file which is in the
included accessories.

**\[mkdir -p \$EM\_HOME/lib\] \[Enter\]**

**\[cp -r \~/setup/em/EmModule/lib/\* \$EM\_HOME/lib/\] \[Enter\]**

Grant executional privilege to the located file with the following
steps.

**\[chmod 777 \$EM\_HOME/lib/MsfEmMain.py\] \[Enter\]**

### 3.2.2. Locating the Configuration File

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command to locate the configuration file which is
in the included accessories.

**\[mkdir -p \$EM\_HOME/conf\] \[Enter\]**

**\[cp -r \~/setup/em**/**EmModule/conf/\* \$EM\_HOME/conf/\]
\[Enter\]**

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

\*Please modify configuration values based on your installed server.

Please refer to "Appendix\_Configuration Specifications.xlsx" for the
details of the change.

### 3.2.3. Locating the Startup Shell

**&lt;Execution Host: ACT/SBY&gt;**

Execute the following command to locate the startup shell file which is
in the included accessories.

**\[mkdir -p \$EM\_HOME/bin\] \[Enter\]**

**\[cp -r \~/setup/em/EmModule/bin/\* \$EM\_HOME/bin/\] \[Enter\]**

Grant executional privilege to the located file in accordance with the
following steps.

**\[cd \$EM\_HOME/bin\] \[Enter\]**

**\[chmod 777 em\_ctl.sh\] \[Enter\]**

**\[chmod 777 controller\_status.sh\] \[Enter\]**

### 3.2.4. Making of Log Folder

**&lt;Execution Host: ACT/SBY&gt;**

> Make the folder for logging by use of the following command.

**\[mkdir -p \$EM\_HOME/logs/em/log\] \[Enter\]**

### 3.2.5. Making of Schema

**&lt;Execution Host: DB&gt;**

Make the schema by use of the following command.

**\[createdb "Schema Name"\] \[Enter\]**

Make a table in the schema by use of the following command.

**\[cd \~/setup/em/script/\] \[Enter\]**

**\[psql "Schema Name" &lt; create\_table.sql\] \[Enter\]**

### 3.2.6. Configuration of Monitoring Account for Resource Agent

**&lt;Execution Host: ACT/SBY&gt;**

Set the IP address, connecting user name and password for EM monitoring
to the startup script.

Modify the configuration definition of startup script by use of the
following command.

**\[cd \$EM\_HOME/bin\] \[Enter\]**

**\[vi em\_ctl.sh\] \[Enter\]**

Edit the following lines. (Modify the highlighted section.)

&lt;Before Change&gt;

> \# Environmental Definition
>
> \# Set information to access EM from the monitoring module
>
> \# Login User Name for EM
>
> USERNAME=\"root\"
>
> \# Loging Password for EM
>
> PASSWORD=\"\"
>
> \# Waiting IP Address for EM
>
> IPV4=\"127.0.0.1\"
>
> \# Waiting Port for EM
>
> PORT=830

&lt;After Change&gt;

> \# Environmental Definition
>
> \# Set information to access EM from the monitoring module
>
> \# Login User Name for EM
>
> USERNAME = "(User Name that has been set to the Account at
> conf\_if\_process.conf of EM)"
>
> \# Login Password for EM
>
> PASSWORD = "(Password that has been set to the Password at
> conf\_if\_process.conf of EM)"
>
> \# Waiting IP Address for EM
>
> IPV4 = "(IP Address that has been set to the Netconf\_server\_address
> at conf\_if\_process.conf of EM)"
>
> PORT = "(Port Number that has been set to the Port\_number at
> conf\_if\_process.conf of EM)"

Save it when you have completed the edit.

### 3.2.7. Configuration of Environment Variables

**&lt;Execution Host: ACT/SBY&gt;**

Open the file to register environment variables by use of the following
command.

**\[vi /root/.bash\_profile\] \[Enter\]**

Add the following lines in the end of the file.

> PYTHONPATH=""
>
> PYTHONPATH=\"\$PYTHONPATH:/lib/ocf/resource.d/heartbeat\"
>
> export PYTHONPATH

Change the PATH environment variable as follows.

&lt;Before Change&gt;

> PATH=\$PATH:\$HOME/bin

&lt;After Change&gt; ( Add the highlighted section.)

> PATH=\$PATH:\$HOME/bin:\$EMTOPPATH/bin:/usr/bin/python

Save and close the file when you have completed the addition.

3.3. Registration and Configuration of the Resource Agent
----------------------------------------------------

### 3.3.1. Locating the Resource Agent

**&lt;Execution Host: ACT/SBY&gt;**

Copy the EM resource agent from the startup shell folder of EM
installation folder to the default resource agent folder.

> **\[cp \$EM\_HOME/bin/em /lib/ocf/resource.d/heartbeat/\] \[Enter\]**

Then grant execution privilege to the copied EM resource agent.

> **\[cd /lib/ocf/resource.d/heartbeat/\] \[Enter\]**
>
> **\[chmod 775 em\] \[Enter\]**

### 3.3.2. Making of crm File

**&lt;Execution Host: ACT&gt;**

Create a working folder to locate files. (It should be removed when the
configuration completes.)

**\[mkdir \~/setup\] \[Enter\]**

Edit the ra\_config.xlsx file, which has the configuration of resource
agent in the included accessories, for updating the necessary
information, then convert it to a csv file and locate in the working
folder.

Execute the following command at the folder where you locate the csv
file to convert it into a crm file that is used for registering it to
the resource agent.

> **\[pm\_crmgen -o crm\_conf.crm (located csv file name).csv\]
> \[Enter\]**

If the conversion completes successfully, nothing will be displayed in
the screen but in case anything went wrong with the csv file, the
location to be amended would be displayed.

### 3.3.3. Injection of crm File

**&lt;Execution Host: ACT&gt;**

> With the following commend, register the resource agent.
>
> **\[crm configure load update crm\_conf.crm\] \[Enter\]**

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

### 3.3.4. Confirmation of the Result of Injection

**&lt;Execution Host: ACT or SBY&gt;**

Confirm the operational status of resource agent with the following
command.

> **\[crm\_mon --fA -1\] \[Enter\]**

If it injected successfully, a message will be displayed as follows.

Last updated: WDW MMM DD HH:MM:SS YYYY Last change: WDW MMM DD HH:MM:SS
YYYY by root via cibadmin on (Active Node Name or Stand-by Node Name)

Stack: corosync

Current DC: (Active Node Name or Stand-by Node Name) (version
1.1.14-1.el7-70404b0) - partition with quorum

2 nodes and 6 resources configured

Online: \[(Active Node Name) (Stand-by Node Name)\]

Resource Group: grpEC

vipCheck (ocf::heartbeat:VIPcheck): Started (Active Node Name)

prmIP (ocf::heartbeat:IPaddr2): Started (Active Node Name)

prmEC (ocf::heartbeat:ec): Started (Active Node Name)

prmSNMPTrapd (ocf::heartbeat:snmptrapd): Started (Active Node Name)

Clone Set: clnDiskd \[prmDiskd\]

Started: \[(Active Node Name) (Stand-by Node Name)\]

Node Attributes:

\* Node (Active Node Name):

\+ diskcheck\_status\_internal : normal

\* Node (Stand-by Node Name):

\+ diskcheck\_status\_internal : normal

Migration Summary:

\* Node (Active Node Name):

\* Node Stand-by Node Name):
