#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmBLeafScenario.py
from EmSeparateScenario import EmScenario
from EmCommonLog import decorater_log
import GlobalModule
'''
Scenario commonly used for B-Leaf
'''


class EmBLeafScenario(EmScenario):
    '''
    B-Leaf flavor
    '''


    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''
        pass

    @decorater_log
    def _gen_json_b_leaf_ospf(self, json, xml, xml_ns):
        '''
            Obtain OSPF information from xml message to be analyzed and
            set it for EC message storage dictionary object.
            Explanation about parameter:
                json:dictionary object for EC message storage
                xml:xml message to be analyzed
                xml_ns:Name space
        '''

        ospf_elm = self._find_xml_node(xml, xml_ns + "ospf")

        ospf_data = {"area-id": ospf_elm[0].text}

        vir_link = {"router-id": None}
        vir_elm = self._find_xml_node(ospf_elm, xml_ns + "virtual-link")
        if vir_elm is not None:
            if xml.find(xml_ns + "equipment") is None:
                if (vir_elm.get("operation") == "replace") or \
                        (vir_elm.get("operation") == "delete"):
                    vir_link = {"operation": "delete"}
                else:
                    vir_link = {"operation": "merge"}
            tmp_elm = vir_elm.find(xml_ns + "router-id")
            if tmp_elm is not None:
                vir_link["router-id"] = tmp_elm.text
            ospf_data["virtual-link"] = vir_link

        ospf_range = {"address": None,
                      "prefix": 0
                      }
        range_elm = self._find_xml_node(ospf_elm, xml_ns + "range")
        if range_elm is not None:
            tmp_elm = range_elm.find(xml_ns + "address")
            tmp_elm2 = range_elm.find(xml_ns + "prefix")
            if tmp_elm is not None:
                ospf_range["address"] = tmp_elm.text
                ospf_range["prefix"] = int(tmp_elm2.text)
            else:
                ospf_range = {}
            if xml.find(xml_ns + "equipment") is None:
                if range_elm.get("operation") == "delete":
                    ospf_range.update({"operation": "delete"})
                else:
                    ospf_range.update({"operation": "merge"})
            ospf_data["range"] = ospf_range

        GlobalModule.EM_LOGGER.debug('Created ospf_data = %s', ospf_data)

        return ospf_data
