#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: ASRDriverParts/ShowCommand.py

'''
Part module for ASR driver show-comma
'''
import GlobalModule
from EmCommonLog import decorater_log
from ASRDriverParts.ASRDriverConfigBase import ASRDriverConfigBase


class ShowCommand(ASRDriverConfigBase):
    '''
    Part class for setting ASR driver show-command
    '''
    @decorater_log
    def __init__(self, device_name=None, is_get_startup=True):
        '''
        Constructor
        '''
        super(ShowCommand, self).__init__()
        self.device_name = device_name
        self.show_resp_mes = self.device_name + self.default_res_mes
        self.is_get_startup = is_get_startup

    @decorater_log
    def output_add_command(self):
        '''
        Command line to add configuration is output.
        '''
        self._clear_command()
        self._append_add_command("show running-config",
                                 resp_mes=self.show_resp_mes)
        if self.is_get_startup:
            self._append_add_command("show startup-config",
                                     resp_mes=self.show_resp_mes)
        GlobalModule.EM_LOGGER.debug(
            "show command = %s" % (self._tmp_add_command,))
        return self._tmp_add_command
