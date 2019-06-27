#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: NVRDriverCLIProtocol.py

import traceback
import re
import GlobalModule
from EmCommonLog import decorater_log
from CgwshDriverCLIProtocol import CgwshDriverCLIProtocol


class NVRDriverCLIProtocol(CgwshDriverCLIProtocol):
    '''
    Class for processing NVR driver protocol(CLI)
    '''

    @decorater_log
    def __init__(self, error_recv_message=[], connected_recv_message="~"):
        super(NVRDriverCLIProtocol, self).__init__(error_recv_message,
                                                   connected_recv_message)

    @decorater_log
    def _exit_configuration_mode(self):
        '''
        Release of configuration mode is forced.
        '''
        
        re_txt_save_conf = "Save new configuration \? \(Y/N\)"

        send_message = [("quit", "{0}|{1}".format(">", re_txt_save_conf))]
        GlobalModule.EM_LOGGER.debug(
            "start exit command :\n%s" % (send_message,))
        try:
            output = self._exec_interactive(send_message,
                                            self.error_recv_message)
            if re.search(re_txt_save_conf, output):
                self._send_command_no_save()
        except Exception as ex:
            GlobalModule.EM_LOGGER.debug("Error exit command:%s", ex)
            GlobalModule.EM_LOGGER.debug("Traceback:%s",
                                         traceback.format_exc())
        else:
            GlobalModule.EM_LOGGER.debug("Success configuration exit")
            self._is_mode_configuration = False

    @decorater_log
    def _send_command_no_save(self):
        '''
        Save new configuration ? n is set as reponse to question(Y/N).
        Return value:
            Received message
        '''
        GlobalModule.EM_LOGGER.debug(
            "Send n for 'Save new configuration ? (Y/N)'")
        shell_obj = self._ssh_shell
        send_message = "n"
        receive_keyword = ">"
        shell_obj.send(send_message)
        return self._recv_message(shell_obj, receive_keyword)
