#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmL2SliceEvpnControl.py
'''
Individual scenario to add L2 slice.
'''
import json
from lxml import etree
from EmMergeScenario import EmMergeScenario
import GlobalModule
from EmCommonLog import decorater_log


class EmL2SliceEvpnControl(EmMergeScenario):
    '''
    Class for adding L2 slice.
    '''


    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmL2SliceEvpnControl, self).__init__()

        self._scenario_name = "L2SliceEvpnControl"

        self.service = GlobalModule.SERVICE_L2_SLICE

        self._xml_ns = "{%s}" % GlobalModule.EM_NAME_SPACES[self.service]

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
                "device-leaf":
                {
                    "name": None,
                    "slice_name": None,
                    "merge_cp_value": 0,
                    "delete_cp_value": 0,
                    "replace_cp_value": 0,
                    "cp": [],
                    "dummy_cp": []
                }
            }

        xml_elm = etree.fromstring(device_message)

        GlobalModule.EM_LOGGER.debug(
            "device_message = %s", etree.tostring(xml_elm, pretty_print=True))

        device_elm = self._find_xml_node(xml_elm, self._xml_ns + "name")
        device_json_message["device-leaf"]["name"] = device_elm.text

        slice_elm = self._find_xml_node(xml_elm, self._xml_ns + "slice_name")
        device_json_message["device-leaf"]["slice_name"] = slice_elm.text

        merge_cp_value = 0
        delete_cp_value = 0
        replace_cp_value = 0

        vrf_elm = self._find_xml_node(xml_elm,
                                      self._xml_ns + "vrf")
        if vrf_elm is not None:
            device_json_message["device-leaf"]["vrf"] = {}
            vrf_name = vrf_elm.find(self._xml_ns + "vrf-name").text
            device_json_message["device-leaf"]["vrf"]["vrf-name"] = vrf_name

            vrf_id = vrf_elm.find(self._xml_ns + "vrf-id").text
            device_json_message["device-leaf"]["vrf"]["vrf-id"] = vrf_id

            if vrf_elm.find(self._xml_ns + "rt") is not None:
                vrf_rt = vrf_elm.find(self._xml_ns + "rt").text
                device_json_message["device-leaf"]["vrf"]["rt"] = vrf_rt

            if vrf_elm.find(self._xml_ns + "rd") is not None:
                vrf_rd = vrf_elm.find(self._xml_ns + "rd").text
                device_json_message["device-leaf"]["vrf"]["rd"] = vrf_rd

            if vrf_elm.find(self._xml_ns + "router-id") is not None:
                vrf_router_id = vrf_elm.find(self._xml_ns + "router-id").text
                device_json_message[
                    "device-leaf"]["vrf"]["router-id"] = vrf_router_id

            vrf_loopback = vrf_elm.find(self._xml_ns + "loopback")
            if vrf_loopback is not None:
                device_json_message["device-leaf"]["vrf"]["loopback"] = {}
                vrf_lp_addr = vrf_loopback.find(self._xml_ns + "address").text
                vrf_lp_px = int(
                    vrf_loopback.find(self._xml_ns + "prefix").text)
                device_json_message[
                    "device-leaf"]["vrf"]["loopback"]["address"] = vrf_lp_addr
                device_json_message[
                    "device-leaf"]["vrf"]["loopback"]["prefix"] = vrf_lp_px

            vrf_l3_vni = vrf_elm.find(self._xml_ns + "l3-vni")
            if vrf_l3_vni is not None:
                device_json_message["device-leaf"]["vrf"]["l3-vni"] = {}
                vrf_l3_vni_id = int(
                    vrf_l3_vni.find(self._xml_ns + "vni-id").text)
                vrf_l3_vni_vlan_id = int(
                    vrf_l3_vni.find(self._xml_ns + "vlan-id").text)
                device_json_message["device-leaf"]["vrf"]["l3-vni"]["vni-id"] = \
                    vrf_l3_vni_id
                device_json_message["device-leaf"]["vrf"]["l3-vni"]["vlan-id"] = \
                    vrf_l3_vni_vlan_id

        for cp_info in xml_elm.findall(self._xml_ns + "cp"):
            cp_message = \
                {
                    "operation": None,
                    "name": None,
                    "vlan-id": 0,
                    "qos": {}
                }
            if cp_info.get("operation") == "delete":
                cp_message["operation"] = "delete"
                delete_cp_value += 1
            else:
                cp_message["operation"] = "merge"
                merge_cp_value += 1

            cp_message["name"] = cp_info.find(self._xml_ns + "name").text
            cp_message["vlan-id"] = \
                int(cp_info.find(self._xml_ns + "vlan-id").text)

            port_mode = cp_info.find(self._xml_ns + "port-mode")
            if port_mode is not None:
                cp_message["port-mode"] = port_mode.text
            vni = cp_info.find(self._xml_ns + "vni")
            if vni is not None:
                cp_message["vni"] = int(vni.text)
            esi = cp_info.find(self._xml_ns + "esi")
            if (esi is not None) and (esi.get("operation") != "delete"):
                cp_message["esi"] = esi.text
            system_id = cp_info.find(self._xml_ns + "system-id")
            if (system_id is not None) and\
                    (system_id.get("operation") != "delete"):
                cp_message["system-id"] = system_id.text
            clag_id = cp_info.find(self._xml_ns + "clag-id")
            if clag_id is not None:
                cp_message["clag-id"] = int(clag_id.text)
            speed = cp_info.find(self._xml_ns + "speed")
            if speed is not None:
                cp_message["speed"] = speed.text

            qos_info = self._find_xml_node(cp_info,
                                           self._xml_ns + "qos")
            if qos_info is not None:
                inflow_shaping_rate = qos_info.find(
                    self._xml_ns + "inflow-shaping-rate")
                if inflow_shaping_rate is not None:
                    cp_message["qos"]["inflow-shaping-rate"] = float(
                        inflow_shaping_rate.text)

                outflow_shaping_rate = qos_info.find(
                    self._xml_ns + "outflow-shaping-rate")
                if outflow_shaping_rate is not None:
                    cp_message["qos"]["outflow-shaping-rate"] = float(
                        outflow_shaping_rate.text)

                remark_menu = qos_info.find(self._xml_ns + "remark-menu")
                if remark_menu is not None:
                    cp_message["qos"]["remark-menu"] = remark_menu.text

                egress_menu = qos_info.find(self._xml_ns + "egress-menu")
                if egress_menu is not None:
                    cp_message["qos"]["egress-menu"] = egress_menu.text

            irb_info = self._find_xml_node(cp_info,
                                           self._xml_ns + "irb")
            if irb_info is not None:
                cp_message["irb"] = {
                    "physical-ip-address": {},
                    "virtual-mac-address": None,
                    "virtual-gateway": {}
                }
                physical_addr = irb_info.find(
                    self._xml_ns + "physical-ip-address")
                physical_ip_address = physical_addr.find(
                    self._xml_ns + "address").text
                cp_message["irb"]["physical-ip-address"][
                    "address"] = physical_ip_address
                physical_ip_prefix = physical_addr.find(
                    self._xml_ns + "prefix").text
                cp_message["irb"]["physical-ip-address"][
                    "prefix"] = int(physical_ip_prefix)
                if irb_info.find(self._xml_ns + "virtual-mac-address") \
                        is not None:
                    vr_addr = irb_info.find(
                        self._xml_ns + "virtual-mac-address").text
                    cp_message["irb"]["virtual-mac-address"] = vr_addr
                vr_gw = irb_info.find(self._xml_ns + "virtual-gateway")
                vr_address = vr_gw.find(self._xml_ns + "address").text
                cp_message["irb"]["virtual-gateway"]["address"] = vr_address
                vr_prefix = vr_gw.find(self._xml_ns + "prefix").text
                cp_message["irb"]["virtual-gateway"]["prefix"] = int(vr_prefix)

            if (esi is not None and esi.get("operation") == "delete") and\
                    (system_id is not None and
                     system_id.get("operation") == "delete"):
                cp_message["operation"] = "delete"
                cp_message["system-id"] = "0"
                cp_message["esi"] = "0"

            tmp = cp_info.find(self._xml_ns + "q-in-q")
            if tmp is not None:
                cp_message["q-in-q"] = True

            device_json_message["device-leaf"]["cp"].append(cp_message)

        if self._find_xml_node(xml_elm, self._xml_ns + "dummy_vlan"):
            dummy_vlans = xml_elm.findall(self._xml_ns + "dummy_vlan")
            self._creating_json_dummy_vlan(
                dummy_vlans, device_json_message)

        if self._find_xml_node(xml_elm, self._xml_ns + "multi-homing"):
            multi_homing = xml_elm.find(self._xml_ns + "multi-homing")
            self._creating_json_multi_homing(
                multi_homing, device_json_message)

        if not len(device_json_message["device-leaf"]["cp"]):
            del device_json_message["device-leaf"]["cp"]
        if not len(device_json_message["device-leaf"]["dummy_cp"]):
            del device_json_message["device-leaf"]["dummy_cp"]

        device_json_message["device-leaf"]["merge_cp_value"] = merge_cp_value

        device_json_message["device-leaf"][
            "delete_cp_value"] = delete_cp_value

        device_json_message["device-leaf"][
            "replace_cp_value"] = replace_cp_value

        GlobalModule.EM_LOGGER.debug(
            "device__json_message = %s", device_json_message)

        return json.dumps(device_json_message)

    @decorater_log
    def _creating_json_dummy_vlan(self, xml_elm, ms_json):
        '''
        Shaping dummy VLAN element into JSON style
        Explanatin about parameter：
            xml_elm: message for each device
            ms_json: JSON message
        Explanation about return value
            ms_json: JSON message
        '''

        for dummy_vlan_info in xml_elm:
            dum_vlan_message = \
                {
                    "operation": None,
                    "vlan-id": 0
                }
            if dummy_vlan_info.get("operation") == "delete":
                dum_vlan_message["operation"] = "delete"
            else:
                dum_vlan_message["operation"] = "merge"

            dum_vlan_message["vlan-id"] = \
                int(dummy_vlan_info.find(self._xml_ns + "vlan-id").text)

            if dummy_vlan_info.find(self._xml_ns + "vni") is not None:
                dum_vlan_message["vni"] = \
                    int(dummy_vlan_info.find(self._xml_ns + "vni").text)

            irb_info = self._find_xml_node(dummy_vlan_info,
                                           self._xml_ns + "irb")
            if irb_info is not None:
                dum_vlan_message["irb"] = {
                    "physical-ip-address": {},
                    "virtual-mac-address": None
                }
                physical_addr = irb_info.find(
                    self._xml_ns + "physical-ip-address")
                physical_ip_address = physical_addr.find(
                    self._xml_ns + "address").text
                dum_vlan_message["irb"]["physical-ip-address"][
                    "address"] = physical_ip_address
                physical_ip_prefix = physical_addr.find(
                    self._xml_ns + "prefix").text
                dum_vlan_message["irb"]["physical-ip-address"][
                    "prefix"] = int(physical_ip_prefix)
                if irb_info.find(self._xml_ns + "virtual-mac-address") \
                        is not None:
                    vr_addr = irb_info.find(
                        self._xml_ns + "virtual-mac-address").text
                    dum_vlan_message["irb"]["virtual-mac-address"] = vr_addr

            ms_json["device-leaf"]["dummy_cp"].append(dum_vlan_message)

    @decorater_log
    def _creating_json_multi_homing(self, xml_elm, ms_json):
        '''
        Shaping multihoming configuration element into JSON style
        Explanation about parameter：
            xml_elm: message for each device
            ms_json: JSON message
        Explanation about return value
            ms_json: JSON message
        '''
        multi_homing_message = {
            "anycast": {},
            "interface": {},
            "clag": {
                "backup": {},
                "peer": {}
            }
        }

        anycast = xml_elm.find(self._xml_ns + "anycast")
        any_addr = anycast.find(self._xml_ns + "address").text
        multi_homing_message["anycast"]["address"] = any_addr

        anycast_id = GlobalModule.EMSYSCOMUTILDB.get_anycast_id(any_addr)
        multi_homing_message["anycast"]["id"] = anycast_id

        interface = xml_elm.find(self._xml_ns + "interface")
        multi_homing_message["interface"][
            "address"] = interface.find(self._xml_ns + "address").text
        multi_homing_message["interface"][
            "prefix"] = int(interface.find(self._xml_ns + "prefix").text)

        clag = xml_elm.find(self._xml_ns + "clag")
        backup = clag.find(self._xml_ns + "backup")
        multi_homing_message["clag"][
            "backup"]["address"] = backup.find(self._xml_ns + "address").text
        peer = clag.find(self._xml_ns + "peer")
        multi_homing_message["clag"][
            "peer"]["address"] = peer.find(self._xml_ns + "address").text

        ms_json["device-leaf"]["multi-homing"] = multi_homing_message

    @staticmethod
    @decorater_log
    def _gen_netconf_message(element, slice_name):
        '''
        Device name:Create Netconf message (json letter strings).
        '''
        slice_elm = etree.Element("slice_name")
        slice_elm.text = slice_name
        element.append(slice_elm)
        return etree.tostring(element)
