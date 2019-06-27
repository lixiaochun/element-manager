## Element Manager Configuration Specifications

**Version 1.0**
** June 27, 2019 **
** Copyright(c) 2019 Nippon Telegraph and Telephone Corporation**

### Configuration Definitions

Configurations are classified and defined by their usage. Also, they are distributed into separate files according to the usage. The table below is a list of them.

|Name   |Description            |
|:---------|:---------------|
|conf_if_process.conf|It defines the Netconf server address, port number, host key information and Capability information, which are necessary for operating the  I/F Process Part. |
|conf_if_process_rest.conf|It defines the REST server address, port number, host key information and Capability information, which are necessary for operating the  I/F Process Part.|
|conf_scenario.conf|It defines the files to be started for each service type and operation type that is needed for operating Scenario Individual part.|
|conf_scenario_rest.conf|It defines the files to be started for each URI that is needed for operating REST Scenario Individual Part.|
|conf_driver.conf|It defines the files to be started for each platform name, OS and firmware version that is required for operating Driver Individual Part.|
|conf_sys_common.conf|It defines the common configuration items (DB server address, port number, Data Base name, DB access user name, DB access user password, configured value for confirm-timeout, etc.) that are necessary for EM.|
|conf_separate_driver_cisco.conf|Configurations that are used in the Individual Driver (cisco) but not used in the Configuration Management Function. It defines the detailed information of the variable parameters that are necessary for injecting data to Cisco devices.|
|conf_internal_link_vlan.conf|VLAN ID setting config for internal link. (Internal link configuration for Beluganos opposing device.) |
|conf_act_threshold.conf    |It defines the threshold for the monitored value in the ACT server.|
|conf_sby_threshold.conf    |It defines the threshold for the monitored value in the SBY server.|
|conf_asr_device_<Device Name>.conf      |It defines the parameters required to register the CGW-SH device(ASR) information to DB when EM is initiated.<br> The number of the parameter files should be the same as  that of the devices.<br> The definitions are described using XML.|
|conf_nvr_device_<Device Name>.conf      |It defines the parameters required to register the CGW-SH device(NVR) information to DB when EM is initiated.<br> The number of the parameter files should be the same as  that of the devices.<br> The definitions are described using XML.|
|conf_<Driver Name>_audit_exclusion.conf |It defines the configuration files to be excluded on the base of the gotten diffrence information.<br> The number of these files should be the same as  that of the devices.|

### Rules of Description for Configurations

There are some rules to describe definitions in configuration files with KEY_VALUE method as follows.

|No.  |Rule of Description|
|:---------|:---------------|
|1|Character Code: UTF-8|
|2|Line Feed Code: LF|
|3|Delimiter between Key and Value: =|
|4|A line feed must be inserted just after each pair of key and value.|
|5|If a line is started with "#", it is a comment line (and will not be imported).|
|6|Half-width space and TAB characters are prohibited to be used (even in front or behind of "=" sign) except in comments.|
|7|Full-width characters (incl. all Japanese characters) are prohibited to be used except in comments.|
|8|Characters "=" and "#" are prohibited to be used in keys and values.|

Description Example (case of `conf_if_process.conf`)

~~~console
#Netconf Server Address
Netconf_server_address=0.0.0.0
#Port Number
Port_number=8080
~~~

### Rules of Description for Configurations (XML)

There are some rules to describe definitions in configuration files (XML) method as follows.

|No.  |Rule of Description|
|:---------|:---------------|
|1|Character Code: UTF-8|
|2|Line Feed Code: LF|
|3|Follow the XML description rules|
|4|Type follows Table 1. If the condition of the type is not satisfied, set it as an error.|
|5|When the number of elements is 1, it must be set, and if it is 0..1, it is set as necessary.|
|6|If the condition of the number of elements is not satisfied (1 is not set, etc.), it is set as an error.|
|7|In addition, if a value that causes an error is set for each item, it is set as an error.|


Table1. Type description
|Type      |Description     |
|:---------|:---------------|
|string    |Text            |
|uint      |Unsigned Integer|
|empty     |A parameter with no value. The parameter name itself has meaning.|
|container |A structured container that can hold multiple parameters.|
|list      |A structured list that can hold multiple parameters. (Need key parameters)|

Description Example (case of `conf_nvr_device_\<Device Name\>.conf`)

