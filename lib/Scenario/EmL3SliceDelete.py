#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmL3SliceDelete.py
'''
Individual scenario for deleting L3 slice.
'''
import json
from lxml import etree
from EmDeleteScenario import EmDeleteScenario
import GlobalModule
from EmCommonLog import decorater_log


class EmL3SliceDelete(EmDeleteScenario):
    '''
        Class for L3 slice deletion.
    '''

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmL3SliceDelete, self).__init__()

        self.service = GlobalModule.SERVICE_L3_SLICE

        self._xml_ns = "{%s}" % GlobalModule.EM_NAME_SPACES[self.service]

        self._scenario_name = "L3SliceDelete"

        self.device_type = "device-leaf"

        self.device_force_list = []

        self.device_force_deleting_list = []

    @decorater_log
    def _process_scenario(self,
                          device_message=None,
                          transaction_id=None,
                          order_type=None,
                          condition=None,
                          device_name=None,
                          force=False):
        '''
        Executes scenario for each device.
        Explanation about parameter:
            device_message: Message for each device (byte)            
            transaction_id:  TransactionID (uuid)
            order_type: Order type (str)
            condition: Thread control information (condition object)
            device_name: Device name (str)
            force: Flag of deletion to be forced(boolean)
        Explanation about return value
            None:
        '''
        if force:
            self.device_force_list.append(device_name)
        super(EmL3SliceDelete, self)._process_scenario(
            device_message=device_message,
            transaction_id=transaction_id,
            order_type=order_type,
            condition=condition,
            device_name=device_name,
            force=force)

    @decorater_log
    def _setting_device(self,
                        device_name=None,
                        order_type=None,
                        transaction_id=None,
                        json_message=None):
        '''
        Sets device.
        Explanation about parameter:
            device_name: Device name (str)
            order_type: Order type (str)
            transaction_id:  TransactionID (uuid)
            json_message: EC message for json type (str)
        Explanation about return value
            None:
        '''
        com_driver = self.com_driver_list[device_name]
        is_result = com_driver.delete_device_setting(device_name,
                                                     self.service,
                                                     order_type,
                                                     json_message)
        if is_result == GlobalModule.COM_DELETE_OK:
            GlobalModule.EM_LOGGER.debug("delete_device_setting OK")
        else:
            if is_result == GlobalModule.COM_DELETE_VALICHECK_NG:
                GlobalModule.EM_LOGGER.debug(
                    "delete_device_setting validation check NG")
                GlobalModule.EM_LOGGER.warning(
                    "%s Scenario:%s Device:%s NG:9" +
                    "(processing failure(validation check NG))",
                    self.error_code02, self._scenario_name, device_name)

                self._find_subnormal(transaction_id, order_type, device_name,
                                     GlobalModule.TRA_STAT_PROC_ERR_CHECK,
                                     True, False)
            else:
                GlobalModule.EM_LOGGER.debug("delete_device_setting delete NG")
                if device_name in self.device_force_list:
                    GlobalModule.EM_LOGGER.debug(
                        "Enforced deletion flag enabled")
                    self.device_force_deleting_list.append(device_name)
                    return
                else:
                    GlobalModule.EM_LOGGER.debug(
                        "Invalid forced deletion flag")
                    GlobalModule.EM_LOGGER.warning(
                        "%s Scenario:%s Device:%s NG:16" +
                        "(processing failure(device setting NG))",
                        self.error_code02, self._scenario_name, device_name)
                    self._find_subnormal(
                        transaction_id,
                        order_type,
                        device_name,
                        GlobalModule.TRA_STAT_PROC_ERR_SET_DEV,
                        True,
                        False)
            raise Exception("delete_device_setting NG")

    @decorater_log
    def _reserve_device(self,
                        device_name=None,
                        order_type=None,
                        transaction_id=None):
        '''
        Reserves device setting.
        Explanation about parameter:
            device_name: Device name (str)
            order_type: Order type (str)
            transaction_id:  Transaction ID (uuid)
        Explanation about return value
            None:
        '''
        if device_name not in self.device_force_deleting_list:
            super(EmL3SliceDelete, self)._reserve_device(
                device_name=device_name,
                order_type=order_type,
                transaction_id=transaction_id)

    @decorater_log
    def _enable_device(self,
                       device_name=None,
                       order_type=None,
                       transaction_id=None):
        '''
        Enables device setting.
        Explanation about parameter:
            device_name: Device name (str)
            order_type: Order type (str)
            transaction_id:  TransactionID (uuid)
        Explanation about return value
            None:
        '''
        if device_name not in self.device_force_deleting_list:
            super(EmL3SliceDelete, self)._enable_device(
                device_name=device_name,
                order_type=order_type,
                transaction_id=transaction_id)

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
                "device-leaf": {
                    "name": None,
                    "slice_name": None,
                    "cp_value": 0,
                    "cp": []
                }
            }

        xml_elm = etree.fromstring(device_message)

        GlobalModule.EM_LOGGER.debug(
            "device_message = %s", etree.tostring(xml_elm, pretty_print=True))

        device_elm = self._find_xml_node(
            xml_elm, self._xml_ns + "name")
        device_json_message["device-leaf"]["name"] = device_elm.text

        slice_elm = self._find_xml_node(xml_elm, self._xml_ns + "slice_name")
        device_json_message["device-leaf"]["slice_name"] = slice_elm.text

        cp_tag = self._xml_ns + "cp"
        for cp_get in xml_elm.findall(".//" + cp_tag):
            cp_list = \
                {
                    "operation": None,
                    "name": None,
                    "vlan-id": 0,
                    "vrrp": {
                        "operation": None
                    },
                    "bgp": {
                        "operation": None,
                    },
                    "static": {
                        "route": [],
                        "route6": []

                    }
                }

            cp_list["name"] = \
                cp_get.find(self._xml_ns + "name").text
            cp_list["vlan-id"] = \
                int(cp_get.find(self._xml_ns + "vlan-id").text)
            operation = cp_get.get("operation")
            if operation == "delete":
                cp_list["operation"] = "delete"
            else:
                cp_list["operation"] = "merge"

            vrrp_elm = self._find_xml_node(cp_get,
                                           self._xml_ns + "vrrp")
            if vrrp_elm is not None:
                vrrp_operation = vrrp_elm.get("operation")

                if vrrp_operation == "delete":
                    cp_list["vrrp"]["operation"] = "delete"
                else:
                    cp_list["vrrp"]["operation"] = "merge"
            else:
                del cp_list["vrrp"]
                
            bgp_elm = self._find_xml_node(cp_get,
                                          self._xml_ns + "bgp")
            if bgp_elm is not None:
                bgp_operation = bgp_elm.get("operation")

                if bgp_operation == "delete":
                    cp_list["bgp"]["operation"] = "delete"
                else:
                    cp_list["bgp"]["operation"] = "merge"
            else:
                del cp_list["bgp"]

            static_elm = self._find_xml_node(cp_get,
                                             self._xml_ns + "static")
            if static_elm is not None:
                if static_elm.find(self._xml_ns + "route") is not None:
                    ipv4_tag = self._xml_ns + "route"
                    for route_ipv4 in static_elm.findall(".//" + ipv4_tag):
                        route_info = \
                            {
                                "operation": None,
                                "address": None,
                                "prefix": 0,
                                "nexthop": None
                            }
                        route_operation = route_ipv4.get("operation")
                        if route_operation == "delete":
                            route_info["operation"] = "delete"
                        else:
                            route_info["operation"] = "merge"

                        route_info["address"] = \
                            route_ipv4.find(self._xml_ns + "address").text
                        route_info["prefix"] = \
                            int(route_ipv4.find(self._xml_ns + "prefix").text)
                        route_info["nexthop"] = \
                            route_ipv4.find(self._xml_ns + "next-hop").text

                        cp_list["static"]["route"].append(route_info.copy())

                    route_ipv4_len = len(cp_list["static"]["route"])
                    cp_list["static"]["route_value"] = route_ipv4_len
                else:
                    del cp_list["static"]["route"]

                if static_elm.find(self._xml_ns + "route6") is not None:
                    ipv6_tag = self._xml_ns + "route6"
                    for route_ipv6 in static_elm.findall(".//" + ipv6_tag):
                        route6_info = \
                            {
                                "operation": None,
                                "address": None,
                                "prefix": 0,
                                "nexthop": None
                            }
                        route6_operation = route_ipv6.get("operation")
                        if route6_operation == "delete":
                            route6_info["operation"] = "delete"
                        else:
                            route6_info["operation"] = "merge"

                        route6_info["address"] = \
                            route_ipv6.find(self._xml_ns + "address").text
                        route6_info["prefix"] = \
                            int(route_ipv6.find(self._xml_ns + "prefix").text)
                        route6_info["nexthop"] = \
                            route_ipv6.find(self._xml_ns + "next-hop").text

                        cp_list["static"]["route6"].append(route6_info.copy())

                    route_ipv6_len = len(cp_list["static"]["route6"])
                    cp_list["static"]["route6_value"] = route_ipv6_len
                else:
                    del cp_list["static"]["route6"]
            else:
                del cp_list["static"]

            device_json_message["device-leaf"]["cp"].append(cp_list)

        device_json_message["device-leaf"]["cp_value"] = \
            len(device_json_message["device-leaf"]["cp"])

        GlobalModule.EM_LOGGER.debug(
            "device__json_message = %s", device_json_message)

        return json.dumps(device_json_message)

    @staticmethod
    @decorater_log
    def _gen_netconf_message(element, slice_name):
        '''
        Device name:Create Netconf message (json letter string).
        '''
        slice_elm = etree.Element("slice_name")
        slice_elm.text = slice_name
        element.append(slice_elm)
        return etree.tostring(element)
