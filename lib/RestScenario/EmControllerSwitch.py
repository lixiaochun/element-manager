#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmControllerSwitch.py
'''
Scenario for switch-over controller
'''
import os
import traceback
import subprocess
from flask import jsonify
import EmSeparateRestScenario
import GlobalModule
from EmCommonLog import decorater_log


class EmControllerSwitch(EmSeparateRestScenario.EmRestScenario):
    '''
    Class for switching-over controller
    '''

    @decorater_log
    def __init__(self):
        '''
        Costructor
        '''
        super(EmControllerSwitch, self).__init__()
        self.scenario_name = "ControllerSwitch"
        self.error_code_top = "04"
        self._error_code_list = {"040301": 500,
                                 "040399": 500, }
 
        self._em_lib_path = GlobalModule.EM_LIB_PATH

        self._em_resource_name = self._get_config(
            "Em_resource_group_name",
            GlobalModule.EM_CONFIG.read_sys_common_conf)
        self._em_resource_status_target_name = self._get_config(
            "Em_resource_status_target_name",
            GlobalModule.EM_CONFIG.read_sys_common_conf)

    @decorater_log
    def _get_config(self, key=None, conf=None):
        '''
        Config is acquired from config management part.
        Argument:
            key: key value in config
            conf: config file to be acquired
        Return value:
            config value
        '''
        is_ok, value = conf(key)
        if not is_ok:
            raise IOError((self._error_text %
                           ("040399", "Cannot read Config")))
        return value

    @decorater_log
    def _scenario_main(self, *args, **kwargs):
        '''
        Scenario processing part
        Controller is switched-over.
        '''
        try:
            self._exec_shell_controller_switch()
            response = self._gen_response()
        except IOError as ex:
            GlobalModule.EM_LOGGER.debug(
                "Trace Back:%s" % (traceback.format_exc(),))

            raise IOError(
                (self._error_text % ("040301", ex.message)))
        except Exception as ex:
            GlobalModule.EM_LOGGER.debug(
                "Trace Back:%s" % (traceback.format_exc(),))
            raise
        return response

    @decorater_log
    def _gen_response(self):
        '''
        Response is generated.
        '''
        tmp_json = {}
        response = jsonify(tmp_json)
        response.headers["Content-Type"] = "application/json"
        response.status_code = 202
        return response

    @decorater_log
    def _exec_shell_controller_switch(self):
        '''
        Controller_switch.sh is executed.
        '''
        isout, shell_file_name = (
            GlobalModule.
            EM_CONFIG.read_if_process_rest_conf(
                "Controller_switch_shell_file_path"))
        if not isout:
            raise IOError(
                (self._error_text % ("040301", "Cannot read Config")))
        shelL_path = os.path.join(self._em_lib_path, shell_file_name)
        command_txt = "%s %s %s" % (shelL_path,
                                    self._em_resource_name,
                                    self._em_resource_status_target_name)
        GlobalModule.EM_LOGGER.debug("exec command:%s" % (command_txt,))
        try:
            subprocess.Popen(command_txt, shell=True)
            GlobalModule.EM_LOGGER.info(
                "112003 Controller switching script Start")

        except Exception as ex:
            GlobalModule.EM_LOGGER.debug("command error:%s" % (ex.message,))
            raise Exception((self._error_text % ("040301", ex.message)))
