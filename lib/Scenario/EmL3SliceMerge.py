#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmL3SliceMerge.py
'''
Individual scenario to add L3 slice.
'''
import json
from lxml import etree
from EmMergeScenario import EmMergeScenario
import GlobalModule
from EmCommonLog import decorater_log


class EmL3SliceMerge(EmMergeScenario):
    '''
    Class for adding L3 slice.
    '''


    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmL3SliceMerge, self).__init__()

        self.service = GlobalModule.SERVICE_L3_SLICE

        self._xml_ns = "{%s}" % GlobalModule.EM_NAME_SPACES[self.service]

        self._scenario_name = "L3SliceMerge"

        self.device_type = "device-leaf"

    @decorater_log
    def _creating_json(self, device_message):
        '''
        Convert EC message (XML) divided for each device into JSON.
        Explanation about parameter:
            device_message: Message for each device
        Explanation about return value 
            device__json_message: JSON message
        '''           
        device_json_message = \
            {
                "device-leaf": {
                    "name": None,
                    "slice_name": None,
                    "vrf": {},
                    "cp_value": 0,
                    "cp": []
                }
            }

        xml_elm = etree.fromstring(device_message)

        GlobalModule.EM_LOGGER.debug(
            "device_message = %s", etree.tostring(xml_elm, pretty_print=True))

        device_elm = self._find_xml_node(xml_elm, self._xml_ns + "name")
        device_json_message["device-leaf"]["name"] = device_elm.text

        slice_elm = self._find_xml_node(xml_elm, self._xml_ns + "slice_name")
        device_json_message["device-leaf"]["slice_name"] = slice_elm.text

        vrf_elm = self._find_xml_node(xml_elm,
                                      self._xml_ns + "vrf")
        vrf_name = vrf_elm.find(self._xml_ns + "vrf-name").text
        device_json_message["device-leaf"]["vrf"]["vrf-name"] = vrf_name

        vrf_rt = vrf_elm.find(self._xml_ns + "rt").text
        device_json_message["device-leaf"]["vrf"]["rt"] = vrf_rt

        vrf_rd = vrf_elm.find(self._xml_ns + "rd").text
        device_json_message["device-leaf"]["vrf"]["rd"] = vrf_rd

        vrf_router_id = vrf_elm.find(self._xml_ns + "router-id").text
        device_json_message[
            "device-leaf"]["vrf"]["router-id"] = vrf_router_id

        cp_tag = self._xml_ns + "cp"
        for cp_get in xml_elm.findall(".//" + cp_tag):
            cp_list = \
                {
                    "name": None,
                    "vlan-id": 0,
                    "ce-interface": {},
                    "vrrp": {
                        "track": {
                            "interface": []
                        }
                    },
                    "bgp": {},
                    "static": {
                        "route": [],
                        "route6": []
                    },
                    "qos": {}
                }

            cp_list["name"] = \
                cp_get.find(self._xml_ns + "name").text
            cp_list["vlan-id"] = \
                int(cp_get.find(self._xml_ns + "vlan-id").text)

            ce_elm = self._find_xml_node(cp_get,
                                         self._xml_ns + "ce-interface")

            if ce_elm.find(self._xml_ns + "address") is not None:
                ipv4_addr = ce_elm.find(self._xml_ns + "address").text
                cp_list["ce-interface"]["address"] = ipv4_addr

            if ce_elm.find(self._xml_ns + "prefix") is not None:
                ipv4_prefix = int(ce_elm.find(self._xml_ns + "prefix").text)
                cp_list["ce-interface"]["prefix"] = ipv4_prefix

            if ce_elm.find(self._xml_ns + "address6") is not None:
                ipv6_addr = ce_elm.find(self._xml_ns + "address6").text
                cp_list["ce-interface"]["address6"] = ipv6_addr

            if ce_elm.find(self._xml_ns + "prefix6") is not None:
                ipv6_prefix = int(ce_elm.find(self._xml_ns + "prefix6").text)
                cp_list["ce-interface"]["prefix6"] = ipv6_prefix

            if ce_elm.find(self._xml_ns + "mtu") is not None:
                mtu = int(ce_elm.find(self._xml_ns + "mtu").text)
                cp_list["ce-interface"]["mtu"] = mtu

            vrrp_elm = self._find_xml_node(cp_get,
                                           self._xml_ns + "vrrp")
            if vrrp_elm is not None:
                vrrp_group_id = int(
                    vrrp_elm.find(self._xml_ns + "group-id").text)
                cp_list["vrrp"]["group-id"] = vrrp_group_id

                vrrp_priority = int(
                    vrrp_elm.find(self._xml_ns + "priority").text)
                cp_list["vrrp"]["priority"] = vrrp_priority

                if vrrp_elm.find(self._xml_ns + "virtual-address") is not None:
                    vr_addr = vrrp_elm.find(
                        self._xml_ns + "virtual-address").text
                    cp_list["vrrp"]["virtual-address"] = vr_addr

                if vrrp_elm.find(self._xml_ns +
                                 "virtual-address6") is not None:
                    vr_addr6 = vrrp_elm.find(
                        self._xml_ns + "virtual-address6").text
                    cp_list["vrrp"]["virtual-address6"] = vr_addr6

                if vrrp_elm.find(self._xml_ns + "track") is not None:

                    track_elm = self._find_xml_node(
                        vrrp_elm, self._xml_ns + "track")
                    track_tag = self._xml_ns + "interface"
                    for track_if in track_elm.findall(".//" + track_tag):
                        track_if_info = \
                            {
                                "name": None
                            }
                        track_if_info["name"] = \
                            track_if.find(self._xml_ns + "name").text

                        cp_list["vrrp"]["track"][
                            "interface"].append(track_if_info.copy())

                    track_len = len(cp_list["vrrp"]["track"]["interface"])
                    cp_list["vrrp"]["track"][
                        "track_interface_value"] = track_len
                else:
                    del cp_list["vrrp"]["track"]
            else:
                del cp_list["vrrp"]

            bgp_elm = self._find_xml_node(cp_get,
                                          self._xml_ns + "bgp")
            if bgp_elm is not None:
                bgp_remote_as_num = int(
                    bgp_elm.find(self._xml_ns + "remote-as-number").text)
                cp_list["bgp"]["remote-as-number"] = bgp_remote_as_num

                if bgp_elm.find(self._xml_ns + "master") is not None:
                    cp_list["bgp"]["master"] = "ON"

                if bgp_elm.find(self._xml_ns + "local-address") is not None:
                    local_addr = bgp_elm.find(
                        self._xml_ns + "local-address").text
                    cp_list["bgp"]["local-address"] = local_addr

                if bgp_elm.find(self._xml_ns + "remote-address") is not None:
                    remote_addr = bgp_elm.find(
                        self._xml_ns + "remote-address").text
                    cp_list["bgp"]["remote-address"] = remote_addr

                if bgp_elm.find(self._xml_ns + "local-address6") is not None:
                    local_addr6 = bgp_elm.find(
                        self._xml_ns + "local-address6").text
                    cp_list["bgp"]["local-address6"] = local_addr6

                if bgp_elm.find(self._xml_ns + "remote-address6") is not None:
                    remote_addr6 = bgp_elm.find(
                        self._xml_ns + "remote-address6").text
                    cp_list["bgp"]["remote-address6"] = remote_addr6
            else:
                del cp_list["bgp"]

            static_elm = self._find_xml_node(cp_get,
                                             self._xml_ns + "static")
            if static_elm is not None:
                if static_elm.find(self._xml_ns + "route") is not None:
                    ipv4_tag = self._xml_ns + "route"
                    for route_ipv4 in static_elm.findall(".//" + ipv4_tag):
                        route_info = \
                            {
                                "address": None,
                                "prefix": 0,
                                "nexthop": None
                            }
                        route_info["address"] = \
                            route_ipv4.find(self._xml_ns + "address").text
                        route_info["prefix"] = \
                            int(route_ipv4.find(self._xml_ns + "prefix").text)
                        route_info["nexthop"] = \
                            route_ipv4.find(self._xml_ns + "next-hop").text

                        cp_list["static"]["route"].append(route_info.copy())

                    route_ipv4_len = len(cp_list["static"]["route"])
                    cp_list["static"]["route_value"] = route_ipv4_len
                else:
                    del cp_list["static"]["route"]

                if static_elm.find(self._xml_ns + "route6") is not None:
                    ipv6_tag = self._xml_ns + "route6"
                    for route_ipv6 in static_elm.findall(".//" + ipv6_tag):
                        route6_info = \
                            {
                                "address": None,
                                "prefix": 0,
                                "nexthop": None
                            }
                        route6_info["address"] = \
                            route_ipv6.find(self._xml_ns + "address").text
                        route6_info["prefix"] = \
                            int(route_ipv6.find(self._xml_ns + "prefix").text)
                        route6_info["nexthop"] = \
                            route_ipv6.find(self._xml_ns + "next-hop").text

                        cp_list["static"]["route6"].append(route6_info.copy())

                    route_ipv6_len = len(cp_list["static"]["route6"])
                    cp_list["static"]["route6_value"] = route_ipv6_len
                else:
                    del cp_list["static"]["route6"]

            else:
                del cp_list["static"]


            qos_info = self._find_xml_node(cp_get,
                                           self._xml_ns + "qos")
            if qos_info is not None:
                inflow_shaping_rate = qos_info.find(
                    self._xml_ns + "inflow-shaping-rate")
                if inflow_shaping_rate is not None:
                    cp_list["qos"]["inflow-shaping-rate"] = float(
                        inflow_shaping_rate.text)

                outflow_shaping_rate = qos_info.find(
                    self._xml_ns + "outflow-shaping-rate")
                if outflow_shaping_rate is not None:
                    cp_list["qos"]["outflow-shaping-rate"] = float(
                        outflow_shaping_rate.text)

                remark_menu = qos_info.find(self._xml_ns + "remark-menu")
                if remark_menu is not None:
                    cp_list["qos"]["remark-menu"] = remark_menu.text

                egress_menu = qos_info.find(self._xml_ns + "egress-menu")
                if egress_menu is not None:
                    cp_list["qos"]["egress-menu"] = egress_menu.text

            device_json_message["device-leaf"]["cp"].append(cp_list.copy())

        cp_len = len(device_json_message["device-leaf"]["cp"])
        device_json_message["device-leaf"]["cp_value"] = cp_len

        GlobalModule.EM_LOGGER.debug(
            "device__json_message = %s", device_json_message)

        return json.dumps(device_json_message)

    @staticmethod
    @decorater_log
    def _gen_netconf_message(element, slice_name):
        '''
        Device name:Create Netconf message (json character string).
        '''
        slice_elm = etree.Element("slice_name")
        slice_elm.text = slice_name
        element.append(slice_elm)
        return etree.tostring(element)
