#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmPluginCgwshDeviceControl.py
import GlobalModule
from EmCgwshDeviceUtilityDB import EmCgwshDeviceUtilityDB
from EmCommonLog import decorater_log, decorater_log_in_out


@decorater_log_in_out
def run():
    """
    Plugin -is executed.
    Plugin common process for adding  process in initialization  
    """
    plugin_ins = EmPluginCgwshDeviceControl()
    plugin_ins.merge_cgwsh_device()


class EmPluginCgwshDeviceControl(object):
    """
    Plugin for increase/ decrease device for CGW-SH
    """
    @decorater_log
    def __init__(self):
        """
        Plugin class is initialized.
        """
        self.dev_conf_dir = self._get_dev_conf_dir()

    @decorater_log_in_out
    def merge_cgwsh_device(self):
        """
        Device for CGW-SH is increased or decreased.
        """
        util_ins = EmCgwshDeviceUtilityDB()
        is_ok = util_ins.merge_cgwsh_device_from_config_file(self.dev_conf_dir)
        if not is_ok:
            GlobalModule.EM_LOGGER.debug("Failed to merge cgwsh device")
            raise IOError("Failed to update fvw device data to DB")
        GlobalModule.CGWSH_DEV_UTILITY_DB = util_ins

    @decorater_log
    def _get_dev_conf_dir(self):
        """
        Device for CGW-SH is increased or decreased.
        Return value:
            Directory path for CGW-SH device configuration : str
        """
        is_ok, file_dir = (
            GlobalModule.EM_CONFIG.read_sys_common_conf(
                "Cgwsh_device_dir_path"))
        if not is_ok:
            raise IOError("Failed to get Config : Cgwsh_device_dir_path")
        return file_dir
