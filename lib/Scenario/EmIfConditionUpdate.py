# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmIfConditionUpdate.py
'''
Scenario for opening and closing IF
'''
import json
from lxml import etree
from EmMergeScenario import EmMergeScenario
import GlobalModule
from EmCommonLog import decorater_log


class EmIfConditionUpdate(EmMergeScenario):
    '''
    Class for opening and closing IF
    '''

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmIfConditionUpdate, self).__init__()

        self._scenario_name = "IfConditionUpdate"

        self.service = GlobalModule.SERVICE_IF_CONDITION

        self._xml_ns = "{%s}" % GlobalModule.EM_NAME_SPACES[self.service]

        self.device_type = "device"

    @decorater_log
    def _creating_json(self, device_message):
        '''
        EC message(XML) devided for each device is converted to JSDN.
        Argument:
            device_message: message in each device
        Return value:
            device__json_message: JSON message
        '''
        device_json_message = \
            {
                "device": {
                    "name": None,
                    "interface-physical_value": 0,
                    "interface-physical": [],
                    "internal-lag_value": 0,
                    "internal-lag": []
                }
            }

        xml_elm = etree.fromstring(device_message)

        GlobalModule.EM_LOGGER.debug(
            "device_message = %s", etree.tostring(xml_elm, pretty_print=True))

        self._gen_json_name(device_json_message, xml_elm, self._xml_ns)

        self._gen_json_if_condition(
            device_json_message, xml_elm, self._xml_ns)

        GlobalModule.EM_LOGGER.debug(
            "device__json_message = %s", device_json_message)

        return json.dumps(device_json_message)

    @decorater_log
    def _gen_json_name(self, json, xml, xml_ns):
        '''
            Device name is acquired from xml message to be analyzed.
            It is set to dictionary object which stores EC message.
            Argument:
                dictionary object which stores EC message
                xml：xml message to be analyzed
                xml_ns：name space
        '''

        name_elm = self._find_xml_node(xml, xml_ns + "name")
        json["device"]["name"] = name_elm.text

    @decorater_log
    def _gen_json_if_condition(self, json, xml, xml_ns):
        '''
            IF open/close information is acquired from xml message to be analyzed.
            It is set to dictionary object which stores EC message.
            Argument:
                dictionary object which stores EC message
                xml：xml message to be analyzed
                xml_ns：name space
        '''
        if_condition_elm = self._find_xml_node(xml,
                                               xml_ns + "interface")

        if if_condition_elm is not None:
            if_condition_tag = xml_ns + "interface"
            for if_condition in xml.findall(".//" + if_condition_tag):
                if if_condition.find(xml_ns + "type") is not None:
                    if_type = if_condition.find(xml_ns + "type").text
                    if if_type == "physical-ifs":
                        GlobalModule.EM_LOGGER.debug(
                            "Test _gen_json_if_condition_phy Start")
                        self._gen_json_if_condition_phy(
                            json, xml_ns, if_condition)
                    elif if_type == "lag-ifs":
                        GlobalModule.EM_LOGGER.debug(
                            "Test _gen_json_if_condition_lag Start")
                        self._gen_json_if_condition_lag(
                            json, xml_ns, if_condition)

        json["device"]["interface-physical_value"] = \
            len(json["device"]["interface-physical"])

        json["device"]["internal-lag_value"] = \
            len(json["device"]["internal-lag"])

    @decorater_log
    def _gen_json_if_condition_phy(self, json, xml_ns, interface_phy):
        '''
            IF open/close information is acquired from xml message to be analyzed.
            It is set to dictionary object which stores EC message.
            Argument:
                json：dictionary object which stores EC message
                xml_ns：name space
                interface_phy：xml message to be analyzed
        '''

        interface_phy_message = \
            {
                "name": None,
                "condition": None,
            }

        interface_phy_message["name"] = \
            interface_phy.find(xml_ns + "name").text
        interface_phy_message["condition"] = \
            interface_phy.find(xml_ns + "condition").text

        json["device"]["interface-physical"].append(interface_phy_message)

    @decorater_log
    def _gen_json_if_condition_lag(self, json, xml_ns, internal_lag):
        '''
            IF open/close information is acquired from xml message to be analyzed.
            It is set to dictionary object which stores EC message.
            
            Argument:
                json：dictionary object which stores EC message
                xml_ns：name space
                internal_lag：xml message to be analyzed
        '''

        internal_lag_message = \
            {
                "name": None,
                "condition": None,
            }

        internal_lag_message["name"] = \
            internal_lag.find(xml_ns + "name").text
        internal_lag_message["condition"] = \
            internal_lag.find(xml_ns + "condition").text

        json["device"]["internal-lag"].append(internal_lag_message)