~~~console
 <registration-info>
   <device>
    <host-name>stm1spuni0101</host-name>
    <delete-flag>false</delete-flag>
    <address>192.168.10.2</address>
    <platform-name>NVR510</platform-name>
    <os-name>Rev.</os-name>
    <firm-version>15.01.02</firm-version>
    <username>username</username>
    <password>password</password>
    <administrator-password>password</administrator-password>
  </device> 
 </registration-info>
~~~

### Configuration Files Placement

The figure below shows the structure of configuration files placement.

~~~console
   conf
    „   Beluganos.conf
    „   Cisco.conf
    „   conf_driver.conf
    „   conf_if_process.conf
    „   conf_if_process_rest.conf
    „   conf_internal_link_vlan.conf
    „   conf_scenario.conf
    „   conf_scenario_rest.conf
    „   conf_separate_driver_cisco.conf
    „   conf_service.conf
    „   conf_sys_common.conf
    „   Cumulus.conf
    „   Juniper.conf
    „   OcNOS.conf
    „   conf_act_threshold.conf 
    „   conf_standby_threshold.conf
    „ 
    „¥„Ÿconf_audit
    „       conf_qfx5110_audit_exclusion.conf *1
    „ 
    „¤„Ÿfvw_device
            conf_asr_device_sample1.conf *2
            conf_nvr_device_sample1.conf *2
~~~

\*1 For conf_audit, set as many conf_\<Driver Name\>_audit_exclusion.conf as necessary.

\*2 For fvw_device, set as many conf_asr_device_sample1.conf or conf_nvr_device_sample1.conf as necessary.

### conf_if_process.conf

The table below shows the detail of items which are managed in this configuration file.

|No.|Item Name|Key|Description|Required?|default Value|Type|in case invalid value is set|Remarks|
|:----|:-----|:----|:-----|:----|:----|:----|:----|:----|
|1|Netconf Server Address|Netconf_server_address|Netconf Server Address|Yes|0.0.0.0|Text|Process cannot be started.|-|
|2|Port Number|Port_number|Netconf Port Number|Yes|8080|Numeral|Process cannot be started.|-|
|3|Account Name|Account|Set the certificate account name which is used in the I/F Process Part.|Yes|-|Text|SSH connection from EC cannot be established.|-|
|4|Password|Password|Set the certificate password which is used in the I/F Process Part.|Yes|-|Text|SSH connection from EC cannot be established.|-|
|5|Response plugin|Response_plugin|The file name is set for the plugin file used when the response message for Netconf are gererated.<br>(The file extension should not be included.)|Yes|-|Text|Process cannot be started.|Example :  NcsPluginCreateResponseMSF.py <br> -\> NcsPluginCreateResponseMSF|
|6|Capability Information 1|Capability1|Capability information 1 of HELLO to be sent to EC|Yes|-|Text|Capability exchange of HELLO cannot be performed.|-|
|7|Capability Information 2|Capability2|Capability information 2 of HELLO to be sent to EC|Yes|-|Text|Ditto.|-|

**Append lines each time when Capability Information is added in the future.**

### conf_if_process_rest.conf

The table below shows the detail of items which are managed in this configuration file.

|No.|Item Name|Key|Description|Required?|default Value|Type|in case invalid value is set|Remarks|
|:----|:-----|:----|:-----|:----|:----|:----|:----|:----|
|1|REST Server Address|Rest_server_address|REST Server Address|Yes|0.0.0.0|Text|Process cannot be started.|-|
|2|Port Number|Port_number|REST Port Number|Yes|8080|Numeral|Process cannot be started.|-|
|3|Controller Status Acquisition Shell Script Path|Statusget_shell_file_path|Path for Controller Status Acquisition Shell Script <br> The relative path from the lib/ in the EM install dirctory is required.|Yes|'../bin/controller_status.sh|Text|Process for acquiring controller status fails|-|
|4|Path for the script describing the failover method for the controllers  |Controller_switch_shell_file_path|The shell script path for executing the failover in the controller.<br> The relative path from the lib/ in the EM install dirctory is required.|Yes|'../bin/controller_switch.sh|Text|The failover process in the controllers fails.|-|

### conf_scenario.conf

This file specifies the configuration of each scenario performed by EM. Parameters set in each scenario are as follows.

For the clear description, please refer to the following file.

`conf/conf_scenario.conf`

