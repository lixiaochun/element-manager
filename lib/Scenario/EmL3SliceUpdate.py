#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2018 Nippon Telegraph and Telephone Corporation
# Filename: EmL3SliceUpdate.py
'''
Individual scenario to add L3 slice.
'''
import json
from lxml import etree
from EmMergeScenario import EmMergeScenario
import GlobalModule
from EmCommonLog import decorater_log


class EmL3SliceUpdate(EmMergeScenario):
    '''
    Class for adding L3 slice.
    '''


    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmL3SliceUpdate, self).__init__()

        self._scenario_name = "L3SliceUpdate"

        self.service = GlobalModule.SERVICE_L3_SLICE

        self._xml_ns = "{%s}" % GlobalModule.EM_NAME_SPACES[self.service]

        self.device_type = "device-leaf"

    @decorater_log
    def _creating_json(self, device_message):
        '''
        Convert EC message (XML) divided for each device into JSON.
        Explanation about parameter:
            device_message: Message for each device
        Explanation about return value
            device_json_message: JSON message
        '''
        device_json_message = \
            {
                "device-leaf": {
                    "name": None,
                    "slice_name": None,
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

        for cp_get in xml_elm.findall(self._xml_ns + "cp"):
            cp_list = \
                {
                    "operation": None,
                    "name": None,
                    "vlan-id": 0,
                    "static": {
                        "route": [],
                        "route6": []
                    },
                    "qos": {}
                }

            cp_list["name"] = cp_get.find(self._xml_ns + "name").text
            cp_list["vlan-id"] = \
                int(cp_get.find(self._xml_ns + "vlan-id").text)

            static_elm = self._find_xml_node(cp_get,
                                             self._xml_ns + "static")
            if static_elm is not None:
                if static_elm.find(self._xml_ns + "route") is not None:
                    for route_ipv4 in static_elm.findall(
                            self._xml_ns + "route"):
                        route_info = \
                            {
                                "operation": None,
                                "address": None,
                                "prefix": 0,
                                "nexthop": None
                            }
                        if route_ipv4.get("operation") == "delete":
                            route_info["operation"] = "delete"
                        else:
                            route_info["operation"] = "merge"

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
                                "operation": None,
                                "address": None,
                                "prefix": 0,
                                "nexthop": None
                            }
                        if route_ipv6.get("operation") == "delete":
                            route6_info["operation"] = "delete"
                        else:
                            route6_info["operation"] = "merge"

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
                    if inflow_shaping_rate.get("operation") == "replace" and \
                            inflow_shaping_rate.text is None:
                        cp_list["qos"]["inflow-shaping-rate"] = None
                    else:
                        cp_list["qos"]["inflow-shaping-rate"] = float(
                            inflow_shaping_rate.text)

                outflow_shaping_rate = qos_info.find(
                    self._xml_ns + "outflow-shaping-rate")
                if outflow_shaping_rate is not None:
                    if outflow_shaping_rate.get("operation") == "replace" and \
                            outflow_shaping_rate.text is None:
                        cp_list["qos"]["outflow-shaping-rate"] = None
                    else:
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
        Device name:Create Netconf message (json letter string).
        '''
        slice_elm = etree.Element("slice_name")
        slice_elm.text = slice_name
        element.append(slice_elm)
        return etree.tostring(element)
