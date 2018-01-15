#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2017 Nippon Telegraph and Telephone Corporation
# Filename: EmControllerStatusGet.py.
'''
Scenario to obtain controller status
'''
import re
import os
import traceback
import commands
import json
from flask import jsonify
from copy import deepcopy
import EmSeparateRestScenario
import GlobalModule
from EmCommonLog import decorater_log
from MsfEmMain import get_counter_send
from EmRestServer import get_counter_recv
from EmSysCommonUtilityDB import EmSysCommonUtilityDB


class EmControllerStatusGet(EmSeparateRestScenario.EmRestScenario):
    '''
    Class to obtain controller status
    '''

    EM_STATUS_10 = "startready"  
    EM_STATUS_50 = "changeover"  
    EM_STATUS_90 = "stopready"  
    EM_STATUS_100 = "inservice"  
    EM_STATUS_UK = "unknown"    


    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''
        super(EmControllerStatusGet, self).__init__()
        self.scenario_name = "EmControllerStatusGet"
        self.error_code_top = "01"
        self._error_code_list = {"010101": 400,
                                 "010201": 409,
                                 "010303": 500,
                                 "010304": 500,
                                 "010305": 500,
                                 "010399": 500, }
        self._em_lib_path = GlobalModule.EM_LIB_PATH
        self.os_cpu = "os-cpu"
        self.os_mem = "os-mem"
        self.os_disk = "os-disk"
        self.os_trafic = "os-traffic"
        self.ctr_cpu = "ctr-cpu"
        self.ctr_mem = "ctr-mem"
        self.ctr_state = "ctr-state"
        self.ctr_receive_req = "ctr-receive_req"
        self.ctr_send_req = "ctr-send_req"
        self._get_info_list = (self.os_cpu,
                               self.os_mem,
                               self.os_disk,
                               self.os_trafic,
                               self.ctr_cpu,
                               self.ctr_mem,
                               self.ctr_state,
                               self.ctr_receive_req,
                               self.ctr_send_req, )

    @decorater_log
    def _get_url_param(self, request):
        '''
        Obtain URL parameter. 
        '''
        if request is None:
            raise ValueError("Request object is NULL")
        get_info = self._get_url_parameter(request, "get_info", str, True)
        self.url_parameter = {"get_info": get_info, }
        self.get_info = get_info
        return self.url_parameter

    @decorater_log
    def _scenario_main(self, *args, **kwargs):
        '''
        Scenario processing section. 
        Obtain log data.  
        '''
        get_info = self.get_info
        request_count = kwargs.get("request_date_list", ())
        try:
            get_info_list = self._analysis_get_info(get_info)
            os_info = self._exec_shell_controller_status(get_info_list)
            response = self._gen_response(get_info_list,
                                          os_info,
                                          request_count)
        except IOError as ex:
            GlobalModule.EM_LOGGER.debug(
                "Trace Back:%s" % (traceback.format_exc(),))
            raise IOError(
                (self._error_text % ("010305", ex.message)))
        except Exception as ex:
            GlobalModule.EM_LOGGER.debug(
                "Trace Back:%s" % (traceback.format_exc(),))
            raise
        return response

    @decorater_log
    def _gen_response(self,  get_info_list, os_info, request_count):
        '''
        Create response.  
        '''
        tmp_json = self._gen_response_json(
            get_info_list, os_info)
        response = jsonify(tmp_json)
        response.headers["Content-Type"] = "application/json"
        response.status_code = 200
        return response

    @decorater_log
    def _gen_response_json(self, get_info_list, os_info):
        '''
        Create Json for response. 
        '''

        res_json = {}
        tmp_info = {}
        if os_info is not None:
            res_json = deepcopy(os_info)
            tmp_info = res_json["informations"][0]
        is_ok, em_status = GlobalModule.EMSYSCOMUTILDB.read_system_status()
        if not is_ok:
            raise IOError(
                (self._error_text % ("010305", "Cannot get Em Status")))
        is_ok, mgmt_ip = (
            GlobalModule.EM_CONFIG.read_sys_common_conf(
                "Controller_management_address"))
        if not is_ok:
            raise IOError(
                (self._error_text % ("010305", "Cannot read Config Mgmt IP")))

        res_json["status"] = self.__get_status_str(em_status)

        tmp_info["management_ip_address"] = mgmt_ip
        GlobalModule.EM_LOGGER.debug(
            "Make Response Json:%s" % (res_json,))
        return res_json

    @decorater_log
    def _analysis_get_info(self, get_info):
        '''
        Analyze the get_info's URL parameter, decide the items to obtain. 
        '''
        get_info_list = []
        tmp = get_info if get_info else ""
        for param in self._get_info_list:
            match_obj = re.search(param, tmp)
            if match_obj:
                get_info_list.append(param)
        if not get_info_list:
            get_info_list.extend(deepcopy(self._get_info_list))
        return get_info_list

    @decorater_log
    def _set_shell_command_parameter(self, get_info_list):
        '''
        Create command line argument for controller_status, sh. 
        '''
        top_param = 0
        nproc_param = 0
        df_param = 0
        sar_param = 0
        hostname_param = 1
        mypid = os.getpid()
        for item in get_info_list:
            if item in (self.os_cpu,
                        self.os_mem,
                        self.os_disk,
                        self.ctr_cpu,
                        self.ctr_mem):
                top_param = 1
            if item in (self.ctr_cpu,):
                nproc_param = 1
            if item in (self.os_disk,):
                df_param = 1
            if item in (self.os_trafic,):
                sar_param = 1
        command_param = "%s %s %s %s %s %s" % (top_param,
                                               nproc_param,
                                               df_param,
                                               sar_param,
                                               hostname_param,
                                               mypid)

        return command_param

    @decorater_log
    def _exec_shell_controller_status(self, get_info_list):
        '''
        Execute controller_status, sh. 
        '''
        comm_param = self._set_shell_command_parameter(get_info_list)
        isout, shell_file_name = (
            GlobalModule.
            EM_CONFIG.read_if_process_rest_conf(
                "Statusget_shell_file_path"))
        if not isout:
            raise IOError(
                (self._error_text % ("010305", "Cannot read Config")))
        shelL_path = os.path.join(self._em_lib_path, shell_file_name)

        return_value = ""
        command_txt = "%s %s" % (shelL_path, comm_param)
        GlobalModule.EM_LOGGER.debug("exec command:%s" % (command_txt,))
        try:
            shell_result = commands.getstatusoutput(command_txt)
            if shell_result[0] != 0:
                raise
            else:
                return_value = shell_result[1]
                GlobalModule.EM_LOGGER.debug(return_value)

        except Exception as ex:
            GlobalModule.EM_LOGGER.debug("command error:%s" % (ex.message,))
            raise Exception((self._error_text % ("010304", ex.message)))
        json_result = self._analysis_result_shell(return_value, get_info_list)
        return json_result

    @decorater_log
    def _analysis_result_shell(self,
                               shell_result_txt,
                               get_info_list):
        '''
        Store the shell script result.  
        '''
        result_shell = {}
        result_json = json.loads(shell_result_txt)
        result_shell["host_name"] = result_json.get("hostname")
        info_flug = False
        os_flag = False
        tmp_os = {}
        tmp_result_top = result_json.get("top")
        tmp_cpu_id = float(tmp_result_top.get("id"))
        if self.os_mem in get_info_list:
            tmp_os["memory"] = {
                "used": tmp_result_top.get("used"),
                "free": tmp_result_top.get("free"),
                "buff_cache": tmp_result_top.get("buffers"),
                "swpd": tmp_result_top.get("swapused"),
            }
            os_flag = True
        if self.os_cpu in get_info_list:
            tmp_os["cpu"] = {"use_rate": 100.0 - tmp_cpu_id, }
            os_flag = True
        if self.os_disk in get_info_list:
            tmp_list = []
            for tmp_disk in result_json.get("df", ()):
                tmp_data = tmp_disk.split(" ")
                tmp_json_data = {"file_system": tmp_data[0],
                                 "mounted_on":  tmp_data[5],
                                 "size":  tmp_data[1],
                                 "used":  tmp_data[2],
                                 "avail":  tmp_data[3], }
                tmp_list.append(tmp_json_data)
            tmp_os["disk"] = {"devices": tmp_list}
            os_flag = True
        if self.os_trafic in get_info_list:
            tmp_list = []
            for tmp_if in result_json.get("sar", ()):
                tmp_data = tmp_if.split(" ")
                tmp_json_data = {"ifname": tmp_data[1],
                                 "rxpck":  float(tmp_data[2]),
                                 "txpck":  float(tmp_data[3]),
                                 "rxkb":  float(tmp_data[4]),
                                 "txkb":  float(tmp_data[5]), }
                tmp_list.append(tmp_json_data)
            tmp_os["traffic"] = {"interfaces": tmp_list}
            os_flag = True
        if os_flag:
            result_shell["os"] = tmp_os
            info_flug = True

        ctr_flag = False
        tmp_ctl = {}
        tmp_nprco = float(result_json.get("nproc"))
        tmp_cpu_val = None
        if self.ctr_cpu in get_info_list:
            tmp_cpu_ctrl = float(tmp_result_top.get("cpu"))
            tmp_cpu_val = tmp_cpu_ctrl / tmp_nprco
            tmp_ctl["cpu"] = tmp_cpu_val
            ctr_flag = True
        if self.ctr_mem in get_info_list:
            tmp_ctl["memory"] = tmp_result_top.get("res")
            ctr_flag = True
        if self.ctr_receive_req in get_info_list:
            tmp_ctl["receive_rest_request"] = get_counter_recv()
            ctr_flag = True
        if self.ctr_send_req in get_info_list:
            tmp_ctl["send_rest_request"] = get_counter_send()
            ctr_flag = True
        if ctr_flag:
            result_shell["controller"] = tmp_ctl
            info_flug = True

        result_info = None
        result_info = {"informations": [result_shell]}

        GlobalModule.EM_LOGGER.debug("exec command result:%s" % (result_info,))
        return result_info

    @decorater_log
    def __get_status_str(self, em_status):
        '''
        Convert EM status to letter strings.  
        '''
        em_status_str = ""

        if em_status == EmSysCommonUtilityDB.STATE_READY_TO_START:
            em_status_str = EmControllerStatusGet.EM_STATUS_10
        elif em_status == EmSysCommonUtilityDB.STATE_CHANGE_OVER:
            em_status_str = EmControllerStatusGet.EM_STATUS_50
        elif em_status == EmSysCommonUtilityDB.STATE_READY_TO_STOP:
            em_status_str = EmControllerStatusGet.EM_STATUS_90
        elif em_status == EmSysCommonUtilityDB.STATE_START:
            em_status_str = EmControllerStatusGet.EM_STATUS_100
        else:
            em_status_str = self.EM_STATUS_UK

        GlobalModule.EM_LOGGER.debug("return str result:%s" % (em_status_str,))
        return em_status_str
