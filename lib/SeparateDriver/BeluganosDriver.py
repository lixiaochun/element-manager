#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: BeluganosDriver.py
'''
Beluganos driver module
'''
import traceback
from lxml import etree
from xml.etree import ElementTree

from EmSeparateDriver import EmSeparateDriver
from EmCommonLog import decorater_log

_xmlns_netconf_insert_point = "__XMLNS_NETCONF_INSERT_POINT__"
ncclient_update = {
    _xmlns_netconf_insert_point: "\" xmlns:netconf=\"urn:ietf:params:xml:ns:netconf:base:1.0"
}


class BeluganosDriver(EmSeparateDriver):
    '''
    Beluganos driver class
    '''

    _XML_LOG = "set xml node (parent = %s):\n%s"

    _DEFAULT_INTERNAL_LINK_COST = 100

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''
        self.as_super = super(BeluganosDriver, self)
        self.as_super.__init__()

        self.list_enable_service = [
            self.name_internal_link,
        ]
        self._ope_xmlns_ianaift = "xmlns_ianaift"
        self._ope_xmlns_oc_ospf_types = "xmlns_oc_ospf_types"
        self._ope_xmlns_oc_pol_types = "xmlns_oc_pol_types"
        self._ope_netconf_operation = "netconf_operation"
        self._beluganos_name_spaces = {
            self._ope_xmlns_ianaift: "xmlns:ianaift",
            self._ope_xmlns_oc_ospf_types: "xmlns:oc-ospf-types",
            self._ope_xmlns_oc_pol_types: "xmlns:oc-pol-types",
            self._ope_netconf_operation: "netconf:operation",
        }

        self._ATRI_OPE = self._ope_netconf_operation

        self._xmlns_netconf_insert_point = "__XMLNS_NETCONF_INSERT_POINT__"
        self.ncclient_update = {
            self._xmlns_netconf_insert_point: "xmlns:netconf=\"urn:ietf:params:xml:ns:netconf:base:1.0\""
        }


    @decorater_log
    def _send_control_signal(self,
                             device_name,
                             message_type,
                             send_message=None,
                             service_type=None,
                             operation=None):
        '''
        Send message to protocol processing section
        Parameter:
            device_name ; Device name
            message_type ; Message type
            send_message : Transmission message
        Return value
            Processing result ; Boolean （result of send_control_signal)
            Message ; str （result of send_control_signal)
        '''
        if message_type == "edit-config":
            return self._send_edit_config(device_name,
                                          send_message,
                                          service_type,
                                          operation)
        elif message_type in ("validate", "confirmed-commit", "commit"):
            return True, None
        else:
            return (self.as_super._send_control_signal(device_name,
                                                       message_type,
                                                       send_message))

    @decorater_log
    def _send_edit_config(self,
                          device_name,
                          send_message=None,
                          service_type=None,
                          operation=None):
        '''
        Send edit-config message
        Parameter:
            device_name ; Device name
            send_message : Transmission message
            service_type:Service type
            operation ; Operation
        Return value
            Processing result ; Boolean （result of _send_edit_config_signal)
            Message ; str （result of _send_edit_config_signal)
        '''
        if (service_type == self.name_internal_link and
                operation in (self._MERGE, None) and
                send_message is not None):
            send_xml = etree.fromstring(send_message)
            conf_ifs = etree.Element(self._send_message_top_tag)
            conf_ifs.append(send_xml[0])
            send_mes_1 = etree.tostring(conf_ifs)
            send_mes_2 = etree.tostring(send_xml)
            is_result, message = self._send_edit_config_signal(device_name,
                                                               send_mes_1)
            if not is_result:
                return False, message
            else:
                return self._send_edit_config_signal(device_name,
                                                     send_mes_2)
        return self._send_edit_config_signal(device_name, send_message)

    @decorater_log
    def _send_edit_config_signal(self, device_name, send_message=None):
        '''
        Send message to protocol processing section
        Parameter:
            device_name ; Device name
            send_message : Transmission message
        Return value
            Processing result ; Boolean （result of _send_control_signal)
            Message ; str （result of _send_control_signal)
        '''
        send_message = self._convert_beluganos_name_space(send_message)
        is_result, edit_message = (
            self.as_super._send_control_signal(
                device_name, "edit-config", send_message)
        )
        if not is_result:
            return False, edit_message
        is_result, message = (
            self.as_super._send_control_signal(
                device_name, "validate")
        )
        if not is_result:
            return False, message
        is_result, message = (
            self.as_super._send_control_signal(
                device_name, "commit")
        )
        if not is_result:
            return False, message
        return True, edit_message

    @decorater_log
    def _convert_beluganos_name_space(self, xml_str):
        return_xml_str = xml_str
        if isinstance(xml_str, str):
            for key, value in self._beluganos_name_spaces.items():
                return_xml_str = return_xml_str.replace(key, value)
        return return_xml_str


    @decorater_log
    def _gen_internal_link_fix_message(self, xml_obj, operation):
        '''
        Fixed value to create message for Netconf(InternalLink)
            Called out when generating messages for InternalLink
        Parameter:
            xml_obj : xmlobject
            operation : Designate "delete" when deleting
        Return value
            Generate result : Boolean
        '''
        return True

    @decorater_log
    def _gen_internal_link_variable_message(self,
                                            xml_obj,
                                            device_info,
                                            ec_message,
                                            operation):
        '''
        Variable value to create message for Netconf(InternalLink)
            Called out when creating message for InternalLink
        Parameter:
            xml_obj : xmlobject
            device_info : Device information
            operation : Designate "delete" when deleting
        Return value
            Generate result : Boolean (Write properly using override method)
        '''
        device_mes = ec_message.get("device", {})
        device_name = device_mes.get("name")

        try:
            area_id = device_info["device"]["ospf"]["area_id"]
            if len(device_mes.get("internal-lag")) > 0:
                raise ValueError(
                    "Lag IF for internal-link in this driver is not allowed.")
            if operation == self._DELETE:
                inner_ifs = self._get_del_internal_link_from_ec(
                    device_mes, db_info=device_info)
            elif operation == self._REPLACE:
                inner_ifs = self._get_replace_internal_link_from_ec(device_mes,
                                                                    device_info)
            else:
                inner_ifs = self._get_internal_link_from_ec(device_mes)
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
        self.common_util_log.logging(
            device_name,
            self.log_level_debug,
            "area_id:{0}, IL param:{1}".format(area_id, inner_ifs),
            __name__)
        self._set_internal_link(xml_obj, inner_ifs, area_id, operation)
        return True


    @decorater_log
    def _get_del_internal_link_from_ec(self, device_mes, db_info=None):
        '''
        Obtain EC message/DB information relating to internal link for deletion(LAG)
        Explanation about parameter:
            device_message: Message for each device
            db_info : DB information
        Return Value :
             internal link information
        '''
        inner_ifs = []

        for tmp_if in device_mes.get("internal-physical", ()):
            if_name = tmp_if.get("name")
            vlan_id = self._get_vlan_id_by_db_info(if_name, db_info)
            if not if_name or vlan_id is None:
                raise ValueError("internal-physical not enough information")

            inner_ifs.append(
                {
                    "IF-NAME": if_name,
                    "INNER-IF-VLAN": vlan_id,
                }
            )
        return inner_ifs

    @decorater_log
    def _get_vlan_id_by_db_info(self, if_name, db_info):
        db_link = db_info.get("internal-link", ())
        for link_if in db_link:
            if link_if.get("if_name") == if_name:
                return link_if.get("vlan_id")
        return None

    @decorater_log
    def _get_internal_link_from_ec(self, device_mes):
        '''
        Obtain information of EC message relating to internal link(LAG)
        '''
        inner_ifs = []

        for tmp in device_mes.get("internal-physical", ()):
            if (not tmp.get("name") or
                    tmp.get("vlan-id") is None or
                not tmp.get("address") or
                    tmp.get("prefix") is None):
                raise ValueError("internal-physical not enough information")

            inner_ifs.append(
                self._get_internal_if_info(tmp, self._if_type_phy))

        return inner_ifs

    @decorater_log
    def _get_replace_internal_link_from_ec(self, device_mes, device_info):
        '''
        Obtain information of EC message relating to internal link
        '''
        inner_ifs = []

        for tmp in device_mes.get("internal-physical", ()):
            if (not tmp.get("name") or
                    tmp.get("cost") is None):
                raise ValueError("internal-physical not enough information")

            inner_ifs.append(
                self._get_internal_if_replace_info(tmp,
                                                   self._if_type_phy,
                                                   device_info))
        return inner_ifs

    @decorater_log
    def _get_internal_if_replace_info(self,
                                      if_info,
                                      if_type=None,
                                      device_info=None):
        '''
        Obtain information of internal link from EC message (physical only)
        '''
        if_name = if_info.get("name")
        vlan_id = self._get_vlan_id_by_db_info(if_name, device_info)

        tmp = {
            "IF-TYPE": if_type,
            "IF-NAME": if_info.get("name"),
            "INNER-IF-VLAN": vlan_id,
            "OSPF-METRIC": if_info.get("cost")
        }
        return tmp

    @decorater_log
    def _get_internal_if_info(self, if_info, if_type=None):
        '''
        Obtain information of internal link from EC message (physical only)
        '''
        tmp = {
            "IF-TYPE": if_type,
            "IF-NAME": if_info.get("name"),
            "IF-ADDR": if_info.get("address"),
            "IF-PREFIX": if_info.get("prefix"),
            "INNER-IF-VLAN": if_info.get("vlan-id"),
            "OSPF-METRIC": if_info.get("cost",
                                       self._DEFAULT_INTERNAL_LINK_COST)
        }
        return tmp

    @decorater_log
    def _set_internal_link(self, xml_obj, inner_ifs, area_id, operation=None):
        '''
        Generate message of internal link
        '''
        if not operation == self._REPLACE:
            self._set_internal_link_interfaces_node(
                xml_obj, inner_ifs, operation)
        self._set_internal_link_nw_ins_node(xml_obj,
                                            inner_ifs,
                                            area_id,
                                            operation)

    @decorater_log
    def _set_internal_link_interfaces_node(self,
                                           xml_obj,
                                           inner_ifs,
                                           operation=None):
        '''
        Generate interfaces section of internal link
        '''
        ifs_node = self._set_interfaces_node(xml_obj, operation)
        for inner_if in inner_ifs:
            self._set_internal_link_interface_node(ifs_node,
                                                   inner_if,
                                                   operation)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (ifs_node.tag, etree.tostring(ifs_node),),
            __name__)

    @decorater_log
    def _set_internal_link_interface_node(self,
                                          ifs_node,
                                          inner_if,
                                          operation=None):
        '''
        Generate interface section of internal link
        '''
        if_node = self._set_interface_base(ifs_node,
                                           inner_if["IF-NAME"],
                                           operation)
        if operation != self._DELETE:
            subifs_node = self._set_subinterfaces_node(if_node)
            self._set_subinterface(subifs_node, vlan_id=0, mtu=4114)
            self._set_subinterface(subifs_node,
                                   inner_if["INNER-IF-VLAN"],
                                   4096,
                                   inner_if["IF-ADDR"],
                                   inner_if["IF-PREFIX"])

    @decorater_log
    def _set_internal_link_nw_ins_node(self,
                                       xml_obj,
                                       inner_ifs=[],
                                       area_id=None,
                                       operation=None):
        '''
        Generate network setting section of internal link (network-instances)
        '''
        nw_inss_node = self._set_network_instances_node(xml_obj, operation)
        nw_ins_node = self._set_network_instance_node(nw_inss_node, "mic")
        if operation != self._REPLACE:
            self._set_assignment_to_master_interface(nw_ins_node,
                                                     inner_ifs,
                                                     operation)
        protocols_node = self._set_protocols_node(nw_ins_node)
        self._set_ospf_protocol_node(protocols_node,
                                     area_id,
                                     inner_ifs,
                                     operation)
        self.common_util_log.logging(
            None, self.log_level_debug,
            self._XML_LOG % (nw_inss_node.tag, etree.tostring(nw_inss_node),),
            __name__)



    @decorater_log
    def _set_interfaces_node(self, xml_obj, operation=None):
        '''
        Create interfaces node, and return the node which has been created
        '''
        ns = "https://github.com/beluganos/beluganos/yang/interfaces"
        if operation == self._REPLACE or operation == self._DELETE:
            ns = "https://github.com/beluganos/beluganos/yang/interfaces" + \
                _xmlns_netconf_insert_point
        else:
            ns = "https://github.com/beluganos/beluganos/yang/interfaces"
        return self._set_xml_tag(xml_obj, "interfaces", "xmlns", ns)

    @decorater_log
    def _set_interface_base(self, ifs_node, if_name, operation=None):
        '''
        Create interface as child node of interfaces node, and return the node which has been created
        '''
        attr, attr_val = self._get_attr_from_operation(operation)
        if_node = self._set_xml_tag(ifs_node, "interface", attr, attr_val)
        self._set_xml_tag(if_node, "name", text=if_name)
        if operation != self._DELETE:
            conf_node = self._set_xml_tag(if_node, "config")
            self._set_xml_tag(conf_node, "name", text=if_name)
            self._set_xml_tag(conf_node,
                              "type",
                              self._ope_xmlns_ianaift,
                              "urn:ietf:params:xml:ns:yang:iana-if-type",
                              "ianaift:ethernetCsmacd")
        return if_node

    @decorater_log
    def _set_subinterfaces_node(self, if_node):
        '''
        Create subinterfaces node and return the node which has been created
        '''
        return self._set_xml_tag(if_node, "subinterfaces")

    @decorater_log
    def _set_subinterface(self,
                          subifs_node,
                          vlan_id=None,
                          mtu=None,
                          address=None,
                          prefix=None):
        '''
        Create interface as child node of interfaces node, and return the node which has been created
        '''
        sif_node = self._set_xml_tag(subifs_node, "subinterface")
        self._set_xml_tag(sif_node, "index", text=vlan_id)
        conf_node = self._set_xml_tag(sif_node, "config")
        self._set_xml_tag(conf_node, "index", text=vlan_id)
        self._set_xml_tag(conf_node, "enabled", text="true")
        ns = "https://github.com/beluganos/beluganos/yang/interfaces/ip"
        ipv4_node = self._set_xml_tag(sif_node, "ipv4", "xmlns", ns)
        if address is not None and prefix is not None:
            self._set_subinterface_ip_address(ipv4_node, address, prefix)
        ip_conf_node = self._set_xml_tag(ipv4_node, "config")
        self._set_xml_tag(ip_conf_node, "mtu", text=mtu)
        return sif_node

    @decorater_log
    def _set_subinterface_ip_address(self, ip_node, address=None, prefix=None):
        '''
        Create interface as child node of interfaces node, and return the node which has been created
        '''
        addrs_node = self._set_xml_tag(ip_node, "addresses")
        addr_node = self._set_xml_tag(addrs_node, "address")
        self._set_xml_tag(addr_node, "ip", text=address)
        conf_node = self._set_xml_tag(addr_node, "config")
        self._set_xml_tag(conf_node, "ip", text=address)
        self._set_xml_tag(conf_node, "prefix-length", text=prefix)
        return addrs_node


    @decorater_log
    def _set_network_instances_node(self, xml_obj, operation=None):
        '''
        Create network-instances node and return the node which has been created
        '''
        if operation == self._REPLACE or operation == self._DELETE:
            ns = "https://github.com/beluganos/beluganos/yang/network-instance" + \
                _xmlns_netconf_insert_point
        else:
            ns = "https://github.com/beluganos/beluganos/yang/network-instance"
        return self._set_xml_tag(xml_obj, "network-instances", "xmlns", ns)

    @decorater_log
    def _set_network_instance_node(self, nw_inss_node, name="mic"):
        '''
        Create network-instance node, and return the node which has been created which has been created
        '''
        node_1 = self._set_xml_tag(nw_inss_node, "network-instance")
        self._set_xml_tag(node_1, "name", text=name)
        return node_1

    @decorater_log
    def _set_assignment_to_master_interface(self,
                                            nw_ins_node,
                                            inner_ifs=[],
                                            operation=None):
        '''
        Create attribute configuration to master interface, and return the node which has been created
        '''
        ifs_node = self._set_xml_tag(nw_ins_node, "interfaces")
        for inner_if in inner_ifs:
            if_name = inner_if["IF-NAME"]
            vlan_id = inner_if["INNER-IF-VLAN"]
            self._set_interface_of_assignment_to_master_interface(
                ifs_node, if_name, operation=operation)
            self._set_interface_of_assignment_to_master_interface(
                ifs_node, if_name, vlan_id, operation)
        return ifs_node

    def _set_interface_of_assignment_to_master_interface(
            self, ifs_node, if_name, vlan_id=None, operation=None):
        '''
        Create attribute IF configuraiton to master interface, and return the node which has been created
        '''
        attr, attr_val = self._get_attr_from_operation(operation)
        set_id = (if_name if vlan_id is None
                  else "{0}.{1}".format(if_name, vlan_id))
        if_node = self._set_xml_tag(ifs_node, "interface", attr, attr_val)
        self._set_xml_tag(if_node, "id", text=set_id)
        if operation != self._DELETE:
            conf_node = self._set_xml_tag(if_node, "config")
            self._set_xml_tag(conf_node, "id", text=set_id)
            if vlan_id is not None:
                self._set_xml_tag(conf_node, "interface", text=if_name)
                self._set_xml_tag(conf_node, "subinterface", text=vlan_id)

    @decorater_log
    def _set_protocols_node(self, nw_ins_node):
        '''
        Create protocols node and return the node which has been created
        '''
        return self._set_xml_tag(nw_ins_node, "protocols")

    @decorater_log
    def _set_ospf_protocol_node(self,
                                protocols_node,
                                area_id=None,
                                inner_ifs=[],
                                operation=None):
        '''
        Create protocols node and return the node which has been created
        '''
        protocol_node = self._set_xml_tag(protocols_node, "protocol")
        self._set_xml_tag(protocol_node,
                          "identifier",
                          self._ope_xmlns_oc_pol_types,
                          "http://openconfig.net/yang/policy-types",
                          "oc-pol-types:OSPF")
        self._set_xml_tag(protocol_node, "name", text="MSF-infra")
        ospf_node = self._set_xml_tag(protocol_node, "ospfv2")
        areas_node = self._set_xml_tag(ospf_node, "areas")
        area_node = self._set_xml_tag(areas_node, "area")
        set_area_id = "0.0.0.{0}".format(area_id)
        self._set_xml_tag(area_node, "identifier", text=set_area_id)
        if inner_ifs:
            ifs_node = self._set_xml_tag(area_node, "interfaces")
            for inner_if in inner_ifs:
                if_name = inner_if["IF-NAME"]
                vlan_id = inner_if["INNER-IF-VLAN"]
                cost = None
                if operation != self._DELETE:
                    cost = inner_if["OSPF-METRIC"]
                self._set_ospf_internal_link(ifs_node,
                                             if_name,
                                             vlan_id,
                                             cost,
                                             operation)

    @decorater_log
    def _set_ospf_internal_link(self,
                                ifs_node,
                                if_name,
                                vlan_id=None,
                                cost=None,
                                operation=None):
        '''
        Create IF configuration of ospf and return the node which has been created
        '''
        set_id = "{0}.{1}".format(if_name, vlan_id)
        if_node = self._set_xml_tag(ifs_node, "interface")
        self._set_xml_tag(if_node, "id", text=set_id)
        if operation == self._DELETE:
            if_node.set(self._ATRI_OPE, self._DELETE)
        else:
            conf_node = self._set_xml_tag(if_node, "config")
            self._set_xml_tag(conf_node, "id", text=set_id)
            mtr_node = self._set_xml_tag(conf_node, "metric", text=cost)
            if operation == self._REPLACE:
                mtr_node.set(self._ATRI_OPE, self._REPLACE)
            else:
                self._set_xml_tag(conf_node, "passive", text="false")
                self._set_xml_tag(conf_node,
                                  "network-type",
                                  self._ope_xmlns_oc_ospf_types,
                                  "http://openconfig.net/yang/ospf-types",
                                  "oc-ospf-types:POINT_TO_POINT_NETWORK")
                ref_node = self._set_xml_tag(if_node, "interface-ref")
                conf_node = self._set_xml_tag(ref_node, "config")
                self._set_xml_tag(conf_node, "interface", text=if_name)
                self._set_xml_tag(conf_node, "subinterface", text=vlan_id)
                timers_node = self._set_xml_tag(if_node, "timers")
                conf_node = self._set_xml_tag(timers_node, "config")
                self._set_xml_tag(conf_node, "dead-interval", text=40)
                self._set_xml_tag(conf_node, "hello-interval", text=10)
        return if_node
