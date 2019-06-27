# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: JuniperDriver5100.py
'''
Individual section on driver
(JuniperDriver's driver(QFX5100-48S, QFX5100-24Q))
'''
import re
import ipaddress
from lxml import etree
import copy
import traceback
import GlobalModule
from EmSeparateDriver import EmSeparateDriver
from EmCommonLog import decorater_log


class JuniperDriver5100(EmSeparateDriver):
    '''
    Individual section on driver (JuniperDriver's driver)
                    (QFX5100-48S, QFX5100-24Q))
    '''

    _PORT_MODE_ACCESS = "access"
    _PORT_MODE_TRUNK = "trunk"
    _ATTR_OPE = "operation"
    _XML_LOG = "set xml node (parent = %s):\n%s"

    _DEFAULT_INTERNAL_LINK_COST = 100

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''
        self.as_super = super(JuniperDriver5100, self)
        self.as_super.__init__()
        self._MERGE = GlobalModule.ORDER_MERGE
        self._DELETE = GlobalModule.ORDER_DELETE
        self._REPLACE = GlobalModule.ORDER_REPLACE
        self._vpn_types = {"l2": 2, "l3": 3}
        self.list_enable_service = [self.name_spine,
                                    self.name_leaf,
                                    self.name_b_leaf,
                                    self.name_l2_slice,
                                    self.name_l3_slice,
                                    self.name_celag,
                                    self.name_internal_link,
                                    self.name_breakout,
                                    self.name_cluster_link,
                                    self.name_recover_node,
                                    self.name_recover_service,
                                    self.name_if_condition,
                                    ]
        self._lag_check = re.compile("^ae([0-9]{1,})")
        self._breakout_check = re.compile("[0-9]{1,}/[0-9]{1,}/([0-9]{1,})")
        tmp_get_mes = (
            '<filter>' +
            '<configuration></configuration>' +
            '</filter>')
        self.get_config_message = {
            self.name_l2_slice: tmp_get_mes,
            self.name_l3_slice: tmp_get_mes,
        }
        self._device_count_margin = 2
        self._device_type_leaf = "leaf"
        self._device_type_spine = "spine"

    @decorater_log
    def _send_control_signal(self,
                             device_name,
                             message_type,
                             send_message=None,
                             service_type=None,
                             operation=None):
        '''
        Send message to protocol processing section.
        Parameter:
            device_name ; Device name
            message_type ; Message type
            send_message : Send message
        Return value.
            Processed result ; Boolean （Result of send_control_signal)
            Message ; str （Result of send_control_signal)
        '''
        is_result, message = (self.as_super.
                              _send_control_signal(device_name,
                                                   message_type,
                                                   send_message))
        if not is_result and isinstance(message, str) and "<ok/>" in message:
            is_result = True
        return is_result, message

    @decorater_log
    def _get_conf_device_count(self,
                               lag_ifs=None,
                               device_info=None,
                               operation=None):
        '''
        device_count calculation
        Parameter:
            lag_ifs ; LAG Information（EC message）
            device_info ; DB Information
            operation ; Operation
        Return Value
            device_count
            (The maximum value of the LAGID (aeXX : XX) of the device) + 2)
        '''
        lag_id_set = set()
        del_if_name_set = set()

        for lag_if_ec in lag_ifs:
            if (operation == self._MERGE) or (operation is None):
                lag_id_set.add(lag_if_ec.get("LAG-ID"))
            else:
                del_if_name_set.add(lag_if_ec.get("IF-NAME"))

        if device_info is not None:
            for lag_if_db in device_info.get("lag", {}):
                if lag_if_db.get("if_name") in del_if_name_set:
                    pass
                else:
                    lag_id_set.add(lag_if_db.get("lag_if_id"))

        if len(lag_id_set) != 0:
            ret_val = max(lag_id_set) + self._device_count_margin
        else:
            ret_val = self._device_count_margin

        return ret_val


    @decorater_log
    def _set_configuration_node(self, xml_obj):
        '''
        Create configuration node.
        '''
        return self._set_xml_tag(xml_obj,
                                 "configuration",
                                 "xmlns",
                                 "http://xml.juniper.net/xnm/1.1/xnm",
                                 None)

    @decorater_log
    def _set_system_config(self, conf_node, host_name=None):
        '''
        Create system node. (Set the host-name)
        '''
        node_2 = self._set_xml_tag(conf_node, "system")
        self._set_xml_tag(node_2, "host-name", None, None, host_name)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (conf_node.tag, etree.tostring(node_2),),
            __name__)
        return node_2

    @decorater_log
    def _set_chassis_device_count(self, conf_node, device_count=None):
        '''
        Create device_count node. (Set LAG count)
        '''
        node_1 = self._xml_setdefault_node(conf_node, "chassis")
        node_2 = self._set_xml_tag(node_1, "aggregated-devices")
        node_3 = self._set_xml_tag(node_2, "ethernet")
        self._set_xml_tag(node_3,
                          "device-count",
                          self._ATTR_OPE,
                          self._REPLACE,
                          device_count)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (conf_node.tag, etree.tostring(node_1),),
            __name__)
        return node_1

    @decorater_log
    def _set_chassis_breakout(self,
                              conf_node,
                              breakout_ifs=[],
                              operation=None):
        '''
        Create chassis node. (set breakout)
        '''
        node_1 = self._xml_setdefault_node(conf_node, "chassis")

        for br_if in breakout_ifs:
            self._set_fpc_breakout(node_1, br_if, operation)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (conf_node.tag, etree.tostring(node_1),),
            __name__)
        return node_1

    @decorater_log
    def _set_fpc_breakout(self,
                          conf_node,
                          br_if=None,
                          operation=None):
        '''
        Create fpc node. (set breakout)
        '''
        attr, attr_val = self._get_attr_from_operation(operation)

        port_name = self._breakout_check.search(br_if["IF-NAME"]).groups()[0]

        node_2 = self._set_xml_tag(conf_node, "fpc")
        self._set_xml_tag(node_2, "name", None, None, 0)
        node_3 = self._set_xml_tag(node_2, "pic")
        self._set_xml_tag(node_3, "name", None, None, 0)
        node_4 = self._set_xml_tag(node_3, "port", attr, attr_val)
        self._set_xml_tag(node_4, "name", None, None, port_name)
        if operation != self._DELETE:
            self._set_xml_tag(
                node_4, "channel-speed", None, None, br_if["SPEED"])
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (conf_node.tag, etree.tostring(conf_node),),
            __name__)
        return conf_node

    @decorater_log
    def _set_interfaces_node(self, conf_node):
        '''
        Set interfaces.
        '''
        return self._xml_setdefault_node(conf_node, "interfaces")

    @decorater_log
    def _set_interface_loopback(self, if_node, lo_addr, lo_prefix):
        '''
        Set Loopback IF.
        '''
        node_1 = self._set_xml_tag(if_node, "interface")
        self._set_xml_tag(node_1, "interface_name", None, None, "lo0")
        node_2 = self._set_xml_tag(node_1, "unit")
        self._set_xml_tag(node_2, "name", None, None, "0")
        node_3 = self._set_xml_tag(node_2, "family")
        node_4 = self._set_xml_tag(node_3, "inet")
        node_5 = self._set_xml_tag(node_4, "address")
        self._set_xml_tag(node_5,
                          "source",
                          None,
                          None,
                          "%s/%s" % (lo_addr, lo_prefix))
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (if_node.tag, etree.tostring(node_1),),
            __name__)
        return if_node

    @decorater_log
    def _set_interface_lag_member(self,
                                  if_node,
                                  lag_mem_ifs=None,
                                  operation=None):
        '''
        Set LAG member IF.
        '''
        attr, attr_val = self._get_attr_from_operation(operation)

        if operation == self._REPLACE:
            attr, attr_val = self._get_attr_from_operation(
                lag_mem_ifs["OPERATION"])
        node_1 = self._set_xml_tag(if_node, "interface", attr, attr_val)
        self._set_xml_tag(node_1,
                          "interface_name",
                          None,
                          None,
                          lag_mem_ifs["IF-NAME"])
        if operation == self._DELETE:
            return node_1
        node_2 = self._set_xml_tag(node_1, "ether-options")
        node_3 = self._set_xml_tag(node_2, "ieee-802.3ad")
        bundle_val = lag_mem_ifs["LAG-IF-NAME"]
        self._set_xml_tag(node_3,
                          "bundle",
                          None,
                          None,
                          bundle_val)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (if_node.tag, etree.tostring(node_1),),
            __name__)
        return node_1

    @decorater_log
    def _set_interface_physical(self,
                                if_node,
                                if_name=None,
                                operation=None):
        '''
        Set physical IF.
        '''
        attr, attr_val = self._get_attr_from_operation(operation)

        node_1 = self._set_xml_tag(if_node,
                                   "interface",
                                   attr,
                                   attr_val)
        self._set_xml_tag(node_1, "interface_name", None, None, if_name)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (if_node.tag, etree.tostring(node_1),),
            __name__)
        return node_1

    @decorater_log
    def _set_interface_lag(self,
                           if_node,
                           lag_if_name=None,
                           lag_links=None,
                           lag_speed=None,
                           operation=None):
        '''
        Set LAGIF. (can be LAG for CE as standalone)
        '''
        attr, attr_val = self._get_attr_from_operation(operation)

        node_1 = self._set_xml_tag(if_node,
                                   "interface",
                                   attr,
                                   attr_val)
        self._set_xml_tag(node_1, "interface_name", None, None, lag_if_name)
        if operation != self._DELETE:
            node_2 = self._set_xml_tag(node_1, "aggregated-ether-options")
            if operation == self._REPLACE:
                attr = self._ATRI_OPE
                attr_val = self._REPLACE
            self._set_xml_tag(node_2,
                              "minimum-links",
                              attr,
                              attr_val,
                              lag_links)
            if operation != self._REPLACE:
                self._set_xml_tag(node_2,
                                  "link-speed",
                                  None,
                                  None,
                                  lag_speed)
                node_3 = self._set_xml_tag(node_2, "lacp")
                self._set_xml_tag(node_3, "active")
                self._set_xml_tag(node_3, "periodic", None, None, "fast")
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (if_node.tag, etree.tostring(node_1),),
            __name__)
        return node_1

    @decorater_log
    def _set_interface_inner_links(self,
                                   if_node,
                                   operation=None,
                                   **ifs_info):
        '''
        Set all internal link IF.
            ifs_info:lag_ifs       :LAG internal link IF
                     lag_mem_ifs   :LAG member IF
                     phy_ifs       :Physical internal link IF
                     vpn_type      :VPN type (no need to set spine)
        '''
        vpn_type = ifs_info.get("vpn_type")

        for tmp_if in ifs_info.get("lag_mem_ifs", ()):
            self._set_interface_lag_member(if_node,
                                           lag_mem_ifs=tmp_if,
                                           operation=operation)
        for tmp_if in ifs_info.get("lag_ifs", ()):
            self._set_interface_inner_link(if_node,
                                           tmp_if,
                                           self._if_type_lag,
                                           vpn_type=vpn_type,
                                           operation=operation)
        for tmp_if in ifs_info.get("phy_ifs", ()):
            self._set_interface_inner_link(if_node,
                                           tmp_if,
                                           self._if_type_phy,
                                           vpn_type=vpn_type,
                                           operation=operation)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (if_node.tag, etree.tostring(if_node),),
            __name__)

    @decorater_log
    def _set_interface_inner_link(self,
                                  if_node,
                                  if_info,
                                  if_type,
                                  vpn_type=None,
                                  operation=None):
        '''
        Set internal link IF. (common for physical, LAG)
        '''

        if operation == self._DELETE:
            node_1 = self._set_xml_tag(if_node,
                                       "interface",
                                       self._ATTR_OPE,
                                       self._DELETE)
            self._set_xml_tag(node_1, "interface_name",
                              None,
                              None,
                              if_info.get("IF-NAME"))
            self.common_util_log.logging(
                None, self.log_level_debug,
                self._XML_LOG % (if_node.tag, etree.tostring(node_1),),
                __name__)
            return node_1
        if if_type == self._if_type_phy:
            node_1 = self._set_interface_physical(if_node,
                                                  if_info.get("IF-NAME"))
        else:
            node_1 = self._set_interface_lag(if_node,
                                             if_info.get("IF-NAME"),
                                             if_info.get("LAG-LINKS"),
                                             if_info.get("LAG-SPEED"),
                                             operation)
        mtu = 4110
        inner_vlan = 0
        if if_info.get("INNER-IF-VLAN") is not None:
            self._set_xml_tag(node_1, "vlan-tagging")
            mtu = 4114
            inner_vlan = if_info.get("INNER-IF-VLAN")
        if operation != self._REPLACE:
            self._set_xml_tag(node_1, "mtu", None, None, mtu)
            self._set_interface_unit_inner(node_1,
                                           if_info.get("IF-ADDR"),
                                           if_info.get("IF-PREFIX"),
                                           vpn_type,
                                           if_info.get("OPPOSITE-NODE-VPN"),
                                           inner_vlan
                                           )
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (if_node.tag, etree.tostring(node_1),),
            __name__)
        return node_1

    @decorater_log
    def _set_interface_condition(self,
                                 if_node,
                                 if_mes_ec=None,
                                 operation=None):
        '''
        Set IF open/close information(Common to physical, LAG)
        '''

        node_1 = self._set_xml_tag(if_node,
                                   "interface",
                                   None,
                                   None)
        self._set_xml_tag(node_1,
                          "interface_name",
                          None,
                          None,
                          if_mes_ec["IF-NAME"])
        if if_mes_ec["CONDITION"] == "enable":
            self._set_xml_tag(node_1, "disable", self._ATTR_OPE, self._DELETE)
        else:
            self._set_xml_tag(node_1, "disable")
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (if_node.tag, etree.tostring(node_1),),
            __name__)
        return node_1

    @decorater_log
    def _set_interface_cluster_link(self,
                                    if_node,
                                    if_info,
                                    if_type,
                                    vpn_type=None,
                                    operation=None):
        '''
        Set inter-cluster IF. (common for physical, LAG)
        '''

        if operation == self._DELETE:
            if if_type == self._if_type_phy:
                node_1 = self._set_xml_tag(if_node,
                                           "interface",
                                           self._ATTR_OPE,
                                           self._DELETE)
                self._set_xml_tag(node_1, "interface_name",
                                  None,
                                  None,
                                  if_info.get("IF-NAME"))
            else:
                node_1 = self._set_xml_tag(if_node,
                                           "interface",
                                           None,
                                           None)
                self._set_xml_tag(node_1, "interface_name",
                                  None,
                                  None,
                                  if_info.get("IF-NAME"))
                self._set_xml_tag(node_1, "mtu", self._ATTR_OPE, self._DELETE)
                node_2 = self._set_xml_tag(
                    node_1, "unit", self._ATTR_OPE, self._DELETE)
                self._set_xml_tag(node_2, "name", None, None, "0")
            self.common_util_log.logging(
                None, self.log_level_debug,
                self._XML_LOG % (if_node.tag, etree.tostring(node_1),),
                __name__)
            return node_1
        if if_type == self._if_type_phy:
            node_1 = self._set_interface_physical(if_node,
                                                  if_info.get("IF-NAME"))
        else:
            node_1 = self._set_xml_tag(if_node, "interface")
            self._set_xml_tag(node_1,
                              "interface_name",
                              None,
                              None,
                              if_info.get("IF-NAME"))
        self._set_xml_tag(node_1, "mtu", None, None, "4110")
        self._set_interface_unit_inner(
            node_1, if_info.get("IF-ADDR"), if_info.get("IF-PREFIX"), 3, 3)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (if_node.tag, etree.tostring(node_1),),
            __name__)
        return node_1

    @decorater_log
    def _set_interface_unit_inner(self,
                                  if_node,
                                  if_addr,
                                  if_prefix,
                                  vpn_type=None,
                                  opposite_vpn_type=None,
                                  inner_vlan=0):
        '''
        Create unit node of interface node
        for internal link/inter-cluster link.
        '''
        node_2 = self._set_xml_tag(if_node, "unit")
        self._set_xml_tag(node_2, "name", None, None, inner_vlan)
        node_3 = self._set_xml_tag(node_2, "family")
        node_4 = self._set_xml_tag(node_3, "inet")
        node_5 = self._set_xml_tag(node_4, "filter")
        node_6 = self._set_xml_tag(node_5, "input")
        self._set_xml_tag(
            node_6, "filter-name", None, None, "ipv4_filter_msf_input")
        node_5 = self._set_xml_tag(node_4, "address")
        self._set_xml_tag(node_5,
                          "source",
                          None,
                          None,
                          "%s/%s" % (if_addr, if_prefix))
        if vpn_type != 2 and opposite_vpn_type != 2:
            self._set_xml_tag(node_3, "mpls")
        if inner_vlan != 0:
            self._set_xml_tag(node_2, "vlan-id", text=inner_vlan)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (if_node.tag, etree.tostring(node_2),),
            __name__)
        return node_2

    @decorater_log
    def _set_device_routing_options(self,
                                    conf_node,
                                    loopback=None,
                                    vpn_type=None,
                                    as_number=None):
        '''
        Set the routing-options for the device.
        '''
        node_1 = self._set_xml_tag(conf_node, "routing-options")
        self._set_xml_tag(node_1, "router-id", None, None, loopback)
        if vpn_type is not None:
            self._set_xml_tag(
                node_1, "autonomous-system", None, None, as_number)
        node_2 = self._set_xml_tag(node_1, "forwarding-table")
        self._set_xml_tag(node_2, "export", None, None, "ECMP")
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (conf_node.tag, etree.tostring(node_1),),
            __name__)

    @decorater_log
    def _set_device_protocols(self, conf_node):
        '''
        Set the protocols for the device.
        '''
        return self._xml_setdefault_node(conf_node, "protocols")

    @decorater_log
    def _set_device_protocols_mpls(self,
                                   protocols_node):
        '''
        Set the mpls node for protocols. (should be set only by spine, L3Leaf)
        '''
        node_3 = self._set_xml_tag(protocols_node, "mpls")
        self._set_xml_tag(node_3, "ipv6-tunneling")
        node_4 = self._set_xml_tag(node_3, "interface")
        self._set_xml_tag(node_4, "interface_name", None, None, "all")
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (protocols_node.tag, etree.tostring(node_3),),
            __name__)

    @decorater_log
    def _set_device_protocols_bgp_common(self,
                                         protocols_node,
                                         loopback=None,
                                         vpn_type=None,
                                         as_number=None):
        '''
        Set bgp node for protocols. (except for neighbor)
        '''
        node_1 = self._set_xml_tag(protocols_node, "bgp")
        node_2 = self._set_xml_tag(node_1, "group")
        self._set_xml_tag(node_2, "group_name", None, None, "VPN")
        self._set_xml_tag(node_2, "type", None, None, "internal")
        self._set_xml_tag(node_2, "local-address", None, None, loopback)
        self._set_xml_tag(node_2, "hold-time", None, None, "90")
        node_3 = self._set_xml_tag(node_2, "family")
        if vpn_type == 2:
            node_4 = self._set_xml_tag(node_3, "evpn")
            self._set_xml_tag(node_4, "signaling")
        else:
            node_4 = self._set_xml_tag(node_3, "inet-vpn")
            self._set_xml_tag(node_4, "unicast")
            node_4 = self._set_xml_tag(node_3, "inet6-vpn")
            self._set_xml_tag(node_4, "unicast")
        self._set_xml_tag(node_2, "vpn-apply-export")
        self._set_xml_tag(node_2, "peer-as", None, None, as_number)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (protocols_node.tag, etree.tostring(node_1),),
            __name__)
        return node_2

    @decorater_log
    def _set_device_protocols_bgp_neighbors(self,
                                            group_node,
                                            l3v_lbb_infos=(),
                                            vpn_type=None):
        '''
        Set neighbor for bgp node of protocols.
        '''
        for l3v_lbb in l3v_lbb_infos:
            node_1 = self._set_xml_tag(group_node, "neighbor")
            self._set_xml_tag(
                node_1, "address", None, None, l3v_lbb["RR-ADDR"])
            if vpn_type == 3:
                node_2 = self._set_xml_tag(node_1, "import")
                self._set_xml_tag(node_2, "value", None, None, "VPN_import")
                node_2 = self._set_xml_tag(node_1, "export")
                self._set_xml_tag(node_2, "value", None, None, "VPN_export")
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (group_node.tag, etree.tostring(group_node)),
            __name__)

    def _set_b_leaf_ospf_data(self, conf_node, dev_reg_info):
        '''
        Create tag for updating B-Leaf. (can also be used to create B-Leaf)
        '''
        protocols_node = self._set_device_protocols(conf_node)
        if dev_reg_info.get("VIRTUAL-LINK-ROUTER-ID"):
            self._set_device_protocols_ospf_area_0(
                protocols_node,
                dev_reg_info["VIRTUAL-LINK-ROUTER-ID"],
                dev_reg_info["OSPF-AREA-ID"],
                dev_reg_info["VIRTUAL-LINK-OPERATION"])
        area_node = self._set_device_protocols_ospf_area_N(
            protocols_node,
            dev_reg_info["OSPF-AREA-ID"],
            dev_reg_info.get("RANGE-ADDRESS"),
            dev_reg_info.get("RANGE-PREFIX"),
            dev_reg_info.get("RANGE-OPERATION"))
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (conf_node.tag, etree.tostring(protocols_node)),
            __name__)
        return area_node

    @decorater_log
    def _set_device_protocols_ospf_area_0(self,
                                          protocols_node,
                                          peer_router=None,
                                          transit_area=None,
                                          operation=None):
        '''
        Set ospf node for protocols and set area0 (crossing between clusters).
        '''
        attr, attr_val = self._get_attr_from_operation(operation)

        node_1 = self._xml_setdefault_node(protocols_node, "ospf")
        node_2 = self._set_xml_tag(node_1, "area", attr, attr_val)
        self._set_xml_tag(node_2, "area_id", None, None, "0.0.0.0")
        if (attr_val != self._DELETE and
                peer_router is not None and transit_area is not None):
            set_area_id = "0.0.0.%s" % (transit_area,)
            node_3 = self._set_xml_tag(node_2, "virtual-link")
            self._set_xml_tag(node_3, "neighbor-id", None, None, peer_router)
            self._set_xml_tag(node_3, "transit-area", None, None, set_area_id)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (protocols_node.tag, etree.tostring(node_1)),
            __name__)
        return node_2

    @decorater_log
    def _set_device_protocols_ospf_area_N(self,
                                          protocols_node,
                                          area_id,
                                          range_addr=None,
                                          range_prefix=None,
                                          operation=None):
        '''
        Set ospf node for protocols and set areaN (crossing between clusters).
        Internal link should not be set here.
        '''
        attr, attr_val = self._get_attr_from_operation(operation)

        set_area_id = "0.0.0.%s" % (area_id,)

        node_1 = self._xml_setdefault_node(protocols_node, "ospf")
        node_2 = self._set_xml_tag(node_1, "area", None, None)
        self._set_xml_tag(node_2, "area_id", None, None, set_area_id)
        if range_addr and range_prefix is not None:
            node_3 = self._set_xml_tag(node_2, "area-range", attr, attr_val)
            tmp_addr = "%s/%s" % (range_addr, range_prefix)
            self._set_xml_tag(node_3, "area_range", None, None, tmp_addr)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (protocols_node.tag, etree.tostring(node_1)),
            __name__)
        return node_2

    @decorater_log
    def _set_ospf_area_interfaces(self,
                                  area_node,
                                  if_infos=(),
                                  **options):
        '''
        Set IF for the ospf/area node.
            options : service : Service name
                    ; operation : Operation type
                    ; is_loopback : Possibility of loopback setting
        '''
        service = options.get("service")
        operation = options.get("operation")
        is_loopback = options.get("is_loopback", False)

        for if_info in if_infos:
            self._set_ospf_area_interface(area_node,
                                          if_info.get("IF-NAME"),
                                          if_info.get("INNER-IF-VLAN"),
                                          if_info.get("OSPF-METRIC", 100),
                                          operation=operation)
        if is_loopback:
            self._set_ospf_area_lo_interface(area_node)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (area_node.tag, etree.tostring(area_node)),
            __name__)

    @decorater_log
    def _set_ospf_area_interface(self,
                                 area_node,
                                 if_name,
                                 inner_vlan=0,
                                 metric=100,
                                 operation=None):
        '''
        Set IF to ospf/area node
        '''
        attr, attr_val = self._get_attr_from_operation(operation)

        if inner_vlan is None:
            inner_vlan = 0

        node_2 = self._set_xml_tag(area_node, "interface",  attr, attr_val)
        self._set_xml_tag(node_2,
                          "interface_name",
                          None,
                          None,
                          "%s.%d" % (if_name, inner_vlan))
        if operation != self._DELETE:
            if operation != self._REPLACE:
                self._set_xml_tag(node_2, "interface-type", None, None, "p2p")
                self._set_xml_tag(node_2, "metric", None, None, metric)
            else:
                self._set_xml_tag(node_2,
                                  "metric",
                                  "operation",
                                  "replace",
                                  metric)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (area_node.tag, etree.tostring(node_2)),
            __name__)
        return node_2

    @decorater_log
    def _set_ospf_area_lo_interface(self, area_node):
        '''
        Set Loopback IF for ospf/area node.
        '''
        node_2 = self._set_xml_tag(area_node, "interface")
        self._set_xml_tag(node_2, "interface_name", None, None, "lo0.0")
        self._set_xml_tag(node_2, "passive")
        self._set_xml_tag(node_2, "metric", None, None, 10)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (area_node.tag, etree.tostring(node_2)),
            __name__)
        return node_2

    @decorater_log
    def _set_device_protocols_ldp(self, protocols_node, service_type):
        '''
        Set ldp node for protocols.
        '''
        node_1 = self._set_xml_tag(protocols_node, "ldp")

        if service_type == GlobalModule.SERVICE_SPINE:
            self._set_xml_tag(node_1, "egress-policy", None, None, "EL_To_LDP")
            self._set_xml_tag(node_1, "explicit-null")

        node_2 = self._set_xml_tag(node_1, "interface")
        self._set_xml_tag(node_2, "interface_name", None, None, "all")
        self._set_xml_tag(node_2, "hello-interval", None, None, "5")
        self._set_xml_tag(node_2, "hold-time", None, None, "15")
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (protocols_node.tag, etree.tostring(node_1)),
            __name__)

    @decorater_log
    def _set_device_protocols_evpn(self, protocols_node):
        node_1 = self._set_xml_tag(protocols_node, "evpn")
        self._set_xml_tag(node_1, "encapsulation", None, None, "vxlan")
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (protocols_node.tag, etree.tostring(node_1)),
            __name__)

    @decorater_log
    def _set_qos_policy_interfaces(self,
                                   conf_node,
                                   if_infos=(),
                                   service=None,
                                   operation=None):
        '''
        Set class-of-service node. (QoS policy setting)
        '''
        if not if_infos:
            return
        node_1 = self._set_xml_tag(conf_node, "class-of-service")
        node_2 = self._set_xml_tag(node_1, "interfaces")

        for if_info in if_infos:
            self._set_qos_policy_interface(
                node_2,
                if_info.get("IF-NAME"),
                service=service,
                operation=operation,
                port_mode=if_info.get("IF-PORT-MODE"))
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (conf_node.tag, etree.tostring(node_1)),
            __name__)
        return node_1

    @decorater_log
    def _set_qos_policy_interface(self,
                                  if_node,
                                  if_name,
                                  operation=None,
                                  **qos_info):
        '''
        Conduct interface settings for class-of-service node.
        Argument:qos_info
            service:Service name
        '''
        attr, attr_val = self._get_attr_from_operation(operation)

        node_1 = self._set_xml_tag(if_node,
                                   "interface",
                                   attr,
                                   attr_val)
        self._set_xml_tag(node_1, "interface_name", None, None, if_name)
        if operation != self._DELETE:
            service = qos_info.get("service")
            if service == self.name_l2_slice:
                port_mode = qos_info.get("port_mode")
                self._set_qos_policy_l2_slice(node_1, port_mode)
            elif service == self.name_l3_slice:
                self._set_qos_policy_l3_slice(node_1)
            else:
                self._set_qos_policy_inner_link(node_1)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (if_node.tag, etree.tostring(node_1)),
            __name__)

    @decorater_log
    def _set_qos_policy_inner_link_device_dependent(self, if_node):
        '''
        Conduct settings on device-dependent section
        for class-of-service node. (internal link/inter-cluster link)
        '''
        self._set_qos_forwarding_class_set(if_node,
                                           "fcs_unicast_af_and_be_class",
                                           "tcp_unicast_af_and_be")
        self._set_qos_forwarding_class_set(if_node,
                                           "fcs_unicast_ef_class",
                                           "tcp_unicast_ef")
        self._set_qos_forwarding_class_set(if_node,
                                           "fcs_multicast_class",
                                           "tcp_multicast")

    @decorater_log
    def _set_qos_policy_slice_device_dependent(self, if_node):
        '''
        Conduct the settings on device-dependent section
        of class-of-service node. (slice-adding-related)
        '''
        self._set_qos_forwarding_class_set(if_node,
                                           "fcs_unicast_af_and_be_class",
                                           "tcp_unicast_af_and_be_pt2")
        self._set_qos_forwarding_class_set(if_node,
                                           "fcs_unicast_ef_class",
                                           "tcp_unicast_ef_pt2")
        self._set_qos_forwarding_class_set(if_node,
                                           "fcs_multicast_class",
                                           "tcp_multicast_pt2")

    @decorater_log
    def _set_qos_forwarding_class_set(self, if_node, class_name, profile_name):
        '''
        Add forwarding-class-set node to if_node.
        '''
        node_1 = self._set_xml_tag(if_node, "forwarding-class-set")
        self._set_xml_tag(node_1, "class-name", None, None, class_name)
        node_2 = self._set_xml_tag(node_1, "output-traffic-control-profile")
        self._set_xml_tag(node_2, "profile-name", None, None, profile_name)
        return node_1

    @decorater_log
    def _set_qos_policy_inner_link(self, if_node):
        '''
        Conduct settings relating to internal Link of class-of-service node.
        '''
        self._set_qos_policy_inner_link_device_dependent(if_node)
        node_1 = self._set_xml_tag(if_node, "unit")
        self._set_xml_tag(node_1, "interface_unit_number", None, None, "0")
        node_2 = self._set_xml_tag(node_1, "rewrite-rules")
        node_3 = self._set_xml_tag(node_2, "exp")
        self._set_xml_tag(
            node_3, "rewrite-rule-name", None, None, "msf_mpls_exp_remark")
        node_1 = self._set_xml_tag(if_node, "classifiers")
        node_2 = self._set_xml_tag(node_1, "dscp")
        self._set_xml_tag(node_2,
                          "classifier-dscp-name",
                          None,
                          None,
                          "msf_unicast_dscp_classify")
        node_1 = self._set_xml_tag(if_node, "rewrite-rules")
        node_2 = self._set_xml_tag(node_1, "dscp")
        self._set_xml_tag(node_2,
                          "rewrite-rule-name",
                          None,
                          None,
                          "msf_dscp_remark")

    @decorater_log
    def _set_qos_policy_l2_slice(self, if_node, port_mode=None):
        '''
        Conduct settings relating to L2 slice of class-of-service node.
        '''
        self._set_qos_policy_slice_device_dependent(if_node)
        if port_mode == self._PORT_MODE_TRUNK:
            node_1 = self._set_xml_tag(if_node, "unit")
            self._set_xml_tag(
                node_1, "interface_unit_number", None, None, "0")
            node_2 = self._set_xml_tag(node_1, "rewrite-rules")
            node_3 = self._set_xml_tag(node_2, "ieee-802.1")
            self._set_xml_tag(
                node_3, "rewrite-rule-name", None,  None, "ce_l2_cos_remark")

    @decorater_log
    def _set_qos_policy_l3_slice(self, if_node):
        '''
        Conduct settings relating to L3 slice of class-of-service node.
        '''
        self._set_qos_policy_slice_device_dependent(if_node)
        node_1 = self._set_xml_tag(if_node, "classifiers")
        node_2 = self._set_xml_tag(node_1, "dscp")
        self._set_xml_tag(node_2,
                          "classifier-dscp-name",
                          None,
                          None,
                          "ce_unicast_dscp_classify")
        node_1 = self._set_xml_tag(if_node, "rewrite-rules")
        node_2 = self._set_xml_tag(node_1, "dscp")
        self._set_xml_tag(node_2,
                          "rewrite-rule-name",
                          None,
                          None,
                          "ce_dscp_remark")

    @decorater_log
    def _set_device_switch_port(self,
                                conf_node,
                                loopback=None):
        '''
        Set switch-options for L2Leaf.
        '''
        node_2 = self._set_xml_tag(conf_node, "switch-options")
        self._set_xml_tag(node_2, "vtep-source-interface", None, None, "lo0.0")
        self._set_xml_tag(node_2, "route-distinguisher",
                          None, None, "%s:2" % (loopback,))
        self._set_xml_tag(node_2, "vrf-import", None, None, "VPN_import_L2")
        self._set_xml_tag(node_2, "vrf-target", None, None, "target:9999:9999")
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (conf_node.tag, etree.tostring(node_2)),
            __name__)
        return node_2


    @decorater_log
    def _set_slice_mtu_value(self,
                             mtu=None,
                             is_vlan=False,
                             port_mode=None,
                             slice_type=2):
        '''
        Set mtu value for L2/L3CPIF.
        '''
        tmp = None
        if slice_type == 3:
            if mtu is None:
                tmp = None
            else:
                if is_vlan:
                    tmp = 4114
                else:
                    tmp = int(mtu) + 14
        return tmp


    @decorater_log
    def _set_l2_slice_interfaces(self,
                                 conf_node,
                                 cp_infos):
        '''
        Set all l2CP for CE.
        '''
        node_1 = self._set_interfaces_node(conf_node)
        for tmp_cp in cp_infos.values():
            self._set_l2_slice_vlan_if(node_1, tmp_cp)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (conf_node.tag, etree.tostring(node_1)),
            __name__)

    @decorater_log
    def _set_l2_slice_vlan_if(self,
                              ifs_node,
                              cp_info):
        '''
        Set l2CP for CE.
        '''
        operation = cp_info.get("OPERATION")
        if_type = cp_info.get("IF-TYPE")
        attr, attr_val = self._get_attr_from_operation(operation)
        if operation == self._DELETE and if_type == self._if_type_phy:
            node_1 = self._set_xml_tag(ifs_node, "interface", attr, attr_val)
            self._set_xml_tag(
                node_1, "name", None, None, cp_info.get("IF-NAME"))
            self.common_util_log.logging(
                None, self.log_level_debug,
                self._XML_LOG % (ifs_node.tag, etree.tostring(node_1)),
                __name__)
            return node_1
        node_1 = self._set_xml_tag(ifs_node, "interface")
        self._set_xml_tag(node_1, "name", None, None, cp_info.get("IF-NAME"))
        evpn = cp_info.get("EVPN-MULTI")
        if (evpn is not None and evpn.get("OPERATION") is not None and
                evpn.get("IF-ESI") is not None and
                evpn.get("IF-SYSTEM-ID") is not None):
            self._set_l2_slice_evpn_esi(node_1,
                                        evpn["IF-ESI"],
                                        evpn["OPERATION"])
            self._set_l2_slice_evpn_lag_links(node_1,
                                              cp_info.get("IF-LAG-LINKS"),
                                              evpn["OPERATION"],
                                              cp_info["IF-TYPE"])
            self._set_l2_slice_evpn_system_id(node_1,
                                              evpn["IF-SYSTEM-ID"],
                                              evpn["OPERATION"])
            if operation == self._REPLACE:
                self.common_util_log.logging(
                    None, self.log_level_debug,
                    self._XML_LOG % (ifs_node.tag, etree.tostring(node_1)),
                    __name__)
                return node_1

        if attr_val == self._DELETE:
            node_2 = self._set_xml_tag(node_1, "unit", attr, attr_val)
            self._set_xml_tag(node_2, "name", None, None, 0)
        elif cp_info.get("VLAN"):
            for unit in cp_info.get("VLAN").values():
                tmp_port = cp_info.get("IF-PORT-MODE")
                tmp_qos = cp_info.get("QOS")
                self._set_l2_slice_vlan_unit(
                    node_1, unit, port_mode=tmp_port, qos_info=tmp_qos)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (ifs_node.tag, etree.tostring(node_1)),
            __name__)
        return node_1

    @decorater_log
    def _set_l2_slice_vlan_unit(self, if_node, vlan, **param):
        '''
        Set unit for interface node.
            param : port_mode : Designate the port mode.
                    qos : qos information
        '''
        port_mode = param.get("port_mode")

        qos_info = None
        if port_mode == "trunk":
            qos_info = "input_l2_ce_filter"
        else:
            qos_info = "input_vpnbulk_l2_be_ce_filter"

        attr, attr_val = self._get_attr_from_operation(vlan.get("OPERATION"))

        node_1 = self._set_xml_tag(if_node, "unit")
        self._set_xml_tag(node_1, "name", None, None, 0)
        node_2 = self._set_xml_tag(node_1, "family")
        node_3 = self._set_xml_tag(node_2, "ethernet-switching")
        node_4 = self._set_xml_tag(node_3, "vlan")
        self._set_xml_tag(
            node_4, "members", attr, attr_val, vlan.get("CE-IF-VLAN-ID"))
        if attr_val != self._DELETE:
            self._set_xml_tag(
                node_3, "interface-mode", None, None, port_mode)
            node_4 = self._set_xml_tag(node_3, "filter")
            self._set_xml_tag(
                node_4, "input", None, None, qos_info)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (if_node.tag, etree.tostring(node_1)),
            __name__)
        return node_1

    @decorater_log
    def _set_l2_slice_evpn_esi(self, if_node, esi, operation=None):
        '''
        Conduct esi setting.
        '''
        attr, attr_val = self._get_attr_from_operation(operation)
        node_1 = self._set_xml_tag(if_node, "esi", attr, attr_val)
        if operation != self._DELETE:
            self._set_xml_tag(node_1, "identifier", None, None, esi)
            self._set_xml_tag(node_1, "all-active")
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (if_node.tag, etree.tostring(node_1)),
            __name__)
        return node_1

    @decorater_log
    def _set_l2_slice_evpn_lag_links(self,
                                     if_node,
                                     links,
                                     operation=None,
                                     if_type=None):
        '''
        Set links for LAG.
        '''
        node_1 = self._xml_setdefault_node(if_node, "aggregated-ether-options")
        if if_type == self._if_type_lag:
            val_links = links if operation == self._DELETE else 1
            self._set_xml_tag(node_1,
                              "minimum-links",
                              self._ATTR_OPE,
                              self._REPLACE,
                              val_links)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (if_node.tag, etree.tostring(node_1)),
            __name__)
        return node_1

    @decorater_log
    def _set_l2_slice_evpn_system_id(self, if_node, system_id, operation=None):
        '''
        Conduct system-id of LAG.
        '''
        attr, attr_val = self._get_attr_from_operation(operation)
        node_1 = self._xml_setdefault_node(if_node, "aggregated-ether-options")
        node_2 = self._set_xml_tag(node_1, "lacp")
        if operation != self._DELETE:
            self._set_xml_tag(node_2, "system-id", attr, attr_val, system_id)
        else:
            self._set_xml_tag(node_2, "system-id", attr, attr_val)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (if_node.tag, etree.tostring(node_1)),
            __name__)
        return node_1

    @decorater_log
    def _set_l2_slice_vlans(self,
                            conf_node,
                            vlans_vni,
                            operation=None):
        '''
        Create vlans.
        '''
        node_1 = self._set_xml_tag(conf_node, "vlans")
        for vlan_id, vni in vlans_vni.items():
            self._set_l2_slice_vlan_vni(node_1,
                                        vlan_id,
                                        vni,
                                        operation)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (conf_node.tag, etree.tostring(node_1)),
            __name__)
        return node_1

    @decorater_log
    def _set_l2_slice_vlan_vni(self,
                               vlans_node,
                               vlan_id,
                               vni=None,
                               operation=None):
        '''
        Create vlan(vlan_id/vni sxettings) inside vlans.
        '''
        attr, attr_val = self._get_attr_from_operation(operation)
        node_1 = self._set_xml_tag(vlans_node, "vlan", attr, attr_val)
        self._set_xml_tag(node_1, "name", None,  None, "vlan%d" % (vlan_id,))
        if attr_val == self._DELETE:
            return node_1
        node_2 = self._set_xml_tag(node_1, "vxlan")
        self._set_xml_tag(node_2, "vni", None, None, vni)
        self._set_xml_tag(node_2, "ingress-node-replication")
        self._set_xml_tag(node_1, "vlan-id", None, None, vlan_id)
        return node_1

    @decorater_log
    def _set_l2_slice_protocols_evpn(self,
                                     conf_node,
                                     vnis,
                                     operation=None):
        '''
        Create vni for protocols/evpn.
        '''
        attr, attr_val = self._get_attr_from_operation(operation)
        node_1 = self._set_xml_tag(conf_node, "protocols")
        node_2 = self._set_xml_tag(node_1, "evpn")
        for vni in vnis:
            self._set_xml_tag(node_2,
                              "extended-vni-list",
                              attr,
                              attr_val,
                              vni)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (conf_node.tag, etree.tostring(node_1)),
            __name__)
        return node_1


    @decorater_log
    def _set_slice_protocol_routing_options(self, conf_node, vrf_name=None):
        '''
        Set routing-options in preparation of L3 slice protocol settings.
        '''
        node_1 = self._xml_setdefault_node(conf_node, "routing-instances")
        node_2 = self._xml_setdefault_node(node_1, "instance")
        tmp = self._xml_setdefault_node(node_2, "name")
        if not tmp.text:
            tmp.text = vrf_name
        node_3 = self._xml_setdefault_node(node_2, "routing-options")
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (conf_node.tag, etree.tostring(node_1)),
            __name__)
        return node_3

    @decorater_log
    def _set_slice_protocol_bgp(self,
                                conf_node,
                                vrf_name,
                                bgp_list=None):
        '''
        Set bgp for L3VLANIF.
        '''
        node_1 = self._set_slice_protocol_routing_options(
            conf_node, vrf_name).getparent()
        tmp_node_2 = self._set_xml_tag(node_1, "protocols")
        node_2 = self._set_xml_tag(tmp_node_2, "bgp")
        for bgp in bgp_list:
            self._set_slice_bgp_group(node_2,
                                      ip_ver=bgp.get("BGP-IP-VERSION"),
                                      bgp=bgp)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (conf_node.tag, etree.tostring(node_1)),
            __name__)

    @decorater_log
    def _set_slice_bgp_group(self,
                             bgp_node,
                             ip_ver=4,
                             bgp=None):
        '''
        Set bgp for L3VLANIF.
        '''
        node_1 = self._set_xml_tag(bgp_node, "group")
        self._set_xml_tag(node_1, "name", None, None, "RI_eBGPv%d" % (ip_ver,))
        self._set_slice_bgp_neighbor(node_1, bgp)
        if bgp.get("OPERATION") != self._DELETE:
            node_2 = self._set_xml_tag(node_1, "family")
            tag_name = "inet" if ip_ver == 4 else "inet6"
            node_3 = self._set_xml_tag(node_2, tag_name)
            self._set_xml_tag(node_3, "unicast")
            self._set_xml_tag(node_1, "type", None, None, "external")
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (bgp_node.tag, etree.tostring(node_1)),
            __name__)
        return node_1

    @decorater_log
    def _set_slice_bgp_neighbor(self,
                                group_node,
                                bgp=None):
        '''
        Set bgp for L3VLANIF.
        '''
        attr, attr_val = self._get_attr_from_operation(bgp.get("OPERATION"))
        ip_ver = bgp.get("BGP-IP-VERSION")
        node_1 = self._set_xml_tag(group_node, "neighbor", attr, attr_val)
        self._set_xml_tag(
            node_1, "name", None, None, bgp["BGP-RADD"])
        if attr_val == self._DELETE:
            return node_1
        self._set_xml_tag(
            node_1, "import", None, None, "eBGPv%d_To_CE_import" % (ip_ver,))
        if bgp.get("BGP-MASTER") is None:
            tmp = "eBGPv%d_To_standby-CE_export" % (ip_ver,)
        else:
            tmp = "eBGPv%d_To_active-CE_export" % (ip_ver,)
        self._set_xml_tag(node_1, "export",  None, None, tmp)
        self._set_xml_tag(node_1, "peer-as", None, None, bgp["BGP-PEER-AS"])
        self._set_xml_tag(node_1, "local-address", None, None, bgp["BGP-LADD"])
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (group_node.tag, etree.tostring(node_1)),
            __name__)
        return node_1

    @decorater_log
    def _set_slice_protocol_static_route(self,
                                         conf_node,
                                         vrf_name,
                                         static_dict=None):
        '''
        Set static route for L3VLANIF.
        '''
        node_1 = self._set_slice_protocol_routing_options(conf_node, vrf_name)
        rib_node = {4: None, 6: None}
        for route in static_dict.values():
            ip_ver = route["IP-VERSION"]
            if rib_node.get(ip_ver) is None:
                rib_node[ip_ver] = self._set_slice_protocol_rib(node_1,
                                                                vrf_name,
                                                                ip_ver)
            self._set_static_route_in_rib(rib_node[ip_ver], route)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (conf_node.tag, etree.tostring(node_1)),
            __name__)

    @decorater_log
    def _set_slice_protocol_rib(self,
                                options_node,
                                vrf_name,
                                ip_ver=4):
        '''
        Set rib node.
        '''
        node_1 = self._set_xml_tag(options_node, "rib")
        if ip_ver == 6:
            tmp_name = vrf_name + ".inet6.0"
        else:
            tmp_name = vrf_name + ".inet.0"
        self._set_xml_tag(node_1, "name", None, None, tmp_name)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (options_node.tag, etree.tostring(node_1)),
            __name__)
        return node_1

    @decorater_log
    def _set_static_route_in_rib(self, rib_node, route):
        '''
        Set static route for rib node.
        '''
        attr, attr_val = self._get_attr_from_operation(route.get("OPERATION"))
        tmp_rib_node = self._xml_setdefault_node(rib_node, "static")
        node_2 = self._set_xml_tag(tmp_rib_node, "route", attr, attr_val)
        self._set_xml_tag(node_2,
                          "name",
                          None,
                          None,
                          route["ROUTE-IP"])
        if attr_val != self._DELETE:
            for tmp_nh, tmp_op in route.get("NEXTHOP", {}).items():
                attr, attr_val = self._get_attr_from_operation(tmp_op)
                node_3 = self._set_xml_tag(node_2,
                                           "qualified-next-hop",
                                           attr,
                                           attr_val)
                self._set_xml_tag(
                    node_3, "nexthop", None, None, tmp_nh)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (rib_node.tag, etree.tostring(node_2)),
            __name__)

    @decorater_log
    def _set_l3_slice_interfaces(self,
                                 conf_node,
                                 cp_infos):
        '''
        Set all L3CP for CE.
        '''
        node_1 = self._set_interfaces_node(conf_node)
        for tmp_cp in cp_infos.values():
            self._set_l3_slice_vlan_if(node_1, tmp_cp)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (conf_node.tag, etree.tostring(node_1)),
            __name__)

    @decorater_log
    def _set_l3_slice_vlan_if(self,
                              ifs_node,
                              cp_info):
        '''
        Set L3CP for CE.
        '''
        operation = cp_info.get("OPERATION")
        if_type = cp_info.get("IF-TYPE")
        mtu = cp_info.get("IF-MTU")
        is_vlan = cp_info.get("IF-IS-VLAN", False)
        attr, attr_val = self._get_attr_from_operation(operation)
        if operation == self._DELETE and if_type == self._if_type_phy:
            node_1 = self._set_xml_tag(ifs_node, "interface", attr, attr_val)
            self._set_xml_tag(
                node_1, "name", None, None, cp_info.get("IF-NAME"))
            self.common_util_log.logging(
                None, self.log_level_debug,
                self._XML_LOG % (ifs_node.tag, etree.tostring(node_1)),
                __name__)
            return node_1
        node_1 = self._set_xml_tag(ifs_node, "interface")
        self._set_xml_tag(node_1, "name", None, None, cp_info.get("IF-NAME"))
        if is_vlan:
            self._set_xml_tag(node_1, "vlan-tagging", attr, attr_val)
        tmp = self._set_slice_mtu_value(
            mtu=mtu, is_vlan=is_vlan, slice_type=3)
        if (tmp is not None and
                not (operation != self._DELETE and
                     cp_info.get("IF-DELETE-VLAN"))):
            if operation == self._DELETE:
                tmp = ""
            self._set_xml_tag(node_1, "mtu", attr, attr_val, tmp)
        if cp_info.get("VLAN"):
            for unit in cp_info.get("VLAN").values():
                tmp_qos = cp_info.get("QOS")
                self._set_l3_slice_vlan_unit(node_1,
                                             unit,
                                             is_vlan=is_vlan,
                                             mtu=mtu,
                                             qos=tmp_qos)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (ifs_node.tag, etree.tostring(node_1)),
            __name__)
        return node_1

    @decorater_log
    def _set_l3_slice_vlan_unit(self,
                                if_node,
                                vlan,
                                is_vlan=None,
                                mtu=None,
                                qos={}):
        '''
        Set unit for interface node.
        '''
        attr, attr_val = self._get_attr_from_operation(vlan.get("OPERATION"))

        node_1 = self._set_xml_tag(if_node, "unit", attr, attr_val)
        self._set_xml_tag(node_1,
                          "name",
                          None,
                          None,
                          vlan.get("CE-IF-VLAN-ID"))
        if attr_val == self._DELETE:
            self.common_util_log.logging(
                None, self.log_level_debug,
                self._XML_LOG % (if_node.tag, etree.tostring(node_1)),
                __name__)
            return node_1
        node_2 = self._set_xml_tag(node_1, "family")
        vrrp = vlan.get("VRRP")
        is_add_cp = False
        if vlan.get("CE-IF-ADDR6") or vlan.get("CE-IF-ADDR"):
            is_add_cp = True
        if vlan.get("CE-IF-ADDR6"):
            node_3 = self._set_l3_slice_vlan_unit_address(
                node_2,
                6,
                ip_addr=vlan.get("CE-IF-ADDR6"),
                prefix=vlan.get("CE-IF-PREFIX6"),
                is_vlan=is_vlan,
                mtu=mtu,
                is_add_cp=is_add_cp,
                qos_info=qos
            )
            if vrrp and vrrp.get("VRRP-VIRT-ADDR6"):
                self._set_l3_slice_vrrp(node_3, vrrp, 6)
        if vlan.get("CE-IF-ADDR"):
            node_3 = self._set_l3_slice_vlan_unit_address(
                node_2,
                4,
                ip_addr=vlan.get("CE-IF-ADDR"),
                prefix=vlan.get("CE-IF-PREFIX"),
                is_vlan=is_vlan,
                mtu=mtu,
                is_add_cp=is_add_cp,
                qos_info=qos
            )
            if vrrp and vrrp.get("VRRP-VIRT-ADDR"):
                self._set_l3_slice_vrrp(node_3, vrrp, 4)
        if is_add_cp:
            self._set_xml_tag(
                node_1, "vlan-id", None, None, vlan.get("CE-IF-VLAN-ID"))
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (if_node.tag, etree.tostring(node_1)),
            __name__)
        return node_1

    @decorater_log
    def _set_l3_slice_vlan_unit_address(self,
                                        family_node,
                                        ip_ver=4,
                                        **params):
        '''
        Set inet for family node. (common for IPv4,IPv6)　
            params : ip_addr = address value
                    ; prefix = prefix value
                    ; is_vlan = IF-IS-VLAN value
                    ; mtu = IF-MTU value
                    : qos_info = QOS value
        '''
        ip_addr = params.get("ip_addr")
        prefix = params.get("prefix")
        is_vlan = params.get("is_vlan")
        mtu = params.get("mtu")
        qos_info = params.get("qos_info")
        is_add_cp = params.get("is_add_cp", True)

        tag_name = "inet" if ip_ver == 4 else "inet6"
        node_1 = self._set_xml_tag(family_node, tag_name)
        if is_add_cp:
            node_2 = self._set_xml_tag(node_1, "filter")
            node_3 = self._set_xml_tag(node_2, "input")
            key_name = "IPV%d" % (ip_ver,)
            filter_name = qos_info.get("REMARK-MENU").get(key_name)
            self._set_xml_tag(node_3,
                              "filter-name",
                              None,
                              None,
                              filter_name)
        node_2 = self._set_xml_tag(node_1, "address")
        node_3 = self._set_xml_tag(node_2,
                                   "name",
                                   None,
                                   None,
                                   "%s/%s" % (ip_addr, prefix))
        if is_add_cp and mtu is not None and is_vlan:
            self._set_xml_tag(node_1, "mtu", None, None, mtu)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (family_node.tag, etree.tostring(node_1)),
            __name__)
        return node_2

    @decorater_log
    def _set_l3_slice_vrrp(self,
                           address_node,
                           vrrp=None,
                           ip_ver=4):
        '''
        Set inet for family node. (common for IPv4,IPv6)
            params : ip_addr = Setting IPAddress object
                    ; is_vlan = IF-IS-VLAN value
                    ; mtu = IF-MTU value
        '''
        attr, attr_val = self._get_attr_from_operation(vrrp.get("OPERATION"))
        tag_name = "vrrp-group" if ip_ver == 4 else "vrrp-inet6-group"
        node_1 = self._set_xml_tag(address_node, tag_name, attr, attr_val)
        self._set_xml_tag(node_1,
                          "group_id",
                          None,
                          None,
                          vrrp.get("VRRP-GROUP-ID"))
        if attr_val == self._DELETE:
            self.common_util_log.logging(
                None, self.log_level_debug,
                self._XML_LOG % (address_node.tag, etree.tostring(node_1)),
                __name__)
            return node_1
        if ip_ver == 4:
            tmp = vrrp.get("VRRP-VIRT-ADDR")
            tag_name = "virtual-address"
        else:
            tmp = vrrp.get("VRRP-VIRT-ADDR6")
            tag_name = "virtual-inet6-address"
        self._set_xml_tag(node_1, tag_name, None, None,  tmp)
        self._set_xml_tag(
            node_1, "priority", None, None,   vrrp.get("VRRP-VIRT-PRI"))
        if ip_ver == 4:
            tmp = 1
            tag_name = "advertise-interval"
        else:
            tmp = 1000
            tag_name = "inet6-advertise-interval"
        self._set_xml_tag(node_1, tag_name, None, None,  tmp)
        node_2 = self._set_xml_tag(node_1, "preempt")
        self._set_xml_tag(node_2, "hold-time", None, None,  180)
        tmp_track = vrrp.get("track")
        if tmp_track:
            node_2 = self._set_xml_tag(node_1, "track")
            self._set_xml_tag(node_2, "priority-hold-time", None, None, 180)
            for track_if in tmp_track:
                node_3 = self._set_xml_tag(node_2, "interface")
                self._set_xml_tag(
                    node_3, "interface_name", None, None, track_if)
                self._set_xml_tag(node_3, "priority-cost", None, None, 10)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (address_node.tag, etree.tostring(node_1)),
            __name__)
        return node_1

    @decorater_log
    def _set_l3_slice_routing_instance(self,
                                       conf_node,
                                       vrf_name,
                                       operation=None):
        '''
        Set routing_instance node.
        '''
        attr, attr_val = self._get_attr_from_operation(operation)
        node_1 = self._xml_setdefault_node(conf_node, "routing-instances")
        node_2 = self._xml_setdefault_node(node_1, "instance")
        if attr_val == self._DELETE:
            node_2.attrib[attr] = self._DELETE
        self._set_xml_tag(node_2, "name", None, None, vrf_name)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (conf_node.tag, etree.tostring(node_1)),
            __name__)
        return node_2

    @decorater_log
    def _set_l3_slice_routing_instance_interface(self,
                                                 ins_node,
                                                 cps_info,
                                                 operation="merge"):
        '''
        Set IF for instance node.
        '''
        for if_info in cps_info.values():
            if_name = if_info["IF-NAME"]
            for vlan_info in if_info.get("VLAN", {}).values():
                vlan_ope = vlan_info.get("OPERATION")
                if not vlan_ope:
                    vlan_ope = "merge"
                if operation == vlan_ope:
                    vlan_id = vlan_info["CE-IF-VLAN-ID"]
                    tmp = "%s.%d" % (if_name, vlan_id)
                    attr, attr_val = self._get_attr_from_operation(
                        vlan_info.get("OPERATION"))
                    node_3 = self._set_xml_tag(
                        ins_node, "interface", attr, attr_val)
                    self._set_xml_tag(node_3, "name", None, None, tmp)

    @decorater_log
    def _set_l3_slice_routing_instance_vrf(self,
                                           conf_node,
                                           vrf_name,
                                           vrf_info,
                                           cps_info):
        '''
        Set routing_instance node.
        '''
        node_1 = self._xml_setdefault_node(conf_node, "routing-instances")
        node_2 = self._xml_setdefault_node(node_1, "instance")
        self._set_xml_tag(node_2, "name", None, None, vrf_name)
        self._set_xml_tag(node_2, "instance-type", None, None, "vrf")
        self._set_l3_slice_routing_instance_interface(node_2,
                                                      cps_info)
        node_3 = self._set_xml_tag(node_2, "route-distinguisher")
        self._set_xml_tag(node_3, "rd-type", None, None, vrf_info["VRF-RD"])
        node_3 = self._set_xml_tag(node_2, "vrf-target")
        self._set_xml_tag(node_3, "community", None, None, vrf_info["VRF-RT"])
        self._set_xml_tag(node_2, "vrf-table-label")
        self._set_xml_tag(node_2, "no-vrf-propagate-ttl")
        node_3 = self._xml_setdefault_node(node_2, "routing-options")
        self._set_xml_tag(node_3,
                          "router-id",
                          None,
                          None,
                          vrf_info["VRF-ROUTER-ID"])
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (conf_node.tag, etree.tostring(node_1)),
            __name__)
        return node_2


    @decorater_log
    def _get_device_from_ec(self, device_mes, service=None):
        '''
        Obtain EC message information regarding
        device expansion. (common for spine, leaf)
        '''
        dev_reg_info = {}
        dev_reg_info["DEVICE-NAME"] = device_mes.get("name")
        tmp = device_mes.get("loopback-interface", {})
        dev_reg_info["LB-IF-ADDR"] = tmp.get("address")
        dev_reg_info["LB-IF-PREFIX"] = tmp.get("prefix")
        ospf = device_mes.get("ospf", {})
        dev_reg_info["OSPF-AREA-ID"] = ospf.get("area-id")
        for chk_item in dev_reg_info.values():
            if chk_item is None:
                raise ValueError("device info not enough information")
        return dev_reg_info

    @staticmethod
    @decorater_log
    def _get_leaf_vpn_from_ec(device_mes):
        dev_reg_info = {}
        tmp = device_mes.get("l3-vpn", {})
        if tmp:
            vpn_type = 3
        else:
            tmp = device_mes.get("l2-vpn", {})
            if tmp:
                vpn_type = 2
            else:
                raise ValueError("Leaf VPN  not enough information")
        dev_reg_info["AS-NUMBER"] = tmp.get("as", {}).get("as-number")
        dev_reg_info["VPN-TYPE"] = vpn_type
        if dev_reg_info["AS-NUMBER"] is None:
            raise ValueError("device neighbor not enough information")
        tmp = tmp.get("bgp", {})
        l3v_lbb_infos = []
        for nbrs in tmp.get("neighbor", ()):
            if (not nbrs.get("address") or
                    not tmp.get("community") or
                    not tmp.get("community-wildcard")):
                raise ValueError("device neighbor not enough information")
            else:
                tmp_nbr = \
                    {"RR-ADDR": nbrs.get("address"),
                     "BGP-COMMUNITY": tmp.get("community"),
                     "BGP-COM-WILD": tmp.get("community-wildcard")}
                l3v_lbb_infos.append(tmp_nbr)
        return dev_reg_info, l3v_lbb_infos

    @decorater_log
    def _get_b_leaf_data_from_ec(self, device_mes, db_info=None):
        '''
        Obtain EC message information (virtual-link, range) regarding b-leaf.
        '''
        ospf_mes = device_mes.get("ospf", {})
        dev_reg_info = {}
        tmp = ospf_mes.get("virtual-link")
        if tmp is not None:
            if tmp.get("operation") == self._DELETE:
                db_tmp = db_info["device"]["ospf"]["virtual_link"]
                router_id = db_tmp.get("router_id")
            else:
                router_id = tmp.get("router-id")
            if not router_id:
                raise ValueError("virtual-link not enough information")
            dev_reg_info["VIRTUAL-LINK-ROUTER-ID"] = router_id
            dev_reg_info["VIRTUAL-LINK-OPERATION"] = tmp.get("operation")
        tmp = ospf_mes.get("range")
        if tmp is not None:
            if tmp.get("operation") == self._DELETE:
                db_tmp = db_info["device"]["ospf"]["range"]
                addr = db_tmp.get("address")
                prefix = db_tmp.get("prefix")
            else:
                addr = tmp.get("address")
                prefix = tmp.get("prefix")
            if not addr or prefix is None:
                raise ValueError("ospf-range not enough information")
            dev_reg_info["RANGE-OPERATION"] = tmp.get("operation")
            dev_reg_info["RANGE-ADDRESS"] = addr
            dev_reg_info["RANGE-PREFIX"] = prefix
        return dev_reg_info

    @decorater_log
    def _get_breakout_data_in_db(self, db_info, if_name):
        '''
        Obtain breakout IF data stored in DB.
        '''
        for tmp_if in db_info.get("breakout_info", {}).get("interface", ()):
            if tmp_if.get("base-interface") == if_name:
                return tmp_if.copy()
        raise("Not found base breakoutIF from DB")

    @decorater_log
    def _get_breakout_from_ec(self, device_mes, db_info=None, operation=None):
        '''
        Obtain EC message information regarding breakout IF.
        '''
        breakout_ifs = []
        for tmp in device_mes.get("breakout-interface", ()):
            breakout = {}
            if not self._breakout_check.search(
                    tmp.get("base-interface", "")):
                raise ValueError("breakout base IF %s is illegal" %
                                 (tmp.get("base-interface"),))
            breakout["IF-NAME"] = tmp.get("base-interface")
            breakout["SPEED"] = tmp.get("speed")
            breakout["BREAKOUT-NUM"] = tmp.get("breakout-num")
            if operation == self._DELETE:
                db_data = self._get_breakout_data_in_db(
                    db_info, breakout["IF-NAME"])
                breakout["SPEED"] = db_data.get("speed")
                breakout["BREAKOUT-NUM"] = db_data.get("breakout-num")
            for chk_item in breakout.values():
                if chk_item is None:
                    raise ValueError(
                        "breakout info not enough information")
            breakout_ifs.append(breakout)
        return breakout_ifs

    @decorater_log
    def _get_ce_lag_from_ec(self,
                            device_mes,
                            service=None,
                            operation=None,
                            db_info=None):
        '''
        Obtain EC message information relating to LAG for CE.
        '''
        lag_ifs = []
        lag_mem_ifs = []
        for tmp in device_mes.get("ce-lag-interface", ()):
            if operation == self._DELETE:
                tmp_bool = bool(not tmp.get("name") or
                                not tmp.get("leaf-interface") or
                                len(tmp["leaf-interface"]) == 0)
            elif operation == self._REPLACE:
                tmp_bool = bool(not tmp.get("name") or
                                tmp.get("minimum-links") is None or
                                not tmp.get("leaf-interface") or
                                len(tmp["leaf-interface"]) == 0)
            else:
                tmp_bool = bool(not tmp.get("name") or
                                tmp.get("lag-id") is None or
                                tmp.get("minimum-links") is None or
                                tmp.get("link-speed") is None or
                                not tmp.get("leaf-interface") or
                                len(tmp["leaf-interface"]) == 0)
            if tmp_bool:
                raise ValueError("ce-lag not enough information")
            lag_ifs.append(self._get_lag_if_info(tmp))
            for lag_mem in tmp.get("leaf-interface"):
                if not lag_mem["name"]:
                    raise ValueError(
                        "leaf-interface not enough information ")
                if operation == self._REPLACE:
                    if lag_mem.get("operation")is None:
                        raise ValueError(
                            "leaf-interface not enough information ")
                lag_mem_ifs.append(self._get_lag_mem_if_info(tmp, lag_mem))
        return lag_ifs, lag_mem_ifs

    @decorater_log
    def _get_lag_if_info(self, if_info):
        '''
        Obtain LAG information from EC message.
        '''
        tmp = {
            "IF-NAME": if_info.get("name"),
            "LAG-ID": if_info.get("lag-id"),
            "LAG-LINKS": if_info.get("minimum-links"),
            "LAG-SPEED": if_info.get("link-speed"),
        }
        return tmp

    @decorater_log
    def _get_lag_mem_if_info(self, lag_if, lag_mem_if):
        '''
        Obtain LAG member information from EC message.
        '''
        tmp = {"IF-NAME": lag_mem_if.get("name"),
               "LAG-IF-NAME": lag_if["name"],
               "OPERATION": lag_mem_if.get("operation")}
        return tmp

    @decorater_log
    def _get_cluster_link_from_ec(self,
                                  device_mes,
                                  db_info=None):
        '''
        Obtain EC message information relating to internal link (LAG).
        '''
        phy_ifs = []

        for tmp in device_mes.get("cluster-link-physical-interface", ()):
            if (not tmp.get("name") or
                not tmp.get("address") or
                    tmp.get("prefix") is None or
                    tmp.get("ospf", {}).get("metric") is None):
                raise ValueError(
                    "cluster-link-physical not enough information")

            phy_ifs.append(self._get_cluster_if_info(tmp, self._if_type_phy))

        lag_ifs = []
        for tmp in device_mes.get("cluster-link-lag-interface", ()):
            if (not tmp.get("name") or
                not tmp.get("address") or
                    tmp.get("prefix") is None or
                    tmp.get("ospf", {}).get("metric") is None):
                raise ValueError("cluster-link-lag not enough information")

            lag_ifs.append(self._get_cluster_if_info(tmp, self._if_type_lag))

        for tmp in device_mes.get("cluster-link-interface", ()):
            if not tmp.get("name"):
                raise ValueError("del cluster-link not enough information")

            if_type = None
            tmp_if = None
            for db_if in db_info.get("cluster-link_info", ()):
                if db_if.get("name") == tmp.get("name"):
                    if_type = db_if.get("type")
                    tmp_if = {
                        "IF-TYPE": if_type,
                        "IF-NAME": tmp.get("name"),
                    }
                    if if_type == self._if_type_phy:
                        phy_ifs.append(tmp_if)
                    elif if_type == self._if_type_lag:
                        lag_ifs.append(tmp_if)
                    else:
                        raise ValueError(
                            "cluster-link if_type in db is irregular")
                    break

            if not tmp_if:
                raise ValueError("cluster-link if_name in db is irregular")

        inner_ifs = copy.deepcopy(phy_ifs)
        inner_ifs.extend(lag_ifs)
        return phy_ifs, lag_ifs,  inner_ifs

    @decorater_log
    def _get_cluster_if_info(self, if_info, if_type=None):
        '''
        Obtain inter-cluster link information from EC message.
        (regardless of physical/LAG)
        '''
        tmp = {
            "IF-TYPE": if_type,
            "IF-NAME": if_info.get("name"),
            "IF-ADDR": if_info.get("address"),
            "IF-PREFIX": if_info.get("prefix"),
            "OSPF-METRIC": if_info.get("ospf", {}).get("metric"),
        }
        return tmp

    @decorater_log
    def _get_internal_link_from_ec(self,
                                   device_mes,
                                   service=None,
                                   operation=None,
                                   db_info=None):
        '''
        Obtain EC message information relating to internal link (LAG).
        '''

        if (service == self.name_spine) or \
                (service == self.name_internal_link and
                 db_info.get("device", {}).get(
                     "device_type") == self._device_type_spine):
            need_oppo_info = True
        else:
            need_oppo_info = False

        phy_ifs = []

        for tmp in device_mes.get("internal-physical", ()):
            if (not tmp.get("name") or
                not tmp.get("address") or
                    tmp.get("prefix") is None):
                raise ValueError("internal-physical not enough information")

            phy_ifs.append(
                self._get_internal_if_info(tmp,
                                           self._if_type_phy, need_oppo_info))

        lag_ifs = []
        lag_mem_ifs = []

        for tmp in device_mes.get("internal-lag", ()):
            if (not tmp.get("name") or
                not tmp.get("address") or
                    tmp.get("prefix") is None or
                    tmp.get("lag-id") is None or
                    tmp.get("minimum-links") is None or
                    tmp.get("link-speed") is None or
                not tmp.get("internal-interface") or
                    len(tmp["internal-interface"]) == 0):
                raise ValueError("internal-lag not enough information")

            lag_ifs.append(
                self._get_internal_if_info(tmp,
                                           self._if_type_lag, need_oppo_info))

            for lag_mem in tmp.get("internal-interface"):
                if not lag_mem.get("name"):
                    raise ValueError(
                        "internal-interface not enough information ")
                lag_mem_ifs.append(self._get_lag_mem_if_info(tmp, lag_mem))

        inner_ifs = copy.deepcopy(phy_ifs)
        inner_ifs.extend(lag_ifs)
        return phy_ifs, lag_ifs, lag_mem_ifs, inner_ifs

    @decorater_log
    def _get_del_internal_link_from_ec(self,
                                       device_mes,
                                       service=None,
                                       operation=None,
                                       db_info=None):
        '''
        Obtain EC message/DB information relating to
        internal link (LAG) for deletion.
        '''
        inner_ifs = []

        phy_ifs = []

        for tmp_if in device_mes.get("internal-physical", ()):
            if not tmp_if.get("name"):
                raise ValueError("internal-physical not enough information")

            tmp = copy.deepcopy(tmp_if)

            inner_ifs.append(tmp.get("name"))
            phy_ifs.append(
                self._get_internal_if_del_info(tmp,
                                               self._if_type_lag, db_info))

        lag_ifs = []
        lag_mem_ifs = []

        for tmp_if in device_mes.get("internal-lag", ()):
            if (not tmp_if.get("name") or
                    tmp_if.get("minimum-links") is None or
                not tmp_if.get("internal-interface") or
                    len(tmp_if["internal-interface"]) == 0):
                raise ValueError("internal-lag not enough information")

            tmp = copy.deepcopy(tmp_if)

            inner_ifs.append(tmp.get("name"))
            lag_ifs.append(
                self._get_internal_if_del_info(tmp,
                                               self._if_type_lag, db_info))

            for lag_mem in tmp.get("internal-interface"):
                if not lag_mem.get("name"):
                    raise ValueError(
                        "internal-interface not enough information ")
                lag_mem_ifs.append(self._get_lag_mem_if_info(tmp, lag_mem))

        inner_ifs = copy.deepcopy(phy_ifs)
        inner_ifs.extend(lag_ifs)

        return phy_ifs, lag_ifs, lag_mem_ifs, inner_ifs

    @decorater_log
    def _get_replace_internal_link_from_ec(self,
                                           device_mes,
                                           service=None,
                                           operation=None,
                                           db_info=None,
                                           is_cost_replace=True):
        '''
        Obtain the EC message/ DB information regarding the internal link for deletion(LAG).
        '''
        inner_ifs = []

        phy_ifs = []

        for tmp_if in device_mes.get("internal-physical", ()):
            if (not tmp_if.get("name")) or\
                    (is_cost_replace and (not tmp_if.get("cost"))):
                raise ValueError("internal-physical not enough information")

            tmp = copy.deepcopy(tmp_if)

            inner_ifs.append(tmp.get("name"))
            phy_ifs.append(
                self._get_internal_if_replace_info(tmp,
                                                   self._if_type_phy, db_info))

        lag_ifs = []
        lag_mem_ifs = []

        for tmp_if in device_mes.get("internal-lag", ()):
            if (not tmp_if.get("name")) or\
                    (is_cost_replace and (not tmp_if.get("cost"))):
                raise ValueError("internal-lag not enough information")

            tmp = copy.deepcopy(tmp_if)

            inner_ifs.append(tmp.get("name"))
            lag_ifs.append(
                self._get_internal_if_replace_info(tmp,
                                                   self._if_type_lag, db_info))

            if tmp.get("internal-interface"):
                for lag_mem in tmp.get("internal-interface"):
                    if (not lag_mem.get("name")or
                            lag_mem.get("operation")is None):
                        raise ValueError(
                            "internal-interface not enough information ")
                    lag_mem_ifs.append(self._get_lag_mem_if_info(tmp, lag_mem))

        inner_ifs = copy.deepcopy(phy_ifs)
        inner_ifs.extend(lag_ifs)

        return phy_ifs, lag_ifs, lag_mem_ifs, inner_ifs

    @decorater_log
    def _get_internal_if_info(self,
                              if_info,
                              if_type=None,
                              need_oppo_info=True):
        '''
        Obtain internal link information from EC message.
        (regardless of physical, LAG)
        '''
        op_node_type = None
        op_node_vpn = None
        op_node_os = None
        inner_vlan = None

        if not if_info.get("opposite-node-name"):
            raise ValueError("fault opposite-node device = %s" %
                             (if_info.get("opposite-node-name")))
        elif if_info.get("opposite-node-name") == "Recover":
            inner_vlan = if_info.get("vlan-id")
        else:
            op_node_type, op_node_vpn = \
                self.common_util_db.read_device_type(
                    if_info.get("opposite-node-name"))
            if need_oppo_info:
                if (not op_node_type):
                    raise ValueError("fault opposite-node-type device = %s" %
                                     (if_info.get("opposite-node-name")))
            op_node_os = \
                self.common_util_db.read_device_os(
                    if_info.get("opposite-node-name"))
            if not op_node_os:
                raise ValueError("fault opposite-node-os device = %s" %
                                 (if_info.get("opposite-node-name")))

            if op_node_os in self.internal_link_vlan_config:
                inner_vlan = if_info.get("vlan-id")

        tmp = {
            "IF-TYPE": if_type,
            "IF-NAME": if_info.get("name"),
            "OPPOSITE-NODE-TYPE": op_node_type,
            "OPPOSITE-NODE-VPN": self._vpn_types.get(op_node_vpn),
            "IF-ADDR": if_info.get("address"),
            "IF-PREFIX": if_info.get("prefix"),
            "INNER-IF-VLAN": inner_vlan,
            "OSPF-METRIC": if_info.get("cost",
                                       self._DEFAULT_INTERNAL_LINK_COST)
        }
        if if_type == self._if_type_lag:
            tmp.update(self._get_lag_if_info(if_info))
        return tmp

    @decorater_log
    def _get_internal_if_del_info(self, if_info, if_type=None, db_info=None):
        '''
        Obtain internal link information from EC message.
        (regardless of physical, LAG)
        '''
        internal_link_db = self._get_internal_link_db(
            db_info, if_info.get("name"))

        tmp = {
            "IF-TYPE": if_type,
            "IF-NAME": if_info.get("name"),
            "INNER-IF-VLAN": internal_link_db.get("vlan_id")
        }
        if if_type == self._if_type_lag:
            tmp.update(self._get_lag_if_info(if_info))
        return tmp

    @decorater_log
    def _get_internal_link_db(self, db_info, if_name):
        '''
        Obtain the relevant Internal Link Information（DB)
        '''
        for internal_link_db in db_info.get("internal-link", ()):
            if internal_link_db.get("if_name") == if_name:
                return internal_link_db
        raise ValueError("fault get_internal_link_db")

    @decorater_log
    def _get_internal_if_replace_info(self,
                                      if_info,
                                      if_type=None,
                                      db_info=None):
        '''
        Obtain the informaiton about Internal Link from EC message(Regardless of physical or LAG)
        '''
        internal_link_db = self._get_internal_link_db(
            db_info, if_info.get("name"))

        tmp = {
            "IF-TYPE": if_type,
            "IF-NAME": if_info.get("name"),
            "INNER-IF-VLAN": internal_link_db.get("vlan_id"),
            "OSPF-METRIC": if_info.get("cost")
        }
        if if_type == self._if_type_lag:
            tmp.update(self._get_lag_if_info(if_info))
        return tmp

    @decorater_log
    def _get_if_condition_from_ec(self,
                                  device_mes,
                                  service=None,
                                  operation=None,
                                  db_info=None):
        '''
        Obtain EC message related to OF open/close and DB information.
        '''

        phy_ifs = []

        for tmp_if in device_mes.get("interface-physical", ()):
            if (not tmp_if.get("name") or
                    tmp_if.get("condition")is None):
                raise ValueError("interface-physical not enough information")

            tmp = copy.deepcopy(tmp_if)

            phy_ifs.append(
                self._get_if_condition_info(tmp))

        lag_ifs = []

        for tmp_if in device_mes.get("internal-lag", ()):
            if (not tmp_if.get("name") or
                    tmp_if.get("condition") is None):
                raise ValueError("internal-lag not enough information")

            tmp = copy.deepcopy(tmp_if)

            lag_ifs.append(
                self._get_if_condition_info(tmp))

        return phy_ifs, lag_ifs

    @decorater_log
    def _get_if_condition_info(self, if_info):
        '''
        Obtain IF information from EC message(regardless of physical, LAG).
        '''
        tmp = {
            "IF-NAME": if_info.get("name"),
            "CONDITION": if_info.get("condition"),
        }
        return tmp

    @decorater_log
    def _get_cp_interface_info_from_ec(self, cp_dicts, cp_info, db_info):
        '''
        Collect IF information relating to slice from EC message
        (independent unit CPs). (common for L2, L3)
        '''
        if_name = cp_info.get("name")
        vlan_id = cp_info.get("vlan-id")
        if not if_name or vlan_id is None:
            raise ValueError("CP is not enough information")
        if if_name not in cp_dicts:
            tmp = {
                "IF-TYPE": (self._if_type_lag
                            if self._lag_check.search(if_name)
                            else self._if_type_phy),
                "IF-NAME": if_name,
                "IF-IS-VLAN":  bool(vlan_id),
                "OPERATION": None,
                "VLAN":  {},
            }

            if cp_info.get("qos"):
                tmp["QOS"] = self._get_cp_qos_info_from_ec(cp_info, db_info)
            cp_dicts[if_name] = tmp
        else:
            tmp = cp_dicts[if_name]
        return tmp, vlan_id


    @decorater_log
    def _get_l2_cps_from_ec(self,
                            device_mes,
                            db_info,
                            slice_name=None,
                            operation=None):
        '''
        Parameter from EC. (obtain cp data from cp)
        '''
        cp_dicts = {}
        if not device_mes.get("cp"):
            raise ValueError("not found L2CP Data from EC")
        for tmp_cp in device_mes.get("cp"):
            tmp, vlan_id = self._get_cp_interface_info_from_ec(
                cp_dicts, tmp_cp, db_info)
            if_name = tmp["IF-NAME"]
            cp_ope = tmp_cp.get("operation", self._MERGE)
            if (tmp["IF-TYPE"] == self._if_type_lag and
                    not tmp.get("IF-LAG-LINKS")):
                for tmp_lag in db_info.get("lag", ()):
                    if tmp_lag["if_name"] == if_name:
                        tmp["IF-LAG-LINKS"] = tmp_lag.get("links")
                        break
            is_ec_evpn = bool(tmp_cp.get("esi", tmp_cp.get("system-id")))
            if not tmp.get("EVPN-MULTI") and is_ec_evpn:
                esi = tmp_cp.get("esi")
                system_id = tmp_cp.get("system-id")
                if (esi and not system_id) or (not esi and system_id):
                    raise ValueError("EVPN ESI data is enough data")
                tmp["EVPN-MULTI"] = {
                    "OPERATION": cp_ope,
                    "IF-ESI": esi,
                    "IF-SYSTEM-ID": system_id,
                }
                if ((cp_ope == self._DELETE and is_ec_evpn) or
                        (cp_ope == self._MERGE and
                         not tmp_cp.get("port-mode"))):
                    tmp["OPERATION"] = self._REPLACE
            elif (not tmp.get("EVPN-MULTI") and cp_ope == self._DELETE):
                db_cp = self._get_vlan_if_from_db(db_info,
                                                  if_name,
                                                  slice_name,
                                                  vlan_id,
                                                  "cp")
                if db_cp.get("vni") is not None:
                    tmp["EVPN-MULTI"] = {
                        "IF-ESI": db_cp.get("esi"),
                        "IF-SYSTEM-ID": db_cp.get("system-id")}
            if not tmp.get("IF-PORT-MODE"):
                if tmp_cp.get("port-mode"):
                    tmp_port = tmp_cp["port-mode"]
                else:
                    db_cp = self._get_vlan_if_from_db(db_info,
                                                      if_name,
                                                      slice_name,
                                                      vlan_id,
                                                      "cp")
                    tmp_port = db_cp["vlan"]["port_mode"]
                tmp["IF-PORT-MODE"] = tmp_port
            if tmp.get("OPERATION") != self._REPLACE:
                tmp["VLAN"][vlan_id] = self._get_l2_vlan_if_info_from_ec(
                    tmp_cp, db_info, slice_name)
        return cp_dicts

    @decorater_log
    def _get_l2_vlan_if_info_from_ec(self,
                                     ec_cp,
                                     db_info,
                                     slice_name=None):
        '''
        Conduct setting for the section relating to VLAN on CP.
        '''
        if_name = ec_cp.get("name")
        vlan_id = ec_cp.get("vlan-id")
        operation = ec_cp.get("operation")
        if operation == self._DELETE:
            db_cp = self._get_vlan_if_from_db(db_info,
                                              if_name,
                                              slice_name,
                                              vlan_id,
                                              "cp")
            vni = db_cp["vni"]
        else:
            vni = ec_cp["vni"]
        return {
            "OPERATION": ec_cp.get("operation"),
            "CE-IF-VLAN-ID": ec_cp.get("vlan-id"),
            "VNI": vni,
        }

    @decorater_log
    def _get_vlans_list(self,
                        cp_dict,
                        db_info,
                        slice_name=None,
                        operation=None):
        '''
        Create list for vlans.
        (Compare CP on DB and CP on operation instruction simultaneously.)
        (Make judgment on the necessity of IF deletion and
        possibility for slice to remain inside device.)
        '''
        cos_if_list = {}
        is_vlans_del = False

        db_cp = {}
        if db_info:
            slice_name_list = []
            for tmp_db in db_info.get("cp", {}):
                if tmp_db.get("slice_name") in slice_name_list:
                    continue
                slice_name_list.append(tmp_db.get("slice_name"))
            for slice_name in slice_name_list:
                tmp_cp = self._get_db_cp_ifs(db_info, slice_name)
                db_cp = self._compound_list_val_dict(db_cp, tmp_cp)
        db_vlan = self._get_db_vlan_counts(db_cp)
        ec_vlan = self._get_ec_vlan_counts(cp_dict.copy())
        if operation == self._DELETE:
            for vlan_id, vlan in ec_vlan.items():
                if vlan["count"] == db_vlan.get(vlan_id, 0):
                    cos_if_list[vlan_id] = ec_vlan.get("VNI")
            if len(cos_if_list) == len(db_vlan):
                is_vlans_del = True
        else:
            for vlan_id in ec_vlan.keys():
                if vlan_id not in db_vlan:
                    cos_if_list[vlan_id] = ec_vlan[vlan_id].get("VNI")
        return cos_if_list, is_vlans_del

    @staticmethod
    @decorater_log
    def _compound_list_val_dict(dict_1, dict_2):
        '''
        Combine two dictionaries carrying list as the value.
        '''
        tmp = dict_1.keys()
        tmp.extend(dict_2.keys())
        tmp = list(set(tmp))
        ret_dict = {}
        for key in tmp:
            tmp_val = []
            if key in dict_1:
                tmp_val.extend(dict_1[key])
            if key in dict_2:
                tmp_val.extend(dict_2[key])
            tmp_val = list(set(tmp_val))
            ret_dict[key] = tmp_val
        return ret_dict

    @staticmethod
    @decorater_log
    def _get_db_vlan_counts(db_cp_info):
        db_vlan = {}
        for db_if in db_cp_info.values():
            for vlan in db_if:
                if vlan in db_vlan:
                    db_vlan[vlan] += 1
                else:
                    db_vlan[vlan] = 1
        return db_vlan

    @decorater_log
    def _get_ec_vlan_counts(self, ec_cp_info):
        ec_vlan = {}
        for ec_if in ec_cp_info.values():
            if ec_if.get("OPERATION") == self._REPLACE:
                continue
            for vlan_id, vlan in ec_if.get("VLAN", {}).items():
                if vlan_id in ec_vlan.keys():
                    ec_vlan[vlan_id]["count"] += 1
                else:
                    ec_vlan[vlan_id] = {"count": 1, "VNI": vlan.get("VNI")}
        return ec_vlan

    @decorater_log
    def _get_vni_list(self,
                      cp_dict,
                      db_info,
                      slice_name=None,
                      operation=None):
        '''
        Create list fir vni.
        '''
        vni_list = []
        db_vni = self._get_db_vni_counts(db_info, slice_name)
        ec_vni = self._get_ec_vni_counts(cp_dict.copy())
        if operation == self._DELETE:
            for vni in ec_vni.keys():
                if ec_vni[vni] == db_vni.get(vni, 0):
                    vni_list.append(vni)
        else:
            for vni in ec_vni.keys():
                if vni not in db_vni:
                    vni_list.append(vni)
        return vni_list

    @decorater_log
    def _get_db_vni_counts(self, db_info, slice_name):
        db_vni = {}
        db_cp = db_info.get("cp", ())
        for tmp_cp in db_cp:
            if tmp_cp.get("slice_name") == slice_name:
                vni = tmp_cp.get("vni")
                if vni in db_vni:
                    db_vni[vni] += 1
                else:
                    db_vni[vni] = 1
        return db_vni

    @decorater_log
    def _get_ec_vni_counts(self, ec_cp_info):
        ec_vni = {}
        for ec_if in ec_cp_info.values():
            if ec_if.get("OPERATION") == self._REPLACE:
                continue
            for vlan in ec_if.get("VLAN", {}).values():
                vni = vlan.get("VNI")
                if vni in ec_vni.keys():
                    ec_vni[vni] += 1
                else:
                    ec_vni[vni] = 1
        return ec_vni


    @decorater_log
    def _get_vrf_from_ec(self, device_mes):
        vrf_mes = device_mes.get("vrf", {})
        tmp = {}
        if vrf_mes:
            tmp = {
                "VRF-NAME": vrf_mes.get("vrf-name"),
                "VRF-RT": vrf_mes.get("rt"),
                "VRF-RD": vrf_mes.get("rd"),
                "VRF-ROUTER-ID": vrf_mes.get("router-id"),
            }
            if None in tmp.values():
                raise ValueError("vrf not enough information")
        return tmp

    @staticmethod
    @decorater_log
    def _get_vrrp_track_from_ec(track):
        '''
        Obtain VRRP TrackIF data from EC message.
        '''
        track_if_list = []
        for track_if in track.get("interface", ()):
            if track_if.get("name") is None:
                raise ValueError("Vrrp TrackIF is not enough Info")
            track_if_list.append(track_if["name"])
        return track_if_list

    @decorater_log
    def _get_vrrp_info_from_ec(self, ec_cp, db_info=None, slice_name=None):
        '''
        Obtain VRRP data from EC message.
        '''
        ec_vrrp = ec_cp.get("vrrp", {})
        if (ec_cp.get("operation") == self._DELETE or
                ec_vrrp.get("operation") == self._DELETE):
            vlan_if = self._get_vlan_if_from_db(db_info,
                                                ec_cp["name"],
                                                slice_name,
                                                ec_cp["vlan-id"],
                                                "vrrp_detail")
            if not vlan_if or vlan_if.get("group_id") is None:
                raise ValueError("Vrrp is not enough Info")
            tmp = {
                "OPERATION": self._DELETE,
                "VRRP-GROUP-ID": vlan_if["group_id"],
                "VRRP-VIRT-ADDR": vlan_if["virtual"].get("ipv4_address"),
                "VRRP-VIRT-ADDR6": vlan_if["virtual"].get("ipv6_address")
            }
            return tmp
        if (ec_vrrp.get("group-id") is None or
                ec_vrrp.get("priority") is None):
            raise ValueError("Vrrp is not enough Info")
        tmp = ec_vrrp.get("virtual-address", ec_vrrp.get("virtual-address6"))
        ip_addr = ipaddress.ip_address(u"%s" % (tmp,))
        tmp = {
            "VRRP-GROUP-ID": ec_vrrp["group-id"],
            "VRRP-VIRT-ADDR6": ec_vrrp.get("virtual-address6"),
            "VRRP-VIRT-ADDR": ec_vrrp.get("virtual-address"),
            "VRRP-VIRT-IP-ADDRESS": ip_addr,
            "VRRP-VIRT-PRI": ec_vrrp["priority"],
            "track": self._get_vrrp_track_from_ec(ec_vrrp.get("track", {})),
        }
        return tmp

    @decorater_log
    def _get_l3_vlan_if_info_from_ec(self,
                                     ec_cp,
                                     db_info,
                                     slice_name=None):
        '''
        Set the section relating to VLAN_IF of CP.
        '''
        if_name = ec_cp.get("name")
        tmp = {
            "OPERATION": ec_cp.get("operation"),
            "CE-IF-VLAN-ID": ec_cp.get("vlan-id"),
        }
        if ec_cp.get("vrrp"):
            tmp_vrrp = self._get_vrrp_info_from_ec(ec_cp,
                                                   db_info,
                                                   slice_name)
            if (ec_cp.get("operation") != self._DELETE and
                    tmp_vrrp.get("OPERATION") == self._DELETE):
                tmp["OPERATION"] = self._REPLACE
            tmp["VRRP"] = tmp_vrrp
        ce_if = ec_cp.get("ce-interface", {})
        self._get_if_ip_network(ce_if.get("address"), ce_if.get("prefix"))
        self._get_if_ip_network(ce_if.get("address6"), ce_if.get("prefix6"))
        tmp.update({
            "CE-IF-ADDR6": ce_if.get("address6"),
            "CE-IF-PREFIX6": ce_if.get("prefix6"),
            "CE-IF-ADDR": ce_if.get("address"),
            "CE-IF-PREFIX":  ce_if.get("prefix"),
        })
        if (ec_cp.get("vrrp") and
                not ce_if.get("address") and
                not ce_if.get("address6")):
            tmp_db_if = self._get_vlan_if_from_db(db_info,
                                                  if_name,
                                                  slice_name,
                                                  ec_cp.get("vlan-id"),
                                                  "cp")
            tmp_db_addr = tmp_db_if.get("ce_ipv4", {})
            if tmp_db_addr.get("address"):
                tmp.update({
                    "CE-IF-ADDR": tmp_db_addr.get("address"),
                    "CE-IF-PREFIX":  tmp_db_addr.get("prefix"),
                })
            tmp_db_addr = tmp_db_if.get("ce_ipv6", {})
            if tmp_db_addr.get("address"):
                tmp.update({
                    "CE-IF-ADDR6": tmp_db_addr.get("address6"),
                    "CE-IF-PREFIX6": tmp_db_addr.get("prefix6"),
                })
        return tmp

    @staticmethod
    @decorater_log
    def _get_if_ip_network(address, prefix):
        '''
        Create IP network object based on address and pre-fix.
        *IP network object will not be created and
         cidr mesage will be returned.
        
        '''
        if not address and prefix is None:
            return None
        elif not address or prefix is None:
            raise ValueError(
                "IPaddress is enough data %s/%s" % (address, prefix))
        else:
            return "%s/%d" % (address, prefix)

    @staticmethod
    @decorater_log
    def _get_vlan_if_from_db(db_info,
                             if_name,
                             slice_name,
                             vlan_id,
                             db_name):
        '''
        Obtain VLAN_IF from DB. (cp, vrf, bgp, vrrp)
        '''
        for vlan_if in db_info.get(db_name, ()):
            db_if_name = vlan_if.get("if_name")
            db_slice_name = vlan_if.get("slice_name")
            if db_name == "cp":
                db_vlan_id = vlan_if.get("vlan", {}).get("vlan_id")
            else:
                db_vlan_id = vlan_if.get("vlan_id")
            if (if_name == db_if_name and
                    slice_name == db_slice_name and
                    vlan_id == db_vlan_id):
                return vlan_if
        return {}

    @decorater_log
    def _get_l3_cps_from_ec(self,
                            device_mes,
                            db_info,
                            slice_name=None,
                            operation=None):
        '''
        Parameter from EC. (obtain cp data from cp)
        '''
        cp_dicts = {}
        for tmp_cp in device_mes.get("cp", ()):
            if (not tmp_cp.get("ce-interface") and
                tmp_cp.get("operation") is None and
                    not tmp_cp.get("vrrp")):
                continue
            tmp, vlan_id = self._get_cp_interface_info_from_ec(
                cp_dicts, tmp_cp, db_info)
            tmp["VLAN"][vlan_id] = self._get_l3_vlan_if_info_from_ec(
                tmp_cp, db_info, slice_name)
            if tmp["VLAN"][vlan_id].get("OPERATION") == self._REPLACE:
                tmp["OPERATION"] = self._REPLACE
            elif tmp["VLAN"][vlan_id].get("OPERATION") == self._DELETE:
                tmp_db_if = self._get_vlan_if_from_db(db_info,
                                                      tmp_cp["name"],
                                                      slice_name,
                                                      vlan_id,
                                                      "cp")
                tmp["IF-MTU"] = tmp_db_if.get("mtu_size")
                tmp["IF-DELETE-VLAN"] = True
            else:
                tmp["IF-MTU"] = tmp_cp.get("ce-interface", {}).get("mtu")
        return cp_dicts

    @decorater_log
    def _get_cos_if_list(self,
                         cp_dict,
                         db_info,
                         slice_name=None,
                         operation=None):
        '''
        Create list for class-or-service.
        (Compare CP on DB and CP on operation instruction simultaneously.)
        (Make judgment on the necessity of IF deletion and
        possibility for slice to remain inside device.)
        '''
        cos_if_list = []
        db_cp = {}
        if db_info:
            slice_name_list = []
            for tmp_db in db_info.get("cp", {}):
                if tmp_db.get("slice_name") in slice_name_list:
                    continue
                slice_name_list.append(tmp_db.get("slice_name"))
            for slice_name in slice_name_list:
                tmp_cp = self._get_db_cp_ifs(db_info, slice_name)
                db_cp = self._compound_list_val_dict(db_cp, tmp_cp)
        tmp_cp_dict = cp_dict.copy()
        if operation == self._DELETE:
            for if_name, cp_data in tmp_cp_dict.items():
                if cp_data.get("OPERATION") == self._REPLACE:
                    continue
                if len(cp_data["VLAN"]) == len(db_cp.get(if_name, ())):
                    tmp = {"IF-NAME": if_name,
                           "IF-PORT-MODE": cp_data.get("IF-PORT-MODE")}
                    cos_if_list.append(tmp)
                    cp_dict[if_name]["OPERATION"] = self._DELETE
                    if cp_dict[if_name].get("EVPN-MULTI"):
                        cp_dict[if_name][
                            "EVPN-MULTI"]["OPERATION"] = self._DELETE
        else:
            for if_name in tmp_cp_dict.keys():
                if if_name not in db_cp:
                    tmp = {"IF-NAME": if_name,
                           "IF-PORT-MODE":
                           tmp_cp_dict[if_name].get("IF-PORT-MODE")}
                    cos_if_list.append(tmp)
        return cos_if_list

    @decorater_log
    def _get_db_cp_ifs(self, db_info, slice_name):
        '''
        Obtain the combination of IF name and vlan from DB.
        '''
        db_cp = db_info.get("cp", ())
        if_dict = {}
        for tmp_cp in db_cp:
            if tmp_cp.get("slice_name") != slice_name:
                continue
            if_name = tmp_cp.get("if_name")
            vlan_id = tmp_cp["vlan"]["vlan_id"]
            if if_name in if_dict:
                if_dict[if_name].append(vlan_id)
            else:
                if_dict[if_name] = [vlan_id]
        return if_dict

    @decorater_log
    def _get_bgp_from_ec(self, device_mes, db_info, slice_name=None):
        '''
        Parameter from EC. (obtain bgp data from cp)
        '''
        bgp_list = []
        for tmp_cp in device_mes.get("cp", ()):
            if_name = tmp_cp["name"]
            vlan_id = tmp_cp["vlan-id"]
            if (not tmp_cp.get("bgp") and
                    tmp_cp.get("operation") != self._DELETE):
                continue
            tmpbgp = tmp_cp.get("bgp")
            if (tmp_cp.get("operation") == self._DELETE or
                    tmpbgp.get("operation") == self._DELETE):
                db_bgp = self._get_vlan_if_from_db(db_info,
                                                   if_name,
                                                   slice_name,
                                                   vlan_id,
                                                   "bgp_detail")
                if db_bgp.get("remote", {}).get("ipv4_address"):
                    bgp_list.append(self._get_params_delete_bgp(db_bgp, 4))
                if db_bgp.get("remote", {}).get("ipv6_address"):
                    bgp_list.append(self._get_params_delete_bgp(db_bgp, 6))
            else:
                if tmpbgp.get("remote-as-number") is None:
                    raise ValueError("BGP is not enough information")
                if (tmpbgp.get("local-address") or
                        tmpbgp.get("remote-address")):
                    bgp_list.append(self._get_params_bgp(tmpbgp, 4))
                if (tmpbgp.get("local-address6") or
                        tmpbgp.get("remote-address6")):
                    bgp_list.append(self._get_params_bgp(tmpbgp, 6))
        return bgp_list

    @decorater_log
    def _get_params_delete_bgp(self, bgp, ip_ver=4):
        '''
        Obtain BGP data suitable for IP version. (for deletion, re-use from DB)
        '''
        if ip_ver == 4:
            radd = bgp.get("remote", {}).get("ipv4_address")
        else:
            radd = bgp.get("remote", {}).get("ipv6_address")
        remote_ip = ipaddress.ip_address(u"%s" % (radd,))
        return {
            "OPERATION": self._DELETE,
            "BGP-IP-VERSION": ip_ver,
            "BGP-RADD": radd,
            "BGP-REMOTE-IP-ADDRESS": remote_ip,
        }

    def _get_params_bgp(self, bgp, ip_ver=4):
        '''
        Obtain BGP data suitable for IP version.
        '''
        if ip_ver == 4:
            radd = bgp.get("remote-address")
            ladd = bgp.get("local-address")
        else:
            radd = bgp.get("remote-address6")
            ladd = bgp.get("local-address6")
        remote_ip = ipaddress.ip_address(u"%s" % (radd,))
        local_ip = ipaddress.ip_address(u"%s" % (ladd,))
        return {
            "OPERATION": bgp.get("operation"),
            "BGP-MASTER": bgp.get("master"),
            "BGP-PEER-AS": bgp.get("remote-as-number"),
            "BGP-IP-VERSION": ip_ver,
            "BGP-RADD": radd,
            "BGP-LADD": ladd,
            "BGP-LOCAL-IP-ADDRESS": local_ip,
            "BGP-REMOTE-IP-ADDRESS": remote_ip,
        }

    @decorater_log
    def _get_static_routes_from_ec(self, device_mes, db_info, slice_name=None):
        '''
        Parameter from EC (Obtain static data from static)
        '''
        tmp_routes = []

        for tmp_cp in device_mes.get("cp", ()):
            if tmp_cp.get("operation") == self._DELETE:
                tmp_routes.extend(
                    self._get_db_static_linked_to_del_cp(
                        db_info,
                        slice_name,
                        tmp_cp.get("name"),
                        tmp_cp.get("vlan-id")))
            else:
                static_mes = tmp_cp.get("static", {})
                tmp_routes.extend(list(static_mes.get("route", ())))
                tmp_routes.extend(list(static_mes.get("route6", ())))

        if not tmp_routes:
            return None

        tmp_routes = self._normalizing_ec_static(tmp_routes)

        route_dict = {}
        nexthop_dict = {}
        for route in tmp_routes:
            self._get_static_route_from_ec_route(route,
                                                 route_dict,
                                                 nexthop_dict,
                                                 slice_name=slice_name)
        db_static = self._get_static_route_from_db_route(db_info, slice_name)
        s_nh_list, s_ip_list = self._check_del_static_route(nexthop_dict,
                                                            db_static)
        self._del_set_statics(route_dict, s_nh_list, s_ip_list)

        return route_dict

    @decorater_log
    def _get_db_static_linked_to_del_cp(self,
                                        db_info,
                                        slice_name,
                                        if_name,
                                        vlan_id):
        '''
        Obtain all static routes linked with CP from DB when deleting all CP.
        '''
        tmp_routes = []
        for cps in db_info.copy().get("static_detail", []):
            if (cps.get("slice_name") == slice_name and
                    cps.get("if_name") == if_name and
                    cps.get("vlan_id") == vlan_id):
                pass
                tmp_route = \
                    self._get_db_static_del_nexthop(cps.get("ipv4", {}))
                if tmp_route:
                    tmp_route["operation"] = self._DELETE
                    tmp_routes.append(tmp_route)
                tmp_route = \
                    self._get_db_static_del_nexthop(cps.get("ipv6", {}))
                if tmp_route:
                    tmp_route["operation"] = self._DELETE
                    tmp_routes.append(tmp_route)
        return tmp_routes

    @decorater_log
    def _get_db_static_del_nexthop(self, static_addrs):
        '''
        Obtain static nexthop of DB.
        ・Obtain the contents of ipv4/ipv6 tags.
        ・None will be returned if all is null inside.
        '''
        if (static_addrs.get("address") is None and
                static_addrs.get("prefix") is None and
                static_addrs.get("nexthop") is None):
            return None
        else:
            return {"address": static_addrs.get("address"),
                    "prefix": static_addrs.get("prefix"),
                    "nexthop": static_addrs.get("nexthop"), }

    @decorater_log
    def _normalizing_ec_static(self, ec_static=[]):
        '''
        Make the static route of EC message official.
        Delete the repeated orders. (note: treat them as "Error" unless
        additionally offset since repeated deletion never goes into machine.)
        Offset the additions/deletions for the same staticIP/nexthop.
        '''
        tmp_list = []
        tmp_dict = {}
        for route in copy.deepcopy(ec_static):
            if (not route.get("address") or
                route.get("prefix") is None or
                    not route.get("nexthop")):
                raise ValueError("static route not enough information")
            tmp_key = (route.get("address"),
                       route.get("prefix"),
                       route.get("nexthop"))
            tmp = -1 if route.get("operation") == self._DELETE else 1
            if tmp_dict.get(tmp_key):
                tmp_dict[tmp_key]["value"] += tmp
            else:
                tmp_dict[tmp_key] = {
                    "value": tmp,
                    "route": route
                }
        for key in tmp_dict:
            tmp = tmp_dict[key]["value"]
            if tmp < -1:
                raise ValueError("static route Invalid values")
            elif tmp == -1 or tmp > 0:
                tmp_list.append(tmp_dict[key]["route"])
        return tmp_list

    @decorater_log
    def _del_set_statics(self,
                         route_dict,
                         no_diff_np_list,
                         no_diff_ip_list):
        tmp_r_dict = copy.deepcopy(route_dict)
        for route in tmp_r_dict.keys():
            for nexthop in tmp_r_dict[route]["NEXTHOP"].keys():
                if (tmp_r_dict[route]["NEXTHOP"][nexthop] == self._DELETE and
                        (route, nexthop) not in no_diff_np_list):
                    route_dict[route]["NEXTHOP"].pop(nexthop)
            if (tmp_r_dict[route]["OPERATION"] == self._DELETE and
                    route not in no_diff_ip_list):
                route_dict[route]["OPERATION"] = None

    @decorater_log
    def _check_del_static_route(self, p_ec_static, p_db_static):
        '''
        Search the static route and static IP address applicable for deletion.
        '''
        tmp_list = []
        tmp_ip_list = []
        ec_static = copy.deepcopy(p_ec_static)
        db_static = copy.deepcopy(p_db_static)
        for key in ec_static.keys():
            if (db_static.get(key, 0) != 0 and
                    db_static.get(key) + ec_static[key] == 0):
                tmp_list.append((key[1], key[2]))
                is_del_ip = True
                for db_data in db_static.keys():
                    if (key != db_data and
                            key[0] == db_data[0] and
                            key[1] == db_data[1]):
                        is_del_ip = False
                        break
                if is_del_ip:
                    tmp_ip_list.append(key[1])
                db_static.pop(key)
        return tmp_list, tmp_ip_list

    @decorater_log
    def _get_static_route_from_db_route(self,
                                        db_info,
                                        slice_name=None):
        '''
        Obtain static route information from DB.
        '''
        tmp_routes = {}
        db_routes = []
        for static in db_info.get("static_detail", ()):
            tmp_route = self._get_db_static_del_nexthop(static.get("ipv4"))
            if tmp_route:
                db_routes.append(tmp_route)
            tmp_route = self._get_db_static_del_nexthop(static.get("ipv6"))
            if tmp_route:
                db_routes.append(tmp_route)
        for route in db_routes:
            route_ip = "%s/%d" % (route.get("address"), route.get("prefix"))
            nexthop_dict_key = (slice_name,
                                route_ip,
                                route.get("nexthop"))
            tmp_routes.setdefault(nexthop_dict_key, 0)
            tmp_routes[nexthop_dict_key] += 1
        return tmp_routes

    @decorater_log
    def _get_static_route_from_ec_route(self,
                                        route_obj,
                                        route_dict,
                                        nexthop_dict,
                                        slice_name=None):
        '''
        Parameter from EC (Obtain static data from static)
        '''
        route_ip = "%s/%d" % (route_obj.get("address"),
                              route_obj.get("prefix"))
        ip_ver = ipaddress.ip_address(route_obj.get("address")).version
        if route_ip not in route_dict:
            route_dict[route_ip] = {
                "NEXTHOP":
                    {
                        route_obj.get("nexthop"): route_obj.get("operation"),
                    },
                "OPERATION": route_obj.get("operation"),
                "ROUTE-IP": route_ip,
                "IP-VERSION": ip_ver,
            }
        else:
            route_dict[route_ip]["NEXTHOP"][
                route_obj.get("nexthop")] = route_obj.get("operation")
            if route_obj.get("operation") != self._DELETE:
                route_dict[route_ip]["OPERATION"] = None
        nexthop_dict_key = (slice_name,
                            route_ip,
                            route_obj.get("nexthop"))
        nexthop_dict.setdefault(nexthop_dict_key, 0)
        nexthop_dict[nexthop_dict_key] += (
            -1 if route_obj.get("operation") == self._DELETE else 1)

    @decorater_log
    def _get_vrf_name_from_db(self, db_info, slice_name):
        '''
        Obtain VRF name from DB based on slice name.
        '''
        ret_val = None
        vrf_dtls = db_info.get("vrf_detail", ())
        for vrf_dtl in vrf_dtls:
            if vrf_dtl.get("slice_name") == slice_name:
                ret_val = vrf_dtl.get("vrf_name")
                break
        return ret_val

    @decorater_log
    def _check_l3_slice_del(self, cps_info):
        '''
        Judge whether there are any CP deletions.
        '''
        for if_info in cps_info.values():
            for vlan_info in if_info.get("VLAN", {}).values():
                if vlan_info.get("OPERATION") == self._DELETE:
                    return True
        return False

    @decorater_log
    def _check_l3_slice_all_cp_del(self,
                                   cos_ifs,
                                   device_info,
                                   slice_name):
        '''
        Judge whether there are any CP deletions.
        '''
        del_if_count = len(cos_ifs)
        db_ifs = len(self._get_db_cp_ifs(device_info, slice_name))
        return bool(del_if_count == db_ifs)


    @decorater_log
    def _gen_spine_fix_message(self, xml_obj, operation):
        ''' 
        Fixed value to create message (Spine) for Netconf.
            Called out when creating message for Spine.
        Parameter:
            xml_obj : xml object
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean 
            
        '''
        return True

    @decorater_log
    def _gen_leaf_fix_message(self, xml_obj, operation):
        '''
        Fixed value to create message (Leaf) for Netconf.
            Called out when creating message for Leaf.
        Parameter:
            xml_obj : xml object
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean (Write properly using override method)   
            
        '''
        return True

    @decorater_log
    def _gen_l2_slice_fix_message(self, xml_obj, operation):


        '''
        Fixed value to create message (L2Slice) for Netconf. 
            Called out when creating message for L2Slice.
        Parameter:
            xml_obj : xml object
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean (Write properly using override method)
        '''
        return True

    @decorater_log
    def _gen_l3_slice_fix_message(self, xml_obj, operation):
        '''
        Fixed value to create message (L3Slice) for Netconf.
            Called out when creating message for L3Slice.
        Parameter:
            xml_obj : xml object
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean (Write properly using override method)
        '''
        return True

    @decorater_log
    def _gen_ce_lag_fix_message(self, xml_obj, operation):
        '''
        Fixed value to create message (CeLag) for Netconf.
            Called out when creating message for CeLag.
        Parameter:
            xml_obj : xml object
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean (Write properly using override method)
        '''
        return True

    @decorater_log
    def _gen_internal_link_fix_message(self, xml_obj, operation):
        '''
        Fixed value to create message (InternalLink) for Netconf. 
            Called out when creating message for InternalLink.
        Parameter:
            xml_obj : xml object
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean 
        '''
        return True

    @decorater_log
    def _gen_if_condition_fix_message(self, xml_obj, operation):
        '''
        Fixed value to create message (IfCondition) for Netconf. 
            Called out when creating message for IfCondition.
        Parameter:
            xml_obj : xml object
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean (Write properly using override method)
        '''
        return True

    @decorater_log
    def _gen_breakout_fix_message(self, xml_obj, operation):
        '''
        Fixed value to create message (breakout) for Netconf.
            Called out when creating message for breakout.
        Parameter:
            xml_obj : xml object
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean (Write properly using override method)
        '''
        return True

    @decorater_log
    def _gen_cluster_link_fix_message(self, xml_obj, operation):
        '''
        Fixed value to create message (cluster-link) for Netconf.
            Called out when creating message for cluster-link.
        Parameter:
            xml_obj : xml object
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean (Write properly using override method)
        '''
        return True


    @decorater_log
    def _gen_spine_variable_message(self,
                                    xml_obj,
                                    device_info,
                                    ec_message,
                                    operation):
        '''
        Variable value to create message (Spine) for Netconf.
            Called out when creating message for Spine.
            (After fixed message has been created.)
        Parameter:
            xml_obj : xml object
            device_info : Device information
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean (Write properly using override method)
        '''
        device_mes = ec_message.get("device", {})
        device_name = device_mes.get("name")

        try:
            dev_reg_info = self._get_device_from_ec(device_mes,
                                                    service=self.name_spine)
            phy_ifs, lag_ifs, lag_mem_ifs, inner_ifs = \
                self._get_internal_link_from_ec(device_mes,
                                                service=self.name_spine)
            breakout_ifs = self._get_breakout_from_ec(device_mes)
            self._check_breakout_if_name(breakout_ifs)
        except Exception as ex:
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "ERROR : message = %s / Exception: %s" % (ec_message, ex),
                __name__)
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "Traceback:%s" % (traceback.format_exc(),),
                __name__)
            return False


        conf_node = self._set_configuration_node(xml_obj)

        self._set_system_config(conf_node, dev_reg_info["DEVICE-NAME"])

        device_count = self._get_conf_device_count(
            lag_ifs, device_mes, operation=operation)
        self._set_chassis_device_count(conf_node, device_count)
        self._set_chassis_breakout(conf_node, breakout_ifs)

        if_node = self._set_interfaces_node(conf_node)
        self._set_interface_inner_links(if_node,
                                        lag_mem_ifs=lag_mem_ifs,
                                        lag_ifs=lag_ifs,
                                        phy_ifs=phy_ifs)
        self._set_interface_loopback(if_node,
                                     dev_reg_info["LB-IF-ADDR"],
                                     dev_reg_info["LB-IF-PREFIX"])

        self._set_device_routing_options(conf_node,
                                         dev_reg_info["LB-IF-ADDR"])

        protocols_node = self._set_device_protocols(conf_node)
        self._set_device_protocols_mpls(protocols_node)
        area_node = self._set_device_protocols_ospf_area_N(
            protocols_node, dev_reg_info["OSPF-AREA-ID"])
        self._set_ospf_area_interfaces(area_node, inner_ifs, is_loopback=True)
        self._set_device_protocols_ldp(
            protocols_node, GlobalModule.SERVICE_SPINE)

        self._set_qos_policy_interfaces(conf_node,
                                        inner_ifs,
                                        self.name_spine)
        return True

    @decorater_log
    def _gen_leaf_variable_message(self,
                                   xml_obj,
                                   device_info,
                                   ec_message,
                                   operation):
        '''
        Variable value to create message (Leaf) for Netconf.
            Called out when creating message for Leaf.
            (After fixed message has been created.)
        Parameter:
            xml_obj : xml object
            device_info : Device information
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean (Write properly using override method)
        '''
        device_mes = ec_message.get("device", {})
        device_name = device_mes.get("name")

        try:
            if not device_mes.get("equipment"):
                dev_reg_info = {}
                dev_reg_info["OSPF-AREA-ID"] = device_mes["ospf"]["area-id"]
            else:
                dev_reg_info = self._get_device_from_ec(device_mes,
                                                        service=self.name_leaf)
                tmp_dev, l3v_lbb_infos = self._get_leaf_vpn_from_ec(device_mes)
                dev_reg_info.update(tmp_dev)
                phy_ifs, lag_ifs, lag_mem_ifs, inner_ifs = \
                    self._get_internal_link_from_ec(device_mes,
                                                    service=self.name_leaf)
                breakout_ifs = self._get_breakout_from_ec(device_mes)
                self._check_breakout_if_name(breakout_ifs)
            dev_reg_info.update(self._get_b_leaf_data_from_ec(device_mes,
                                                              device_info))
        except Exception as ex:
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "ERROR : message = %s / Exception: %s" % (ec_message, ex),
                __name__)
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "Traceback:%s" % (traceback.format_exc(),),
                __name__)
            return False


        conf_node = self._set_configuration_node(xml_obj)

        if not device_mes.get("equipment"):
            self._set_b_leaf_ospf_data(conf_node, dev_reg_info)
            return True

        self._set_system_config(conf_node, dev_reg_info["DEVICE-NAME"])

        device_count = self._get_conf_device_count(
            lag_ifs, device_info, operation=operation)
        self._set_chassis_device_count(conf_node, device_count)
        self._set_chassis_breakout(conf_node, breakout_ifs)

        if_node = self._set_interfaces_node(conf_node)
        self._set_interface_inner_links(if_node,
                                        lag_mem_ifs=lag_mem_ifs,
                                        lag_ifs=lag_ifs,
                                        phy_ifs=phy_ifs,
                                        vpn_type=dev_reg_info["VPN-TYPE"])
        self._set_interface_loopback(if_node,
                                     dev_reg_info["LB-IF-ADDR"],
                                     dev_reg_info["LB-IF-PREFIX"])

        self._set_device_routing_options(conf_node,
                                         dev_reg_info["LB-IF-ADDR"],
                                         dev_reg_info["VPN-TYPE"],
                                         dev_reg_info["AS-NUMBER"])

        protocols_node = self._set_device_protocols(conf_node)
        if dev_reg_info["VPN-TYPE"] == 3:
            self._set_device_protocols_mpls(protocols_node)
        gr_node = self._set_device_protocols_bgp_common(
            protocols_node,
            dev_reg_info["LB-IF-ADDR"],
            dev_reg_info["VPN-TYPE"],
            dev_reg_info["AS-NUMBER"])
        self._set_device_protocols_bgp_neighbors(gr_node,
                                                 l3v_lbb_infos,
                                                 dev_reg_info["VPN-TYPE"])

        area_node = self._set_b_leaf_ospf_data(conf_node, dev_reg_info)
        self._set_ospf_area_interfaces(area_node, inner_ifs, is_loopback=True)
        if dev_reg_info["VPN-TYPE"] == 3:
            self._set_device_protocols_ldp(
                protocols_node, GlobalModule.SERVICE_LEAF)
        if dev_reg_info["VPN-TYPE"] == 2:
            self._set_device_protocols_evpn(protocols_node)

        self._set_qos_policy_interfaces(conf_node,
                                        inner_ifs,
                                        self.name_leaf)
        if dev_reg_info["VPN-TYPE"] == 2:
            self._set_device_switch_port(conf_node, dev_reg_info["LB-IF-ADDR"])
        return True

    @decorater_log
    def _gen_l2_slice_variable_message(self,
                                       xml_obj,
                                       device_info,
                                       ec_message,
                                       operation):
        '''
        Fixed value to create message (L2Slice) for Netconf.
            Called out when creating message for L2Slice.
            (After fixed message has been created.)
        Parameter:
            xml_obj : xml object
            device_info : device information
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean (Write properly using override method)          
        '''

        if not ec_message.get("device-leaf", {}).get("cp"):
            self.common_util_log.logging(
                None,
                self.log_level_debug,
                "ERROR : message = %s" % ("Config L2CP is not found.",),
                __name__)
            return False
        if operation == self._REPLACE:
            return self._gen_l2_slice_replace_message(xml_obj,
                                                      device_info,
                                                      ec_message,
                                                      operation)

        device_mes = ec_message.get("device-leaf", {})
        device_name = device_mes.get("name")
        slice_name = device_mes.get("slice_name")

        try:
            cp_info = self._get_l2_cps_from_ec(device_mes,
                                               device_info,
                                               slice_name)

            vlans_info, is_del_vlans = self._get_vlans_list(
                cp_info,
                device_info,
                slice_name=slice_name,
                operation=operation)

            vni_list = self._get_vni_list(cp_info,
                                          device_info,
                                          slice_name=slice_name,
                                          operation=operation)

            cos_ifs = self._get_cos_if_list(cp_info,
                                            device_info,
                                            slice_name=slice_name,
                                            operation=operation)
        except Exception as ex:
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "ERROR : message = %s / Exception: %s" % (ec_message, ex),
                __name__)
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "Traceback:%s" % (traceback.format_exc(),),
                __name__)
            return False

        conf_node = self._set_configuration_node(xml_obj)
        if cp_info:
            self._set_l2_slice_interfaces(conf_node, cp_info)

        if is_del_vlans:
            self._set_xml_tag(conf_node,
                              "vlans",
                              self._ATTR_OPE,
                              self._DELETE)
        elif vlans_info:
            self._set_l2_slice_vlans(conf_node,
                                     vlans_info,
                                     operation=operation)
        if vni_list:
            self._set_l2_slice_protocols_evpn(conf_node,
                                              vni_list,
                                              operation=operation)
        if cos_ifs:
            self._set_qos_policy_interfaces(conf_node,
                                            cos_ifs,
                                            self.name_l2_slice,
                                            operation)
        return True

    @decorater_log
    def _gen_l2_slice_replace_message(self,
                                      xml_obj,
                                      device_info,
                                      ec_message,
                                      operation):
        '''
        Variable value to create message (L2Slice) for Netconf.
            Called out when creating message for L2Slice.
            (After fixed message has been created.)
        Parameter:
            xml_obj : xml object
            device_info : Device information
            ec_message : EC Message
            operation : Designate "delete" when deleting.
        Return value:
            Creation result : Boolean (Write properly using override method)
        '''
        device_mes = ec_message.get("device-leaf", {})
        device_name = None
        try:
            device_name = device_mes["name"]
            slice_name = device_mes["slice_name"]

            qos_info = self._get_l2_cps_qos_from_ec(device_mes,
                                                    device_info,
                                                    slice_name)
        except Exception as ex:
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "ERROR : message = %s / Exception: %s" % (ec_message, ex),
                __name__)
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "Traceback:%s" % (traceback.format_exc(),),
                __name__)
            return False

        conf_node = self._set_configuration_node(xml_obj)

        if qos_info:
            self._set_l2_slice_qos(conf_node, qos_info)

        return True

    @decorater_log
    def _get_l2_cps_qos_from_ec(self,
                                device_mes,
                                db_info,
                                slice_name=None,
                                operation=None):
        '''
        Obtain paramter from EC( obtain qos data from cp.)
        '''
        cp_dicts = {}
        for tmp_cp in device_mes.get("cp", ()):
            if (not tmp_cp.get("qos")):
                continue
            tmp, vlan_id = self._get_cp_interface_info_from_ec(
                cp_dicts, tmp_cp, db_info)
            port_mode = self._get_port_mode_l2slice_update(
                slice_name, tmp_cp, db_info)
            if port_mode == self._PORT_MODE_ACCESS:
                tmp["QOS"][
                    "REMARK-MENU"]["IPV4"] = "input_vpnbulk_l2_be_ce_filter"
                tmp["QOS"][
                    "REMARK-MENU"]["IPV6"] = "input_vpnbulk_l2_be_ce_filter"
            else:
                tmp["QOS"]["REMARK-MENU"]["IPV4"] = "input_l2_ce_filter"
                tmp["QOS"]["REMARK-MENU"]["IPV6"] = "input_l2_ce_filter"

            tmp["VLAN"][vlan_id] = self._get_qos_l2_vlan_if_info_from_ec(
                tmp_cp, db_info, slice_name)
            if tmp["VLAN"][vlan_id].get("OPERATION") == self._REPLACE:
                tmp["OPERATION"] = self._REPLACE

        return cp_dicts

    @decorater_log
    def _get_port_mode_l2slice_update(self, slice_name, cp_ec_msg, db_info):
        '''
        Match the EC message (CP information) with the DB information and
        acquire the port_mode of the CP currently being processed.
        '''
        if_name = cp_ec_msg.get("name")
        vlan_id = cp_ec_msg.get("vlan-id")

        port_mode = None
        for cp_db in db_info.get("cp", []):
            if cp_db.get("slice_name") == slice_name and \
                    cp_db.get("if_name") == if_name and \
                    cp_db.get("vlan", {}).get("vlan_id") == vlan_id:
                port_mode = cp_db.get("vlan", {}).get("port_mode")
                break
        if port_mode is None:
            raise ValueError(
                "getting port_mode from DB is None (or not fount)")
        return port_mode

    @decorater_log
    def _get_qos_l2_vlan_if_info_from_ec(self,
                                         ec_cp,
                                         db_info,
                                         slice_name=None):
        '''
        Set the part related to the VLAN IF of the CP.
        '''
        tmp = {
            "OPERATION": ec_cp.get("operation"),
            "CE-IF-VLAN-ID": ec_cp.get("vlan-id"),
        }

        return tmp

    @decorater_log
    def _set_l2_slice_qos(self, conf_node, qos_infos=None):
        '''
        Set qos for changing L2 VLAN IF.
        '''
        node_1 = self._set_interfaces_node(conf_node)
        for tmp_cp in qos_infos.values():
            self._set_qos_l2_vlan_if(node_1, tmp_cp)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (conf_node.tag, etree.tostring(node_1)),
            __name__)

    @decorater_log
    def _set_qos_l2_vlan_if(self,
                            ifs_node,
                            cp_info):
        '''
        Set IF(qos) for changing L2 VLAN IF.
        '''
        node_1 = self._set_xml_tag(ifs_node, "interface")
        self._set_xml_tag(node_1, "name", None, None, cp_info.get("IF-NAME"))
        if cp_info.get("VLAN"):
            for unit in cp_info.get("VLAN").values():
                tmp_qos = cp_info.get("QOS")
                self._set_qos_l2_vlan_unit(node_1,
                                           unit,
                                           qos=tmp_qos)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (ifs_node.tag, etree.tostring(node_1)),
            __name__)
        return node_1

    @decorater_log
    def _set_qos_l2_vlan_unit(self,
                              if_node,
                              vlan,
                              qos={}):
        '''
        Set unit to interface node.
        '''
        attr = self._ATTR_OPE
        attr_val = self._REPLACE

        node_1 = self._set_xml_tag(if_node, "unit")
        self._set_xml_tag(node_1,
                          "name",
                          None,
                          None,
                          0)
        node_2 = self._set_xml_tag(node_1, "family")

        node_3 = self._set_xml_tag(node_2, "ethernet-switching")

        node_4 = self._set_xml_tag(node_3, "filter")
        self._set_xml_tag(
            node_4, "input", attr,
            attr_val, qos.get("REMARK-MENU").get("IPV4"))

        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (if_node.tag, etree.tostring(node_1)),
            __name__)
        return node_1

    @decorater_log
    def _gen_l3_slice_replace_message(self,
                                      xml_obj,
                                      device_info,
                                      ec_message,
                                      operation):
        '''
        Variable value to create message (L3Slice) for Netconf.
            Called out when creating message for L3Slice.
            (After fixed message has been created.)
        Parameter:
            xml_obj : xml object
            device_info : Device information
            operation : Designate "delete" when deleting.
        Return value:
            Creation result : Boolean (Write properly using override method)
        '''
        device_mes = ec_message.get("device-leaf", {})
        device_name = None
        try:
            device_name = device_mes["name"]
            slice_name = device_mes["slice_name"]
            vrf_name = self._get_vrf_name_from_db(device_info, slice_name)
            if not vrf_name:
                raise ValueError(
                    "getting vrf_name from DB is None (or not fount)")
            static = self._get_static_routes_from_ec(device_mes,
                                                     device_info,
                                                     slice_name)

            qos_info = self._get_l3_cps_qos_from_ec(device_mes,
                                                    device_info,
                                                    slice_name)
        except Exception as ex:
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "ERROR : message = %s / Exception: %s" % (ec_message, ex),
                __name__)
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "Traceback:%s" % (traceback.format_exc(),),
                __name__)
            return False

        conf_node = self._set_configuration_node(xml_obj)
        if static:
            self._set_slice_protocol_static_route(conf_node,
                                                  vrf_name,
                                                  static)

        if qos_info:
            self._set_l3_slice_qos(conf_node, qos_info)

        return True

    @decorater_log
    def _get_l3_cps_qos_from_ec(self,
                                device_mes,
                                db_info,
                                slice_name=None,
                                operation=None):
        '''
        Get qos data from parameter (cp) from EC message.
        '''
        cp_dicts = {}
        for tmp_cp in device_mes.get("cp", ()):
            if (not tmp_cp.get("qos")):
                continue
            tmp, vlan_id = self._get_cp_interface_info_from_ec(
                cp_dicts, tmp_cp, db_info)
            tmp["VLAN"][vlan_id] = self._get_qos_l3_vlan_if_info_from_ec(
                tmp_cp, db_info, slice_name)
            if tmp["VLAN"][vlan_id].get("OPERATION") == self._REPLACE:
                tmp["OPERATION"] = self._REPLACE

        return cp_dicts

    @decorater_log
    def _get_qos_l3_vlan_if_info_from_ec(self,
                                         ec_cp,
                                         db_info,
                                         slice_name=None):
        '''
        Set the part related to VLAN_IF of CP.
        '''
        if_name = ec_cp.get("name")
        tmp = {
            "OPERATION": ec_cp.get("operation"),
            "CE-IF-VLAN-ID": ec_cp.get("vlan-id"),
        }

        target_cp = None
        for tmp_cp in db_info.get("cp"):
            if if_name == tmp_cp["if_name"] and \
                    ec_cp.get("vlan-id") == \
                    tmp_cp["vlan"].get("vlan_id"):
                target_cp = tmp_cp
                break

        if target_cp["ce_ipv6"]:
            tmp["CE-IF-ADDR6"] = target_cp["ce_ipv6"].get("address")
        if target_cp["ce_ipv4"]:
            tmp["CE-IF-ADDR"] = target_cp["ce_ipv4"].get("address")
        return tmp

    @decorater_log
    def _set_l3_slice_qos(self, conf_node, qos_infos=None):
        '''
        Set qos for changing L3 VLAN IF.
        '''
        node_1 = self._set_interfaces_node(conf_node)
        for tmp_cp in qos_infos.values():
            self._set_qos_l3_vlan_if(node_1, tmp_cp)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (conf_node.tag, etree.tostring(node_1)),
            __name__)

    @decorater_log
    def _set_qos_l3_vlan_if(self,
                            ifs_node,
                            cp_info):
        '''
        Set IF(qos) for changing L3 VLAN IF.
        '''
        node_1 = self._set_xml_tag(ifs_node, "interface")
        self._set_xml_tag(node_1, "name", None, None, cp_info.get("IF-NAME"))
        if cp_info.get("VLAN"):
            for unit in cp_info.get("VLAN").values():
                tmp_qos = cp_info.get("QOS")
                self._set_qos_l3_vlan_unit(node_1,
                                           unit,
                                           qos=tmp_qos)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (ifs_node.tag, etree.tostring(node_1)),
            __name__)
        return node_1

    @decorater_log
    def _set_qos_l3_vlan_unit(self,
                              if_node,
                              vlan,
                              qos={}):
        '''
        Set unit to interface node.
        '''
        attr = self._ATTR_OPE
        attr_val = self._REPLACE

        node_1 = self._set_xml_tag(if_node, "unit")
        self._set_xml_tag(node_1,
                          "name",
                          None,
                          None,
                          vlan.get("CE-IF-VLAN-ID"))
        node_2 = self._set_xml_tag(node_1, "family")

        if vlan.get("CE-IF-ADDR6"):
            node_3 = self._set_qos_l3_vlan_unit_address(
                node_2,
                6,
                attr_info=attr,
                attr_val_info=attr_val,
                qos_info=qos
            )
        if vlan.get("CE-IF-ADDR"):
            node_3 = self._set_qos_l3_vlan_unit_address(
                node_2,
                4,
                attr_info=attr,
                attr_val_info=attr_val,
                qos_info=qos
            )
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (if_node.tag, etree.tostring(node_1)),
            __name__)
        return node_1

    @decorater_log
    def _set_qos_l3_vlan_unit_address(self,
                                      family_node,
                                      ip_ver=4,
                                      **params):
        '''
        Set inet on the family node (IPv4 or IPv6)
            params : qos_info = QOS value
        '''
        qos_info = params.get("qos_info")
        attr = params.get("attr_info")
        attr_val = params.get("attr_val_info")

        tag_name = "inet" if ip_ver == 4 else "inet6"
        node_1 = self._set_xml_tag(family_node, tag_name)
        node_2 = self._set_xml_tag(node_1, "filter")
        node_3 = self._set_xml_tag(node_2, "input")
        key_name = "IPV%d" % (ip_ver,)
        filter_name = qos_info.get("REMARK-MENU").get(key_name)
        self._set_xml_tag(node_3,
                          "filter-name",
                          attr,
                          attr_val,
                          filter_name)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (family_node.tag, etree.tostring(node_1)),
            __name__)
        return node_2

    @decorater_log
    def _gen_l3_slice_variable_message(self,
                                       xml_obj,
                                       device_info,
                                       ec_message,
                                       operation):
        '''
         Fixed value to create message (L3Slice) for Netconf.
            Called out when creating message for L3Slice.
            (After fixed message has been created.)
        Parameter:
            xml_obj : xml object
            device_info : device information
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean (Write properly using override method)           
            
        '''
        if not ec_message.get("device-leaf", {}).get("cp"):
            self.common_util_log.logging(
                None,
                self.log_level_debug,
                "ERROR : message = %s" % ("Config L3CP is not found.",),
                __name__)
            return False
        if operation == self._REPLACE:
            return self._gen_l3_slice_replace_message(xml_obj,
                                                      device_info,
                                                      ec_message,
                                                      operation)

        device_mes = ec_message.get("device-leaf", {})
        device_name = None
        try:
            device_name = device_mes["name"]
            slice_name = device_mes["slice_name"]
            if device_mes.get("vrf"):
                vrf_name = device_mes["vrf"]["vrf-name"]
            else:
                vrf_name = self._get_vrf_name_from_db(device_info, slice_name)
                if not vrf_name:
                    raise ValueError(
                        "getting vrf_name from DB is None (or not fount)")
            vrf = self._get_vrf_from_ec(device_mes)
            cp_info = self._get_l3_cps_from_ec(device_mes,
                                               device_info,
                                               slice_name)
            cos_ifs = self._get_cos_if_list(cp_info,
                                            device_info,
                                            slice_name=slice_name,
                                            operation=operation)
            bgp = self._get_bgp_from_ec(device_mes,
                                        device_info,
                                        slice_name)
            static = self._get_static_routes_from_ec(device_mes,
                                                     device_info,
                                                     slice_name=slice_name)
        except Exception as ex:
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "ERROR : message = %s / Exception: %s" % (ec_message, ex),
                __name__)
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "Traceback:%s" % (traceback.format_exc(),),
                __name__)
            return False

        conf_node = self._set_configuration_node(xml_obj)
        if cp_info:
            self._set_l3_slice_interfaces(conf_node, cp_info)
        is_all_del = False
        if operation == self._DELETE:
            is_cp_del = self._check_l3_slice_del(cp_info)
            is_all_del = self._check_l3_slice_all_cp_del(cos_ifs,
                                                         device_info,
                                                         slice_name)
            if is_all_del:
                self._set_l3_slice_routing_instance(conf_node,
                                                    vrf_name,
                                                    self._DELETE)
            elif is_cp_del:
                node_1 = self._set_l3_slice_routing_instance(conf_node,
                                                             vrf_name)
                self._set_l3_slice_routing_instance_interface(
                    node_1,
                    cp_info,
                    self._DELETE)
        elif vrf:
            self._set_l3_slice_routing_instance_vrf(conf_node,
                                                    vrf_name,
                                                    vrf,
                                                    cp_info)
        if bgp and not is_all_del:
            self._set_slice_protocol_bgp(conf_node, vrf_name, bgp)
        if static and not is_all_del:
            self._set_slice_protocol_static_route(conf_node,
                                                  vrf_name,
                                                  static)
        if cos_ifs:
            self._set_qos_policy_interfaces(conf_node,
                                            cos_ifs,
                                            self.name_l3_slice,
                                            operation)
        return True

    @decorater_log
    def _gen_ce_lag_variable_message(self,
                                     xml_obj,
                                     device_info,
                                     ec_message,
                                     operation):
        '''            
        Fixed value to create message (CeLag) for Netconf.
            Called out when creating message for CeLag.
            (After fixed message has been created.)
        Parameter:
            xml_obj : xml object
            device_info : device information
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean (Write properly using override method)            
        '''
        device_mes = ec_message.get("device", {})
        device_name = device_mes.get("name")

        try:
            if not device_mes.get("ce-lag-interface"):
                raise ValueError("Config CE-LAG is not found.")
            lag_ifs, lag_mem_ifs = \
                self._get_ce_lag_from_ec(device_mes,
                                         operation=operation)
        except Exception as ex:
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "ERROR : message = %s / Exception: %s" % (ec_message, ex),
                __name__)
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "Traceback:%s" % (traceback.format_exc(),),
                __name__)
            return False

        conf_node = self._set_configuration_node(xml_obj)

        if operation != self._REPLACE:
            device_count = self._get_conf_device_count(
                lag_ifs, device_info, operation=operation)
            self._set_chassis_device_count(conf_node, device_count)

        if_node = self._set_interfaces_node(conf_node)

        for tmp_if in lag_mem_ifs:
            self._set_interface_lag_member(if_node,
                                           lag_mem_ifs=tmp_if,
                                           operation=operation)
        for tmp_if in lag_ifs:
            self._set_interface_lag(if_node,
                                    tmp_if.get("IF-NAME"),
                                    tmp_if.get("LAG-LINKS"),
                                    tmp_if.get("LAG-SPEED"),
                                    operation=operation)
        return True

    @decorater_log
    def _gen_internal_link_variable_message(self,
                                            xml_obj,
                                            device_info,
                                            ec_message,
                                            operation):
        '''
        Variable value to create message (InternalLag) for Netconf.
            Called out when creating message for InternalLag.
            (After fixed message has been created.)
        Parameter:
            xml_obj : xml object
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean (Write properly using override method)
        '''
        device_mes = ec_message.get("device", {})
        device_name = device_mes.get("name")

        vpns = {"l2": 2, "l3": 3}

        try:
            area_id = device_info["device"]["ospf"]["area_id"]
            breakout_ifs = None
            vpn_type = None
            is_cost_replace = False
            if operation == self._DELETE:
                phy_ifs, lag_ifs, lag_mem_ifs, inner_ifs = \
                    self._get_del_internal_link_from_ec(
                        device_mes,
                        service=self.name_internal_link,
                        operation=operation,
                        db_info=device_info)
            elif operation == self._REPLACE:
                is_cost_replace = self._check_replace_kind(device_mes)
                phy_ifs, lag_ifs, lag_mem_ifs, inner_ifs = \
                    self._get_replace_internal_link_from_ec(
                        device_mes,
                        service=self.name_internal_link,
                        operation=operation,
                        db_info=device_info,
                        is_cost_replace=is_cost_replace)
            else:
                vpn_type = vpns.get(
                    ec_message.get("device", {}).get("vpn-type"))
                phy_ifs, lag_ifs, lag_mem_ifs, inner_ifs = \
                    self._get_internal_link_from_ec(
                        device_mes,
                        service=self.name_internal_link,
                        db_info=device_info)
                breakout_ifs = self._get_breakout_from_ec(device_mes)
                self._check_breakout_if_name(breakout_ifs)
        except Exception as ex:
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "ERROR : message = %s / Exception: %s" % (ec_message, ex),
                __name__)
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "Traceback:%s" % (traceback.format_exc(),),
                __name__)
            return False

        conf_node = self._set_configuration_node(xml_obj)

        if operation != self._REPLACE:
            device_count = self._get_conf_device_count(
                lag_ifs, device_info, operation=operation)
            self._set_chassis_device_count(conf_node, device_count)

            if breakout_ifs and operation != self._DELETE:
                self._set_chassis_breakout(conf_node, breakout_ifs)

        if not is_cost_replace:
            if_node = self._set_interfaces_node(conf_node)
            self._set_interface_inner_links(if_node,
                                            lag_mem_ifs=lag_mem_ifs,
                                            lag_ifs=lag_ifs,
                                            phy_ifs=phy_ifs,
                                            operation=operation,
                                            vpn_type=vpn_type)

        if operation != self._REPLACE or is_cost_replace:
            protocols_node = self._set_device_protocols(conf_node)
            area_node = self._set_device_protocols_ospf_area_N(protocols_node,
                                                               area_id)
            self._set_ospf_area_interfaces(area_node,
                                           inner_ifs,
                                           operation=operation,)

        if operation != self._REPLACE:
            self._set_qos_policy_interfaces(conf_node,
                                            inner_ifs,
                                            self.name_internal_link,
                                            operation=operation,)

        return True

    @decorater_log
    def _check_replace_kind(self, device_mes):
        '''
        Judge whether internal-link IF to be changed is for cost  value change or Lag speed change. 
        Parameter:
            device_mes : EC message(device and below)（json）
        Return value:
            result : Boolean(cost value change：True, Lag speed change：False)
        '''
        result = True

        for tmp in device_mes.get("internal-physical", ()):
            if tmp.get("cost"):
                result = True
                break
        for tmp in device_mes.get("internal-lag", ()):
            if tmp.get("cost"):
                result = True
                break
            if tmp.get("minimum-links"):
                result = False
                break

        return result

    @decorater_log
    def _gen_if_condition_variable_message(self,
                                           xml_obj,
                                           device_info,
                                           ec_message,
                                           operation):
        '''
        Variable value to create message for Netconf(IfCondition)
            Get called out when creating message for IfConditiont(after fixed message has been created)           
        Parameter:
            xml_obj : xml object
            device_info : device information
            ec_message : EC mesage
            operation : Designate "delete" when deleting. 
        Creation result : Boolean (Write properly using override method)   
   
        '''
        device_mes = ec_message.get("device", {})
        device_name = device_mes.get("name")

        try:
            phy_ifs, lag_ifs = \
                self._get_if_condition_from_ec(
                    device_mes,
                    service=self.name_if_condition,
                    operation=operation,
                    db_info=device_info)
        except Exception as ex:
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "ERROR : message = %s / Exception: %s" % (ec_message, ex),
                __name__)
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "Traceback:%s" % (traceback.format_exc(),),
                __name__)
            return False

        conf_node = self._set_configuration_node(xml_obj)

        if_node = self._set_interfaces_node(conf_node)
        for tmp_if in lag_ifs:
            self._set_interface_condition(if_node,
                                          if_mes_ec=tmp_if,
                                          operation=operation)
        for tmp_if in phy_ifs:
            self._set_interface_condition(if_node,
                                          if_mes_ec=tmp_if,
                                          operation=operation)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (if_node.tag, etree.tostring(if_node),),
            __name__)

        return True

    @decorater_log
    def _gen_breakout_variable_message(self,
                                       xml_obj,
                                       device_info,
                                       ec_message,
                                       operation):
        '''
        Variable value to create message for Netconf( breakout )
            Get called out when creating message for breakout(after fixed message has been created)
        Parameter:
            xml_obj : xml object
            device_info : Device information
            ec_message : EC message
            operation : Designate "delete" when deleting
        Return value
            Creation result : Boolean (Write properly using override method)
        '''
        device_mes = ec_message.get("device", {})
        device_name = device_mes.get("name")

        try:
            breakout_ifs = self._get_breakout_from_ec(device_mes,
                                                      operation=operation,
                                                      db_info=device_info)
            self._check_breakout_if_name(breakout_ifs)
        except Exception as ex:
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "ERROR : message = %s / Exception: %s" % (ec_message, ex),
                __name__)
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "Traceback:%s" % (traceback.format_exc(),),
                __name__)
            return False

        conf_node = self._set_configuration_node(xml_obj)

        self._set_chassis_breakout(conf_node, breakout_ifs, operation)

        return True

    @decorater_log
    def _gen_cluster_link_variable_message(self,
                                           xml_obj,
                                           device_info,
                                           ec_message,
                                           operation):
        '''
        Variable value to create message (cluster-link) for Netconf.
            Called out when creating message for cluster-link.
            (After fixed message has been created.)
        Parameter:
            xml_obj : xml object
            device_info : device information
            ec_message : EC mesage
            operation : Designate "delete" when deleting.

        Return value.
            Creation result : Boolean (Write properly using override method)            
            
        '''
        device_mes = ec_message.get("device", {})
        device_name = device_mes.get("name")

        try:
            if not device_name:
                raise ValueError("device name is not None")
            phy_ifs, lag_ifs, inner_ifs = self._get_cluster_link_from_ec(
                device_mes,
                db_info=device_info)
            if not inner_ifs:
                raise ValueError("clusterLink is not found")
        except Exception as ex:
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "ERROR : message = %s / Exception: %s" % (ec_message, ex),
                __name__)
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "Traceback:%s" % (traceback.format_exc(),),
                __name__)
            return False

        conf_node = self._set_configuration_node(xml_obj)

        if_node = self._set_interfaces_node(conf_node)
        for phy_if in phy_ifs:
            self._set_interface_cluster_link(if_node,
                                             if_info=phy_if,
                                             if_type=self._if_type_phy,
                                             operation=operation)
        for lag_if in lag_ifs:
            self._set_interface_cluster_link(if_node,
                                             if_info=lag_if,
                                             if_type=self._if_type_lag,
                                             operation=operation)

        protocols_node = self._set_device_protocols(conf_node)
        area_node = self._set_device_protocols_ospf_area_0(protocols_node)
        self._set_ospf_area_interfaces(area_node,
                                       inner_ifs,
                                       operation=operation,
                                       service=self.name_cluster_link)
        self._set_qos_policy_interfaces(conf_node,
                                        inner_ifs,
                                        self.name_cluster_link,
                                        operation=operation,)

        return True


    @decorater_log
    def _comparsion_sw_db_l2_slice(self, message, db_info):
        '''
        SW-DB comparison processing (check for information matching) (L2Slice).
            Called out when checking information matching of L2Slice.
        Parameter:
            message : Response message
            db_info : DB information
        Return value :
            Matching result :
                Boolean (Should always be "True" unless override occurs.)
        '''
        class ns_xml(object):
            '''
            Workable with name space xml analysis internal class
            '''
            class ns_list(object):
                '''
                Name space list.
                '''
                xnm = "xnm"
            n_sp_dict = {ns_list.xnm: "http://xml.juniper.net/xnm/1.1/xnm"}

            def __init__(self, ini_ns=ns_list.xnm):
                self.name_space = ini_ns

            def ns_find_node(self, parent, *tags):
                tmp = parent
                for tag in tags:
                    if (tmp is not None and
                            tmp.find("%s:%s" % (self.name_space, tag),
                                     self.n_sp_dict)is not None):
                        tmp = tmp.find("%s:%s" % (self.name_space, tag),
                                       self.n_sp_dict)
                    else:
                        return None
                return tmp

            def ns_findall_node(self, parent, tag):
                return parent.findall("%s:%s" % (self.name_space, tag),
                                      self.n_sp_dict)

        port_mtu = {self._PORT_MODE_ACCESS: 4110,
                    self._PORT_MODE_TRUNK: 4114}

        is_return = True

        ns_p = ns_xml(ns_xml.ns_list.xnm)

        cp_list = []
        if_list = []
        vni_list = []
        device_name = None
        for tmp_cp in db_info.get("cp", ()):
            cp_info = {"if_name": None,
                       "vlan_id": None,
                       "port_mode": None,
                       "vni": None,
                       "esi": None,
                       "system_id": None,
                       "links": None,
                       }.copy()
            if not device_name:
                device_name = tmp_cp.get("device_name")
            cp_info["if_name"] = tmp_cp.get("if_name")
            cp_info["vlan_id"] = (tmp_cp["vlan"].get("vlan_id")
                                  if tmp_cp.get("vlan") else None)
            cp_info["port_mode"] = (tmp_cp["vlan"].get("port_mode")
                                    if tmp_cp.get("vlan") else None)
            cp_info["vni"] = tmp_cp.get("vni")
            vni_list.append("%s" % (tmp_cp.get("vni"),))
            cp_info["esi"] = tmp_cp.get("esi")
            cp_info["system_id"] = tmp_cp.get("system-id")
            for lag in db_info.get("lag", ()):
                if cp_info["if_name"] == lag.get("if_name"):
                    cp_info["links"] = (1 if cp_info["esi"] else
                                        lag.get("links", 0))
                    break
            if cp_info["if_name"] and cp_info["vlan_id"]:
                if_list.append(cp_info["if_name"])
                cp_list.append(cp_info)

        interfaces = ns_p.ns_find_node(message,
                                       "configuration",
                                       "interfaces")
        for interface in (ns_p.ns_findall_node(interfaces, "interface")
                          if interfaces is not None else []):
            if_name = ns_p.ns_find_node(interface, "name")

            if if_name is None or if_name.text not in if_list:
                is_return = False
                self.common_util_log.logging(
                    device_name, self.log_level_debug,
                    "Config if node don't find : %s" %
                    (if_name.text if if_name is not None else None,), __name__)
                break

            mtu = ns_p.ns_find_node(interface, "mtu")

            esi = ns_p.ns_find_node(interface, "esi", "identifier")

            links = ns_p.ns_find_node(interface,
                                      "aggregated-ether-options",
                                      "minimum-links")

            system_id = ns_p.ns_find_node(interface,
                                          "aggregated-ether-options",
                                          "lacp",
                                          "system-id")

            for unit in (ns_p.ns_findall_node(interface, "unit")
                         if interface is not None else []):
                port_mode = ns_p.ns_find_node(unit,
                                              "family",
                                              "ethernet-switching",
                                              "interface-mode")
                vlans = ns_p.ns_find_node(unit,
                                          "family",
                                          "ethernet-switching",
                                          "vlan")
                for vlan in (ns_p.ns_findall_node(vlans, "members")
                             if vlans is not None else []):
                    match_flg = False
                    for db_cp in cp_list:
                        db_mtu = port_mtu.get(
                            ("%s" % (db_cp.get("port_mode"),)).lower())
                        db_esi = db_cp.get("esi")
                        db_links = db_cp.get("links")
                        db_sys_id = db_cp.get("system_id")
                        if (self._comparsion_pair(
                                if_name, db_cp.get("if_name")) and
                                self._comparsion_pair(mtu, db_mtu) and
                                self._comparsion_pair(esi, db_esi) and
                                self._comparsion_pair(links, db_links) and
                                self._comparsion_pair(system_id, db_sys_id) and
                                self._comparsion_pair(
                                port_mode, db_cp.get("port_mode")) and
                                self._comparsion_pair(
                                vlan, db_cp.get("vlan_id"))):
                            match_flg = True
                            break
                    if not match_flg:
                        self.common_util_log.logging(
                            device_name, self.log_level_debug,
                            ("VLAN don't find" +
                             " (if_name:%s mtu:%s port:%s vlan:%s)" %
                             (if_name.text if if_name is not None else None,
                              mtu.text if mtu is not None else None,
                              (port_mode.text
                               if port_mode is not None else None),
                              vlan.text if vlan is not None else None,)),
                            __name__)
                        return False

        vlans = ns_p.ns_find_node(message, "configuration", "vlans")
        for vlan in (ns_p.ns_findall_node(vlans, "vlan")
                     if is_return and vlans is not None else []):

            vlan_name = ns_p.ns_find_node(vlan, "name")
            vni = ns_p.ns_find_node(vlan, "vxlan", "vni")
            vlan_id = ns_p.ns_find_node(vlan, "vlan-id")

            is_match = False
            for db_cp in cp_list:
                if(self._comparsion_pair(
                        vlan_name, "vlan%s" % (db_cp.get("vlan_id"),)) and
                   self._comparsion_pair(vni, db_cp.get("vni")) and
                   self._comparsion_pair(vlan_id, db_cp.get("vlan_id"))):
                    is_match = True
                    break

            if not is_match:
                is_return = False
                self.common_util_log.logging(
                    device_name, self.log_level_debug,
                    "VLAN don't find (v_name:%s vni:%s v_id:%s)" %
                    (vlan_name.text if vlan_name is not None else None,
                     vni.text if vni is not None else None,
                     vlan_id.text if vlan_id is not None else None,),
                    __name__)
                break

        evpn = ns_p.ns_find_node(message,
                                 "configuration",
                                 "protocols",
                                 "evpn")
        for vni in (ns_p.ns_findall_node(evpn, "extended-vni-list")
                    if is_return and evpn is not None else []):
            if str(vni.text) not in vni_list:
                is_return = False
                self.common_util_log.logging(
                    device_name, self.log_level_debug,
                    "EVPN/VNI don't find (vni:%s / DB_vnis:%s)" %
                    (vni.text, vni_list),
                    __name__)
                break

        interfaces = ns_p.ns_find_node(message,
                                       "configuration",
                                       "class-of-service",
                                       "interfaces")
        for interface in (ns_p.ns_findall_node(interfaces, "interface")
                          if is_return and interfaces is not None else []):

            if_name = ns_p.ns_find_node(interface, "interface_name")
            if if_name is None or if_name.text not in if_list:
                is_return = False
                self.common_util_log.logging(
                    device_name, self.log_level_debug,
                    "Policy if node don't find : %s" %
                    (if_name.text if if_name is not None else None,), __name__)
                break
            unit = ns_p.ns_find_node(interface, "unit")
            if unit is not None:
                is_ok = False
                for db_cp in cp_list:
                    if (self._comparsion_pair(if_name, db_cp["if_name"]) and
                            ("%s" % (db_cp["port_mode"],)).lower() ==
                            self._PORT_MODE_TRUNK):
                        is_ok = True
                        break
                if not is_ok:
                    self.common_util_log.logging(
                        device_name, self.log_level_debug,
                        "ERROR Unknowo unit node if_name = %s" %
                        (if_name.text,), __name__)
                    is_return = False
                    break

        return is_return

    @decorater_log
    def _comparsion_sw_db_l3_slice(self, message, db_info):
        '''
        SW-DB comparison process (check for information matching) (L3Slice).
            Called out when checking information matching of L3Slice.
        Parameter:
            message : Response message
            db_info : DB information
        Return value :
            Matching result :
                Boolean (Should always be "True" unless override occurs.)
        '''
        class ns_xml(object):

            class ns_list(object):
                xnm = "xnm"
            n_sp_dict = {ns_list.xnm:
                         "http://xml.juniper.net/xnm/1.1/xnm"}

            def __init__(self, ini_ns=ns_list.xnm):
                self.name_space = ini_ns

            def ns_find_node(self, parent, *tags):
                tmp = parent
                for tag in tags:
                    if (tmp is not None and
                            tmp.find("%s:%s" % (self.name_space, tag),
                                     self.n_sp_dict)is not None):
                        tmp = tmp.find("%s:%s" % (self.name_space, tag),
                                       self.n_sp_dict)
                    else:
                        return None
                return tmp

            def ns_findall_node(self, parent, tag):
                return parent.findall("%s:%s" % (self.name_space, tag),
                                      self.n_sp_dict)

        is_return = True

        ns_p = ns_xml(ns_xml.ns_list.xnm)

        device_name = (db_info["device"].get("device_name")
                       if db_info.get("device") else "db_unknown_device")

        db_vrf = {"vrf_name": None,
                  "rt": None,
                  "rd": None,
                  "router_id": None}
        if db_info.get("vrf_detail"):
            vrf_name = db_info["vrf_detail"][0].get("vrf_name")
            db_vrf.update(db_info["vrf_detail"][0])
            self.common_util_log.logging(device_name, self.log_level_debug,
                                         "DB_VRF_COUNT = %s" % (
                                             len(db_info["vrf_detail"])),
                                         __name__)
        else:
            vrf_name = None
            self.common_util_log.logging(device_name, self.log_level_debug,
                                         "DB_VRF_COUNT = 0", __name__)

        config_node = ns_p.ns_find_node(message, "configuration")
        if config_node is None:
            is_return = False
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "ERROR cannot find configuration node",
                __name__)

        tmp_node = ns_p.ns_find_node(config_node, "interfaces")
        for cp in (ns_p.ns_findall_node(tmp_node, "interface")
                   if is_return and tmp_node is not None else []):

            if_name_node = ns_p.ns_find_node(cp, "name")
            if if_name_node is None:
                self.common_util_log.logging(
                    device_name,
                    self.log_level_debug,
                    "ERROR cannot find if name node",
                    __name__)
                is_return = False
                break

            is_vlan_tagging = False
            cp_data = None
            for db_cp in db_info.get("cp") if db_info.get("cp") else []:
                if if_name_node.text != db_cp.get("if_name"):
                    continue
                cp_dict = {
                    "if_name": None,
                    "vlan": None,
                    "mtu": None,
                    "ipv4_addr": None,
                    "ipv4_mtu": None,
                    "ipv6_addr": None,
                    "ipv6_mtu": None,
                    "vrrp_group_id": None,
                    "vrrp_v_ipv4_addr": None,
                    "vrrp_v_ipv6_addr": None,
                    "vrrp_priority": None,
                    "vrrp_track_if": None
                }
                cp_dict["if_name"] = db_cp.get("if_name")
                cp_dict["vlan"] = (db_cp["vlan"].get("vlan_id")
                                   if db_cp.get("vlan") else None)
                if cp_dict["vlan"] != 0:
                    is_vlan_tagging = True
                if db_cp.get("mtu_size") is None:
                    cp_dict["mtu"] = None
                elif cp_dict["vlan"] == 0:
                    cp_dict["mtu"] = str(int(db_cp["mtu_size"]) + 14)
                else:
                    cp_dict["mtu"] = str(int(db_cp["mtu_size"]) + 18)
                if (db_cp.get("ce_ipv4") and
                        db_cp.get("ce_ipv4").get("address") and
                        db_cp.get("ce_ipv4").get("prefix")):
                    cp_dict["ipv4_addr"] = (
                        "%s/%s" % (db_cp.get("ce_ipv4").get("address"),
                                   db_cp.get("ce_ipv4").get("prefix"))
                    )
                if (cp_dict["ipv4_addr"] is not None and
                        cp_dict["mtu"] is not None and
                        cp_dict["vlan"] != 0):
                    cp_dict["ipv4_mtu"] = db_cp["mtu_size"]
                if (db_cp.get("ce_ipv6") and
                        db_cp.get("ce_ipv6").get("address") and
                        db_cp.get("ce_ipv6").get("prefix")):
                    cp_dict["ipv6_addr"] = (
                        "%s/%s" % (db_cp.get("ce_ipv6").get("address"),
                                   db_cp.get("ce_ipv6").get("prefix"))
                    )
                if (cp_dict["ipv6_addr"] is not None and
                        cp_dict["mtu"] is not None and
                        cp_dict["vlan"] != 0):
                    cp_dict["ipv6_mtu"] = db_cp["mtu_size"]

                for vrrp in (db_info.get("vrrp_detail")
                             if db_info.get("vrrp_detail") else []):
                    if (cp_dict["if_name"] == vrrp.get("if_name") and
                            cp_dict["vlan"] == vrrp.get("vlan_id")):
                        cp_dict["vrrp_group_id"] = vrrp.get("group_id")
                        cp_dict["vrrp_v_ipv4_addr"] = (
                            vrrp["virtual"].get("ipv4_address")
                            if vrrp.get("virtual") is not None else None)
                        cp_dict["vrrp_v_ipv6_addr"] = (
                            vrrp["virtual"].get("ipv6_address")
                            if vrrp.get("virtual") is not None else None)
                        cp_dict["vrrp_priority"] = vrrp.get("priority")
                        cp_dict["vrrp_track_if"] = vrrp.get("track_if_name")
                        break
                if cp_dict["vlan"] is not None:
                    cp_data = cp_dict.copy()
                    break

            if cp_data is None:
                self.common_util_log.logging(
                    device_name,
                    self.log_level_debug,
                    ("ERROR cp_info don't have interface %s" %
                     (if_name_node.text,)),
                    __name__)
                is_return = False
                break

            tmp_text = (True if ns_p.ns_find_node(cp, "vlan-tagging")
                        is not None else False)
            if tmp_text != is_vlan_tagging:
                self.common_util_log.logging(
                    device_name,
                    self.log_level_debug,
                    ("ERROR vlan-tagging Fault (ec_mes = %s,db = %s)" %
                     (tmp_text, is_vlan_tagging)),
                    __name__)
                is_return = False
                break

            node_1 = ns_p.ns_find_node(cp, "unit")

            if not self._comparsion_pair(
                    ns_p.ns_find_node(node_1, "name"), cp_data["vlan"]):
                is_return = False
                break
            if not self._comparsion_pair(
                    ns_p.ns_find_node(node_1, "vlan-id"),
                    cp_data["vlan"] if cp_data["vlan"] != 0 else None):
                is_return = False
                break

            node_2 = ns_p.ns_find_node(node_1,
                                       "family",
                                       "inet6")
            if node_2 is not None:
                if not self._comparsion_pair(
                        ns_p.ns_find_node(node_2, "mtu"),
                        cp_data["ipv6_mtu"]):
                    is_return = False
                    break
                if not self._comparsion_pair(
                        ns_p.ns_find_node(node_2, "address", "name"),
                        cp_data["ipv6_addr"]):
                    is_return = False
                    break

                node_3 = ns_p.ns_find_node(node_2,
                                           "address", "vrrp-inet6-group")
                if node_3 is not None:
                    if not (
                            self._comparsion_pair(
                                ns_p.ns_find_node(node_3, "group_id"),
                                cp_data["vrrp_group_id"]) and
                            self._comparsion_pair(
                                ns_p.ns_find_node(
                                    node_3, "virtual-inet6-address"),
                                cp_data["vrrp_v_ipv6_addr"]) and
                            self._comparsion_pair(
                                ns_p.ns_find_node(node_3, "priority"),
                                cp_data["vrrp_priority"])
                    ):
                        is_return = False
                        break
                    node_4 = ns_p.ns_find_node(node_3, "track")
                    if node_4 is not None:
                        for track in ns_p.ns_findall_node(node_4, "interface"):
                            node_5 = ns_p.ns_find_node(
                                track, "interface_name")
                            if (node_5 is None or
                                    cp_data.get("vrrp_track_if") is None or
                                    node_5.text not in
                                    cp_data.get("vrrp_track_if")):
                                self.common_util_log.logging(
                                    device_name,
                                    self.log_level_debug,
                                    "ERROR vrrp_track_if %s don't find in %s" %
                                    (node_5, cp_data.get("vrrp_track_if")),
                                    __name__)
                                is_return = False
                                break

            node_2 = ns_p.ns_find_node(node_1,
                                       "family",
                                       "inet")
            if node_2 is not None:
                if not self._comparsion_pair(
                        ns_p.ns_find_node(node_2, "mtu"),
                        cp_data["ipv4_mtu"]):
                    is_return = False
                    break
                if not self._comparsion_pair(
                        ns_p.ns_find_node(node_2, "address", "name"),
                        cp_data["ipv4_addr"]):
                    is_return = False
                    break

                node_3 = ns_p.ns_find_node(node_2, "address", "vrrp-group")
                if node_3 is not None:
                    if not (
                            self._comparsion_pair(
                                ns_p.ns_find_node(node_3, "group_id"),
                                cp_data["vrrp_group_id"]) and
                            self._comparsion_pair(
                                ns_p.ns_find_node(
                                    node_3, "virtual-address"),
                                cp_data["vrrp_v_ipv4_addr"]) and
                            self._comparsion_pair(
                                ns_p.ns_find_node(node_3, "priority"),
                                cp_data["vrrp_priority"])
                    ):
                        is_return = False
                        break
                    node_4 = ns_p.ns_find_node(node_3, "track")
                    if node_4 is not None:
                        for track in ns_p.ns_findall_node(node_4, "interface"):
                            node_5 = ns_p.ns_find_node(
                                track, "interface_name")
                            if (node_5 is None or
                                    cp_data.get("vrrp_track_if") is None or
                                    node_5.text not in
                                    cp_data.get("vrrp_track_if")):
                                self.common_util_log.logging(
                                    device_name,
                                    self.log_level_debug,
                                    "ERROR vrrp_track_if %s don't find in %s" %
                                    (node_5, cp_data.get("vrrp_track_if")),
                                    __name__)
                                is_return = False
                                break


        node_1 = ns_p.ns_find_node(config_node,
                                   "routing-instances",
                                   "instance",
                                   "name")
        if is_return and not self._comparsion_pair(node_1, vrf_name):
            is_return = False

        node_1 = ns_p.ns_find_node(config_node,
                                   "routing-instances",
                                   "instance",
                                   "route-distinguisher",
                                   "rd-type")
        if is_return and not self._comparsion_pair(node_1, db_vrf["rd"]):
            is_return = False

        node_1 = ns_p.ns_find_node(config_node,
                                   "routing-instances",
                                   "instance",
                                   "vrf-target",
                                   "community")
        if is_return and not self._comparsion_pair(node_1, db_vrf["rt"]):
            is_return = False

        node_1 = ns_p.ns_find_node(config_node,
                                   "routing-instances",
                                   "instance",
                                   "routing-options",
                                   "router-id")
        if (is_return and
                not self._comparsion_pair(node_1, db_vrf["router_id"])):
            is_return = False

        tmp_list = []
        for db_vrf in (db_info.get("vrf_detail")
                       if is_return and db_info.get("vrf_detail") else []):
            tmp_list.append("%s.%s" % (db_vrf.get("if_name"),
                                       db_vrf.get("vlan_id")))
        node_1 = ns_p.ns_find_node(config_node,
                                   "routing-instances",
                                   "instance")
        for node_2 in (ns_p.ns_findall_node(node_1, "interface")
                       if is_return and node_1 is not None else []):
            node_3 = ns_p.ns_find_node(node_2, "name")
            if node_3.text not in tmp_list:
                self.common_util_log.logging(
                    device_name, self.log_level_debug,
                    ("ERROR vrf_if %s don't find in db_vrf (%s)" %
                     (node_3.text, tmp_list)), __name__)
                is_return = False
                break

        node_1 = ns_p.ns_find_node(config_node,
                                   "routing-instances",
                                   "instance",
                                   "routing-options")
        rib_nodes = (ns_p.ns_findall_node(node_1, "rib")
                     if node_1 is not None else [])
        if is_return and len(rib_nodes) > 0:
            tmp_list = []
            for db_static in (db_info.get("static_detail")
                              if db_info.get("static_detail") else []):
                if (db_static.get("ipv4") and
                        db_static["ipv4"].get("address") and
                        db_static["ipv4"].get("prefix") and
                        db_static["ipv4"].get("nexthop")):
                    tmp_val = ("%s.inet.0" % (vrf_name,),
                               "%s/%s" % (db_static["ipv4"].get("address"),
                                          db_static["ipv4"].get("prefix")),
                               "%s" % (db_static["ipv4"].get("nexthop"),))
                    tmp_list.append(tmp_val)
                if (db_static.get("ipv6") and
                        db_static["ipv6"].get("address") and
                        db_static["ipv6"].get("prefix") and
                        db_static["ipv6"].get("nexthop")):
                    tmp_val = ("%s.inet6.0" % (vrf_name,),
                               "%s/%s" % (db_static["ipv6"].get("address"),
                                          db_static["ipv6"].get("prefix")),
                               "%s" % (db_static["ipv6"].get("nexthop"),))
                    tmp_list.append(tmp_val)
            for node_2 in rib_nodes:
                rib_name = ns_p.ns_find_node(node_2, "name")
                tmp_node = ns_p.ns_find_node(node_2, "static")
                for node_3 in (ns_p.ns_findall_node(tmp_node, "route")
                               if tmp_node is not None else []):
                    route_name = ns_p.ns_find_node(node_3, "name")
                    nexthop_node = ns_p.ns_find_node(node_3,
                                                     "qualified-next-hop",
                                                     "nexthop")
                    tmp_val = (rib_name.text if rib_name is not None else None,
                               (route_name.text
                                if route_name is not None else None),
                               (nexthop_node.text
                                if nexthop_node is not None else None))
                    if tmp_val not in tmp_list:
                        self.common_util_log.logging(
                            device_name, self.log_level_debug,
                            ("ERROR static_route (vrf,addr/prefix,nexthop)=" +
                             "(%s,%s,%s)" % tmp_val +
                             " don't find in db_static (%s)" %
                             (tmp_list,), __name__))
                        is_return = False
                        break

        node_1 = ns_p.ns_find_node(config_node,
                                   "routing-instances",
                                   "instance",
                                   "protocols")
        if is_return and node_1 is not None:
            if (ns_p.ns_find_node(node_1, "ospf3") is not None or
                    ns_p.ns_find_node(node_1, "ospf3") is not None):
                tmp_list = []
                for db_cp in (db_info.get("cp")
                              if is_return and db_info.get("cp") else []):
                    tmp_list.append(
                        ("%s.%s" % (db_cp.get("if_name"),
                                    db_cp["vlan"].get("vlan_id")
                                    if db_cp.get("vlan") else None),
                         "%s" % (db_cp.get("metric"),))
                    )
                for node_2 in ns_p.ns_findall_node(node_1, "ospf3"):
                    node_3 = ns_p.ns_find_node(node_2,
                                               "area",
                                               "interface",
                                               "name")
                    node_4 = ns_p.ns_find_node(node_2,
                                               "area",
                                               "interface",
                                               "metric")
                    tmp_val = (node_3.text if node_3 is not None else None,
                               node_4.text if node_4 is not None else None)
                    if tmp_val not in tmp_list:
                        self.common_util_log.logging(
                            device_name, self.log_level_debug,
                            ("ERROR ospf3 (name,metric)=" +
                             "(%s,%s)" % tmp_val +
                             " don't find in db_ospf (%s)" %
                             (tmp_list,), __name__))
                        is_return = False
                for node_2 in (ns_p.ns_findall_node(node_1, "ospf")
                               if is_return else []):
                    node_3 = ns_p.ns_find_node(node_2,
                                               "area",
                                               "interface",
                                               "name")
                    node_4 = ns_p.ns_find_node(node_2,
                                               "area",
                                               "interface",
                                               "metric")
                    tmp_val = (node_3.text if node_3 is not None else None,
                               node_4.text if node_4 is not None else None)
                    if tmp_val not in tmp_list:
                        self.common_util_log.logging(
                            device_name, self.log_level_debug,
                            ("ERROR ospf (name,metric)=" +
                             "(%s,%s)" % tmp_val +
                             " don't find in db_ospf (%s)" %
                             (tmp_list,), __name__))
                        is_return = False

            node_2 = ns_p.ns_find_node(node_1, "bgp")
            if is_return and node_2 is not None:
                tmp_list = []
                for db_bgp in (db_info.get("bgp_detail")
                               if db_info.get("bgp_detail") else []):
                    bgp_as_number = db_bgp.get("as_number")
                    tmp_list.append((
                        (db_bgp["remote"].get("ipv4_address")
                         if db_bgp.get("remote") else None),
                        "%s" % (bgp_as_number,),
                        (db_bgp["local"].get("ipv4_address")
                         if db_bgp.get("local") else None)
                    ))
                    tmp_list.append((
                        (db_bgp["remote"].get("ipv6_address")
                         if db_bgp.get("remote") else None),
                        "%s" % (bgp_as_number,),
                        (db_bgp["local"].get("ipv6_address")
                         if db_bgp.get("local") else None)
                    ))
                for node_3 in ns_p.ns_findall_node(node_2, "group"):
                    node_4 = ns_p.ns_find_node(node_3, "neighbor", "name")
                    node_5 = ns_p.ns_find_node(node_3, "neighbor", "peer-as")
                    node_6 = ns_p.ns_find_node(
                        node_3, "neighbor", "local-address")
                    tmp_val = (node_4.text if node_4 is not None else None,
                               node_5.text if node_5 is not None else None,
                               node_6.text if node_6 is not None else None)
                    if tmp_val not in tmp_list:
                        self.common_util_log.logging(
                            device_name, self.log_level_debug,
                            ("ERROR bgp (name,peer-as,local-address)=" +
                             "(%s,%s,%s)" % tmp_val +
                             " don't find in db_bgp (%s)" %
                             (tmp_list,), __name__))
                        is_return = False
                        break

        tmp_list = []
        for db_cp in (db_info.get("cp")
                      if is_return and db_info.get("cp") else []):
            if db_cp.get("if_name"):
                tmp_list.append(db_cp.get("if_name"))
        node_1 = ns_p.ns_find_node(config_node,
                                   "class-of-service",
                                   "interfaces")
        for node_2 in (ns_p.ns_findall_node(node_1, "interface")
                       if is_return and node_1 is not None else []):
            node_3 = ns_p.ns_find_node(node_2, "interface_name")
            if node_3.text not in tmp_list:
                self.common_util_log.logging(
                    device_name, self.log_level_debug,
                    ("ERROR QoS_if %s don't find in db_cp_if (%s)" %
                     (node_3.text, tmp_list)), __name__)
                is_return = False
                break

        return is_return

    @decorater_log
    def _check_breakout_if_name(self,
                                breakout_ifs=[]):
        for br_if in breakout_ifs:
            self._breakout_check.search(br_if["IF-NAME"]).groups()[0]

    @decorater_log
    def _get_cp_qos_info_from_ec(self, cp_info_ec, db_info):
        '''
        Add QoS information from EC to CP information to be set.
        Parameter:
            cp_info_ec: dict  CP information input from EC.
            db_info: dict  DB Information.
        Return value:
            cp_info_em : dict  QoS information for device setting
        '''
        cp_info_em = {}

        conf_qos_remark, conf_qos_egress = GlobalModule.EM_CONFIG.get_qos_conf(
            db_info["device"].get("platform_name"),
            db_info["device"].get("os_name"),
            db_info["device"].get("firm_version"))

        tmp_remark_menu = cp_info_ec["qos"].get("remark-menu")
        for tmp_conf_key in conf_qos_remark.keys():
            if tmp_remark_menu == tmp_conf_key:
                tmp_remark_menu = conf_qos_remark[tmp_conf_key]
                break

        cp_info_em["REMARK-MENU"] = tmp_remark_menu

        return cp_info_em
