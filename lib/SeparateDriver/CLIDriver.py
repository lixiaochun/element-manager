#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2018 Nippon Telegraph and Telephone Corporation
# Filename: CLIDriver.py

'''
CLI driver (base) module
'''
import json
import traceback

from EmSeparateDriver import EmSeparateDriver
from EmCLIProtocolBase import EmCLIProtocol
from EmCommonLog import decorater_log
from EmCommonLog import decorater_log_in_out
import GlobalModule


class CLIDriverBase(EmSeparateDriver):
    '''
    CLI driver (base) class
    '''

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''
        self.as_super = super(CLIDriverBase, self)
        self.as_super.__init__()
        self.net_protocol = EmCLIProtocol()
        self._port_number = 22

    @decorater_log_in_out
    def connect_device(self,
                       device_name,
                       device_info,
                       service_type,
                       order_type):
        '''
        Connection control of individual section on driver
            Get launched from driver common section,
             and conduct device connection control to the protocol processing section.
        Parameter:
            device_name : Device name
            device_info : Device information
            service_type : Service type
            order_type : Order type
        Return value :
            Protocol processint section response : int (1:Normal, 3:No response)
        '''
        if service_type not in self.list_enable_service:
            return GlobalModule.COM_CONNECT_NG
        else:
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
    def _gen_message_child(self,
                           device_info,
                           ec_message,
                           operation,
                           method_fix_message_gen,
                           method_variable_message_gen,
                           top_tag=None):
        '''
        Each message creation method
            Get called out when creating message of each service after service type has been determined.

        Parameter:
            device_info : DB informaiton
            ec_message : EC message
            operation : Order type (whether to delete or not only)
            method_fix_message_gen : Fixed message creation method
            method_variable_message_gen : Variable message creation method
        Return value
            Message creation result: Boolean
            Creation message : str
        '''
        return_val = False
        return_command = None
        try:
            return_command = method_variable_message_gen(device_info,
                                                         ec_message,
                                                         operation)
            self.common_util_log.logging(
                None, self.log_level_debug,
                "gen command:%s" % (
                    self._logging_send_command_str(return_command),
                )
            )
            return_val = True
        except Exception as exc_info:
            self.common_util_log.logging(
                None,
                self.log_level_debug,
                "ERROR : generating command message is failed " +
                "/ Exception: %s" % (exc_info),
                __name__)
        return return_val, return_command

    @staticmethod
    @decorater_log
    def _logging_send_command_str(command_list=[]):
        '''
        Indicate transmission command as string
        '''
        com_str = "start_command_display:\n"
        for item in command_list:
            com_str += "%s\n" % (item[0],)
        com_str += "end_command_display"
        return com_str
