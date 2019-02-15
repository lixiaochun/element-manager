#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2018 Nippon Telegraph and Telephone Corporation
# Filename: EmBLeafUpdate.py
'''
Individual scenario for updating B-Leaf.
'''
import json
from lxml import etree
import GlobalModule
from EmCommonLog import decorater_log
from EmLeafMerge import EmLeafMerge
from EmBLeafScenario import EmBLeafScenario


class EmBLeafUpdate(EmBLeafScenario, EmLeafMerge):
    '''
    B-Leaf update class. (take-over from Leaf expansion scenario)
    '''


    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmBLeafScenario, self).__init__()

        self.service = GlobalModule.SERVICE_B_LEAF

        self._xml_ns = "{%s}" % GlobalModule.EM_NAME_SPACES[self.service]

        self.scenario_name = "B-LeafUpdate"

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
        xml_elm = etree.fromstring(device_message)

        GlobalModule.EM_LOGGER.debug(
            "device_message = %s", etree.tostring(xml_elm, pretty_print=True))

        device_json_message = {"device": {"name": None}}
        self._gen_json_name(
            device_json_message, xml_elm, self._xml_ns)

        device_json_message["device"]["ospf"] = self._gen_json_b_leaf_ospf(
            device_json_message, xml_elm, self._xml_ns)

        GlobalModule.EM_LOGGER.debug(
            "device__json_message = %s", device_json_message)

        return json.dumps(device_json_message)
