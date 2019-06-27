#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: CgwshDeviceDriverSetParameterECDB.py

'''
Parameter module for Cgwsh driver configuration
'''
import GlobalModule
from EmCommonLog import decorater_log
from DriverSetParameterECDB import DriverSetParameterECDB


class CgwshDeviceDriverSetParameterECDB(DriverSetParameterECDB):
    '''
    Parameter class for Cgwsh driver configuration
    '''

    @decorater_log
    def __init__(self,
                 device_name=None,
                 ec_message=None,
                 db_info=None):
        '''
        Constructor
        '''
        super(CgwshDeviceDriverSetParameterECDB, self).__init__(device_name,
                                                                ec_message,
                                                                db_info)
        self.ec_message = self.ec_message["device"]

    @decorater_log
    def get_service_info(self):
        '''
        Service information is acquired.
        '''
        pass

    @decorater_log
    def get_management_info(self):
        '''
        Management information is acquired.
        '''
        get_info = {}
        get_info["device_name"] = self.ec_message.get("name")
        GlobalModule.EM_LOGGER.debug("get management_info = %s" % (get_info,))
        return get_info

    @decorater_log
    def get_static_route_info(self):
        '''
        Static route information is acquired.
        acquired dict:
        {
            static_route:[{
                ip_address:str,
                subnet_mask:str,
                gateway_address:str
            }]
        }
        '''
        get_info = {}
        tmp_list = []
        routes = self.ec_message.get("serviceInfo", {}).get("staticRoute", ())
        for route in routes:
            tmp_item = {}
            tmp_item["ip_address"] = route.get("ipAddress")
            tmp_item["subnet_mask"] = route.get("subnetMask")
            tmp_item["gateway_address"] = route.get("gatewayIpAddress")
            tmp_list.append(tmp_item)
        get_info["static_route"] = tmp_list
        GlobalModule.EM_LOGGER.debug("get static_route = %s" % (get_info,))
        return get_info

    @decorater_log
    def get_tunnel_if_info(self):
        '''
        Tunnel interface information is acquired.
        acquired dict:
        {
            tunnel_if:[{
                vrf_name:str,
                if_name:str,
                uni_if_name:str,
                uni_vlan_id:str,
                tunnel_source:str,
            }]
        }
        '''
        get_info = {}
        tmp_list = []
        tunnel_uni = self.ec_message.get("serviceInfo", {}).get("uni", ())
        tunnel_officeInfo = self.ec_message.get(
            "serviceInfo", {}).get("officeInfo", ())
        vrf_name = tunnel_uni.get("vrfName")
        uni_if_name = tunnel_uni.get("ifName")
        uni_vlan_id = tunnel_uni.get("vlanId")
        for tunnel in tunnel_officeInfo:
            tmp_item = {}
            tmp_item["vrf_name"] = vrf_name
            tmp_item["if_name"] = tunnel.get("tunnelIfName")
            tmp_item["uni_if_name"] = uni_if_name
            tmp_item["uni_vlan_id"] = uni_vlan_id
            tmp_item["tunnel_source"] = tunnel.get(
                "tunnelSrcIpAddress")
            tmp_list.append(tmp_item)
        get_info["tunnel_if"] = tmp_list
        GlobalModule.EM_LOGGER.debug("get tunnel_if = %s" % (get_info,))
        return get_info

    @decorater_log
    def get_pppoe_info(self):
        '''
        PPPoE information is acquired.
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
        get_info = {}
        tmp_list = []
        ppp_infos = self.ec_message.get("serviceInfo", {}).get("pppInfo", ())
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