|No.|Item Name|Key|Description|Required?|Type|
|:----|:-----|:----|:-----|:----|:----|
|1|Scenario Key Name|Scenario_key|The service type to run each scenario individual process from Order Flow Control|Yes|Test|
|2|Order Type|Scenario_order|The order type to run each scenario individual process from Order Flow Control|Yes|Text|
|3|Individual Scenario Startup Name|Scenario_name|The scenario name (Spine enhanced) to run each scenario individual process from Order Flow Control|Yes|Text|
|4|Waiting Time of Order Request for each scenario|Scenario_Timer_Order_Wait|The guard timer (ms) for each scenario. It watches that the time between the order reception and the configuration completion of all devices does not exceed the specified value.|Yes|Numeral|
|5|Service Transaction ID for each scenario|Scenario_Service_Transaction_No|An ID (Service Type) which is used by transaction management in Order Flow Control|Yes|Numeral|
|6|Order Transaction ID for each scenario|Scenario_Order_Transaction_No|The service type to run each scenario individual process from Order Flow Control|Yes|Numeral|

**Append lines each time when the items to be configured by each scenario are increased in the future.
**

### conf_scenario_rest.conf

The table below shows the detail of items which are managed in this configuration file.

|No.|Item Name|Key|Description|Required?|default Value|Type|in case invalid value is set|Remarks|
|:----|:-----|:----|:-----|:----|:----|:----|:----|:----|
|1|Scenario URI 1|Scenario_uri1|URI to start each scenario individual process from REST server|Yes|/v1/internal/em_ctrl/statusget|Text|Process cannot be started.|-|
|2|Individual Scenario Start Name 1|Scenario_name1|A scenario name (controller status acquisition) to start each scenario individual process from REST server|Yes|ControllerStatusGet|Text|Ditto.|-|
|3|Scenario URI 2|Scenario_uri2|URI to start each scenario individual process from REST server|Yes|/v1/internal/em_ctrl/log|Text|Ditto.|-|
|4|Individual Scenario Start Name 2|Scenario_name2|A scenario name (controller status acquisition) to start each scenario individual process from REST server|Yes|ControllerLogGet|Text|Ditto.|-|
|5|Scenario URI 3|Scenario_uri3|URI to start each scenario individual process from REST server|Yes|/v1/internal/em_ctrl/ctrl-switch|Text|Process cannot be started.|-|
|6|Individual Scenario Start Name 3|Scenario_name3|A scenario name (Switching system) to start each scenario individual process from REST server|Yes|ControllerSwitch|Text|Ditto.|-|


### conf_driver.conf

The table below shows the detail of items which are managed in this configuration file.

|No.|Item Name|Key|Description|Required?|default Value|Type|in case invalid value is set|Remarks|
|:----|:-----|:----|:-----|:----|:----|:----|:----|:----|
|1|Platform Name 1|Platform_name1|platform name of the target device|Yes|-|Text|driver selection failure|-|
|2|Driver OS 1|Driver_os1|OS of the target device|Yes|-|Text|Ditto.|-|
|3|Firmware Version 1|Firmware_ver1|firmware version of the target device|Yes|-|Text|Ditto.|-|
|4|Individual Driver Startup Name 1|Driver_name1|name of the driver which is started at the time of control request of the target device<br>* specified in absolute path|Yes|-|Text|Ditto.|-|
|5|Individual Driver Class Name 1|Driver_class1|name of the class which is started at the time of control request of the target device|Yes|-|Text|Ditto.|-|
|6|QoS Configuration File Name 1|Qos_conf_file1|name of the QoS settiong file <br> specified in relative path  assumption to be placed under conf directory  * see the additional explanation(**qos.conf**)|Yes|-|Text|Ditto.|Values are required even if there is no file.|
|7|Platform Name 2|Platform_name2|same as the first equivalent|Yes|-|Text|Ditto.|-|
|8|Driver OS 2|Driver_os2|same as the first equivalent|Yes|-|Text|Ditto.|-|
|9|Firmware Version 2|Firmware_ver2|same as the first equivalent|Yes|-|Text|Ditto.|-|
|10|Individual Driver Startup Name 2|Driver_name2|same as the first equivalent|Yes|-|Text|Ditto.|-|
|11|Individual Driver Class Name 2|Driver_class2|same as the first equivalent|Yes|-|Text|Ditto.|-|
|12|QoS Configuration File Name 2|Qos_conf_file2|same as the first equivalent|Yes|-|Text|Ditto.|Values are required even if there is no file.|

