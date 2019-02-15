#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2018 Nippon Telegraph and Telephone Corporation
# Filename: EmCLIProtocolMultipleBase.py
'''
Protocol processing section(CLI)
'''
import json
import paramiko
import re
import traceback
import GlobalModule
from EmCommonLog import decorater_log
from EmCommonLog import decorater_log_in_out


class EmCLIProtocol(object):
    '''
    Protocol processing section(CLI)Class
    '''

    __CONNECT_OK = 1
    __CONNECT_CAPABILITY_NG = 2
    __CONNECT_NO_RESPONSE = 3

    _SSH_RECV_COUNT = 10

    @decorater_log
    def __init__(self, error_recv_message=[], connected_recv_message="#"):
        '''
        Constructor
        '''
        self._ssh_connect_device = None
        self._ssh_shell = None
        self.error_recv_message = error_recv_message
        self.non_error_recv_message = []
        self.connected_recv_message = connected_recv_message
        self._device_ip = None
        self._ssh_timeout_val = None
        self._ssh_recv_time = None
        self._ssh_recv_mes_max_bytes = 50
        self._send_message_methods = {
            "get-config": self._send_edit_config,
            "edit-config": self._send_edit_config,
        }
        self._send_message_type = self._send_message_methods.keys()
        self._test_mode = False

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
        self._ssh_shell = None

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

        self._username = username
        self._port_number = port_number
        self._password = password

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

        try:
            self._ssh_connect()

        except Exception as ex:
            if self._ssh_connect_device:
                self._ssh_connect_device.close()
            GlobalModule.EM_LOGGER.debug("Error exec command:%s" % (ex,))
            GlobalModule.EM_LOGGER.debug(
                "Traceback:%s" % (traceback.format_exc(),))
            return GlobalModule.COM_CONNECT_NO_RESPONSE
        GlobalModule.EM_LOGGER.info("111001 SSH Connection(CLI) Open for %s",
                                    self._device_ip)
        return GlobalModule.COM_CONNECT_OK

    @decorater_log_in_out
    def send_control_signal(self, message_type, send_message=None):
        '''
        Transmit device control signal
            Transmit CLI to device and returns response signal
        Explanation about parameter:
            message_type: Message type (response message)
            send_message: List of CLI command
                        （Sends each transmission message by sending str of command one by one）
        Explanation about return value:
            Transmission result : boolean (True:Normal,False:Abnormal)
            Response signal : str (CLIResponse signal
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
        Disconnect from the device
        Explanation about parameter:
        None
        Explanation about return value:
        Judgment result : boolean (True:Normal,False:Abnormal)
        '''
        try:
            if self._ssh_connect_device:
                self._ssh_connect_device.close()
        except Exception as exception:
            GlobalModule.EM_LOGGER.debug("Disconnect Error:%s", exception)
            return False
        GlobalModule.EM_LOGGER.info(
            "111002 SSH Connection(CLI) Closed For %s", self._device_ip)
        return True

    @decorater_log
    def _ssh_connect(self):
        self._ssh_connect_device = paramiko.SSHClient()
        self._ssh_connect_device.set_missing_host_key_policy(
            paramiko.AutoAddPolicy())
        GlobalModule.EM_LOGGER.debug(
            "start ssh connect: %s@%s:%s Password=%s" % (
                self._username,
                self._device_ip,
                self._port_number,
                self._password)
        )
        self._ssh_connect_device.connect(hostname=self._device_ip,
                                         port=self._port_number,
                                         username=self._username,
                                         password=self._password)
        self._ssh_shell = self._ssh_connect_device.invoke_shell()
        self._ssh_shell.settimeout(self._ssh_timeout_val)
        self._recv_message(self._ssh_shell, self.connected_recv_message)
        GlobalModule.EM_LOGGER.info("SSH Connected")

    @decorater_log
    def _judg_control_signal(self, message_type):
        '''
        Control Signal Judgment
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

        message_list = [
            "discard-changes",
            "validate",
            "lock",
            "unlock",
            "get-config",
            "edit-config",
            "confirmed-commit",
            "commit",
        ]

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
        Sends messages to the device
        '''
        if mes_type not in self._send_message_type:
            GlobalModule.EM_LOGGER.debug(
                "non %s request is OK",
                "/".join(self._send_message_type)
            )
            return True, "<ok/>"

        GlobalModule.EM_LOGGER.debug("send_message: %s", send_message)

        send_method = self._send_message_methods[mes_type]
        output = send_method(send_message)

        GlobalModule.EM_LOGGER.debug("receive_message: %s", output)
        GlobalModule.EM_LOGGER.info("107003 Sending %s to %s",
                                    mes_type, self._device_ip)
        GlobalModule.EM_LOGGER.info("107002 Receiving rpc-reply from %s",
                                    self._device_ip)
        return True, output

    @decorater_log
    def _send_edit_config(self, send_message):
        '''
        edit-config for CLI(SSSends messages for the connected object by using SSH)
        '''
        GlobalModule.EM_LOGGER.debug(
            "start exec command :\n%s" % (send_message,))
        GlobalModule.EM_LOGGER.debug(
            self._logging_send_command_str(send_message))
        try:
            output = self._exec_interactive(send_message,
                                            self.error_recv_message)
            GlobalModule.EM_LOGGER.debug("Success exec command")
        except Exception as ex:
            GlobalModule.EM_LOGGER.warning(
                "211003 Protocol(CLI) Execution Error: %s", send_message)
            GlobalModule.EM_LOGGER.debug("Error exec command:%s" % (ex,))
            GlobalModule.EM_LOGGER.debug(
                "Traceback:%s" % (traceback.format_exc(),))
            raise
        return output

    @decorater_log
    def _exec_interactive(self, messages, err_mess):
        '''
        execution commands to ssh connecting device
        '''
        output = ""
        for mes in messages:
            GlobalModule.EM_LOGGER.debug("send command :%s" % (mes,))
            output += self._send_command(self._ssh_shell, mes[0], mes[1])
            self._check_command_error(output,
                                      err_mess,
                                      self.non_error_recv_message)
        return output

    @staticmethod
    @decorater_log
    def _check_command_error(output, err_mess=[], non_err_mes=[]):
        for recv_err in err_mess if err_mess else []:
            if re.search(recv_err, output):
                is_err = True
                for non_err in non_err_mes:
                    if re.search(non_err, output):
                        is_err = False
                        break
                if is_err:
                    raise Exception(
                        "device config error :\n%s" % (output,))
        return True

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
        shell_obj.send(send_message + '\n')
        return self._recv_message(shell_obj, receive_keyword)

    @decorater_log
    def _recv_message(self, shell_obj, receive_keyword):
        output = ''
        while True:
            tmp_rcv = shell_obj.recv(
                self._ssh_recv_mes_max_bytes).decode('utf-8')
            GlobalModule.EM_LOGGER.debug("receive:%s" % (tmp_rcv,))
            output = output + tmp_rcv
            if(re.search(receive_keyword, output)):
                break
        GlobalModule.EM_LOGGER.debug("receive all message:%s" % (output,))
        return output

    @decorater_log
    def _logging_send_command_str(self, command_list=[]):
        '''
        Displays transmission command as string
        '''
        tmp_ip = {"ip_addr": self._device_ip}
        com_str = "start_command_display[%(ip_addr)s]:\n" % tmp_ip
        for item in command_list:
            com_str += "%s\n" % (item[0],)
        com_str += "end_command_display"
        return com_str
