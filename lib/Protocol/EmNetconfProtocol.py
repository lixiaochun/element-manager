#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmNetconfProtocol.py
'''
Protocol processing section (Netconf)
'''
import traceback
import time
import json
from ncclient import manager
from ncclient import operations
import GlobalModule
import EmNetconfClient
from EmCommonLog import decorater_log
from EmCommonLog import decorater_log_in_out


class EmNetconfProtocol(object):
    '''
    Protocol processing section (Netconf) class
    '''

    __CONNECT_OK = 1
    __CONNECT_CAPABILITY_NG = 2
    __CONNECT_NO_RESPONSE = 3

    @decorater_log_in_out
    def connect_device(self, device_info):
        '''
        Device connection control
            Conduct SSH connection to applicable device as request information.
        Explanation about parameter:
            device_info: Device information
                           Platform name
                           OS
                           Firm version
                           Login ID
                           Password
                           IPv4 address for management
                           Prefix of IPv4 address for management
                           Device information to be used for ncclient.
                               (to be set only when necessary)
                           Port No. to be used for ncclient.
                               (to be set only when necessary)
        Explanation about return value:
            Connection result :
                int (1:Normal, 2: Capability Abnormal 3:No response)
        '''
        parse_json = json.loads(device_info)

        device_info_dict = parse_json["device_info"]
        self.__device_ip = device_info_dict["mgmt_if_address"]
        username = device_info_dict["username"]
        password = device_info_dict["password"]
        device_info = device_info_dict.get("device_info")
        port_number = device_info_dict.get("port_number")

        if device_info is not None:
            device_params = {'name': str(device_info)}

        else:
            device_params = None

        GlobalModule.EM_LOGGER.debug("device_params = %s", device_params)

        if port_number is None:
            port_number = 830

        GlobalModule.EM_LOGGER.debug("port_number = %s", port_number)

        result, timer_protocol = GlobalModule.EM_CONFIG.\
            read_sys_common_conf("Timer_netconf_protocol")

        if result is not True:
            timeout_val = 60
            GlobalModule.EM_LOGGER.debug(
                "Netconf Protocol Timer default Setting: %s", timeout_val)
        else:
            timeout_val = timer_protocol / 1000
            GlobalModule.EM_LOGGER.debug(
                "Netconf Protocol Timer: %s", timeout_val)

        result, timer_connection = GlobalModule.EM_CONFIG.\
            read_sys_common_conf("Timer_connection_retry")

        if result is not True:
            retrytimer_val = 5
            GlobalModule.EM_LOGGER.debug(
                "Connection Retry Timer default Setting: %s", retrytimer_val)
        else:
            retrytimer_val = timer_connection / 1000.0
            GlobalModule.EM_LOGGER.debug(
                "Connection Retry Timer: %s", retrytimer_val)

        result, retry_num = GlobalModule.EM_CONFIG.\
            read_sys_common_conf("Connection_retry_num")

        if result is not True:
            retry_num_val = 5
            GlobalModule.EM_LOGGER.debug(
                "Connection Retry Num default Setting: %s", retry_num_val)
        else:
            retry_num_val = retry_num
            GlobalModule.EM_LOGGER.debug(
                "Connection Retry Num: %s", retry_num_val)

        for count in range(retry_num_val):
            try:
                self.__connection = EmNetconfClient.connect_ssh(
                    host=self.__device_ip,
                    port=port_number,
                    username=username,
                    password=password,
                    timeout=timeout_val,
                    hostkey_verify=False,
                    device_params=device_params,
                    device_info=device_info_dict)

                break

            except Exception as exception:
                GlobalModule.EM_LOGGER.debug(
                    "Connect Error:%s", str(type(exception)))
                GlobalModule.EM_LOGGER.debug(
                    "Connect Error args: %s", str(exception.args))
                GlobalModule.EM_LOGGER.debug(traceback.format_exc())
                GlobalModule.EM_LOGGER.debug(
                    "Connection Wait Counter: %s", count)

                time.sleep(retrytimer_val)

                if count < (retry_num_val - 1):
                    continue

                return self.__CONNECT_NO_RESPONSE

        device_capability_list = self.__connection.server_capabilities
        GlobalModule.EM_LOGGER.debug(
            "device_capability_list: %s", device_capability_list)

        capability_judge = False
        for cap in self.__capability_list:
            for device_cap in device_capability_list:
                if cap == device_cap:
                    capability_judge = True

        if capability_judge is not True:
            GlobalModule.EM_LOGGER.debug(
                "Connect Error:exceptions.MissingCapabilityError")
            return self.__CONNECT_CAPABILITY_NG

        self.__connection.raise_mode = operations.RaiseMode.NONE

        GlobalModule.EM_LOGGER.info("107001 SSH Connection Open for %s",
                                    self.__device_ip)

        return self.__CONNECT_OK

    @decorater_log_in_out
    def send_control_signal(self, message_type, send_message):
        '''
        Transmit device control signal
            Transmit Netconf to device and returns response signal.
        Explanation about parameter:
            message_type: Message type(response message)
                           discard-changes
                           validate
                           lock
                           unlock
                           get-config
                           edit-config
                           confirmed-commit
                           commit
            send_message: Send message
                           get-config:XML format (<config></config>)
                           edit-config:XML format (<config></config>)
                           Not necessary in case of other message types.
        Explanation about return value:
            Send result : boolean (True:Normal,False:Abnormal)
            REsponse signal : str (Netconf response signal
                           (Returns "NetconfSendOK" to return value 1
                            when rpc-error is received successfully.))
        '''
        is_judg_result, judg_message_type = self.__judg_control_signal(
            message_type)

        GlobalModule.EM_LOGGER.debug("__send_signal_judg:%s", is_judg_result)
        GlobalModule.EM_LOGGER.debug("judg_message_type:%s", judg_message_type)

        if is_judg_result is False:
            GlobalModule.EM_LOGGER.debug("__send_signal_judg NG")

            return False, None

        GlobalModule.EM_LOGGER.debug("__send_signal_judg OK")

        try:
            if judg_message_type == "get_config":
                GlobalModule.EM_LOGGER.debug("judg_message_type:get_config")
                GlobalModule.EM_LOGGER.debug(
                    "send_message: %s", send_message)

                receive_message = self.__connection.get_config(
                    source='running',
                    filter=('subtree', send_message)).data_xml

                GlobalModule.EM_LOGGER.debug(
                    "receive_message: %s", receive_message)
                GlobalModule.EM_LOGGER.debug(
                    "receive_message type: %s", type(receive_message))

            elif judg_message_type == "edit_config":
                GlobalModule.EM_LOGGER.debug("judg_message_type:edit_config")
                GlobalModule.EM_LOGGER.debug(
                    "send_message: %s", send_message)

                receive_message = self.__connection.edit_config(
                    config=send_message).xml

                GlobalModule.EM_LOGGER.debug(
                    "receive_message: %s", receive_message)
                GlobalModule.EM_LOGGER.debug(
                    "receive_message type: %s", type(receive_message))

            elif judg_message_type == "confirmed_commit":
                GlobalModule.EM_LOGGER.debug(
                    "judg_message_type:confirmed_commit")

                is_send_result, return_value = \
                    GlobalModule.EM_CONFIG.read_sys_common_conf(
                        "Timer_confirmed-commit")

                GlobalModule.EM_LOGGER.debug("read_sys_common:%s",
                                             is_send_result)

                if is_send_result is False:
                    GlobalModule.EM_LOGGER.debug("read_sys_common NG")

                    return False, None

                GlobalModule.EM_LOGGER.debug("read_sys_common OK")
                GlobalModule.EM_LOGGER.debug("return_value:%s", return_value)

                return_value = return_value / 1000

                receive_message = self.__connection.commit(
                    confirmed=True, timeout=str(return_value)).xml

                GlobalModule.EM_LOGGER.debug(
                    "receive_message: %s", receive_message)
                GlobalModule.EM_LOGGER.debug(
                    "receive_message type: %s", type(receive_message))

            else:
                GlobalModule.EM_LOGGER.debug("judg_message_type:%s",
                                             judg_message_type)

                try:
                    method = getattr(self.__connection, judg_message_type)
                    receive_message = method().xml

                    GlobalModule.EM_LOGGER.debug(
                        "receive_message: %s", receive_message)
                    GlobalModule.EM_LOGGER.debug(
                        "receive_message type: %s", type(receive_message))

                except AttributeError:
                    GlobalModule.EM_LOGGER.debug("AttributeError:%s",
                                                 judg_message_type)

                    return False, None

            GlobalModule.EM_LOGGER.info("107003 Sending %s to %s",
                                        message_type, self.__device_ip)

        except Exception as exception:
            GlobalModule.EM_LOGGER.warning(
                "207005 protocol %s Sending Error", message_type)
            GlobalModule.EM_LOGGER.debug(
                "Sending Error:%s", str(type(exception)))

            return False, None

        GlobalModule.EM_LOGGER.info("107002 Receiving rpc-reply from %s",
                                    self.__device_ip)

        return True, receive_message

    @decorater_log_in_out
    def disconnect_device(self):
        '''
        Device disconnection control
        Disconnect from the device.
        Explanation about parameter:
        None
        Explanation about return value:
        Judgment result : boolean (True:Normal,False:Abnormal)
        '''
        try:
            self.__connection.close_session()

        except Exception as exception:
            GlobalModule.EM_LOGGER.debug(
                "Disconnect Error:%s", str(type(exception)))

            return False

        GlobalModule.EM_LOGGER.info("107004 SSH Connection Closed for %s",
                                    self.__device_ip)

        return True

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        self.__connection = None
        self.__device_ip = None
        self.__capability_list = \
            ('urn:ietf:params:netconf:base:1.0',
             'urn:ietf:params:netconf:base:1.1')

    @decorater_log
    def __judg_control_signal(self, message_type):
        '''
        Control signal judgment
            Make judgment on the message to be sent based on the message type.
        Explanation about parameter:
            message_type: Message type (response message)
                           discard-changes
                           validate
                           lock
                           unlock
                           get-config
                           edit-config
                           confirmed-commit
                           commit
        Explanation about return value:
            Judgment result : boolean (True:Normal,False:Abnormal)
            Judgment message type : str
        '''

        message_list = ["discard-changes", "validate", "lock",
                        "unlock", "get-config", "edit-config",
                        "confirmed-commit", "commit"]

        GlobalModule.EM_LOGGER.debug("message_type:%s", message_type)

        if message_type in message_list:
            GlobalModule.EM_LOGGER.debug("message_type Match")

            judg_message_type = message_type.replace('-', '_')

            return True, judg_message_type

        GlobalModule.EM_LOGGER.debug("message_type UNMatch")

        return False, None