**Append lines each time when devices are added in the future.**

### conf_sys_common.conf

The table below shows the detail of items which are managed in this configuration file.

|No.|Item Name                                                                                         |Key                                       |Description|Required?|default Value|Type|in case invalid value is set|Remarks|
|:--|:-------------------------------------------------------------------------------------------------|:-----------------------------------------|:-----|:----|:----|:----|:----|:----|
|  1|DB Server Address                                                                                 |DB_server_address                         |DB server address|Yes|0.0.0.0|Text|-|-|
|  2|DB Access Port Number                                                                             |DB_access_port                            |DB access port number|Yes|5432|Numeral|-|-|
|  3|DB Access User Name                                                                               |DB_user                                   |DB access user name|Yes|-|Text|-|-|
|  4|DB Access Password                                                                                |DB_access_pass                            |DB access password|Yes|-|Text|-|-|
|  5|DB Access Table                                                                                   |DB_access_table                           |DB access table|Yes|-|Text|-|-|
|  6|Timer Value: confirmed-commit Configuration Time (ms)                                             |Timer_confirmed-commit                    |the timer value (ms) set in confirmed-commit|Yes|30000|Numeral|-|-|
|  7|Timer Value: confirmed-commit EM Internal Adjustment Time (ms)                                    |Timer_confirmed-commit_em_offset          |EM internal adjustment value (ms) for confirmed-commit<br>Both positive and negative vales are allowed.|Yes|0|Numeral|-|The sum of this value and that of Timer_confirmed-commit is set to the timer.|
|  8|Timer Value: Timer of confirmed-commit connected(ms)                                              |Timer_connect_get_before_config           |Time value(ms) of getting the configuration before device is connected.  |Yes|60000|Numeral|-|-|
|  9|Timer Value: Timer of confirmed-commit disconnected(ms)                                           |Timer_disconnect_get_after_config         |Time value(ms) of getting the configuration after device is disconnected.|Yes|60000|Numeral|-|-|
| 10|Timer Value: Netconf Protocol Timer Configuration Time (ms)                                       |Timer_netconf_protocol                    |NETCONF protocol timer value (ms)|Yes|60000|Numeral|The default value is set.|-|
| 11|Timer Value: CLI Protocol Timer Configuration Time (ms)                                           |Timer_cli_protocol                        |CLI protocol timer value (ms)|Yes|60000|Numeral|The default value is set.|-|
| 12|Timer Value: Signal Reception Waiting Timer Configuration Time (ms)                               |Timer_signal_rcv_wait                     |signal reception waiting timer value (ms)|Yes|1000|Numeral|The default value is set.|-|
| 13|Timer Value: Thread Stop Monitoring Timer Configuration Time (ms)                                 |Timer_thread_stop_watch                   |thread stop monitoring timer value (ms)|Yes|200|Numeral|The default value is set.|-|
| 14|Timer Value: Thread Stop Monitoring Timer Configuration Time in Periodic Execution Processing (ms)|Timer_periodic_execution_thread_stop_watch|timer value (ms) for  periodically monitoring thread stop|Yes|200|Numeral|The default value is set.|-|
| 15|Timer Value: Transaction End Monitoring Timer Configuration Time (ms)                             |Timer_transaction_stop_watch              |transaction end monitoring timer value (ms)|Yes|200|Numeral|The default value is set.|-|
| 16|Timer Value: Transaction DB Monitoring Timer Configuration Time (ms)                              |Timer_transaction_db_watch                |transaction DB monitoring timer value (ms)|Yes|100|Numeral|The default value is set.|-|
| 17|Timer Value: Connection Retry Time (ms)                                                           |Timer_connection_retry                    |connection retry timer value (ms)|Yes|5000|Numeral|The default value is set.|-|
| 18|Interval of notifying the controlloer status                                                      |Em_statusget_notify_interval              |Execution Interval for the controller-status notification |Yes|50000|Numeral|The default value is set.|-|
| 19|The Number of Connection Retries                                                                  |Connection_retry_num                      |the number of connection retries|Yes|5|Numeral|The default value is set.|-|
| 20|Log File Path                                                                                     |Em_log_file_path                          |It define the path of log file whose log level is the same as that of specified in the Em_log_level or higher. It define the relative path from lib/ in the EM install directory.|Yes|-|Text|Log cannot be saved correctly.|The file name should be application.log|
| 21|Log File Path  (log level is "INFO" or higher.)                                                   |Em_info_log_file_path                     |It defines the path of log files whose level "INFO" or higher. It defines the relative path from lib/ in the EM install directory.|Yes|-|Text|Log cannot be saved correctly.|The file name should be application_info.log|
| 22|Log Level                                                                                         |Em_log_level                              |Specify the log level of EM|Yes|DEBUG|Text|-|-|
| 23|The number of the rotated log files                                                               |Em_log_file_generation_num                |Number of generations storing log files. One log-rotation is treated as one generation.|Yes|DEBUG|Text|-|-|
| 24|The Number of REST Requests Average Time                                                          |Rest_request_average                      |The unit time (sec) for calculating the number of REST requests|Yes|3600|Numeral|The default value is set.||
| 25|IP Address of EM's Management I/F                                                                 |Controller_management_address             |Specify the IP address of EM's management I/F|Yes|0.0.0.0|Text|-|-|
| 26|IP Address of EC's REST Server                                                                    |Ec_rest_server_address                    |Specify the IP address of EC's REST server|Yes|0.0.0.0|Text|-|-|
| 27|Port Number of EC's REST Server                                                                   |Ec_port_number                            |Specify the port number of EC's REST server|Yes|18080|Numeral|-|-|
| 28|The Number of REST Notification Retries                                                           |Ec_rest_retry_num                         |Specify the number of REST notification retries|Yes|1|Numeral|-|-|
| 29|Interval of REST Notification Retry                                                               |Ec_rest_retry_interval                    |Specify the time interval of REST notification retry|Yes|1|Numeral|-|-|
| 30|Execution judgment configuration of controller status notification (Log Level : INFO)             |Em_notify_info_log                        |Execution judgment configuration of controller status notification (Log Level : INFO) ;If this configuration is "true", it should be notified. |Yes|FALSE|boolean|-|-|
| 31|Execution judgment configuration of controller status notification (Log Level : WARN)             |Em_notify_warn_log                        |Execution judgment configuration of controller status notification (Log Level : WARN) ;If this configuration is "true", it should be notified. |Yes|FALSE|boolean|-|-|
| 32|Execution judgment configuration of controller status notification (Log Level : ERROR)            |Em_notify_error_log                       |Execution judgment configuration of controller status notification (Log Level : ERROR) ;If this configuration is "true", it should be notified. |Yes|FALSE|boolean|-|-|
| 33|IP address for SBY                                                                                |Em_standby_server_address                 |SBY IP address used when the SBY contrller status is notified.|No |-|Text|-|This should not be set in case of the non-redundant-system.|
| 34|Shell File Path for getting  the SBY-controller staus                                             |Em_standby_server_statusget_shell_file_path|The script path for getting the SBY controller status|No |-|Text|-|This should not be set in case of the non-redundant-system.|
| 35|User Name for SBY log-in                                                                          |Em_standby_user                           |User name for SSH-connection with the SBY controller|No |-|Text|-|This should not be set in case of the non-redundant-system.|
| 36|User Password for SBY log-in                                                                      |Em_standby_access_pass                    |User password for SSH-connection with the SBY controller|No |-|Text|-|This should not be set in case of the non-redundant-system.|
| 37|Path for the configuration file on CGWSH device                                                   |Cgwsh_device_dir_path                     |It defines the configuation information on CGWSH device. And It defines the relative path from  /lib in EM install directory. |No |-|Text|-|This should not be set in case of the non-redundant-system.|
| 38|Path for the script file to confirmation on whether the rocked resource has been released         |Em_check_resource_lock                    |It defines the relative path for the script file to check the rocked resource in the redundant configuation.|No |-|Text|-|This should not be set in case of the non-redundant-system.|
| 39|Path for the script file to release the rocked resource                                           |Em_resource_lock_release                  |It defines the relative path for the script file to release the rocked resource in the redundant configuation.|No |-|Text|-|This should not be set in case of the non-redundant-system.|
| 40|Name of resource group                                                                            |Em_resource_group_name                    |Name of resource group which used confirming failover completion|No |-|Text|-|This should not be set in case of the non-redundant-system.|
| 41|Name of the monitored resource                                                                    |Em_resource_status_target_name            |Name of the monitored resource which used confirming failover completion|No |-|Text|-|This should not be set in case of the non-redundant-system.|
| 42|Interval for confirming failover completion                                                       |Em_resource_status_check_retry_num        |Interval for confirming failover completion|No |-|Numeral|-|This should not be set in case of the non-redundant-system.|
| 43|Number of times to confirm failover completion                                                    |Em_resource_status_check_retry_timer      |Number of times to confirm failover completion|No |-|Numeral|-|This should not be set in case of the non-redundant-system.|


