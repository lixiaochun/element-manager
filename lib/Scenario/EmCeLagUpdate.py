# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmCeLagUpdate.py
'''
Individual scenario for changing LAG for CE.
'''
import json
from lxml import etree
from EmMergeScenario import EmMergeScenario
import GlobalModule
from EmCommonLog import decorater_log


class EmCeLagUpdate(EmMergeScenario):
    '''
    Class for changing LAG for CE.
    '''

    @decorater_log
    def __init__(self):
        '''
        Constructor.
        '''

        super(EmCeLagUpdate, self).__init__()

        self._scenario_name = "CeLagUpdate"

        self.service = GlobalModule.SERVICE_CE_LAG

        self._xml_ns = "{%s}" % GlobalModule.EM_NAME_SPACES[self.service]

        self.device_type = "device"

    @decorater_log
    def _creating_json(self, device_message):
        '''
        Convert EC message(XML) divided for each device to JSON.
        Parameter：
            device_message: message for each device
        Reurn value:
            device__json_message: JSON message
        '''

        device__json_message = \
            {
                "device":
                {
                    "name": None,
                    "ce-lag-interface_value": 0,
                    "ce-lag-interface": []
                }
            }

        xml_elm = etree.fromstring(device_message)

        GlobalModule.EM_LOGGER.debug(
            "device_message = %s", etree.tostring(xml_elm, pretty_print=True))

        self._gen_json_name(
            device__json_message, xml_elm, self._xml_ns)

        self._gen_json_ce_lag_if(
            device__json_message, xml_elm, self._xml_ns)

        GlobalModule.EM_LOGGER.debug(
            "device__json_message = %s", device__json_message)

        return json.dumps(device__json_message)

    @decorater_log
    def _gen_json_name(self, json, xml, xml_ns):
        '''
            Obtain device name from xml message to be analyzed
            and set the device name to EC message storage dictionary object.
            Parameter：
                json：EC message storage dictionary object
                xml：device name from xml message to be analyzed
                xml_ns：name space
        '''

        name_elm = self._find_xml_node(xml, xml_ns + "name")
        json["device"]["name"] = name_elm.text

    @decorater_log
    def _gen_json_ce_lag_if(self, json, xml, xml_ns):
        '''
            Obtain LAG information for CE from xml message to be analyzed and
            set it for EC message storage dictionary object.
            Parameter：
                json：EC message storage dictionary object
                xml：device name from xml message to be analyzed
                xml_ns：name space
        '''

        ce_tag = xml_ns + "ce-lag-interface"
        for ce_lag in xml.findall(".//" + ce_tag):

            ce_lag_message = \
                {
                    "name": None,
                    "minimum-links": 0,
                    "leaf-interface_value": 0,
                    "leaf-interface": []
                }

            leaf_tag = xml_ns + "leaf-interface"
            for leaf_int in ce_lag.findall(".//" + leaf_tag):
                leaf_info = \
                    {
                        "operation": None,
                        "name": None
                    }

                if leaf_int.get("operation") == "delete":
                    leaf_info["operation"] = "delete"
                else:
                    leaf_info["operation"] = "merge"

                leaf_info["name"] = \
                    leaf_int.find(xml_ns + "name").text

                ce_lag_message[
                    "leaf-interface"].append(leaf_info)

            ce_lag_message["leaf-interface_value"] = \
                len(ce_lag_message["leaf-interface"])

            ce_lag_message["name"] = \
                ce_lag.find(xml_ns + "name").text
            ce_lag_message["minimum-links"] = \
                int(ce_lag.find(xml_ns + "minimum-links").text)

            json["device"][
                "ce-lag-interface"].append(ce_lag_message)

        json["device"]["ce-lag-interface_value"] = \
            len(json["device"]["ce-lag-interface"])
