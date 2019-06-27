#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: ASRSetParameterECDB.py

'''
Parameter Module for ASR driver configuration for company C.
'''
import GlobalModule
from EmCommonLog import decorater_log
from CgwshDeviceDriverSetParameterECDB import CgwshDeviceDriverSetParameterECDB


class ASRSetParameterECDB(CgwshDeviceDriverSetParameterECDB):
    '''
    Parameter Class for ASR driver configuration for company C.
    '''

    @decorater_log
    def __init__(self,
                 device_name=None,
                 ec_message=None,
                 db_info=None):
        '''
        Constructor
        '''
        super(ASRSetParameterECDB, self).__init__(device_name,
                                                  ec_message,
                                                  db_info)

    @decorater_log
    def get_service_info(self):
        '''
        Service information is acquired.(except for static route)
        '''
        get_info = {}
        get_info.update(self._get_vrf_data())
        get_info.update(self._get_uno_if_data())
        get_info.update(self._get_uni_if_data())
        get_info.update(self._get_tunnel_if_data())
        get_info.update(self._get_bgp_info())
        GlobalModule.EM_LOGGER.debug("get asr service_info = %s" % (get_info,))
        return get_info

    @decorater_log
    def get_management_info(self):
        '''
        Management information is acquired.
        acquired dict:
        {
            device_name:str,
            device_type:str
        }
        '''
        get_info = super(ASRSetParameterECDB, self).get_management_info()
        get_info["device_name"] = self.ec_message.get("name")
        get_info["device_type"] = self.ec_message.get("type")
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
                gateway_address:str,
                vrf_name:str
            }]
        }
        '''
        get_info = super(ASRSetParameterECDB, self).get_static_route_info()
        for route in get_info["static_route"]:
            route.update(self._get_vrf_name())
        GlobalModule.EM_LOGGER.debug("get asr static_route = %s" % (get_info,))
        return get_info

    @decorater_log
    def get_tunnel_if_info(self):
        '''
        Tunnel interace information is acquired.
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
        get_info = self._get_tunnel_if_data()
        return get_info

    @decorater_log
    def _get_vrf_name(self):
        '''
        VRF name is aquired.
        Return value: {vrf_name :vrf_name(VRF name) str}
        '''
        uni_info = self.ec_message.get("serviceInfo", {}).get("uni", {})
        return {"vrf_name": uni_info.get("vrfName")}

    @decorater_log
    def _get_mss_mtu(self):
        '''
        MSS name and MTU name are acquired.
        Return value: {mss(MSS name): str,ipMTU(MTU name): str}
        '''
        svs_info = self.ec_message.get("serviceInfo", {})
        return {"mss": svs_info.get("tcpMss"), "mtu": svs_info.get("ipMtu")}

    @decorater_log
    def _get_vrf_data(self):
        '''
        VRF information is acquired.
        acquired dict:
        {
            vrf:{
                vrf_name:str,
                line_no:str,
                nni_if_name:str,
                nni_vlan_id:str,
            }
        }
        '''
        get_info = {}
        nni_info = self.ec_message.get("serviceInfo", {}).get("nni", {})
        tmp_item = self._get_vrf_name()
        tmp_item["line_no"] = nni_info.get("lineNo")
        tmp_item["nni_if_name"] = nni_info.get("ifName")
        tmp_item["nni_vlan_id"] = nni_info.get("vlanId")
        get_info["vrf"] = tmp_item
        GlobalModule.EM_LOGGER.debug("get vrf_info = %s" % (get_info,))
        return get_info

    @decorater_log
    def _get_uno_if_data(self):
        '''
        UNO interface basic information is acquired.
        acquired dict:
        {
            uno:{
                vrf_name:str,
                if_name:str,
                vlan_id:str,
                ip_address:str,
                subnet_mask:str,
                mss:str,
            }
        }
        '''
        get_info = {}
        nni_info = self.ec_message.get("serviceInfo", {}).get("nni", {})
        tmp_item = self._get_vrf_name()
        tmp_item["if_name"] = nni_info.get("ifName")
        tmp_item["vlan_id"] = nni_info.get("vlanId")
        tmp_item["ip_address"] = nni_info.get("wanRouterIpAddress")
        tmp_item["subnet_mask"] = nni_info.get("subnetMask")
        tmp_item["mss"] = self._get_mss_mtu().get("mss")
        get_info["uno"] = tmp_item
        GlobalModule.EM_LOGGER.debug("get uno_info = %s" % (get_info,))
        return get_info

    @decorater_log
    def _get_uni_if_data(self):
        '''
        UNI interface information is acquired.
        acquired dict:
        {
            uni:{
                vrf_name:str,
                if_name:str,
                vlan_id:str,
                ip_address:str,
                subnet_mask:str,
                vip_ip_address:str,
                hsrp_id:str,
                is_active:Bool

                pair_node_ip_address:str,
            }
        }
        '''
        get_info = {}
        uni_info = self.ec_message.get("serviceInfo", {}).get("uni", {})
        tmp_item = self._get_vrf_name()
        tmp_item["if_name"] = uni_info.get("ifName")
        tmp_item["vlan_id"] = uni_info.get("vlanId")
        tmp_item["ip_address"] = uni_info.get("ipAddress")
        tmp_item["subnet_mask"] = uni_info.get("subnetMask")
        tmp_item["vip_ip_address"] = uni_info.get("virtualIpAddress")
        tmp_item["hsrp_id"] = uni_info.get("hsrpId")
        tmp_item["mtu"] = self._get_mss_mtu().get("mtu")
        device_type = self.get_management_info().get("device_type")
        tmp_act = {"active": True, "standby": False}
        tmp_item["is_active"] = tmp_act[device_type]
        get_info["uni"] = tmp_item
        GlobalModule.EM_LOGGER.debug("get uni_info = %s" % (get_info,))
        return get_info

    @decorater_log
    def _get_tunnel_if_data(self):
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
        uni_info = self._get_uni_if_data()["uni"]
        uni_if_name = uni_info["if_name"]
        uni_vlan_id = uni_info["vlan_id"]
        tnl_info = self.ec_message.get("serviceInfo", {}).get("officeInfo", [])
        tmp_list = []
        for tnl_if in tnl_info:
            tmp_item = self._get_vrf_name()
            tmp_item["if_name"] = tnl_if.get("tunnelIfName")
            tmp_item["uni_if_name"] = uni_if_name
            tmp_item["uni_vlan_id"] = uni_vlan_id
            tmp_item["tunnel_source"] = tnl_if.get("tunnelSrcIpAddress")
            tmp_list.append(tmp_item)
        get_info["tunnel_if"] = tmp_list
        GlobalModule.EM_LOGGER.debug("get tunnel_if = %s" % (get_info,))
        return get_info

    @decorater_log
    def _get_bgp_info(self):
        '''
        BGP information is acquired.
        acquired dict:
        {
            bgp:{
                vrf_name:str,
                ip_address:str,
                nni_ip_address:str,
                nni_vpn_gw:str,
            }
        }
        '''
        get_info = {}
        uni_info = self.ec_message.get("serviceInfo", {}).get("uni", {})
        nni_info = self.ec_message.get("serviceInfo", {}).get("nni", {})
        tmp_item = self._get_vrf_name()
        tmp_item["ip_address"] = uni_info.get("pairIpAddress")
        tmp_item["nni_ip_address"] = nni_info.get("wanRouterIpAddress")
        tmp_item["nni_vpn_gw"] = nni_info.get("vpnGwIpAddress")
        get_info["bgp"] = tmp_item
        GlobalModule.EM_LOGGER.debug("get bgp_info = %s" % (get_info,))
        return get_info
