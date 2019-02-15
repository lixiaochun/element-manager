#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2018 Nippon Telegraph and Telephone Corporation
# Filename: EmL3SliceUpdate.py
'''
Individual scenario of L2 slise update.
'''
import json
from lxml import etree
from EmMergeScenario import EmMergeScenario
import GlobalModule
from EmCommonLog import decorater_log


class EmL2SliceUpdate(EmMergeScenario):
    '''
    Class for updating L2 slice.
    '''

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmL2SliceUpdate, self).__init__()

        self._scenario_name = "L2SliceUpdate"

        self.service = GlobalModule.SERVICE_L2_SLICE

        self._xml_ns = "{%s}" % GlobalModule.EM_NAME_SPACES[self.service]

        self.device_type = "device-leaf"

    @decorater_log
    def _creating_json(self, device_message):
        '''
        Convert EC message (XML) divided for each device into JSON.
        Explanation about parameter：
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
                    "qos": {}
                }

            cp_list["name"] = cp_get.find(self._xml_ns + "name").text
            cp_list["vlan-id"] = \
                int(cp_get.find(self._xml_ns + "vlan-id").text)

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
        Device name：Create Netconf message (json letter string).
        '''
        slice_elm = etree.Element("slice_name")
        slice_elm.text = slice_name
        element.append(slice_elm)
        return etree.tostring(element)
