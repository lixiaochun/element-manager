#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: ASRDriverParts/UNOInterface.py

'''
Parts Module for ASRdriver UNO interface configuration
'''
import GlobalModule
from EmCommonLog import decorater_log
from ASRDriverParts.InterfaceBase import InterfaceBase


class UNOInterface(InterfaceBase):
    '''
    Parts class for ASRdriver UNO interface configuration
    '''
    @decorater_log
    def __init__(self,
                 vrf_name=None,
                 if_name=None,
                 vlan_id=None,
                 ip_address=None,
                 subnet_mask=None,
                 mss=None):
        '''
        Constructor
        '''
        super(UNOInterface, self).__init__(vrf_name=vrf_name,
                                           if_name=if_name)
        self.vlan_id = vlan_id
        self.ip_address = ip_address
        self.subnet_mask = subnet_mask
        self.mss = mss

    @decorater_log
    def output_add_command(self):
        '''
        Command line to add configuration is output.
        '''
        parame = self._get_param()
        self._interface_common_start()
        comm_txt = "ip tcp adjust-mss %(mss)s"
        self._append_add_command(comm_txt, parame)
        self._interface_common_end()
        GlobalModule.EM_LOGGER.debug(
            "uno if command = %s" % (self._tmp_add_command,))
        return self._tmp_add_command

    @decorater_log
    def _get_param(self):
        '''
        Parameter is acquired from attribute.(dict type)
        '''
        tmp_param = super(UNOInterface, self)._get_param()
        tmp_param.update(
            {
                "vlan_id": self.vlan_id,
                "ip_address": self.ip_address,
                "subnet_mask": self.subnet_mask,
                "mss": self.mss,
            }
        )
        return tmp_param
