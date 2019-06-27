#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: AuditConfigManagement.py
import os
from codecs import BOM_UTF8
import glob
import traceback
from EmCommonLog import decorater_log_in_out, decorater_log
import GlobalModule


class AuditConfigManagement(object):

    _SPLITSTR = "="

    @decorater_log_in_out
    def __init__(self, conf_dir="./conf_audit"):
        self.conf_dif_path = os.path.join(GlobalModule.EM_CONF_PATH, conf_dir)
        tmp_path = os.path.join(self.conf_dif_path,
                                "conf_*_audit_exclusion.conf")
        self.conf_file_list = [
            os.path.basename(path) for path in glob.glob(tmp_path)]
        self.conf_data = None

    @decorater_log_in_out
    def get_config(self, platform_name, os_name, firm_version):
        '''
        List for excluding audit comparison is aquired.
        Argument:
            platform_name : platform name str
            os_name : OS name str
            firm_version : firm version str
        Return value:
            list for excluding audit comparison : list
        '''
        return self.conf_data.get((platform_name, os_name, firm_version), [])

    @decorater_log_in_out
    def load_config(self):
        '''
        Information is read from definition file of list for excluding audit comparison.
        '''
        GlobalModule.EM_LOGGER.info(
            '112003 Load conf start ("%s")' % (self.conf_file_list,))
        try:
            tmp_conf_data = {}
            for conf_file in self.conf_file_list:
                GlobalModule.EM_LOGGER.info(
                    '115004 Load conf start ("%s")', conf_file)
                file_path = os.path.join(self.conf_dif_path, conf_file)
                get_config = self._open_conf_file(file_path)
                conf_dict = self._make_conf_dict(get_config)
                key_info = (conf_dict["Platform_name"],
                            conf_dict["Driver_os"],
                            conf_dict["Firmware_ver"],)
                exclusion_info = conf_dict["Exclusion_config"]
                tmp_conf_data[key_info] = exclusion_info
                GlobalModule.EM_LOGGER.debug('load end ("%s")', conf_file)
        except Exception as exc_info:
            GlobalModule.EM_LOGGER.error(
                '315005 Load conf Error ("%s")', conf_file)
            GlobalModule.EM_LOGGER.debug("ERROR:%s" % (exc_info,))
            GlobalModule.EM_LOGGER.debug(
                "Trace Back:%s" % (traceback.format_exc(),))
            raise IOError("Failed to load config")
        self.conf_data = tmp_conf_data
        GlobalModule.EM_LOGGER.debug('load end config = %s', self.conf_data)

    @decorater_log
    def _open_conf_file(self, file_path):
        '''
        Conf fire is read. Each line is returned as KeyValue dictionary.
        It is called at the beginning of each process for definition acquisition.
        Argument:
            file_path : file path for definition file to be read
        Return value:
            result (each line is listed as string.) : List
        '''
        with open(file_path, 'r') as fp:
            conf_list = fp.readlines()
        return_list = []
        for value in conf_list:
            if not(value.startswith('#')) and self._SPLITSTR in value:
                tmp_line = value.strip()
                tmp_line = tmp_line.replace(BOM_UTF8, '')
                return_list.append(tmp_line)
        return return_list

    @decorater_log
    def _make_conf_dict(self, conf_list):
        '''
        Definition dictionary is created.
        Argument:
            conf_list : string list acquired from file
        Return value:
            Definition dictionary : Dict
        '''
        conf_dict = {}  
        capability_list = []
        index = 0
        while index < len(conf_list):
            tmp_key_value = conf_list[index].split(self._SPLITSTR)
            if len(tmp_key_value) == 2:
                if tmp_key_value[0].find("Exclusion_config") == 0:
                    capability_list.append(tmp_key_value[1])
                else:
                    conf_dict[tmp_key_value[0]] = tmp_key_value[1]
            index += 1
        conf_dict["Exclusion_config"] = capability_list
        return conf_dict
