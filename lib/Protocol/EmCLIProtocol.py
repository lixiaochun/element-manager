#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmCLIProtocol.py
'''
Protocol processing section (CLI)
'''
import time
import json
import paramiko
import re
import GlobalModule
from EmCommonLog import decorater_log
from EmCommonLog import decorater_log_in_out


class EmCLIProtocol(object):
    '''
    Protocol processing section(CLI)class
    '''

    __CONNECT_OK = 1
    __CONNECT_CAPABILITY_NG = 2
    __CONNECT_NO_RESPONSE = 3

    _SSH_RECV_COUNT = 10

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''
        self._ssh_connect_device = None
        self.error_recv_message = []
        self._device_ip = None
        self._ssh_timeout_val = None
        self._ssh_recv_time = None

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
        Explanation about return value:
            Connection result : int (1:Normal, 3:No response)
        '''
        self._ssh_connect_device = None
        self._ssh_timeout_val = None
        self._ssh_recv_time = None

        parse_json = json.loads(device_info)

        device_info_dict = parse_json["device_info"]
        self._device_ip = device_info_dict["mgmt_if_address"]
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
            port_number = 22

        GlobalModule.EM_LOGGER.debug("port_number = %s", port_number)

        result, timer_protocol = GlobalModule.EM_CONFIG.\
            read_sys_common_conf("Timer_cli_protocol")

        if result is not True:
            timeout_val = 60
            GlobalModule.EM_LOGGER.debug(
                "CLI Timer default Setting: %s", timeout_val)
        else:
            timeout_val = int(timer_protocol) / 1000
            GlobalModule.EM_LOGGER.debug(
                "CLI Timer: %s", timeout_val)
        self._ssh_timeout_val = timeout_val
        self._ssh_recv_time = timeout_val / self._SSH_RECV_COUNT

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
                self._ssh_connect_device = paramiko.SSHClient()
                self._ssh_connect_device.set_missing_host_key_policy(
                    paramiko.AutoAddPolicy())
                self._ssh_connect_device.connect(hostname=self._device_ip,
                                                 port=port_number,
                                                 username=username,
                                                 password=password)
                break
            except Exception as exception:
                self._ssh_connect_device.close()
                GlobalModule.EM_LOGGER.debug(
                    "Connect Error:%s", str(type(exception)))
                GlobalModule.EM_LOGGER.debug(
                    "Connect Error args: %s", str(exception.args))
                GlobalModule.EM_LOGGER.debug(
                    "Connection Wait Counter: %s", count)
                time.sleep(retrytimer_val)
                if count < (retry_num_val - 1):
                    continue
                return GlobalModule.COM_CONNECT_NO_RESPONSE

        GlobalModule.EM_LOGGER.info("111001 SSH Connection(CLI) Open for %s",
                                    self._device_ip)

        return GlobalModule.COM_CONNECT_OK

    @decorater_log_in_out
    def send_control_signal(self, message_type, send_message):
        '''
        Transmit device control signal
            Transmit CLI to device and returns response signal.
        Explanation about parameter:
            message_type: Message type(response message)
            send_message: CLI command list
                        （Sends each transmission message by sending str of command one by one）
        Explanation about return value:
            Transmission result : boolean (True:Normal,False:Abnormal)
            Response signal : str (CLI response signal
                           (Returns OK or NG))
        '''
        is_judg_result, judg_message_type = self._judg_control_signal(
            message_type)

        GlobalModule.EM_LOGGER.debug("__send_signal_judg:%s", is_judg_result)
        GlobalModule.EM_LOGGER.debug("judg_message_type:%s", judg_message_type)

        if not is_judg_result:
            GlobalModule.EM_LOGGER.debug("__send_signal_judg NG")
            return False, None

        GlobalModule.EM_LOGGER.debug("_send_signal_judg OK")

        try:
            is_result, output = self._send_signal_to_device(send_message,
                                                            message_type)
        except Exception as exception:
            GlobalModule.EM_LOGGER.warning(
                "207005 protocol %s Sending Error", message_type)
            GlobalModule.EM_LOGGER.debug("Sending Error:%s", (exception,))
            is_result = False
            output = None

        return is_result, output

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
            self._ssh_connect_device.close()
        except Exception as exception:
            GlobalModule.EM_LOGGER.debug("Disconnect Error:%s", exception)
            return False
        GlobalModule.EM_LOGGER.info(
            "111002 SSH Connection(CLI) Closed For %s", self._device_ip)
        return True

    @decorater_log
    def _judg_control_signal(self, message_type):
        '''
        Control signal judgment
            Make judgment on the message to be sent based on the message type
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

    @decorater_log
    def _send_signal_to_device(self, send_message, mes_type):
        '''
         Sends messages to device
        '''
        if mes_type != "edit-config":
            GlobalModule.EM_LOGGER.debug("non edit-config request is OK")
            return True, "<ok/>"

        GlobalModule.EM_LOGGER.debug("send_message: %s", send_message)

        output = self._send_edit_config(send_message)

        GlobalModule.EM_LOGGER.debug("receive_message: %s", output)
        GlobalModule.EM_LOGGER.info("107003 Sending %s to %s",
                                    mes_type, self._device_ip)
        GlobalModule.EM_LOGGER.info("107002 Receiving rpc-reply from %s",
                                    self._device_ip)
        return True, output

    @decorater_log
    def _send_edit_config(self, send_message):
        '''
        edit-config for CLI(Sends messages for the connected object by using SSH)
        '''
        GlobalModule.EM_LOGGER.debug(
            "start exec command :\n%s" % (send_message,))
        try:
            output = self._exec_interactive(self._ssh_connect_device,
                                            send_message,
                                            self.error_recv_message)
            GlobalModule.EM_LOGGER.debug("Success exec command")
        except Exception as ex:
            GlobalModule.EM_LOGGER.warning(
                "211003 Protocol(CLI) Execution Error: %s", send_message)
            GlobalModule.EM_LOGGER.debug("Error exec command:%s" % (ex,))
            raise
        return output

    @decorater_log
    def _exec_interactive(self, ssh_obj, messages, err_mess):
        '''
        execution commands to ssh connecting device
        '''
        shell = ssh_obj.invoke_shell()
        shell.settimeout(self._ssh_timeout_val)
        shell.recv(self._ssh_recv_time)
        output = ""
        for mes in messages:
            GlobalModule.EM_LOGGER.debug("send command :%s" % (mes,))
            output += self._send_command(shell, mes[0], mes[1])
            if err_mess:
                for recv_err in err_mess:
                    if re.search(recv_err, output):
                        raise Exception(
                            "device config error :\n%s" % (output,))
        return output

    @decorater_log
    def _send_command(self,
                      shell_obj,
                      send_message,
                      receive_keyword):
        '''
        Send CLI command list to device connected by SSH.
        Parameter:
            shell_obj : ssh object
            send_message : Send message
            receive_keyword : Receive keyword
            error_keyword : Error keyword（default:None）
        Return value
            Received message
        '''
        output = ''
        shell_obj.send(send_message + '\n')
        while True:
            output = output + \
                shell_obj.recv(self._ssh_recv_time).decode('utf-8')
            if(re.search(receive_keyword, output)):
                break
        GlobalModule.EM_LOGGER.debug("receive message:%s" % (output,))
        return output
