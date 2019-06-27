#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: YamahaDriverNVR510.py

'''
Yamaha NVR 510 driver
'''
import json

from CgwshDriverBase import CgwshDriverBase
from EmCommonLog import decorater_log, decorater_log_in_out
import GlobalModule

from NVRDriverParts.ShowCommand import ShowCommand
from NVRDriverParts.Interface import Interface
from NVRDriverParts.PPPoE import PPPoE
from NVRDriverParts.Filtering import Filtering
from NVRDriverParts.DefaultGateway import DefaultGateway
from NVRDriverParts.StaticRoute import StaticRoute

from NVRSetParameterECDB import NVRSetParameterECDB
from NVRDriverCLIProtocol import NVRDriverCLIProtocol


class YamahaDriverNVR510(CgwshDriverBase):
    '''
    Yamaha NVR 510 driver class
    '''

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''
        self.nvr_as_super = super(YamahaDriverNVR510, self)
        self.nvr_as_super.__init__()
        self.net_protocol = NVRDriverCLIProtocol()
        self.normal_res_mes = ">"
        self.default_res_mes = "#"
        self.password_res_mes = "Password:"
        self.net_protocol.error_recv_message = ["Error:"]
        self.net_protocol.connected_recv_message = ">"
        self.list_enable_service = [
            GlobalModule.SERVICE_CGWSH_SERVICE_MANAGEMENT,
            GlobalModule.SERVICE_CGWSH_CUSTOMER_UNI_ROUTE,
            GlobalModule.SERVICE_CGWSH_PPP_SESSION,
        ]
        self._comm_administrator_start = ("administrator",
                                          self.password_res_mes)
        self._comm_administrator_end = ("quit", self.normal_res_mes)

    @decorater_log_in_out
    def get_device_setting(self,
                           device_name,
                           service_type,
                           order_type,
                           is_before=False):
        '''
        Control process to acquire individual driver part is initiated by driver common part.
        It is executed in protocol processing part.
        Argument:
            device_name : device name
            service_type : service type
            order_type : order type
            ec_message: EC message
        Return value:
            status in which process  has been terminated : Boolean (True:normal , False:fail)
            response from device : Str
        '''
        if is_before:
            return True, None
        is_ok, return_val = self.nvr_as_super.get_device_setting(device_name,
                                                                 service_type,
                                                                 order_type,
                                                                 is_before)
        if is_ok and service_type is None:
            return_val = self._correct_get_config_for_compare(return_val)
        return is_ok, return_val

    @decorater_log
    def _correct_get_config_for_compare(self, device_config):
        '''
        Config acquired for comparison are adjusted.
        '''
        tmp = json.loads(self.device_info)
        platform_name = tmp.get("device_info", {}).get("platform_name")
        method = GlobalModule.CGWSH_DEV_UTILITY_DB.parse_config_data_for_public
        corrected_config = method(device_config, platform_name)[0]
        return corrected_config

    @decorater_log
    def _gen_get_command_list(self, device_name, service_type=None):
        '''
        Acquire-infomation  command is generated.
        '''
        comm_list = []
        tmp_ins = ShowCommand(device_name=device_name)
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
        get_db = self.common_util_db.read_administrator_password
        is_db_result, device_info = get_db(device_name, service_type)
        if not is_db_result:
            raise Exception("Fault getting administrator password from DB")
        fvw_param = NVRSetParameterECDB(device_name=device_name,
                                        ec_message=ec_message,
                                        db_info=device_info)

        comm_list.extend(self._gen_start_command(fvw_param))

        if service_type == GlobalModule.SERVICE_CGWSH_SERVICE_MANAGEMENT:
            tmp_list = self._gen_service_info_command(fvw_param, order_type)
            comm_list.extend(tmp_list)
        if service_type in (GlobalModule.SERVICE_CGWSH_SERVICE_MANAGEMENT,
                            GlobalModule.SERVICE_CGWSH_CUSTOMER_UNI_ROUTE):
            tmp_list = self._gen_static_route_command(fvw_param, order_type)
            comm_list.extend(tmp_list)
        if service_type == GlobalModule.SERVICE_CGWSH_PPP_SESSION:
            tmp_list = self._gen_ppp_command(fvw_param, order_type)
            comm_list.extend(tmp_list)

        comm_list.extend(self._gen_end_command(is_edit=True))
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
        tmp_obj = Interface(**service_param["interface"])
        tmp_comm.extend(self._get_command(tmp_obj, operation))
        for item in service_param["pppoe"]:
            tmp_obj = PPPoE(**item)
            tmp_comm.extend(self._get_command(tmp_obj, operation))
        tmp_obj = Filtering()
        tmp_comm.extend(self._get_command(tmp_obj, operation))
        return tmp_comm

    @decorater_log
    def _gen_static_route_command(self, fvw_param, operation=None):
        '''
        static route command is generated.
        '''
        tmp_comm = []
        static_param = fvw_param.get_static_route_info()
        if static_param.get("default_gateway"):
            tmp_obj = DefaultGateway(
                static_param["default_gateway"])
            tmp_comm.extend(self._get_command(tmp_obj, operation))
        for route in static_param["static_route"]:
            tmp_obj = StaticRoute(**route)
            tmp_comm.extend(self._get_command(tmp_obj, operation))
        return tmp_comm

    @decorater_log
    def _gen_ppp_command(self, fvw_param, operation=None):
        '''
        ppp command is generated.
        '''
        tmp_comm = []
        ppp_param = fvw_param.get_pppoe_info()
        for item in ppp_param["pppoe"]:
            tmp_obj = PPPoE(**item)
            tmp_comm.extend(self._get_command(tmp_obj, operation))
        return tmp_comm

    @decorater_log
    def _gen_start_command(self, fvw_param=None):
        '''
        Advanced process command (to switch administrator mode) is generated.
        '''
        password = fvw_param.get_adminstrator_password()
        start_comm = []
        start_comm.append(self._comm_administrator_start)
        tmp = "{0}|{1}".format(self.default_res_mes, self.normal_res_mes)
        tmp_comm = (password, tmp)
        start_comm.append(tmp_comm)
        self.net_protocol.set_configuration_mode_command(
            tmp_comm, self._comm_administrator_end)
        return start_comm

    @decorater_log
    def _gen_end_command(self, is_edit=False):
        '''
        Command after main process is executed (to save result and exit administrator mode) is generated.
        '''
        end_comm = []
        if is_edit:
            tmp_comm = ("save", self.default_res_mes)
            end_comm.append(tmp_comm)
        end_comm.append(self._comm_administrator_end)
        return end_comm
