#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: ASRDriverParts/BGP.py

'''
Parts module for ASR driver BGP cnfiguration
'''
import GlobalModule
from EmCommonLog import decorater_log
from ASRDriverParts.ASRDriverConfigBase import ASRDriverConfigBase


class BGP(ASRDriverConfigBase):
    '''
    Parts class for ASR driver BGP cnfiguration
    '''
    @decorater_log
    def __init__(self,
                 vrf_name=None,
                 ip_address=None,
                 nni_ip_address=None,
                 nni_vpn_gw=None):
        '''
        Costructor
        Argument:
            vrf_name : VRF nmae
            ip_address :   physical IP address
            nni_ip_address : IP address for NNI line
            nni_vpn_gw : VPN-GW for NWI
        '''
        super(BGP, self).__init__()
        self.vrf_name = vrf_name
        self.ip_address = ip_address
        self.nni_ip_address = nni_ip_address
        self.nni_vpn_gw = nni_vpn_gw

    @decorater_log
    def output_add_command(self):
        '''
        Command line to add configuration is output
        '''
        self._clear_command()
        parame = self._get_param()
        self._append_add_command("router bgp 65000")
        comm_txt = "address-family ipv4 vrf %(vrf_name)s"
        self._append_add_command(comm_txt, parame)
        comm_txt = "bgp router-id %(nni_ip_address)s"
        self._append_add_command(comm_txt, parame)
        self._append_add_command("redistribute connected")
        self._append_add_command("redistribute static")
        comm_txt = "neighbor %(ip_address)s remote-as 65000"
        self._append_add_command(comm_txt, parame)
        comm_txt = "neighbor %(ip_address)s activate"
        self._append_add_command(comm_txt, parame)
        comm_txt = "neighbor %(ip_address)s next-hop-self"
        self._append_add_command(comm_txt, parame)
        comm_txt = "neighbor %(ip_address)s soft-reconfiguration inbound"
        self._append_add_command(comm_txt, parame)
        comm_txt = "neighbor %(nni_vpn_gw)s remote-as 9598"
        self._append_add_command(comm_txt, parame)
        comm_txt = "neighbor %(nni_vpn_gw)s activate"
        self._append_add_command(comm_txt, parame)
        comm_txt = "neighbor %(nni_vpn_gw)s soft-reconfiguration inbound"
        self._append_add_command(comm_txt, parame)
        comm_txt = "neighbor %(nni_vpn_gw)s route-map BGP-MED-100 out"
        self._append_add_command(comm_txt, parame)
        self._append_add_command("default-information originate")
        self._append_add_command("exit-address-family")
        self._append_add_command("exit")
        GlobalModule.EM_LOGGER.debug(
            "bgp command = %s" % (self._tmp_add_command,))
        return self._tmp_add_command

    @decorater_log
    def _get_param(self):
        '''
        Parameter is acquired from attribute.(dict type)
        '''
        return {
            "vrf_name": self.vrf_name,
            "ip_address": self.ip_address,
            "nni_ip_address": self.nni_ip_address,
            "nni_vpn_gw": self.nni_vpn_gw,
        }
