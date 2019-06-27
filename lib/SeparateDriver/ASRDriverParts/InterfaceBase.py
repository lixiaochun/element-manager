#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: ASRDriverParts/InterfaceBase.py

'''
Parts module for ASR driver interface base
'''
import GlobalModule
from EmCommonLog import decorater_log
from ASRDriverParts.ASRDriverConfigBase import ASRDriverConfigBase


class InterfaceBase(ASRDriverConfigBase):
    '''
    Parts class for ASR driver interface base
    '''
    @decorater_log
    def __init__(self,
                 vrf_name=None,
                 if_name=None):
        '''
        Costructor
        '''
        super(InterfaceBase, self).__init__()
        self.vrf_name = vrf_name
        self.if_name = if_name

    @decorater_log
    def output_del_command(self):
        '''
        Command line to delete configuration is output.
        '''
        self._clear_command()
        self._interface_common_if_shutdown()
        GlobalModule.EM_LOGGER.debug(
            "if command = %s" % (self._tmp_del_command,))
        return self._tmp_del_command

    @decorater_log
    def _interface_common_start(self):
        parame = self._get_param()
        comm_txt = "interface %(if_name)s.%(vlan_id)s"
        self._append_add_command(comm_txt, parame)
        comm_txt = "encapsulation dot1Q %(vlan_id)s"
        self._append_add_command(comm_txt, parame)
        comm_txt = "vrf forwarding %(vrf_name)s"
        self._append_add_command(comm_txt, parame)
        comm_txt = "ip address %(ip_address)s %(subnet_mask)s"
        self._append_add_command(comm_txt, parame)

    @decorater_log
    def _interface_common_end(self):
        self._append_add_command("no shutdown")
        self._append_add_command("exit")

    @decorater_log
    def _interface_common_if_shutdown(self):
        parame = self._get_param()
        if parame.get("vlan_id"):
            if_command = "interface %(if_name)s.%(vlan_id)s"
        else:
            if_command = "interface %(if_name)s"
        self._append_del_command(if_command, parame)
        self._append_del_command("shutdown")
        self._append_del_command("exit")
        self._append_del_command("no " + if_command, parame)

    @decorater_log
    def _get_param(self):
        '''
        Parameter is acquired from attribute(dict type).
        '''
        return {
            "vrf_name": self.vrf_name,
            "if_name": self.if_name,
        }
