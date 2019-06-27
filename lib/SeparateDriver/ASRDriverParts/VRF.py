#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: ASRDriverParts/VRF.py

'''
Part Module for ASR driver VRF configuration
'''
import GlobalModule
from EmCommonLog import decorater_log
from ASRDriverParts.ASRDriverConfigBase import ASRDriverConfigBase


class VRF(ASRDriverConfigBase):
    '''
    Part class for ASR driver VRF configuration
    '''
    @decorater_log
    def __init__(self,
                 vrf_name=None,
                 line_no=None,
                 nni_if_name=None,
                 nni_vlan_id=None):
        '''
        Constructor
        '''
        super(VRF, self).__init__()
        self.vrf_name = vrf_name
        self.line_no = line_no
        self.nni_if_name = nni_if_name
        self.nni_vlan_id = nni_vlan_id

    @decorater_log
    def output_add_command(self):
        '''
        Command line to add configuration is output.
        '''
        self._clear_command()
        parame = self._get_param()
        comm_txt = "vrf definition %(vrf_name)s"
        self._append_add_command(comm_txt, parame)
        comm_txt = "rd %(line_no)s%(nni_vlan_id)s:1"
        self._append_add_command(comm_txt, parame)
        self._append_add_command("address-family ipv4")
        comm_txt = "route-target export %(line_no)s%(nni_vlan_id)s:1"
        self._append_add_command(comm_txt, parame)
        comm_txt = "route-target import %(line_no)s%(nni_vlan_id)s:1"
        self._append_add_command(comm_txt, parame)
        self._append_add_command("exit-address-family")
        self._append_add_command("exit")
        GlobalModule.EM_LOGGER.debug(
            "vrf command = %s" % (self._tmp_add_command,))
        return self._tmp_add_command

    @decorater_log
    def output_del_command(self):
        '''
        Command line to delete configuration is output..
        '''
        self._clear_command()
        parame = self._get_param()
        comm_txt = "no vrf definition %(vrf_name)s"
        self._append_del_command(comm_txt, parame)
        GlobalModule.EM_LOGGER.debug(
            "vrf command = %s" % (self._tmp_del_command,))
        return self._tmp_del_command

    @decorater_log
    def _get_param(self):
        '''
        Parameter is acquired from attribute.(dict type)
        '''
        return {
            "vrf_name": self.vrf_name,
            "line_no": self.line_no,
            "nni_if_name": self.nni_if_name,
            "nni_vlan_id": self.nni_vlan_id,
        }
