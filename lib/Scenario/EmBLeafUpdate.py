#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmBLeafUpdate.py

'''
Individual scenario for updating B-Leaf.
'''
import json
from lxml import etree
import GlobalModule
from EmCommonLog import decorater_log
from EmBLeafScenario import EmBLeafScenario
from EmLeafMerge import EmLeafMerge
from EmDeviceMerge import EmDeviceMerge


class EmBLeafUpdate(EmBLeafScenario, EmLeafMerge):
    '''
    B-Leaf update class. (take-over from Leaf expansion scenario)
    '''


    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmBLeafUpdate, self).__init__()
        super(EmBLeafScenario, self).__init__()

        self.service = GlobalModule.SERVICE_B_LEAF

        self._xml_ns = "{%s}" % GlobalModule.EM_NAME_SPACES[self.service]

        self._scenario_name = "B-LeafUpdate"

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

    @decorater_log
    def _process_scenario(self,
                          device_message=None,
                          transaction_id=None,
                          order_type=None,
                          condition=None,
                          device_name=None,
                          force=False):
        '''
        Executes scenario process in each device
        Explanation about parameter：
            device_message: Message for each device(byte)
            transaction_id: Transaction ID (uuid)
            order_type: Order type (int)
            condition: Thread control information (condition object)
            device_name: Device name (str)
            force: Frag of deletion to be forced(boolean)
        Explanation about return value
            None
        '''

        super(EmDeviceMerge, self)._process_scenario(
            device_message=device_message,
            transaction_id=transaction_id,
            order_type=order_type,
            condition=condition,
            device_name=device_name,
            force=force)
