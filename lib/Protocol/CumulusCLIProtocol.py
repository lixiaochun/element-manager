#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: CumulusCLIProtocol.py

import json
import paramiko
import re
import traceback
import GlobalModule
from EmCommonLog import decorater_log
from EmCommonLog import decorater_log_in_out
from EmCLIProtocolBase import EmCLIProtocol


class CumulusCLIProtocol(EmCLIProtocol):
    '''
    Protocol Processing Section (CLI) Class for Cumulus
    '''

    _CUMULU_ROOT_RECV_MES = "#"
    _CUMULU_USER_RECV_MES = "\$"

    _COMM_ACLTOOL_INS = "cl-acltool -i"

    @decorater_log
    def __init__(self, error_recv_message=[], connected_recv_message="~"):
        super(CumulusCLIProtocol, self).__init__(error_recv_message,
                                                 connected_recv_message)
        self._send_message_methods = {
            "get-config": self._send_edit_config,
            "edit-config": self._send_edit_config,
            "discard-changes": self._send_discard_changes,
            "confirmed-commit": self._send_confirmed_commit,
            "commit": self._send_commit,
        }
        self._send_message_type = self._send_message_methods.keys()
        self._is_complete_confirmed_commit = False
        self._is_complete_commit = False
        self._recv_string_protocol = self._CUMULU_USER_RECV_MES
        self._password = None
        self.is_operation_policy_d = False
        self.is_complete_discard_change = False

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
        parse_json = json.loads(device_info)
        self._password = parse_json["device_info"]["password"]
        return super(CumulusCLIProtocol, self).connect_device(device_info)

    @decorater_log_in_out
    def disconnect_device(self):
        '''
        Device Disconnection Control
        Disconnects from the Device
        Parameter Explanation:
        None
        Explanation about Return Value:
        Judgement Result : boolean (True:Normal,False:Abnormal)
        '''
        if (self.is_operation_policy_d and
            not self._is_complete_commit and
                self.is_complete_discard_change):
            self._roleback_policy_d()
        return super(CumulusCLIProtocol, self).disconnect_device()


    @decorater_log
    def _ssh_connect(self):
        '''
        SSH Connection Process
        '''
        super(CumulusCLIProtocol, self)._ssh_connect()

    @decorater_log
    def _roleback_policy_d(self):
        '''
        policy.d rollback
        '''
        su_message = []
        su_message.extend(
            self._set_sudo_command("rm -fR /etc/cumulus/acl/policy.d",
                                   self._recv_string_protocol)
        )
        su_message.extend(
            self._set_sudo_command("cp -fR /tmp/policy.d /etc/cumulus/acl",
                                   self._recv_string_protocol)
        )
        su_message.extend(
            self._set_sudo_command(self._COMM_ACLTOOL_INS,
                                   self._recv_string_protocol)
        )
        try:
            self._exec_interactive(su_message,
                                   self.error_recv_message)
            GlobalModule.EM_LOGGER.debug("Success exec command")
        except Exception as ex:
            GlobalModule.EM_LOGGER.warning(
                "211003 Protocol(CLI) Execution Error: %s", su_message)
            GlobalModule.EM_LOGGER.debug("Error exec command:%s" % (ex,))
            GlobalModule.EM_LOGGER.debug(
                "Traceback:%s" % (traceback.format_exc(),))
        GlobalModule.EM_LOGGER.debug("policy.d roleback complete")

    @decorater_log
    def _send_discard_changes(self, send_message=None):
        '''
        discard-changes for CumulusCLI(Sends messages for the connected object by using SSH)
        '''
        GlobalModule.EM_LOGGER.debug(
            "param command :\n%s" % (send_message,))
        discard_changes_message = []
        if self.is_operation_policy_d:
            discard_changes_message.extend(
                self._set_sudo_command("rm -fR /tmp/policy.d",
                                       self._recv_string_protocol)
            )
            discard_changes_message.extend(
                self._set_sudo_command("cp -fR /etc/cumulus/acl/policy.d /tmp",
                                       self._recv_string_protocol)
            )
        discard_changes_message.extend(
            [("net abort", self._recv_string_protocol)]
        )

        GlobalModule.EM_LOGGER.debug(
            "start exec command :\n%s" % (discard_changes_message,))
        try:
            output = self._exec_interactive(discard_changes_message,
                                            self.error_recv_message)
            GlobalModule.EM_LOGGER.debug("Success exec command")
            self.is_complete_discard_change = True
        except Exception as ex:
            GlobalModule.EM_LOGGER.warning(
                "211003 Protocol(CLI) Execution Error: %s", send_message)
            GlobalModule.EM_LOGGER.debug("Error exec command:%s" % (ex,))
            GlobalModule.EM_LOGGER.debug(
                "Traceback:%s" % (traceback.format_exc(),))
            raise
        return output

    @decorater_log
    def _send_confirmed_commit(self, send_message=None):
        '''
        confirmed-commit for CumulusCLI(Sends messages for the connected object by using SSH)
        '''
        GlobalModule.EM_LOGGER.debug(
            "param command :\n%s" % (send_message,))

        is_ok, timer_val = GlobalModule.EM_CONFIG.read_sys_common_conf(
            "Timer_confirmed-commit")
        if not is_ok:
            GlobalModule.EM_LOGGER.debug("read_sys_common NG")
            raise
        GlobalModule.EM_LOGGER.debug("read_sys_common OK")
        GlobalModule.EM_LOGGER.debug("return_value:%s", timer_val)
        timer_val = timer_val / 1000

        send_comm = []
        if self.is_operation_policy_d:
            send_comm.extend(
                self._set_sudo_command(self._COMM_ACLTOOL_INS,
                                       self._recv_string_protocol)
            )
        output = ""
        try:
            output += self._exec_interactive(send_comm,
                                             self.error_recv_message)
            output += self._exec_confirmed_commit(timer_val)
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
    def _send_commit(self, send_message=None):
        '''
        Commit for CumulusCLI(Sends messages for the connected object by using SSH)
        '''
        GlobalModule.EM_LOGGER.debug(
            "param command :\n%s" % (send_message,))
        try:
            output = self._exec_commit_against_confirm()
            GlobalModule.EM_LOGGER.debug("Success exec command")
            self._is_complete_commit = True
        except Exception as ex:
            GlobalModule.EM_LOGGER.warning(
                "211003 Protocol(CLI) Execution Error: %s", send_message)
            GlobalModule.EM_LOGGER.debug("Error exec command:%s" % (ex,))
            GlobalModule.EM_LOGGER.debug(
                "Traceback:%s" % (traceback.format_exc(),))
            raise
        return output

    @decorater_log
    def _exec_confirmed_commit(self, confirm_time=10):
        output = ""
        mes = ("net commit confirm %s" % (confirm_time,),
               "Press <ENTER> to confirm connectivity" +
               "|There are no pending changes")
        GlobalModule.EM_LOGGER.debug("send command :%s" % (mes,))
        output += self._send_command(self._ssh_shell, mes[0], mes[1])
        self._check_command_error(output,
                                  self.error_recv_message,
                                  self.non_error_recv_message)
        return output

    @decorater_log
    def _exec_commit_against_confirm(self):
        output = ""
        err_mess = list(self.error_recv_message)
        err_mess.append("rollback already happened")
        mes = ("\n", self._recv_string_protocol)
        GlobalModule.EM_LOGGER.debug("send command :%s" % (mes,))
        output += self._send_command(self._ssh_shell, mes[0], mes[1])
        self._check_command_error(output,
                                  err_mess,
                                  self.non_error_recv_message)
        return output

    @decorater_log
    def _set_sudo_command(self, send_command, recv_command):
        comm_list = []
        sudo_send_comm = "sudo -k {0}".format(send_command)
        comm_list.append((sudo_send_comm, "\[sudo\] password for cumulus:"))
        comm_list.append((self._password, recv_command))
        return comm_list