### conf_separate_driver_cisco.conf

The table below shows the detail of items which are managed in this configuration file.

|No.|Item Name|Key|Description|Required?|default Value|Type|in case invalid value is set|Remarks|
|:----|:-----|:----|:-----|:----|:----|:----|:----|:----|
|1|I/F Name Prefix 1|IF_Name1|conventional prefix of the corresponding I/F name|Yes|-|Text|No default value can be set for this item.|Reference Value:<br>TenGigE|
|2|mtu owner Value 1|IF_Owner_Name1|the corresponding I/F's mtu owner value which is to be injected to the device|Yes|-|Text|No default value can be set for this item.|Reference Value:<br>TenGigE|
|3|Tracking Object Prefix 1|IF_TrackingObject_Name1|the initial of tracking object|Yes|-|Text|No default value can be set for this item.|Reference Value:<br>TG|
|4|I/F Name Prefix 2|IF_Name2|conventional prefix of the corresponding I/F name|Yes|-|Text|No default value can be set for this item.|Reference Value:<br>HundredGigE|
|5|mtu owner Value 2|IF_Owner_Name2|the corresponding I/F's mtu owner value which is to be injected to the device|Yes|-|Text|No default value can be set for this item.|Reference Value:<br>HundredGigE|
|6|Tracking Object Prefix 2|IF_TrackingObject_Name2|the initial of tracking object|Yes|-|Text|No default value can be set for this item.|Reference Value:<br>HG|
|7|I/F Name Prefix 3|IF_Name3|conventional prefix of the corresponding I/F name|Yes|-|Text|No default value can be set for this item.|Reference Value:<br>Bundle-Ether|
|8|mtu owner Value 3|IF_Owner_Name3|the corresponding I/F's mtu owner value which is to be injected to the device|Yes|-|Text|No default value can be set for this item.|Reference Value:<br>etherbundle|
|9|Tracking Object Prefix 3|IF_TrackingObject_Name3|the initial of tracking object|Yes|-|Text|No default value can be set for this item.|Reference Value:<br>EB|

