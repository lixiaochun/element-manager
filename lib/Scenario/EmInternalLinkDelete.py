#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmInternalLinkDelete.py
'''
Individual scenario for deleting IF for internal Link.
'''
import json
from lxml import etree
from EmDeleteScenario import EmDeleteScenario
import GlobalModule
from EmCommonLog import decorater_log


class EmInternalLinkDelete(EmDeleteScenario):
    '''
    Class for deleting IF for internal Link.
    '''



    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmInternalLinkDelete, self).__init__()

        self.service = GlobalModule.SERVICE_INTERNAL_LINK

        self._xml_ns = "{%s}" % GlobalModule.EM_NAME_SPACES[self.service]

        self._scenario_name = "InternalLinkDelete"

        self.device_type = "device"

    @decorater_log
    def _creating_json(self, device_message):
        '''
        Convert EC message (XML) divided for each device into JSON.
        Explanation about parameter:
            device_message: Message for each device
        Explanation about return value
            device_json_message: JSON message
        '''

        device_json_message = {
            "device":
            {
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

        self._gen_json_name(
            device_json_message, xml_elm, self._xml_ns)

        self._gen_json_internal_if(
            device_json_message, xml_elm, self._xml_ns)

        GlobalModule.EM_LOGGER.debug(
            "device__json_message = %s", device_json_message)

        return json.dumps(device_json_message)

    @decorater_log
    def _gen_json_name(self, json, xml, xml_ns):
        '''
            Obtain device name from xml message to be analyzed
            and set it for EC message storage dictionary object.
            Explanation about parameter:
                json:dictionary object for EC message storage
                xml:xml message to be analyzed
                xml_ns: name space
        '''

        name_elm = self._find_xml_node(xml, xml_ns + "name")
        json["device"]["name"] = name_elm.text

    @decorater_log
    def _gen_json_internal_if(self, json, xml, xml_ns):
        '''
            Obtain IF information for internal Link from xml message to
            be analyzed and set it for EC message storage dictionary object.
            Explanation about parameter:
                json:dictionary object for EC message storage
                xml:xml message to be analyzed
                xml_ns:Name space
        '''

        internal_if_elm = self._find_xml_node(xml,
                                              xml_ns + "internal-interface")

        if internal_if_elm is not None:
            internal_if_tag = xml_ns + "internal-interface"
            for internal_if_lag in xml.findall(".//" + internal_if_tag):
                if internal_if_lag.find(xml_ns + "type") is not None:
                    internal_if_type = internal_if_lag.find(
                        xml_ns + "type").text
                    if internal_if_type == "physical-if":
                        GlobalModule.EM_LOGGER.debug(
                            "Test _gen_json_internal_phy Start")
                        self._gen_json_internal_phy(
                            json, xml_ns, internal_if_lag)
                    elif internal_if_type == "lag-if":
                        GlobalModule.EM_LOGGER.debug(
                            "Test _gen_json_internal_lag Start")
                        self._gen_json_internal_lag(
                            json, xml_ns, internal_if_lag)

        json["device"]["internal-physical_value"] = \
            len(json["device"]["internal-physical"])

        json["device"]["internal-lag_value"] = \
            len(json["device"]["internal-lag"])

    @decorater_log
    def _gen_json_internal_phy(self, json, xml_ns, internal_phy):
        '''
            Obtain physical IF information for internal Link
            from xml message to be analyzed and set it
            for EC message storage dictionary object.
            Explanation about parameter:
                json:dictionary object for EC message storage
                xml_ns:Name space
                internal_phy:xml message to be analyzed
        '''

        internal_phy_name = internal_phy.find(xml_ns + "name").text
        json["device"]["internal-physical"].append(
            {"name": internal_phy_name})

    @decorater_log
    def _gen_json_internal_lag(self, json, xml_ns, itnal_lag):
        '''
            Obtain LAG information for internal Link from xml message to
            be analyzed and set it for EC message storage dictionary object.
            Explanation about parameter:
                json:dictionary object for EC message storage
                xml_ns:Name space
                itnal_lag:xml message to be analyzed
        '''
        internal_lag_message = {
            "name": None,
            "minimum-links": 0,
            "internal-interface_value": 0,
            "internal-interface": []
        }
        itnal_int_tag = xml_ns + "internal-interface"
        for itnal_int in itnal_lag.findall(".//" + itnal_int_tag):
            interface_name = itnal_int.find(xml_ns + "name").text
            internal_if_name = {"name": interface_name}
            internal_lag_message[
                "internal-interface"].append(internal_if_name)

        internal_lag_message["internal-interface_value"] = \
            len(internal_lag_message["internal-interface"])

        internal_lag_message["name"] = \
            itnal_lag.find(xml_ns + "name").text
        internal_lag_message["minimum-links"] = \
            int(itnal_lag.find(xml_ns + "minimum-links").text)

        json["device"][
            "internal-lag"].append(internal_lag_message)
