#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmRecoverNode.py
'''
Individual scenario of recover node
'''
import json
from lxml import etree
import EmRecover
import GlobalModule
from EmCommonLog import decorater_log


class EmRecoverNode(EmRecover.EmRecover):
    '''
    Scenario class for recover node
    '''

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmRecoverNode, self).__init__()

        self.service = GlobalModule.SERVICE_RECOVER_NODE

        self._xml_ns = "{%s}" % GlobalModule.EM_NAME_SPACES[self.service]

        self.scenario_name = "RecoverNode"

    @decorater_log
    def _creating_json(self, device_message):
        '''
        Merges EC message(XML) devided into that in each device and
        device registration information received from  DB
        converts them  to JSDN and sets QOS information for service resetting

        Argument:
            device_message: message for each device
        Return value:
            device_json_message: JSON message
        '''
        json_message = super(EmRecoverNode, self)._creating_json(
            device_message)

        device_json_message = json.loads(json_message)

        xml_elm = etree.fromstring(device_message)

        self._gen_json_inner_if(
            device_json_message, xml_elm, self._xml_ns, "internal-interface")

        self._gen_json_db_update(
            device_json_message, xml_elm, self._xml_ns)

        GlobalModule.EM_LOGGER.debug(
            "device__json_message = %s", device_json_message)

        return json.dumps(device_json_message)

    @decorater_log
    def _gen_json_inner_if(self,
                           json,
                           xml,
                           xml_ns,
                           convert_table_name):
        '''
            Gets information conversion table for internal link from message to be analyzed  
            Set it in dictionary object for storing EC message 
                json：dictionary object which stores EC message
                xml：message to be analyzed
                xml_ns：name space
                convert_table_name：convert table namr
        '''
        inner_if_message = {
            convert_table_name: []}
        if_convert_elm = self._find_xml_node(xml,
                                             xml_ns + convert_table_name)

        if if_convert_elm is not None:
            if_convert_tag = xml_ns + convert_table_name
            for if_convert in xml.findall(".//" + if_convert_tag):
                name = if_convert.find(xml_ns + "name").text
                opposite_node_name = if_convert.find(
                    xml_ns + "opposite-node-name").text
                inner_if_message[convert_table_name].append(
                    {"name": name,
                     "opposite-node-name": opposite_node_name})
            json["device"][convert_table_name] = inner_if_message[convert_table_name]
        json["device"][convert_table_name + "_value"] = \
            len(inner_if_message[convert_table_name])

    @decorater_log
    def _gen_json_db_update(self, json, xml, xml_ns):
        '''
            Gets DB update frag information from xml message to be analyzed.
            Sets it to dictionary object whic stores EC message
            Argument:
                json：dictionary object which stores EC message
                xml：xml message to be analyzed
                xml_ns： name space
        '''
        db_update = self._find_xml_node(xml, xml_ns + "db_update")
        if db_update is not None:
            flag = True
        else:
            flag = False
        json["device"]["db_update"] = flag

    @decorater_log
    def _register_the_setting_in_em(self,
                                    device_name=None,
                                    order_type=None,
                                    device_message=None,
                                    transaction_id=None,):
        '''
        Registers information in DB(if only db_update is executed, )
        Argument:
            device_name: device name (str)
            order_type: order type (str)
            device_message: Device-related EC message (byte)
            transaction_id: transaction ID (uuid)
        Return value:
            None
        '''
        xml_elm = etree.fromstring(device_message)
        db_update = self._find_xml_node(
            xml_elm, self._xml_ns + "db_update")

        if db_update is not None:
            super(EmRecoverNode, self)._register_the_setting_in_em(
                device_name, order_type, device_message, transaction_id)
        else:
            pass