**Append lines each time when the patterns to be registered are increased in the future.
**

### conf_internal_link_vlan.conf

The table below shows the detail of items which are managed in this configuration file.

|No.|Item Name|Key|Description|Required?|default Value|Type|in case invalid value is set|Remarks|
|:----|:-----|:----|:-----|:----|:----|:----|:----|:----|
|1|Driver OS‚P|Driver_os1|OS name of the model to which VLAN ID is to be set.|No|-|Text|In some cases, creation of internal link might be failed.|Same format as OS name of conf_driver.conf|

**Append lines each time when devices are added in the future.**

### [Additional Explanation] qos.conf

The table below shows the detail of items which are managed in this configuration file.

|No.|Item Name|Key|Description|Required?|default Value|Type|in case invalid value is set|Remarks|
|:----|:-----|:----|:-----|:----|:----|:----|:----|:----|
|1|Key information of remark menu 1|Remark_menu_key_1|Key information of remark menu 1(strings which input to EM)|Yes|-|Text|-|-|
|2|IPv4 Policy information of remark menu 1|Remark_menu_value_ipv4_1|the string of device setting for ipv4 remark menu|Yes|-|Text|-|If the device doesn't have difference between ipv4 and ipv6 setting, write the value here.|
|3|IPv6 Policy information of remark menu 1|Remark_menu_value_ipv6_1|the string of device setting for ipv6 remark menu|Yes|-|Text|-|Values are required even if there is no configuration differences between IPv4 and IPv6.|
|4|Key information of remark menu 2|Remark_menu_key_2|Key information of remark menu 2(strings which input to EM)|Yes|-|Text|-|-|
|5|IPv4 Policy information of remark menu 2|Remark_menu_value_ipv4_2|the string of device setting for ipv4 remark menu|Yes|-|Text|-|If the device doesn't have difference between ipv4 and ipv6 setting, write the value here.|
|6|IPv6 Policy information of remark menu 2|Remark_menu_value_ipv6_2|the string of device setting for ipv6 remark menu|Yes|-|Text|-|Values are required even if there is no configuration differences between IPv4 and IPv6.|
|7|Key information of eguress queue menu 1|Egress_menu_key_1|Key information of eguress queue menu 1(strings which input to EM)|Yes|-|Text|-|-|
|8|IPv4 Policy information of eguress queue menu 1|Egress_menu_value_ipv4_1|the string of device setting for ipv4 eguress queue menu|Yes|-|Text|-|If the device doesn't have difference between ipv4 and ipv6 setting, write the value here.|
|9|IPv6 Policy information of eguress queue menu 1|Egress_menu_value_ipv6_1|the string of device setting for ipv6 eguress queue menu|Yes|-|Text|-|Values are required even if there is no configuration differences between IPv4 and IPv6.|
|10|Key information of eguress queue menu 2|Egress_menu_key_2|Key information of eguress queue menu 1(strings which input to EM)|Yes|-|Text|-|-|
|11|IPv4 Policy information of eguress queue menu 2|Egress_menu_value_ipv4_2|the string of device setting for ipv4 eguress queue menu|Yes|-|Text|-|If the device doesn't have difference between ipv4 and ipv6 setting, write the value here.|
|12|IPv6 Policy information of eguress queue menu 2|Egress_menu_value_ipv6_2|the string of device setting for ipv6 eguress queue menu|Yes|-|Text|-|Values are required even if there is no configuration differences between IPv4 and IPv6.|

