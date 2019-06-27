#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: ASRDriverParts/UNIInterface.py

'''
Parts Module for ASR driver UNI interface configuraton
'''
import GlobalModule
from EmCommonLog import decorater_log
from ASRDriverParts.InterfaceBase import InterfaceBase


class UNIInterface(InterfaceBase):
    '''
    Parts class for ASR driver UNI interface configuraton
    '''
    @decorater_log
    def __init__(self,
                 vrf_name=None,
                 if_name=None,
                 vlan_id=None,
                 ip_address=None,
                 subnet_mask=None,
                 vip_ip_address=None,
                 hsrp_id=None,
                 mtu=None,
                 is_active=True):
        '''
        Costructor
        '''
        super(UNIInterface, self).__init__(vrf_name=vrf_name,
                                           if_name=if_name)
        self.vlan_id = vlan_id
        self.ip_address = ip_address
        self.subnet_mask = subnet_mask
        self.vip_ip_address = vip_ip_address
        self.hsrp_id = hsrp_id
        self.mtu = mtu
        self.is_active = is_active

    @decorater_log
    def output_add_command(self):
        '''
        Command line to add configuration is output.
        '''
        parame = self._get_param()
        self._interface_common_start()
        self._append_add_command("standby version 2")
        comm_txt = "standby %(hsrp_id)s ip %(vip_ip_address)s"
        self._append_add_command(comm_txt, parame)
        if self.is_active:
            comm_txt = "standby %(hsrp_id)s priority 105"
            self._append_add_command(comm_txt, parame)
        comm_txt = "standby %(hsrp_id)s preempt"
        self._append_add_command(comm_txt, parame)
        comm_txt = "ip mtu %(mtu)s"
        self._append_add_command(comm_txt, parame)
        self._interface_common_end()
        GlobalModule.EM_LOGGER.debug(
            "uni if command = %s" % (self._tmp_add_command,))
        return self._tmp_add_command

    @decorater_log
    def _get_param(self):
        '''
        Parameter is acquired from attribute.(dict type)
        '''
        tmp_param = super(UNIInterface, self)._get_param()
        tmp_param.update(
            {
                "vlan_id": self.vlan_id,
                "ip_address": self.ip_address,
                "subnet_mask": self.subnet_mask,
                "vip_ip_address": self.vip_ip_address,
                "hsrp_id": self.hsrp_id,
                "mtu": self.mtu,
            }
        )
        return tmp_param
