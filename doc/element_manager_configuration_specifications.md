## Element Manager Configuration Specifications

**Version 1.0**
**December 7, 2018**
**Copyright(c) 2018 Nippon Telegraph and Telephone Corporation**

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

### conf_if_process.conf

The table below shows the detail of items which are managed in this configuration file.

|No.|Item Name|Key|Description|Required?|default Value|Type|in case invalid value is set|Remarks|
|:----|:-----|:----|:-----|:----|:----|:----|:----|:----|
|1|Netconf Server Address|Netconf_server_address|I/F Process Part Definition: Netconf Server Address|Yes|0.0.0.0|Text|Process cannot be started.|-|
|2|Port Number|Port_number|I/F Process Part Definition: Port Number|Yes|8080|Numeral|Process cannot be started.|-|
|3|Account Name|Account|Set the certificate account name which is used in the I/F Process Part.|Yes|-|Text|SSH connection from EC cannot be established.|-|
|4|Password|Password|Set the certificate password which is used in the I/F Process Part.|Yes|-|Text|SSH connection from EC cannot be established.|-|
|5|Capability Information 1|Capability1|Capability information 1 of HELLO to be sent to EC|Yes|-|Text|Capability exchange of HELLO cannot be performed.|-|
|6|Capability Information 2|Capability2|Capability information 2 of HELLO to be sent to EC|Yes|-|Text|Ditto.|-|

**Append lines each time when Capability Information is added in the future.**

### conf_if_process_rest.conf

The table below shows the detail of items which are managed in this configuration file.

|No.|Item Name|Key|Description|Required?|default Value|Type|in case invalid value is set|Remarks|
|:----|:-----|:----|:-----|:----|:----|:----|:----|:----|
|1|REST Server Address|Rest_server_address|I/F Process Part Definition: REST Server Address|Yes|0.0.0.0|Text|Process cannot be started.|-|
|2|Port Number|Port_number|I/F Process Part Definition: Port Number|Yes|8080|Numeral|Process cannot be started.|-|
|3|Controller Status Acquisition Shell Script Path|Statusget_shell_file_path|I/F Process Part Definition: Path for Controller Status Acquisition Shell Script|Yes|'../bin/controller_status.sh|Text|Process for acquiring controller status fails|-|

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

|No.|Item Name|Key|Description|Required?|default Value|Type|in case invalid value is set|Remarks|
|:----|:-----|:----|:-----|:----|:----|:----|:----|:----|
|1|DB Server Address|DB_server_address|DB server address|Yes|0.0.0.0|Text|-|-|
|2|DB Access Port Number|DB_access_port|DB access port number|Yes|5432|Numeral|-|-|
|3|DB Access User Name|DB_user|DB access user name|Yes|-|Text|-|-|
|4|DB Access Password|DB_access_pass|DB access password|Yes|-|Text|-|-|
|5|DB Access Table|DB_access_table|DB access table|Yes|-|Text|-|-|
|6|Timer Value: confirmed-commit Configuration Time (ms)|Timer_confirmed-commit|the timer value (ms) set in confirmed-commit|Yes|30000|Numeral|-|-|
|7|Timer Value: confirmed-commit EM Internal Adjustment Time (ms)|Timer_confirmed-commit_em_offset|EM internal adjustment value (ms) for confirmed-commit<br>Both positive and negative vales are allowed.|Yes|0|Numeral|-|The sum of this value and that of Timer_confirmed-commit is set to the timer.|
|8|Timer Value: Netconf Protocol Timer Configuration Time (ms)|Timer_netconf_protocol|NETCONF protocol timer value (ms)|Yes|60000|Numeral|The default value is set.|-|
|9|Timer Value: CLI Protocol Timer Configuration Time (ms)|Timer_cli_protocol|CLI protocol timer value (ms)|Yes|60000|Numeral|The default value is set.|-|
|10|Timer Value: Signal Reception Waiting Timer Configuration Time (ms)|Timer_signal_rcv_wait|signal reception waiting timer value (ms)|Yes|1000|Numeral|The default value is set.|-|
|11|Timer Value: Thread Stop Monitoring Timer Configuration Time (ms)|Timer_thread_stop_watch|thread stop monitoring timer value (ms)|Yes|200|Numeral|The default value is set.|-|
|12|Timer Value: Transaction End Monitoring Timer Configuration Time (ms)|Timer_transaction_stop_watch|transaction end monitoring timer value (ms)|Yes|200|Numeral|The default value is set.|-|
|13|Timer Value: Transaction DB Monitoring Timer Configuration Time (ms)|Timer_transaction_db_watch|transaction DB monitoring timer value (ms)|Yes|100|Numeral|The default value is set.|-|
|14|Timer Value: Connection Retry Time (ms)|Timer_connection_retry|connection retry timer value (ms)|Yes|5000|Numeral|The default value is set.|-|
|15|The Number of Connection Retries|Connection_retry_num|the number of connection retries|Yes|5|Numeral|The default value is set.|-|
|16|Log File|Em_log_file_path|Specify the log file path of EM.|Yes|-|Text|Log cannot be saved correctly.|-|
|17|Log Level|Em_log_level|Specify the log level of EM|Yes|DEBUG|Text|-|-|
|18|IP Address of EM's REST Server|Em_Rest_server_address|Specify the IP address of EM's REST server|Yes|0.0.0.0|Text|-|-|
|19|Port Number of EM's REST Server|Em_port_number|Specify the port number of EM's REST server|Yes|8080|Text|-|-|
|20|The Number of REST Requests Average Time|Rest_request_average|The unit time (sec) for calculating the number of REST requests|Yes|3600|Numeral|The default value is set.||
|21|IP Address of EM's Management I/F|Controller_management_address|Specify the IP address of EM's management I/F|Yes|0.0.0.0|Text|-|-|
|22|IP Address of EC's REST Server|Ec_rest_server_address|Specify the IP address of EC's REST server|Yes|0.0.0.0|Text|-|-|
|23|Port Number of EC's REST Server|Ec_port_number|Specify the port number of EC's REST server|Yes|18080|Numeral|-|-|
|24|The Number of REST Notification Retries|Ec_rest_retry_num|Specify the number of REST notification retries|Yes|1|Numeral|-|-|
|25|Interval of REST Notification Retry|Ec_rest_retry_interval|Specify the time interval of REST notification retry|Yes|1|Numeral|-|-|

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
