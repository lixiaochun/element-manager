# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2018 Nippon Telegraph and Telephone Corporation
# Filename: JuniperDriverMX240.py
'''
Individual section on driver (JuniperDriver's driver (MX240))
'''
import re
import ipaddress
from lxml import etree
import copy
import traceback
import GlobalModule
from EmSeparateDriver import EmSeparateDriver
from EmCommonLog import decorater_log
from EmCommonLog import decorater_log_in_out


class JuniperDriverMX240(EmSeparateDriver):
    '''
    Individual section on driver (JuniperDriver's driver)
                                (MX240)
    '''

    _PORT_MODE_ACCESS = "access"
    _PORT_MODE_TRUNK = "trunk"
    _ATTR_OPE = "operation"
    _XML_LOG = "set xml node (parent = %s):\n%s"

    @decorater_log_in_out
    def connect_device(self, device_name,
                       device_info, service_type, order_type):
        '''
        Driver individual section connection control.
            Launch from the common section on driver,
            conduct device connection control to protocol processing section.
        Parameter:
            device_name : Device name
            device_info : Device information
            service_type : Service type
            order_type : Order type
        Return value :
            Protocol processing section response :
                int (1:Normal, 2:Capability abnormal, 3:No response)
        '''
        if service_type in (self.name_spine,
                            self.name_leaf,
                            self.name_b_leaf,
                            self.name_recover_node,
                            self.name_internal_link,):
            return GlobalModule.COM_CONNECT_OK
        else:
            return self.as_super.connect_device(device_name,
                                                device_info,
                                                service_type,
                                                order_type)

    @decorater_log_in_out
    def update_device_setting(self, device_name,
                              service_type, order_type, ec_message=None):
        '''
        Driver individual section edit control.
            Launch from the common section on driver,
            transmit device control signal to protocol processing section.
        Parameter:
            device_name : Device name
            service_type : Service type
            order_type : Order type
        Return value :
            Processing finish status : int (1:Successfully updated
                                2:Validation check NG
                                3:Updating unsuccessful)
        '''
        if service_type in (self.name_spine,
                            self.name_leaf,
                            self.name_b_leaf,
                            self.name_recover_node,
                            self.name_internal_link,):
            return GlobalModule.COM_UPDATE_OK
        else:
            return self.as_super.update_device_setting(device_name,
                                                       service_type,
                                                       order_type,
                                                       ec_message)

    @decorater_log_in_out
    def delete_device_setting(self, device_name,
                              service_type, order_type, ec_message=None):
        '''
        Driver individual section deletion control.
            Launch from the common section on driver,
            conduct device deletion control to protocol processing section.
        Parameter:
            device_name : Device name
            service_type : Service type
            order_type : Order type
            diff_info : Information about difference
        Return value :
            Processing finish status : int (1:Successfully deleted
                                2:Validation check NG
                                3:Deletion unsuccessful)
        '''
        if service_type in (self.name_spine,
                            self.name_leaf,
                            self.name_b_leaf,
                            self.name_recover_node,
                            self.name_internal_link,):
            return GlobalModule.COM_DELETE_OK
        else:
            return self.as_super.delete_device_setting(device_name,
                                                       service_type,
                                                       order_type,
                                                       ec_message)

    @decorater_log_in_out
    def reserve_device_setting(self, device_name, service_type, order_type):
        '''
        Driver individual section tentative setting control.
            Launch from the common section on driver,
            conduct device tentative setting control
            to protocol processing section.
        Parameter:
            device_name : Device name
            service_type : Service type
            order_type : Order type
        Return value :
            Processing finish status : Boolean (True:Normal, False:Abnormal)
        '''
        if service_type in (self.name_spine,
                            self.name_leaf,
                            self.name_b_leaf,
                            self.name_recover_node,
                            self.name_internal_link,):
            return GlobalModule.COM_UPDATE_OK
        else:
            return self.as_super.reserve_device_setting(device_name,
                                                        service_type,
                                                        order_type)

    @decorater_log_in_out
    def enable_device_setting(self, device_name, service_type, order_type):
        '''
        Driver individual section established control.
            Launch from the common section on driver,
            conduct device established control to protocol processing section.
        Parameter:
            device_name : Device name
            service_type : Service type
            order_type : Order type
        Return value :
            Processing finish status : Boolean (True:Normal, False:Abnormal)
        '''
        if service_type in (self.name_spine,
                            self.name_leaf,
                            self.name_b_leaf,
                            self.name_recover_node,
                            self.name_internal_link):
            return GlobalModule.COM_UPDATE_OK
        else:
            return self.as_super.enable_device_setting(device_name,
                                                       service_type,
                                                       order_type)

    @decorater_log_in_out
    def disconnect_device(self, device_name, service_type, order_type):
        '''
        Driver individual section disconnection control.
            Launch from the common section on driver,
            conduct device disconnection control to
            protocol processing section.
        Parameter:
            device_name : Device name
            service_type : Service type
            order_type : Order type
        Return value :
            Processing finish status : Should always return "True"
        '''
        if service_type in (self.name_spine,
                            self.name_leaf,
                            self.name_b_leaf,
                            self.name_recover_node,
                            self.name_internal_link):
            return GlobalModule.COM_CONNECT_OK
        else:
            return self.as_super.disconnect_device(device_name,
                                                   service_type,
                                                   order_type)

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''
        self.as_super = super(JuniperDriverMX240, self)
        self.as_super.__init__()
        self._MERGE = GlobalModule.ORDER_MERGE
        self._DELETE = GlobalModule.ORDER_DELETE
        self._REPLACE = GlobalModule.ORDER_REPLACE
        self._vpn_types = {"l2": 2, "l3": 3}
        self.list_enable_service = [self.name_spine,
                                    self.name_leaf,
                                    self.name_b_leaf,
                                    self.name_l3_slice,
                                    self.name_celag,
                                    self.name_internal_link,
                                    self.name_cluster_link,
                                    self.name_recover_service,
                                    ]
        self._lag_check = re.compile("^ae([0-9]{1,})")
        tmp_get_mes = (
            '<filter>' +
            '<configuration></configuration>' +
            '</filter>')
        self.get_config_message = {
            self.name_l2_slice: tmp_get_mes,
            self.name_l3_slice: tmp_get_mes,
        }

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
        elif not is_result and isinstance(message, str) and\
                "Cannot connect to other RE, ignoring it" in message:
            is_result = True
        return is_result, message


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
    def _set_interfaces_node(self, conf_node):
        '''
        Set interfaces.
        '''
        return self._xml_setdefault_node(conf_node, "interfaces")

    @decorater_log
    def _set_interface_lag_member(self,
                                  if_node,
                                  base_if_name=None,
                                  lag_if_name=None,
                                  operation=None):
        '''
        Set LAG member IF.
        '''
        attr, attr_val = self._get_attr_from_operation(operation)

        node_1 = self._set_xml_tag(if_node, "interface", attr, attr_val)
        self._set_xml_tag(node_1,
                          "interface_name",
                          None,
                          None,
                          base_if_name)
        if operation == self._DELETE:
            return node_1
        node_2 = self._set_xml_tag(node_1, "gigether-options")
        node_3 = self._set_xml_tag(node_2, "ieee-802.3ad")
        bundle_val = lag_if_name
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
            self._set_xml_tag(node_2,
                              "minimum-links",
                              None,
                              None,
                              lag_links)
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
                                  opposite_vpn_type=None):
        '''
        Create unit node of interface node for
        internal link/inter-cluster link.
        '''
        node_2 = self._set_xml_tag(if_node, "unit")
        self._set_xml_tag(node_2, "name", None, None, "0")
        node_3 = self._set_xml_tag(node_2, "family")
        node_4 = self._set_xml_tag(node_3, "inet")
        node_5 = self._set_xml_tag(node_4, "address")
        self._set_xml_tag(node_5,
                          "source",
                          None,
                          None,
                          "%s/%s" % (if_addr, if_prefix))
        if vpn_type != 2 and opposite_vpn_type != 2:
            self._set_xml_tag(node_3, "mpls")
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (if_node.tag, etree.tostring(node_2),),
            __name__)
        return node_2

    @decorater_log
    def _set_device_protocols(self, conf_node):
        '''
        Set protocols for device.
        '''
        return self._xml_setdefault_node(conf_node, "protocols")

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
        *Should be only for ClusterLink since
        InternalLink does not exist in MX240.
            options  ; operation : Operation type
        '''
        operation = options.get("operation")

        for if_info in if_infos:
            metric = if_info.get("OSPF-METRIC", 100)
            self._set_ospf_area_interface(area_node,
                                          if_info.get("IF-NAME"),
                                          metric,
                                          operation=operation)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (area_node.tag, etree.tostring(area_node)),
            __name__)

    @decorater_log
    def _set_ospf_area_interface(self,
                                 area_node,
                                 if_name,
                                 metric=100,
                                 operation=None):
        '''
        Set IF for the ospf/area node.
        '''
        attr, attr_val = self._get_attr_from_operation(operation)

        node_2 = self._set_xml_tag(area_node, "interface",  attr, attr_val)
        self._set_xml_tag(node_2,
                          "interface_name",
                          None,
                          None,
                          "%s.%d" % (if_name, 0))
        if operation != self._DELETE:
            self._set_xml_tag(node_2, "interface-type", None, None, "p2p")
            self._set_xml_tag(node_2, "metric", None, None, metric)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (area_node.tag, etree.tostring(node_2)),
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
        *Should be only L3CP in case of MX240.
        '''
        tmp = None
        if mtu is None:
            tmp = None
        else:
            if is_vlan:
                tmp = 4114
            else:
                tmp = int(mtu) + 14
        return tmp


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
                self._set_l3_slice_vlan_unit(node_1,
                                             unit,
                                             is_vlan=is_vlan,
                                             mtu=mtu)
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
                                mtu=None):
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
        is_add_cp = False
        if vlan.get("CE-IF-ADDR6") or vlan.get("CE-IF-ADDR"):
            is_add_cp = True
        if vlan.get("CE-IF-ADDR6"):
            self._set_l3_slice_vlan_unit_address(
                node_2,
                6,
                ip_addr=vlan.get("CE-IF-ADDR6"),
                prefix=vlan.get("CE-IF-PREFIX6"),
                is_vlan=is_vlan,
                mtu=mtu,
                is_add_cp=is_add_cp
            )
        if vlan.get("CE-IF-ADDR"):
            self._set_l3_slice_vlan_unit_address(
                node_2,
                4,
                ip_addr=vlan.get("CE-IF-ADDR"),
                prefix=vlan.get("CE-IF-PREFIX"),
                is_vlan=is_vlan,
                mtu=mtu,
                is_add_cp=is_add_cp
            )
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
        '''
        ip_addr = params.get("ip_addr")
        prefix = params.get("prefix")
        is_vlan = params.get("is_vlan")
        mtu = params.get("mtu")
        is_add_cp = params.get("is_add_cp", True)

        tag_name = "inet" if ip_ver == 4 else "inet6"
        node_1 = self._set_xml_tag(family_node, tag_name)
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

        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (conf_node.tag, etree.tostring(node_1)),
            __name__)
        return node_2


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
            else:
                tmp_bool = bool(not tmp.get("name") or
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
                lag_mem_ifs.append(self._get_lag_mem_if_info(tmp, lag_mem))
        return lag_ifs, lag_mem_ifs

    @decorater_log
    def _get_lag_if_info(self, if_info):
        '''
        Obtain LAG information from EC message.
        '''
        tmp = {
            "IF-NAME": if_info.get("name"),
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
               "LAG-IF-NAME": lag_if["name"], }
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
    def _get_cp_interface_info_from_ec(self, cp_dicts, cp_info):
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
            cp_dicts[if_name] = tmp
        else:
            tmp = cp_dicts[if_name]
        return tmp, vlan_id

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

    @decorater_log
    def _get_l3_vlan_if_info_from_ec(self,
                                     ec_cp,
                                     db_info,
                                     slice_name=None):
        '''
        Conduct setting for the section relating to VLAN_IF on CP.
        '''
        if_name = ec_cp.get("name")
        tmp = {
            "OPERATION": ec_cp.get("operation"),
            "CE-IF-VLAN-ID": ec_cp.get("vlan-id"),
        }
        ce_if = ec_cp.get("ce-interface", {})
        self._get_if_ip_network(ce_if.get("address"), ce_if.get("prefix"))
        self._get_if_ip_network(ce_if.get("address6"), ce_if.get("prefix6"))
        tmp.update({
            "CE-IF-ADDR6": ce_if.get("address6"),
            "CE-IF-PREFIX6": ce_if.get("prefix6"),
            "CE-IF-ADDR": ce_if.get("address"),
            "CE-IF-PREFIX":  ce_if.get("prefix"),
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
                    tmp_cp.get("operation") is None):
                continue
            tmp, vlan_id = self._get_cp_interface_info_from_ec(
                cp_dicts, tmp_cp)
            tmp["VLAN"][vlan_id] = self._get_l3_vlan_if_info_from_ec(
                tmp_cp, db_info, slice_name)
            if tmp["VLAN"][vlan_id].get("OPERATION") == self._DELETE:
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
                if len(cp_data["VLAN"]) == len(db_cp.get(if_name, ())):
                    tmp = {"IF-NAME": if_name,
                           "IF-PORT-MODE": cp_data.get("IF-PORT-MODE")}
                    cos_if_list.append(tmp)
                    cp_dict[if_name]["OPERATION"] = self._DELETE
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
    def _gen_l3_slice_fix_message(self, xml_obj, operation):
        '''
        L3Slice
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
    def _gen_l3_slice_replace_message(self,
                                      xml_obj,
                                      device_info,
                                      ec_message,
                                      operation):
        '''
        Variable value to create message (L3Slice) for Netconf.
            Called out when creating message for SpineL3Slice.
            (After fixed message has been created.)
        Parameter:
            xml_obj : xml object
            device_info : Device information
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean (Write properly using override method)
        '''
        self.common_util_log.logging(
            None,
            self.log_level_debug,
            "ERROR : l3slice order_type = replace ",
            __name__)
        return False

    @decorater_log
    def _gen_l3_slice_variable_message(self,
                                       xml_obj,
                                       device_info,
                                       ec_message,
                                       operation):
        '''
        Variable value to create message (L3Slice) for Netconf.
            Called out when creating message for SpineL3Slice.
            (After fixed message has been created.)
        Parameter:
            xml_obj : xml object
            device_info : Device information
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

        return True

    @decorater_log
    def _gen_ce_lag_variable_message(self,
                                     xml_obj,
                                     device_info,
                                     ec_message,
                                     operation):
        '''
        Variable value to create message (CeLag) for Netconf.
            Called out when creating message for CeLag.
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

        if_node = self._set_interfaces_node(conf_node)

        for tmp_if in lag_mem_ifs:
            self._set_interface_lag_member(if_node,
                                           tmp_if["IF-NAME"],
                                           tmp_if["LAG-IF-NAME"],
                                           operation=operation)
        for tmp_if in lag_ifs:
            self._set_interface_lag(if_node,
                                    tmp_if.get("IF-NAME"),
                                    tmp_if.get("LAG-LINKS"),
                                    tmp_if.get("LAG-SPEED"),
                                    operation=operation)
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
            device_info : Device information
            ec_message : EC message
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

        return True


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

        return is_return
