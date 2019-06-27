#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: ASRDriverParts/StaticRoute.py

'''
Parts module for ASR driver static route configuration
'''
import GlobalModule
from EmCommonLog import decorater_log
from ASRDriverParts.ASRDriverConfigBase import ASRDriverConfigBase


class StaticRoute(ASRDriverConfigBase):
    '''
    Parts class for ASR driver static route configuration
    '''
    @decorater_log
    def __init__(self,
                 vrf_name=None,
                 ip_address=None,
                 subnet_mask=None,
                 gateway_address=None):
        '''
        Costructor
        '''
        super(StaticRoute, self).__init__()
        self.vrf_name = vrf_name
        self.ip_address = ip_address
        self.subnet_mask = subnet_mask
        self.gateway_address = gateway_address
        self._ip_route_comm = ("ip route vrf %(vrf_name)s %(ip_address)s " +
                               "%(subnet_mask)s %(gateway_address)s")

    @decorater_log
    def output_add_command(self):
        '''
        Command line to add configuration is output.
        '''
        self._clear_command()
        parame = self._get_param()
        self._append_add_command(self._ip_route_comm, parame)
        GlobalModule.EM_LOGGER.debug(
            "static_route command = %s" % (self._tmp_add_command,))
        return self._tmp_add_command

    @decorater_log
    def output_del_command(self):
        '''
        Command line to add configuration is output.
        '''
        self._clear_command()
        parame = self._get_param()
        self._append_del_command("no " + self._ip_route_comm, parame)
        GlobalModule.EM_LOGGER.debug(
            "static_route command = %s" % (self._tmp_del_command,))
        return self._tmp_del_command

    @decorater_log
    def _get_param(self):
        '''
        Parameter is acquired from attribute.(dict type)
        '''
        return {
            "vrf_name": self.vrf_name,
            "ip_address": self.ip_address,
            "subnet_mask": self.subnet_mask,
            "gateway_address": self.gateway_address,
        }