**Append lines each time when the patterns to be registered are increased in the future.
**

### conf_act_threshold.conf 

The table below shows the detail of items which are managed in the configuration file for the disk utilization in the ACT server.

|No.|Item Name                                                                               |Key                                                          |Description                                                                                                                              |Required?|default Value|Type   |in case invalid value is set     |Remarks|
|:--|:---------------------------------------------------------------------------------------|:------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------|:--|:------------|:------|:--------------------------------|:------|
|  1|Threshold for CPU utilization                                                           |Em_os_cpu_use_rate_threshold                                 |Threshold for cpu utilization                                                                                                                  |Yes|100          |Numeral|The default value is set.        |-      |
|  2|Threshold for memory utilization                                                        |Em_os_memory_usage_threshold                                 |Threshold for memory utilization                                                                                                               |Yes|4194304      |Numeral|The default value is set.        |-      |
|  3|Threshold for disk utilization                                                          |Mount point of the file system which is monitoring target of the server status|Threshold for disk utilization                                                                                                |Yes|4194304      |Numeral|The default value is set.        |-      |
|  4|Threshold for the Controller-CPU utilization                                            |Em_controller_cpu_use_rate_threshold                         |Threshold for the Controller-CPU utilization                                                                                                   |Yes|100          |Numeral|The default value is set.        |If this is described in conf_stanby.conf, it will be ignored.|
|  5|Threshold for the Controller-memory utilization                                         |Em_controller_memory_usage_threshold                         |Threshold for the Controller-memory utilization                                                                                                |Yes|4194304      |Numeral|The default value is set.        |If this is described in conf_stanby.conf, it will be ignored.|

#### Example description of the disk configuration (No.3)
> /dev=1000000<br>
> /sys/fs/cgroup=500000

### conf_sby_threshold.conf 

The table below shows the detail of items which are managed in the configuration file for the disk utilization in the SBY server.

|No.|Item Name                                                                               |Key                                                          |Description                                                                                                                              |Required?|default Value|Type   |in case invalid value is set     |Remarks|
|:--|:---------------------------------------------------------------------------------------|:------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------|:--|:------------|:------|:--------------------------------|:------|
|  1|Threshold for CPU utilization                                                           |Em_os_cpu_use_rate_threshold                                 |Threshold for cpu utilization                                                                                                                  |Yes|100          |Numeral|The default value is set.        |-      |
|  2|Threshold for memory utilization                                                        |Em_os_memory_usage_threshold                                 |Threshold for memory utilization                                                                                                               |Yes|4194304      |Numeral|The default value is set.        |-      |
|  3|Threshold for disk utilization                                                          |Mount point of the file system which is monitoring target of the server status|Threshold for disk utilization                                                                                                |Yes|4194304      |Numeral|The default value is set.        |-      |

#### Example description of the disk configuration (No.3)
> /dev=1000000<br>
> /sys/fs/cgroup=500000

### conf_asr_device_\<Device Name\>.conf 

The table below shows the detail of items which are managed in the configuration file for ASR device. This configuration file is described in XML.

