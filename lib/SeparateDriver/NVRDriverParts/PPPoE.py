#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: NVRDriverParts/PPPoE.py

'''
Parts module for NVR driver PPPoE configuration
'''
import GlobalModule
from EmCommonLog import decorater_log
from NVRDriverParts.NVRDriverConfigBase import NVRDriverConfigBase


class PPPoE(NVRDriverConfigBase):
    '''
    Parts class NVR driver PPPoE configuration
    '''
    @decorater_log
    def __init__(self,
                 pp_no=None,
                 username=None,
                 password=None,
                 tenant=None):
        '''
        Constructor
        '''
        super(PPPoE, self).__init__()
        self.pp_no = pp_no
        self.username = username
        self.password = password
        self.tenant = tenant

    @decorater_log
    def output_add_command(self):
        '''
        Command line to add configuration is output.
        '''
        self._clear_command()
        parame = self._get_param()
        comm_txt = "pp select %(pp_no)s"
        self._append_add_command(comm_txt, parame)
        self._append_add_command(
            "pp keepalive interval 30 retry-interval=30 count=12")
        self._append_add_command("pp always-on on")
        self._append_add_command("pppoe use onu1")
        self._append_add_command("pppoe auto disconnect off")
        self._append_add_command("pp auth accept pap chap")
        comm_txt = "pp auth myname %(username)s@%(tenant)s %(password)s"
        self._append_add_command(comm_txt, parame)
        self._append_add_command("ppp lcp mru on 1454")
        self._append_add_command("ppp ipcp ipaddress on")
        self._append_add_command("ppp ipcp msext on")
        self._append_add_command("ppp ccp type none")
        self._append_add_command(
            "ip pp secure filter in 100 101 102 103 104 105 1000")
        self._append_add_command(
            "ip pp secure filter out 100 101 102 103 104 105 1000")
        comm_txt = "pp enable %(pp_no)s"
        self._append_add_command(comm_txt, parame)
        self._append_add_command("pp select none")
        GlobalModule.EM_LOGGER.debug(
            "PPPoE command = %s" % (self._tmp_add_command,))
        return self._tmp_add_command

    @decorater_log
    def output_del_command(self):
        '''
        Command line to delete configuration is output.
        '''
        self._clear_command()
        parame = self._get_param()
        comm_txt = "pp select %(pp_no)s"
        self._append_del_command(comm_txt, parame)
        comm_txt = "pp disable %(pp_no)s"
        self._append_del_command(comm_txt, parame)
        self._append_del_command("no pp keepalive interval")
        self._append_del_command("no pp always-on")
        self._append_del_command("no pppoe use")
        self._append_del_command("no pppoe auto disconnect")
        self._append_del_command("no pp auth accept")
        self._append_del_command("no pp auth myname")
        self._append_del_command("no ppp lcp mru")
        self._append_del_command("no ppp ipcp ipaddress")
        self._append_del_command("no ppp ipcp msext on")
        self._append_del_command("no ppp ccp type none")
        self._append_del_command("no ip pp secure filter in")
        self._append_del_command("no ip pp secure filter out")
        self._append_del_command("pp select none")
        GlobalModule.EM_LOGGER.debug(
            "PPPoE command = %s" % (self._tmp_del_command,))
        return self._tmp_del_command

    @decorater_log
    def _get_param(self):
        '''
        Parameter is acquired from attribute.(dict type)
        '''
        return {
            "pp_no": self.pp_no,
            "username": self.username,
            "password": self.password,
            "tenant": self.tenant,
        }
