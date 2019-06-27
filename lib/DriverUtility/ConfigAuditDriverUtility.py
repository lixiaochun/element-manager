#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: ConfigAuditDriverUtility.py
'''
Driver Utility(Audit)
'''
import re
import traceback
import EmDifflib
from EmCommonLog import decorater_log, decorater_log_in_out
from AuditConfigManagement import AuditConfigManagement
import GlobalModule


class ConfigAuditDriverUtility(object):
    '''
    Driver Utility(Audit)
    '''

    @decorater_log_in_out
    def __init__(self,
                 from_config=None,
                 from_config_name="",
                 to_config=None,
                 to_config_name="",
                 driver_info=None):
        self.from_config = from_config
        self.from_config_name = from_config_name
        self.to_config = to_config
        self.to_config_name = to_config_name
        self.driver_info = driver_info
        audit_conf = AuditConfigManagement()
        audit_conf.load_config()
        exclusion_list = audit_conf.get_config(*driver_info)
        self.exclusion_re_list = [re.compile(item) for item in exclusion_list]

    @decorater_log_in_out
    def compare_device_configuration(self):
        '''
        Execute device configuration comparison.
        Argument:
            None
        Return value:
            Comparison result : str
        '''
        GlobalModule.EM_LOGGER.info(
            "115001 Start Compare Device Configuration")
        try:
            list_config_1 = self._make_conf_list(self.from_config)
            list_config_2 = self._make_conf_list(self.to_config)

            diff_obj = EmDifflib.unified_diff(list_config_1,
                                              list_config_2,
                                              fromfile=self.from_config_name,
                                              tofile=self.to_config_name,
                                              n=0)
            str_list = []
            for line_str in diff_obj:
                str_list.append(line_str)
        except Exception as exc_info:
            GlobalModule.EM_LOGGER.warning(
                "215002 Compare Device Configuration Error")
            GlobalModule.EM_LOGGER.debug("Error:%s ", exc_info)
            GlobalModule.EM_LOGGER.debug(
                "Traceback:%s ", traceback.format_exc())
            raise
        return_str = "".join(str_list)
        if return_str:
            GlobalModule.EM_LOGGER.info(
                "115003 Difference between Device Configurations")
            GlobalModule.EM_LOGGER.debug("diff = %s", return_str)
        return return_str

    @decorater_log
    def _make_conf_list(self, config_str):
        '''
        Device configuration string list generation after exclusion string application.
        Argument:
            config_str : device configuration str
        Return value:
            device configuration (exclusion string applied, slice by row) : list
        '''
        tmp = config_str.splitlines(True)
        return ["" if self._check_exclusion(line) else line for line in tmp]

    @decorater_log
    def _check_exclusion(self, line_str):
        '''
        Judgment of excluded string.
        Argument:
            line_str : Character string to be judged. str
        Return value:
            result (True : exclusion target, False : other) : boolean
        '''
        result = False
        for re_item in self.exclusion_re_list:
            if re_item.search(line_str):
                result = True
        return result
