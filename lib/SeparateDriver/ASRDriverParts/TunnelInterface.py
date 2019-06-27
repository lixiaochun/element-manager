#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: ASRDriverParts/TunnelInterface.py

'''
Parts module for ASR driver tunnel interface configuration
'''
import GlobalModule
from EmCommonLog import decorater_log
from ASRDriverParts.InterfaceBase import InterfaceBase


class TunnelInterface(InterfaceBase):
    '''
    Parts Class for ASR driver tunnel interface configuration
    '''
    @decorater_log
    def __init__(self,
                 vrf_name=None,
                 if_name=None,
                 uni_if_name=None,
                 uni_vlan_id=None,
                 tunnel_source=None):
        '''
        Costructor
        '''
        super(TunnelInterface, self).__init__(vrf_name=vrf_name,
                                              if_name=if_name)
        self.uni_if_name = uni_if_name
        self.uni_vlan_id = uni_vlan_id
        self.tunnel_source = tunnel_source

    @decorater_log
    def output_add_command(self):
        '''
        Command line to add configuration is output.
        '''
        parame = self._get_param()
        comm_txt = "interface %(if_name)s"
        self._append_add_command(comm_txt, parame)
        comm_txt = "vrf forwarding %(vrf_name)s"
        self._append_add_command(comm_txt, parame)
        comm_txt = "ip unnumbered %(uni_if_name)s.%(uni_vlan_id)s"
        self._append_add_command(comm_txt, parame)
        self._append_add_command("load-interval 30")
        comm_txt = "tunnel source %(uni_if_name)s.%(uni_vlan_id)s"
        self._append_add_command(comm_txt, parame)
        self._append_add_command("tunnel mode ipip")
        comm_txt = "tunnel destination %(tunnel_source)s"
        self._append_add_command(comm_txt, parame)
        comm_txt = "tunnel vrf %(vrf_name)s"
        self._append_add_command(comm_txt, parame)
        self._interface_common_end()
        GlobalModule.EM_LOGGER.debug(
            "tunnel if command = %s" % (self._tmp_add_command,))
        return self._tmp_add_command

    @decorater_log
    def _get_param(self):
        '''
        Parameter is acquired from attribute.(dict type)
        '''
        tmp_param = super(TunnelInterface, self)._get_param()
        tmp_param.update(
            {
                "uni_if_name": self.uni_if_name,
                "uni_vlan_id": self.uni_vlan_id,
                "tunnel_source": self.tunnel_source,
            }
        )
        return tmp_param
