#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: NVRSetParameterECDB.py

'''
NWR driver configuration parameter module for company Y
'''
import GlobalModule
from EmCommonLog import decorater_log
from CgwshDeviceDriverSetParameterECDB import CgwshDeviceDriverSetParameterECDB


class NVRSetParameterECDB(CgwshDeviceDriverSetParameterECDB):
    '''
    NWR driver configuration parameter class for company Y
    '''
    @decorater_log
    def __init__(self,
                 device_name=None,
                 ec_message=None,
                 db_info=None):
        '''
        Constructor
        '''
        super(NVRSetParameterECDB, self).__init__(device_name,
                                                  ec_message,
                                                  db_info)

    @decorater_log
    def get_service_info(self):
        '''
        Service information is aquired(except for static route/default gateway)
        '''
        get_info = {}
        get_info.update(self._get_if_data())
        get_info.update(self._get_pppoe())
        GlobalModule.EM_LOGGER.debug("get nvr service_info = %s" % (get_info,))
        return get_info

    @decorater_log
    def get_static_route_info(self):
        '''
        Static route information is acquired.
        acquired dict:
        {
            static_route:{
                ip_address:str,
                subnet_mask:str,
                gateway_address:str
            },
            default_gateway:str

        }
        '''
        get_info = super(NVRSetParameterECDB, self).get_static_route_info()
        get_info.update(self._get_default_gateway())
        GlobalModule.EM_LOGGER.debug("get nvr static_route = %s" % (get_info,))
        return get_info

    @decorater_log
    def get_pppoe_info(self):
        '''
        PPPoE information is aquired.
        acquired dict:
        {
            pppoe:[{
                username:str,
                password:str,
                tenant:str,
                pp_no:str
            }]
        }
        '''
        get_info = self._get_pppoe()
        return get_info

    @decorater_log
    def get_adminstrator_password(self):
        '''
        Administrator password is aquired.
        '''
        return self.db_info.get("administrator_password")

    @decorater_log
    def _get_default_gateway(self):
        '''
        Default gateway information is acquired.
        acquired dict: {default_gateway:str}
        '''
        tmp = self.ec_message.get("serviceInfo", {}).get("defaultGateway")
        return {"default_gateway": tmp}

    @decorater_log
    def _get_if_data(self):
        '''
        IF information is aquired.
        acquired dict :
        {
            interface;{
                vlan_id:str,
                ip_address:str,
                subnet_mask:str,
            }
        }
        '''
        get_info = {}
        svs_info = self.ec_message.get("serviceInfo", {})
        tmp_item = {}
        tmp_item["vlan_id"] = svs_info.get("vlanId")
        tmp_item["ip_address"] = svs_info.get("ipAddress")
        tmp_item["subnet_mask"] = svs_info.get("subnetMask")
        get_info["interface"] = tmp_item
        GlobalModule.EM_LOGGER.debug("get nvr if_info = %s" % (get_info,))
        return get_info

    @decorater_log
    def _get_pppoe(self):
        '''
        PPPoE information is aquired.
        acquired dict :
        {
            pppoe:[{
                username:str,
                password:str,
                tenant:str,
                pp_no:str
            }]
        }
        '''
        get_info = {}
        ppp_infos = self.ec_message.get("serviceInfo", {}).get("pppInfo", [])
        tmp_list = []
        for ppp_info in ppp_infos:
            tmp_item = {}
            tmp_item["username"] = ppp_info.get("connectionId")
            tmp_item["password"] = ppp_info.get("connectionPassword")
            tmp_item["tenant"] = ppp_info.get("corporationId")
            tmp_item["pp_no"] = ppp_info.get("ppId")
            tmp_list.append(tmp_item)
        get_info["pppoe"] = tmp_list
        GlobalModule.EM_LOGGER.debug("get pppoe = %s" % (get_info,))
        return get_info
