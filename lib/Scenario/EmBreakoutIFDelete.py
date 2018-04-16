#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2018 Nippon Telegraph and Telephone Corporation
# Filename: EmBreakoutIFDelete.py
'''
Individual scenario for deletion of BreakoutIF.
'''
import json
from lxml import etree
from EmDeleteScenario import EmDeleteScenario
import GlobalModule
from EmCommonLog import decorater_log


class EmBreakoutIFDelete(EmDeleteScenario):
    '''
    BreakoutIF deletion class
    '''

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmBreakoutIFDelete, self).__init__()

        self.service = GlobalModule.SERVICE_BREAKOUT

        self._xml_ns = "{%s}" % GlobalModule.EM_NAME_SPACES[self.service]

        self._scenario_name = "BreakoutDelete"

        self.device_type = "device"

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
                "device":
                {
                    "name": None,
                    "breakout-interface_value": 0,
                    "breakout-interface": []
                }
            }

        xml_elm = etree.fromstring(device_message)

        GlobalModule.EM_LOGGER.debug(
            "device_message = %s", etree.tostring(xml_elm, pretty_print=True))

        self._gen_json_name(
            device__json_message, xml_elm, self._xml_ns)

        self._gen_json_breakout(
            device__json_message, xml_elm, self._xml_ns)

        GlobalModule.EM_LOGGER.debug(
            "device__json_message = %s", device__json_message)

        return json.dumps(device__json_message)

    @decorater_log
    def _gen_json_breakout(self, json, xml, xml_ns):
        '''
            Obtain BreakoutIF information from xml message to be analyzed and
            set it for EC message storage dictionary object.
            Explanation about parameter:
                json:dictionary object for EC message storage
                xml:xml message to be analyzed
                xml_ns:Name space
                service:Service name
                order:Order name
        '''
        breakout_elm = self._find_xml_node(xml,
                                           xml_ns + "breakout-interface")

        if breakout_elm is not None:
            breakout_tag = xml_ns + "breakout-interface"
            for breakout in xml.findall(".//" + breakout_tag):
                breakout_base = breakout.find(xml_ns + "base-interface").text

                json["device"]["breakout-interface"].append(
                    {"base-interface": breakout_base})

        json["device"]["breakout-interface_value"] = \
            len(json["device"]["breakout-interface"])
