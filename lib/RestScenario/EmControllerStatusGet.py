#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmControllerStatusGet.py.
'''
Scenario to obtain controller status
'''
import os
import traceback
import commands
import json
from flask import jsonify
from copy import deepcopy
import paramiko
import EmSeparateRestScenario
import GlobalModule
from EmCommonLog import decorater_log, decorater_log_in_out
from MsfEmMain import get_counter_send
from EmRestServer import get_counter_recv
from EmSysCommonUtilityDB import EmSysCommonUtilityDB


class UrlParameterGetInfo(object):
    os_cpu = "os-cpu"
    os_mem = "os-mem"
    os_disk = "os-disk"
    os_trafic = "os-traffic"
    ctr_cpu = "ctr-cpu"
    ctr_mem = "ctr-mem"
    ctr_state = "ctr-state"
    ctr_receive_req = "ctr-receive_rest_req"
    ctr_send_req = "ctr-send_rest_req"


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
        super(self.__class__, self).__init__()
        self.scenario_name = "EmControllerStatusGet"
        self.error_code_top = "01"
        self._error_code_list = {"010101": 400,
                                 "010201": 409,
                                 "010303": 500,
                                 "010304": 500,
                                 "010305": 500,
                                 "010306": 500,
                                 "010399": 500, }
        self._em_lib_path = GlobalModule.EM_LIB_PATH
        self.os_cpu = UrlParameterGetInfo.os_cpu
        self.os_mem = UrlParameterGetInfo.os_mem
        self.os_disk = UrlParameterGetInfo.os_disk
        self.os_trafic = UrlParameterGetInfo.os_trafic
        self.ctr_cpu = UrlParameterGetInfo.ctr_cpu
        self.ctr_mem = UrlParameterGetInfo.ctr_mem
        self.ctr_state = UrlParameterGetInfo.ctr_state
        self.ctr_receive_req = UrlParameterGetInfo.ctr_receive_req
        self.ctr_send_req = UrlParameterGetInfo.ctr_send_req
        self._get_info_list = (self.os_cpu,
                               self.os_mem,
                               self.os_disk,
                               self.os_trafic,
                               self.ctr_cpu,
                               self.ctr_mem,
                               self.ctr_state,
                               self.ctr_receive_req,
                               self.ctr_send_req, )
        self.em_act = "em"
        self.em_sby = "em_sby"
        self._ctl_info_list = (self.em_act, self.em_sby)
        self._ctl_shell_class = {
            self.em_act: ExecuteShellScript,
            self.em_sby: ExecuteShellScriptWithSSH,
        }
        self._shell_analysis_class = {
            self.em_act: AnalysisShellResultAct,
            self.em_sby: AnalysisShellResultSby,
        }

    @decorater_log_in_out
    def get_status(self, get_info="", controller=""):
        '''
        Execute shell script to obtain specified information.
        Parameter:
            get_info : URL parameter get_info (str)
            controller : URL parameter controller (str)
        Return value:
            Result in case when get_info and controller are set as argument(dict)
            However, management IF and EM status does not exist.
        '''
        try:
            os_info = self._scenario_main_get_status(controller, get_info)
        except Exception as exc_info:
            GlobalModule.EM_LOGGER.debug("ERROR:%s", exc_info)
            GlobalModule.EM_LOGGER.debug(
                "Trace Back:%s" % (traceback.format_exc(),))
            raise
        GlobalModule.EM_LOGGER.debug("GetStatus:%s", os_info)
        return os_info

    @decorater_log
    def _get_url_param(self, request):
        '''
        Obtain URL parameter.
        '''
        if request is None:
            raise ValueError("Request object is NULL")
        get_info = self._get_url_parameter(request, "get_info", str, True)
        get_info = self._correct_url_param(get_info)
        ctl_info = self._get_url_parameter(request, "controller", str, True)
        ctl_info = self._correct_url_param(ctl_info)
        self.url_parameter = {"get_info": get_info, "controller": ctl_info, }
        self.get_info = get_info
        self.ctl_info = ctl_info
        return self.url_parameter

    @decorater_log
    def _correct_url_param(self, url_param):
        '''
        Correct specified URL parameter value.
        Parameter:
            url_param : URL parameter (str)
        Return value:
            Corrected URL parameter str
        '''
        return_val = url_param.replace(" ", "+") if url_param else url_param
        return return_val

    @decorater_log
    def _scenario_main(self, *args, **kwargs):
        '''
        Scenario processing section.
        Obtain controller status.
        '''
        os_info = {}
        get_info = self.get_info
        ctl_info = self.ctl_info
        request_count = kwargs.get("request_date_list", ())
        try:
            os_info = self._scenario_main_get_status(ctl_info, get_info)
            response = self._gen_response(os_info, request_count)
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
    def _scenario_main_get_status(self, ctl_info, get_info):
        '''
        Execute shell script to obtain controller status.
        Parameter：
            ctl_info:controller to be obtained (str)
            get_info::controller to be obtained (str)
        Return value:
            Result : information(dict)
        '''
        os_info = {}
        ctl_info_list = self._analysis_url_parameter(ctl_info,
                                                     self._ctl_info_list)
        get_info_list = self._analysis_url_parameter(get_info,
                                                     self._get_info_list)
        info_list = []
        ctl = None
        try:
            for ctl in ctl_info_list:
                exec_shell_cls = self._ctl_shell_class[ctl]
                result_analysis_cls = self._shell_analysis_class[ctl]
                shell_result = (
                    self._exec_shell_controller_status(get_info_list,
                                                       exec_shell_cls,
                                                       result_analysis_cls)
                )
                shell_result["controller_type"] = ctl
                info_list.append(shell_result)
        except Exception:
            GlobalModule.EM_LOGGER.error(
                '310010 Failed to Em Controller status get: "%s"', ctl)
            raise
        os_info["informations"] = info_list
        return os_info

    @decorater_log
    def _gen_response(self, os_info, request_count):
        '''
        Create response.
        '''
        tmp_json = self._gen_response_json(os_info)
        response = jsonify(tmp_json)
        response.headers["Content-Type"] = "application/json"
        response.status_code = 200
        return response

    @decorater_log
    def _gen_response_json(self, os_info):
        '''
        Create Json for response.
        '''
        res_json = deepcopy(os_info)
        is_ok, em_status = GlobalModule.EMSYSCOMUTILDB.read_system_status()
        if not is_ok:
            raise IOError(
                (self._error_text % ("010305", "Cannot get Em Status")))
        res_json["status"] = self._get_status_str(em_status)
        GlobalModule.EM_LOGGER.debug(
            "Make Response Json:%s" % (res_json,))
        return res_json

    @decorater_log_in_out
    def _analysis_url_parameter(self, url_info=None, info_list=()):
        '''
        Analyze URL parameter and determine items to be obtained.
        Parameter:
            url_info : URL parameter value (str)
            info_list : list storing URL parameter elements (tuple)
        Return value:
            list of URL parameter elements (list)
        '''
        url_info = url_info if url_info else ""
        url_datas = url_info.split("+")
        url_info_list = [param for param in info_list if (param in url_datas)]
        if not url_info_list:
            url_info_list = list(deepcopy(info_list))
        return url_info_list

    @decorater_log
    def _exec_shell_controller_status(self,
                                      get_info_list,
                                      shell_class,
                                      result_analysis_cls):
        '''
        Execute controller_status,sh.
        '''
        shell_obj = shell_class(self._em_lib_path)
        shell_obj.get_shell_info_from_config()
        shell_obj.set_shell_command_parameter(get_info_list)
        shell_obj.set_command()
        return_value = shell_obj.execute()

        analysis_obj = result_analysis_cls()
        json_result = analysis_obj.analysis_result(return_value,
                                                   get_info_list)
        return json_result

    @decorater_log
    def _get_status_str(self, em_status):
        '''
        Convert EM status to string.
        Explanation about parameter:
            em_status:EM Status (integer)
        Explanation about return value:
            EM Status (str)
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


class ExecuteShellScript(object):
    '''
    Execute shell script.
    '''

    _error_text = EmSeparateRestScenario.EmRestScenario._error_text

    @decorater_log
    def __init__(self, lib_path):
        '''
        Constructor.
        '''
        self.lib_path = lib_path
        self.shell_file_path = None
        self.command_param = None
        self.command_txt = None

    @decorater_log_in_out
    def get_shell_info_from_config(self):
        '''
        Obtain necessary information from config management section.
        '''
        self.shell_file_path = self._get_config(
            "Statusget_shell_file_path",
            GlobalModule.EM_CONFIG.read_if_process_rest_conf)

    @decorater_log_in_out
    def set_command(self):
        '''
        Create executing command.
        Parameter:
            command_param : command argument in shell script (str)
        '''
        shell_path = os.path.join(self.lib_path, self.shell_file_path)
        self.command_txt = "%s %s" % (shell_path, self.command_param)

    @decorater_log
    def set_shell_command_parameter(self, get_info_list):
        '''
        Create command line argument for controller_status,sh.
        Explanation about parameter:
            get_info_list:Acquisition Target List
        Explanation about return value:
            None
        '''
        top_param = 0
        nproc_param = 0
        df_param = 0
        sar_param = 0
        hostname_param = 1
        mypid = self._get_pid()
        for item in get_info_list:
            if item in (UrlParameterGetInfo.os_cpu,
                        UrlParameterGetInfo.os_mem,
                        UrlParameterGetInfo.os_disk,
                        UrlParameterGetInfo.ctr_cpu,
                        UrlParameterGetInfo.ctr_mem):
                top_param = 1
            if item in (UrlParameterGetInfo.ctr_cpu,):
                nproc_param = 1
            if item in (UrlParameterGetInfo.os_disk,):
                df_param = 1
            if item in (UrlParameterGetInfo.os_trafic,):
                sar_param = 1
        command_param = "%s %s %s %s %s %s" % (top_param,
                                               nproc_param,
                                               df_param,
                                               sar_param,
                                               hostname_param,
                                               mypid)
        self.command_param = command_param

    @decorater_log
    def _get_pid(self):
        '''
        Obtain PID.
        '''
        return os.getpid()

    @decorater_log_in_out
    def execute(self):
        '''
        Execute command.
        '''
        GlobalModule.EM_LOGGER.debug("exec command:%s" % (self.command_txt,))
        return_value = self._execute_command()
        GlobalModule.EM_LOGGER.debug("shell result = %s", return_value)
        return return_value

    @decorater_log
    def _execute_command(self, command_txt=None):
        '''
        Execute shell script for this server.
        Explanation about parameter:
            command_txt:Execute Command
        Explanation about return value:
            Command Execute Result
        '''
        if not command_txt:
            command_txt = self.command_txt
        shell_result = commands.getstatusoutput(command_txt)
        if shell_result[0] != 0:
            error_mes = "Failed to execute shell:{0}".format(shell_result[1])
            raise Exception((self._error_text % ("010305", error_mes)))
        else:
            return_value = shell_result[1]
        return return_value

    @decorater_log
    def _get_config(self, key=None, conf=None):
        '''
        Obtain config from config manamement section.
        Explanation about parameter:
            key:Configuration Key
            conf:Configuration Dictionary
        Explanation about return value:
            Configuration Value
        '''
        is_ok, value = conf(key)
        if not is_ok:
            raise IOError((self._error_text %
                           ("010305", "Cannot read Config")))
        return value


class ExecuteShellScriptWithSSH(ExecuteShellScript):
    '''
    Connecct with SSH and execute shell script.
    '''

    @decorater_log
    def __init__(self, lib_path):
        '''
        Constructor
        '''
        super(self.__class__, self).__init__(lib_path)
        self.address = None
        self.port = 22
        self.username = None
        self.password = None

    @decorater_log_in_out
    def get_shell_info_from_config(self):
        '''
        Obtain necessary information from config management section.
        '''
        self.address = self._get_config(
            "Em_standby_server_address",
            GlobalModule.EM_CONFIG.read_sys_common_conf)
        self.shell_file_path = self._get_config(
            "Em_standby_server_statusget_shell_file_path",
            GlobalModule.EM_CONFIG.read_sys_common_conf)
        self.username = self._get_config(
            "Em_standby_user",
            GlobalModule.EM_CONFIG.read_sys_common_conf)
        self.password = self._get_config(
            "Em_standby_access_pass",
            GlobalModule.EM_CONFIG.read_sys_common_conf)

    @decorater_log_in_out
    def set_command(self):
        '''
        Create executing command.
        '''
        shell_path = self.shell_file_path
        self.command_txt = "%s %s" % (shell_path, self.command_param)

    @decorater_log
    def _get_pid(self):
        '''
        Obtain PID(0 is set because EM is not running in SBY(pid=null).
        '''
        return 0

    @decorater_log
    def _execute_command(self, command_txt=None):
        '''
        Connect with the server by using SSH and execute shell script.
        Explanation about parameter:
            command_txt:Execute Command
        Explanation about return value:
            Command Execute Result
        '''
        if not command_txt:
            command_txt = self.command_txt
        with paramiko.SSHClient() as ssh:
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=self.address,
                        port=self.port,
                        username=self.username,
                        password=self.password)
            stdin, stdout, stderr = ssh.exec_command(command_txt)
            info_stdout = stdout.read()
            info_stderr = stderr.read()
            if info_stderr:
                GlobalModule.EM_LOGGER.debug("stdout:%s", info_stdout)
                error_mes = "Failed to execute shell:{0}".format(info_stderr)
                raise paramiko.ssh_exception.SSHException(
                    (self._error_text % ("010306", error_mes)))
            else:
                return_value = info_stdout
        return return_value


class AnalysisShellResult(object):
    '''
    Analyze shell script result.
    '''

    _error_text = EmSeparateRestScenario.EmRestScenario._error_text

    @decorater_log
    def __init__(self):
        self.mgmt_conf_key = None
        self.mgmt_conf_method = GlobalModule.EM_CONFIG.read_sys_common_conf
        self.ctl_type = None

    @decorater_log
    def analysis_result(self, shell_result_txt, get_info_list):
        '''
        Analyze shell script result.
        Explanation about parameter:
            result_json:shell script result (txt)
            get_info_list:Acquisition Target List
        Explanation about return value:
            Shell script result (dict)
        '''
        result_json = json.loads(shell_result_txt)
        result_shell = self._analysis_shell_info(result_json,
                                                 get_info_list)
        mgmt_ip = self._get_em_mgmt_ip_address()
        if mgmt_ip:
            result_shell["management_ip_address"] = mgmt_ip
        result_shell["controller_type"] = self.ctl_type
        return result_shell

    @decorater_log
    def _analysis_shell_info(self,
                             result_json,
                             get_info_list):
        '''
        Analyze shell script result(core information and  OS information).
        Explanation about parameter:
            result_json:shell script result (json)
            get_info_list:Acquisition Target List
        Explanation about return value:
            Shell script result (dict)
        '''
        result_shell = {}
        result_shell["host_name"] = result_json.get("hostname")
        tmp_os = {}
        tmp_result_top = result_json.get("top")
        tmp_cpu_id = float(tmp_result_top.get("id"))
        if UrlParameterGetInfo.os_mem in get_info_list:
            tmp_os["memory"] = {
                "used": tmp_result_top.get("used"),
                "free": tmp_result_top.get("free"),
                "buff_cache": tmp_result_top.get("buffers"),
                "swpd": tmp_result_top.get("swapused"),
            }
        if UrlParameterGetInfo.os_cpu in get_info_list:
            tmp_os["cpu"] = {"use_rate": 100.0 - tmp_cpu_id, }
        if UrlParameterGetInfo.os_disk in get_info_list:
            tmp_list = []
            for tmp_disk in result_json.get("df", ()):
                tmp_data = tmp_disk.split(" ")
                tmp_json_data = {"file_system": tmp_data[0],
                                 "mounted_on":  tmp_data[5],
                                 "size":  int(tmp_data[1]),
                                 "used":  int(tmp_data[2]),
                                 "avail":  int(tmp_data[3]), }
                tmp_list.append(tmp_json_data)
            tmp_os["disk"] = {"devices": tmp_list}
        if UrlParameterGetInfo.os_trafic in get_info_list:
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
        if tmp_os:
            result_shell["os"] = tmp_os

        GlobalModule.EM_LOGGER.debug(
            "exec command result:%s" % (result_shell,))
        return result_shell

    @decorater_log
    def _get_em_mgmt_ip_address(self):
        '''
        Obtain management IP address for em.
        '''
        is_ok, mgmt_ip = self.mgmt_conf_method(self.mgmt_conf_key)
        if not is_ok:
            raise IOError(
                (self._error_text % ("010305", "Cannot read Config Mgmt IP")))
        return mgmt_ip


class AnalysisShellResultAct(AnalysisShellResult):
    '''
    Analyze shell script result(ACT).
    '''

    @decorater_log
    def __init__(self):
        '''
        Constructor.
        '''
        super(self.__class__, self).__init__()
        self.mgmt_conf_key = "Controller_management_address"
        self.ctl_type = "em"

    @decorater_log
    def _analysis_shell_info(self,
                             result_json,
                             get_info_list):
        '''
        Analyze shell script result(core information and  OS information).
        Explanation about parameter:
            result_json:shell script result (json)
            get_info_list:Acquisition Target List
        Explanation about return value:
            Shell script result (dict)
        '''
        super_mtd = super(self.__class__, self)._analysis_shell_info
        result_info = super_mtd(result_json, get_info_list)
        ctl_info = self._analysis_controller_info(result_json,
                                                  get_info_list)
        if ctl_info:
            result_info["controller"] = ctl_info
        return result_info

    @decorater_log
    def _analysis_controller_info(self,
                                  result_json,
                                  get_info_list):
        '''
        Obtain controller information.
        Explanation about parameter:
            result_json:shell script result (json)
            get_info_list:Acquisition Target List
        Explanation about return value:
            Shell script result (dict)
        '''
        tmp_ctl = {}
        tmp_result_top = result_json.get("top")
        tmp_nprco = float(result_json.get("nproc"))
        tmp_cpu_val = None
        if UrlParameterGetInfo.ctr_cpu in get_info_list:
            tmp_cpu_ctrl = float(tmp_result_top.get("cpu"))
            tmp_cpu_val = tmp_cpu_ctrl / tmp_nprco
            tmp_ctl["cpu"] = tmp_cpu_val
        if UrlParameterGetInfo.ctr_mem in get_info_list:
            tmp_ctl["memory"] = tmp_result_top.get("res")
        if UrlParameterGetInfo.ctr_receive_req in get_info_list:
            tmp_ctl["receive_rest_request"] = get_counter_recv()
        if UrlParameterGetInfo.ctr_send_req in get_info_list:
            tmp_ctl["send_rest_request"] = get_counter_send()
        return tmp_ctl


class AnalysisShellResultSby(AnalysisShellResult):
    '''
    Analyze shell script result(SBY).
    '''

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''
        super(self.__class__, self).__init__()
        self.mgmt_conf_key = "Em_standby_server_address"
        self.ctl_type = "em_sby"
