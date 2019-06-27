#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: CgwshDriverCLIProtocol.py

import traceback
import GlobalModule
from EmCommonLog import decorater_log
from EmCommonLog import decorater_log_in_out
from EmCLIProtocolBase import EmCLIProtocol


class CgwshDriverCLIProtocol(EmCLIProtocol):
    '''
    Class of protocol processing part for CGW-SH driver(ASR,NVR)
    '''

    @decorater_log
    def __init__(self, error_recv_message=[], connected_recv_message="~"):
        super(CgwshDriverCLIProtocol, self).__init__(error_recv_message,
                                                     connected_recv_message)
        self.change_configuration_mode_comm = None
        self.exit_configuration_mode_comm = None
        self._is_mode_configuration = False
        self._is_send_chande_configuration = False
        self._is_configuration_effect = False

    @decorater_log_in_out
    def set_configuration_mode_command(self,
                                       change_configuration_mode_comm,
                                       exit_configuration_mode_comm):
        self.change_configuration_mode_comm = change_configuration_mode_comm
        self.exit_configuration_mode_comm = exit_configuration_mode_comm
        self._is_configuration_effect = True

    @decorater_log
    def _send_edit_config(self, send_message):
        '''
        edit-config for CLI (Message is set to destination in SSH connection)
        '''
        self._is_mode_configuration = False
        self._is_send_chande_configuration = False
        try:
            super_mtd = super(CgwshDriverCLIProtocol, self)
            return_val = super_mtd._send_edit_config(send_message)
        except Exception:
            if self._is_mode_configuration:
                self._exit_configuration_mode()
            raise
        return return_val

    @decorater_log
    def _exit_configuration_mode(self):
        '''
        Exit of configuration mode is forced.
        '''
        send_message = [self.exit_configuration_mode_comm]
        GlobalModule.EM_LOGGER.debug(
            "start exit command :\n%s" % (send_message,))
        try:
            self._exec_interactive(send_message, self.error_recv_message)
        except Exception as ex:
            GlobalModule.EM_LOGGER.debug("Error exit command:%s", ex)
            GlobalModule.EM_LOGGER.debug("Traceback:%s",
                                         traceback.format_exc())
        else:
            GlobalModule.EM_LOGGER.debug("Success configuration exit")
            self._is_mode_configuration = False

    @decorater_log
    def _send_command(self,
                      shell_obj,
                      send_message,
                      receive_keyword):
        '''
        CLI command list is sent to device during SSH connection.
        Argument:
            shell_obj : ssh object
            send_message : sendingmessage
            receive_keyword : received keyword
        Return value:
            received message
        '''
        if self._is_send_chande_configuration:
            self._is_mode_configuration = True
        self._is_send_chande_configuration = False

        super_mtd = super(CgwshDriverCLIProtocol, self)
        return_val = super_mtd._send_command(shell_obj,
                                             send_message,
                                             receive_keyword)
        if self._is_configuration_effect:
            conf_command = self.change_configuration_mode_comm[0]
            exit_command = self.exit_configuration_mode_comm[0]
            if send_message == conf_command:

                self._is_send_chande_configuration = True
            elif send_message == exit_command:

                self._is_mode_configuration = False
        return return_val
