# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmACLFilterMerge.py
'''
Individual scenario for ACLFilter generation
'''
import json
from lxml import etree
import ipaddress
from EmMergeScenario import EmMergeScenario
import GlobalModule
from EmCommonLog import decorater_log


class EmACLFilterMerge(EmMergeScenario):
    '''
    Class for ACLFilter configuration
    '''


    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmACLFilterMerge, self).__init__()

        self.service = GlobalModule.SERVICE_ACL_FILTER

        self._xml_ns = "{%s}" % GlobalModule.EM_NAME_SPACES[self.service]

        self._scenario_name = "ACLFilterMerge"

        self.device_type = "device-leaf"

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
                    "filter": []
                }
            }

        xml_elm = etree.fromstring(device_message)

        GlobalModule.EM_LOGGER.debug(
            "device_message = %s", etree.tostring(xml_elm, pretty_print=True))

        self._gen_json_name(
            device_json_message, xml_elm, self._xml_ns)

        self._gen_json_acl_filter(
            device_json_message, xml_elm, self._xml_ns)

        GlobalModule.EM_LOGGER.debug(
            "device__json_message = %s", device_json_message)

        return json.dumps(device_json_message)

    @decorater_log
    def _gen_json_acl_filter(self, json, xml, xml_ns):
        '''
            Obtain ACL configuration information from xml message to be analyzed and
            set it for EC message storage dictionary object.
                Explanation about parameter:
                json:dictionary object for EC message storage
                xml:xml message to be analyzed
                xml_ns:Name space
        '''
        filter_tag = xml_ns + "filter"
        for filter_get in xml.findall(".//" + filter_tag):
            filter_dict = {"filter_id": 0, "term": []}
            filter_dict["filter_id"] = int(
                filter_get.find(xml_ns + "filter_id").text)
            filter_dict["term"] = self._create_term_list(xml_ns, filter_get)
            json["device"]["filter"].append(filter_dict)

    @decorater_log
    def _create_term_list(self, xml_ns, filter_get):
        out_list = []
        acl_term_tag = xml_ns + "term"
        for acl_term_get in filter_get.findall(".//" + acl_term_tag):
            acl_term_item = {}
            acl_term_items = self._term_items(acl_term_get)
            acl_term_item.update(acl_term_items)

            source_mac_address = self._find_xml_node(
                acl_term_get, xml_ns + "source-mac-address")
            if source_mac_address is not None:
                source_mac_list = self._analysis_address(
                    source_mac_address.text)
                acl_term_item.update(
                    {"source-mac-address": source_mac_list})

            destination_mac_address = self._find_xml_node(
                acl_term_get, xml_ns + "destination-mac-address")

            if destination_mac_address is not None:
                destination_mac_list = self._analysis_address(
                    destination_mac_address.text)
                acl_term_item.update(
                    {"destination-mac-address": destination_mac_list})

            source_port = self._find_xml_node(
                acl_term_get, xml_ns + "source-port")
            if source_port is not None:
                acl_term_item["source-port"] = (acl_term_get.find(
                    self._xml_ns + "source-port").text)

            destination_port = self._find_xml_node(
                acl_term_get, xml_ns + "destination-port")
            if destination_port is not None:
                acl_term_item["destination-port"] = (acl_term_get.find(
                    self._xml_ns + "destination-port").text)

            source_ip_address = self._find_xml_node(
                acl_term_get, xml_ns + "source-ip-address")
            if source_ip_address is not None:
                source_ip_list = self._analysis_ip_address(
                    source_ip_address.text)
                acl_term_item.update(
                    {"source-ip-address": source_ip_list})

            destination_ip_address = self._find_xml_node(
                acl_term_get, xml_ns + "destination-ip-address")
            if destination_ip_address is not None:
                destination_ip_list = self._analysis_ip_address(
                    destination_ip_address.text)
                acl_term_item.update(
                    {"destination-ip-address": destination_ip_list})

            protocol = self._find_xml_node(
                acl_term_get, xml_ns + "protocol")
            if protocol is not None:
                acl_term_item["protocol"] = (acl_term_get.find(
                    self._xml_ns + "protocol").text)

            priority = self._find_xml_node(
                acl_term_get, xml_ns + "priority")
            if priority is not None:
                acl_term_item["priority"] = int(
                    acl_term_get.find(self._xml_ns + "priority").text)

            out_list.append(acl_term_item)
        return out_list

    @decorater_log
    def _term_items(self, acl_term_get):
        '''
            Obtain term items
            Explanation about parameter:
                acl_term_get: term data
            Explanation about return value
                term items
        '''
        acl_term_item = {}

        acl_term_item["term-name"] = str(acl_term_get.find(
            self._xml_ns + "term_name").text)
        acl_term_item["name"] = str(acl_term_get.find(
            self._xml_ns + "name").text)
        vlan_id = acl_term_get.find(self._xml_ns + "vlan-id")
        if vlan_id is not None:
            acl_term_item["vlan-id"] = str(vlan_id.text)
        acl_term_item["action"] = (acl_term_get.find(
            self._xml_ns + "action").text)
        acl_term_item["direction"] = (acl_term_get.find(
            self._xml_ns + "direction").text)

        return acl_term_item

    def _analysis_ip_address(self, ec_address):
        '''
            Obtain ip address and version
            Explanation about parameter:
                ec_address: EC ip information
            Explanation about return value
                ip address and version
        '''
        tmp_addr = self._analysis_address(ec_address)
        address = tmp_addr["address"]
        ip_version = ipaddress.ip_address(unicode(address)).version
        tmp_addr["ip_version"] = int(ip_version)

        return tmp_addr

    def _analysis_address(self, ec_address):
        '''
            Obtain ip address and prefix
            Explanation about parameter:
                ec_address: EC ip information
            Explanation about return value
                ip address and prefix
        '''
        address, part, prefix = ec_address.rpartition("/")
        tmp_addr = {
            "address": str(address),
            "prefix": int(prefix)
        }
        return tmp_addr
