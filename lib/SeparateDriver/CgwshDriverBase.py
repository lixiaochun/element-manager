#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: CgwshDriverBase.py

'''
Cgwsh driver(base) module
'''
import json
import traceback

from EmSeparateDriver import EmSeparateDriver
from CgwshDriverCLIProtocol import CgwshDriverCLIProtocol
from CgwshDeviceDriverUtilityDB import CgwshDeviceDriverUtilityDB
from EmCommonLog import decorater_log
import GlobalModule


class CgwshDriverBase(EmSeparateDriver):
    '''
    Cgwsh driver(base) class
    '''

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''
        self.as_super = super(CgwshDriverBase, self)
        self.as_super.__init__()
        self.net_protocol = CgwshDriverCLIProtocol()
        self.common_util_db = CgwshDeviceDriverUtilityDB()
        self._port_number = 22
        self.driver_public_method["compare_to_latest_device_configuration"] = (
            self.compare_to_latest_device_configuration)

    @decorater_log
    def connect_device(self,
                       device_name,
                       device_info,
                       service_type,
                       order_type):
        '''
        Individual driver part is connected.
            It is initiated by common driver part.
            Connection process is requested to protocol processing part.
        Argument:
            device_name : device name
            device_info : device information
            service_type : service type
            order_type : order type
        Return value:
            response from protocol processing part : int (1:normal, 3:no response)
        '''
        tmp_device_info = None
        if device_info is not None:
            tmp_json = json.loads(device_info)
            if tmp_json.get("device_info") is not None:
                tmp_json["device_info"]["port_number"] = self._port_number
            tmp_device_info = json.dumps(tmp_json)
        return self.as_super.connect_device(device_name,
                                            tmp_device_info,
                                            service_type,
                                            order_type)

    @decorater_log
    def update_device_setting(self,
                              device_name,
                              service_type,
                              order_type,
                              ec_message=None):
        '''
        Individual driver part is edited.
            It is initiated by common driver part.
            Device control signal is sent to protocol processing part.
        Argument:
            device_name : device name
            service_type : service type
            order_type : order type
        Return value:
            status of process completed : int (1:update has succeeded.
                                               3:update has failed.)
        '''
        return self._edit_config_device_setting(device_name,
                                                service_type,
                                                order_type,
                                                ec_message)

    @decorater_log
    def delete_device_setting(self,
                              device_name,
                              service_type,
                              order_type,
                              ec_message=None):
        '''
        Individual driver part is deleted.
            It is initiated by common driver part.
            Delete process is requested to protocol processing part.
        Argument:
            device_name : device name
            service_type : service type
            order_type : order type
        Return value:
            status of process completed : int (1:succeed
                                               2:validation check is NG
                                               3:fail )
        '''
        return self._edit_config_device_setting(device_name,
                                                service_type,
                                                order_type,
                                                ec_message)

    @decorater_log
    def reserve_device_setting(self, device_name, service_type, order_type):
        '''
        Individual driver part is pre-set.
            It is initiated by common driver part.
            Pre-setting is requested to  protocol processing part.
        Argument:
            device_name : device name
            service_type : service type
            order_type : order type
        Return value:
            status of process completed : Boolean (True:succeeded, False:fail)
        '''

        return True

    @decorater_log
    def enable_device_setting(self, device_name, service_type, order_type):
        '''
        Individual driver part is committed.
            It is initiated by common driver part.
            Device-setting is comitted by protocol processing part.
        Argument:
            device_name : device name
            service_type : service type
            order_type : order type
        Return value:
            status of process completed : Boolean (True:succed , False:fail)
        '''
        return True

    @decorater_log
    def get_device_setting(self,
                           device_name,
                           service_type,
                           order_type,
                           is_before=False):
        '''
        Individual driver part is acquired.
            It is initiated by common driver part.
            Device information is acquired from protocol processing part.
        Argument:
            device_name : device name
            service_type : service type
            order_type : order type
            ec_message: EC message
        Return value:
            status of process completed : Boolean (True:succeed , False:fail)
            response signal from device : Str
        '''
        try:
            send_command = self._gen_get_command_list(device_name,
                                                      service_type)
            if not send_command:
                raise Exception("No command!")

            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                self._logging_send_command_str(send_command),
                __name__)

    
            is_result, res_mes = self._send_control_signal(device_name,
                                                           "get-config",
                                                           send_command)
            if not is_result:
                raise Exception("Fault Run Command!")

            return_val = True
            return_signal = res_mes
        except Exception as exc_info:
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "ERROR:Exception:%s" % (exc_info,),
                __name__)
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "Traceback:%s" % (traceback.format_exc(),),
                __name__)
            return_val = False
            return_signal = None
        return return_val, return_signal

    @decorater_log
    def _edit_config_device_setting(self,
                                    device_name,
                                    service_type,
                                    order_type,
                                    ec_message=None):
        '''
        Individual driver part is edited.
            It is initiated by common driver part.
            Device control signal is sent to protocol processing part.
        Argument:
            device_name : device name
            service_type : service type
            order_type : order type
        Return value:
            status of process completed : int (1:update has succeeded.
                                               3:update has failed.)
        '''
        self.common_util_log.logging(
            device_name,
            self.log_level_debug,
            "service=%s,order_type=%s" % (service_type, order_type,),
            __name__)
        try:
            if not self._check_service_type(device_name, service_type):
                raise ValueError("service NG(%s)" % (service_type,))
            if order_type == self._REPLACE:
                raise ValueError("Order NG(%s)" % (order_type,))

            send_command = self._gen_edit_command_list(device_name,
                                                       ec_message,
                                                       service_type,
                                                       order_type)
            if not send_command:
                raise Exception("No command!")

            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                self._logging_send_command_str(send_command),
                __name__)

            is_result = self._send_control_signal(device_name,
                                                  "edit-config",
                                                  send_command,
                                                  service_type,
                                                  order_type)[0]
            if not is_result:
                raise Exception("Fault Run Command!")

            return_val = self._update_ok
        except Exception as exc_info:
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "ERROR:Exception:%s" % (exc_info,),
                __name__)
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "Traceback:%s" % (traceback.format_exc(),),
                __name__)
            return_val = self._update_error
        return return_val

    @decorater_log
    def _get_command(self, comm_obj, operation=None):
        '''
        Command is output.
        '''
        tmp_comm = None
        if operation == self._DELETE:
            tmp_comm = comm_obj.output_del_command()
        else:
            tmp_comm = comm_obj.output_add_command()
        return tmp_comm

    @decorater_log
    def _gen_edit_command_list(self,
                               device_name,
                               ec_message,
                               service_type,
                               order_type):
        pass

    @decorater_log
    def _gen_get_command_list(self,
                              device_name,
                              ec_message,
                              order_type):
        pass

    @staticmethod
    @decorater_log
    def _logging_send_command_str(command_list=[]):
        '''
        Send-command is showed as a string.
        '''
        com_str = "start_command_display:\n"
        for item in command_list:
            com_str += "%s\n" % (item[0],)
        com_str += "end_command_display"
        return com_str
