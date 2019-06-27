#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmACLFilterDelete.py
'''
Individual scenario for ACL configuration deletion
'''
import json
from lxml import etree
from EmDeleteScenario import EmDeleteScenario
import GlobalModule
from EmCommonLog import decorater_log


class EmACLFilterDelete(EmDeleteScenario):
    '''
    Class for ACL configuration deletion
    '''


    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmACLFilterDelete, self).__init__()

        self.service = GlobalModule.SERVICE_ACL_FILTER

        self._xml_ns = "{%s}" % GlobalModule.EM_NAME_SPACES[self.service]

        self._scenario_name = "ACLFilterDelete"

        self.device_type = "device-leaf"

    @decorater_log
    def _creating_json(self, device_message):
        '''
        Convert EC message (XML) divided for each device into JSON.
        Explanation about parameter:
            device_message: Message for each device
         Explanation about return value
            device__json_message: JSON message
        '''

        device_json_message = {
            "device":
            {
                "name": None,
                "filter": []
            }
        }

        xml_elm = etree.fromstring(device_message)

        GlobalModule.EM_LOGGER.debug(
            "device_message = %s", etree.tostring(xml_elm, pretty_print=True))

        self._gen_json_name(device_json_message, xml_elm, self._xml_ns)

        self._gen_json_acl_filter(
            device_json_message, xml_elm, self._xml_ns)

        GlobalModule.EM_LOGGER.debug(
            "device__json_message = %s", device_json_message)

        return json.dumps(device_json_message)

    @decorater_log
    def _gen_json_acl_filter(self, json, xml, xml_ns):
        '''
            Obtain ACL configuration inforamtion from xml message to be analyzed and
            set it for EC message storage dictionary object.
            Explanation about parameter:                
                json:dictionary object for EC message storage
                xml:xml message to be analyzed
                xml_ns:Name space
        '''
        device_name = self._find_xml_node(xml, xml_ns + "name").text
        acl_filter_elm = xml.findall(xml_ns + "filter")
        for filter in acl_filter_elm:
            filter_param = {
                "filter_id": 0,
                "term": []
            }
            filter_id = int(filter.find(xml_ns + "filter_id").text)
            operation = filter.get("operation")
            if operation:
                filter_param["operation"] = operation
            filter_param["filter_id"] = filter_id
            acl_term_elm = filter.findall(xml_ns + "term")
            for acl_term in acl_term_elm:
                term_param = {
                    "name": None,
                    "term-name": None
                }
                term_name = acl_term.find(xml_ns + "term_name").text
                if_name = GlobalModule.EMSYSCOMUTILDB._get_acl_del_if(
                    device_name, filter_id)
                operation = acl_term.get("operation")
                if operation:
                    term_param["operation"] = operation
                term_param["name"] = if_name
                term_param["term-name"] = term_name
                filter_param["term"].append(term_param)
            if len(acl_term_elm) == 0:
                del filter_param["term"]
            json["device"]["filter"].append(filter_param)
