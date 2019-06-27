#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmCgwshDeviceUtilityDB.py
'''
Device utility for CGW-SH(DB)
'''
import os
import GlobalModule
import re
import json
from EmCommonLog import decorater_log
from CgwshDeviceConfigManagement import CgwshDeviceConfigManagement


class EmCgwshDeviceUtilityDB(object):
    '''
    Device utility for CGW-SH(DB)
    '''

    _db_delete = "DELETE"
    _platform_name_asr = "ASR1002-X"
    _platform_name_nvr = "NVR510"
    _platform_name_conf_asr = "asr"
    _platform_name_conf_nvr = "nvr"
    _log_type_running = "running_config"
    _log_type_startup = "startup_config"

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''
        self._re_file = re.compile("^conf_(asr|nvr)_device_.*\.conf$")

    @decorater_log
    def write_show_config_info(self,
                               device_name,
                               working_date,
                               working_time,
                               ec_message,
                               config_data,
                               is_before):
        '''
        Device config set as argument is saved in DB.
        Argument:
            device_name: device name (str)
            working_date: working date (YYYYmmDD) (str)
            working_time: working time (HHMMSS) (str)
            ec_message: EC message (str)
            config_data: advanced config (str)
            is_before: advanced config? (if yes, true) (boolean)
        Return value:
            result (boolean)
        '''
        json_ec_mes = json.loads(ec_message).get("device", {})
        practice_system = json_ec_mes.get("type")
        if practice_system:
            platform_name = self._platform_name_asr
        else:
            platform_name = self._platform_name_nvr
        svs_info = json_ec_mes["serviceInfo"]
        vrf_name = svs_info.get("uni", {}).get("vrfName")
        get_timing = 1 if is_before else 2
        write_conf_datas = self._parse_config_data(config_data,
                                                   platform_name,
                                                   is_before)
        db_method = []
        db_param = []
        for item in write_conf_datas:
            tmp_db_method, tmp_db_param = self._gen_config_info(
                device_name=device_name,
                working_date=working_date,
                working_time=working_time,
                platform_name=platform_name,
                vrf_name=vrf_name,
                practice_system=practice_system,
                log_type=item[0],
                get_timing=get_timing,
                config_file=item[1],
            )
            db_method.extend(tmp_db_method)
            db_param.extend(tmp_db_param)
        is_result = GlobalModule.DB_CONTROL.write_simultaneous_table(db_method,
                                                                     db_param)
        return is_result

    @decorater_log
    def merge_cgwsh_device_from_config_file(self, conf_dir_path):
        '''
        Device for CGWSH is registered in DB as Config in directory set as argument.
        Argument:
            conf_dir_path : directory path of registered device (str)
        Return value:
            result (boolean)
        '''
        tmp_dir_path = os.path.join(GlobalModule.EM_LIB_PATH, conf_dir_path)
        file_list = self._get_all_device_info_files(tmp_dir_path)
        db_method = []
        db_param = []
        for file_path in file_list:
            tmp_db_method, tmp_db_param = self._gen_sql_parameter(file_path)
            db_method.extend(tmp_db_method)
            db_param.extend(tmp_db_param)
        is_result = GlobalModule.DB_CONTROL.write_simultaneous_table(db_method,
                                                                     db_param)
        return is_result

    @decorater_log
    def parse_config_data_for_public(self,
                                     config_data,
                                     platform_name=None):
        '''
        Device config is conveted to information which can be stored in DB.
        (It is public method to external.)
        Argument:
            config_data : acquired config (str)
            platform_name : platform name (list)
        Return value:
            tuple of adjusted device config (tuple(str))
            (ASR is running => startup)
        '''
        tmp_conf_datas = []
        if platform_name == self._platform_name_asr:
            run_log, start_log = self._get_asr_log(config_data)
            tmp_conf_datas.append(run_log)
            tmp_conf_datas.append(start_log)
        else:
            tmp_log = self._get_nvr_log(config_data)
            tmp_conf_datas.append(tmp_log)
        return tuple(tmp_conf_datas)

    @decorater_log
    def _get_all_device_info_files(self, dir_path):
        '''
        Only device registration information file in directory path is acquired as a list.
        Argument:
            dir_path : directory path of registered device (str)
        Return value:
            path list for files (list)
        '''
        file_list = os.listdir(dir_path)
        dev_file_list = []
        for file_path in file_list:
            if self._re_file.search(file_path):
                dev_file_list.append(os.path.join(dir_path, file_path))
        return dev_file_list

    @decorater_log
    def _parse_config_data(self,
                           config_data,
                           platform_name,
                           is_before):
        '''
        Config data is analyzed.
        Argument:
            config_data : acquired config (str)
            platform_name : platform name (list)
            is_before : Advanced config?  (If yes, true) (boolean)
        Return value:
            list of adjusted device config (list)
        '''
        tmp_conf_datas = []
        if platform_name == self._platform_name_asr:
            if is_before:
                tmp_log_timing = "before"
            else:
                tmp_log_timing = "after"
            run_log, start_log = self._get_asr_log(config_data)
            tmp_log_type = "%s_%s" % (tmp_log_timing, self._log_type_running)
            tmp_conf_datas.append((tmp_log_type, run_log))
            tmp_log_type = "%s_%s" % (tmp_log_timing, self._log_type_startup)
            tmp_conf_datas.append((tmp_log_type, start_log))
        else:
            tmp_log = self._get_nvr_log(config_data)
            tmp_conf_datas.append((None, tmp_log))
        return tmp_conf_datas

    @decorater_log
    def _search_show_parts(self, get_log, start_str, end_str, driver=None):
        '''
        Execution result of show command is detected.
        Argument:
            get_log : device information log to be acquired (str)
            start_str : start command(show running-config, etc)
            end_str : termination command(show startup-config, etc)
            driver : self._platform_name_asr or self._platform_name_nvr
        Return value:
            str1 : string of result including start_str(show running-config - )
            str2 : string including end_str and subsequent string(show startup-config -)
        '''
        tmp1 = get_log.partition(start_str)
        tmp0 = tmp1[0].rpartition("\n")[2]
        tmp2 = tmp0 + tmp1[1] + tmp1[2]
        if driver == self._platform_name_nvr:
            tmp3 = tmp2.partition(tmp0 + end_str)
        else:
            tmp3 = tmp2.partition(tmp0 + end_str)
            tmp3 = (tmp3[0], tmp3[1], tmp3[2].rpartition(tmp0)[0])
        show_result = tmp3[0]
        after_log = tmp3[1] + tmp3[2]
        return show_result, after_log

    @decorater_log
    def _get_asr_log(self, config_data):
        '''
        ASR config data is acquired.
        Argument:
            config_data : acquired config (str)
        Return value:
            ASR running-config (str)
            ASR startup-config (str)
        '''
        tmp_running_conf, tmp_startup_conf = self._search_show_parts(
            config_data,
            "show running-config",
            "show startup-config",
            self._platform_name_asr)
        return tmp_running_conf, tmp_startup_conf

    @decorater_log
    def _get_nvr_log(self, config_data):
        '''
        NVR config data is acquired.
        Argument:
            config_data : acquired NVR config data (str)
        Return value:
            NVR config (str)
        '''
        tmp_conf = self._search_show_parts(
            config_data,
            "show config",
            "console columns 80",
            self._platform_name_nvr)
        return tmp_conf[0]

    @decorater_log
    def _gen_sql_parameter(self, file_path):
        '''
        Paramter list for SQL method is acquired.
        Argument:
            file_path : path of file in which device is registered.
        Return value:
            method list (list)
            parameter list (list)
        '''
        file_name = os.path.basename(file_path)
        device_platform = self._re_file.search(file_name).groups()[0]
        tmp_conf = CgwshDeviceConfigManagement(file_path)
        tmp_conf.load_config()
        conf_data = tmp_conf.get_config()
        if (device_platform == self._platform_name_conf_nvr and
                conf_data.get("administrator-password") is None):
            raise ValueError(
                "administrator-password is not found. (NVR device)")

        db_method = []
        db_param = []
        dev_name = conf_data.get("host-name")
        is_delete = conf_data.get("delete-flag")
        tmp_db_funcs = []
        if is_delete:
            tmp_db_funcs.append(
                self._gen_config_info(is_delete=is_delete,
                                      device_name=dev_name))
            tmp_db_funcs.append(
                self._gen_admin_pass_info(is_delete=is_delete,
                                          device_name=dev_name)
            )
            tmp_db_funcs.append(
                self._gen_dev_reg_info(is_delete=is_delete,
                                       device_name=dev_name)
            )
        else:
            tmp_db_funcs.append(
                self._gen_dev_reg_info(
                    is_delete=is_delete,
                    device_name=dev_name,
                    platform_name=conf_data.get("platform-name"),
                    os_name=conf_data.get("os-name"),
                    firm_version=conf_data.get("firm-version"),
                    username=conf_data.get("username"),
                    password=conf_data.get("password"),
                    mgmt_if_address=conf_data.get("address"))
            )
            if conf_data.get("administrator-password"):
                tmp_db_funcs.append(
                    self._gen_admin_pass_info(
                        is_delete=is_delete,
                        device_name=dev_name,
                        admin_pass=conf_data.get("administrator-password"))
                )
        for item in tmp_db_funcs:
            db_method.extend(item[0])
            db_param.extend(item[1])
        return db_method, db_param

    @decorater_log
    def _gen_dev_reg_info(self,
                          is_delete=False,
                          device_name=None,
                          platform_name=None,
                          os_name=None,
                          firm_version=None,
                          username=None,
                          password=None,
                          mgmt_if_address=None):
        '''
        Write-method parameter is acquired in order to write into device registration information table.
        Argument:
            is_delete : Is it delete process? (if it is deletion, true) (boolean)
c
        Return value:
            method list (list)
            parameter list (list)
        '''
        db_func = [GlobalModule.DB_CONTROL.write_device_regist_info]
        regist_param = {}
        regist_param["device_name"] = device_name
        if is_delete:
            regist_param["db_control"] = self._db_delete
        else:
            regist_param["db_control"] = None
            regist_param["platform_name"] = platform_name
            regist_param["os"] = os_name
            regist_param["firm_version"] = firm_version
            regist_param["username"] = username
            regist_param["password"] = password
            regist_param["mgmt_if_address"] = mgmt_if_address
            regist_param["device_type"] = 0
            regist_param["mgmt_if_prefix"] = 0
            regist_param["loopback_if_address"] = "fvw_parameter"
            regist_param["loopback_if_prefix"] = 0
            regist_param["snmp_server_address"] = "fvw_parameter"
            regist_param["snmp_community"] = "fvw_parameter"
            regist_param["ntp_server_address"] = "fvw_parameter"
        return_regist_param = [regist_param]
        return db_func, return_regist_param

    @decorater_log
    def _gen_admin_pass_info(self,
                             is_delete=False,
                             device_name=None,
                             admin_pass=None):
        '''
        Write-method parameter is acquired in order to write into NWR privilege password table.
        Argument:
            is_delete : Is it delete process? (if it is deletion, true) (boolean)
            
            device_name subsequent string : argument of write-method 
                                            into device registration information table (str)
        Return value:
            method list (list)
            parameter list (list)
        '''
        db_func = [
            GlobalModule.DB_CONTROL.write_nvr_administrator_password_info]
        regist_param = {}
        regist_param["device_name"] = device_name
        if is_delete:
            regist_param["db_control"] = self._db_delete
        else:
            regist_param["db_control"] = None
            regist_param["administrator_password"] = admin_pass
        return_regist_param = [regist_param]
        return db_func, return_regist_param

    @decorater_log
    def _gen_config_info(self,
                         is_delete=False,
                         device_name=None,
                         working_date=None,
                         working_time=None,
                         platform_name=None,
                         vrf_name=None,
                         practice_system=None,
                         log_type=None,
                         get_timing=None,
                         config_file=None,
                         ):
        '''
        Write-method parameter is acquired in order to write into device config information table.
        Argument:
            is_delete : Is it delete process? (if it is deletion, true) (boolean)
            device_name subsequent string  : argument of write-method 
                                             into device registration information table.
                                (str (int in case of only get_timing))
        Return value:
            method list (list)
            parameter list (list)
        '''
        db_func = [GlobalModule.DB_CONTROL.write_device_configration_info]
        regist_param = {}
        regist_param["device_name"] = device_name
        if is_delete:
            regist_param["db_control"] = self._db_delete
        else:
            regist_param["db_control"] = None
            regist_param["working_date"] = working_date
            regist_param["working_time"] = working_time
            regist_param["platform_name"] = platform_name
            regist_param["vrf_name"] = vrf_name
            regist_param["practice_system"] = practice_system
            regist_param["log_type"] = log_type
            regist_param["get_timing"] = get_timing
            regist_param["config_file"] = config_file
        return_regist_param = [regist_param]
        return db_func, return_regist_param
