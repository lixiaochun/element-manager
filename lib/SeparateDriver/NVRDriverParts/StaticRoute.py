#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: NVRDriverParts/StaticRoute.py

'''
Parts module for NVR driver Static Route configuration
'''
import GlobalModule
from EmCommonLog import decorater_log
from NVRDriverParts.NVRDriverConfigBase import NVRDriverConfigBase


class StaticRoute(NVRDriverConfigBase):
    '''
    Parts class NVR driver Static Route configuration
    '''
    @decorater_log
    def __init__(self,
                 vrf_name=None,
                 ip_address=None,
                 subnet_mask=None,
                 gateway_address=None):
        '''
        Constructor
        '''
        super(StaticRoute, self).__init__()
        self.vrf_name = vrf_name
        self.ip_address = ip_address
        self.subnet_mask = subnet_mask
        self.gateway_address = gateway_address
        self._max_subnet_mask = "/32"

    @decorater_log
    def output_add_command(self):
        '''
        Command line to add configuration is output.
        '''
        self._clear_command()
        self._set_ip_route()
        GlobalModule.EM_LOGGER.debug(
            "static_route command = %s" % (self._tmp_add_command,))
        return self._tmp_add_command

    @decorater_log
    def output_del_command(self):
        '''
        Command line to delete configuration is output.
        '''
        self._clear_command()
        self._set_ip_route(is_delete=True)
        GlobalModule.EM_LOGGER.debug(
            "static route command = %s" % (self._tmp_del_command,))
        return self._tmp_del_command

    @decorater_log
    def _set_ip_route(self, is_delete=False):
        parame = self._get_param()
        if self.subnet_mask == self._max_subnet_mask:
            comm_txt = "ip route %(ip_address)s gateway %(gateway_address)s"
        else:
            comm_txt = ("ip route %(ip_address)s%(subnet_mask)s " +
                        "gateway %(gateway_address)s")
        if is_delete:
            comm_method = self._append_del_command
            comm_txt = "no " + comm_txt
        else:
            comm_method = self._append_add_command
        comm_method(comm_txt, parame)

    @decorater_log
    def _get_param(self):
        '''
        Parameter is acquired from attribute.(dict type)
        '''
        return {
            "ip_address": self.ip_address,
            "subnet_mask": self.subnet_mask,
            "gateway_address": self.gateway_address,
        }
