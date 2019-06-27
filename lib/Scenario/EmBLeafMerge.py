#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmBLeafMerge.py
'''
Individual scenario for B-Leaf expansion.
'''
import json
from lxml import etree
import GlobalModule
from EmCommonLog import decorater_log
from EmLeafMerge import EmLeafMerge
from EmBLeafScenario import EmBLeafScenario


class EmBLeafMerge(EmBLeafScenario, EmLeafMerge):
    '''
   B-Leaf expansion class (take-over from Leaf expansion scenario)
    '''


    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmBLeafMerge, self).__init__()
        super(EmBLeafScenario, self).__init__()

        self.service = GlobalModule.SERVICE_B_LEAF

        self._xml_ns = "{%s}" % GlobalModule.EM_NAME_SPACES[self.service]

        self._scenario_name = "B-LeafMerge"

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

        equ_elm = self._find_xml_node(xml_elm, self._xml_ns + "equipment")
        if equ_elm is not None:
            leaf_json = \
                super(EmBLeafMerge, self)._creating_json(device_message)
            device_json_message = json.loads(leaf_json)
        else:
            device_json_message = {"device": {"name": None}}
            self._gen_json_name(
                device_json_message, xml_elm, self._xml_ns)

        device_json_message["device"]["ospf"] = self._gen_json_b_leaf_ospf(
            device_json_message, xml_elm, self._xml_ns)

        GlobalModule.EM_LOGGER.debug(
            "device__json_message = %s", device_json_message)

        return json.dumps(device_json_message)
