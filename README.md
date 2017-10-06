# Element Manager(EM)

Element Manager(EM) is one of the software components of Multi-Service Fabric(MSF).

 EM provides the function to convert abstracted instructions from upper systems (FC, EC) into vendor-specific configurations. Multiple device drivers for Southbound enable to extract suitable configurations. EM also has the function of order flow control that manages the configuration functions to multiple devices with one single transaction, and the roll-back functions in case of error by Netconf technology.

## System Elements

![system_elements_em](doc/img/system_elements_em.png)

- Netconf Server:
  - Interface for EC main Module uses Netconf protocol
- OrderflowControl:
 - makes it possible to handle orders received from EC main module as one transaction. If any transaction fails, it rolls back the setting for each transaction.
 - selects the Scenario to be activated based on the contents of the order.
- Scenario
  - executes a scenario for controlling devices, corresponding the the content of the order.
- Common driver
  - stores the device information (device name, vendor type, management IP address, etc) in EM-Database when you add new switch.
  - specifies vendor type and which separate driver to access based on the information from Scenario.
  - stores all the information received from the EC.
- Driver Common Utility
  - provides interfaces for Separate Drivers to access EM-Database.
- Separate driver
  - provides interfaces for configuration setting to Scenario.
- Netconf Protocol
  - accesses each device with Netconf.

## How to use
- installation
  - [installation manual(English)](doc/Element_Manager_Installation_Manual_en.pdf) (PDF)
  - [configuration specifications(English)](doc/Element_Manager_Configuration_Specifications_en.pdf) (PDF)
  - [installation manual(Japanese)](doc/Element_Manager_Installation_Manual_ja.pdf)   (PDF)
  - [configuration specifications(Japanese)](doc/Element_Manager_Configuration_Specifications_ja.pdf) (PDF)
- Executable file `/em_pyc`
- source code `/EmModule`


## Hardware
The following conditions are the minimum operation environment.

| item | Configuraiton |
| ---- | ---- |
| OS | CentOS 7.2 x86_64 |
| CPU | 2 Core or more |
| memory | 1G or more |
| NIC | 1 port or more |


## License
**Apache 2.0**. See `LICENSE`.

## support
If you have any questions, or find any bug, let us know with GitHub issues, or please contact `msf-contact [at] lab.ntt.co.jp`.

## project
This project is a part of [Multi-Service Fabric](http://github.com/multi-service-fabric/).
