#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmDeviceInfoUpdate.py
'''
Class for updating device information
'''
from lxml import etree
import json
from EmDeviceMerge import EmDeviceMerge
import GlobalModule
from EmCommonLog import decorater_log


class EmDeviceInfoUpdate(EmDeviceMerge):
    '''
    Class for updating device information
    '''


    @decorater_log
    def __init__(self):
        '''
        Costructor
        '''

        super(EmDeviceInfoUpdate, self).__init__()

        self._scenario_name = "DeviceInfoUpdate"

        self.service = GlobalModule.SERVICE_DEVICE_INFO

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
        Scenario process in each device is executed.
        Argument:
            device_message: message for each device(byte)
            transaction_id: transaction ID (uuid)
            order_type: order type(int)
            condition: thread control object (condition object)
            device_name: device name(str)
            force: flag indicating forced stop (boolean)
        Return value:
            none
        '''
        self._process_scenario_existing(
            device_message=device_message,
            transaction_id=transaction_id,
            order_type=order_type,
            condition=condition,
            device_name=device_name,
            force=force)

    @decorater_log
    def _creating_json(self, device_message):
        '''
        EC message(XML) devided for each device is converted to JSDN.
        (json is not used. It is checked whether necesary argument exists or not).
        Argument:
            device_message: message for each device
        Return value:
            device_json_message: JSON message
        '''
        device_json_message = {}
        xml_elm = etree.fromstring(device_message)
        GlobalModule.EM_LOGGER.debug(
            "device_message = %s", etree.tostring(xml_elm, pretty_print=True))
        device_obj = {}
        device_obj["name"] = self._gen_json_name(xml_elm, self._xml_ns)
        device_obj["equipment"] = self._gen_json_equipment(xml_elm,
                                                           self._xml_ns)
        device_json_message["device"] = device_obj
        return json.dumps(device_json_message)

    @decorater_log
    def _gen_json_name(self, xml, xml_ns):
        '''
            Name information is acquired from xml message to be analyzed.
            It is set in dictionary object which stores EC message.
            Return value:
                json：dictionary object which stores EC message
                xml：xml message to be analyzed
                xml_ns：name space
        '''

        name_elm = self._find_xml_node(xml, xml_ns + "name")
        return name_elm.text

    @decorater_log
    def _gen_json_equipment(self, xml, xml_ns):
        '''
            Device-connection information is acquired from xml message to be analyzed.
            It is set in dictionary object which stores EC message.
            Return value:
                json：dictionary object which stores EC message
                xml：xml message to be analyzed
                xml_ns：name space
        '''
        equ_json = {}
        equ_elm = self._find_xml_node(xml, xml_ns + "equipment")
        equ_json["platform"] = equ_elm.find(xml_ns + "platform").text
        equ_json["os"] = equ_elm.find(xml_ns + "os").text
        equ_json["firmware"] = equ_elm.find(xml_ns + "firmware").text
        return equ_json
