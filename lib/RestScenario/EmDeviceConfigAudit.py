#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmDeviceConfigAudit.py
'''
Module for host Config-Audit 
'''
import re
import socket
import traceback
import datetime
from flask import jsonify
import EmSeparateRestScenario
import GlobalModule
from EmCommonLog import decorater_log, decorater_log_in_out
from EmCommonDriver import EmCommonDriver


class EmDeviceConfigAudit(EmSeparateRestScenario.EmRestScenario):
    '''
    Class for host Config-Audit 
    '''

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmDeviceConfigAudit, self).__init__()
        self.scenario_name = "EmDeviceConfigAudit"
        self.error_code_top = "03"
        self._error_code_list = {"030101": 404,
                                 "030301": 500,
                                 "030302": 500,
                                 "030303": 500,
                                 "030399": 500, }
        self.hostname = None
        self.latest_date = None
        self.em_host = None
        self.latest_config = None
        self.now_date = None
        self.now_device_info = None
        self.diff = None

    @decorater_log
    def _scenario_main(self, *args, **kwargs):
        '''
        Scenario processing
        Host Config-Audit is executed.
        Argument:
            *args, **kwargs : variable argument, variable keyword argument(list,dict)
                              (hostname(str) is in kwarg.)
        Return value:
            response object
        '''
        GlobalModule.EM_LOGGER.debug(
            "start config-audit: args=%s ,kwargs=%s" % (args, kwargs))
        hostname = kwargs.get("hostname")
        try:
            self._execute_config_audit(hostname)
            response = self._gen_response()
        except Exception:
            GlobalModule.EM_LOGGER.debug(
                "Trace Back:%s" % (traceback.format_exc(),))
            raise
        return response

    @decorater_log
    def _gen_response(self):
        '''
        Response is generated.
        Argument:
            None
        Return value:
            response object
        '''

        tmp_json = self._gen_response_json()
        response = jsonify(tmp_json)
        response.headers["Content-Type"] = "application/json"
        response.status_code = 200
        return response

    @decorater_log
    def _gen_response_json(self):
        '''
        Json for response is generated.
        Argument:
            None
        Return value:
            json  for response ; dict
        '''
        response_json = {}
        response_json["hostname"] = self.hostname
        if self.latest_date and self.latest_config:
            latest_em_config = {
                "date": self.latest_date,
                "server_name": self.em_host,
                "config": self._correct_response_data(self.latest_config),
            }
            response_json["latest_em_config"] = latest_em_config
        ne_config = {
            "date": self.now_date,
            "config": self._correct_response_data(self.now_device_info),
        }
        response_json["ne_config"] = ne_config
        tmp_diff_data = {
            "diff_data_unified": self._correct_response_data(self.diff),
        }
        response_json["diff"] = tmp_diff_data
        return response_json

    @decorater_log
    def _correct_response_data(self, res_content):
        '''
        Response data is adjusted.
        Argument:
            res_content : response data(one of each contents) (str)
        Return value:
            adjusted response data : str
        '''
        return_str = res_content
        return_str = re.sub("\r\n|\r", "\n", return_str)
        return_str = re.sub("\b", "", return_str)
        return return_str

    @decorater_log_in_out
    def _execute_config_audit(self, hostname):
        '''
        Config-Audit for each host is executed.
        Argument:
            hostname : host name (str)
        Return value:
            None
        '''
        self.hostname = hostname
        self.em_host = socket.gethostname()
        device_driver = self._set_driver(hostname)

        try:
            conn_result = device_driver.connect_device(hostname)
            if conn_result != GlobalModule.COM_CONNECT_OK:
                raise _NeConfigError(
                    _NeConfigError.err_txt("Failed to connect device."))

            self._get_now_config(hostname, device_driver)
            self._execute_compare(hostname, device_driver)
        except Exception:
            raise
        finally:
            device_driver.disconnect_device(hostname, get_config_flag=False)

        return

    @decorater_log
    def _set_driver(self, hostname):
        '''
        Driver is connected with each host.
        Argument:
            hostname : host name (str)
        Return value:
            driver common instance
        '''
        is_ok, data = (
            GlobalModule.EMSYSCOMUTILDB.read_separate_driver_info(hostname))
        if not is_ok or not data:
            raise _NotExistDeviceError(
                _NotExistDeviceError.err_txt("Device does not exist."))

        device_driver = EmCommonDriver()

        is_ok = device_driver.start(hostname)

        if not is_ok:
            raise IOError("Failed to start the driver.")

        return device_driver

    @decorater_log
    def _get_now_config(self, hostname=None, device_driver=None):
        '''
        Host configuration is acquired.
        Argument:
            hostname : host name (str)
            device_driver : driver object
        Return value:
            None
        '''
        is_ok, now_device_info = device_driver.get_device_setting(hostname)
        if not is_ok:
            raise _NeConfigError(
                _NeConfigError.err_txt("Failed to get device config."))
        self.now_device_info = now_device_info
        self.now_date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    @decorater_log
    def _execute_compare(self, hostname=None, device_driver=None):
        '''
        Hosts are compared.
        Argument:
            hostname : host name (str)
            device_driver : driver object
        Return value:
            None
        '''
        mtd_result = (
            device_driver.execute_driver_method(
                "compare_to_latest_device_configuration",
                device_name=hostname,
                device_config=self.now_device_info,
            ))
        if not mtd_result:
            raise Exception(
                "Failed to run compare_to_latest_device_configuration")
        is_result = mtd_result[0]
        diff_data = mtd_result[1]
        latest_config = mtd_result[2]
        latest_date = mtd_result[3]
        if is_result == GlobalModule.COM_AUDIT_DB_INFO_NG:
            raise _LatestDbConfigError(
                _LatestDbConfigError.err_txt("Failed to config compare."))
        elif is_result == GlobalModule.COM_AUDIT_AUDIT_NG:
            raise _AuditConfigError(
                _AuditConfigError.err_txt("Failed to config compare."))

        self.latest_date = latest_date
        self.latest_config = latest_config
        self.diff = diff_data


class _BaseAuditScenarioError(Exception):
    '''
    Error process is executed in this scenario.
    '''
    err_fmt = EmSeparateRestScenario.EmRestScenario._error_text
    ErrorCode = "030399"

    @classmethod
    def err_txt(cls, message=""):
        '''
        Error code is set. Error message is generated  based on error message format.
        4XX error message can be generated.
        '''
        return cls.err_fmt % (cls.ErrorCode, message)


class _NotExistDeviceError(_BaseAuditScenarioError):
    '''
    Error has occured when the specified host is not registered.
    '''
    ErrorCode = "030101"


class _LatestDbConfigError(_BaseAuditScenarioError):
    '''
    Error has occurred in EM when newest config information after process execution is acquired.
    '''
    ErrorCode = "030301"


class _NeConfigError(_BaseAuditScenarioError):
    '''
    Error has occured when host-config is acquired.
    '''
    ErrorCode = "030302"


class _AuditConfigError(_BaseAuditScenarioError):
    '''
    Error has occurred when difference information between host config and newest config in EM is acquired.
    '''
    ErrorCode = "030303"
