#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmCgwshServiceFlavor.py
from EmCommonLog import decorater_log
import GlobalModule
'''
Flavor class for Cgwsh service scenario
'''


class EmCgwshServiceFlavor(object):
    '''
    Flavor class for Cgwsh service scenario
    Flavor:Parts depending on service is embodied.
    '''
    
    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''
        self._xml_ns = "{http://www.ntt.co.jp/msf/service/}"
        self.order_type = None

    @decorater_log
    def _get_asr_info(self, xml):
        '''
        ASR information is acquired.
        '''
        service_info_ele = xml.find(self._xml_ns + "serviceInfo")
        service_info = {}
        service_info.update(self._get_asr_uni_info(service_info_ele))
        service_info.update(self._get_asr_nni_info(service_info_ele))
        service_info.update(self._get_elem_text(service_info_ele,
                                                self._xml_ns + "tcpMss",
                                                "tcpMss"))
        service_info.update(self._get_elem_text(service_info_ele,
                                                self._xml_ns + "ipMtu",
                                                "ipMtu"))
        service_info.update(self._get_asr_office_infos(service_info_ele))
        service_info.update(self._get_device_static_routes(service_info_ele))
        device_info = {}
        device_info.update(self._get_device_name(xml))
        device_info.update(self._get_device_type(xml))
        device_info["serviceInfo"] = service_info
        json_mes = {"device": device_info}
        GlobalModule.EM_LOGGER.debug('created asrInfo = %s' % (json_mes,))
        return json_mes

    @decorater_log
    def _get_asr_static_info(self, xml):
        '''
        ASR static route information is acquired.
        '''
        service_info_ele = xml.find(self._xml_ns + "serviceInfo")
        service_info = {}
        service_info.update(self._get_asr_uni_info(service_info_ele))
        service_info.update(self._get_asr_nni_info(service_info_ele))
        service_info.update(self._get_device_static_routes(service_info_ele))
        device_info = {}
        device_info.update(self._get_device_name(xml))
        device_info.update(self._get_device_type(xml))
        device_info["serviceInfo"] = service_info
        json_mes = {"device": device_info}
        GlobalModule.EM_LOGGER.debug(
            'created asrStaticInfo = %s' % (json_mes,))
        return json_mes

    @decorater_log
    def _get_nvr_info(self, xml):
        '''
        NVR information is acquired.
        '''
        service_info_ele = xml.find(self._xml_ns + "serviceInfo")
        service_info = {}
        service_info.update(self._get_nvr_service_addr_info(service_info_ele))
        service_info.update(self._get_nvr_ppp_infos(service_info_ele))
        service_info.update(self._get_nvr_default_gateways(service_info_ele))
        service_info.update(self._get_device_static_routes(service_info_ele))
        device_info = {}
        device_info.update(self._get_device_name(xml))
        device_info["serviceInfo"] = service_info
        json_mes = {"device": device_info}
        GlobalModule.EM_LOGGER.debug('created nvrInfo = %s' % (json_mes,))
        return json_mes

    @decorater_log
    def _get_nvr_static_info(self, xml):
        '''
        NVR static route information is acquired.
        '''
        service_info_ele = xml.find(self._xml_ns + "serviceInfo")
        service_info = {}
        service_info.update(self._get_nvr_default_gateways(service_info_ele))
        service_info.update(self._get_device_static_routes(service_info_ele))
        device_info = self._get_device_name(xml)
        device_info["serviceInfo"] = service_info
        json_mes = {"device": device_info}
        GlobalModule.EM_LOGGER.debug(
            'created nvrStaticInfo = %s' % (json_mes,))
        return json_mes

    @decorater_log
    def _get_device_name(self, xml):
        '''
        Device name is acquired.(common to ASR and NVR)
        '''
        get_tag = ".//%(name_space)smanagementInfo/%(name_space)shostname"
        get_tag = get_tag % {"name_space": self._xml_ns}
        dev_name = xml.find(get_tag).text
        return {"name": dev_name}

    @decorater_log
    def _get_device_type(self, xml):
        '''
        Acting device is acquired.(ASR)
        '''
        tmp = {}
        get_tag = ".//%(name_space)smanagementInfo/%(name_space)stype"
        get_tag = get_tag % {"name_space": self._xml_ns}
        get_ele = xml.find(get_tag)
        if get_ele is not None:
            tmp = {"type": get_ele.text}
        return tmp

    @decorater_log
    def _get_asr_uni_info(self, service_info_xml):
        '''
        UNI interface is acquired.(ASR)
        '''
        uni_info = service_info_xml.find(self._xml_ns + "uni")
        tmp = {"vlanId": uni_info.find(self._xml_ns + "vlanId").text,
               "ifName": uni_info.find(self._xml_ns + "ifName").text,
               "vrfName": uni_info.find(self._xml_ns + "vrfName").text,
               }
        tmp.update(self._get_elem_text(uni_info,
                                       self._xml_ns + "hsrpId",
                                       "hsrpId"))
        tmp.update(self._get_elem_text(uni_info,
                                       self._xml_ns + "virtualIpAddress",
                                       "virtualIpAddress"))
        tmp.update(self._get_elem_text(uni_info,
                                       self._xml_ns + "ipAddress",
                                       "ipAddress"))
        tmp.update(self._get_elem_text(uni_info,
                                       self._xml_ns + "pairIpAddress",
                                       "pairIpAddress"))
        tmp.update(self._get_elem_text(uni_info,
                                       self._xml_ns + "subnetMask",
                                       "subnetMask"))
        return {"uni": tmp}

    @decorater_log
    def _get_asr_nni_info(self, service_info_xml):
        '''
        NNI interface information is acquired.(ASR)
        '''
        nni_info = service_info_xml.find(self._xml_ns + "nni")
        tmp = {"vlanId": nni_info.find(self._xml_ns + "vlanId").text,
               "ifName": nni_info.find(self._xml_ns + "ifName").text,
               }
        tmp.update(self._get_elem_text(nni_info,
                                       self._xml_ns + "lineNo",
                                       "lineNo"))
        tmp.update(self._get_elem_text(nni_info,
                                       self._xml_ns + "wanRouterIpAddress",
                                       "wanRouterIpAddress"))
        tmp.update(self._get_elem_text(nni_info,
                                       self._xml_ns + "vpnGwIpAddress",
                                       "vpnGwIpAddress"))
        tmp.update(self._get_elem_text(nni_info,
                                       self._xml_ns + "subnetMask",
                                       "subnetMask"))
        return {"nni": tmp}

    @decorater_log
    def _get_asr_office_infos(self, service_info_xml):
        '''
        Place information is acquired.(ASR)
        '''
        tmp = []
        return_tmp = {}
        office_infos = service_info_xml.findall(self._xml_ns + "officeInfo")
        for office_info in office_infos:
            tmp.append(self._get_asr_office_unit_info(office_info))
        if tmp:
            return_tmp = {"officeInfo": tmp}
        GlobalModule.EM_LOGGER.debug(
            'created officeInfos = %s' % (return_tmp,))
        return return_tmp

    @decorater_log
    def _get_asr_office_unit_info(self, office_info_xml):
        '''
        Place information (simple) is acquired.(ASR)
        '''
        return_tmp = {
            "tunnelIfName":
            office_info_xml.find(self._xml_ns + "tunnelIfName").text,
        }
        return_tmp.update(
            self._get_elem_text(office_info_xml,
                                self._xml_ns + "tunnelSrcIpAddress",
                                "tunnelSrcIpAddress")
        )
        return return_tmp

    @staticmethod
    @decorater_log
    def _get_elem_text(xml_elem, tag_name, key_name):
        '''
        Tag name is searched from xml elements.
        If name is exsists, the dictionary is returned. If no, null dictionary is returned.
        '''
        tmp = {}
        tmp_elem = xml_elem.find(tag_name)
        if tmp_elem is not None:
            tmp = {key_name: tmp_elem.text}
        return tmp

    @decorater_log
    def _get_nvr_service_addr_info(self, service_info_xml):
        '''
        Service IP address,VLANID, subnet mask is acquired.(NVR)
        '''
        return_tmp = {}
        return_tmp.update(self._get_elem_text(service_info_xml,
                                              self._xml_ns + "vlanId",
                                              "vlanId"))
        return_tmp.update(self._get_elem_text(service_info_xml,
                                              self._xml_ns + "ipAddress",
                                              "ipAddress"))
        return_tmp.update(self._get_elem_text(service_info_xml,
                                              self._xml_ns + "subnetMask",
                                              "subnetMask"))
        return return_tmp

    @decorater_log
    def _get_nvr_ppp_infos(self, service_info_xml):
        '''
        PPPoE is acquired.(NVR)
        '''
        tmp = []
        return_tmp = {}
        ppp_infos = service_info_xml.findall(self._xml_ns + "pppInfo")
        for ppp_info in ppp_infos:
            tmp.append(self._get_nvr_ppp_unit_info(ppp_info))
        if tmp:
            return_tmp = {"pppInfo": tmp}
        GlobalModule.EM_LOGGER.debug('created PPPoEs = %s' % (return_tmp,))
        return return_tmp

    @decorater_log
    def _get_nvr_ppp_unit_info(self, ppp_info_xml):
        '''
        PPPoE(simple) is acquired.(NVR)
        '''
        return {
            "connectionId":
            ppp_info_xml.find(self._xml_ns + "connectionId").text,
            "connectionPassword":
            ppp_info_xml.find(self._xml_ns + "connectionPassword").text,
            "corporationId":
            ppp_info_xml.find(self._xml_ns + "corporationId").text,
            "ppId":
            ppp_info_xml.find(self._xml_ns + "ppId").text,
        }

    @decorater_log
    def _get_nvr_default_gateways(self, service_info_xml):
        '''
        Default gateway is acquired.(NVR)
        '''
        tmp = {}
        gateways = service_info_xml.find(self._xml_ns + "defaultGateway")
        if gateways is not None:
            tmp = {"defaultGateway": gateways.text}
        GlobalModule.EM_LOGGER.debug('created defaultGateway = %s' % (tmp,))
        return tmp

    @decorater_log
    def _get_device_static_routes(self, service_info_xml):
        '''
        Static route is acquired.(common to ASR and NVR)
        '''
        tmp = []
        return_tmp = {}
        static_routes = service_info_xml.findall(self._xml_ns + "staticRoute")
        for static_route in static_routes:
            tmp.append(self._get_device_static_route_unit(static_route))
        if tmp:
            return_tmp = {"staticRoute": tmp}
        GlobalModule.EM_LOGGER.debug(
            'created staticRoutes = %s' % (return_tmp,))
        return return_tmp

    @decorater_log
    def _get_device_static_route_unit(self, static_route_xml):
        '''
        Static route(simple) is acquired.(common to ASR and NVR)
        '''
        return {
            "ipAddress":
            static_route_xml.find(self._xml_ns + "ipAddress").text,
            "subnetMask":
            static_route_xml.find(self._xml_ns + "subnetMask").text,
            "gatewayIpAddress":
            static_route_xml.find(self._xml_ns + "gatewayIpAddress").text,
        }

    @decorater_log
    def _get_nvr_ppp_info(self, xml):
        '''
        PPP information is acquired. 
        '''
        service_info_ele = xml.find(self._xml_ns + "serviceInfo")
        service_info = {}
        service_info.update(self._get_nvr_ppp_infos(service_info_ele))
        device_info = self._get_device_name(xml)
        device_info["serviceInfo"] = service_info
        json_mes = {"device": device_info}
        GlobalModule.EM_LOGGER.debug(
            'created nvrStaticInfo = %s' % (json_mes,))
        return json_mes

    @decorater_log
    def _get_asr_tunnel_info(self, xml):
        '''
        Tunnel information is acquired.(NVR)
        '''
        service_info_ele = xml.find(self._xml_ns + "serviceInfo")
        service_info = {}
        service_info.update(self._get_asr_uni_info(service_info_ele))
        service_info.update(self._get_asr_office_infos(service_info_ele))
        device_info = self._get_device_name(xml)
        type = self._get_device_type(xml)
        device_info.update(self._get_device_type(xml))
        device_info["serviceInfo"] = service_info
        json_mes = {"device": device_info}
        GlobalModule.EM_LOGGER.debug(
            'created nvrStaticInfo = %s' % (json_mes,))
        return json_mes
