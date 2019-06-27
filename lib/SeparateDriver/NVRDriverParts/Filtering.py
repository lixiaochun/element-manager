#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: NVRDriverParts/Filtering.py

'''
Parts module for MVR driver filtering configuration
'''
import GlobalModule
from EmCommonLog import decorater_log
from NVRDriverParts.NVRDriverConfigBase import NVRDriverConfigBase


class Filtering(NVRDriverConfigBase):
    '''
    Class for MVR driver filtering configuration
    '''
    @decorater_log
    def __init__(self):
        '''
        Costructor
        '''
        super(Filtering, self).__init__()

    @decorater_log
    def output_add_command(self):
        '''
        Command line for adding configuration is output.
        '''
        self._clear_command()
        self._append_add_command("ip filter 100 reject * 10.250.0.0/16 * *")
        self._append_add_command("ip filter 101 reject * 10.251.0.0/16 * *")
        self._append_add_command("ip filter 102 reject * 10.252.0.0/16 * *")
        self._append_add_command("ip filter 103 reject * 10.253.0.0/16 * *")
        self._append_add_command("ip filter 104 reject * 10.254.0.0/16 * *")
        self._append_add_command("ip filter 105 reject * 10.255.0.0/16 * *")
        self._append_add_command("ip filter 1000 pass * * * *")
        GlobalModule.EM_LOGGER.debug(
            "filtering command = %s" % (self._tmp_add_command,))
        return self._tmp_add_command

    @decorater_log
    def output_del_command(self):
        '''
        Command line for deleting configuration is output.
        '''
        self._clear_command()
        self._append_del_command("no ip filter 100")
        self._append_del_command("no ip filter 101")
        self._append_del_command("no ip filter 102")
        self._append_del_command("no ip filter 103")
        self._append_del_command("no ip filter 104")
        self._append_del_command("no ip filter 105")
        self._append_del_command("no ip filter 1000")
        GlobalModule.EM_LOGGER.debug(
            "default gateway command = %s" % (self._tmp_del_command,))
        return self._tmp_del_command
