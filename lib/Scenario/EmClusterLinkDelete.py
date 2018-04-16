#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2018 Nippon Telegraph and Telephone Corporation
# Filename: EmClusterLinkDelete.py
'''
Individual scenario for deleting inter-cluster link.
'''
import json
from lxml import etree
from EmDeleteScenario import EmDeleteScenario
import GlobalModule
from EmCommonLog import decorater_log


class EmClusterLinkDelete(EmDeleteScenario):
    '''
    Class for deleting inter-cluster link.
    '''

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''
        super(EmClusterLinkDelete, self).__init__()
        self.service = GlobalModule.SERVICE_CLUSTER_LINK
        self._xml_ns = "{%s}" % GlobalModule.EM_NAME_SPACES[self.service]
        self._scenario_name = "ClusterLinkDelete"
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
                "cluster-link-interface_value": 0,
                "cluster-link-interface": []
            }
        }

        xml_elm = etree.fromstring(device_message)

        GlobalModule.EM_LOGGER.debug(
            "device_message = %s", etree.tostring(xml_elm, pretty_print=True))

        self._gen_json_name(device_json_message, xml_elm, self._xml_ns)

        self._gen_json_cluster_link(
            device_json_message, xml_elm, self._xml_ns)

        self._gen_json_cluster_link_value(device_json_message)

        GlobalModule.EM_LOGGER.debug(
            "device__json_message = %s", device_json_message)

        return json.dumps(device_json_message)

    @decorater_log
    def _gen_json_cluster_link(self, json, xml, xml_ns):
        '''
            Obtain inter-cluster physical IF information from xml message to
            be analyzed and set it for EC message storage dictionary object.
            Explanation about parameter:
                json:dictionary object for EC message storage
                xml:xml message to be analyzed
                xml_ns:Name space
                service:Service name
                order:Order name
        '''

        cls_link_elm = xml.findall(xml_ns + "cluster-link")
        for cls_link in cls_link_elm:
            cls_link_name = cls_link.find(xml_ns + "name").text
            cluster_name_param = {
                "name": cls_link_name
            }
            json["device"]["cluster-link-interface"].append(cluster_name_param)

    @decorater_log
    def _gen_json_cluster_link_value(self, json):
        '''
            Obtain inter-cluster physical IF information count
            and set it for EC message storage dictionary object.
            Explanation about parameter:
                json:dictionary object for EC message storage
        '''

        json["device"]["cluster-link-interface_value"] = \
            len(json["device"]["cluster-link-interface"])
