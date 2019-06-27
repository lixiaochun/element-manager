#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: CiscoDriverASR1002_X.py

'''
Cisco ASR 1002-X driver
'''
import json

from CgwshDriverBase import CgwshDriverBase
from EmCommonLog import decorater_log, decorater_log_in_out
import GlobalModule

from ASRDriverParts.ShowCommand import ShowCommand
from ASRDriverParts.VRF import VRF
from ASRDriverParts.UNOInterface import UNOInterface
from ASRDriverParts.UNIInterface import UNIInterface
from ASRDriverParts.TunnelInterface import TunnelInterface
from ASRDriverParts.BGP import BGP
from ASRDriverParts.StaticRoute import StaticRoute

from ASRSetParameterECDB import ASRSetParameterECDB


class CiscoDriverASR1002_X(CgwshDriverBase):
    '''
    Cisco ASR 1002-X driver class
    '''

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''
        self.asr_as_super = super(CiscoDriverASR1002_X, self)
        self.asr_as_super.__init__()
        self.default_res_mes = "#"
        self.conf_res_mes = "#"
        self.net_protocol.error_recv_message = ["\n%"]
        self.net_protocol.non_error_recv_message = [
            "removed due to VRF change",
        ]
        self.net_protocol.connected_recv_message = "#"
        self.list_enable_service = [
            GlobalModule.SERVICE_CGWSH_SERVICE_MANAGEMENT,
            GlobalModule.SERVICE_CGWSH_UNI_ROUTE,
            GlobalModule.SERVICE_CGWSH_TUNNEL_SESSION
        ]
        self._comm_configuration_start = ("configure terminal",
                                          self.conf_res_mes)
        self._comm_configuration_end = ("end", self.default_res_mes)
        self.net_protocol.set_configuration_mode_command(
            self._comm_configuration_start, self._comm_configuration_end)

    @decorater_log
    def get_device_setting(self,
                           device_name,
                           service_type,
                           order_type,
                           is_before=False):
        is_ok, return_val = self.asr_as_super.get_device_setting(device_name,
                                                                 service_type,
                                                                 order_type,
                                                                 is_before)
        if is_ok and service_type is None:
            return_val = self._correct_get_config_for_compare(return_val)
        return is_ok, return_val

    @decorater_log
    def _get_latest_device_configuration(self, device_name):
        '''
        Newest device config for acquired. 
        Argument:
            device_name : device name str
        Return value:
            newest device config ; Str
            date and time when newest device config is aquired ; Str
        '''
        read_method = self.common_util_db.read_latest_device_configuration

        running_config, running_date = read_method(
            device_name, get_timing=2, log_type="after_running_config")
        return running_config, running_date

    @decorater_log
    def _correct_get_config_for_compare(self, device_config):
        '''
        Config acquired for comparison is adjusted.
        '''
        tmp = json.loads(self.device_info)
        platform_name = tmp.get("device_info", {}).get("platform_name")
        if "show startup-config" not in device_config:
            device_config = device_config.rstrip()
            device_config += "show startup-config"
        method = GlobalModule.CGWSH_DEV_UTILITY_DB.parse_config_data_for_public
        running_config, startup_config = method(device_config, platform_name)
        return running_config

    @decorater_log
    def _gen_get_command_list(self, device_name, service_type=None):
        '''
        Command for acquiring information  is generated.
        '''
        is_startup = False if service_type is None else True
        comm_list = []
        comm_list.extend(self._gen_start_command())
        tmp_ins = ShowCommand(device_name=device_name,
                              is_get_startup=is_startup)
        comm_list.extend(tmp_ins.output_add_command())
        self.common_util_log.logging(
            device_name,
            self.log_level_debug,
            "get command:%s" % (comm_list,),
            __name__)
        return comm_list

    @decorater_log
    def _gen_edit_command_list(self,
                               device_name,
                               ec_message,
                               service_type,
                               order_type):
        '''
        Set-command is generated.
        '''
        comm_list = []
        fvw_param = ASRSetParameterECDB(device_name=device_name,
                                        ec_message=ec_message,
                                        db_info=None)
        comm_list.extend(self._gen_start_command(is_edit=True))

        if service_type == GlobalModule.SERVICE_CGWSH_SERVICE_MANAGEMENT:
            tmp_list = self._gen_service_info_command(fvw_param, order_type)
            comm_list.extend(tmp_list)
        if service_type in (GlobalModule.SERVICE_CGWSH_SERVICE_MANAGEMENT,
                            GlobalModule.SERVICE_CGWSH_UNI_ROUTE):
            tmp_list = self._gen_static_route_command(fvw_param, order_type)
            comm_list.extend(tmp_list)
        if service_type == GlobalModule.SERVICE_CGWSH_TUNNEL_SESSION:
            tmp_list = self._gen_tunnel_if_command(fvw_param, order_type)
            comm_list.extend(tmp_list)
        comm_list.extend(self._gen_end_command())
        self.common_util_log.logging(
            device_name,
            self.log_level_debug,
            "edit command:%s" % (comm_list,),
            __name__)
        return comm_list

    @decorater_log
    def _gen_service_info_command(self, fvw_param, operation=None):
        '''
        Service (new) registration and delete command (except for static route) is generated.
        '''
        tmp_comm = []
        service_param = fvw_param.get_service_info()
        tmp_obj = VRF(**service_param["vrf"])
        tmp_comm.extend(self._get_command(tmp_obj, operation))
        tmp_obj = UNOInterface(**service_param["uno"])
        tmp_comm.extend(self._get_command(tmp_obj, operation))
        tmp_obj = UNIInterface(**service_param["uni"])
        tmp_comm.extend(self._get_command(tmp_obj, operation))
        for tunnel_if in service_param["tunnel_if"]:
            tmp_obj = TunnelInterface(**tunnel_if)
            tmp_comm.extend(self._get_command(tmp_obj, operation))
        tmp_obj = BGP(**service_param["bgp"])
        tmp_comm.extend(self._get_command(tmp_obj, operation))
        return tmp_comm

    @decorater_log
    def _gen_static_route_command(self, fvw_param, operation=None):
        '''
        staticRoute command is generated.
        '''
        tmp_comm = []
        static_param = fvw_param.get_static_route_info()
        for route in static_param["static_route"]:
            tmp_obj = StaticRoute(**route)
            tmp_comm.extend(self._get_command(tmp_obj, operation))
        return tmp_comm

    @decorater_log
    def _gen_tunnel_if_command(self, fvw_param, operation=None):
        '''
        tunnel command is generated.
        '''
        tmp_comm = []
        tunnel_param = fvw_param.get_tunnel_if_info()
        for tunnel_if in tunnel_param["tunnel_if"]:
            tmp_obj = TunnelInterface(**tunnel_if)
            tmp_comm.extend(self._get_command(tmp_obj, operation))
        return tmp_comm

    @decorater_log
    def _gen_start_command(self, is_edit=False):
        '''
        '''
        start_comm = []
        tmp_comm = ("terminal length 0", self.default_res_mes)
        start_comm.append(tmp_comm)
        if is_edit:
            start_comm.append(self._comm_configuration_start)
        return start_comm

    @decorater_log
    def _gen_end_command(self):
        '''
        Command used after process execution is generated.(it is set in edit mode)
        '''
        end_comm = []
        end_comm.append(self._comm_configuration_end)
        tmp_comm = ("write memory", self.default_res_mes)
        end_comm.append(tmp_comm)
        return end_comm
