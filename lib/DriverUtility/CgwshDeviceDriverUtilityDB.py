#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: CgwshDeviceDriverUtilityDB.py

'''
Module for Cgwsh driver utility(DB)
'''
import GlobalModule
from EmCommonLog import decorater_log
from EmDriverCommonUtilityDB import EmDriverCommonUtilityDB


class CgwshDeviceDriverUtilityDB(EmDriverCommonUtilityDB):
    '''
    Class for Cgwsh driver utility(DB)
    '''
    fvw_services = (GlobalModule.SERVICE_CGWSH_SERVICE_MANAGEMENT,
                    GlobalModule.SERVICE_CGWSH_CUSTOMER_UNI_ROUTE,
                    GlobalModule.SERVICE_CGWSH_UNI_ROUTE,
                    GlobalModule.SERVICE_CGWSH_PPP_SESSION,
                    GlobalModule.SERVICE_CGWSH_TUNNEL_SESSION,
                    )

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''
        super(CgwshDeviceDriverUtilityDB, self).__init__()

    @decorater_log
    def read_administrator_password(self, device_name, service_name):
        '''
        administrator password is aquired.
        '''
        if service_name not in self.fvw_services:
            GlobalModule.EM_LOGGER.warning(
                "1 213001 Service Classification Error")
            return False, None
        get_method = (
            GlobalModule.DB_CONTROL.read_nvr_administrator_password_info)
        is_ok, tmp_row = get_method(device_name)
        if not is_ok:
            GlobalModule.EM_LOGGER.warning("2 213002 Get Information Error")
            return False, None
        ret_val = None
        if tmp_row:
            password = tmp_row[0]["administrator_password"]
            ret_val = {"administrator_password": password}
        GlobalModule.EM_LOGGER.debug("get password = %s", ret_val)
        return True, ret_val