|No.|Type      |Element count|Parameters1       |Parameters2     |Parameters3     |Outline                               |Description                                            |Example      |
|:--|:---------|:------------|:-----------------|:---------------|:---------------|:-------------------------------------|:------------------------------------------------------|:------------|
|  1|container |1            |registration-info |                |                |Registration information              |Registration information                               |-            |
|  2|container |1            |                  |device          |                |Device information                    |Device information                                     |-            |
|  3|string    |1            |                  |                |host-name       |host name (device)                    |Device Name (ASR)                                      |stm1spunirt01|
|  4|string    |0..1         |                  |                |delete-flag     |device delete flag                    |Device delete flag. Set it only when you want to delete a device. If there is no target device, neither deletion processing nor update processing is performed.|-|
|  5|string    |1            |                  |                |address         |device IP address                     |The IP address of the device used to connect the device.|192.168.10.1|
|  6|string    |1            |                  |                |platform-name   |platform name of the target device    |The same platform name as the key of the ASR driver described in conf_driver.conf|ASR1002-X|
|  7|string    |1            |                  |                |os-name         |OS of the target device               |The same OS name as the key of the ASR driver described in conf_driver.conf|IOS|
|  8|string    |1            |                  |                |firm-version    |firmware version of the target device |The same firmware version as the key of the ASR driver described in conf_driver.conf|Version15.3|
|  9|string    |1            |                  |                |username        |Device login user name                |The user name of the device used to connect the device.|username|
| 10|string    |1            |                  |                |password        |Device login password                 |The password of the device used to connect the device. |password|


### conf_nvr_device_\<Device Name\>.conf 

The table below shows the detail of items which are managed in the configuration file for NVR device. This configuration file is described in XML.

|No.|Type      |Element count|Parameters1       |Parameters2     |Parameters3     |Outline                               |Description                                            |Example      |
|:--|:---------|:------------|:-----------------|:---------------|:---------------|:-------------------------------------|:------------------------------------------------------|:------------|
|  1|container |1            |registration-info |                |                |Registration information              |Registration information                               |-            |
|  2|container |1            |                  |device          |                |Device information                    |Device information                                     |-            |
|  3|string    |1            |                  |                |host-name       |host name (device)                    |Device Name (NVR)                                      |stm1spuni0101|
|  4|string    |0..1         |                  |                |delete-flag     |device delete flag                    |Device delete flag. Set it only when you want to delete a device. If there is no target device, neither deletion processing nor update processing is performed.|-|
|  5|string    |1            |                  |                |address         |device IP address                     |The IP address of the device used to connect the device.|192.168.10.2|
|  6|string    |1            |                  |                |platform-name   |platform name of the target device    |The same platform name as the key of the NVR driver described in conf_driver.conf|NVR510|
|  7|string    |1            |                  |                |os-name         |OS of the target device               |The same OS name as the key of the NVR driver described in conf_driver.conf|Rev.|
|  8|string    |1            |                  |                |firm-version    |firmware version of the target device |The same firmware version as the key of the NVR driver described in conf_driver.conf|15.01.02|
|  9|string    |1            |                  |                |username        |Device login user name                |The user name of the device used to connect the device.|username|
| 10|string    |1            |                  |                |password        |Device login password                 |The password of the device used to connect the device. |password|
| 11|string    |1            |                  |                |administrator-password|Administrator password          |Password used to switch to privileged mode (administrator) |admin_password|


### conf_\<Driver Name\>_audit_exclusion.conf 

The table below shows the detail of items which are managed in this configuration file.

|No.|Item Name|Key|Description|Required?|default Value|Type|in case invalid value is set|Remarks|
|:----|:-----|:----|:-----|:----|:----|:----|:----|:----|
|1|Platform Name 1|Platform_name|platform name of the target device|Yes|-|Text|Configuration exclusion is not done|-|
|2|Driver OS 1|Driver_os|OS of the target device|Yes|-|Text|Ditto.|-|
|3|Firmware Version 1|Firmware_ver|firmware version of the target device|Yes|-|Text|Ditto.|-|
|4|Exclusion config 1|Exclusion_config1|The lines  where the  specified configuration file are described  are regarded as "Blank". Since both of two compared configuration files are regarded as "Blank", the difference will not be detected.|Yes|-|Text|Ditto.|-|

**Append lines each time when exclusion config (Exclusion_config) are added.**

