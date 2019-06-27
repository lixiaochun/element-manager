#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmSpineMerge.py
'''
Individual scenario for Spine expansion.
'''
import json
from lxml import etree
from EmDeviceMerge import EmDeviceMerge
import GlobalModule
from EmCommonLog import decorater_log


class EmSpineMerge(EmDeviceMerge):
    '''
    Class for Spine expansion
    '''


    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmSpineMerge, self).__init__()

        self.scenario_name = "SpineMerge"

        self.service = GlobalModule.SERVICE_SPINE

        self._xml_ns = "{%s}" % GlobalModule.EM_NAME_SPACES[self.service]

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

        device_json_message = \
            {
                "device":
                {
                    "name": None,
                    "equipment":
                    {
                        "platform": None,
                        "os": None,
                        "firmware": None,
                        "loginid": None,
                        "password": None
                    },
                    "breakout-interface_value": 0,
                    "breakout-interface": [],
                    "internal-physical_value": 0,
                    "internal-physical": [],
                    "internal-lag_value": 0,
                    "internal-lag": [],
                    "management-interface":
                    {
                        "address": None,
                        "prefix": 0
                    },
                    "loopback-interface":
                    {
                        "address": None,
                        "prefix": 0
                    },
                    "snmp":
                    {
                        "server-address": None,
                        "community": None
                    },
                    "ntp":
                    {
                        "server-address": None
                    },
                    "ospf":
                    {
                        "area-id": None
                    }
                }
            }

        xml_elm = etree.fromstring(device_message)

        GlobalModule.EM_LOGGER.debug(
            "device_message = %s", etree.tostring(xml_elm, pretty_print=True))

        device_json_message["device"]["name"] = \
            self._gen_json_name(xml_elm, self._xml_ns)

        self._gen_json_equipment(
            device_json_message, xml_elm, self._xml_ns)

        self._gen_json_breakout(
            device_json_message, xml_elm, self._xml_ns)

        self._gen_json_internal_if(
            device_json_message, xml_elm, self._xml_ns)

        self._gen_json_management(
            device_json_message, xml_elm, self._xml_ns)

        self._gen_json_loopback(
            device_json_message, xml_elm, self._xml_ns)

        self._gen_json_snmp(
            device_json_message, xml_elm, self._xml_ns)

        self._gen_json_ntp(
            device_json_message, xml_elm, self._xml_ns)

        self._gen_json_ospf(
            device_json_message, xml_elm, self._xml_ns)

        GlobalModule.EM_LOGGER.debug(
            "device__json_message = %s", device_json_message)

        return json.dumps(device_json_message)

    @decorater_log
    def _gen_json_name(self, xml, xml_ns):
        '''
            Obtain name information from xml message to be analyzed and
            set it for EC message storage dictionary object.
            Explanation about parameter:
                json:dictionary object for EC message storage
                xml:xml message to be analyzed
                xml_ns: name space
                service：service name
                order：order name
        '''

        name_elm = self._find_xml_node(xml, xml_ns + "name")
        return name_elm.text

    @decorater_log
    def _gen_json_equipment(self, json, xml, xml_ns):
        '''
            Obtain device connection information from xml message to
            be analyzed and set it for EC message storage dictionary object.
            Explanation about parameter:
                json:dictionary object for EC message storage
                xml:xml message to be analyzed
                xml_ns: name space              
        '''

        equ_elm = self._find_xml_node(xml, xml_ns + "equipment")
        equ_json = json["device"]["equipment"]
        equ_json["platform"] = \
            equ_elm.find(xml_ns + "platform").text
        equ_json["os"] = \
            equ_elm.find(xml_ns + "os").text
        equ_json["firmware"] = \
            equ_elm.find(xml_ns + "firmware").text
        equ_json["loginid"] = \
            equ_elm.find(xml_ns + "loginid").text
        equ_json["password"] = \
            equ_elm.find(xml_ns + "password").text

    @decorater_log
    def _gen_json_breakout(self, json, xml, xml_ns):
        '''
            Obtain breakoutIF information from xml message to be analyzed and
            set it for EC message storage dictionary object.
            Explanation about parameter:
                json:dictionary object for EC message storage
                xml:xml message to be analyzed
                xml_ns: name space       
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
            Obtain IF information for internal Link from xml message to
            be analyzed and set it for EC message storage dictionary object.
            Explanation about parameter:
                json:dictionary object for EC message storage
                xml:xml message to be analyzed
                xml_ns: name space 
        '''
        internal_if_elm = self._find_xml_node(xml,
                                              xml_ns + "internal-interface")

        if internal_if_elm is not None:
            internal_if_tag = xml_ns + "internal-interface"
            for internal_if in xml.findall(".//" + internal_if_tag):
                if internal_if.find(xml_ns + "type") is not None:
                    internal_if_type = internal_if.find(xml_ns + "type").text
                    if internal_if_type == "physical-if":
                        self._gen_json_internal_phy(json, xml_ns, internal_if)
                    elif internal_if_type == "lag-if":
                        self._gen_json_internal_lag(json, xml_ns, internal_if)

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
                xml:xml message to be analyzed
                xml_ns: name space   
                internal_phy:xml message to be analyzed
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
            Obtain LAG information for internal Link from xml message to
            be analyzed and set it for EC message storage dictionary object.
            Explanation about parameter:
                json:dictionary object for EC message storage
                xml:xml message to be analyzed
                xml_ns: name space
                itnal_lag:xml message to be analyzed
        '''
        internal_lag_message = {
            "name": None,
            "opposite-node-name": None,
            "lag-id": 0,
            "vlan-id": 0,
            "minimum-links": 0,
            "link-speed": 0,
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
        internal_lag_message["opposite-node-name"] = \
            itnal_lag.find(xml_ns + "opposite-node-name").text
        internal_lag_message["lag-id"] = \
            int(itnal_lag.find(xml_ns + "lag-id").text)
        internal_lag_message["vlan-id"] = \
            int(itnal_lag.find(xml_ns + "vlan-id").text)
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

    @decorater_log
    def _gen_json_management(self, json, xml, xml_ns):
        '''
            Obtain management IF information from xml message to be analyzed
            and set it for EC message storage dictionary object.
            Explanation about parameter:
                json:dictionary object for EC message storage
                xml:xml message to be analyzed
                xml_ns: name space
        '''
        man_elm = self._find_xml_node(xml,
                                      xml_ns + "management-interface")
        man_json = json["device"]["management-interface"]
        man_json["address"] = \
            man_elm.find(xml_ns + "address").text
        man_json["prefix"] = \
            int(man_elm.find(xml_ns + "prefix").text)

    @decorater_log
    def _gen_json_loopback(self, json, xml, xml_ns):
        '''
            Obtain loopback IF information from xml message to be analyzed
            and set it for EC message storage dictionary object.
            Explanation about parameter:
                json:dictionary object for EC message storage
                xml:xml message to be analyzed
                xml_ns: name space
        '''
        loop_elm = self._find_xml_node(xml,
                                       xml_ns + "loopback-interface")
        loop_json = json["device"]["loopback-interface"]
        loop_json["address"] = \
            loop_elm.find(xml_ns + "address").text
        loop_json["prefix"] = \
            int(loop_elm.find(xml_ns + "prefix").text)

    @decorater_log
    def _gen_json_snmp(self, json, xml, xml_ns):
        '''
            Obtain SNMP information from xml message to be analyzed
            and set it for EC message storage dictionary object.
            Explanation about parameter:
                json:dictionary object for EC message storage
                xml:xml message to be analyzed
                xml_ns: name space
        '''
        snmp_elm = self._find_xml_node(xml,
                                       xml_ns + "snmp")
        temp_json = json["device"]["snmp"]
        temp_json["server-address"] = \
            snmp_elm.find(xml_ns + "server-address").text
        temp_json["community"] = \
            snmp_elm.find(xml_ns + "community").text

    @decorater_log
    def _gen_json_ntp(self, json, xml, xml_ns):
        '''
            Obtain NTP information from xml message to be analyzed
            and set it for EC message storage dictionary object.
            Explanation about parameter:
                json:dictionary object for EC message storage
                xml:xml message to be analyzed
                xml_ns: name space
        '''
        ntp_elm = self._find_xml_node(xml,
                                      xml_ns + "ntp")
        json["device"]["ntp"]["server-address"] = \
            ntp_elm.find(xml_ns + "server-address").text

    @decorater_log
    def _gen_json_ospf(self, json, xml, xml_ns):
        '''
            Obtain OSPF information from xml message to be analyzed
            and set it for EC message storage dictionary object.
            Explanation about parameter:
                json:dictionary object for EC message storage
                xml:xml message to be analyzed
                xml_ns: name space
        '''
        ospf_elm = self._find_xml_node(xml,
                                       xml_ns + "ospf")
        json["device"]["ospf"]["area-id"] = \
            int(ospf_elm.find(xml_ns + "area-id").text)
