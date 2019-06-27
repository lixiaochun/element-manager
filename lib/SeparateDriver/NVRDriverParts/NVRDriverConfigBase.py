#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: NVRDriverParts/NVRDriverConfigBase.py

'''
Parts module for NVR driver configuration
'''
from EmCommonLog import decorater_log


class NVRDriverConfigBase(object):
    '''
    Class for NVR driver configuration
    '''
    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''
        self.default_res_mes = "#"
        self._tmp_add_command = []
        self._tmp_del_command = []
        self._comm_param = None

    @decorater_log
    def output_add_command(self):
        '''
        Command line for adding configuration is output.
        '''
        return []

    @decorater_log
    def output_del_command(self):
        '''
        Command line for deleting configuration is output.
        '''
        return []

    def _append_add_command(self, command=None, com_param=None, resp_mes=None):
        '''
        Command to be added is appended.
        '''
        return self._set_command(
            self._tmp_add_command, command, com_param, resp_mes)

    def _append_del_command(self, command=None, com_param=None, resp_mes=None):
        '''
        Command to be deleted is appended.
        '''
        return self._set_command(
            self._tmp_del_command, command, com_param, resp_mes)

    def _set_command(self,
                     set_list,
                     command=None,
                     com_param=None,
                     resp_mes=None):
        '''
        Command is set.
        '''
        if resp_mes is None:
            resp_mes = self.default_res_mes
        if com_param:
            comm = (command % com_param, resp_mes)
        else:
            comm = (command, resp_mes)
        set_list.append(comm)
        return comm

    def _clear_command(self):
        '''
        All of command are cleared.
        '''
        self._tmp_add_command = []
        self._tmp_del_command = []
