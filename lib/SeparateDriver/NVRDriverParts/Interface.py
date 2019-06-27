#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: NVRDriverParts/Interface.py

'''
Parts module for NWR driver interface configuration
'''
import GlobalModule
from EmCommonLog import decorater_log
from NVRDriverParts.NVRDriverConfigBase import NVRDriverConfigBase


class Interface(NVRDriverConfigBase):
    '''
    Parts class for NWR driver interface configuration
    '''
    @decorater_log
    def __init__(self,
                 vlan_id=None,
                 ip_address=None,
                 subnet_mask=None):
        '''
        Costructor
        '''
        super(Interface, self).__init__()
        self.vlan_id = vlan_id
        self.ip_address = ip_address
        self.subnet_mask = subnet_mask

    @decorater_log
    def output_add_command(self):
        '''
        Command line to add configuration is output.
        '''
        self._clear_command()
        parame = self._get_param()
        comm_txt = "vlan lan1/2 802.1q vid=%(vlan_id)s name=user"
        self._append_add_command(comm_txt, parame)
        comm_txt = "ip lan1/2 address %(ip_address)s%(subnet_mask)s"
        self._append_add_command(comm_txt, parame)
        self._append_add_command(
            "ip lan1/2 secure filter in 100 101 102 103 104 105 1000")
        self._append_add_command(
            "ip lan1/2 secure filter out 100 101 102 103 104 105 1000")
        self._append_add_command("ip lan1/2 tcp mss limit 1414")
        GlobalModule.EM_LOGGER.debug(
            "Interface command = %s" % (self._tmp_add_command,))
        return self._tmp_add_command

    @decorater_log
    def output_del_command(self):
        '''
        Command line to delete configuration is output.
        '''
        self._clear_command()
        self._append_del_command("no vlan lan1/2 802.1q")
        self._append_del_command("no ip lan1/2 address")
        self._append_del_command("no ip lan1/2 secure filter in")
        self._append_del_command("no ip lan1/2 secure filter out")
        self._append_del_command("no ip lan1/2 tcp mss limit")
        GlobalModule.EM_LOGGER.debug(
            "Interface command = %s" % (self._tmp_del_command,))
        return self._tmp_del_command

    @decorater_log
    def _get_param(self):
        '''
        Parameter is acquired from attribute.(dict type)
        '''
        return {
            "vlan_id": self.vlan_id,
            "ip_address": self.ip_address,
            "subnet_mask": self.subnet_mask
        }
