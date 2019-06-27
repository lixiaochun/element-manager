#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation

'''
Individual scenario for B-Leaf reduction.
'''
from lxml import etree
import json
from EmBLeafScenario import EmBLeafScenario
from EmDeleteScenario import EmDeleteScenario
from EmLeafDelete import EmLeafDelete
import GlobalModule
from EmCommonLog import decorater_log


class EmBLeafDelete(EmBLeafScenario, EmLeafDelete):
    '''
    B-Leaf B-Leaf reduction class
    '''

    @decorater_log
    def __init__(self):
        '''
        
        '''
        super(EmBLeafDelete, self).__init__()
        super(EmBLeafScenario, self).__init__()

        self._scenario_name = "B-LeafDelete"

        self.service = GlobalModule.SERVICE_B_LEAF

        self._xml_ns = "{%s}" % GlobalModule.EM_NAME_SPACES[self.service]

        self.device_type = "device"

    @decorater_log
    def _process_scenario(self,
                          device_message=None,
                          transaction_id=None,
                          order_type=None,
                          condition=None,
                          device_name=None,
                          force=False):
        '''
        Execute scenario process in each device
        Explanation about return value:
            device_message: Message for each device (byte)
            transaction_id: Transacttion ID (uuid)
            order_type: Order type (int)
            condition: Thread cntrol information (condition object)
            device_name: Device name (str)
            force: Forced deletion flag(boolean)
        Explanation about parameter:
            None
        '''
        xml_elm = etree.fromstring(device_message)
        ospf_elm = self._find_xml_node(xml_elm, self._xml_ns + "ospf")
        if ospf_elm is not None:
            GlobalModule.EM_LOGGER.debug('OSPF tag EXIST')
            super(EmDeleteScenario, self)._process_scenario(device_message,
                                                            transaction_id,
                                                            order_type,
                                                            condition,
                                                            device_name,
                                                            force)
        else:
            GlobalModule.EM_LOGGER.debug('OSPF tag NOT EXIST')

            super(EmBLeafDelete, self)._process_scenario_existing(
                device_message,
                transaction_id,
                order_type,
                condition,
                device_name,
                force)

    @decorater_log
    def _creating_json(self, device_message):
        '''
        Convert EC message(XML) devided into that for each device to JSDN
        Explanation about parameter:
            device_message: message for each device
        Explanation about return value:
            device_json_message: JSON message
        '''
        xml_elm = etree.fromstring(device_message)

        GlobalModule.EM_LOGGER.debug(
            "device_message = %s", etree.tostring(xml_elm, pretty_print=True))

        device_json_message = {"device": {"name": None}}
        self._gen_json_name(
            device_json_message, xml_elm, self._xml_ns)

        if self._find_xml_node(xml_elm, self._xml_ns + "ospf") is not None:
            device_json_message["device"]["ospf"] = (
                self._gen_json_b_leaf_ospf(device_json_message,
                                           xml_elm,
                                           self._xml_ns)
            )

        GlobalModule.EM_LOGGER.debug(
            "device__json_message = %s", device_json_message)

        return json.dumps(device_json_message)
