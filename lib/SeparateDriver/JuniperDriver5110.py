# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: JuniperDriver5110.py

'''
Individual section on driver
(JuniperDriver's driver(QFX5110-48S))
'''
import re
import ipaddress
from lxml import etree
import copy
import traceback
import GlobalModule
from EmCommonLog import decorater_log_in_out
from EmSeparateDriver import EmSeparateDriver
from EmCommonLog import decorater_log


class JuniperDriver5110(EmSeparateDriver):
    '''
    Individual section on driver (JuniperDriver's driver)
                    (QFX5110-48S))
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
        self.as_super = super(JuniperDriver5110, self)
        self.as_super.__init__()
        self._MERGE = GlobalModule.ORDER_MERGE
        self._DELETE = GlobalModule.ORDER_DELETE
        self._REPLACE = GlobalModule.ORDER_REPLACE
        self._vpn_types = {"l2": 2, "l3": 3}
        self.list_enable_service = [
            self.name_leaf,
            self.name_l2_slice,
            self.name_celag,
            self.name_internal_link,
            self.name_recover_node,
            self.name_recover_service,
            self.name_acl_filter,
            self.name_if_condition,
        ]
        self._lag_check = re.compile("^ae([0-9]{1,})")

        tmp_get_mes = (
            '<configuration></configuration>')
        self.get_config_message = {
            self.name_l2_slice: tmp_get_mes,
        }
        self._device_count_margin = 2
        self._device_type_leaf = "leaf"
        self._device_type_spine = "spine"
        self.driver_public_method["compare_to_latest_device_configuration"] = (
            self.compare_to_latest_device_configuration)
        self.get_config_default = tmp_get_mes

    @decorater_log_in_out
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

    @decorater_log_in_out
    def disconnect_device(self, device_name,
                          service_type=None,
                          order_type=None,
                          get_config_flag=True):
        '''
        Control part for driver individual disconnecton.
            Initiate from driver common part and 
            Protocol processing part disconnects with device.
        Parameter:
            device_name : device name
            service_type : aervice type
            order_type : order type
            get_config_flag: Flag for obtaining device config(except for in config audit）
        Return Value:
            status for process termination : Return Always true.
        '''

        is_get_ok = self._write_device_setting(device_name, get_config_flag)

        is_disconnect_device_ok = self.as_super.disconnect_device(device_name,
                                                                  service_type,
                                                                  order_type,
                                                                  get_config_flag)

        ret_val = is_get_ok and is_disconnect_device_ok

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
        Create system node(Set host-name)
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
        Create device_count node(Set LAG count)
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
    def _set_interfaces_node(self, conf_node):
        '''
        Set interfaces
        '''
        return self._xml_setdefault_node(conf_node, "interfaces")

    @decorater_log
    def _set_firewall(self, conf_node):
        '''
        Set firewall
        '''
        return self._xml_setdefault_node(conf_node, "firewall")

    @decorater_log
    def _set_firewall_ethernet_switching(self, fire_wall_node):
        '''
        Set family/ethernet-switching
        '''
        family_node = self._xml_setdefault_node(fire_wall_node, "family")
        eth_sw_node = self._xml_setdefault_node(family_node,
                                                "ethernet-switching")
        return eth_sw_node

    @decorater_log
    def _set_interface_loopback(self,
                                if_node,
                                name,
                                lo_addr=None,
                                lo_prefix=None,
                                operation=None):
        '''
        Set loopback IF
        '''
        attr, attr_val = self._get_attr_from_operation(operation)
        node_1 = self._set_xml_tag(if_node, "interface")
        self._set_xml_tag(node_1, "interface_name", None, None, "lo0")
        node_2 = self._set_xml_tag(node_1, "unit", attr, attr_val)
        self._set_xml_tag(node_2, "name", text=name)
        if operation != self._DELETE:
            node_3 = self._set_xml_tag(node_2, "family")
            node_4 = self._set_xml_tag(node_3, "inet")
            node_5 = self._set_xml_tag(node_4, "address")
            lo_addr = "{0}/{1}" .format(lo_addr, lo_prefix)
            self._set_xml_tag(node_5, "source", text=lo_addr)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (if_node.tag, etree.tostring(node_1),),
            __name__)
        return if_node

    @decorater_log
    def _set_acl_filter(self,
                        eth_sw_node,
                        filter_data,
                        operation=None):
        filter_name = filter_data["FILTER-NAME"]
        filter_node = self._set_firewall_filter_base_node(eth_sw_node,
                                                          filter_name)
        for term_data in filter_data["TERM"].values():
            self._set_acl_filter_term(filter_node,
                                      term_data,
                                      filter_name=filter_name,
                                      operation=operation)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (filter_node.tag, etree.tostring(filter_node),),
            __name__)
        return filter_node

    @decorater_log
    def _set_acl_filter_term(self,
                             filter_node,
                             term_data,
                             filter_name=None,
                             operation=None):
        attr, attr_val = self._get_attr_from_operation(operation)
        term_node = self._set_xml_tag(filter_node, "term", attr, attr_val)
        self._set_xml_tag(term_node, "name", text=term_data["TERM-NAME"])
        if operation != self._DELETE:
            self._set_acl_term_from(term_node, term_data)
            self._set_acl_term_then(term_node, filter_name=filter_name)
        return term_node

    @decorater_log
    def _set_acl_term_then(self,
                           term_node,
                           filter_name=None):
        then_node = self._set_xml_tag(term_node, "then")
        self._set_xml_tag(then_node, "discard")
        count_val = "acl_drop_{0}".format(filter_name)
        self._set_xml_tag(then_node, "count", text=count_val)
        return then_node

    @decorater_log
    def _set_acl_term_from(self,
                           term_node,
                           term_data):
        from_node = self._set_xml_tag(term_node, "from")
        tmp = term_data.get("SOURCE-MAC-ADDR", {}).get("CIDR")
        self._set_acl_term_setting_value(from_node, "source-mac-address", tmp)
        tmp = term_data.get("DESTINATION-MAC-ADDR", {}).get("CIDR")
        self._set_acl_term_setting_value(from_node,
                                         "destination-mac-address",
                                         tmp)
        if term_data.get("SOURCE-PORT") is not None:
            self._set_xml_tag(from_node,
                              "source-port",
                              text=term_data["SOURCE-PORT"])
        if term_data.get("DESTINATION-PORT") is not None:
            self._set_xml_tag(from_node,
                              "destination-port",
                              text=term_data["DESTINATION-PORT"])
        self._set_acl_term_ip_filter(from_node, term_data)
        if term_data.get("PROTOCOL") is not None:
            self._set_xml_tag(from_node,
                              "ip-protocol",
                              text=term_data["PROTOCOL"])
        return from_node

    @decorater_log
    def _set_acl_term_ip_filter(self,
                                term_node,
                                term_data):
        source_data = term_data.get("SOURCE-IP-ADDR", {})
        dest_data = term_data.get("DESTINATION-IP-ADDR", {})
        source_ip_v = source_data.get("IP_VERSION")
        dest_ip_v = dest_data.get("IP_VERSION")
        source_cidr = source_data.get("CIDR")
        dest_cidr = dest_data.get("CIDR")
        if source_ip_v == 4:
            self._set_acl_term_setting_value(term_node,
                                             "ip-source-address",
                                             source_cidr)
        if dest_ip_v == 4:
            self._set_acl_term_setting_value(term_node,
                                             "ip-destination-address",
                                             dest_cidr)
        if source_ip_v == 6 or dest_ip_v == 6:
            ip_node = self._set_xml_tag(term_node, "ip-version")
            ipv6_node = self._set_xml_tag(ip_node, "ipv6")
            if source_ip_v == 6:
                self._set_acl_term_setting_value(ipv6_node,
                                                 "ip6-source-address",
                                                 source_cidr)
            if dest_ip_v == 6:
                self._set_acl_term_setting_value(ipv6_node,
                                                 "ip6-destination-address",
                                                 dest_cidr)

    @decorater_log
    def _set_acl_term_setting_value(self,
                                    parent_node,
                                    tag_name,
                                    data=None):
        set_node = None
        if data is not None:
            set_node = self._set_xml_tag(parent_node, tag_name)
            self._set_xml_tag(set_node, "name", text=data)
        return set_node

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
        if attr_val != self._DELETE:
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
        Set physical IF
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
        Set LAGIF (can be LAG for CE as standalone)
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
        Set Internal Link IF(Common for physical and LAG)
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
        Set IF open/close information(common to physical and LAG)
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
    def _set_interface_unit_inner(self,
                                  if_node,
                                  if_addr,
                                  if_prefix,
                                  vpn_type=None,
                                  opposite_vpn_type=None,
                                  inner_vlan=0):
        '''
        Create unit node of interface node for Inter Link/Inter0cluster Link
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
        Set routing-options for device
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
        Set protocols for device
        '''
        return self._xml_setdefault_node(conf_node, "protocols")

    @decorater_log
    def _set_device_protocols_bgp_common(self,
                                         protocols_node,
                                         loopback=None,
                                         vpn_type=None,
                                         as_number=None):
        '''
        Set bgp node to protocols (except for neighbor)
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
        Set neighbor to bgp node of protocols
        '''
        for l3v_lbb in l3v_lbb_infos:
            node_1 = self._set_xml_tag(group_node, "neighbor")
            self._set_xml_tag(
                node_1, "address", None, None, l3v_lbb["RR-ADDR"])
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (group_node.tag, etree.tostring(group_node)),
            __name__)

    def _set_b_leaf_ospf_data(self, conf_node, dev_reg_info):
        '''
        Create tag for B-Leaf update (available even for B-Leaf creation)
        '''
        protocols_node = self._set_device_protocols(conf_node)
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
    def _set_device_protocols_ospf_area_N(self,
                                          protocols_node,
                                          area_id,
                                          range_addr=None,
                                          range_prefix=None,
                                          operation=None):
        '''
        Set ospf node to protocols, and set areaN (Bridge inside of cluster）
        Here, Internal Link will not be set
        '''
        attr, attr_val = self._get_attr_from_operation(operation)

        set_area_id = "0.0.0.%s" % (area_id,)

        node_1 = self._xml_setdefault_node(protocols_node, "ospf")
        node_2 = self._set_xml_tag(node_1, "area", None, None)
        self._set_xml_tag(node_2, "area_id", None, None, set_area_id)
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
        Set IF to ospf/area node
            options : service : Service name
                    ; operation : Operation type
                    ; is_loopback : Loopback configurability
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
        Set loopback IF to ospf/area node
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
    def _set_device_protocols_evpn(self, protocols_node):
        node_1 = self._set_xml_tag(protocols_node, "evpn")
        self._set_xml_tag(node_1, "encapsulation", None, None, "vxlan")
        self._set_xml_tag(node_1, "default-gateway", None, None,
                          "no-gateway-community")
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
        Set class-of-service node(QoS policy setting)
        '''
        node_1 = None
        if if_infos:
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
        Conduct interface setting of class-of-service node
        Argument：qos_info
            service：Service name
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
            else:
                self._set_qos_policy_inner_link(node_1)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (if_node.tag, etree.tostring(node_1)),
            __name__)

    @decorater_log
    def _set_qos_policy_inner_link_device_dependent(self, if_node):
        '''
        Set the device dependent section of class-of-service node(Internal Link/Inter-cluster Link)
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
        Set the device dependent section of class-of-service node(Slice addition related)
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
        Add forwarding-class-set node to if_node
        '''
        node_1 = self._set_xml_tag(if_node, "forwarding-class-set")
        self._set_xml_tag(node_1, "class-name", None, None, class_name)
        node_2 = self._set_xml_tag(node_1, "output-traffic-control-profile")
        self._set_xml_tag(node_2, "profile-name", None, None, profile_name)
        return node_1

    @decorater_log
    def _set_qos_policy_inner_link(self, if_node):
        '''
        Conduct settings related to Internal LInk of class-of-service node
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
        Conduct settings related to L2 slice of class-of-service node
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
    def _set_device_switch_port(self,
                                conf_node,
                                loopback=None):
        '''
        Set switch-options for L2Leaf
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
    def _set_l2_slice_interfaces(self,
                                 conf_node,
                                 cp_infos,
                                 dummy_cp_infos,
                                 vrf_info,
                                 irb_cps,
                                 vlan_list,
                                 dummy_list,
                                 irb_cps_del,
                                 irb_del_vlan_list,
                                 new_vlan_list,
                                 chg_dummy_if_list,
                                 virtual_gateway_address_list,
                                 vrf_id=None,
                                 is_all_del=None,
                                 is_loop_del=False,
                                 is_other_slice=False,
                                 operation=None):
        '''
        Set the entire l2CP for CE
        '''
        node_1 = self._set_interfaces_node(conf_node)
        for tmp_cp in cp_infos.values():
            self._set_l2_slice_vlan_if(node_1, tmp_cp)

        if (irb_cps and cp_infos and operation != self._DELETE) or (
                (irb_cps and dummy_cp_infos and operation != self._DELETE)):
            is_all_del = False
            self._set_l2_slice_interfaces_irb(
                node_1, irb_cps, vlan_list, dummy_list, irb_cps_del,
                irb_del_vlan_list, is_all_del)

        if (operation == self._DELETE and is_all_del and
                irb_cps and not is_other_slice):
            self._set_l2_slice_interfaces_irb_del(
                node_1, irb_del_vlan_list, is_all_del, operation)
        elif operation == self._DELETE and irb_cps:
            if new_vlan_list:
                self._set_l2_slice_interfaces_irb_del(
                    node_1,  new_vlan_list, False, operation)
            if chg_dummy_if_list:
                self._set_l2_slice_interfaces_irb_vlan_del(
                    node_1, irb_cps, vlan_list, dummy_list, irb_cps_del,
                    irb_del_vlan_list, chg_dummy_if_list,
                    virtual_gateway_address_list)

        if (irb_cps and cp_infos and is_loop_del or (
                irb_cps and len(dummy_list) == 0 and(
                    dummy_cp_infos and is_loop_del)) and (
                        operation != self._DELETE)):
            self._set_interface_loopback(node_1,
                                         vrf_id,
                                         lo_addr=vrf_info["VRF-LB-ADDR"],
                                         lo_prefix=vrf_info["VRF-LB-PREFIX"])

        if is_all_del and irb_cps:
            self._set_interface_loopback(node_1,
                                         vrf_id,
                                         operation=self._DELETE)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (conf_node.tag, etree.tostring(node_1)),
            __name__)

    @decorater_log
    def _set_l2_slice_interfaces_irb(self,
                                     ifs_node,
                                     irb_cps,
                                     vlan_list,
                                     dummy_list,
                                     irb_cps_del,
                                     irb_del_vlan_list,
                                     is_all_del=False):
        '''
        Set IRB to interfaces node
        '''
        operation = None
        node_1 = self._set_xml_tag(ifs_node, "interface")
        self._set_xml_tag(node_1, "name", None, None, "irb")

        for tmp_cp in irb_cps:

            if len(vlan_list) > 0 or len(dummy_list) > 0:
                if tmp_cp.get("VLAN"):
                    for vlan_id, unit in tmp_cp.get("VLAN").items():
                        operation = unit.get("OPERATION")
                        if vlan_id in vlan_list and (
                                tmp_cp.get("IRB") is not None):
                            self._set_l2_slice_irb_unit(node_1,
                                                        is_all_del,
                                                        irb_addr=tmp_cp.get(
                                                            "IRB"),
                                                        vlan_id=vlan_id,
                                                        operation=operation)
            else:
                if tmp_cp.get("VLAN"):
                    for vlan_id, unit in tmp_cp.get("VLAN").items():
                        operation = unit.get("OPERATION")
                        if tmp_cp.get("IRB") is not None:
                            self._set_l2_slice_irb_unit(node_1,
                                                        is_all_del,
                                                        irb_addr=tmp_cp.get(
                                                            "IRB"),
                                                        vlan_id=vlan_id,
                                                        operation=operation)

        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (ifs_node.tag, etree.tostring(node_1)),
            __name__)

    @decorater_log
    def _set_l2_slice_interfaces_irb_vlan_del(self,
                                              ifs_node,
                                              irb_cps,
                                              vlan_list,
                                              dummy_list,
                                              irb_cps_del,
                                              irb_del_vlan_list,
                                              chg_dummy_if_list,
                                              virtual_gateway_address_list):
        '''
        Set IRB to interfaces node
        '''
        operation = None
        node_1 = self._set_xml_tag(ifs_node, "interface")
        self._set_xml_tag(node_1, "name", None, None, "irb")

        for tmp_cp in irb_cps:
            if tmp_cp.get("VLAN"):
                for vlan_id, unit in tmp_cp.get("VLAN").items():
                    for chg_vlan_id in chg_dummy_if_list:
                        vlan_id = chg_vlan_id
                        if tmp_cp.get("IRB") is not None:
                            self._set_l2_slice_irb_unit_chg_dummy(
                                node_1,
                                irb_addr=tmp_cp.get(
                                    "IRB"),
                                vlan_id=vlan_id,
                                operation=operation,
                                virtual_gateway_address_list=virtual_gateway_address_list)

        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (ifs_node.tag, etree.tostring(node_1)),
            __name__)

    @decorater_log
    def _set_l2_slice_interfaces_irb_del(self,
                                         ifs_node,
                                         new_vlan_list,
                                         is_all_del,
                                         operation=None):
        '''
        Set IRB to interfaces node
        '''

        if is_all_del:
            node_1 = self._set_xml_tag(ifs_node,
                                       "interface",
                                       self._ATTR_OPE,
                                       self._DELETE)
            self._set_xml_tag(node_1, "name", None, None, "irb")
        else:
            node_1 = self._set_xml_tag(ifs_node, "interface")
            self._set_xml_tag(node_1, "name", None, None, "irb")
            for vlan_id in new_vlan_list:
                operation = "delete"
                self._set_l2_slice_irb_unit_del(node_1,
                                                vlan_id=vlan_id,
                                                operation=operation)

            self.common_util_log.logging(
                None, self.log_level_debug,
                self._XML_LOG % (ifs_node.tag, etree.tostring(node_1)),
                __name__)

    @decorater_log
    def _set_l2_slice_vlan_if(self,
                              ifs_node,
                              cp_info):
        '''
        Set l2CP for CE
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
        if (evpn is not None and
                evpn.get("OPERATION") is not None and
                evpn.get("IF-ESI") is not None and
                evpn.get("IF-SYSTEM-ID") is not None and
                evpn.get("IF-CLAG-ID") is not None):
            self._set_l2_slice_evpn_esi(node_1,
                                        evpn["IF-ESI"],
                                        evpn["OPERATION"])
            self._set_l2_slice_evpn_lag_links(node_1,
                                              cp_info.get("IF-LAG-LINKS"),
                                              evpn["OPERATION"],
                                              cp_info["IF-TYPE"])
            self._set_l2_slice_evpn_system_id(node_1,
                                              evpn["IF-SYSTEM-ID"],
                                              evpn["IF-CLAG-ID"],
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
                tmp_if_name = cp_info["IF-NAME"]
                self._set_l2_slice_vlan_unit(node_1,
                                             unit,
                                             port_mode=tmp_port,
                                             qos_info=tmp_qos,
                                             if_name=tmp_if_name)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (ifs_node.tag, etree.tostring(node_1)),
            __name__)
        return node_1

    @decorater_log
    def _set_l2_slice_vlan_unit(self, if_node, vlan, **param):
        '''
       Set unit to interface node
            param : port_mode : Designate port mode
                    qos : qos information
        '''
        port_mode = param.get("port_mode")
        qos_info = param["qos_info"] if param.get("qos_info") else {}

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

            node_5 = self._set_xml_tag(node_3, "storm-control")
            self._set_xml_tag(
                node_5, "profile-name", None, None, "default-shutdown")
            node_6 = self._set_xml_tag(node_3, "recovery-timeout")
            self._set_xml_tag(
                node_6, "time-in-seconds", None, None, 100)

            node_4 = self._set_xml_tag(node_3, "filter")
            if_name = param.get("if_name")
            new_if_name = self._change_change_underbar_name(if_name)
            self._set_xml_tag(node_4, "input", None, None,
                              "for_" + new_if_name)
            if (port_mode == self._PORT_MODE_TRUNK and
                    qos_info.get("OUTFLOW-SHAPING-RATE") is not None):
                self._set_xml_tag(node_4, "output", None, None,
                                  "for_" + new_if_name + "_egress")

        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (if_node.tag, etree.tostring(node_1)),
            __name__)
        return node_1

    @decorater_log
    def _set_l2_slice_irb_unit(self, if_node, is_all_del=None, **param):
        '''
       Set unit to interface node(irb)
            param : irb_addr : Address information for IRB configuration
                    is_dummy: Should be True in case of dummy VLAN information
                    vlan_id : Set vlan_id
        '''
        irb_addr = param.get("irb_addr")
        vlan_id = param.get("vlan_id")
        operation = param.get("operation")

        attr, attr_val = self._get_attr_from_operation(operation)

        node_1 = self._set_xml_tag(if_node, "unit")
        self._set_xml_tag(node_1, "name", attr, attr_val, vlan_id)

        if attr_val != self._DELETE:
            node_2 = self._set_xml_tag(node_1, "family")
            node_3 = self._set_xml_tag(node_2, "inet")
            node_4 = self._set_xml_tag(node_3, "address")

            irb_addr_str = irb_addr.get("IRB-ADDR") + "/" +\
                str(irb_addr.get("IRB-PREFIX"))
            self._set_xml_tag(node_4, "name", attr, attr_val, irb_addr_str)

            if irb_addr.get("IRB-VIRT-GW-ADDR"):
                self._set_xml_tag(node_4, "virtual-gateway-address",
                                  None, None,
                                  irb_addr.get("IRB-VIRT-GW-ADDR"))
            elif irb_addr.get("IRB-VIRT-GW-ADDR") and is_all_del:
                self._set_xml_tag(node_4, "virtual-gateway-address",
                                  attr, attr_val,
                                  irb_addr.get("IRB-VIRT-GW-ADDR"))

        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (if_node.tag, etree.tostring(node_1)),
            __name__)
        return node_1

    @decorater_log
    def _set_l2_slice_irb_unit_chg_dummy(self, if_node, **param):
        '''
       Set unit to interface node(irb)
            param : irb_addr : Address information for IRB configuration
                    is_dummy: Should be True in case of dummy VLAN information
                    vlan_id : Set vlan_id
        '''
        irb_addr = param.get("irb_addr")
        vlan_id = param.get("vlan_id")
        operation = param.get("operation")

        virtual_gateway_address_list = param.get(
            "virtual_gateway_address_list")
        virtual_gateway_address = None
        for tmp_virtual_gateway_address in virtual_gateway_address_list:
            if tmp_virtual_gateway_address == vlan_id:
                virtual_gateway_address = virtual_gateway_address_list[vlan_id]
        attr = self._ATRI_OPE
        attr_val = self._DELETE

        node_1 = self._set_xml_tag(if_node, "unit")
        self._set_xml_tag(node_1, "name", None, None, vlan_id)

        node_2 = self._set_xml_tag(node_1, "family")
        node_3 = self._set_xml_tag(node_2, "inet")
        node_4 = self._set_xml_tag(node_3, "address")

        irb_addr_str = irb_addr.get("IRB-ADDR") + "/" +\
            str(irb_addr.get("IRB-PREFIX"))
        self._set_xml_tag(node_4, "name", None, None, irb_addr_str)

        self._set_xml_tag(node_4, "virtual-gateway-address",
                          attr, attr_val,
                          None)

        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (if_node.tag, etree.tostring(node_1)),
            __name__)
        return node_1

    @decorater_log
    def _set_l2_slice_irb_unit_del(self, if_node, vlan_id, operation,):
        '''
       Set unit to interface node(irb)
            param : irb_addr : Address information for IRB configuration
                    is_dummy: Should be True in case of dummy VLAN information
                    vlan_id : Set vlan_id
        '''

        node_1 = self._set_xml_tag(if_node,
                                   "unit",
                                   self._ATTR_OPE,
                                   self._DELETE)
        self._set_xml_tag(node_1, "name", None, None, vlan_id)

        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (if_node.tag, etree.tostring(node_1)),
            __name__)
        return node_1

    @decorater_log
    def _set_l2_slice_evpn_esi(self, if_node, esi, operation=None):
        '''
        Set esi
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
        Set links of LAG
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
    def _set_l2_slice_evpn_system_id(self, if_node, system_id, clag_id,
                                     operation=None):
        '''
        Set system-id,admin-key of LAG
        '''
        attr, attr_val = self._get_attr_from_operation(operation)
        node_1 = self._xml_setdefault_node(if_node, "aggregated-ether-options")
        node_2 = self._set_xml_tag(node_1, "lacp")
        if operation != self._DELETE:
            self._set_xml_tag(node_2, "system-id", attr, attr_val, system_id)
            self._set_xml_tag(node_2, "admin-key", attr, attr_val, clag_id)
        else:
            self._set_xml_tag(node_2, "system-id", attr, attr_val)
            self._set_xml_tag(node_2, "admin-key", attr, attr_val)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (if_node.tag, etree.tostring(node_1)),
            __name__)
        return node_1

    @decorater_log
    def _set_l2_slice_vlans(self,
                            conf_node,
                            vlans_vni,
                            irb_cps,
                            operation=None):
        '''
        Create vlans
        '''
        node_1 = self._set_xml_tag(conf_node, "vlans")

        for vlan_id, vni in vlans_vni.items():
            is_irb = False
            for irb_cp in irb_cps:
                if vlan_id in irb_cp.get("VLAN", {}):
                    is_irb = True
                    break

            self._set_l2_slice_vlan_vni(node_1,
                                        vlan_id,
                                        vni,
                                        is_irb,
                                        operation)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (conf_node.tag, etree.tostring(node_1)),
            __name__)
        return node_1

    @decorater_log
    def _set_l2_slice_vlans_del(self,
                                conf_node,
                                del_vlan_list,
                                operation=None):
        '''
        Create vlans
        '''
        node_1 = self._set_xml_tag(conf_node, "vlans")
        for vlan_id in del_vlan_list:
            self._set_l2_slice_vlan_vni(node_1,
                                        vlan_id,
                                        None,
                                        None,
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
                               is_irb=False,
                               operation=None):
        '''
        Create vlan(vlan_id/vni setting) inside of vlans
        '''
        attr, attr_val = self._get_attr_from_operation(operation)
        node_1 = self._set_xml_tag(vlans_node, "vlan", attr, attr_val)
        self._set_xml_tag(node_1, "name", None,  None, "vlan%d" % (vlan_id,))
        if attr_val == self._DELETE:
            return node_1
        self._set_xml_tag(node_1, "no-arp-suppression", None, None, None)
        node_2 = self._set_xml_tag(node_1, "vxlan")
        self._set_xml_tag(node_2, "vni", None, None, vni)
        self._set_xml_tag(node_2, "ingress-node-replication")
        self._set_xml_tag(node_1, "vlan-id", None, None, vlan_id)
        if is_irb:
            l3_if_str = "irb.{0}".format(vlan_id)
            self._set_xml_tag(node_1, "l3-interface", None, None, l3_if_str)
        return node_1

    @decorater_log
    def _set_l2_slice_protocols_evpn(self,
                                     conf_node,
                                     vnis,
                                     operation=None):
        '''
        Create vni to protocols/evpn
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
    def _set_slice_routing_instance(self,
                                    conf_node,
                                    vrf_name,
                                    operation=None):
        '''
        Set routing_instance node
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
    def _set_slice_routing_instance_interface(self,
                                              ins_node,
                                              cps_info,
                                              dummy_cp_info,
                                              vrf_cps,
                                              operation="merge"):
        '''
        Set IF to instance node
        '''
        for if_info in cps_info.values():
            for vlan_info in if_info.get("VLAN", {}).values():
                vlan_id = vlan_info["CE-IF-VLAN-ID"]
                tmp = "%s.%d" % ("irb", vlan_id)
                attr, attr_val = self._get_attr_from_operation(
                    vlan_info.get("OPERATION"))
                if vlan_id in vrf_cps:
                    node_3 = self._set_xml_tag(
                        ins_node, "interface", attr, attr_val)
                    self._set_xml_tag(node_3, "name", None, None, tmp)

        for if_info in dummy_cp_info.values():
            for vlan_info in if_info.get("VLAN", {}).values():

                vlan_ope = vlan_info.get("OPERATION")
                vlan_ope = "merge"
                vlan_id = vlan_info["CE-IF-VLAN-ID"]
                tmp = "%s.%d" % ("irb", vlan_id)
                attr, attr_val = self._get_attr_from_operation(
                    vlan_info.get("OPERATION"))
                if vlan_id in vrf_cps:
                    node_3 = self._set_xml_tag(
                        ins_node, "interface", attr, attr_val)
                    self._set_xml_tag(node_3, "name", None, None, tmp)

    @decorater_log
    def _set_slice_routing_instance_interface_delete(self,
                                                     ins_node,
                                                     cps_info,
                                                     vrf_cps,
                                                     operation):
        '''
        Set IF to instance node
        '''
        for vlan_id in vrf_cps:
            tmp = "%s.%d" % ("irb", vlan_id)
            attr, attr_val = self._get_attr_from_operation(
                self._DELETE)
            node_3 = self._set_xml_tag(
                ins_node, "interface", attr, attr_val)
            self._set_xml_tag(node_3, "name", None, None, tmp)

    @decorater_log
    def _set_slice_routing_instance_interface_lo(self,
                                                 ins_node,
                                                 vrf_info):
        '''
        Set loopback IF to instance node
        '''
        vrf_id = vrf_info.get("VRF-ID")
        tmp = "lo0.{0}".format(vrf_id)
        node_3 = self._set_xml_tag(ins_node, "interface")
        self._set_xml_tag(node_3, "name", None, None, tmp)

    @decorater_log
    def _set_slice_routing_instance_vrf(self,
                                        conf_node,
                                        vrf_name,
                                        vrf_info,
                                        cps_info,
                                        dummy_cp_info,
                                        vrf_cps):
        '''
        Set routing_instance node
        '''
        is_configured = vrf_info.get("IS-CONFIGURED")
        node_1 = self._xml_setdefault_node(conf_node, "routing-instances")
        node_2 = self._xml_setdefault_node(node_1, "instance")
        self._set_xml_tag(node_2, "name", None, None, vrf_name)
        self._set_xml_tag(node_2, "instance-type", None, None, "vrf")
        self._set_slice_routing_instance_interface(node_2,
                                                   cps_info,
                                                   dummy_cp_info,
                                                   vrf_cps)
        if not is_configured:
            self._set_slice_routing_instance_interface_lo(node_2,
                                                          vrf_info)
            node_3 = self._set_xml_tag(node_2, "route-distinguisher")
            self._set_xml_tag(node_3, "rd-type", None,
                              None, vrf_info["VRF-RD"])
            node_3 = self._set_xml_tag(node_2, "vrf-target")
            self._set_xml_tag(node_3, "community", None,
                              None, vrf_info["VRF-RT"])

        return node_2

    @decorater_log
    def _set_vlan_traffic_firewall(self,
                                   conf_node,
                                   cps_info,
                                   device_info):
        '''
        Set firewall for VLAN traffic acquisition
        '''
        for cp_info in cps_info.values():
            operation = cp_info.get("OPERATION")
            port_mode = cp_info.get("IF-PORT-MODE")
            if_name = cp_info.get("IF-NAME")
            is_filter = cp_info.get("IS-FILTER")
            if_node = self._set_firewall(conf_node)
            eth_sw_node = self._set_firewall_ethernet_switching(if_node)
            self._set_vlan_traffic_firewall_if_filter(eth_sw_node,
                                                      if_name,
                                                      device_info,
                                                      operation=operation,
                                                      cp_info=cp_info,)
            if is_filter and port_mode == self._PORT_MODE_TRUNK:
                flow_val = None
                if operation != self._DELETE:
                    outflow = cp_info.get("QOS", {}).get(
                        "OUTFLOW-SHAPING-RATE")
                    speed = cp_info.get("IF-SPEED")
                    if_speed = None
                    if cp_info.get("IF-TYPE") == self._if_type_lag:
                        for lag_if in device_info.get("lag", {}):
                            if if_name == lag_if.get("if_name"):
                                if_speed = \
                                    int(lag_if.get("link_speed").strip("g")) * \
                                    int(lag_if.get("links"))
                                break
                    else:
                        if_speed = int(speed.strip("g"))

                    if outflow:
                        flow_val = int(round(float(outflow) *
                                             float(if_speed) * 10.0))
                    else:
                        flow_val = None
                self._set_vlan_traffic_firewall_if_egress_filter(
                    eth_sw_node,
                    if_name,
                    outflow_shaping_rate=flow_val,
                    operation=operation)

            self.common_util_log.logging(
                None, self.log_level_debug,
                self._XML_LOG % (conf_node.tag, etree.tostring(if_node)),
                __name__)

    @decorater_log
    def _set_vlan_traffic_firewall_if_filter(self,
                                             eth_sw_node,
                                             if_name,
                                             device_info,
                                             operation=None,
                                             cp_info=None):
        '''
        Create filter for IF
        '''
        port_mode = cp_info.get("IF-PORT-MODE")
        is_filter = cp_info.get("IS-FILTER")
        new_if_name = self._change_change_underbar_name(if_name)
        name_str = "for_{0}".format(new_if_name)
        filter_node = self._set_firewall_filter_base_node(eth_sw_node,
                                                          name_str,
                                                          operation)
        if operation == self._DELETE and is_filter:
            return filter_node
        if port_mode == self._PORT_MODE_ACCESS:
            self._set_vlan_traffic_firewall_term_access(filter_node)
        else:
            for tmp_vlan_id, tmp_vlan_data in cp_info.get("VLAN", {}).items():
                vlan_operation = tmp_vlan_data.get("OPERATION")
                self._set_vlan_traffic_firewall_term_trunk(filter_node,
                                                           cp_info,
                                                           if_name,
                                                           tmp_vlan_id,
                                                           device_info,
                                                           vlan_operation)
        return filter_node

    @decorater_log
    def _set_firewall_filter_base_node(self,
                                       eth_sw_node,
                                       filter_name,
                                       operation=None):
        '''
        Create filter node (until filter/name)
        '''
        attr, attr_val = self._get_attr_from_operation(operation)
        filter_node = self._set_xml_tag(eth_sw_node, "filter", attr, attr_val)
        self._set_xml_tag(filter_node, "name", None, None, filter_name)
        return filter_node

    @decorater_log
    def _set_vlan_traffic_firewall_if_egress_filter(self,
                                                    eth_sw_node,
                                                    if_name,
                                                    outflow_shaping_rate=None,
                                                    operation=None):
        '''
        Create Egress filter for IF
        '''
        attr, attr_val = self._get_attr_from_operation(operation)
        filter_node = self._set_xml_tag(eth_sw_node, "filter", attr, attr_val)
        new_if_name = self._change_change_underbar_name(if_name)
        name_str = "for_{0}_egress".format(new_if_name)
        self._set_xml_tag(filter_node, "name", text=name_str)
        if operation == self._DELETE:
            return filter_node
        term_node = (
            self._set_vlan_traffic_firewall_term_name(filter_node,
                                                      "output_accept")
        )
        from_node = self._set_xml_tag(term_node, "from")
        self._set_term_destination_mac_address(from_node,
                                               "01:80:c2:00:00:02/48")
        then_node = self._set_xml_tag(term_node, "then")
        self._set_xml_tag(then_node, "accept")
        term_node = (
            self._set_vlan_traffic_firewall_term_name(filter_node,
                                                      "output_policing")
        )
        if outflow_shaping_rate is not None:
            policer = "{0}m-limit".format(outflow_shaping_rate)
            self._set_vlan_traffic_firewall_term_then(
                term_node, policer=policer)
        else:
            policer = "1000m-limit"
            self._set_vlan_traffic_firewall_term_then(
                term_node, policer=policer)

        return filter_node

    @decorater_log
    def _set_vlan_traffic_firewall_term_access(self, filter_node):
        '''
        Set term to set firewall for VLAN traffic acquisition(access port)
        '''

        term_name = "2000_bulk-multicast_be"
        term_node = self._set_vlan_traffic_firewall_term_name(filter_node,
                                                              term_name)
        self._set_vlan_traffic_firewall_term_from(term_node)
        self._set_vlan_traffic_firewall_term_then(
            term_node, forwarding_class="multicast_be", loss_priority="low")

        term_name = "2001_bulk-unicast_be"
        term_node = self._set_vlan_traffic_firewall_term_name(filter_node,
                                                              term_name)
        self._set_vlan_traffic_firewall_term_then(
            term_node, forwarding_class="unicast_be", loss_priority="low")

    @decorater_log
    def _set_vlan_traffic_firewall_term_trunk(self,
                                              conf_node,
                                              cp_info,
                                              if_name,
                                              vlan_id,
                                              device_info,
                                              operation):
        '''
        Set term to set firewall for VLAN traffic acquisition(trunk port)
        '''

        attr, attr_val = self._get_attr_from_operation(operation)
        term_name = "1000_vlan{0}-multicast_be".format(vlan_id)
        node_1 = self._set_vlan_traffic_firewall_term_name(
            conf_node, term_name, attr, attr_val)
        if operation != self._DELETE:
            node_2 = self._set_vlan_traffic_firewall_term_from(node_1)
            self._set_xml_tag(node_2, "user-vlan-id", None, None, vlan_id)
            new_if_name = self._change_change_underbar_name(if_name)
            tmp_count = "count-vlan{0}-{1}".format(vlan_id, new_if_name)
            self._set_vlan_traffic_firewall_term_then(
                node_1, forwarding_class="multicast_be",
                loss_priority="low", count=tmp_count)

        term_name = "1001_vlan{0}-unicast_be".format(vlan_id)
        node_3 = self._set_vlan_traffic_firewall_term_name(
            conf_node, term_name, attr, attr_val)
        if operation != self._DELETE:
            self._set_vlan_traffic_firewall_term_from_vlanid(
                node_3, user_vlan_id=vlan_id, user_vlan_priority_value=1)

            qos_inflow = cp_info.get("QOS", {}).get("INFLOW-SHAPING-RATE")
            speed = cp_info.get("IF-SPEED")
            if_speed = None
            if cp_info.get("IF-TYPE") == self._if_type_lag:
                for lag_if in device_info.get("lag", {}):
                    if if_name == lag_if.get("if_name"):
                        if_speed = \
                            int(lag_if.get("link_speed").strip("g")) * \
                            int(lag_if.get("links"))
                        break
            else:
                if_speed = int(speed.strip("g"))

            flow_val = None
            if qos_inflow:
                flow_val = int(round(float(qos_inflow) *
                                     float(if_speed) * 10.0))
            policer = "{0}m-limit".format(flow_val) if flow_val else None
            self._set_vlan_traffic_firewall_term_then(
                node_3, forwarding_class="unicast_be", loss_priority="low",
                count=tmp_count, policer=policer)

        term_name = "1002_vlan{0}-unicast_af1".format(vlan_id)
        node_4 = self._set_vlan_traffic_firewall_term_name(
            conf_node, term_name, attr, attr_val)
        if operation != self._DELETE:
            self._set_vlan_traffic_firewall_term_from_vlanid(
                node_4, user_vlan_id=vlan_id, user_vlan_priority_value=2)
            self._set_vlan_traffic_firewall_term_then(
                node_4, forwarding_class="unicast_af1", loss_priority="low",
                count=tmp_count)

        term_name = "1003_vlan{0}-unicast_af2".format(vlan_id)
        node_5 = self._set_vlan_traffic_firewall_term_name(
            conf_node, term_name, attr, attr_val)
        if operation != self._DELETE:
            self._set_vlan_traffic_firewall_term_from_vlanid(
                node_5, user_vlan_id=vlan_id, user_vlan_priority_value=3)
            self._set_vlan_traffic_firewall_term_then(
                node_5, forwarding_class="unicast_af2", loss_priority="low",
                count=tmp_count)

        term_name = "1004_vlan{0}-unicast_af3".format(vlan_id)
        node_6 = self._set_vlan_traffic_firewall_term_name(
            conf_node, term_name, attr, attr_val)
        if operation != self._DELETE:
            self._set_vlan_traffic_firewall_term_from_vlanid(
                node_6, user_vlan_id=vlan_id, user_vlan_priority_value=4)
            self._set_vlan_traffic_firewall_term_then(
                node_6, forwarding_class="unicast_af3", loss_priority="low",
                count=tmp_count)

        term_name = "1005_vlan{0}-other".format(vlan_id)
        node_7 = self._set_vlan_traffic_firewall_term_name(
            conf_node, term_name, attr, attr_val)
        if operation != self._DELETE:
            node_8 = self._set_vlan_traffic_firewall_term_from_vlanid(
                node_7, user_vlan_id=vlan_id, user_vlan_priority_value=5)
            self._set_xml_tag(node_8, "user-vlan-1p-priority", None, None, 5)
            self._set_xml_tag(node_8, "user-vlan-1p-priority", None, None, 6)
            self._set_xml_tag(node_8, "user-vlan-1p-priority", None, None, 7)
            self._set_vlan_traffic_firewall_term_then(
                node_7, forwarding_class="unicast_be", loss_priority="low",
                count=tmp_count)

    @decorater_log
    def _set_vlan_traffic_firewall_term_name(self,
                                             filter_node,
                                             term_name,
                                             attr=None,
                                             attr_val=None):
        '''
        Set name of term to set firewall for VLAN traffic acquisition
        '''
        term_node = self._set_xml_tag(filter_node, "term", attr, attr_val)
        self._set_xml_tag(term_node, "name", None, None, term_name)
        return term_node

    @decorater_log
    def _set_vlan_traffic_firewall_term_from(self, conf_node):
        '''
        Set from of term to set firewall for VLAN traffic acquisition
        '''
        node_1 = self._set_xml_tag(conf_node, "from")
        self._set_term_destination_mac_address(node_1, "ff:ff:ff:ff:ff:ff/48")
        self._set_term_destination_mac_address(node_1, "01:00:5e:00:00:00/24")
        self._set_term_destination_mac_address(node_1, "33:33:00:00:00:00/16")
        return node_1

    @decorater_log
    def _set_vlan_traffic_firewall_term_from_vlanid(self, conf_node, **params):
        '''
        Set from of term to set firewall for VLAN traffic acquisition
            params: user_vlan_id
                    user_vlan_priority_value
        '''
        user_vlan_id = params.get("user_vlan_id")
        user_vlan_priority_value = params.get("user_vlan_priority_value", ())

        node_1 = self._set_xml_tag(conf_node, "from")
        self._set_xml_tag(node_1, "user-vlan-id", None, None, user_vlan_id)
        if user_vlan_priority_value:
            self._set_xml_tag(node_1, "user-vlan-1p-priority",
                              None, None, user_vlan_priority_value - 1)
        return node_1

    @decorater_log
    def _set_vlan_traffic_firewall_term_then(self, conf_node, **params):
        '''
        Set then of term to set firewall for VLAN traffic acquisition
            params: forwarding_class
                    loss-priority
                    count
                    policer
        '''
        forwarding_class = params.get("forwarding_class", ())
        loss_priority = params.get("loss_priority", ())
        count = params.get("count", ())
        policer = params.get("policer", ())

        node_1 = self._set_xml_tag(conf_node, "then")
        if forwarding_class:
            self._set_xml_tag(
                node_1, "forwarding-class", None, None, forwarding_class)
        if loss_priority:
            self._set_xml_tag(
                node_1, "loss-priority", None, None, loss_priority)
        if count:
            self._set_xml_tag(node_1, "count", None, None, count)
        if policer:
            self._set_xml_tag(node_1, "policer", None, None, policer)

        return node_1

    @decorater_log
    def _set_term_destination_mac_address(self,
                                          conf_node,
                                          address_str):
        '''
        Set destination-mac-address
        '''
        node_1 = self._set_xml_tag(conf_node, "destination-mac-address")
        self._set_xml_tag(node_1, "mac-address", None, None, address_str)
        return node_1


    @decorater_log
    def _get_device_from_ec(self, device_mes, service=None):
        '''
        Obtain the information of EC message relating to device expansion(Common for spine and leaf)
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
    def _get_ce_lag_from_ec(self,
                            device_mes,
                            service=None,
                            operation=None,
                            db_info=None):
        '''
        Obtain the information of EC message relating to LAG for CE
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
                if not lag_mem.get("name"):
                    raise ValueError(
                        "leaf-interface not enough information ")
                if operation == self._REPLACE:
                    if lag_mem.get("operation")is None:
                        raise ValueError(
                            "leaf-interface not enough information ")
                lag_mem_ifs.append(self._get_lag_mem_if_info(tmp, lag_mem))
        return lag_ifs, lag_mem_ifs

    @decorater_log
    def _get_acl_filter_from_ec(self, device_mes):
        '''
        Obtain the information of EC message relating to ACL configuration.
        '''
        filter_datas = {}
        for filters_ec_mes in device_mes.get("filter", ()):
            term_ec_mes_top = filters_ec_mes.get("term", ())[0]
            is_not_data = bool(not term_ec_mes_top.get("term-name") or
                               term_ec_mes_top.get("name") is None)
            if is_not_data:
                raise ValueError("acl_filter not enough information")
            if_name = term_ec_mes_top.get("name")
            filter_name = "for_{0}".format(
                self._change_change_underbar_name(if_name))
            term_datas = {}
            for term_ec_mes in filters_ec_mes.get("term", ()):
                term_name = term_ec_mes["term-name"]
                term_data = {
                    "IF-NAME": term_ec_mes["name"],
                    "TERM-NAME": term_ec_mes["term-name"],
                }
                if term_ec_mes.get("source-port") is not None:
                    term_data["SOURCE-PORT"] = term_ec_mes["source-port"]
                if term_ec_mes.get("destination-port") is not None:
                    term_data["DESTINATION-PORT"] = (
                        term_ec_mes["destination-port"])
                if term_ec_mes.get("protocol") is not None:
                    term_data["PROTOCOL"] = term_ec_mes["protocol"]
                for key, value in {
                    "source-mac-address": "SOURCE-MAC-ADDR",
                    "destination-mac-address": "DESTINATION-MAC-ADDR",
                    "source-ip-address": "SOURCE-IP-ADDR",
                    "destination-ip-address": "DESTINATION-IP-ADDR",
                }.items():
                    if term_ec_mes.get(key):
                        tmp = self._get_acl_address_info_from_ec(
                            term_ec_mes[key])
                        term_data[value] = tmp
                term_datas[term_name] = term_data
            filter_data = {
                "FILTER-NAME": filter_name,
                "TERM": term_datas,
            }
            filter_datas[filter_name] = filter_data
        return filter_datas

    @decorater_log
    def _get_acl_address_info_from_ec(self, address_info):
        '''
        Obtain ACL configuration transmit destination mac address information from EC message
        '''

        address = address_info.get("address")
        prefix = address_info.get("prefix")
        cidr_str = "{0}/{1}".format(address, prefix)
        ip_version = address_info.get("ip_version")
        tmp = {
            "ADDRESS": address,
            "PREFIX": prefix,
            "CIDR": cidr_str,
        }
        if ip_version is not None:
            tmp["IP_VERSION"] = ip_version
        return tmp

    @decorater_log
    def _get_lag_if_info(self, if_info):
        '''
       Obtain EC message from LAG information
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
        Obtain the information of LAG member from EC message
        '''
        tmp = {"IF-NAME": lag_mem_if.get("name"),
               "LAG-IF-NAME": lag_if["name"],
               "OPERATION": lag_mem_if.get("operation"), }
        return tmp

    @decorater_log
    def _get_internal_link_from_ec(self,
                                   device_mes,
                                   service=None,
                                   operation=None,
                                   db_info=None):
        '''
        Obtain the information of EC message relating to Internal Link (LAG)
        '''
        phy_ifs = []

        for tmp in device_mes.get("internal-physical", ()):
            if (not tmp.get("name") or
                not tmp.get("address") or
                    tmp.get("prefix") is None):
                raise ValueError("internal-physical not enough information")

            phy_ifs.append(
                self._get_internal_if_info(tmp, self._if_type_phy))

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
                self._get_internal_if_info(tmp, self._if_type_lag))

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
        Obtain the EC message/ DB information relating to Internal Link for deletion (LAG)
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
        Obtain the EC message/ DB information relating to Internal Link for deletion (LAG)
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
                              if_type=None):
        '''
        Obtain the information of Internal Link from EC message(Regardless of physical or LAG)
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
        Obtain the information of Internal Link from EC message(Regardless of physical or LAG)
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
        Obtain the applicable Internal Link Information (DB)
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
        Obtain the information of Internal Link from EC message(Regardless of physical or LAG)
        '''
        internal_link_db = self._get_internal_link_db(db_info,
                                                      if_info.get("name"))
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
        Obtain EC message and DB information on IF open/close. 
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
        Obtain IF inforation from EC message(Regardless of physical or LAG)
        '''
        tmp = {
            "IF-NAME": if_info.get("name"),
            "CONDITION": if_info.get("condition"),
        }
        return tmp


    @decorater_log
    def _get_cp_interface_info_from_ec(self,
                                       cp_dicts,
                                       cp_info,
                                       db_info,
                                       slice_name):
        '''
        Collect IF information related to slice from EC message(Each unit of CP).
        '''
        if_name = cp_info.get("name")
        vlan_id = cp_info.get("vlan-id")
        operation = cp_info.get("operation")
        cp_irb_vlan_id_list = self._get_db_irb_cp(db_info, slice_name)
        is_irb = False
        if not if_name or vlan_id is None:
            raise ValueError("CP is not enough information")
        if if_name not in cp_dicts:
            if (operation == self._DELETE and
                    vlan_id in cp_irb_vlan_id_list) or (cp_info.get("irb")):
                is_irb = True
            tmp = {
                "IF-TYPE": (self._if_type_lag
                            if self._lag_check.search(if_name)
                            else self._if_type_phy),
                "IF-NAME": if_name,
                "IF-IS-VLAN":  bool(vlan_id),
                "IS-IRB": bool(is_irb),
                "OPERATION": None,
                "VLAN":  {},
                "IF-SPEED": cp_info.get("speed")
            }

            if cp_info.get("qos"):
                tmp["QOS"] = self._get_cp_qos_info_from_ec(cp_info, db_info)

            if cp_info.get("irb"):
                tmp["IRB"] = self._get_cp_irb_info_from_ec(cp_info, db_info)

            cp_dicts[if_name] = tmp
        else:
            tmp = cp_dicts[if_name]
        return tmp, vlan_id

    @decorater_log
    def _get_dummy_cp_interface_info_from_ec(self,
                                             cp_dicts, cp_info,
                                             dummy_cp_info,
                                             db_info):
        '''
        Collect IF information related to slide from EC message (Each unit of dummyCP)
        '''
        vlan_id = dummy_cp_info.get("vlan-id")
        operation = dummy_cp_info.get("operation")
        if vlan_id is None:
            raise ValueError("dummy CP is not enough information")

        if vlan_id not in cp_dicts:
            tmp = {
                "IS-DUMMY": True,
                "CE-IF-VLAN-ID": vlan_id,
                "OPERATION": operation,
                "VLAN":  {},
            }
            if (dummy_cp_info.get("irb") or operation == self._DELETE):
                tmp["IS-IRB"] = True
                if dummy_cp_info.get("irb"):
                    tmp["IRB"] = self._get_cp_irb_info_from_ec(dummy_cp_info,
                                                               db_info)
                if cp_info is not None:
                    for cp in cp_info:
                        if cp.get("vlan_id") == vlan_id and (
                                dummy_cp_info.get("irb")):
                            tmp["IRB"] = self._get_cp_irb_info_from_ec(cp,
                                                                       db_info)

            cp_dicts[vlan_id] = tmp

        return tmp, vlan_id


    @decorater_log
    def _get_l2_cps_from_ec(self,
                            device_mes,
                            db_info,
                            slice_name=None,
                            operation=None):
        '''
        Parameter from EC(Obtain cp data and dummy_cp data from cp)
        '''
        device_mes_cps = None
        cp_dicts = {}
        dummy_cp_dicts = {}
        if device_mes.get("cp"):
            device_mes_cps = device_mes.get("cp")
            self._get_cps_from_ec(
                cp_dicts, device_mes_cps, db_info, slice_name, operation)
        if device_mes.get("dummy_cp"):
            device_mes_dummy_cps = device_mes.get("dummy_cp")
            self._get_dummy_cps_from_ec(
                dummy_cp_dicts, device_mes_cps, device_mes_dummy_cps, db_info,
                slice_name, operation)

        return cp_dicts, dummy_cp_dicts

    @decorater_log
    def _get_cps_from_ec(self,
                         cp_dicts,
                         device_mes_cps,
                         db_info,
                         slice_name=None,
                         operation=None):
        '''
        Parameter from EC(Obtain cp data from cp)
        '''
        for tmp_cp in device_mes_cps:
            tmp, vlan_id = self._get_cp_interface_info_from_ec(cp_dicts,
                                                               tmp_cp,
                                                               db_info,
                                                               slice_name)
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
                clag_id = tmp_cp.get("clag-id")
                if clag_id is None:
                    db_cp = self._get_vlan_if_from_db(db_info,
                                                      if_name,
                                                      slice_name,
                                                      vlan_id,
                                                      "cp")
                    clag_id = db_cp.get("clag-id")
                if not (esi and system_id and clag_id):
                    raise ValueError("EVPN ESI data is enough data")
                tmp["EVPN-MULTI"] = {
                    "OPERATION": cp_ope,
                    "IF-ESI": esi,
                    "IF-SYSTEM-ID": system_id,
                    "IF-CLAG-ID": int(clag_id),
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
                        "IF-SYSTEM-ID": db_cp.get("system-id"),
                        "IF-CLAG-ID": db_cp.get("clag-id")}
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
    def _get_dummy_cps_from_ec(self,
                               cp_dicts,
                               device_mes_cps,
                               device_mes_dummy_cps,
                               db_info,
                               slice_name=None,
                               operation=None):
        '''
        Parameter from EC(Obtain dummy_cp data from cp)
        '''
        for tmp_cp in device_mes_dummy_cps:
            tmp, vlan_id = self._get_dummy_cp_interface_info_from_ec(
                cp_dicts, device_mes_cps, tmp_cp, db_info)

            if tmp.get("OPERATION") != self._REPLACE:
                tmp["VLAN"][vlan_id] = self._get_l2_vlan_if_info_from_ec(
                    tmp_cp, db_info, slice_name, is_dummy=True)

        return cp_dicts

    @decorater_log
    def _get_l2_vlan_if_info_from_ec(self,
                                     ec_cp,
                                     db_info,
                                     slice_name=None,
                                     is_dummy=False):
        '''
        Set the section related to VLAN of CP
        '''
        if_name = None
        db_name = "cp"
        if not is_dummy:
            if_name = ec_cp.get("name")
        else:
            db_name = "dummy_cp"
        vlan_id = ec_cp.get("vlan-id")
        operation = ec_cp.get("operation")
        if operation == self._DELETE:
            db_cp = self._get_vlan_if_from_db(db_info,
                                              if_name,
                                              slice_name,
                                              vlan_id,
                                              db_name,
                                              is_dummy=is_dummy)
            vni = db_cp.get("vni")
        else:
            vni = ec_cp.get("vni")
        return {
            "OPERATION": ec_cp.get("operation"),
            "CE-IF-VLAN-ID": ec_cp.get("vlan-id"),
            "VNI": vni,
        }

    @decorater_log
    def _get_vlans_list(self,
                        cp_dict,
                        dummy_cp_dict,
                        db_info,
                        slice_name=None,
                        operation=None):
        '''
       Create list for vlans
        (Make judgment on the necessity of IF deletion and possibility for slice to remain inside device.)
        '''
        cos_if_list = {}
        is_vlans_del = False

        db_vlan = self._get_db_vlan_id_counts(db_info)
        ec_vlan = self._get_ec_vlan_counts(cp_dict.copy())
        ec_dummy_vlan = self._get_ec_dummy_vlan_counts(dummy_cp_dict.copy())

        if operation == self._DELETE:
            for vlan_id, vlan in ec_vlan.items():
                if ec_dummy_vlan.get(vlan_id) is None:
                    if vlan["count"] == db_vlan.get(vlan_id, 0):
                        cos_if_list[vlan_id] = ec_vlan.get("VNI")
                else:
                    del_vlan_num = vlan["count"] - \
                        ec_dummy_vlan.get(vlan_id, {}).get("count")
                    if del_vlan_num == db_vlan.get(vlan_id, 0):
                        cos_if_list[vlan_id] = ec_vlan.get("VNI")

            if len(cos_if_list) == len(db_vlan):
                is_vlans_del = True
        else:
            for vlan_id in ec_vlan.keys():
                if vlan_id not in db_vlan:
                    cos_if_list[vlan_id] = ec_vlan[vlan_id].get("VNI")
            for vlan_id in ec_dummy_vlan.keys():
                if ((vlan_id not in db_vlan) and
                        (cos_if_list.get(vlan_id) is None)):
                    cos_if_list[vlan_id] = ec_dummy_vlan[vlan_id].get("VNI")

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

    def _get_db_vlan_id_counts(self, db_info):
        db_vlan = {}
        db_cp = db_info.get("cp", ())
        db_dummy_cp = db_info.get("dummy_cp", ())
        for tmp_cp in db_cp:
            vlan = tmp_cp.get("vlan", {}).get("vlan_id")
            if vlan in db_vlan:
                db_vlan[vlan] += 1
            else:
                db_vlan[vlan] = 1
        for tmp_cp in db_dummy_cp:
            vlan = tmp_cp.get("vlan", {}).get("vlan_id")
            if vlan in db_vlan:
                db_vlan[vlan] += 1
            else:
                db_vlan[vlan] = 1
        return db_vlan

    @decorater_log
    def _check_slice_vrf_from_ec(self,
                                 device_mes):
        '''
        Parameter from EC(Judge whether vrf information exists or not)
        '''
        device_mes_vrf = False
        delete_vlan_list = []
        delete_vlan = []

        if device_mes.get("vrf"):
            device_mes_vrf = True

        for tmp_cp in device_mes.get("cp", {}):
            if tmp_cp.get("operation") == self._DELETE:
                delete_vlan_list.append(tmp_cp.get("vlan-id"))
        for tmp_cp in device_mes.get("dummy_cp", {}):
            if tmp_cp.get("operation") == self._DELETE:
                delete_vlan_list.append(tmp_cp.get("vlan-id"))

        for vlan_id in delete_vlan_list:
            if vlan_id not in delete_vlan:
                delete_vlan.append(vlan_id)

        return device_mes_vrf, delete_vlan

    @decorater_log
    def _check_slice_vrf_from_ec_del(self,
                                     device_mes,
                                     db_info):
        '''
        Parameter from EC(Judge whether vrf information exists or not)
        '''
        delete_vlan_list = []
        delete_vlan = []
        chg_dummy_vlan = []
        new_vlan = []
        db_vlan = {}
        delete_vlan_count_list = {}
        virtual_gateway_address_list = {}
        for tmp_cp in device_mes.get("cp", {}):
            if tmp_cp.get("operation") == self._DELETE and \
                    tmp_cp.get("esi") is None:
                vlan_id = tmp_cp.get("vlan-id")
                delete_vlan_list.append(vlan_id)
                if delete_vlan_count_list.get(vlan_id) is None:
                    tmp = {"count": 1}
                    delete_vlan_count_list[vlan_id] = tmp
                else:
                    delete_vlan_count_list[vlan_id]["count"] += 1

        for tmp_cp in device_mes.get("dummy_cp", {}):
            if tmp_cp.get("operation") == self._DELETE:
                vlan_id = tmp_cp.get("vlan-id")
                delete_vlan_list.append(vlan_id)
                if delete_vlan_count_list.get(vlan_id) is None:
                    tmp = {"count": 1}
                    delete_vlan_count_list[vlan_id] = tmp
                else:
                    delete_vlan_count_list[vlan_id]["count"] += 1
            else:
                chg_dummy_vlan.append(tmp_cp.get("vlan-id"))

        for vlan_if in db_info.get("cp", ()):
            db_vlan_id = (vlan_if.get("vlan", {}).get("vlan_id"))
            if db_vlan.get(db_vlan_id) is None:
                db_cp = {"count": 1}
                db_vlan[db_vlan_id] = db_cp
            else:
                db_vlan[db_vlan_id]["count"] += 1

            virtual_gateway_address_list[db_vlan_id] = \
                vlan_if.get("virtual_gateway_address")

        for vlan_if in db_info.get("dummy_cp", ()):
            db_vlan_id = (vlan_if.get("vlan", {}).get("vlan_id"))
            if db_vlan.get(db_vlan_id) is None:
                db_cp = {"count": 1}
                db_vlan[db_vlan_id] = db_cp
            else:
                db_vlan[db_vlan_id]["count"] += 1

        for vlan_id in delete_vlan_list:
            if vlan_id not in delete_vlan:
                delete_vlan.append(vlan_id)

        tmp_new_vlan = set(delete_vlan) - set(chg_dummy_vlan)

        for chk_del_vlan in tmp_new_vlan:
            if (db_vlan.get(chk_del_vlan) is not None) and \
                    db_vlan.get(chk_del_vlan).get("count") == \
                    delete_vlan_count_list.get(chk_del_vlan).get("count"):
                new_vlan.append(chk_del_vlan)

        return chg_dummy_vlan, new_vlan, virtual_gateway_address_list

    @decorater_log
    def _check_slice_vrf_from_ec_dict(self,
                                      device_mes):
        '''
        Parameter from EC(Judge whether vrf information exists or not)
        '''
        vlan_list = []

        if_list = []
        if_dict = {}
        vlan_id = None

        for tmp_cp in device_mes.get("dummy_cp", {}):
            if tmp_cp.get("operation") == "merge":
                vlan_id = tmp_cp.get("vlan-id")
                vlan_list.append(vlan_id)

        for tmp_cp in device_mes.get("cp", {}):
            if tmp_cp.get("operation") == self._DELETE:
                if (tmp_cp.get("vlan-id")) in vlan_list:
                    if_list.append(tmp_cp.get("name"))
                    tmp_cp.get
        if vlan_id is not None:
            if_dict[vlan_id] = if_list
        return if_dict

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
                      dummy_cp_dict,
                      db_info,
                      slice_name=None,
                      operation=None):
        '''
        Create list for vni
        '''
        vni_list = []
        db_vni = self._get_db_vni_counts(db_info)
        ec_vni = self._get_ec_vni_counts(cp_dict.copy())
        ec_dummy_vni = self._get_ec_dummy_vni_counts(dummy_cp_dict.copy())

        if operation == self._DELETE:
            for vni in ec_vni.keys():
                if ec_dummy_vni.get(vni) is None:
                    if ec_vni[vni] == db_vni.get(vni, 0):
                        vni_list.append(vni)
                else:
                    del_vni_num = ec_vni.get(vni) - ec_dummy_vni.get(vni)
                    if del_vni_num == db_vni.get(vni, 0):
                        vni_list.append(vni)
            for vni in ec_dummy_vni.keys():
                if ec_vni.get(vni) is not None:
                    tmp = ec_vni.get(vni)
                else:
                    tmp = 0
                del_vni_num = tmp - ec_dummy_vni.get(vni)
                if ((vni not in vni_list) and
                        (del_vni_num == db_vni.get(vni, 0))):
                    vni_list.append(vni)
        else:
            for vni in ec_vni.keys():
                if vni not in db_vni:
                    vni_list.append(vni)
            for vni in ec_dummy_vni.keys():
                if (vni not in db_vni) and (vni not in vni_list):
                    vni_list.append(vni)

        return vni_list

    @decorater_log
    def _get_db_vni_counts(self, db_info):
        db_vni = {}
        db_cp = db_info.get("cp", ())
        db_dummy_cp = db_info.get("dummy_cp", ())
        for tmp_cp in db_cp:
            vni = tmp_cp.get("vni")
            if vni in db_vni:
                db_vni[vni] += 1
            else:
                db_vni[vni] = 1
        for tmp_cp in db_dummy_cp:
            vni = int(tmp_cp.get("vni"))
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
    def _get_vrf_from_ec(self, device_mes, device_info=None, slice_name=None):
        vrf_mes = device_mes.get("vrf", {})
        tmp = {}
        is_db_vrf = bool(
            self._get_vrf_name_from_db(device_info, slice_name)[0])
        if vrf_mes:
            tmp = {
                "VRF-NAME": vrf_mes.get("vrf-name"),
                "VRF-ID": vrf_mes.get("vrf-id"),
                "VRF-RT": vrf_mes.get("rt"),
                "VRF-RD": vrf_mes.get("rd"),
                "VRF-ROUTER-ID": vrf_mes.get("router-id"),
            }
            if vrf_mes.get("loopback"):
                lp_addr = vrf_mes.get("loopback")
                tmp["VRF-LB-ADDR"] = lp_addr.get("address")
                tmp["VRF-LB-PREFIX"] = int(lp_addr.get("prefix"))

            tmp["IS-CONFIGURED"] = is_db_vrf
        return tmp

    @staticmethod
    @decorater_log
    def _get_vlan_if_from_db(db_info,
                             if_name,
                             slice_name,
                             vlan_id,
                             db_name,
                             is_dummy=False):
        '''
        Obtain VLAN_IF from DB(cp, vrf, bgp, vrrp)
        '''
        rtn_vlan_if = {}
        for vlan_if in db_info.get(db_name, ()):
            db_if_name = None
            if not is_dummy:
                db_if_name = vlan_if.get("if_name")
            db_slice_name = vlan_if.get("slice_name")
            db_vlan_id = (vlan_if.get("vlan", {}).get("vlan_id")
                          if (db_name == "cp" or db_name == "dummy_cp")
                          else vlan_if.get("vlan_id"))
            if (if_name == db_if_name and
                    slice_name == db_slice_name and
                    vlan_id == db_vlan_id):
                rtn_vlan_if = vlan_if
                break
        return rtn_vlan_if

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
        Obtain combination of IF name and vlan from DB.
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
    def _get_if_filter_data_list(self, cp_info, cos_if_list, device_info):
        '''
        Obtain IF to be set to filter
        '''
        filter_if_name = []
        filter_info = {}
        for cos_if in cos_if_list if cos_if_list else ():
            filter_if_name.append(cos_if["IF-NAME"])
        for if_name, cp_data in cp_info.items():
            if if_name in filter_if_name:
                if not (cp_data["OPERATION"] == self._DELETE and
                        self._check_acl_exist_db(if_name, device_info)):
                    filter_info[if_name] = copy.deepcopy(cp_data)
                    filter_info[if_name]["IS-FILTER"] = True
            elif cp_data.get("IF-PORT-MODE") == self._PORT_MODE_TRUNK:
                filter_info[if_name] = copy.deepcopy(cp_data)
        return filter_info

    @decorater_log
    def _get_db_irb_cp(self, db_info, slice_name):
        '''
        Obtain vlan-id list of CP with IRB from DB.
        '''
        db_cp = db_info.get("cp", ())
        vlan_id_list = []
        for tmp_cp in db_cp:
            if not tmp_cp.get("slice_name") == slice_name:
                continue
            if tmp_cp.get("irb_ipv4_address"):
                vlan_id_db = tmp_cp.get("vlan", {}).get("vlan_id")
                vlan_id_list.append(vlan_id_db)

        return vlan_id_list

    @decorater_log
    def _get_db_cp(self, db_info, device_name):
        '''
        Obtain list of vlan-id of CP from DB
        '''
        db_cp = db_info.get("cp", ())
        vlan_id_list = []
        for tmp_cp in db_cp:
            if not tmp_cp.get("device_name") == device_name:
                continue
            vlan_id_db = tmp_cp.get("vlan", {}).get("vlan_id")
            vlan_id_list.append(vlan_id_db)

        return vlan_id_list

    @decorater_log
    def _get_db_cp_same_slice(self, db_info, slice_name):
        '''
        Obtain CP vlan-id list  from DB.
        '''
        db_cp = db_info.get("cp", ())
        vlan_id_list = []
        for tmp_cp in db_cp:
            if not tmp_cp.get("slice_name") == slice_name:
                continue
            vlan_id_db = tmp_cp.get("vlan", {}).get("vlan_id")
            vlan_id_list.append(vlan_id_db)

        return vlan_id_list

    @decorater_log
    def _get_db_dummy_cp(self, db_info, slice_name):
        '''
        Obtain list of vlan-id of dummy_cp from DB
        '''
        db_cp = db_info.get("dummy_cp", ())
        vlan_id_list = []
        for tmp_cp in db_cp:
            if not tmp_cp.get("slice_name") == slice_name:
                continue
            vlan_id_db = tmp_cp.get("vlan", {}).get("vlan_id")
            vlan_id_list.append(vlan_id_db)

        return vlan_id_list

    @decorater_log
    def _get_db_dummy_cp_device(self, db_info, device_name):
        '''
        Obtain list of vlan-id of dummy_cp from DB
        '''
        db_cp = db_info.get("dummy_cp", ())
        vlan_id_list = []
        for tmp_cp in db_cp:
            if not tmp_cp.get("device_name") == device_name:
                continue
            vlan_id_db = tmp_cp.get("vlan", {}).get("vlan_id")
            vlan_id_list.append(vlan_id_db)

        return vlan_id_list

    @decorater_log
    def _get_vrf_name_from_db(self, db_info, slice_name):
        '''
        Obtain VRF name based on slide name from DB
        '''
        vrf_name = None
        vrf_id = None
        vrf_data_tables = ("vrf_detail", "dummy_cp")

        for db_table_name in vrf_data_tables:
            tmp_vrf_data = db_info.get(db_table_name, ())
            for tmp_data in tmp_vrf_data:
                if tmp_data.get("slice_name") == slice_name:
                    tmp_vrf = (tmp_data.get("vrf", {})
                               if db_table_name == "dummy_cp" else tmp_data)
                    vrf_name = tmp_vrf.get("vrf_name")
                    vrf_id = tmp_vrf.get("vrf_id")
                    break

        return vrf_name, vrf_id

    @decorater_log
    def _check_new_cp_add(self, device_info, device_name, irb_cps):
        '''
        Judge whether or not there is vlan_id to be added.
        '''
        db_cp = self._get_db_cp(device_info, device_name)
        vlan_list = []
        for tmp_cp in irb_cps:
            if tmp_cp.get("VLAN"):
                for vlan_id, unit in tmp_cp.get("VLAN").items():
                    if not (vlan_id in db_cp):
                        vlan_list.append(vlan_id)

        return vlan_list

    @decorater_log
    def _check_slice_del(self, irb_cps=[]):
        '''
        Judge whether CP is to be deleted or not.
        '''
        for if_info in irb_cps:
            for vlan_info in if_info.get("VLAN", {}).values():
                if vlan_info.get("OPERATION") == self._DELETE:
                    return True
        return False

    @decorater_log
    def _check_slice_all_cp_del(self,
                                irb_cps,
                                device_info,
                                device_name,
                                slice_name,
                                cp_info,
                                dummy_cp_info):
        '''
        Judge whether CP is to be deleted or not.
        '''
        del_cp_count = 0
        for irb_cp in irb_cps:
            if irb_cp.get("OPERATION") == self._DELETE:
                del_cp_count = del_cp_count + 1
            else:
                del_cp_count = del_cp_count - 1

        db_ifs = self._get_db_irb_cp(device_info, slice_name)
        db_dummy_cp = self._get_db_dummy_cp(device_info, slice_name)
        db_cp_count = len(db_ifs) + len(db_dummy_cp)
        return bool(del_cp_count == db_cp_count)

    @decorater_log
    def _check_slice_all_vlans_del(self,
                                   device_info,
                                   slice_name,
                                   cp_info,
                                   dummy_cp_info):
        '''
        Judge VLAN-deletion.
        * all of vlans deletion process does not run in case other slice exists
          Restrict slice  for CP to be deleted in order to refine scope of processing.
        Parameter:
            device_info   : DB information
            slice_name    : slice name
            cp_info       : CP information(EC message)
            dummy_cp_info : dummy CP information(EC message)
        '''
        del_cp_count = 0
        for cp_unit in cp_info.values():
            if cp_unit.get("OPERATION") == self._DELETE:
                del_cp_count = del_cp_count + 1
            else:
                del_cp_count = del_cp_count - 1

        for cp_unit in dummy_cp_info.values():
            if cp_unit.get("OPERATION") == self._DELETE:
                del_cp_count = del_cp_count + 1
            else:
                del_cp_count = del_cp_count - 1

        db_vlans = self._get_db_cp_same_slice(device_info, slice_name)
        db_dummy_cp = self._get_db_dummy_cp(device_info, slice_name)
        db_cp_count = len(db_vlans) + len(db_dummy_cp)
        return bool(del_cp_count == db_cp_count)

    @decorater_log
    def _check_slice_irb_from_ec(self, cps_info, dummy_cp_infos):
        '''
        Return CP informatioin corresponding to IRB inside of EC message
        '''
        irb_cps = []
        for tmp_cp in cps_info.values():
            if tmp_cp.get("IS-IRB"):
                irb_cps.append(tmp_cp)
        for tmp_dummy_cp in dummy_cp_infos.values():
            if tmp_dummy_cp.get("IS-IRB"):
                irb_cps.append(tmp_dummy_cp)

        return irb_cps

    @decorater_log
    def _check_irb_interface(self, db_info, cp_info,
                             dummy_cp_info, slice_name, operation):
        '''
        Confirm whether CP information with IRB and vlan_id of dummy_vlan in EC message
        are registered in DB.
        Return vlan_id which are not registered in DB.
        '''
        irb_cps = []
        irb_dummy_cp = []
        new_cp_list = []
        param_list = []
        vlan_list = []
        cps_list = []
        db_vlan_list = []
        del_vlan_num_dict = {}
        db_vlan_num_dict = {}
        check_param = "vlan_id"

        for tmp_cp in cp_info.values():
            if tmp_cp.get("IS-IRB"):
                irb_cps.append(tmp_cp)
        for tmp_cp_irb in irb_cps:
            vlans = tmp_cp_irb.get("VLAN")
            for vlan_id in vlans:
                new_cp_list.append(vlan_id)
                if vlans.get(vlan_id).get("OPERATION") == self._DELETE and \
                        operation == self._DELETE:
                    if del_vlan_num_dict.get(vlan_id) is None:
                        del_vlan_num_dict[vlan_id] = 1
                    else:
                        del_vlan_num_dict[vlan_id] += 1

        for tmp_cp in dummy_cp_info.values():
            if tmp_cp.get("IS-IRB"):
                irb_dummy_cp.append(tmp_cp)
        for tmp_dummy_cp in irb_dummy_cp:
            vlans = tmp_dummy_cp.get("VLAN")
            for vlan_id in vlans:
                new_cp_list.append(vlan_id)
                if operation == self._DELETE:
                    if vlans.get(vlan_id).get("OPERATION") != self._DELETE:
                        if del_vlan_num_dict.get(vlan_id) is None:
                            del_vlan_num_dict[vlan_id] = -1
                        else:
                            del_vlan_num_dict[vlan_id] -= 1
                    else:
                        if del_vlan_num_dict.get(vlan_id) is None:
                            del_vlan_num_dict[vlan_id] = 1
                        else:
                            del_vlan_num_dict[vlan_id] += 1

        for vlan_id in new_cp_list:
            if vlan_id not in vlan_list:
                vlan_list.append(vlan_id)

        db_name = "cp"
        self._get_param_list(db_info, db_name, check_param,
                             param_list, slice_name, db_vlan_num_dict)
        db_name = "dummy_cp"
        self._get_param_list(db_info, db_name, check_param,
                             param_list, slice_name, db_vlan_num_dict)

        for vlan_id in param_list:
            if vlan_id not in db_vlan_list:
                db_vlan_list.append(vlan_id)

        if operation != self._DELETE:
            cps_list = set(vlan_list) - set(db_vlan_list)
        else:
            for vlan_id in vlan_list:
                if del_vlan_num_dict.get(vlan_id, 0) > 0 and \
                        del_vlan_num_dict.get(vlan_id) == (
                            db_vlan_num_dict.get(vlan_id)):
                    cps_list.append(vlan_id)

        return cps_list

    def _check_irb_interface_duplication(self,
                                         db_info,
                                         cp_info,
                                         dummy_cp_info):
        '''
        Check whether IRB supported CP information inside of EC message 
        and vlan_id of dummy_vlan have been registered in db, 
        and return vlan_id which has not been registered in DB.
        '''
        irb_cps = []
        irb_dummy_cp = []
        new_cp_list = []
        vlan_list = []
        check_param = "vlan_id"

        for tmp_cp in cp_info.values():
            if tmp_cp.get("IS-IRB") and tmp_cp.get("OPERATION") == "delete":
                irb_cps.append(tmp_cp)
        for tmp_cp_irb in irb_cps:
            vlans = tmp_cp_irb.get("VLAN")
            for vlan_id in vlans:
                new_cp_list.append(vlan_id)

        for tmp_cp in dummy_cp_info.values():
            if tmp_cp.get("IS-IRB") and tmp_cp.get("OPERATION") == "delete":
                irb_dummy_cp.append(tmp_cp)
        for tmp_dummy_cp in irb_dummy_cp:
            vlans = tmp_dummy_cp.get("VLAN")
            for vlan_id in vlans:
                new_cp_list.append(vlan_id)

        for vlan_id in new_cp_list:
            if vlan_id not in vlan_list:
                vlan_list.append(vlan_id)

        return vlan_list

    @decorater_log
    def _get_param_list(self, db_info, db_name, check_param, param_list,
                        slice_name, db_vlan_num_dict):
        data = db_info.get(db_name, ())
        for tmp_data in data:
            if tmp_data.get("slice_name") == slice_name:
                vlan_id = tmp_data.get("vlan").get(check_param)
                param_list.append(vlan_id)
                if db_vlan_num_dict.get(vlan_id) is None:
                    db_vlan_num_dict[vlan_id] = 1
                else:
                    db_vlan_num_dict[vlan_id] += 1

    @decorater_log
    def _check_acl_exist_db(self, if_name, db_info):
        '''
        Check if the applicable IF exists in ACL configuration inside the DB.
        '''
        result = False
        acl_infos = db_info.get("acl_info", ())
        for acl_info in acl_infos:
            if acl_info.get("if_name") == if_name:
                result = True
        return result


    @decorater_log
    def _gen_leaf_fix_message(self, xml_obj, operation):
        '''
        Fixed value to create message (Leaf) for Netconf
            Called out when creating message for Leaf.
        Parameter:
            xml_obj : xml object
            operation : Designate "delete" when deleting
        Return value
            Creation result : Boolean (Write properly using override method)
        '''
        return True

    @decorater_log
    def _gen_l2_slice_fix_message(self, xml_obj, operation):
        '''
        Fixed value to create message (L2Slice) for Netconf.
            Called out when creating message for L2Slice
        Parameter:
            xml_obj : xml object
            operation : Designate "delete" when deleting
        Return value
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
    def _gen_acl_filter_fix_message(self, xml_obj, operation):
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
            dev_reg_info = self._get_device_from_ec(device_mes,
                                                    service=self.name_leaf)
            tmp_dev, l3v_lbb_infos = self._get_leaf_vpn_from_ec(device_mes)
            dev_reg_info.update(tmp_dev)
            phy_ifs, lag_ifs, lag_mem_ifs, inner_ifs = \
                self._get_internal_link_from_ec(device_mes,
                                                service=self.name_leaf)
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
            lag_ifs, device_info, operation=operation)
        self._set_chassis_device_count(conf_node, device_count)

        if_node = self._set_interfaces_node(conf_node)
        self._set_interface_inner_links(if_node,
                                        lag_mem_ifs=lag_mem_ifs,
                                        lag_ifs=lag_ifs,
                                        phy_ifs=phy_ifs,
                                        vpn_type=dev_reg_info["VPN-TYPE"])
        self._set_interface_loopback(if_node,
                                     0,
                                     dev_reg_info["LB-IF-ADDR"],
                                     dev_reg_info["LB-IF-PREFIX"])

        self._set_device_routing_options(conf_node,
                                         dev_reg_info["LB-IF-ADDR"],
                                         dev_reg_info["VPN-TYPE"],
                                         dev_reg_info["AS-NUMBER"])

        protocols_node = self._set_device_protocols(conf_node)

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
            device_info : Device information
            operation : Designate "delete" when deleting
        Return value
            Creation result : Boolean (Write properly using override method)
        '''
        if (not ec_message.get("device-leaf", {}).get("cp") and
                not ec_message.get("device-leaf", {}).get("dummy_cp")):

            return False
        if operation == self._REPLACE:
            return self._gen_l2_slice_replace_message(xml_obj,
                                                      device_info,
                                                      ec_message,
                                                      operation)
        device_mes = ec_message.get("device-leaf", {})
        device_name = device_mes.get("name")
        slice_name = device_mes.get("slice_name")

        irb_cps_del = {}
        del_vlan_list = {}
        chg_dummy_vlan = {}
        new_vlan_list = {}
        chg_dummy_if_list = {}
        virtual_gateway_address_list = {}
        is_other_slice = False

        try:
            if len(device_mes.get("cp", {})) > 0:
                tmp_operation = self._MERGE
                for tmp_cp in device_mes.get("cp", {}):
                    if tmp_cp.get("operation") == self._DELETE:
                        tmp_operation = self._DELETE
                        break
                operation = tmp_operation

            cp_info, dummy_cp_info = self._get_l2_cps_from_ec(device_mes,
                                                              device_info,
                                                              slice_name)

            irb_cps = self._check_slice_irb_from_ec(cp_info,
                                                    dummy_cp_info)

            if operation == self._DELETE:
                irb_cps_del, del_vlan_list = (
                    self._check_slice_vrf_from_ec(device_mes))

                chg_dummy_vlan, new_vlan_list, virtual_gateway_address_list = (
                    self._check_slice_vrf_from_ec_del(device_mes, device_info))

                chg_dummy_if_list = (
                    self._check_slice_vrf_from_ec_dict(device_mes))

                is_other_slice = self._check_other_slice(slice_name,
                                                         device_info)

            vrf_name = None
            vrf_id = None
            if irb_cps:
                if device_mes.get("vrf"):
                    vrf_name = device_mes["vrf"]["vrf-name"]
                    vrf_id = device_mes["vrf"]["vrf-id"]
                else:
                    vrf_name, vrf_id = self._get_vrf_name_from_db(
                        device_info, slice_name)
                    if not vrf_name or not vrf_id:
                        raise ValueError(
                            "getting vrf_name or vrf_id from DB is None \
                            (or not fount)")

            vrf = self._get_vrf_from_ec(device_mes, device_info, slice_name)

            vlans_info, is_del_vlans = self._get_vlans_list(
                cp_info,
                dummy_cp_info,
                device_info,
                slice_name=slice_name,
                operation=operation)

            vni_list = self._get_vni_list(cp_info,
                                          dummy_cp_info,
                                          device_info,
                                          slice_name=slice_name,
                                          operation=operation)

            cos_ifs = self._get_cos_if_list(cp_info,
                                            device_info,
                                            slice_name=slice_name,
                                            operation=operation)

            if_filters = self._get_if_filter_data_list(cp_info,
                                                       cos_ifs,
                                                       device_info)

            is_all_del = self._check_slice_all_cp_del(irb_cps,
                                                      device_info,
                                                      device_name,
                                                      slice_name,
                                                      cp_info,
                                                      dummy_cp_info)
            is_vlans_all_del = self._check_slice_all_vlans_del(device_info,
                                                               slice_name,
                                                               cp_info,
                                                               dummy_cp_info)

            vrf_cps = self._check_irb_interface(
                device_info, cp_info, dummy_cp_info, slice_name, operation)

            dummy_list = self._get_db_dummy_cp_device(
                device_info, device_name)

            vlan_list = self._check_new_cp_add(
                device_info, device_name, irb_cps)

            check_vrf_name, check_vrf_id = self._get_vrf_name_from_db(
                device_info, slice_name)

            if check_vrf_name is None and check_vrf_id is None:
                is_loop_del = True
            else:
                is_loop_del = False
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

        tmp = "Setting L2 VLAN IF"
        tmp += "\nCP={0},\nDummyCP={1},".format(cp_info, dummy_cp_info)
        tmp += "\nIRBCP={0},\nVRF={1},".format(irb_cps, vrf)
        tmp += "\nVLANS={0},\nVNIS={1},\nIsDelVlans={2},".format(
            vlans_info, vni_list, is_del_vlans)
        tmp += "\nCOS={0},\nFILTER={1},".format(cos_ifs, if_filters)
        tmp += "\nVRFCPS={0},\nIsAllDel={1},\nis_vlans_all_del={2}".format(
            vrf_cps, is_all_del, is_vlans_all_del)
        tmp += "\nVLANLIST={0},\nDummyList={1},".format(vlan_list, dummy_list)
        tmp += "\nVRFCPS={0},\nChkVRFID={1},".format(
            check_vrf_name, check_vrf_id)
        tmp += "\nNewvlanlist={0},\nChgDummyIfList={1},".format(
            new_vlan_list, chg_dummy_if_list)
        tmp += "\nIsOtherSlice={0},".format(is_other_slice)
        self.common_util_log.logging(
            device_name, self.log_level_debug, tmp, __name__)

        conf_node = self._set_configuration_node(xml_obj)
        if cp_info or dummy_cp_info:
            self._set_l2_slice_interfaces(conf_node,
                                          cp_info,
                                          dummy_cp_info,
                                          vrf,
                                          irb_cps,
                                          vlan_list,
                                          dummy_list,
                                          irb_cps_del,
                                          del_vlan_list,
                                          new_vlan_list,
                                          chg_dummy_if_list,
                                          virtual_gateway_address_list,
                                          vrf_id,
                                          is_all_del,
                                          is_loop_del,
                                          is_other_slice,
                                          operation)

        if is_vlans_all_del and new_vlan_list and not is_other_slice:
            self._set_xml_tag(conf_node,
                              "vlans",
                              self._ATTR_OPE,
                              self._DELETE)
        elif vlans_info and operation != self._DELETE:
            self._set_l2_slice_vlans(conf_node,
                                     vlans_info,
                                     irb_cps,
                                     operation=operation)
        elif new_vlan_list and operation == self._DELETE:
            self._set_l2_slice_vlans_del(conf_node,
                                         new_vlan_list,
                                         operation=self._DELETE)

        if operation == self._DELETE and irb_cps:
            is_cp_del = self._check_slice_del(irb_cps)
            if is_all_del and vrf_cps:
                self._set_slice_routing_instance(conf_node,
                                                 vrf_name,
                                                 self._DELETE)
            elif is_cp_del and vrf_cps:
                node_1 = self._set_slice_routing_instance(conf_node,
                                                          vrf_name)
                self._set_slice_routing_instance_interface_delete(
                    node_1,
                    cp_info,
                    vrf_cps,
                    self._DELETE)
        elif vrf_cps and operation != self._DELETE:
            self._set_slice_routing_instance_vrf(conf_node,
                                                 vrf_name,
                                                 vrf,
                                                 cp_info,
                                                 dummy_cp_info,
                                                 vrf_cps)

        if vni_list:
            self._set_l2_slice_protocols_evpn(conf_node,
                                              vni_list,
                                              operation=operation)
        if cos_ifs:
            self._set_qos_policy_interfaces(conf_node,
                                            cos_ifs,
                                            self.name_l2_slice,
                                            operation)
        self._set_vlan_traffic_firewall(conf_node,
                                        if_filters,
                                        device_info)

        return True

    @decorater_log
    def _check_other_slice(self, slice_name, db_info):
        cp_infos = db_info.get("cp", ())
        dummys = db_info.get("dummy_cp", ())
        tmp = [cp for cp in cp_infos if cp.get("slice_name") != slice_name]
        tmp2 = [dummy for dummy in dummys if dummy.get(
            "slice_name") != slice_name]
        return bool(tmp or tmp2)

    @decorater_log
    def _gen_l2_slice_replace_message(self,
                                      xml_obj,
                                      device_info,
                                      ec_message,
                                      operation):
        '''
        Variable value to create message (L2Slice Replace) for Netconf.
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

            qos_info = self._get_l2_cps_qos_from_ec_rep(device_mes,
                                                        device_info,
                                                        slice_name)
            bind_ifs = self._get_l2_bind_if_replace(qos_info)

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

        tmp = "Replace L2 VLAN IF"
        tmp += "\nQoSInfo={0},\nBindIFs={1},".format(qos_info, bind_ifs)
        self.common_util_log.logging(
            device_name, self.log_level_debug, tmp, __name__)
        tmp = "EC/DB"
        tmp += "\nEc_message={0},\nDB_info={1},".format(device_mes,
                                                        device_info)
        self.common_util_log.logging(
            device_name, self.log_level_debug, tmp, __name__)

        conf_node = self._set_configuration_node(xml_obj)

        if bind_ifs:
            self._set_l2_slice_bind_if_rep(conf_node, bind_ifs)

        if qos_info:
            self._set_l2_slice_qos_rep(conf_node, qos_info)

        return True

    @decorater_log
    def _get_l2_bind_if_replace(self, qos_info):
        '''
        Set IF which changes the bind to IF  when L2CP is updated.
        '''
        bind_ifs = {}
        for if_name, value in qos_info.items():
            qos = value.get("QOS", {})
            port_mode = value.get("PORT-MODE")
            if (port_mode == self._PORT_MODE_TRUNK and
                    qos.get("BIND_IF_OPERATION")):
                tmp = {"OPERATION": qos["BIND_IF_OPERATION"]}
                bind_ifs[if_name] = tmp
        return bind_ifs

    @decorater_log
    def _get_l2_cps_qos_from_ec_rep(self,
                                    device_mes,
                                    db_info,
                                    slice_name=None,
                                    operation=None):
        '''
        Parameter from EC(Obtain qos data from cp)
        '''
        cp_dicts = {}
        for tmp_cp in device_mes.get("cp", ()):
            if (not tmp_cp.get("qos")):
                continue
            tmp, vlan_id = self._get_cp_interface_info_from_ec_rep(cp_dicts,
                                                                   tmp_cp,
                                                                   db_info,
                                                                   slice_name)
            port_mode = self._get_port_mode_l2slice_update(
                slice_name, tmp_cp, db_info)
            tmp["PORT-MODE"] = port_mode

            tmp["VLAN"][vlan_id] = self._get_qos_l2_vlan_if_info_from_ec(
                tmp_cp, db_info, slice_name)
            if tmp["VLAN"][vlan_id].get("OPERATION") == self._REPLACE:
                tmp["OPERATION"] = self._REPLACE

            self._check_del_policy_info(tmp, db_info)

        return cp_dicts

    @decorater_log
    def _check_del_policy_info(self, cp_info, db_info):
        if_name = cp_info.get("IF-NAME")
        port_mode = cp_info["PORT-MODE"]
        ec_qos = cp_info.get("QOS", {})

        is_ec_ingress = (ec_qos.get("INFLOW-SHAPING-RATE") is not None)
        is_ec_egress = (ec_qos.get("OUTFLOW-SHAPING-RATE") is not None)

        db_qos = None
        for db_cp in db_info["cp"]:
            if (db_cp["if_name"] == if_name and
                    db_cp["vlan"]["vlan_id"] in cp_info["VLAN"].keys()):
                db_qos = db_cp.get("qos", {})
                break

        is_db_ingress = (db_qos.get("inflow_shaping_rate") is not None)
        is_db_egress = (db_qos.get("outflow_shaping_rate") is not None)

        is_other_egress_on_if = False
        for db_cp in db_info["cp"]:
            if (db_cp["if_name"] == if_name and
                    db_cp["vlan"]["vlan_id"] not in cp_info["VLAN"].keys() and
                    db_cp.get("qos", {}).get(
                        "outflow_shaping_rate") is not None):
                is_other_egress_on_if = True
                break

        if port_mode == self._PORT_MODE_TRUNK:
            if is_db_egress and not is_ec_egress and not is_other_egress_on_if:
                cp_info["QOS"]["BIND_IF_OPERATION"] = self._DELETE
            elif is_ec_egress:
                cp_info["QOS"]["BIND_IF_OPERATION"] = self._REPLACE
                cp_info["QOS"]["EGRESS_FILTER_OPERATION"] = self._REPLACE

            if is_db_ingress and not is_ec_ingress:
                cp_info["QOS"]["INGRESS_FILTER_OPERATION"] = self._DELETE
            elif is_ec_ingress:
                cp_info["QOS"]["INGRESS_FILTER_OPERATION"] = self._REPLACE

        return cp_info

    @decorater_log
    def _get_cp_interface_info_from_ec_rep(self,
                                           cp_dicts,
                                           cp_info,
                                           db_info,
                                           slice_name):
        '''
        Collect IF information related to slice from EC message (Each unit of CP).
        '''
        if_name = cp_info.get("name")
        vlan_id = cp_info.get("vlan-id")
        operation = cp_info.get("operation")

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
                "IF-SPEED": None
            }

            if_speed = None
            if tmp.get("IF-TYPE") == self._if_type_lag:
                for lag_if in db_info.get("lag", {}):
                    if if_name == lag_if.get("if_name"):
                        if_speed = \
                            int(lag_if.get("link_speed").strip("g")) * \
                            int(lag_if.get("links"))
                        break
            else:
                for vlan_if in db_info.get("cp", {}):
                    if if_name == vlan_if.get("if_name"):
                        if_speed = \
                            int(vlan_if.get("speed").strip("g"))
                        break
            tmp["IF-SPEED"] = if_speed

            if cp_info.get("qos"):
                tmp["QOS"] = self._get_cp_qos_info_from_ec(cp_info, db_info)

            cp_dicts[if_name] = tmp
        else:
            tmp = cp_dicts[if_name]
        return tmp, vlan_id

    @decorater_log
    def _set_l2_slice_bind_if_rep(self, conf_node, bind_ifs={}):
        '''
        Set IF for L2 VLANIF change
        '''
        if not bind_ifs:
            return conf_node

        ifs_node = self._xml_setdefault_node(conf_node, "interfaces")
        for if_name, value in bind_ifs.items():
            attr_ope = self._ATTR_OPE
            attr_val = value["OPERATION"]

            if_node = self._set_xml_tag(ifs_node, "interface")
            self._set_xml_tag(if_node, "name", text=if_name)
            unit_node = self._set_xml_tag(if_node, "unit")
            self._set_xml_tag(unit_node, "name", text=0)
            family_node = self._set_xml_tag(unit_node, "family")
            ether_node = self._set_xml_tag(family_node, "ethernet-switching")
            filter_node = self._set_xml_tag(ether_node, "filter")
            if attr_val == self._DELETE:
                filter_name = None
            else:
                new_if_name = self._change_change_underbar_name(if_name)
                filter_name = "for_{0}_egress".format(new_if_name)
            self._set_xml_tag(filter_node,
                              "output",
                              attr_ope,
                              attr_val,
                              filter_name)

        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (conf_node.tag, etree.tostring(conf_node)),
            __name__)
        return ifs_node

    @decorater_log
    def _set_l2_slice_qos_rep(self, conf_node, qos_infos=None):
        '''
        Set qos for L2 VLANIF change
        '''
        if [(cp for cp in qos_infos.values()
             if cp["PORT-MODE"] == self._PORT_MODE_TRUNK)]:
            if_node = self._set_firewall(conf_node)
            eth_sw_node = self._set_firewall_ethernet_switching(if_node)
        else:
            self.common_util_log.logging(None, self.log_level_debug,
                                         "update filter is none", __name__)
            return

        for tmp_cp in qos_infos.values():
            tmp_qos = tmp_cp.get("QOS", {})
            if tmp_qos.get("INGRESS_FILTER_OPERATION"):
                tmp_ope = tmp_qos["INGRESS_FILTER_OPERATION"]
                self._set_qos_l2_vlan_if_rep(eth_sw_node,
                                             tmp_cp,
                                             "common",
                                             tmp_ope)
            if tmp_qos.get("EGRESS_FILTER_OPERATION"):
                tmp_ope = tmp_qos["EGRESS_FILTER_OPERATION"]
                self._set_qos_l2_vlan_if_rep(eth_sw_node,
                                             tmp_cp,
                                             "trunk",
                                             tmp_ope)

        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (conf_node.tag, etree.tostring(conf_node)),
            __name__)

    @decorater_log
    def _set_qos_l2_vlan_if_rep(self,
                                ifs_node,
                                cp_info,
                                ope_type,
                                ope_policy):
        '''
        Set IF(qos) for L2 VLANIF change.
        '''
        attr = self._ATTR_OPE
        attr_val = ope_policy

        new_if_name = self._change_change_underbar_name(cp_info["IF-NAME"])
        if ope_type == "trunk":
            name_str = "for_{0}_egress".format(new_if_name)
        else:
            name_str = "for_{0}".format(new_if_name)

        filter_node = self._set_firewall_filter_base_node(ifs_node,
                                                          name_str)
        if ope_type == "trunk":
            term_node = self._set_vlan_traffic_firewall_term_name(
                filter_node, "output_accept")
            from_node = self._set_xml_tag(term_node, "from")
            mac_node = self._set_xml_tag(from_node, "destination-mac-address")
            self._set_xml_tag(mac_node,
                              "mac-address",
                              text="01:80:c2:00:00:02/48")
            then_node = self._set_xml_tag(term_node, "then")
            self._set_xml_tag(then_node, "accept")

            outflow = cp_info.get("QOS", {}).get("OUTFLOW-SHAPING-RATE")
            if outflow is not None:
                if_speed = cp_info.get("IF-SPEED")
                outflow_shaping_rate = int(round(float(outflow) *
                                                 float(if_speed) * 10.0))
                policer = "{0}m-limit".format(outflow_shaping_rate)

                term_node = (
                    self._set_vlan_traffic_firewall_term_name(
                        filter_node,
                        "output_policing")
                )
                then_node = self._set_xml_tag(term_node, "then")
                self._set_xml_tag(then_node, "policer",
                                  attr, attr_val, policer)

        else:
            inflow = cp_info.get("QOS", {}).get("INFLOW-SHAPING-RATE")
            if cp_info.get("VLAN") is not None:
                if_speed = cp_info.get("IF-SPEED")
                inflow_shaping_rate = None
                policer = None
                if inflow is not None:
                    inflow_shaping_rate = int(round(float(inflow) *
                                                    float(if_speed) * 10.0))
                    policer = "{0}m-limit".format(inflow_shaping_rate)

                for vlan_id in cp_info.get("VLAN").keys():
                    term_name = "1001_vlan{0}-unicast_be".format(vlan_id)
                    term_node = (
                        self._set_vlan_traffic_firewall_term_name(filter_node,
                                                                  term_name)
                    )
                    then_node = self._set_xml_tag(term_node, "then")
                    self._set_xml_tag(then_node, "policer",
                                      attr, attr_val, policer)

        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (ifs_node.tag, etree.tostring(ifs_node)),
            __name__)
        return ifs_node

    @decorater_log
    def _get_port_mode_l2slice_update(self, slice_name, cp_ec_msg, db_info):
        '''
        Obtain port_mode of CP which is being processed by comparing EC message (CP information) and DB information.
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
        Set the section relating to VLAN_IF of CP.
        '''
        tmp = {
            "OPERATION": ec_cp.get("operation"),
            "CE-IF-VLAN-ID": ec_cp.get("vlan-id"),
        }

        return tmp

    @decorater_log
    def _gen_acl_filter_variable_message(self,
                                         xml_obj,
                                         device_info,
                                         ec_message,
                                         operation):
        '''
        Variable value to create message (acl-filter) for Netconf.
            Called out when creating message for ACLFilter. (after fixed message has been created)
        Parameter:
            xml_obj : xml object
            device_info : Device information
            operation : Designate "delete" when deleting
        Return value
            Creation result : Boolean (Write properly using override method)
        '''
        device_mes = ec_message.get("device", {})
        device_name = device_mes.get("name")

        try:
            filter_datas = self._get_acl_filter_from_ec(device_mes)
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

        fw_node = self._set_firewall(conf_node)
        eth_sw_node = self._set_firewall_ethernet_switching(fw_node)

        for filter_data in filter_datas.values():
            self._set_acl_filter(eth_sw_node,
                                 filter_data,
                                 operation)
        return True

    @decorater_log
    def _gen_ce_lag_variable_message(self,
                                     xml_obj,
                                     device_info,
                                     ec_message,
                                     operation):
        '''
        Variable value to create message (CeLag) for Netconf.
            Called out when creating message forCeLag(after fixed message has been created)
        Parameter:
            xml_obj : xml object
            device_info : Device information
            operation : Designate "delete" when deleting
        Return value
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
            Called out when creating message for InternalLag.(after fixed message has been created)
        Parameter:
            xml_obj : xml object
            device_info : Device information
            operation : Designate "delete" when deleting
        Return value
            Creation result : Boolean (Write properly using override method)
        '''
        device_mes = ec_message.get("device", {})
        device_name = device_mes.get("name")

        vpns = {"l2": 2, "l3": 3}

        try:
            area_id = device_info["device"]["ospf"]["area_id"]
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
        Judge whether internal link IF change is depends  on cost value change or LAG speed change.
        Parameter:
            device_mes : EC message (device and below)（json）
        Return Value:
            result  : Boolean(cost value change：True, Lag speed change：False)
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
        Variable value to create message (cluster-link) for Netconf.
            Called out when creating message for cluster-link.
            (After fixed message has been created.)
        Parameter:
            xml_obj : xml object
            operation : Designate "delete" when deleting.
        Return value.
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
    def _get_cp_qos_info_from_ec(self, cp_info_ec, db_info):
        '''
        Add QoS information from EC to CP information to be set.
        Parameter:
            cp_info_ec: dict CP information input from EC.
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

        tmp_inflow_shaping_rate = cp_info_ec[
            "qos"].get("inflow-shaping-rate", ())
        if tmp_inflow_shaping_rate:
            cp_info_em["INFLOW-SHAPING-RATE"] = tmp_inflow_shaping_rate
        tmp_outflow_shaping_rate = cp_info_ec[
            "qos"].get("outflow-shaping-rate", ())
        if tmp_outflow_shaping_rate:
            cp_info_em["OUTFLOW-SHAPING-RATE"] = tmp_outflow_shaping_rate

        return cp_info_em

    @decorater_log
    def _get_cp_irb_info_from_ec(self, cp_info_ec, db_info):
        '''
        Add IRB information from EC to CP information to be set.
        Parameter:
            cp_info_ec: dict CP information from EC
            db_info: dict DB information
        Return Value:
            cp_info_em : dict IRB information which is input in device
        '''
        cp_info_em = {}

        irb_ec = cp_info_ec.get("irb")
        phys_ip_addr = irb_ec.get("physical-ip-address")
        if phys_ip_addr:
            cp_info_em["IRB-ADDR"] = phys_ip_addr.get("address")
            cp_info_em["IRB-PREFIX"] = int(phys_ip_addr.get("prefix"))
        if irb_ec.get("virtual-gateway"):
            vr_gw = irb_ec.get("virtual-gateway")
            cp_info_em["IRB-VIRT-GW-ADDR"] = vr_gw.get("address")
        return cp_info_em

    @decorater_log
    def _get_ec_dummy_vni_counts(self, ec_cp_info):
        ec_vni = {}
        for ec_if in ec_cp_info.values():
            for vlan in ec_if.get("VLAN", {}).values():
                vni = int(vlan.get("VNI"))
                if vni in ec_vni.keys():
                    if vlan.get("OPERATION") != self._DELETE:
                        ec_vni[vni] += 1
                    else:
                        ec_vni[vni] -= 1
                else:
                    if vlan.get("OPERATION") != self._DELETE:
                        ec_vni[vni] = 1
                    else:
                        ec_vni[vni] = -1
        return ec_vni

    @decorater_log
    def _get_ec_dummy_vlan_counts(self, ec_cp_info):
        ec_vlan = {}
        for ec_if in ec_cp_info.values():
            for vlan in ec_if.get("VLAN", {}).values():
                vlan_id = vlan.get("CE-IF-VLAN-ID")
                if vlan_id in ec_vlan.keys():
                    if vlan.get("OPERATION") != self._DELETE:
                        ec_vlan[vlan_id]["count"] += 1
                    else:
                        ec_vlan[vlan_id]["count"] -= 1
                else:
                    if vlan.get("OPERATION") != self._DELETE:
                        ec_vlan[vlan_id] = {"count": 1, "VNI": vlan.get("VNI")}
                    else:
                        ec_vlan[vlan_id] = {
                            "count": -1, "VNI": vlan.get("VNI")}
        return ec_vlan

    @decorater_log
    def _change_change_underbar_name(self, change_param):
        first_change_param = change_param.replace("-", "_")
        new_change_param = first_change_param.replace("/", "_")
        return new_change_param
