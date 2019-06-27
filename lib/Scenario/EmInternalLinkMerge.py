#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmInternalLinkMerge.py
'''
Individual scenario to add IF for internal link 
'''
import json
from lxml import etree
from EmMergeScenario import EmMergeScenario
import GlobalModule
from EmCommonLog import decorater_log


class EmInternalLinkMerge(EmMergeScenario):
    '''
    Class for adding L3 slice.
    '''



    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmInternalLinkMerge, self).__init__()

        self.service = GlobalModule.SERVICE_INTERNAL_LINK

        self._xml_ns = "{%s}" % GlobalModule.EM_NAME_SPACES[self.service]

        self._scenario_name = "InternalLinkMerge"

        self.device_type = "device"

    @decorater_log
    def _creating_json(self, device_message):
        '''
        Convert EC message(XML) devided into each device to JSON.
        Explanation about parameter:
            device_message: Message for each device
        Explanation about return value:
            device_json_message: JSON message
        '''

        device_json_message = {
            "device":
            {
                "vpn-type": None,
                "name": None,
                "breakout-interface_value": 0,
                "breakout-interface": [],
                "internal-physical_value": 0,
                "internal-physical": [],
                "internal-lag_value": 0,
                "internal-lag": []
            }
        }

        xml_elm = etree.fromstring(device_message)

        GlobalModule.EM_LOGGER.debug(
            "device_message = %s", etree.tostring(xml_elm, pretty_print=True))

        self._gen_json_vpn_type(device_json_message, xml_elm, self._xml_ns)

        self._gen_json_name(device_json_message, xml_elm, self._xml_ns)

        self._gen_json_breakout(
            device_json_message, xml_elm, self._xml_ns)

        self._gen_json_internal_if(
            device_json_message, xml_elm, self._xml_ns)

        GlobalModule.EM_LOGGER.debug(
            "device__json_message = %s", device_json_message)

        return json.dumps(device_json_message)

    @decorater_log
    def _gen_json_vpn_type(self, json, xml, xml_ns):
        '''
            Obtain physical IF information for internal link from xml message to be analyzed and
            set it for EC message storage dictionary object.
            Explanation about parameter:
                json：dictionary object for EC message storage
                xml：xml message to be analyzed
                xml_ns：name space
        '''

        vpn_type = self._find_xml_node(xml, xml_ns + "vpn-type")

        if vpn_type is not None:
            json["device"].update({"vpn-type": vpn_type.text})

    @decorater_log
    def _gen_json_name(self, json, xml, xml_ns):
        '''
            Obtain device name from xml message to be analyzed and
            set it for EC message storage dictionary object.
            Explanation about parameter:
                json：dictionary object for EC message storage
                xml：xml message to be analyzed
                xml_ns：name space
        '''

        name_elm = self._find_xml_node(xml, xml_ns + "name")
        json["device"]["name"] = name_elm.text

    @decorater_log
    def _gen_json_breakout(self, json, xml, xml_ns):
        '''
            Obtain breakout IF information from xml message to be analyzed and
            set it for EC message storage dictionary object.
            Explanation about parameter:
                json：dictionary object for EC message storage
                xml：xml message to be analyzed
                xml_ns：name space
        '''
        breakout_elm = self._find_xml_node(xml,
                                           xml_ns + "breakout-interface")

        if breakout_elm is not None:
            breakout_tag = xml_ns + "breakout-interface"
            for breakout in xml.findall(".//" + breakout_tag):
                breakout_base = breakout.find(xml_ns + "base-interface").text
                breakout_speed = breakout.find(xml_ns + "speed").text
                breakout_num = int(breakout.find(xml_ns + "breakout-num").text)
                json["device"]["breakout-interface"].append(
                    {"base-interface": breakout_base,
                     "speed": breakout_speed,
                     "breakout-num": breakout_num})

        json["device"]["breakout-interface_value"] = \
            len(json["device"]["breakout-interface"])

    @decorater_log
    def _gen_json_internal_if(self, json, xml, xml_ns):
        '''
            Obtain IF information for internal link from xml message to be analyzed and
            set it for EC message storage dictionary object.
            Explanation about parameter:
                json：dictionary object for EC message storage
                xml：xml message to be analyzed
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
            Obtain physical IF information for internal link from xml message to be analyzed and
            set it for EC message storage dictionary object.
            Explanation about parameter:
                json：dictionary object for EC message storage
                xml_ns：name space
                xml：xml message to be analyzed
        '''

        internal_phy_name = internal_phy.find(xml_ns + "name").text
        internal_phy_opp = internal_phy.find(
            xml_ns + "opposite-node-name").text
        internal_phy_vlan = int(internal_phy.find(xml_ns + "vlan-id").text)
        internal_phy_addr = internal_phy.find(xml_ns + "address").text
        internal_phy_pre = int(internal_phy.find(xml_ns + "prefix").text)
        internal_phy_cost = int(internal_phy.find(xml_ns + "cost").text)

        json["device"]["internal-physical"].append(
            {"name": internal_phy_name,
             "opposite-node-name": internal_phy_opp,
             "vlan-id": internal_phy_vlan,
             "address": internal_phy_addr,
             "prefix": internal_phy_pre,
             "cost": internal_phy_cost})

    @decorater_log
    def _gen_json_internal_lag(self, json, xml_ns, itnal_lag):
        '''
            Obtain LAG information for internal link from xml message to be analyzed and
            set it for EC message storage dictionary object.
            Explanation about parameter:
                json：dictionary object for EC message storage
                xml_ns：name space
                xml：xml message to be analyzed
        '''
        internal_lag_message = {
            "name": None,
            "opposite-node-name": None,
            "lag-id": 0,
            "vlan-id": 0,
            "minimum-links": 0,
            "link-speed": None,
            "address": None,
            "prefix": 0,
            "cost": 0,
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
        internal_lag_message["lag-id"] = \
            int(itnal_lag.find(xml_ns + "lag-id").text)
        internal_lag_message["vlan-id"] = \
            int(itnal_lag.find(xml_ns + "vlan-id").text)
        internal_lag_message["opposite-node-name"] = \
            itnal_lag.find(xml_ns + "opposite-node-name").text
        internal_lag_message["minimum-links"] = \
            int(itnal_lag.find(xml_ns + "minimum-links").text)
        internal_lag_message["link-speed"] = \
            itnal_lag.find(xml_ns + "link-speed").text
        internal_lag_message["address"] = \
            itnal_lag.find(xml_ns + "address").text
        internal_lag_message["prefix"] = \
            int(itnal_lag.find(xml_ns + "prefix").text)
        internal_lag_message["cost"] = \
            int(itnal_lag.find(xml_ns + "cost").text)

        json["device"][
            "internal-lag"].append(internal_lag_message)
