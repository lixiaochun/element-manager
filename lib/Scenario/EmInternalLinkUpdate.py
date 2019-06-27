#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmInternalLinkUpdate.py
'''
Individual scenario for changing internal link IF. 
'''
import json
from lxml import etree
from EmMergeScenario import EmMergeScenario
import GlobalModule
from EmCommonLog import decorater_log


class EmInternalLinkUpdate(EmMergeScenario):
    '''
    Class for changing internal link IF.
    '''
    @decorater_log
    def __init__(self):
        '''
        Constructor.
        '''

        super(EmInternalLinkUpdate, self).__init__()

        self._scenario_name = "InternalLinkUpdate"

        self.service = GlobalModule.SERVICE_INTERNAL_LINK

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
        device_json_message = \
            {
                "device": {
                    "name": None,
                    "internal-physical_value": 0,
                    "internal-physical": [],
                    "internal-lag_value": 0,
                    "internal-lag": []
                }
            }

        xml_elm = etree.fromstring(device_message)

        GlobalModule.EM_LOGGER.debug(
            "device_message = %s", etree.tostring(xml_elm, pretty_print=True))

        self._gen_json_name(device_json_message, xml_elm, self._xml_ns)

        self._gen_json_internal_if(
            device_json_message, xml_elm, self._xml_ns)

        GlobalModule.EM_LOGGER.debug(
            "device__json_message = %s", device_json_message)

        return json.dumps(device_json_message)

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
    def _gen_json_internal_if(self, json, xml, xml_ns):
        '''
            Obtain IF information from internal link from xml message to be analyzed
            and set the device name to EC message storage dictionary object.
            Parameter：
                json：EC message storage dictionary object
                xml：device name from xml message to be analyzed
                xml_ns：name space
        '''
        internal_if_elm = self._find_xml_node(xml,
                                              xml_ns + "internal-interface")

        if internal_if_elm is not None:
            internal_if_tag = xml_ns + "internal-interface"
            for internal_if in xml.findall(".//" + internal_if_tag):
                if internal_if.find(xml_ns + "type") is not None:
                    internal_if_type = internal_if.find(xml_ns + "type").text
                    if internal_if_type == "physical-if":
                        GlobalModule.EM_LOGGER.debug(
                            "Test _gen_json_internal_phy Start")
                        self._gen_json_internal_phy(json, xml_ns, internal_if)
                    elif internal_if_type == "lag-if":
                        GlobalModule.EM_LOGGER.debug(
                            "Test _gen_json_internal_lag Start")
                        self._gen_json_internal_lag(json, xml_ns, internal_if)

        json["device"]["internal-physical_value"] = \
            len(json["device"]["internal-physical"])
            
        json["device"]["internal-lag_value"] = \
            len(json["device"]["internal-lag"])

    @decorater_log
    def _gen_json_internal_phy(self, json, xml_ns, internal_phy):
        '''
            Obtain physical IF information from internal link from xml message to be analyzed
            and set the device name to EC message storage dictionary object.
            Parameter：
                json：EC message storage dictionary object
                xml：device name from xml message to be analyzed
                xml_ns：name space
        '''

        internal_phy_name = internal_phy.find(xml_ns + "name").text
        cost = internal_phy.find(xml_ns + "cost")

        if cost is not None:
            json["device"]["internal-physical"].append(
                {"name": internal_phy_name,
                 "cost": int(cost.text)})
        else:
            json["device"]["internal-physical"].append(
                {"name": internal_phy_name})

    @decorater_log
    def _gen_json_internal_lag(self, json, xml_ns, internal_lag):
        '''
            Obtain LAG information from internal link from xml message to be analyzed
            and set the device name to EC message storage dictionary object.
            Parameter：
                json：EC message storage dictionary object
                xml：device name from xml message to be analyzed
                xml_ns：name space
           '''

        internal_lag_message = \
            {
                "name": None,
                "cost": 0,
                "minimum-links": 0,
                "internal-interface_vallue": 0,
                "internal-interface": []
            }
        internal_interface_tag = xml_ns + "internal-interface"
        for internal_interface_int in \
                internal_lag.findall(".//" + internal_interface_tag):
            internal_interface_info = \
                {
                    "operation": None,
                    "name": None
                }

            if internal_interface_int.get("operation") == "delete":
                internal_interface_info["operation"] = "delete"
            else:
                internal_interface_info["operation"] = "merge"

            internal_interface_info["name"] = \
                internal_interface_int.find(xml_ns + "name").text

            internal_lag_message["internal-interface"].append(
                internal_interface_info)

        internal_lag_message["internal-interface_value"] = \
            len(internal_lag_message["internal-interface"])

        cost = internal_lag.find(xml_ns + "cost")
        minimum_links = internal_lag.find(xml_ns + "minimum-links")

        internal_lag_message["name"] = \
            internal_lag.find(xml_ns + "name").text
        if cost is not None:
            internal_lag_message["cost"] = int(cost.text)
        if minimum_links is not None:
            internal_lag_message["minimum-links"] = int(minimum_links.text)

        json["device"]["internal-lag"].append(internal_lag_message)
