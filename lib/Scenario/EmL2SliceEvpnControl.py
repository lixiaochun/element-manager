#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2017 Nippon Telegraph and Telephone Corporation
# Filename: EmL2SliceEvpnControl.py
'''
Individual scenario to add L2 slice. 
'''
import json
from lxml import etree
from EmMergeScenario import EmMergeScenario
import GlobalModule
from EmCommonLog import decorater_log


class EmL2SliceEvpnControl(EmMergeScenario):
    '''
    Class for adding L2 slice.   
    '''


    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmL2SliceEvpnControl, self).__init__()

        self._scenario_name = "L2SliceEvpnControl"

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

        device__json_message = \
            {
                "device-leaf":
                {
                    "name": None,
                    "slice_name": None,
                    "merge_cp_value": 0,
                    "delete_cp_value": 0,
                    "replace_cp_value": 0,
                    "cp": []
                }
            }

        xml_elm = etree.fromstring(device_message)

        GlobalModule.EM_LOGGER.debug(
            "device_message = %s", etree.tostring(xml_elm, pretty_print=True))

        device_elm = self._find_xml_node(xml_elm, self._xml_ns + "name")
        device__json_message["device-leaf"]["name"] = device_elm.text

        slice_elm = self._find_xml_node(xml_elm, self._xml_ns + "slice_name")
        device__json_message["device-leaf"]["slice_name"] = slice_elm.text

        merge_cp_value = 0
        delete_cp_value = 0
        replace_cp_value = 0

        for cp_info in xml_elm.findall(self._xml_ns + "cp"):
            cp_message = \
                {
                    "operation": None,
                    "name": None,
                    "vlan-id": 0,
                }
            if cp_info.get("operation") == "delete":
                cp_message["operation"] = "delete"
                delete_cp_value += 1
            else:
                cp_message["operation"] = "merge"
                merge_cp_value += 1

            cp_message["name"] = cp_info.find(self._xml_ns + "name").text
            cp_message["vlan-id"] = \
                int(cp_info.find(self._xml_ns + "vlan-id").text)

            port_mode = cp_info.find(self._xml_ns + "port-mode")
            if port_mode is not None:
                cp_message["port-mode"] = port_mode.text
            vni = cp_info.find(self._xml_ns + "vni")
            if vni is not None:
                cp_message["vni"] = int(vni.text)
            esi = cp_info.find(self._xml_ns + "esi")
            if (esi is not None) and (esi.get("operation") != "delete"):
                cp_message["esi"] = esi.text
            system_id = cp_info.find(self._xml_ns + "system-id")
            if (system_id is not None) and\
                    (system_id.get("operation") != "delete"):
                cp_message["system-id"] = system_id.text

            if (esi is not None and esi.get("operation") == "delete") and\
                    (system_id is not None and
                     system_id.get("operation") == "delete"):
                cp_message["operation"] = "delete"
                cp_message["system-id"] = "0"
                cp_message["esi"] = "0"

            device__json_message["device-leaf"]["cp"].append(cp_message)

        device__json_message["device-leaf"]["merge_cp_value"] = merge_cp_value

        device__json_message["device-leaf"][
            "delete_cp_value"] = delete_cp_value

        device__json_message["device-leaf"][
            "replace_cp_value"] = replace_cp_value

        GlobalModule.EM_LOGGER.debug(
            "device__json_message = %s", device__json_message)

        return json.dumps(device__json_message)

    @staticmethod
    @decorater_log
    def _gen_netconf_message(element, slice_name):
        '''
        Device name：Create Netconf message (json letter strings). 
        '''
        slice_elm = etree.Element("slice_name")
        slice_elm.text = slice_name
        element.append(slice_elm)
        return etree.tostring(element)
