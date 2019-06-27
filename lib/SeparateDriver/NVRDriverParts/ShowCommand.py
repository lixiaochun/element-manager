#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: NVRDriverParts/ShowCommand.py

'''
Module for setting NVR driver show-command
'''
import GlobalModule
from EmCommonLog import decorater_log
from NVRDriverParts.NVRDriverConfigBase import NVRDriverConfigBase


class ShowCommand(NVRDriverConfigBase):
    '''
    Part class for setting NVR driver show-command
    '''
    @decorater_log
    def __init__(self, device_name=None):
        '''
        Constructor
        '''
        super(ShowCommand, self).__init__()
        self.device_name = device_name
        self.default_res_mes = ">"

    @decorater_log
    def output_add_command(self):
        '''
        Added Command line is output.
        '''
        self._clear_command()
        self._append_add_command("console columns 200")
        self._append_add_command("show config")
        self._append_add_command("console columns 80")
        GlobalModule.EM_LOGGER.debug(
            "show command = %s" % (self._tmp_add_command,))
        return self._tmp_add_command
