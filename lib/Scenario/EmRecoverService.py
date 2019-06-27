#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmRecoverService.py
'''
Individual scenario of recover service
'''
import json
from lxml import etree
import EmRecover
import GlobalModule
from EmCommonLog import decorater_log


class EmRecoverService(EmRecover.EmRecover):
    '''
    Scenario class for recover service
    '''

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmRecoverService, self).__init__()
        
        self.service = GlobalModule.SERVICE_RECOVER_SERVICE

        self._xml_ns = "{%s}" % GlobalModule.EM_NAME_SPACES[self.service]

        self.scenario_name = "RecoverService"

    @decorater_log
    def _creating_json(self, device_message):
        '''
        Generates JSON using EC message (XML) divided for each device and
        device registration information acquired from DB.
        Sets QoS information specific to "resetting service".

        Explanation about return value:
            device_message: message for each device
        Explanation about return value:
            device_json_message: JSON message
        '''
        json_message = super(EmRecoverService, self)._creating_json(
            device_message)

        device_json_message = json.loads(json_message)

        xml_elm = etree.fromstring(device_message)

        self._gen_json_qos(
            device_json_message, xml_elm, self._xml_ns)

        GlobalModule.EM_LOGGER.debug(
            "device__json_message = %s", device_json_message)

        return json.dumps(device_json_message)

    @decorater_log
    def _gen_json_qos(self, json, xml, xml_ns):
        '''
            Obtain QoS update information from xml message to be analyzed and
            set it for EC message storage dictionary object.
            Explanation about paramete：
                json：Dictionary object for EC message storage
                xml：Xml message to be analyzed
                xml_ns：Name space

        '''
        qos_message = {}
        qos_elm = self._find_xml_node(xml, xml_ns + "qos")
        if qos_elm is None:
            return

        inflow_shaping_rate = qos_elm.find(xml_ns + "inflow-shaping-rate")
        if inflow_shaping_rate is not None:
            qos_message.update({"inflow-shaping-rate": {}})
            if inflow_shaping_rate.get("operation") == "delete":
                qos_message["inflow-shaping-rate"]["operation"] = "delete"
            else:
                qos_message["inflow-shaping-rate"]["operation"] = "merge"
                qos_message[
                    "inflow-shaping-rate"]["value"] = float(inflow_shaping_rate.text)

        outflow_shaping_rate = qos_elm.find(xml_ns + "outflow-shaping-rate")
        if outflow_shaping_rate is not None:
            qos_message.update({"outflow-shaping-rate": {}})
            if outflow_shaping_rate.get("operation") == "delete":
                qos_message["outflow-shaping-rate"]["operation"] = "delete"
            else:
                qos_message["outflow-shaping-rate"]["operation"] = "merge"
                qos_message[
                    "outflow-shaping-rate"]["value"] = float(outflow_shaping_rate.text)

        remark_menu = qos_elm.find(xml_ns + "remark-menu")
        if remark_menu is not None:
            qos_message.update({"remark-menu": {}})
            if remark_menu.get("operation") == "delete":
                qos_message["remark-menu"]["operation"] = "delete"
            else:
                qos_message["remark-menu"]["operation"] = "merge"
                qos_message["remark-menu"]["value"] = remark_menu.text

        egress_menu = qos_elm.find(xml_ns + "egress-menu")
        if egress_menu is not None:
            qos_message.update({"egress-menu": {}})
            if egress_menu.get("operation") == "delete":
                qos_message["egress-menu"]["operation"] = "delete"
            else:
                qos_message["egress-menu"]["operation"] = "merge"
                qos_message["egress-menu"]["value"] = egress_menu.text

        json["device"]["qos"] = qos_message
