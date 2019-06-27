#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmClusterLinkMarge.py
'''
Individual scenario to create inter-cluster link.
'''
import json
from lxml import etree
from EmMergeScenario import EmMergeScenario
import GlobalModule
from EmCommonLog import decorater_log


class EmClusterLinkMerge(EmMergeScenario):
    '''
    Class for creation of inter-cluster link.
    '''



    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmClusterLinkMerge, self).__init__()

        self.service = GlobalModule.SERVICE_CLUSTER_LINK

        self._xml_ns = "{%s}" % GlobalModule.EM_NAME_SPACES[self.service]

        self._scenario_name = "ClusterLinkMerge"

        self.device_type = "leaf-device"

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
                "cluster-link-physical-interface_value": 0,
                "cluster-link-physical-interface": [],
                "cluster-link-lag-interface_value": 0,
                "cluster-link-lag-interface": []
            }
        }

        xml_elm = etree.fromstring(device_message)

        GlobalModule.EM_LOGGER.debug(
            "device_message = %s", etree.tostring(xml_elm, pretty_print=True))

        self._gen_json_name(device_json_message, xml_elm, self._xml_ns)

        node_cluster = xml_elm.find(self._xml_ns + "cluster-link")
        if_type = node_cluster.find(self._xml_ns + "if_type").text

        if if_type in ("physical-if", "breakout-if"):
            self._gen_json_cluster_link_phy(
                device_json_message, xml_elm, self._xml_ns)

            self._gen_json_cluster_link_phy_value(device_json_message)

        elif if_type == "lag-if":
            self._gen_json_cluster_link_lag(
                device_json_message, xml_elm, self._xml_ns)

            self._gen_json_cluster_link_lag_value(device_json_message)

        GlobalModule.EM_LOGGER.debug(
            "device__json_message = %s", device_json_message)

        return json.dumps(device_json_message)

    @decorater_log
    def _gen_json_cluster_link_phy(self, json, xml, xml_ns):
        '''
            Obtain inter-cluster physical IF information from xml message to
            be analyzed and set it for EC message storage dictionary object.
            Explanation about parameter:
                json:dictionary object for EC message storage
                xml:xml message to be analyzed
                xml_ns:Name space
        '''

        cl_link_tag = xml_ns + "cluster-link"
        for cl_link_get in xml.findall(".//" + cl_link_tag):
            cl_link_list = \
                {
                    "name": None,
                    "address": None,
                    "prefix": None,
                    "condition": None
                }

            cl_link_list["name"] = \
                cl_link_get.find(xml_ns + "name").text

            cl_link_list["address"] = \
                cl_link_get.find(xml_ns + "address").text
            cl_link_list["prefix"] = \
                int(cl_link_get.find(xml_ns + "prefix").text)
            cl_link_list["condition"] = \
                self._find_xml_node(cl_link_get,
                                    xml_ns + "cluster-lagmem-interface",
                                    xml_ns + "condition").text

            ospf_elm = self._find_xml_node(cl_link_get,
                                           xml_ns + "ospf")
            ospf_metric = {
                "metric": int(ospf_elm.find(xml_ns + "metric").text)}

            cl_link_list.update({"ospf": ospf_metric})

            json["device"][
                "cluster-link-physical-interface"].append(cl_link_list)

    @decorater_log
    def _gen_json_cluster_link_phy_value(self, json):
        '''
            Obtain inter-cluster physical IF information count
            and set it for EC message storage dictionary object.
            Explanation about parameter:
                json:dictionary object for EC message storage
        '''

        json["device"]["cluster-link-physical-interface_value"] = \
            len(json["device"]["cluster-link-physical-interface"])

    @decorater_log
    def _gen_json_cluster_link_lag(self, json, xml, xml_ns):
        '''
            Obtain inter-cluster LAGIF IF information from xml message to
            be analyzed and set it for EC message storage dictionary object.
            Explanation about parameter:
                json:dictionary object for EC message storage
                xml:xml message to be analyzed
                xml_ns:Name space
        '''

        cl_link_tag = xml_ns + "cluster-link"
        for cl_link_get in xml.findall(".//" + cl_link_tag):
            cl_link_list = \
                {
                    "name": None,
                    "address": None,
                    "prefix": None,
                    "leaf-interface_value": 0,
                    "leaf-interface": []
                }

            cl_link_list["name"] = \
                cl_link_get.find(xml_ns + "name").text

            leaf_tag = xml_ns + "cluster-lagmem-interface"
            for leaf_int in xml.findall(".//" + leaf_tag):
                lagmem = \
                    {
                        "name": None,
                        "condition": None
                    }
                interface_name = leaf_int.find(xml_ns + "name").text
                lagmem["name"] = interface_name
                interface_con = leaf_int.find(xml_ns + "condition").text
                lagmem["condition"] = interface_con
                cl_link_list["leaf-interface"].append(lagmem)

            cl_link_list["leaf-interface_value"] =\
                len(cl_link_list["leaf-interface"])

            cl_link_list["address"] = \
                cl_link_get.find(xml_ns + "address").text
            cl_link_list["prefix"] = \
                int(cl_link_get.find(xml_ns + "prefix").text)

            ospf_elm = self._find_xml_node(cl_link_get,
                                           xml_ns + "ospf")
            ospf_metric = {
                "metric": int(ospf_elm.find(xml_ns + "metric").text)}

            cl_link_list.update({"ospf": ospf_metric})

            json["device"]["cluster-link-lag-interface"].append(cl_link_list)

    @decorater_log
    def _gen_json_cluster_link_lag_value(self, json):
        '''
            Obtain inter-cluster LAGIF information count
            and set it for EC message storage dictionary object.
            Explanation about parameter:
                json:dictionary object for EC message storage
        '''
        json["device"]["cluster-link-lag-interface_value"] = \
            len(json["device"]["cluster-link-lag-interface"])
