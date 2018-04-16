# Element Manager User Guide for Startup/Stop

** Version 2.0 **
** April 12, 2018 **
** Copyright(c) 2018 Nippon Telegraph and Telephone Corporation**

This text describes how to Startup/Stop Element Manager.

## 1. Startup
---

When starting up from RA by Pacemaker, or in the case of non-redundancy configuration, execute the following command to start up EM.
~~~console
# ${EM_HOME}/bin/em_ctl.sh start [Enter]
~~~
\* When using this command, assume that virtual IP is assigned to the target server.
In a redundant configuration, virtual IP is automatically assigned by Pacemaker.

Virtual IP confirmation
~~~console
# ip addr show dev <device name> [Enter]
~~~

Virtual IP configuration
~~~console
# ip addr add <virtual IP address>/<netmask> dev <device name> [Enter]
~~~

## 2. Stop
---

In the case of EM non-redundancy configuration, execute the following command to stop EM.
~~~console
# ${EM_HOME}/bin/em_ctl.sh stop [Enter]
~~~

When stopping from RA by Pacemaker, execute the following command to stop EM.
~~~console
# ${EM_HOME}/bin/em_ctl.sh stop changeover [Enter]
~~~
\* In the case of non-redundancy configuration, if the standby-server is online, execute system switchover.

## 3. Forced stop
---

Forced stop of EM can be done to active-server. Execute the following command to forced stop EM.
~~~console
# ${EM_HOME}/bin/em_ctl.sh forcestop [Enter]
~~~
\* In the case of non-redundancy configuration, if the standby-server is online, execute system switchover.

## 4. Status confirmation
---

When confirming from RA by Pacemaker, or in the case of non-redundancy configuration, execute the following command to confirm EM.
~~~console
# ${EM_HOME}/bin/em_ctl.sh status [Enter]
~~~
