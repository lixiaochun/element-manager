#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: NVRDriverParts/DefaultGateway.py

'''
Parts module for NVR driver default gateway configuration.
'''
import GlobalModule
from EmCommonLog import decorater_log
from NVRDriverParts.NVRDriverConfigBase import NVRDriverConfigBase


class DefaultGateway(NVRDriverConfigBase):
    '''
    Parts class for NVR driver default gateway configuration.
    '''
    @decorater_log
    def __init__(self, default_gateway=None):
        '''
        Costructor
        '''
        super(DefaultGateway, self).__init__()
        self.default_gateway = default_gateway

    @decorater_log
    def output_add_command(self):
        '''
        Command line for adding configuration is output.
        '''
        self._clear_command()
        parame = self._get_param()
        comm_txt = "ip route default gateway %(default_gateway)s"
        self._append_add_command(comm_txt, parame)
        GlobalModule.EM_LOGGER.debug(
            "default gateway command = %s" % (self._tmp_add_command,))
        return self._tmp_add_command

    @decorater_log
    def output_del_command(self):
        '''
        Command line for deleting configuration is output.
        '''
        self._clear_command()
        parame = self._get_param()
        comm_txt = "no ip route default gateway %(default_gateway)s"
        self._append_del_command(comm_txt, parame)
        GlobalModule.EM_LOGGER.debug(
            "default gateway command = %s" % (self._tmp_del_command,))
        return self._tmp_del_command

    @decorater_log
    def _get_param(self):
        '''
        Parameter is aquired from attribute.(dict type)
        '''
        return {
            "default_gateway": self.default_gateway,
        }
