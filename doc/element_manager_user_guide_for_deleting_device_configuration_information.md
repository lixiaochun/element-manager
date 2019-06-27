# Element Manager User Guide for Deleting Device Configuration Information.

** Version 1.0 **
** June 27, 2019 **
** Copyright(c) 2019 Nippon Telegraph and Telephone Corporation**

This text describes how to use the tool for deleting the device configuration information record stored in EM's DB.

## 1. Device configuration information record deletion tool
---

This tool runs periodically by cron and should only be run if you need to do it manually.<br>
The device configuration information record deletion tool can be executed with the following command on the DB server.<br>
However, if the data size (bytes) of the device configuration information table is less than or equal to the threshold (TABLE_SIZE_LIMIT, set in the shell), the record is not deleted.<br>
(DB record deletion will not be executed even if the following command is executed.)
~~~console
# /root/em_config_delete/delete_deviceconfigurationinfo_record.sh [Enter]
~~~
