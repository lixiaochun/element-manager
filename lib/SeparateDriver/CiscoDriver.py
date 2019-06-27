# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: CiscoDriver.py
'''
Individual section on deriver (driver from Cisco).
'''
import json
from lxml import etree
from EmSeparateDriver import EmSeparateDriver
from EmCommonLog import decorater_log
from EmCommonLog import decorater_log_in_out
import GlobalModule
from codecs import BOM_UTF8
import os
import re
import ipaddress


class CiscoDriver(EmSeparateDriver):
    '''
    Cisco driver class(take over from driver individual section class).
    '''

    __cisco_proper_config = {}
    __cisco_trk_obj_config = {}

    _XC_ATRI_OPE = "xc:operation"
    _XC_NS = "xc"
    _XC_NS_MAP = "urn:ietf:params:xml:ns:netconf:base:1.0"
    _REP_ATRI_XMLNS = "xmlns_idx"
    _IDX_ATRI_XMLNS = "xmlns:idx"

    @decorater_log_in_out
    def connect_device(self,
                       device_name, device_info, service_type, order_type):
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
            Protocol processing section responce :
                int (1:Normal, 2:Capability abnormal, 3:No response)
        '''
        tmp_device_info = None
        if device_info is not None:
            tmp_json = json.loads(device_info)
            if tmp_json.get("device_info") is not None:
                tmp_json["device_info"]["port_number"] = \
                    self._cisco_port_number
            tmp_device_info = json.dumps(tmp_json)
        return self.as_super.connect_device(device_name,
                                            tmp_device_info,
                                            service_type,
                                            order_type)

    @decorater_log
    def _get_cisco_config(self):
        '''
        Read config from conf_separate_driver_cisco.conf.
        '''
        splitter_conf = '='
        config_path = os.path.join(GlobalModule.EM_CONF_PATH,
                                   'conf_separate_driver_cisco.conf')
        try:
            with open(config_path, 'r') as open_file:
                conf_list = open_file.readlines()    
        except IOError:
            raise

        tmp_list = []
        for value in conf_list:
            if not(value.startswith('#')) and splitter_conf in value:
                tmp_line = value.strip()
                tmp_line = tmp_line.replace(BOM_UTF8, '')
                tmp_list.append(tmp_line)

        conf_dict_owner = {}  
        conf_dict_track_obj = {}  
        tmp_value_list = []   
        index = 0
        for item in tmp_list:
            tmp = item.split(splitter_conf)[1]
            tmp_value_list.append(tmp)
        max_index = len(tmp_value_list) - 1
        while index < max_index:
            tmp_key = tmp_value_list[index]
            tmp_value = tmp_value_list[index + 1]
            conf_dict_owner[tmp_key] = tmp_value
            tmp_value = tmp_value_list[index + 2]
            conf_dict_track_obj[tmp_key] = tmp_value
            index += 3
        return conf_dict_owner, conf_dict_track_obj

    @decorater_log
    def __init__(self):
        '''
        Constructor.
        '''
        self.as_super = super(CiscoDriver, self)
        self.as_super.__init__()
        self._cisco_port_number = 22
        self._ATRI_OPE = "xc_operation"

        self._base_breakout_if_prefixs = []

        if not CiscoDriver.__cisco_proper_config:
            tmp_tuble = self._get_cisco_config()
            CiscoDriver.__cisco_proper_config = tmp_tuble[0]
            CiscoDriver.__cisco_trk_obj_config = tmp_tuble[1]
            self.common_util_log.logging(
                "", self.log_level_debug,
                "Update proper config:", CiscoDriver.__cisco_proper_config)
        self.list_enable_service = [self.name_spine,
                                    self.name_leaf,
                                    self.name_l3_slice,
                                    self.name_celag,
                                    self.name_internal_link,
                                    self.name_breakout,
                                    self.name_recover_node,
                                    self.name_recover_service,
                                    self.name_if_condition,
                                    ]
        self.get_config_message = {
            self.name_l3_slice: (
                '<filter>' +
                '<vrfs></vrfs>' +
                '<interface-configurations></interface-configurations>' +
                '<router-static></router-static>' +
                '<ospf></ospf>' +
                '<vrrp></vrrp>' +
                '<bgp></bgp>' +
                '</filter>'
            ),
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
            message_type ; Send type
            send_message : Send message
        Return value.
            Processed result ; Boolean （Result of send_control_signal )
            Message ; str （Result of send_control_signal )
        '''
        if (message_type == "edit-config" and
                service_type in (self.name_celag, self.name_internal_link) and
                operation == "delete" and send_message is not None):
            send_xml = etree.fromstring(send_message)
            is_one_node = bool(len(send_xml) == 1)
            lag_mem = self._gen_top_node_edit_config()
            lag_mem.append(send_xml[-1])
            send_mes_1_be = self._replace_xc_delete(etree.tostring(lag_mem))
            send_mes_1 = self._replace_xmlns_idx(send_mes_1_be)
            is_result, message = \
                self.as_super._send_control_signal(device_name,
                                                   message_type,
                                                   send_mes_1)
            if not is_result:
                return False, None
            elif is_one_node:
                return is_result, message
            else:
                send_mes_2_be = self._replace_xc_delete(
                    etree.tostring(send_xml))
                send_mes_2 = self._replace_xmlns_idx(
                    send_mes_2_be)
                return (self.as_super.
                        _send_control_signal(device_name,
                                             message_type,
                                             send_mes_2))
        else:
            tmp_send_be = self._replace_xc_delete(send_message)
            tmp_send = self._replace_xmlns_idx(tmp_send_be)
            is_result, message = (self.as_super.
                                  _send_control_signal(device_name,
                                                       message_type,
                                                       tmp_send))
            if (message_type == "confirmed-commit" and
                    not is_result and isinstance(message, str) and
                    self.re_rpc_error.search(message) is not None and
                    "ME_BACKEND_ERROR_OP_FAILED" in message):
                is_result = True
            return is_result, message

    @decorater_log
    def _gen_message_child(self,
                           device_info,
                           ec_message,
                           operation,
                           method_fix_message_gen,
                           method_variable_message_gen,
                           top_tag="config"):
        '''
        Method to create each message.
            Called out when service type is judged and
            message writing is created for each message.
        Parameter:
            device_info : DB information
            ec_message : EC message
            operation : Order type(only whether Delete or not)
            method_fix_message_gen : Method to create fixed message
            method_variable_message_gen : Method to create variable message
        Return value.
            Message creation result: Boolean
            Created message: str
        '''
        self.common_util_log.logging(None,
                                     self.log_level_debug,
                                     "ec_mes = %s" % (ec_message,),
                                     __name__)
        self.common_util_log.logging(None,
                                     self.log_level_debug,
                                     "device_info = %s" % (device_info,),
                                     __name__)
        return_val = True
        xml_obj = self._gen_top_node_edit_config()
        return_val = return_val and method_fix_message_gen(xml_obj, operation)
        return_val = return_val and method_variable_message_gen(
            xml_obj, device_info, ec_message, operation)
        return_string = etree.tostring(xml_obj)
        return return_val, return_string

    @decorater_log
    def _replace_xc_delete(self, xml_str):
        return (xml_str.replace(self._ATRI_OPE, self._XC_ATRI_OPE)
                if isinstance(xml_str, str) else xml_str)

    @decorater_log
    def _replace_xmlns_idx(self, xml_str):
        return (xml_str.replace(self._REP_ATRI_XMLNS, self._IDX_ATRI_XMLNS)
                if isinstance(xml_str, str) else xml_str)

    @decorater_log
    def _gen_top_node_edit_config(self):
        xml_str = '<%(ns)s:%(tag)s xmlns:%(ns)s="%(nsmap)s"></%(ns)s:%(tag)s>'
        str_map = {"ns": self._XC_NS,
                   "tag": self._send_message_top_tag,
                   "nsmap": self._XC_NS_MAP}
        return etree.fromstring(xml_str % str_map)


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

        self._set_ospf_infra_plane(xml_obj, service=self.name_spine)
        self._set_infra_ldp(xml_obj, service=self.name_spine)

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
            Creation result : Boolean
        '''

        self._set_ospf_infra_plane(xml_obj, service=self.name_leaf)
        self._set_mp_bgp(xml_obj)
        self._set_infra_ldp(xml_obj, service=self.name_leaf)

        return True

    @decorater_log
    def _gen_l2_slice_fix_message(self, xml_obj, operation):
        '''
        Fixed value to create message (L2Slice) for Netconf.
        Not applicable to the L2Slice add/delete function of
        the Cisco's device.
        Parameter:
            xml_obj : xml object
            operation : Designate "delete" when deleting.
        Return value.
            Creation result :
                False(Not applicable to the L2Slice add/delete
                      function of the Cisco's device.)
        '''
        self.common_util_log.logging(
            " ",
            self.log_level_error,
            self.Logmessage["Call_NG_Method"] %
            ("_gen_l2_slice_fix_message"),
            __name__)
        return False

    @decorater_log
    def _gen_l3_slice_fix_message(self, xml_obj, operation):
        '''
        Fixed value to create message (L3Slice) for Netconf.
            Called out when creating message for L3Slice.
        Parameter:
            xml_obj : xml object
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean
        '''
        if operation == self._DELETE:
            self._gen_l3_slice_delete_fix_message(xml_obj)
        elif operation == self._REPLACE:
            self._gen_l3_slice_replace_fix_message(xml_obj)
        else:
            self._gen_l3_slice_merge_fix_message(xml_obj)
        return True

    @decorater_log
    def _gen_l3_slice_merge_fix_message(self, xml_obj):
        '''
        Fixed value to create message (add L3Slice) for Netconf.
            Called out when adding L3Slice.
        Parameter:
            xml_obj : xml object
        Return value.
            Creation result : Boolean
        '''
        self._set_merge_slice_vrf(xml_obj)

        self._set_if_confs(xml_obj)

        self._set_router_static_common(xml_obj)

        self._set_slice_bgp(xml_obj)

        self._set_slice_vrrp(xml_obj)

        return True

    @decorater_log
    def _gen_l3_slice_replace_fix_message(self, xml_obj):
        '''
        Fixed value to create message (update L3Slice) for Netconf.
            Called out when updating L3Slice (staticCP add/delete).
        Parameter:
            xml_obj : xml object
        Return value.
            Creation result : Boolean
        '''

        return True

    @decorater_log
    def _gen_l3_slice_delete_fix_message(self, xml_obj):
        '''
        Fixed value to create message (delete L3Slice) for Netconf.
            Called out when deleting L3Slice.
        Parameter:
            xml_obj : xml object
        Return value.
            Creation result : Boolean
        '''
        node_1 = self._set_xml_tag(xml_obj,
                                   "vrfs",
                                   "xmlns",
                                   "http://cisco.com/ns/yang/" +
                                   "Cisco-IOS-XR-infra-rsi-cfg",
                                   None)
        node_2 = self._set_xml_tag(
            node_1, "vrf", self._ATRI_OPE, self._DELETE, None)
        self._set_xml_tag(node_2, "vrf-name")

        node_1 = self._set_xml_tag(xml_obj,
                                   "interface-configurations",
                                   "xmlns",
                                   "http://cisco.com/ns/yang/" +
                                   "Cisco-IOS-XR-ifmgr-cfg",
                                   None)

        node_1 = self._set_xml_tag(xml_obj,
                                   "router-static",
                                   "xmlns",
                                   "http://cisco.com/ns/yang/" +
                                   "Cisco-IOS-XR-ip-static-cfg",
                                   None)
        node_2 = self._set_xml_tag(node_1, "vrfs")
        node_3 = self._set_xml_tag(node_2, "vrf")
        self._set_xml_tag(node_3, "vrf-name")
        node_4 = self._set_xml_tag(node_3, "address-family")
        node_5 = self._set_xml_tag(node_4, "vrfipv4")
        node_6 = self._set_xml_tag(node_5, "vrf-unicast")
        self._set_xml_tag(node_6, "vrf-prefixes")

        node_1 = self._set_xml_tag(xml_obj,
                                   "bgp",
                                   "xmlns",
                                   "http://cisco.com/ns/yang/" +
                                   "Cisco-IOS-XR-ipv4-bgp-cfg",
                                   None)
        node_2 = self._set_xml_tag(node_1, "instance")
        self._set_xml_tag(node_2, "instance-name", None, None, "default")
        node_3 = self._set_xml_tag(node_2, "instance-as")
        self._set_xml_tag(node_3, "as", None, None, "0")
        node_4 = self._set_xml_tag(node_3, "four-byte-as")
        self._set_xml_tag(node_4, "as")
        self._set_xml_tag(node_4, "bgp-running")
        node_5 = self._set_xml_tag(node_4, "vrfs")
        node_6 = self._set_xml_tag(node_5, "vrf")
        self._set_xml_tag(node_6, "vrf-name")
        node_7 = self._set_xml_tag(node_6, "vrf-neighbors")

        node_1 = self._set_xml_tag(xml_obj,
                                   "vrrp",
                                   "xmlns",
                                   "http://cisco.com/ns/yang/" +
                                   "Cisco-IOS-XR-ipv4-vrrp-cfg",
                                   None)
        node_2 = self._set_xml_tag(node_1, "interfaces")
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
            Creation result : Boolean
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
    def _gen_breakout_fix_message(self, xml_obj, operation):
        '''
        Fixed value to create message (breakout) for Netconf.
            Called out when creating message for breakout.
        Parameter:
            xml_obj : xml object
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean (Write properly using override method.)
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
            Creation result : Boolean (Write properly using override method. )
        '''
        return False


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
            Creation result : Boolean
        '''
        device_mes = ec_message.get("device", {})
        device_name = device_mes.get("name")

        try:
            dev_reg_info = self._get_device_from_ec(device_mes,
                                                    service=self.name_spine)
            phy_ifs, lag_ifs, lag_mem_ifs, inner_if_names = \
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
            return False

        self._set_host_name(xml_obj, dev_reg_info["DEVICE-NAME"])

        if_node = self._set_if_confs(xml_obj)
        self._set_loopback_address(if_node,
                                   dev_reg_info["LB-IF-ADDR"],
                                   dev_reg_info["LB-IF-PREFIX"])

        self._set_breakout_interfaces(if_node, breakout_ifs)

        self._set_internal_links(if_node, phy_ifs, lag_ifs, lag_mem_ifs)

        self._set_xml_tag_variable(xml_obj,
                                   "router-id",
                                   dev_reg_info["LB-IF-ADDR"],
                                   "ospf",
                                   "processes",
                                   "process",
                                   "default-vrf")

        node_5 = self._find_xml_node(xml_obj,
                                     "ospf",
                                     "processes",
                                     "process",
                                     "default-vrf",
                                     "area-addresses")
        self._set_ospf_area_data(node_5,
                                 dev_reg_info["OSPF-AREA-ID"],
                                 inner_if_names,
                                 is_lb=True)

        self._set_xml_tag_variable(xml_obj,
                                   "router-id",
                                   dev_reg_info["LB-IF-ADDR"],
                                   "mpls-ldp",
                                   "default-vrf",
                                   "global")

        self._set_ldp_inner_if(xml_obj, inner_if_names)

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
            Creation result : Boolean
        '''
        device_mes = ec_message.get("device", {})
        device_name = device_mes.get("name")

        try:
            dev_reg_info = self._get_device_from_ec(device_mes,
                                                    service=self.name_leaf)
            tmp_dev, l3v_lbb_infos = self._get_leaf_vpn_from_ec(device_mes)
            dev_reg_info.update(tmp_dev)
            phy_ifs, lag_ifs, lag_mem_ifs, inner_if_names = \
                self._get_internal_link_from_ec(device_mes,
                                                service=self.name_leaf)
            breakout_ifs = self._get_breakout_from_ec(device_mes)
            self._check_breakout_if_name(breakout_ifs)
        except Exception as ex:
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "ERROR : message = %s / Exception: %s" % (ec_message, ex),
                __name__)
            return False

        self._set_host_name(xml_obj, dev_reg_info["DEVICE-NAME"])

        if_node = self._set_if_confs(xml_obj)
        self._set_loopback_address(if_node,
                                   dev_reg_info["LB-IF-ADDR"],
                                   dev_reg_info["LB-IF-PREFIX"])

        self._set_breakout_interfaces(if_node, breakout_ifs)

        self._set_internal_links(if_node, phy_ifs, lag_ifs, lag_mem_ifs)

        self._set_xml_tag_variable(xml_obj,
                                   "router-id",
                                   dev_reg_info["LB-IF-ADDR"],
                                   "ospf",
                                   "processes",
                                   "process",
                                   "default-vrf")

        node_5 = self._find_xml_node(xml_obj,
                                     "ospf",
                                     "processes",
                                     "process",
                                     "default-vrf",
                                     "area-addresses")
        self._set_ospf_area_data(node_5,
                                 dev_reg_info["OSPF-AREA-ID"],
                                 inner_if_names,
                                 is_lb=True)

        self._set_xml_tag_variable(xml_obj,
                                   "as",
                                   str(dev_reg_info["AS-NUMBER"]),
                                   "bgp",
                                   "instance",
                                   "instance-as",
                                   "four-byte-as")

        self._set_xml_tag_variable(xml_obj,
                                   "router-id",
                                   dev_reg_info["LB-IF-ADDR"],
                                   "bgp",
                                   "instance",
                                   "instance-as",
                                   "four-byte-as",
                                   "default-vrf",
                                   "global")

        node_7 = self._find_xml_node(xml_obj,
                                     "bgp",
                                     "instance",
                                     "instance-as",
                                     "four-byte-as",
                                     "default-vrf",
                                     "bgp-entity",
                                     "neighbors")
        for l3v_lbb in l3v_lbb_infos:
            self._set_mp_bgp_neighbor(node_7,
                                      l3v_lbb["RR-ADDR"],
                                      dev_reg_info["AS-NUMBER"])

        self._set_xml_tag_variable(xml_obj,
                                   "router-id",
                                   dev_reg_info["LB-IF-ADDR"],
                                   "mpls-ldp",
                                   "default-vrf",
                                   "global")

        self._set_ldp_inner_if(xml_obj, inner_if_names)

        return True

    @decorater_log
    def _gen_l2_slice_variable_message(self,
                                       xml_obj,
                                       device_info,
                                       ec_message,
                                       operation):
        '''

        Variable value to create message (L2Slice) for Netconf.
            Not applicable to the L2Slice
            add/delete function of the Cisco's device.
        Parameter:
            xml_obj : xml object
            device_info : Device information
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : False (Not applicable to
                the L2Slice add/delete function of the Cisco's device.)
        '''
        self.common_util_log.logging(
            " ",
            self.log_level_error,
            self.Logmessage["Call_NG_Method"] %
            ("_gen_l2_slice_variable_message"),
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
            Called out when creating message for L3Slice.
            (After fixed message has been created.)
        Parameter:
            xml_obj : xml object
            device_info : Device information
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean
        '''
        return_val = False
        if operation == self._DELETE:
            return_val = self._gen_del_l3_slice_variable_message(
                xml_obj, device_info, ec_message)
        elif operation == self._REPLACE:
            return_val = self._gen_replace_l3_slice_variable_message(
                xml_obj, device_info, ec_message)
        else:
            return_val = self._gen_add_l3_slice_variable_message(
                xml_obj, device_info, ec_message)
        return return_val

    @staticmethod
    @decorater_log
    def _set_vlan_if_name(if_name, vlan_id=None):
        if vlan_id is None:
            return if_name
        elif str(vlan_id) == "0":
            return if_name
        else:
            return if_name + "." + str(vlan_id)

    @decorater_log
    def _gen_add_l3_slice_variable_message(self,
                                           xml_obj,
                                           device_info,
                                           ec_message):
        '''
        Variable value to create message (create L3Slice) for Netconf.
            Called out when adding CeLag.
        Parameter:
            xml_obj : xml object
            device_info : Device information
            ec_message : EC message
        Return value.
            Creation result : Boolean
        '''
        is_variable_value = True

        tmp_ec = ec_message["device-leaf"]["vrf"]

        vrf_dtl_info = {}
        vrf_dtl_info["L3-VRF-NAME"] = tmp_ec.get("vrf-name")
        vrf_dtl_info["L3-VRF-RT"] = tmp_ec.get("rt")
        vrf_dtl_info["L3-VRF-RD"] = tmp_ec.get("rd")
        vrf_dtl_info["L3-VRF-ROUTER-ID"] = tmp_ec.get("router-id")

        for chk_item in vrf_dtl_info.values():
            if chk_item is None:
                is_variable_value = False
                break

        is_vrrp = False
        is_bgp = False
        is_static = False
        new_slice = True
        new_bgp = True

        cp_count = 0
        if device_info.get("cp") is not None:
            for cp in device_info["cp"]:
                cp_count += 1
                if cp["slice_name"] == ec_message["device-leaf"]["slice_name"]:
                    new_slice = False

        if device_info.get("bgp_detail") is not None:
            for bgp in device_info["bgp_detail"]:
                if (bgp["slice_name"] ==
                        ec_message["device-leaf"]["slice_name"]):
                    new_bgp = False

        cp_infos = []
        for cp in ec_message["device-leaf"]["cp"]:
            if cp.get("name") is None \
                    or cp["ce-interface"].get("address") is None \
                    or cp["ce-interface"].get("prefix") is None \
                    or cp.get("vlan-id") is None:
                is_variable_value = False
                break

            tmp = \
                {"L3-CE-IF-NAME": cp["name"],
                 "L3-CE-IF-MTU": cp["ce-interface"].get("mtu"),
                 "L3-CE-IF-ADDR": cp["ce-interface"]["address"],
                 "L3-CE-IF-PREFIX": cp["ce-interface"]["prefix"],
                 "L3-CE-IF-VLAN": str(cp["vlan-id"])}
            if "vrrp" in cp:
                is_vrrp = True
                tmp_list = []

                for track in (cp["vrrp"]["track"]["interface"]
                              if cp["vrrp"].get("track") and
                              cp["vrrp"]["track"].get("interface")
                              else []):
                    if track.get("name") is None:
                        is_variable_value = False
                        break

                    tmp_list.append(
                        {"L3-VRRP-VIRT-IF": track["name"]})
                if cp["vrrp"].get("group-id") is None \
                        or cp["vrrp"].get("virtual-address") is None \
                        or cp["vrrp"].get("priority") is None:
                    is_variable_value = False
                    break

                tmp["VRRP"] = {
                    "L3-VRRP-GROUP-ID": cp["vrrp"]["group-id"],
                    "L3-VRRP-VIRT-ADDR": cp["vrrp"]["virtual-address"],
                    "L3-VRRP-VIRT-PRI":
                    cp["vrrp"]["priority"],
                    "L3-VRRP-VIRT-IF": cp["vrrp"]["priority"],
                    "track": tmp_list}
            if "bgp" in cp:
                is_bgp = True
                if cp["bgp"].get("remote-as-number") is None \
                        or cp["bgp"].get("remote-address") is None:
                    is_variable_value = False
                    break

                tmp["BGP"] = {"L3-BGP-PEER-AS":
                              cp["bgp"]["remote-as-number"],
                              "L3-BGP-RADD": cp["bgp"]["remote-address"],
                              "L3-BGP-MASTER": cp["bgp"].get("master")}
            if "static" in cp:
                is_static = True
                tmp_list = []
                for route in cp["static"].get("route", {}):
                    if route.get("address") is None \
                            or route.get("prefix") is None \
                            or route.get("nexthop") is None:
                        is_variable_value = False
                        break
                    tmp_list.append(
                        {"L3-STATIC-ROUTE-ADD": route["address"],
                         "L3-STATIC-ROUTE-PREFIX": route["prefix"],
                         "L3-STATIC-ROUTE-NEXT": route["nexthop"]})
                tmp["STATIC"] = tmp_list
            cp_infos.append(tmp)

        if device_info["device"].get("as_number") is None:
            is_variable_value = False

        lf_as_number = device_info["device"].get("as_number")

        db_base_if = []
        for cp in device_info.get("cp", []):
            if (cp.get("vlan", {}).get("vlan_id", 0) != 0 and "Bundle-Ether"
                    not in cp.get("if_name", "")):
                db_base_if.append(cp.get("if_name"))

        if is_variable_value is False:
            return False

        if new_slice is not True:
            xml_obj.remove(xml_obj.find("vrfs"))
        else:
            self._set_xml_tag_variable(xml_obj,
                                       "vrf-name",
                                       vrf_dtl_info["L3-VRF-NAME"],
                                       "vrfs",
                                       "vrf")
            node_1 = self._find_xml_node(xml_obj,
                                         "vrfs",
                                         "vrf",
                                         "afs",
                                         "af",
                                         "bgp")
            self._set_xml_tag_variable(node_1,
                                       "as",
                                       vrf_dtl_info["L3-VRF-RT"].split(":")[1],
                                       "import-route-targets",
                                       "route-targets",
                                       "route-target",
                                       "as-or-four-byte-as")
            self._set_xml_tag_variable(node_1,
                                       "as-index",
                                       vrf_dtl_info["L3-VRF-RT"].split(":")[2],
                                       "import-route-targets",
                                       "route-targets",
                                       "route-target",
                                       "as-or-four-byte-as")
            self._set_xml_tag_variable(node_1,
                                       "as",
                                       vrf_dtl_info["L3-VRF-RT"].split(":")[1],
                                       "export-route-targets",
                                       "route-targets",
                                       "route-target",
                                       "as-or-four-byte-as")
            self._set_xml_tag_variable(node_1,
                                       "as-index",
                                       vrf_dtl_info["L3-VRF-RT"].split(":")[2],
                                       "export-route-targets",
                                       "route-targets",
                                       "route-target",
                                       "as-or-four-byte-as")
        node_1 = xml_obj.find("interface-configurations")
        for cp in cp_infos:
            if "Bundle-Ether" in cp["L3-CE-IF-NAME"] \
                    and cp["L3-CE-IF-VLAN"] == "0":
                node_2 = self._set_xml_tag(node_1, "interface-configuration")
                self._set_xml_tag(node_2, "active", None, None, "act")
                self._set_xml_tag(
                    node_2, "interface-name", None, None, cp["L3-CE-IF-NAME"])
                self._set_xml_tag(node_2, "interface-virtual")
                if cp["L3-CE-IF-MTU"] is not None:
                    node_3 = self._set_xml_tag(node_2, "mtus")
                    node_4 = self._set_xml_tag(node_3, "mtu")
                    self._set_xml_tag(
                        node_4, "owner", None, None, "etherbundle")
                    self._set_xml_tag(node_4,
                                      "mtu",
                                      None,
                                      None,
                                      int(cp["L3-CE-IF-MTU"]) + 14)
                node_3 = self._set_xml_tag(node_2,
                                           "qos",
                                           "xmlns",
                                           "http://cisco.com/ns/yang/" +
                                           "Cisco-IOS-XR-qos-ma-cfg",
                                           None)
                node_4 = self._set_xml_tag(node_3, "input")
                node_5 = self._set_xml_tag(node_4, "service-policy")
                self._set_xml_tag(node_5,
                                  "service-policy-name",
                                  None,
                                  None,
                                  "in_ce_vpnbulk_be_policy")
                node_4 = self._set_xml_tag(node_3, "output")
                node_5 = self._set_xml_tag(node_4, "service-policy")
                self._set_xml_tag(node_5,
                                  "service-policy-name",
                                  None,
                                  None,
                                  "out_ce_pt2_policy")

                node_3 = self._set_xml_tag(node_2,
                                           "vrf",
                                           "xmlns",
                                           "http://cisco.com/ns/yang/" +
                                           "Cisco-IOS-XR-infra-rsi-cfg",
                                           vrf_dtl_info["L3-VRF-NAME"])
                node_3 = self._set_xml_tag(node_2,
                                           "ipv4-network",
                                           "xmlns",
                                           "http://cisco.com/ns/yang/" +
                                           "Cisco-IOS-XR-ipv4-io-cfg",
                                           None)
                node_4 = self._set_xml_tag(node_3, "addresses")
                node_5 = self._set_xml_tag(node_4, "primary")
                self._set_xml_tag(
                    node_5, "address", None, None, cp["L3-CE-IF-ADDR"])
                self._set_xml_tag(node_5,
                                  "netmask",
                                  None,
                                  None,
                                  self._conversion_cidr2mask(
                                      cp["L3-CE-IF-PREFIX"]))
            elif "Bundle-Ether" not in cp["L3-CE-IF-NAME"] \
                    and cp["L3-CE-IF-VLAN"] == "0":
                node_2 = self._set_xml_tag(node_1, "interface-configuration")
                self._set_xml_tag(node_2, "active", None, None, "act")
                self._set_xml_tag(
                    node_2, "interface-name", None, None, cp["L3-CE-IF-NAME"])
                if cp["L3-CE-IF-MTU"] is not None:
                    node_3 = self._set_xml_tag(node_2, "mtus")
                    node_4 = self._set_xml_tag(node_3, "mtu")
                    self._set_xml_tag(node_4,
                                      "owner",
                                      None,
                                      None,
                                      self._get_owner(cp["L3-CE-IF-NAME"]))
                    self._set_xml_tag(node_4,
                                      "mtu",
                                      None,
                                      None,
                                      int(cp["L3-CE-IF-MTU"]) + 14)
                node_3 = self._set_xml_tag(node_2,
                                           "qos",
                                           "xmlns",
                                           "http://cisco.com/ns/yang/" +
                                           "Cisco-IOS-XR-qos-ma-cfg",
                                           None)
                node_4 = self._set_xml_tag(node_3, "input")
                node_5 = self._set_xml_tag(node_4, "service-policy")
                self._set_xml_tag(node_5,
                                  "service-policy-name",
                                  None,
                                  None,
                                  "in_ce_vpnbulk_be_policy")

                node_4 = self._set_xml_tag(node_3, "output")
                node_5 = self._set_xml_tag(node_4, "service-policy")
                self._set_xml_tag(node_5,
                                  "service-policy-name",
                                  None,
                                  None,
                                  "out_ce_pt2_policy")

                node_3 = self._set_xml_tag(node_2,
                                           "vrf",
                                           "xmlns",
                                           "http://cisco.com/ns/yang/" +
                                           "Cisco-IOS-XR-infra-rsi-cfg",
                                           vrf_dtl_info["L3-VRF-NAME"])
                node_3 = self._set_xml_tag(node_2,
                                           "ipv4-network",
                                           "xmlns",
                                           "http://cisco.com/ns/yang/" +
                                           "Cisco-IOS-XR-ipv4-io-cfg",
                                           None)
                node_4 = self._set_xml_tag(node_3, "addresses")
                node_5 = self._set_xml_tag(node_4, "primary")
                self._set_xml_tag(
                    node_5, "address", None, None, cp["L3-CE-IF-ADDR"])
                self._set_xml_tag(node_5,
                                  "netmask",
                                  None,
                                  None,
                                  self._conversion_cidr2mask(
                                      cp["L3-CE-IF-PREFIX"]))
                self._set_xml_tag(node_2,
                                  "shutdown",
                                  self._ATRI_OPE,
                                  self._DELETE,
                                  None)
            elif cp["L3-CE-IF-VLAN"] != "0":
                node_2 = self._set_xml_tag(node_1, "interface-configuration")
                self._set_xml_tag(node_2, "active", None, None, "act")
                self._set_xml_tag(
                    node_2, "interface-name", None, None, cp["L3-CE-IF-NAME"])
                if "Bundle-Ether" in cp["L3-CE-IF-NAME"]:
                    self._set_xml_tag(node_2, "interface-virtual")
                if cp["L3-CE-IF-MTU"] is not None:
                    node_3 = self._set_xml_tag(node_2, "mtus")
                    node_4 = self._set_xml_tag(node_3, "mtu")
                    if "Bundle-Ether" in cp["L3-CE-IF-NAME"]:
                        self._set_xml_tag(
                            node_4, "owner", None, None, "etherbundle")
                    else:
                        self._set_xml_tag(node_4,
                                          "owner",
                                          None,
                                          None,
                                          self._get_owner(cp["L3-CE-IF-NAME"]))
                    self._set_xml_tag(node_4,
                                      "mtu",
                                      None,
                                      None,
                                      "4114")
                node_3 = self._set_xml_tag(node_2,
                                           "qos",
                                           "xmlns",
                                           "http://cisco.com/ns/yang/" +
                                           "Cisco-IOS-XR-qos-ma-cfg",
                                           None)
                node_4 = self._set_xml_tag(node_3, "input")
                node_5 = self._set_xml_tag(node_4, "service-policy")
                self._set_xml_tag(node_5,
                                  "service-policy-name",
                                  None,
                                  None,
                                  "in_ce_vpnbulk_be_policy")

                node_4 = self._set_xml_tag(node_3, "output")
                node_5 = self._set_xml_tag(node_4, "service-policy")
                self._set_xml_tag(node_5,
                                  "service-policy-name",
                                  None,
                                  None,
                                  "out_ce_pt2_policy")

                if (cp["L3-CE-IF-NAME"] not in db_base_if and "Bundle-Ether"
                        not in cp["L3-CE-IF-NAME"]):
                    self._set_xml_tag(node_2,
                                      "shutdown",
                                      self._ATRI_OPE,
                                      self._DELETE,
                                      None)
                    db_base_if.append(cp["L3-CE-IF-NAME"])

                node_2 = self._set_xml_tag(node_1, "interface-configuration")
                self._set_xml_tag(node_2, "active", None, None, "act")
                self._set_xml_tag(node_2,
                                  "interface-name",
                                  None,
                                  None,
                                  cp["L3-CE-IF-NAME"] + "." +
                                  cp["L3-CE-IF-VLAN"])
                self._set_xml_tag(node_2,
                                  "interface-mode-non-physical",
                                  None,
                                  None,
                                  "default")
                if cp["L3-CE-IF-MTU"] is not None:
                    node_3 = self._set_xml_tag(node_2, "mtus")
                    node_4 = self._set_xml_tag(node_3, "mtu")
                    self._set_xml_tag(
                        node_4, "owner", None, None, "sub_vlan")
                    self._set_xml_tag(node_4,
                                      "mtu",
                                      None,
                                      None,
                                      int(cp["L3-CE-IF-MTU"]) + 18)
                node_3 = self._set_xml_tag(node_2,
                                           "vrf",
                                           "xmlns",
                                           "http://cisco.com/ns/yang/" +
                                           "Cisco-IOS-XR-infra-rsi-cfg",
                                           vrf_dtl_info["L3-VRF-NAME"])
                node_3 = self._set_xml_tag(node_2,
                                           "ipv4-network",
                                           "xmlns",
                                           "http://cisco.com/ns/yang/" +
                                           "Cisco-IOS-XR-ipv4-io-cfg",
                                           None)
                node_4 = self._set_xml_tag(node_3, "addresses")
                node_5 = self._set_xml_tag(node_4, "primary")
                self._set_xml_tag(
                    node_5, "address", None, None, cp["L3-CE-IF-ADDR"])
                self._set_xml_tag(node_5,
                                  "netmask",
                                  None,
                                  None,
                                  self._conversion_cidr2mask(
                                      cp["L3-CE-IF-PREFIX"]))
                node_3 = self._set_xml_tag(node_2,
                                           "vlan-sub-configuration",
                                           "xmlns",
                                           "http://cisco.com/ns/yang/" +
                                           "Cisco-IOS-XR-l2-eth-infra-cfg",
                                           None)
                node_4 = self._set_xml_tag(node_3, "vlan-identifier")
                self._set_xml_tag(
                    node_4, "vlan-type", None, None, "vlan-type-dot1q")
                self._set_xml_tag(
                    node_4, "first-tag", None, None, cp["L3-CE-IF-VLAN"])

        if is_static is False:
            xml_obj.remove(xml_obj.find("router-static"))
        else:
            self._set_xml_tag_variable(xml_obj,
                                       "vrf-name",
                                       vrf_dtl_info["L3-VRF-NAME"],
                                       "router-static",
                                       "vrfs",
                                       "vrf")
            node_1 = self._find_xml_node(xml_obj,
                                         "router-static",
                                         "vrfs",
                                         "vrf",
                                         "address-family")
            node_2 = self._set_xml_tag(node_1, "vrfipv4")
            node_3 = self._set_xml_tag(node_2, "vrf-unicast")
            node_4 = self._set_xml_tag(node_3, "vrf-prefixes")

            for cp in cp_infos:
                for route in cp.get("STATIC", ()):
                    node_5 = self._set_xml_tag(node_4, "vrf-prefix")
                    self._set_xml_tag(node_5,
                                      "prefix",
                                      None,
                                      None,
                                      route["L3-STATIC-ROUTE-ADD"])
                    self._set_xml_tag(node_5,
                                      "prefix-length",
                                      None,
                                      None,
                                      route["L3-STATIC-ROUTE-PREFIX"])
                    node_6 = self._set_xml_tag(node_5, "vrf-route")
                    node_7 = self._set_xml_tag(node_6, "vrf-next-hop-table")
                    node_8 = self._set_xml_tag(
                        node_7, "vrf-next-hop-interface-name-next-hop-address")
                    if cp["L3-CE-IF-VLAN"] == "0":
                        self._set_xml_tag(node_8,
                                          "interface-name",
                                          None,
                                          None,
                                          cp["L3-CE-IF-NAME"])
                    else:
                        self._set_xml_tag(node_8,
                                          "interface-name",
                                          None,
                                          None,
                                          cp["L3-CE-IF-NAME"] + "." +
                                          cp["L3-CE-IF-VLAN"])
                    self._set_xml_tag(node_8,
                                      "next-hop-address",
                                      None,
                                      None,
                                      route["L3-STATIC-ROUTE-NEXT"])

        if not is_bgp and not new_slice:
            xml_obj.remove(xml_obj.find("bgp"))
        else:
            self._set_xml_tag_variable(xml_obj,
                                       "as",
                                       str(lf_as_number),
                                       "bgp",
                                       "instance",
                                       "instance-as",
                                       "four-byte-as")
            node_1 = self._find_xml_node(xml_obj,
                                         "bgp",
                                         "instance",
                                         "instance-as",
                                         "four-byte-as",
                                         "vrfs",
                                         "vrf")
            self._set_xml_tag_variable(node_1,
                                       "vrf-name",
                                       vrf_dtl_info["L3-VRF-NAME"])
            if not new_slice:
                node_1.remove(node_1.find("vrf-global"))
            else:
                self._set_xml_tag_variable(node_1,
                                           "as",
                                           vrf_dtl_info[
                                               "L3-VRF-RD"].split(":")[0],
                                           "vrf-global",
                                           "route-distinguisher")
                self._set_xml_tag_variable(node_1,
                                           "as-index",
                                           vrf_dtl_info[
                                               "L3-VRF-RD"].split(":")[1],
                                           "vrf-global",
                                           "route-distinguisher")
                self._set_xml_tag_variable(node_1,
                                           "router-id",
                                           vrf_dtl_info["L3-VRF-ROUTER-ID"],
                                           "vrf-global")
            if is_bgp:
                node_2 = self._find_xml_node(node_1,
                                             "vrf-neighbors")
                for cp in cp_infos:
                    if cp.get("BGP") is None:
                        continue
                    node_3 = self._set_xml_tag(node_2, "vrf-neighbor")
                    self._set_xml_tag(node_3,
                                      "neighbor-address",
                                      None,
                                      None,
                                      cp["BGP"]["L3-BGP-RADD"])
                    node_4 = self._set_xml_tag(node_3, "remote-as")
                    self._set_xml_tag(node_4, "as-xx", None, None, "0")
                    self._set_xml_tag(node_4,
                                      "as-yy",
                                      None,
                                      None,
                                      cp["BGP"]["L3-BGP-PEER-AS"])
                    self._set_xml_tag(node_3,
                                      "update-source-interface",
                                      None,
                                      None,
                                      self._set_vlan_if_name(
                                          cp["L3-CE-IF-NAME"],
                                          cp["L3-CE-IF-VLAN"]))
                    node_4 = self._set_xml_tag(node_3, "vrf-neighbor-afs")
                    node_5 = self._set_xml_tag(node_4, "vrf-neighbor-af")
                    self._set_xml_tag(
                        node_5, "af-name", None, None, "ipv4-unicast")
                    self._set_xml_tag(node_5, "activate")
                    self._set_xml_tag(node_5,
                                      "route-policy-in",
                                      None,
                                      None,
                                      "eBGPv4_To_CE_import")
                    if cp["BGP"]["L3-BGP-MASTER"] is not None:
                        tmp_val = "eBGPv4_To_active-CE_export"
                    else:
                        tmp_val = "eBGPv4_To_standby-CE_export"
                    self._set_xml_tag(node_5,
                                      "route-policy-out",
                                      None,
                                      None,
                                      tmp_val)
                    self._set_xml_tag(
                        node_5, "send-community-ebgp", None, None, "true")
            else:
                node_1.remove(node_1.find("vrf-neighbors"))

        if is_vrrp is False:
            xml_obj.remove(xml_obj.find("vrrp"))
        else:
            node_1 = self._find_xml_node(xml_obj,
                                         "vrrp",
                                         "interfaces")
            for cp in cp_infos:
                if cp.get("VRRP") is None:
                    continue
                node_2 = self._set_xml_tag(node_1, "interface")
                self._set_xml_tag(node_2,
                                  "interface-name",
                                  None,
                                  None,
                                  self._set_vlan_if_name(cp["L3-CE-IF-NAME"],
                                                         cp["L3-CE-IF-VLAN"]))
                node_3 = self._set_xml_tag(node_2, "ipv4")
                node_4 = self._set_xml_tag(node_3, "version2")
                node_5 = self._set_xml_tag(node_4, "virtual-routers")
                node_6 = self._set_xml_tag(node_5, "virtual-router")
                self._set_xml_tag(node_6,
                                  "vr-id",
                                  None,
                                  None,
                                  cp["VRRP"]["L3-VRRP-GROUP-ID"])
                self._set_xml_tag(node_6,
                                  "priority",
                                  None,
                                  None,
                                  cp["VRRP"]["L3-VRRP-VIRT-PRI"])
                self._set_xml_tag(node_6, "preempt", None, None, "180")
                self._set_xml_tag(node_6,
                                  "primary-ipv4-address",
                                  None,
                                  None,
                                  cp["VRRP"]["L3-VRRP-VIRT-ADDR"])
                if len(cp["VRRP"]["track"]) > 0:
                    node_7 = self._set_xml_tag(node_6, "tracks")
                    for track_if in cp["VRRP"]["track"]:
                        node_8 = self._set_xml_tag(node_7, "track")
                        self._set_xml_tag(node_8,
                                          "interface-name",
                                          None,
                                          None,
                                          track_if["L3-VRRP-VIRT-IF"])
                        self._set_xml_tag(node_8, "priority", None, None, "10")

        return True

    @staticmethod
    @decorater_log
    def _get_l3_cp_info_from_ec(device_info, if_name, vlan_id):
        tmp = {"address": None, "prefix": None, "mtu_size": None}
        for cp in device_info["cp"]:
            if cp["if_name"] == if_name and \
                    cp["vlan"]["vlan_id"] == vlan_id:
                if cp["ce_ipv4"].get("address") is None \
                        or cp["ce_ipv4"].get("prefix") is None:
                    return None

                tmp["address"] = cp["ce_ipv4"]["address"]
                tmp["prefix"] = cp["ce_ipv4"]["prefix"]
                tmp["mtu_size"] = cp.get("mtu_size")
                tmp["protocol_flags"] = cp.get("protocol_flags")
                return tmp
        return None

    @staticmethod
    @decorater_log
    def _get_l3_static_info_from_db(device_info, if_name, vlan_id):
        tmp_list = []
        for cp in device_info["static_detail"]:
            if cp["if_name"] == if_name and \
                    cp["vlan_id"] == vlan_id:
                if cp["ipv4"].get("address") is None \
                        or cp["ipv4"].get("prefix") is None \
                        or cp["ipv4"].get("nexthop") is None:
                    continue
                tmp = {}
                tmp["address"] = cp["ipv4"]["address"]
                tmp["prefix"] = cp["ipv4"]["prefix"]
                tmp["nexthop"] = cp["ipv4"]["nexthop"]
                tmp_list.append(tmp)
        return tmp_list

    @decorater_log
    def _gen_del_l3_slice_variable_message(self,
                                           xml_obj,
                                           device_info,
                                           ec_message):
        '''
        Variable value to create message (L3Slice) for Netconf.
            Called out when adding CeLag.
        Parameter:
            xml_obj : xml object
            device_info : Device information
            ec_message : EC message
        Return value.
            Creation result : Boolean
        '''
        is_variable_value = True

        slice_name = ec_message["device-leaf"]["slice_name"]

        slice_cp_count = 0
        if device_info.get("cp") is not None:
            for cp in device_info["cp"]:

                if cp["slice_name"] == ec_message["device-leaf"]["slice_name"]:
                    slice_cp_count += 1

        is_vrrp = False
        is_bgp = False
        is_static = False
        is_cp_del = False

        cp_infos = []
        cp_count = 0
        ec_mes_cp_value = 0
        ec_static_cp_count = 0
        tmp = {}

        for cp in ec_message["device-leaf"]["cp"]:
            if cp.get("name") is None \
                    or cp.get("vlan-id") is None:
                is_variable_value = False
                break

            tmp_db = self._get_l3_cp_info_from_ec(
                device_info, cp["name"],
                cp["vlan-id"])
            if tmp_db is not None:
                tmp = \
                    {"L3-CE-IF-NAME": cp["name"],
                     "L3-CE-IF-VLAN": str(cp["vlan-id"]),
                     "L3-CE-IF-ADDR": tmp_db["address"],
                     "L3-CE-IF-PREFIX": tmp_db["prefix"],
                     "L3-CE-IF-MTU": tmp_db["mtu_size"],
                     "L3-CE-IF-P_FLAGS": tmp_db["protocol_flags"],
                     "L3-CE-IF-CP_DEL":  bool(cp.get("operation") == "delete"),
                     "L3-CE-IF-OPE": cp.get("operation")}
            else:
                tmp_db = None
                continue

            cp_del = bool(cp.get("operation") == "delete")
            if cp_del:
                is_cp_del = True
                ec_mes_cp_value += 1

            p_flg = tmp_db["protocol_flags"]

            if (cp_del and p_flg.get("vrrp")) or "vrrp" in cp:
                is_vrrp = True

            if (cp_del and p_flg.get("static")) or "static" in cp:
                is_static = True
                tmp_list = []
                if (cp_del and p_flg.get("static")):
                    static = self._get_l3_static_info_from_db(device_info,
                                                              cp["name"],
                                                              cp["vlan-id"])
                else:
                    static = cp["static"].get("route", {})
                for route in static:
                    if route.get("address") is None \
                            or route.get("prefix") is None \
                            or route.get("nexthop") is None:
                        is_variable_value = False
                        break

                    tmp_list.append(
                        {"L3-STATIC-ROUTE-ADD": route["address"],
                         "L3-STATIC-ROUTE-PREFIX": route["prefix"],
                         "L3-STATIC-ROUTE-NEXT": route["nexthop"]})
                    ec_static_cp_count += 1
                tmp["STATIC"] = tmp_list

            if (cp_del and p_flg.get("bgp")) or "bgp" in cp:
                is_bgp = True
            cp_infos.append(tmp)
            cp_count += 1

        if cp_count == 0:
            return False

        vrf_dtl_info = {}

        if len(device_info["vrf_detail"]) < 1:
            is_variable_value = False
        else:
            db_vrf = None
            vrf_dtl = device_info["vrf_detail"]
            for vrfs in vrf_dtl:
                if (vrfs.get("if_name") ==
                        cp_infos[0].get("L3-CE-IF-NAME") and
                        str(vrfs.get("vlan_id")) ==
                        cp_infos[0].get("L3-CE-IF-VLAN")):
                    db_vrf = vrfs
                    break
            if db_vrf is None or db_vrf.get("vrf_name") is None:
                is_variable_value = False
            else:
                vrf_dtl_info["L3-VRF-NAME"] = db_vrf.get("vrf_name")

        if device_info["device"].get("as_number") is None:
            is_variable_value = False
        lf_as_number = device_info["device"].get("as_number")

        vlan_count_db = {}
        vlan_list_db = {}
        vlan_count_cp = {}
        vlan_list_cp = {}
        all_del_vlan_cp = []
        for cp in device_info["cp"]:
            if cp["vlan"].get("vlan_id", 0) == 0:
                continue
            if vlan_count_db.get(cp["if_name"]):
                vlan_count_db[cp["if_name"]] += 1
                vlan_list_db[cp["if_name"]].append(
                    cp["vlan"].get("vlan_id"))
            else:
                vlan_count_db[cp["if_name"]] = 1
                vlan_list_db[cp["if_name"]] = [
                    cp["vlan"].get("vlan_id")]
        for cp_if in cp_infos:
            if cp_if["L3-CE-IF-VLAN"] == "0":
                continue
            if not cp_if["L3-CE-IF-CP_DEL"]:
                continue
            if vlan_count_cp.get(cp_if["L3-CE-IF-NAME"]):
                vlan_count_cp[cp_if["L3-CE-IF-NAME"]] += 1
                vlan_list_cp[cp_if["L3-CE-IF-NAME"]].append(
                    cp_if["L3-CE-IF-VLAN"])
            else:
                vlan_count_cp[cp_if["L3-CE-IF-NAME"]] = 1
                vlan_list_cp[cp_if["L3-CE-IF-NAME"]] = [
                    cp_if["L3-CE-IF-VLAN"]]
        for if_name, v_count in vlan_count_cp.items():
            if v_count == vlan_count_db.get(if_name, -1):
                all_del_vlan_cp.append(if_name)

        is_last_cp = False
        is_last_slice = False

        if int(ec_mes_cp_value) == slice_cp_count:
            is_last_slice = True

        if int(ec_mes_cp_value) == device_info["cp_value"]:
            is_last_cp = True

        bgp_nei = []
        slice_bgp_cp_count = 0
        slice_static_cp_count = 0
        for device_cp in device_info["cp"]:
            if slice_name == device_cp["slice_name"]:

                if device_cp["protocol_flags"]["static"] is True:

                    for static in device_info["static_detail"]:
                        if device_cp["if_name"] == static["if_name"] \
                            and device_cp["vlan"]["vlan_id"] == \
                                static["vlan_id"]:
                            slice_static_cp_count += 1

                if device_cp["protocol_flags"]["bgp"] is True:

                    for bgp in device_info["bgp_detail"]:
                        if device_cp["if_name"] == bgp["if_name"] \
                            and device_cp["vlan"]["vlan_id"] == \
                                bgp["vlan_id"]:
                            slice_bgp_cp_count += 1

        device_bgp_cp_count = 0
        device_static_cp_count = 0
        for ec_cp in cp_infos:
            for device_cp in device_info["cp"]:
                if ec_cp["L3-CE-IF-NAME"] == device_cp["if_name"] \
                    and ec_cp["L3-CE-IF-VLAN"] == \
                        str(device_cp["vlan"]["vlan_id"]):

                    if device_cp["protocol_flags"]["static"] is True and \
                            ec_cp.get("STATIC") is not None:
                        for ec_static in ec_cp["STATIC"]:
                            for static in device_info["static_detail"]:
                                s_ipv4 = (static.get("ipv4")
                                          if static.get("ipv4") is not None
                                          else {"address": "",
                                                "prefix": "nodata",
                                                "nexthop": ""})
                                if ec_cp["L3-CE-IF-NAME"] == static["if_name"] \
                                        and ec_cp["L3-CE-IF-VLAN"] == \
                                        str(static["vlan_id"]) \
                                        and ec_static["L3-STATIC-ROUTE-ADD"] == \
                                        s_ipv4.get("address") \
                                        and str(ec_static["L3-STATIC-ROUTE-PREFIX"]) == \
                                        str(s_ipv4.get("prefix")) \
                                        and ec_static["L3-STATIC-ROUTE-NEXT"] == \
                                        s_ipv4.get("nexthop"):
                                    device_static_cp_count += 1

                    if not ec_cp["L3-CE-IF-CP_DEL"]:
                        continue

                    if device_cp["protocol_flags"]["bgp"] is True:
                        for bgp in device_info["bgp_detail"]:
                            if ec_cp["L3-CE-IF-NAME"] == bgp["if_name"] \
                                and ec_cp["L3-CE-IF-VLAN"] \
                                    == str(bgp["vlan_id"]):
                                device_bgp_cp_count += 1

                                if bgp["remote"].get("ipv4_address") is None:
                                    is_variable_value = False
                                    continue

                                bgp_nei.append(bgp["remote"]["ipv4_address"])

        is_last_bgp = False
        is_last_static = False
        if slice_bgp_cp_count == device_bgp_cp_count:
            is_last_bgp = True

        if slice_static_cp_count == device_static_cp_count:
            is_last_static = True

        if is_variable_value is False:
            return False

        if is_last_cp is False \
                and is_last_slice is False:
            xml_obj.remove(xml_obj.find("vrfs"))
        elif is_last_cp is True:
            node_1 = self._find_xml_node(xml_obj,
                                         "vrfs")
            node_1.attrib[self._ATRI_OPE] = self._DELETE
            node_1.remove(node_1.find("vrf"))
        elif is_last_slice is True:
            self._set_xml_tag_variable(xml_obj,
                                       "vrf-name",
                                       vrf_dtl_info["L3-VRF-NAME"],
                                       "vrfs",
                                       "vrf")

        if is_cp_del:
            set_cps = cp_infos
            node_1 = xml_obj.find("interface-configurations")
        else:
            set_cps = []
            xml_obj.remove(xml_obj.find("interface-configurations"))
        for cp in set_cps:
            if not cp["L3-CE-IF-CP_DEL"]:
                continue

            if "Bundle-Ether" in cp["L3-CE-IF-NAME"] \
                    and cp["L3-CE-IF-VLAN"] == "0":
                node_2 = self._set_xml_tag(node_1, "interface-configuration")
                self._set_xml_tag(node_2, "active", None, None, "act")
                self._set_xml_tag(
                    node_2, "interface-name", None, None, cp["L3-CE-IF-NAME"])
                self._set_xml_tag(node_2, "interface-virtual")
                if cp["L3-CE-IF-MTU"] is not None:
                    node_3 = self._set_xml_tag(node_2, "mtus")
                    node_4 = self._set_xml_tag(
                        node_3, "mtu", self._ATRI_OPE, self._DELETE, None)
                    self._set_xml_tag(
                        node_4, "owner", None, None, "etherbundle")
                node_3 = self._set_xml_tag(node_2,
                                           "qos",
                                           "xmlns",
                                           "http://cisco.com/ns/yang/" +
                                           "Cisco-IOS-XR-qos-ma-cfg",
                                           None)
                node_4 = self._set_xml_tag(node_3, "input")
                node_5 = self._set_xml_tag(node_4,
                                           "service-policy",
                                           self._ATRI_OPE,
                                           self._DELETE,
                                           None)
                self._set_xml_tag(node_5,
                                  "service-policy-name",
                                  None,
                                  None,
                                  "in_ce_vpnbulk_be_policy")

                node_4 = self._set_xml_tag(node_3, "output")
                node_5 = self._set_xml_tag(node_4,
                                           "service-policy",
                                           self._ATRI_OPE,
                                           self._DELETE,
                                           None)
                self._set_xml_tag(node_5,
                                  "service-policy-name",
                                  None,
                                  None,
                                  "out_ce_pt2_policy")

                node_3 = self._set_xml_tag(node_2,
                                           "vrf",
                                           "xmlns",
                                           "http://cisco.com/ns/yang/" +
                                           "Cisco-IOS-XR-infra-rsi-cfg",
                                           vrf_dtl_info["L3-VRF-NAME"])
                node_3.attrib[self._ATRI_OPE] = self._DELETE
                node_3 = self._set_xml_tag(node_2,
                                           "ipv4-network",
                                           "xmlns",
                                           "http://cisco.com/ns/yang/" +
                                           "Cisco-IOS-XR-ipv4-io-cfg",
                                           None)
                node_4 = self._set_xml_tag(node_3, "addresses")
                node_5 = self._set_xml_tag(
                    node_4, "primary", self._ATRI_OPE, self._DELETE, None)
                self._set_xml_tag(
                    node_5, "address", None, None, cp["L3-CE-IF-ADDR"])
                self._set_xml_tag(node_5,
                                  "netmask",
                                  None,
                                  None,
                                  self._conversion_cidr2mask(
                                      cp["L3-CE-IF-PREFIX"]))
            elif "Bundle-Ether" not in cp["L3-CE-IF-NAME"] \
                    and cp["L3-CE-IF-VLAN"] == "0" \
                    and cp["L3-CE-IF-OPE"] == "delete":
                node_2 = self._set_xml_tag(node_1, "interface-configuration")
                self._set_xml_tag(node_2, "active", None, None, "act")
                self._set_xml_tag(
                    node_2, "interface-name", None, None, cp["L3-CE-IF-NAME"])
                if cp["L3-CE-IF-MTU"] is not None:
                    node_3 = self._set_xml_tag(node_2, "mtus")
                    node_4 = self._set_xml_tag(
                        node_3, "mtu", self._ATRI_OPE, self._DELETE, None)
                    self._set_xml_tag(node_4,
                                      "owner",
                                      None,
                                      None,
                                      self._get_owner(cp["L3-CE-IF-NAME"]))
                node_3 = self._set_xml_tag(node_2,
                                           "qos",
                                           "xmlns",
                                           "http://cisco.com/ns/yang/" +
                                           "Cisco-IOS-XR-qos-ma-cfg",
                                           None)
                node_4 = self._set_xml_tag(node_3, "input")
                node_5 = self._set_xml_tag(node_4,
                                           "service-policy",
                                           self._ATRI_OPE,
                                           self._DELETE,
                                           None)
                self._set_xml_tag(node_5,
                                  "service-policy-name",
                                  None,
                                  None,
                                  "in_ce_vpnbulk_be_policy")

                node_4 = self._set_xml_tag(node_3, "output")
                node_5 = self._set_xml_tag(node_4,
                                           "service-policy",
                                           self._ATRI_OPE,
                                           self._DELETE,
                                           None)
                self._set_xml_tag(node_5,
                                  "service-policy-name",
                                  None,
                                  None,
                                  "out_ce_pt2_policy")

                node_3 = self._set_xml_tag(node_2,
                                           "vrf",
                                           "xmlns",
                                           "http://cisco.com/ns/yang/" +
                                           "Cisco-IOS-XR-infra-rsi-cfg",
                                           vrf_dtl_info["L3-VRF-NAME"])
                node_3.attrib[self._ATRI_OPE] = self._DELETE
                node_3 = self._set_xml_tag(node_2,
                                           "ipv4-network",
                                           "xmlns",
                                           "http://cisco.com/ns/yang/" +
                                           "Cisco-IOS-XR-ipv4-io-cfg",
                                           None)
                node_4 = self._set_xml_tag(node_3, "addresses")
                node_5 = self._set_xml_tag(
                    node_4, "primary", self._ATRI_OPE, self._DELETE, None)
                self._set_xml_tag(
                    node_5, "address", None, None, cp["L3-CE-IF-ADDR"])
                self._set_xml_tag(node_5,
                                  "netmask",
                                  None,
                                  None,
                                  self._conversion_cidr2mask(
                                      cp["L3-CE-IF-PREFIX"]))
                self._set_xml_tag(node_2, "shutdown")
            elif cp["L3-CE-IF-VLAN"] != "0":
                if cp["L3-CE-IF-NAME"] in all_del_vlan_cp:
                    node_2 = self._set_xml_tag(node_1,
                                               "interface-configuration")
                    self._set_xml_tag(node_2, "active", None, None, "act")
                    self._set_xml_tag(node_2,
                                      "interface-name",
                                      None,
                                      None,
                                      cp["L3-CE-IF-NAME"])
                    if "Bundle-Ether" in cp["L3-CE-IF-NAME"]:
                        self._set_xml_tag(node_2, "interface-virtual")
                    if cp["L3-CE-IF-MTU"] is not None:
                        node_3 = self._set_xml_tag(node_2, "mtus")
                        node_4 = self._set_xml_tag(
                            node_3, "mtu", self._ATRI_OPE, self._DELETE, None)
                        if "Bundle-Ether" in cp["L3-CE-IF-NAME"]:
                            self._set_xml_tag(
                                node_4, "owner", None, None, "etherbundle")
                        else:
                            self._set_xml_tag(node_4,
                                              "owner",
                                              None,
                                              None,
                                              self._get_owner(
                                                  cp["L3-CE-IF-NAME"]))
                    node_3 = self._set_xml_tag(node_2,
                                               "qos",
                                               "xmlns",
                                               "http://cisco.com/ns/yang/" +
                                               "Cisco-IOS-XR-qos-ma-cfg",
                                               None)
                    node_4 = self._set_xml_tag(node_3, "input")
                    node_5 = self._set_xml_tag(node_4,
                                               "service-policy",
                                               self._ATRI_OPE,
                                               self._DELETE,
                                               None)
                    self._set_xml_tag(node_5,
                                      "service-policy-name",
                                      None,
                                      None,
                                      "in_ce_vpnbulk_be_policy")
                    node_4 = self._set_xml_tag(node_3, "output")
                    node_5 = self._set_xml_tag(node_4,
                                               "service-policy",
                                               self._ATRI_OPE,
                                               self._DELETE,
                                               None)
                    self._set_xml_tag(node_5,
                                      "service-policy-name",
                                      None,
                                      None,
                                      "out_ce_pt2_policy")
                    if "Bundle-Ether" not in cp["L3-CE-IF-NAME"]:
                        self._set_xml_tag(node_2, "shutdown")
                    all_del_vlan_cp.remove(cp["L3-CE-IF-NAME"])

                node_2 = self._set_xml_tag(node_1,
                                           "interface-configuration",
                                           self._ATRI_OPE,
                                           self._DELETE,
                                           None)
                self._set_xml_tag(node_2, "active", None, None, "act")
                self._set_xml_tag(node_2,
                                  "interface-name",
                                  None,
                                  None,
                                  cp["L3-CE-IF-NAME"] + "." +
                                  cp["L3-CE-IF-VLAN"])
                self._set_xml_tag(node_2,
                                  "interface-mode-non-physical",
                                  None,
                                  None,
                                  "default")

        if is_static is False:
            xml_obj.remove(xml_obj.find("router-static"))
        elif is_last_cp is True:
            node_1 = self._find_xml_node(xml_obj,
                                         "router-static")
            node_1.attrib[self._ATRI_OPE] = self._DELETE
            node_1.remove(node_1.find("vrfs"))
        else:
            self._set_xml_tag_variable(xml_obj,
                                       "vrf-name",
                                       vrf_dtl_info["L3-VRF-NAME"],
                                       "router-static",
                                       "vrfs",
                                       "vrf")
            if is_last_static:
                node_1 = self._find_xml_node(xml_obj,
                                             "router-static",
                                             "vrfs",
                                             "vrf")
                node_1.remove(node_1.find("address-family"))
                node_1.attrib[self._ATRI_OPE] = self._DELETE
            else:
                node_4 = self._find_xml_node(xml_obj,
                                             "router-static",
                                             "vrfs",
                                             "vrf",
                                             "address-family",
                                             "vrfipv4",
                                             "vrf-unicast",
                                             "vrf-prefixes")

                for cp in cp_infos:
                    if cp.get("STATIC") is None:
                        continue
                    for route in cp["STATIC"]:
                        node_5 = self._set_xml_tag(node_4,
                                                   "vrf-prefix",
                                                   None,
                                                   None,
                                                   None)
                        self._set_xml_tag(node_5,
                                          "prefix",
                                          None,
                                          None,
                                          route["L3-STATIC-ROUTE-ADD"])
                        self._set_xml_tag(node_5,
                                          "prefix-length",
                                          None,
                                          None,
                                          route["L3-STATIC-ROUTE-PREFIX"])
                        node_6 = self._set_xml_tag(node_5, "vrf-route")
                        node_7 = self._set_xml_tag(
                            node_6, "vrf-next-hop-table")
                        node_8 = self._set_xml_tag(
                            node_7,
                            "vrf-next-hop-interface-name-next-hop-address",
                            self._ATRI_OPE,
                            self._DELETE,
                            None)
                        if cp["L3-CE-IF-VLAN"] == "0":
                            self._set_xml_tag(node_8,
                                              "interface-name",
                                              None,
                                              None,
                                              cp["L3-CE-IF-NAME"])
                        else:
                            self._set_xml_tag(node_8,
                                              "interface-name",
                                              None,
                                              None,
                                              cp["L3-CE-IF-NAME"] + "." +
                                              cp["L3-CE-IF-VLAN"])
                        self._set_xml_tag(node_8,
                                          "next-hop-address",
                                          None,
                                          None,
                                          route["L3-STATIC-ROUTE-NEXT"])

        if not is_bgp and not is_last_slice and not is_last_cp:
            xml_obj.remove(xml_obj.find("bgp"))
        else:
            self._set_xml_tag_variable(xml_obj,
                                       "as",
                                       str(lf_as_number),
                                       "bgp",
                                       "instance",
                                       "instance-as",
                                       "four-byte-as")
            node_1 = self._find_xml_node(xml_obj,
                                         "bgp",
                                         "instance",
                                         "instance-as",
                                         "four-byte-as",
                                         "vrfs",
                                         "vrf")
            self._set_xml_tag_variable(node_1,
                                       "vrf-name",
                                       vrf_dtl_info["L3-VRF-NAME"])
            if is_last_cp:
                node_1 = self._find_xml_node(xml_obj,
                                             "bgp",
                                             "instance",
                                             "instance-as",
                                             "four-byte-as",
                                             "vrfs")
                node_1.attrib[self._ATRI_OPE] = self._DELETE
                node_1.remove(node_1.find("vrf"))
            elif is_last_slice:
                node_1.remove(node_1.find("vrf-neighbors"))
                node_1.attrib[self._ATRI_OPE] = self._DELETE
            else:
                node_2 = self._find_xml_node(node_1,
                                             "vrf-neighbors")
                for ip_addr in bgp_nei:
                    node_3 = self._set_xml_tag(node_2,
                                               "vrf-neighbor",
                                               self._ATRI_OPE,
                                               self._DELETE,
                                               None)
                    self._set_xml_tag(node_3,
                                      "neighbor-address",
                                      None,
                                      None,
                                      ip_addr)

        if is_vrrp is False:
            xml_obj.remove(xml_obj.find("vrrp"))
        elif is_last_cp:
            node_1 = self._find_xml_node(xml_obj,
                                         "vrrp")
            node_1.attrib[self._ATRI_OPE] = self._DELETE
            node_1.remove(node_1.find("interfaces"))
        else:
            node_1 = self._find_xml_node(xml_obj,
                                         "vrrp",
                                         "interfaces")
            for cp in cp_infos:
                if (not cp["L3-CE-IF-CP_DEL"] or
                        not cp["L3-CE-IF-P_FLAGS"].get("vrrp")):
                    continue
                node_2 = self._set_xml_tag(
                    node_1, "interface", self._ATRI_OPE, self._DELETE, None)
                self._set_xml_tag(node_2,
                                  "interface-name",
                                  None,
                                  None,
                                  self._set_vlan_if_name(cp["L3-CE-IF-NAME"],
                                                         cp["L3-CE-IF-VLAN"]))

        return True

    @decorater_log
    def _gen_replace_l3_slice_variable_message(self,
                                               xml_obj,
                                               device_info,
                                               ec_message):
        '''
        Variable value to create message (update L3Slice) for Netconf.
            Called out when adding CeLag.
        Parameter:
            xml_obj : xml object
            device_info : Device information
            ec_message : EC message
        Return value.
            Creation result : Boolean
        '''

        slice_name = ec_message.get("device-leaf", {}).get("slice_name")
        device_name = ec_message.get("device-leaf", {}).get("name")
        vrf_name = self._get_vrf_name_from_db(device_info, slice_name)
        if vrf_name is None:
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "Vrf name is not found.",
                __name__)
            return False
        static_ope_only_del = True

        cps = []

        try:
            for cp in ec_message.get("device-leaf", {}).get("cp", ()):
                tmp = {"L3-CE-IF-NAME": cp["name"],
                       "L3-CE-IF-VLAN": str(cp["vlan-id"]),
                       }
                static_obj = cp.get("static", {})
                tmp_list = []
                if len(static_obj.get("route", ())) == 0:
                    return False
                for route in static_obj.get("route", ()):
                    tmp_static = {
                        "L3-STATIC-ROUTE-ADD": route["address"],
                        "L3-STATIC-ROUTE-PREFIX": route["prefix"],
                        "L3-STATIC-ROUTE-NEXT": route["nexthop"],
                        "L3-STATIC-IP-VERSION": 4,
                        "OPERATION": route.get("operation")}
                    static_ope_only_del = (static_ope_only_del and
                                           bool(route.get("operation") ==
                                                self._DELETE))
                    tmp_list.append(tmp_static)
                tmp["STATIC"] = tmp_list
                cps.append(tmp)

            is_last_cp = False
            is_last_static = False
            operation = None
            if static_ope_only_del:
                operation = self._DELETE
                is_last_cp, is_last_static = self._check_del_static_result(
                    cps, device_info, slice_name)
        except Exception as ex:
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "ERROR : message = %s / Exception: %s" % (ec_message, ex),
                __name__)
            return False

        self._set_static_cp_info(xml_obj,
                                 cps,
                                 vrf_name,
                                 is_last_cp=is_last_cp,
                                 is_last_static=is_last_static,
                                 operation=operation)
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
            Creation result : Boolean
        '''
        return_val = False
        if operation == self._DELETE:
            return_val = self._gen_del_ce_lag_variable_message(
                xml_obj, ec_message, device_info)
        elif operation == self._REPLACE:
            return_val = self._gen_replace_ce_lag_variable_message(
                xml_obj, ec_message)
        else:
            return_val = self._gen_add_ce_lag_variable_message(
                xml_obj, ec_message)
        return return_val

    @decorater_log
    def _gen_add_ce_lag_variable_message(self,
                                         xml_obj,
                                         ec_message):
        '''
        Variable value to create message (create CeLag) for Netconf.
            Called out when adding CeLag.
        Parameter:
            xml_obj : xml object
            device_info : Device information
        Return value.
            Creation result : Boolean
        '''

        device_mes = ec_message.get("device", {})
        device_name = device_mes.get("name")

        try:
            if not device_mes.get("ce-lag-interface"):
                raise ValueError("Config CE-LAG is not found.")
            lag_ifs, lag_mem_ifs = self._get_ce_lag_from_ec(device_mes)
        except Exception as ex:
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "ERROR : message = %s / Exception: %s" % (ec_message, ex),
                __name__)
            return False

        if_node = self._set_if_confs(xml_obj)
        for lag_if in lag_ifs:
            self._set_lag_if(if_node, lag_if)
        for lag_mem_if in lag_mem_ifs:
            self._set_lag_mem_if(if_node, lag_mem_if)

        return True

    @decorater_log
    def _gen_replace_ce_lag_variable_message(self,
                                             xml_obj,
                                             ec_message):
        '''
        Valuable value to create message (CeLag) for Netconf.
            Called out when changing CeLag.
        Parameter:
            xml_obj : xml object
            device_info : device information
        Return value.
            Creation result : Boolean
        '''

        device_mes = ec_message.get("device", {})
        device_name = device_mes.get("name")

        try:
            if not device_mes.get("ce-lag-interface"):
                raise ValueError("Config CE-LAG is not found.")
            lag_ifs, lag_mem_ifs = self._get_ce_lag_from_ec(
                device_mes, service=self.name_celag, operation=self._REPLACE)
        except Exception as ex:
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "ERROR : message = %s / Exception: %s" % (ec_message, ex),
                __name__)
            return False

        if_node = self._set_if_confs(xml_obj)
        for lag_if in lag_ifs:
            self._set_update_lag_if(if_node, lag_if, lag_type=self.name_celag)

        for lag_mem_if in lag_mem_ifs:
            if lag_mem_if.get("OPERATION") == "delete":
                self._set_del_lag_mem_if_lag_speed(if_node, lag_mem_if)
            else:
                self._set_lag_mem_if_lag_speed(if_node, lag_mem_if)

        if_node = self._set_xml_tag(xml_obj,
                                    "interfaces",
                                    "xmlns",
                                    "http://openconfig.net/yang/" +
                                    "interfaces",
                                    None)

        for lag_mem_if in lag_mem_ifs:
            self._set_lag_mem_if_state(if_node, lag_mem_if)

        return True

    @decorater_log
    def _gen_del_ce_lag_variable_message(self,
                                         xml_obj,
                                         ec_message,
                                         device_info):
        '''
        Variable value to create message (delete CeLag) for Netconf.
            Called out when deleting CeLag.
        Parameter:
            xml_obj : xml object
            device_info : Device information
        Return value.
            Creation result : Boolean
        '''
        lag_ifs = []
        lag_mem_ifs = []

        device_mes = ec_message.get("device", {})
        device_name = device_mes.get("name")

        try:
            if not device_mes.get("ce-lag-interface"):
                raise ValueError("Config CE-LAG is not found.")
            lag_ifs, lag_mem_ifs = self._get_ce_lag_from_ec(device_mes)
        except Exception as ex:
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "ERROR : message = %s / Exception: %s" % (ec_message, ex),
                __name__)
            return False

        if_node = self._set_if_confs(xml_obj)
        for lag_if in lag_ifs:
            self._set_del_lag_if(if_node, lag_if)
        if_node = self._set_if_confs(xml_obj)
        for lag_if in lag_ifs:
            self._set_lag_if(if_node, lag_if)
        for lag_mem_if in lag_mem_ifs:
            self._set_del_lag_mem_if(if_node, lag_mem_if)

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
        Parameter:
            xml_obj : xml object
            device_info : device inforamation
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean
        '''
        device_mes = ec_message.get("device", {})

        return_val = False
        if operation == self._DELETE:
            return_val = self._gen_del_internal_lag_variable_message(
                xml_obj, ec_message, device_info)
        elif operation == self._REPLACE:
            is_cost_replace = self._check_replace_kind(device_mes)
            if is_cost_replace:
                return_val = self._gen_replace_internal_lag_variable_message(
                    xml_obj, ec_message, device_info)
            else:
                return_val = self._gen_update_internal_lag_variable_message(
                    xml_obj, ec_message, device_info)
        else:
            return_val = self._gen_add_internal_lag_variable_message(
                xml_obj, ec_message, device_info)
        return return_val

    @decorater_log
    def _check_replace_kind(self, device_mes):
        '''
        Judge whether inernal link change depends on cost value change or Lag speed change.
        Parameter:
            device_mes : EC message(device and below)（json）
        Return value.
            Result : Boolean(cost vlue change：True, Lag speed change：False)
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
    def _gen_add_internal_lag_variable_message(self,
                                               xml_obj,
                                               ec_message,
                                               device_info):
        '''
        Variable value to create message
        (add Link for internal use) for Netconf.
            Called out when adding Link for internal use.
        Parameter:
            xml_obj : xml object
            ec_message : EC message
        Return value.
            Creation result : Boolean
        '''
        device_mes = ec_message.get("device", {})
        device_name = device_mes.get("name")

        try:
            area_id = device_info["device"]["ospf"]["area_id"]

            phy_ifs, lag_ifs, lag_mem_ifs, inner_if_names = \
                self._get_internal_link_from_ec(
                    device_mes,
                    service=self.name_internal_link)
            breakout_ifs = self._get_breakout_from_ec(device_mes)
            self._check_breakout_if_name(breakout_ifs)
        except Exception as ex:
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "ERROR : message = %s / Exception: %s" % (ec_message, ex),
                __name__)
            return False

        self._set_ospf_infra_plane(xml_obj, self.name_internal_link)

        self._set_infra_ldp(xml_obj, self.name_internal_link)

        if_node = self._set_if_confs(xml_obj)

        self._set_breakout_interfaces(if_node, breakout_ifs)

        self._set_internal_links(if_node, phy_ifs, lag_ifs, lag_mem_ifs)

        node_5 = self._find_xml_node(xml_obj,
                                     "ospf",
                                     "processes",
                                     "process",
                                     "default-vrf",
                                     "area-addresses")
        self._set_ospf_area_data(node_5,
                                 area_id,
                                 inner_if_names)

        self._set_ldp_inner_if(xml_obj, inner_if_names)

        return True

    @decorater_log
    def _gen_update_internal_lag_variable_message(self,
                                                  xml_obj,
                                                  ec_message,
                                                  device_info):
        '''
        Variable value to create message (intrnal link change) for Netconf.
            Called out when changing  message for intrnal link.
        Parameter:
            xml_obj : xml object
            ec_message : EC message
            device_info : Device information
        Return value.
            Creation result : Boolean
        '''
        device_mes = ec_message.get("device", {})
        device_name = device_mes.get("name")

        try:
            phy_ifs, lag_ifs, lag_mem_ifs, inner_ifs = \
                self._get_replace_internal_link_from_ec(
                    device_mes,
                    service=self.name_internal_link)
        except Exception as ex:
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "ERROR : message = %s / Exception: %s" % (ec_message, ex),
                __name__)
            return False

        if_node = self._set_xml_tag(xml_obj,
                                    "interface-configurations",
                                    "xmlns",
                                    "http://cisco.com/ns/yang/" +
                                    "Cisco-IOS-XR-ifmgr-cfg",
                                    None)

        for inner_if in inner_ifs:
            self._set_update_lag_if(if_node, inner_if)

        for lag_mem_if in lag_mem_ifs:
            if lag_mem_if["OPERATION"] == "delete":
                self._set_del_lag_mem_if_lag_speed(if_node, lag_mem_if)
            else:
                self._set_lag_mem_if_lag_speed(if_node, lag_mem_if)

        if_node = self._set_xml_tag(xml_obj,
                                    "interfaces",
                                    "xmlns",
                                    "http://openconfig.net/yang/" +
                                    "interfaces",
                                    None)

        for lag_mem_if in lag_mem_ifs:
            self._set_lag_mem_if_state(if_node, lag_mem_if)

        return True

    @decorater_log
    def _gen_replace_internal_lag_variable_message(self,
                                                   xml_obj,
                                                   ec_message,
                                                   device_info):
        '''
        Variable value to create message (intrnal link change) for Netconf.
            Called out when changing  message for intrnal link.
        Parameter:
            xml_obj : xml object
            ec_message : EC message
            device_info : Device information
        Return value.
            Creation result : Boolean
        '''
        device_mes = ec_message.get("device", {})
        device_name = device_mes.get("name")

        try:
            area_id = device_info["device"]["ospf"]["area_id"]
            phy_ifs, lag_ifs, lag_mem_ifs, inner_if_names = \
                self._get_replace_internal_link_from_ec(
                    device_mes,
                    service=self.name_internal_link)
        except Exception as ex:
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "ERROR : message = %s / Exception: %s" % (ec_message, ex),
                __name__)
            return False

        node_1 = self._set_xml_tag(xml_obj,
                                   "ospf",
                                   "xmlns",
                                   "http://cisco.com/ns/yang/" +
                                   "Cisco-IOS-XR-ipv4-ospf-cfg",
                                   None)
        node_2 = self._set_xml_tag(node_1, "processes")
        node_3 = self._set_xml_tag(node_2, "process")
        self._set_xml_tag(node_3,
                          "process-name",
                          None,
                          None,
                          "v4_MSF_OSPF")
        node_4 = self._set_xml_tag(node_3, "default-vrf")
        node_5 = self._set_xml_tag(node_4, "area-addresses")

        self._set_ospf_area_data(node_5,
                                 area_id,
                                 inner_if_names,
                                 operation=self._REPLACE)

        return True

    @decorater_log
    def _check_all_del_lag(self, lag_name, lag_mem_ifs, device_info):
        del_count = 0
        db_count = 0
        for lag_mem in lag_mem_ifs:
            del_count += 1 if lag_mem.get("LAG-IF-NAME") == lag_name else 0
        for db_lag in device_info.get("internal-link"):
            if db_lag.get("if_name") == lag_name:
                for db_lag_mem in db_lag.get("member"):
                    db_count += 1 if db_lag_mem.get(
                        "if_name") == lag_name else 0
        return bool(del_count == db_count)

    @decorater_log
    def _gen_del_internal_lag_variable_message(self,
                                               xml_obj,
                                               ec_message,
                                               device_info):
        '''
        Variable value to create message
        (delete Link for internal use) for Netconf.
            Called out when deleting Link for internal use.
        Parameter:
            xml_obj : xml object
            ec_message : EC message
            device_info : Device information (from DB)
        Return value.
            Creation result : Boolean
        '''
        device_mes = ec_message.get("device", {})
        device_name = device_mes.get("name")

        try:
            area_id = device_info["device"]["ospf"]["area_id"]

            phy_ifs, lag_ifs_for_mem, lag_mem_ifs, inner_if_names = \
                self._get_del_internal_link_from_ec(
                    device_mes,
                    service=self.name_internal_link,
                    db_info=device_info)
            lag_ifs = []

            for lag in lag_ifs_for_mem:
                if self._check_all_del_lag(lag["IF-NAME"],
                                           lag_mem_ifs,
                                           device_info):
                    lag_ifs.append(lag.copy())

        except Exception as ex:
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "ERROR : message = %s / Exception: %s" % (ec_message, ex),
                __name__)
            return False

        self._set_ospf_infra_plane(xml_obj, self.name_internal_link)

        self._set_infra_ldp(xml_obj, self.name_internal_link)

        if len(lag_ifs) + len(phy_ifs) > 0:
            if_node = self._set_xml_tag(xml_obj,
                                        "interface-configurations",
                                        "xmlns",
                                        "http://cisco.com/ns/yang/" +
                                        "Cisco-IOS-XR-ifmgr-cfg",
                                        None)
            for tmp_if in phy_ifs:
                self._set_del_internal_link(if_node, tmp_if, self._if_type_phy)
            for tmp_if in lag_ifs:
                self._set_del_internal_link(if_node, tmp_if, self._if_type_lag)

            node_5 = self._find_xml_node(xml_obj,
                                         "ospf",
                                         "processes",
                                         "process",
                                         "default-vrf",
                                         "area-addresses")
            self._set_ospf_area_data(node_5,
                                     area_id,
                                     inner_if_names,
                                     operation=self._DELETE)

            self._set_ldp_inner_if(
                xml_obj, inner_if_names, operation=self._DELETE)
        else:
            for node_1 in xml_obj:
                xml_obj.remove(node_1)

        if len(lag_mem_ifs) > 0:
            if_node = self._set_xml_tag(xml_obj,
                                        "interface-configurations",
                                        "xmlns",
                                        "http://cisco.com/ns/yang/" +
                                        "Cisco-IOS-XR-ifmgr-cfg",
                                        None)

            if_node = self._set_if_confs(xml_obj)
            for lag_if in lag_ifs:
                self._set_lag_if(if_node, lag_if)
            for lag_mem_if in lag_mem_ifs:
                self._set_del_lag_mem_if(if_node, lag_mem_if)

        return True

    @decorater_log
    def _gen_if_condition_variable_message(self,
                                           xml_obj,
                                           device_info,
                                           ec_message,
                                           operation):
        '''
        Variable value to create message (InternalLag) for Netconf.
            Called out when creating fixed message for InternalLag.
        Parameter:
            xml_obj : xml object
            device_info : device information
            ec_message : EC message
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean
        '''

        device_mes = ec_message.get("device", {})
        device_name = device_mes.get("name")

        try:
            phy_ifs, lag_ifs = \
                self._get_if_condition_from_ec(
                    device_mes,
                    service=self.name_if_condition)
        except Exception as ex:
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "ERROR : message = %s / Exception: %s" % (ec_message, ex),
                __name__)
            return False

        if_node = self._set_xml_tag(xml_obj,
                                    "interface-configurations",
                                    "xmlns",
                                    "http://cisco.com/ns/yang/" +
                                    "Cisco-IOS-XR-ifmgr-cfg",
                                    None)

        for lag_if in lag_ifs:
            self._set_if_condition(if_node, lag_if)

        for phy_if in phy_ifs:
            self._set_if_condition(if_node, phy_if)

        return True

    @decorater_log
    def _gen_breakout_variable_message(self,
                                       xml_obj,
                                       device_info,
                                       ec_message,
                                       operation):
        '''
        Variable value to create message (breakout) for Netconf.
            Called out when creating message for breakout.
            (After fixed message has been created.)
        Parameter:
            xml_obj : xml object
            device_info : Device information
            ec_message : EC message
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean (Write properly using override method. )
        '''
        device_mes = ec_message.get("device", {})
        device_name = device_mes.get("name")

        try:
            breakout_ifs = self._get_breakout_from_ec(device_mes,
                                                      device_info,
                                                      operation)
            self._check_breakout_if_name(breakout_ifs)
        except Exception as ex:
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "ERROR : message = %s / Exception: %s" % (ec_message, ex),
                __name__)
            return False

        if_node = self._set_if_confs(xml_obj)

        self._set_breakout_interfaces(if_node, breakout_ifs, operation)

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
            Creation result : Boolean (Write properly using override method. )
        '''
        self.common_util_log.logging(
            " ",
            self.log_level_error,
            self.Logmessage["Call_NG_Method"] %
            ("_gen_cluster_link_variable_message"),
            __name__)
        return False

    @decorater_log
    def _validation_l3_slice(self, device_info):
        '''
        Validation check (L3Slice).
            Called out when doing validation check for L3Slice.
        Parameter:
            device_info : Device information
        Return value :
            Result after check : Boolean
        '''
        check_result = True
        device = device_info.get("device-leaf")
        if device:
            for row in device.get("cp") if device.get("cp") else []:
                if row.get("ce-interface"):
                    if (row["ce-interface"].get("address6") or
                            row["ce-interface"].get("prefix6")):
                        check_result = False
                        self.common_util_log.logging(
                            " ", self.log_level_debug,
                            "CE-interface have ipv6", __name__)
                        break
                if row.get("vrrp"):
                    if row["vrrp"].get("virtual-address6"):
                        check_result = False
                        self.common_util_log.logging(
                            " ", self.log_level_debug,
                            "VRRP have ipv6", __name__)
                        break
                if row.get("bgp") and (row["bgp"].get("local-address6") or
                                       row["bgp"].get("remote-address6")):
                    check_result = False
                    self.common_util_log.logging(
                        " ", self.log_level_debug,
                        "BGP have ipv6", __name__)
                    break
                if row.get("static") and row["static"].get("route6"):
                    tmp = row["static"].get("route6")
                    is_static_ok = True
                    for item in (tmp if tmp is not None else []):
                        if (item.get("address") or
                                item.get("prefix") or
                                item.get("nexthop")):
                            is_static_ok = False
                        break
                    if not is_static_ok:
                        check_result = False
                        self.common_util_log.logging(
                            " ", self.log_level_debug,
                            "STATIC_ROUTE have ipv6", __name__)
                        break

        return check_result

    @decorater_log
    def _comparsion_sw_db_l3_slice(self, message, db_info):
        '''
        SW-DB comparison process (check for information matching) (L3Slice).
            Called out when checking information matching of L3Slice.
        Parameter:
            message : Response message
            db_info : DB information
        Return value :
            Matching result : Boolean
        '''
        class ns_xml(object):
            '''
            For name space processing.
            '''
            class ns_list(object):
                '''
                Name space processing list.
                '''
                vrf = "vrf"
                bgp = "bgp"
                ifmgr = "ifmgr"
                qos = "qos"
                io = "io"
                pfilter = "pfilter"
                l2_eth = "l2-eth"
                static = "static"
                ospf = "ospf"
                vrrp = "vrrp"

            n_sp_dict = {ns_list.vrf:
                         "http://cisco.com/ns/yang/Cisco-IOS-XR-infra-rsi-cfg",
                         ns_list.bgp:
                         "http://cisco.com/ns/yang/Cisco-IOS-XR-ipv4-bgp-cfg",
                         ns_list.ifmgr:
                         "http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg",
                         ns_list.qos:
                         "http://cisco.com/ns/yang/Cisco-IOS-XR-qos-ma-cfg",
                         ns_list.io:
                         "http://cisco.com/ns/yang/Cisco-IOS-XR-ipv4-io-cfg",
                         ns_list.pfilter:
                         ("http://cisco.com/ns/yang/" +
                          "Cisco-IOS-XR-ip-pfilter-cfg"),
                         ns_list.l2_eth:
                         ("http://cisco.com/ns/yang/" +
                          "Cisco-IOS-XR-l2-eth-infra-cfg"),
                         ns_list.static:
                         "http://cisco.com/ns/yang/Cisco-IOS-XR-ip-static-cfg",
                         ns_list.ospf:
                         "http://cisco.com/ns/yang/Cisco-IOS-XR-ipv4-ospf-cfg",
                         ns_list.vrrp:
                         "http://cisco.com/ns/yang/Cisco-IOS-XR-ipv4-vrrp-cfg"}

            def __init__(self, ini_ns=ns_list.vrf):
                self.name_space = ini_ns

            def ns_find_node(self, parent, *tags):
                tmp = parent
                for tag in tags:
                    if (tmp is not None and
                            tmp.find("%s:%s" % (self.name_space, tag),
                                     self.n_sp_dict) is not None):
                        tmp = tmp.find("%s:%s" % (self.name_space, tag),
                                       self.n_sp_dict)
                    else:
                        return None
                return tmp

            def ns_findall_node(self, parent, tag):
                return parent.findall("%s:%s" % (self.name_space, tag),
                                      self.n_sp_dict)

        ns_p = ns_xml(ns_xml.ns_list.vrf)
        is_return = True

        reg_as_number = (db_info["device"].get("as_number")
                         if db_info.get("device") else None)

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

        ns_p.name_space = ns_xml.ns_list.vrf
        if ns_p.ns_find_node(message, "vrfs") is not None:
            node = ns_p.ns_find_node(message,
                                     "vrfs",
                                     "vrf",
                                     "vrf-name")
            if not self._comparsion_pair(node, vrf_name):
                is_return = False

            rt_val = (db_vrf["rt"].split(":", 2)
                      if db_vrf["rt"] is not None and
                      len(db_vrf["rt"].split(":")) == 3
                      else ("target", "fault_val_rt", "fault_val_rt"))
            tmp_node = ns_p.ns_find_node(message,
                                         "vrfs",
                                         "vrf",
                                         "afs",
                                         "af")
            ns_p.name_space = ns_xml.ns_list.bgp
            node_1 = ns_p.ns_find_node(tmp_node,
                                       "bgp",
                                       "import-route-targets",
                                       "route-targets",
                                       "route-target",
                                       "as-or-four-byte-as")
            node_2 = ns_p.ns_find_node(node_1, "as")
            if not self._comparsion_pair(node_2, rt_val[1]):
                is_return = False
            node_2 = ns_p.ns_find_node(node_1, "as-index")
            if not self._comparsion_pair(node_2, rt_val[2]):
                is_return = False

            node_1 = ns_p.ns_find_node(tmp_node,
                                       "bgp",
                                       "export-route-targets",
                                       "route-targets",
                                       "route-target",
                                       "as-or-four-byte-as")

            node_2 = ns_p.ns_find_node(node_1, "as")
            if not self._comparsion_pair(node_2, rt_val[1]):
                is_return = False
            node_2 = ns_p.ns_find_node(node_1, "as-index")
            if not self._comparsion_pair(node_2, rt_val[2]):
                is_return = False

        ns_p.name_space = ns_xml.ns_list.ifmgr
        ifs = ns_p.ns_find_node(message, "interface-configurations")
        for cp in (ns_p.ns_findall_node(ifs, "interface-configuration")
                   if is_return and ifs is not None else []):
            ns_p.name_space = ns_xml.ns_list.ifmgr
            if_name_node = ns_p.ns_find_node(cp, "interface-name")
            if if_name_node is None:
                return False

            if_name = None
            vlan = None
            mtu = None
            ipv4_addr = None
            ipv4_pre = None
            is_base_if = False

            for db_cp in db_info.get("cp") if db_info.get("cp") else []:
                tmp_if_name = db_cp.get("if_name")
                tmp_vlan = (db_cp["vlan"].get("vlan_id")
                            if db_cp.get("vlan") else None)
                if (if_name_node.text ==
                        self._set_vlan_if_name(tmp_if_name, tmp_vlan)):
                    if_name = self._set_vlan_if_name(tmp_if_name, tmp_vlan)
                    vlan = tmp_vlan
                    if db_cp.get("mtu_size") is None:
                        mtu = None
                    elif int(vlan) == 0:
                        mtu = str(int(db_cp["mtu_size"]) + 14)
                    else:
                        mtu = str(int(db_cp["mtu_size"]) + 18)
                    ipv4_addr = (db_cp["ce_ipv4"].get("address")
                                 if db_cp.get("ce_ipv4") else None)
                    ipv4_pre = (
                        self._conversion_cidr2mask(db_cp["ce_ipv4"]["prefix"])
                        if db_cp.get("ce_ipv4") else None)
                    break
                elif if_name_node.text == tmp_if_name and tmp_vlan != "0":
                    if_name = db_cp.get("if_name")
                    is_base_if = True
                    break
            self.common_util_log.logging(device_name, self.log_level_debug,
                                         "CP_INFO DEVICE_NAME : %s = %s" %
                                         (if_name_node.text, if_name),
                                         __name__)

            if if_name is None:
                is_return = False
                break

            if is_base_if:
                continue

            tmp_node = ns_p.ns_find_node(cp, "mtus", "mtu", "mtu")
            if not self._comparsion_pair(tmp_node, mtu):
                is_return = False
                break

            ns_p.name_space = ns_xml.ns_list.vrf
            if not self._comparsion_pair(
                    ns_p.ns_find_node(cp, "vrf"), vrf_name):
                is_return = False
                break

            ns_p.name_space = ns_xml.ns_list.io
            tmp_node = ns_p.ns_find_node(cp,
                                         "ipv4-network",
                                         "addresses",
                                         "primary",
                                         "address")
            if not self._comparsion_pair(tmp_node, ipv4_addr):
                is_return = False
                break
            tmp_node = ns_p.ns_find_node(cp,
                                         "ipv4-network",
                                         "addresses",
                                         "primary",
                                         "netmask")
            if not self._comparsion_pair(tmp_node, ipv4_pre):
                is_return = False
                break

            if vlan is not None and "%s" % (vlan,) != "0":
                ns_p.name_space = ns_xml.ns_list.l2_eth
                tmp_node = ns_p.ns_find_node(cp,
                                             "vlan-sub-configuration",
                                             "vlan-identifier",
                                             "first-tag")
                if not self._comparsion_pair(tmp_node, vlan):
                    is_return = False
                    break

        ns_p.name_space = ns_xml.ns_list.static
        if (is_return and
                ns_p.ns_find_node(message, "router-static") is not None):
            tmp_node = ns_p.ns_find_node(message,
                                         "router-static",
                                         "vrfs",
                                         "vrf",
                                         "vrf-name")
            if not self._comparsion_pair(tmp_node, vrf_name):
                is_return = False

            tmp_node = ns_p.ns_find_node(message,
                                         "router-static",
                                         "vrfs",
                                         "vrf",
                                         "address-family",
                                         "vrfipv4",
                                         "vrf-unicast",
                                         "vrf-prefixes")
            for node_1 in ns_p.ns_findall_node(tmp_node, "vrf-prefix"):
                node_2 = ns_p.ns_find_node(node_1, "prefix")
                node_3 = ns_p.ns_find_node(node_1, "prefix-length")
                node_tmp = ns_p.ns_find_node(node_1,
                                             "vrf-route",
                                             "vrf-next-hop-table",
                                             "vrf-next-hop-interface-" +
                                             "name-next-hop-address")
                node_4 = ns_p.ns_find_node(node_tmp, "interface-name")
                node_5 = ns_p.ns_find_node(node_tmp, "next-hop-address")

                is_ok = False
                for db_static in (db_info["static_detail"]
                                  if db_info.get("static_detail") else []):
                    if db_static.get("ipv4"):
                        prefix = db_static["ipv4"].get("address")
                        pre_len = (db_static["ipv4"].get("prefix")
                                   if db_static["ipv4"].get("prefix")
                                   else None)
                        s_if_name = (
                            self._set_vlan_if_name(db_static.get("if_name"),
                                                   db_static.get("vlan_id")))
                        next_hop = db_static["ipv4"].get("nexthop")
                    else:
                        prefix = None
                        pre_len = None
                        s_if_name = None
                        next_hop = None

                    if (self._comparsion_pair(node_2, prefix) and
                            self._comparsion_pair(node_3, pre_len) and
                            self._comparsion_pair(node_4, s_if_name) and
                            self._comparsion_pair(node_5, next_hop)):
                        is_ok = True
                        break

                if is_ok is False:
                    is_return = False
                    break

        ns_p.name_space = ns_xml.ns_list.ospf
        if is_return and ns_p.ns_find_node(message, "ospf") is not None:
            node_1 = ns_p.ns_find_node(message,
                                       "ospf",
                                       "processes",
                                       "process",
                                       "vrfs",
                                       "vrf")

            node_2 = ns_p.ns_find_node(node_1, "vrf-name")
            is_return = is_return and self._comparsion_pair(node_2, vrf_name)

            node_2 = ns_p.ns_find_node(node_1,
                                       "redistribution",
                                       "redistributes")

            for node_3 in (ns_p.ns_findall_node(node_2, "redistribute")
                           if node_2 is not None else []):
                node_5 = None
                node_4 = ns_p.ns_find_node(node_3, "protocol-name")
                if node_4 is not None and node_4.text == "bgp":
                    node_5 = node_3
                    break

            if node_5 is None:
                is_return = False
            else:
                node_6 = ns_p.ns_find_node(node_5, "bgp", "as-yy")
                if self._comparsion_pair(node_6, reg_as_number) is False:
                    is_return = False

            node_2 = ns_p.ns_find_node(node_1,
                                       "area-addresses",
                                       "area-area-id",
                                       "name-scopes")

            for node_3 in ns_p.ns_findall_node(node_2, "name-scope"):
                node_4 = ns_p.ns_find_node(node_3, "interface-name")
                node_5 = ns_p.ns_find_node(node_3, "cost")

                is_ok = False
                for db_cp in db_info["cp"] if db_info.get("cp") else []:
                    metric = db_cp.get("metric")
                    if_name = (
                        self._set_vlan_if_name(db_cp.get("if_name"),
                                               db_cp["vlan"].get("vlan_id")))

                    if (self._comparsion_pair(node_4, if_name) and
                            self._comparsion_pair(node_5, metric)):
                        is_ok = True
                        break

                if not is_ok:
                    is_return = False
                    break

        ns_p.name_space = ns_xml.ns_list.bgp
        if is_return and ns_p.ns_find_node(message, "bgp") is not None:
            node_1 = ns_p.ns_find_node(message,
                                       "bgp",
                                       "instance",
                                       "instance-as",
                                       "four-byte-as")

            if not self._comparsion_pair(
                    ns_p.ns_find_node(node_1, "as"),
                    reg_as_number):
                is_return = False

            node_2 = ns_p.ns_find_node(node_1,
                                       "vrfs",
                                       "vrf")
            if not self._comparsion_pair(
                    ns_p.ns_find_node(node_2, "vrf-name"), vrf_name):
                is_return = False

            node_3 = ns_p.ns_find_node(node_2,
                                       "vrf-global",
                                       "route-distinguisher")

            rd_val = (db_vrf["rd"].partition(":")
                      if db_vrf["rd"] is not None and
                      db_vrf["rd"].partition(":")[1] == ":"
                      else ("fault_val_rd", None, "fault_val_rd"))
            if not self._comparsion_pair(
                    ns_p.ns_find_node(node_3, "as"), rd_val[0]):
                is_return = False
            if not self._comparsion_pair(
                    ns_p.ns_find_node(node_3, "as-index"), rd_val[2]):
                is_return = False

            node_3 = ns_p.ns_find_node(node_2,
                                       "vrf-global",
                                       "router-id")
            if not self._comparsion_pair(node_3, db_vrf["router_id"]):
                is_return = False

            node_3 = ns_p.ns_find_node(node_2,
                                       "vrf-neighbors")

            for node_4 in ns_p.ns_findall_node(node_3, "vrf-neighbor"):
                node_5 = ns_p.ns_find_node(node_4, "neighbor-address")
                node_6 = ns_p.ns_find_node(node_4, "remote-as", "as-yy")
                node_7 = ns_p.ns_find_node(node_4, "update-source-interface")

                is_ok = False
                for bgp_cp in db_info["bgp_detail"]:
                    address = bgp_cp["remote"]["ipv4_address"]
                    re_as_num = bgp_cp["as_number"]
                    upd_if = self._set_vlan_if_name(bgp_cp["if_name"],
                                                    bgp_cp["vlan_id"])

                    if (self._comparsion_pair(node_5, address) and
                            self._comparsion_pair(node_6, re_as_num) and
                            self._comparsion_pair(node_7, upd_if)):
                        is_ok = True
                        break

                if not is_ok:
                    is_return = False
                    break

        ns_p.name_space = ns_xml.ns_list.vrrp
        if is_return and ns_p.ns_find_node(message, "vrrp") is not None:
            node_1 = ns_p.ns_find_node(message,
                                       "vrrp",
                                       "interfaces")
            for node_2 in (ns_p.ns_findall_node(node_1, "interface")
                           if node_1 is not None else []):
                if_name = None
                vlan = None
                group_id = None
                priority = None
                ipv4_addr = None
                track_if = None

                if_name_node = ns_p.ns_find_node(node_2, "interface-name")

                if if_name_node is None:
                    is_return = False
                    break

                for db_vrrp in (db_info.get("vrrp_detail")
                                if db_info.get("vrrp_detail") else []):
                    if if_name_node.text == self._set_vlan_if_name(
                            db_vrrp.get("if_name"), db_vrrp.get("vlan_id")):
                        if_name = (self._set_vlan_if_name(db_vrrp["if_name"],
                                                          db_vrrp["vlan_id"]))
                        vlan = db_vrrp.get("vlan_id")
                        group_id = db_vrrp.get("group_id")
                        priority = db_vrrp.get("priority")
                        ipv4_addr = db_vrrp["virtual"]["ipv4_address"]
                        ipv4_addr = (db_vrrp["virtual"].get("ipv4_address")
                                     if db_vrrp.get("virtual") else None)
                        track_if = db_vrrp.get("track_if_name")
                        break

                self.common_util_log.logging(device_name, self.log_level_debug,
                                             "VRRP IF_NAME : %s = %s" %
                                             (if_name_node.text, if_name),
                                             __name__)

                if if_name is None:
                    is_return = False
                    break

                node_3 = ns_p.ns_find_node(node_2,
                                           "ipv4",
                                           "version2",
                                           "virtual-routers",
                                           "virtual-router")

                node_4 = ns_p.ns_find_node(node_3, "vr-id")
                node_5 = ns_p.ns_find_node(node_3, "priority")
                node_6 = ns_p.ns_find_node(node_3, "primary-ipv4-address")

                if not (self._comparsion_pair(node_4, group_id) and
                        self._comparsion_pair(node_5, priority) and
                        self._comparsion_pair(node_6, ipv4_addr)):
                    is_return = False
                    break

                node_tracks = ns_p.ns_find_node(node_3, "tracks")
                for track in (ns_p.ns_findall_node(node_tracks, "track")
                              if node_tracks is not None else []):
                    node_7 = ns_p.ns_find_node(track, "interface-name")
                    self.common_util_log.logging(
                        device_name, self.log_level_debug,
                        "TRACK IF_NAME EXIST: %s in %s" % (
                            (node_7.text if node_7 is not None
                             else None, track_if), if_name), __name__)
                    if node_7 is None or node_7.text not in track_if:
                        is_return = False
                        break
        return is_return


    @decorater_log
    def _get_device_from_ec(self, device_mes, service=None):
        '''
        Obtain EC message information regarding device expansion.
        (common for spine, leaf)
        '''

        dev_reg_info = {}
        dev_reg_info["DEVICE-NAME"] = device_mes.get("name")

        tmp = device_mes.get("snmp", {})
        dev_reg_info["SNMP-SERVER"] = tmp.get("server-address")
        dev_reg_info["SNMP-COMMUNITY"] = tmp.get("community")

        tmp = device_mes.get("loopback-interface", {})
        dev_reg_info["LB-IF-ADDR"] = tmp.get("address")
        dev_reg_info["LB-IF-PREFIX"] = tmp.get("prefix")

        ospf = device_mes.get("ospf", {})
        dev_reg_info["OSPF-AREA-ID"] = ospf.get("area-id")

        for chk_item in dev_reg_info.values():
            if chk_item is None:
                raise ValueError("device info not enough information")

        return dev_reg_info

    @decorater_log
    def _get_leaf_vpn_from_ec(self, device_mes):
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
            breakout["IF-NAME"] = tmp.get("base-interface")

            if operation == self._DELETE:
                db_data = self._get_breakout_data_in_db(
                    db_info, breakout["IF-NAME"])
                breakout["SPEED"] = db_data.get("speed").strip("g|G")
                breakout["BREAKOUT-NUM"] = db_data.get("breakout-num")
            else:
                breakout["SPEED"] = tmp.get("speed").strip("g|G")
                breakout["BREAKOUT-NUM"] = tmp.get("breakout-num")
            if operation == self._DELETE and not breakout.get("IF-NAME"):
                raise ValueError("breakout info not enough information")
            else:
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
        Obtain EC message information regarding LAG for CE.
        '''
        lag_ifs = []
        lag_mem_ifs = []

        for tmp in device_mes.get("ce-lag-interface", ()):
            if (not tmp.get("name") or
                    tmp.get("minimum-links") is None or
                not tmp.get("leaf-interface") or
                    len(tmp["leaf-interface"]) == 0):
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
    def _get_internal_link_from_ec(self,
                                   device_mes,
                                   service=None,
                                   operation=None,
                                   db_info=None):
        '''
        Obtain EC message information regarding internal Link (LAG).
        '''
        inner_ifs = []

        phy_ifs = []

        for tmp in device_mes.get("internal-physical", ()):
            if (not tmp.get("name") or
                not tmp.get("address") or
                    tmp.get("prefix") is None):
                raise ValueError("internal-physical not enough information")

            inner_ifs.append(tmp.get("name"))
            phy_ifs.append(self._get_internal_if_info(tmp, self._if_type_phy))

        lag_ifs = []
        lag_mem_ifs = []

        for tmp in device_mes.get("internal-lag", ()):
            if (not tmp.get("name") or
                not tmp.get("address") or
                    tmp.get("prefix") is None or
                    tmp.get("minimum-links") is None or
                not tmp.get("internal-interface") or
                    len(tmp["internal-interface"]) == 0):
                raise ValueError("internal-lag not enough information")

            inner_ifs.append(tmp.get("name"))
            lag_ifs.append(self._get_internal_if_info(tmp, self._if_type_lag))

            for lag_mem in tmp.get("internal-interface"):
                if not lag_mem.get("name"):
                    raise ValueError(
                        "internal-interface not enough information ")
                lag_mem_ifs.append(self._get_lag_mem_if_info(tmp, lag_mem))

        return phy_ifs, lag_ifs, lag_mem_ifs, inner_ifs

    @decorater_log
    def _get_replace_internal_link_from_ec(self,
                                           device_mes,
                                           service=None,
                                           operation=None,
                                           db_info=None):
        '''
        Obtain EC message information related to imternal link(LAG)
        '''
        inner_ifs = []

        phy_ifs = []

        for tmp in device_mes.get("internal-physical", ()):
            if not tmp.get("name"):
                raise ValueError("internal-physical not enough information")

            inner_ifs.append(self._get_internal_if_info(
                tmp, self._if_type_phy))

        lag_ifs = []
        lag_mem_ifs = []

        for tmp in device_mes.get("internal-lag", ()):
            if not tmp.get("name"):
                raise ValueError("internal-lag not enough information")

            inner_ifs.append(self._get_internal_if_info(
                tmp, self._if_type_lag))

            if tmp.get("internal-interface"):
                for lag_mem in tmp.get("internal-interface"):
                    if (not lag_mem.get("name")or
                            lag_mem.get("operation")is None):
                        raise ValueError(
                            "internal-interface not enough information ")
                    lag_mem_ifs.append(
                        self._get_lag_mem_if_info(tmp, lag_mem))

        return phy_ifs, lag_ifs, lag_mem_ifs, inner_ifs

    @decorater_log
    def _get_internal_link_addr_in_db(self, db_info, if_name):
        '''
        Obtain internal Link's address which is stored in DB.
        '''
        for tmp_if in db_info["internal-link"]:
            if tmp_if.get("if_name") == if_name:
                return tmp_if.get("ip_address"), tmp_if.get("ip_prefix")

    @decorater_log
    def _get_del_internal_link_from_ec(self,
                                       device_mes,
                                       service=None,
                                       operation=None,
                                       db_info=None):
        '''
        Obtain EC message/DB information regarding
        internal Link (LAG) for deletion.
        '''
        inner_ifs = []

        phy_ifs = []

        for tmp_if in device_mes.get("internal-physical", ()):
            if not tmp_if.get("name"):
                raise ValueError("internal-physical not enough information")

            tmp = tmp_if.copy()
            tmp["address"], tmp["prefix"] = \
                self._get_internal_link_addr_in_db(db_info,
                                                   tmp.get("name"))

            inner_ifs.append(tmp.get("name"))
            phy_ifs.append(self._get_internal_if_info(tmp, self._if_type_phy))

        lag_ifs = []
        lag_mem_ifs = []

        for tmp_if in device_mes.get("internal-lag", ()):
            if (not tmp_if.get("name") or
                    tmp_if.get("minimum-links") is None or
                not tmp_if.get("internal-interface") or
                    len(tmp_if["internal-interface"]) == 0):
                raise ValueError("internal-lag not enough information")

            tmp = tmp_if.copy()
            tmp["address"], tmp["prefix"] = \
                self._get_internal_link_addr_in_db(db_info,
                                                   tmp.get("name"))

            inner_ifs.append(tmp.get("name"))
            lag_ifs.append(self._get_internal_if_info(tmp, self._if_type_lag))

            for lag_mem in tmp.get("internal-interface"):
                if not lag_mem.get("name"):
                    raise ValueError(
                        "internal-interface not enough information ")
                lag_mem_ifs.append(self._get_lag_mem_if_info(tmp, lag_mem))

        return phy_ifs, lag_ifs, lag_mem_ifs, inner_ifs

    @decorater_log
    def _get_internal_if_info(self, if_info, if_type=None):
        '''
        Obtain information of internal Link from EC message.
        (regardless of physical or LAG)
        '''

        op_node_type = None
        op_node_vpn = None
        if_prefix = None
        if if_info.get("prefix"):
            if_prefix = self._conversion_cidr2mask(if_info.get("prefix"), 4)

        tmp = {
            "IF-TYPE": if_type,
            "IF-NAME": if_info.get("name"),
            "IF-ADDR": if_info.get("address"),
            "IF-PREFIX": if_prefix,
            "IF-COST": if_info.get("cost"),
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
        Obtain EC message related to IF open/close.
        '''

        phy_ifs = []

        for tmp in device_mes.get("interface-physical", ()):
            if (not tmp.get("name") or
                    tmp.get("condition") is None):
                raise ValueError("internal-physical not enough information")

            phy_ifs.append(self._get_if_condition_info(tmp, self._if_type_phy))

        lag_ifs = []

        for tmp in device_mes.get("internal-lag", ()):
            if (not tmp.get("name") or
                    tmp.get("condition") is None):
                raise ValueError("internal-lag not enough information")

            lag_ifs.append(self._get_if_condition_info(tmp, self._if_type_lag))

        return phy_ifs, lag_ifs

    @decorater_log
    def _get_if_condition_info(self, if_info, if_type=None):
        '''
        Obtain information of internal Link from EC message.
        (regardless of physical or LAG)
        '''
        tmp = {
            "IF-NAME": if_info.get("name"),
            "IF-CONDITION": if_info.get("condition")
        }
        return tmp

    @decorater_log
    def _get_vrf_name_from_db(self, db_info, slice_name):
        '''
        Obtain VRF name from DB based on Slice name.
        '''
        if_name = None
        vlan_id = None
        cps = db_info.get("cp", ())
        for tmp_cp in cps:
            if tmp_cp.get("slice_name") == slice_name:
                if_name = tmp_cp["if_name"]
                vlan_id = tmp_cp["vlan"]["vlan_id"]

        if if_name is not None:
            vrf_dtls = db_info.get("vrf_detail", ())
            for vrf_dtl in vrf_dtls:
                if (vrf_dtl.get("if_name") == if_name and
                        vrf_dtl.get("vlan_id") == vlan_id):
                    return vrf_dtl.get("vrf_name")
        return None

    def _check_del_static_result(self, cps, device_info, slice_name):
        '''
        Judgment on whether static totally disappears from device
        or totally disappears from Slice or not after being deleted.
        '''
        is_last_cp = True
        is_last_static = True
        for db_cp in device_info.get("cp", ()):
            if db_cp.get("protocol_flags", {}).get("static", False) is False:
                continue
            if db_cp.get("slice_name") != slice_name:
                is_last_cp = False
                continue
            if (self._get_ec_static_count(
                    db_cp["if_name"], db_cp["vlan"]["vlan_id"], cps) !=
                    self._get_db_static_count(
                    db_cp["if_name"], db_cp["vlan"]["vlan_id"], device_info)):
                is_last_static = False
        return is_last_cp, is_last_static

    def _get_ec_static_count(self, if_name, vlan_id, cps):
        '''
        Count the no. of static routes inside the applicable CP(IF name,vlan_id)(EC message)
        '''
        for tmp_cp in cps:
            if (tmp_cp["L3-CE-IF-NAME"] == if_name and
                    int(tmp_cp["L3-CE-IF-VLAN"]) == vlan_id):
                return len(tmp_cp["STATIC"])
        return 0

    def _get_db_static_count(self, if_name, vlan_id, db_info):
        '''
        Count static route inside the applicable CP (IF name,vlan_id)
        (inside DB).But, do not check whether slice is the same or not.
        '''
        count = 0
        for tmp_cp in db_info.get("static_detail", ()):
            if (tmp_cp["if_name"] == if_name and
                    tmp_cp["vlan_id"] == vlan_id):
                if tmp_cp.get("ipv4") is not None and \
                        tmp_cp.get("ipv4").get("nexthop") is not None:
                    count = count + 1
                if tmp_cp.get("ipv6") is not None and \
                        tmp_cp.get("ipv6").get("nexthop") is not None:
                    count = count + 1
        return count

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
        tmp = {
            "IF-NAME": lag_mem_if.get("name"),
            "LAG-IF-NAME": lag_if["name"].lstrip("Bundle-Ether"),
            "OPERATION": lag_mem_if.get("operation")}
        return tmp


    @decorater_log
    def _set_host_name(self, xml_obj, host_name=None):
        '''
        Set the host name.
        '''
        node_1 = self._set_xml_tag(xml_obj,
                                   "host-names",
                                   "xmlns",
                                   "http://cisco.com/ns/yang/" +
                                   "Cisco-IOS-XR-shellutil-cfg",
                                   None)
        self._set_xml_tag(node_1, "host-name", None, None, host_name)

    @decorater_log
    def _set_loopback_address(self, xml_obj, address=None, netmask=None):
        '''
        Set loopback address.
        '''
        node_1 = self._set_xml_tag(xml_obj, "interface-configuration")
        self._set_xml_tag(node_1, "active", None, None, "act")
        self._set_xml_tag(node_1, "interface-name", None, None, "Loopback0")
        self._set_xml_tag(node_1, "interface-virtual")
        node_2 = self._set_xml_tag(node_1,
                                   "ipv4-network",
                                   "xmlns",
                                   "http://cisco.com/ns/yang/" +
                                   "Cisco-IOS-XR-ipv4-io-cfg",
                                   None)
        node_3 = self._set_xml_tag(node_2, "addresses")
        node_4 = self._set_xml_tag(node_3, "primary")
        self._set_xml_tag(node_4, "address", None, None, address)
        tmp_mask = self._conversion_cidr2mask(netmask)
        self._set_xml_tag(node_4, "netmask", None, None, tmp_mask)

    def _set_breakout_interfaces(self, xml_ifs, breakout_ifs, operation=None):
        '''
        Set all breakout IF.
        '''
        for br_if in breakout_ifs:
            self._set_breakout_interface(xml_ifs,
                                         br_if["IF-NAME"],
                                         br_if["BREAKOUT-NUM"],
                                         br_if["SPEED"],
                                         operation)

    @decorater_log
    def _set_breakout_interface(self,
                                xml_ifs,
                                base_if,
                                breakout_num,
                                speed,
                                operation=None):
        '''
        Conduct breakout IF settings under interfaces.
        '''
        attr, attr_val = self._get_attr_from_operation(operation)

        if_name = re.search("([0-9]{1,}/[0-9]{1,}/[0-9]{1,}/[0-9]{1,}.*)",
                            base_if).groups()[0]

        self._base_breakout_if_prefixs.append(if_name)

        node_1 = self._set_xml_tag(xml_ifs,
                                   "interface-configuration",
                                   attr,
                                   attr_val)
        self._set_xml_tag(node_1, "active", None, None, "act")
        self._set_xml_tag(node_1,
                          "interface-name",
                          None,
                          None,
                          "Optics%s" % (if_name,))
        node_2 = self._set_xml_tag(node_1,
                                   "optics",
                                   "xmlns",
                                   "http://cisco.com/ns/yang/" +
                                   "Cisco-IOS-XR-controller-optics-cfg",
                                   None)
        self._set_xml_tag(node_2,
                          "breakout",
                          "xmlns",
                          "http://cisco.com/ns/yang/" +
                          "Cisco-IOS-XR-optics-driver-cfg",
                          "%sx%s" % (breakout_num, speed))
        return node_1

    @decorater_log
    def _set_ospf_infra_plane(self, xml_obj, service=None):
        '''
        Set the fixed section of IPv4 OSPF settings
        on MSF infrastructure side as xml of argument.
        '''
        node_1 = self._set_xml_tag(xml_obj,
                                   "ospf",
                                   "xmlns",
                                   "http://cisco.com/ns/yang/" +
                                   "Cisco-IOS-XR-ipv4-ospf-cfg",
                                   None)
        node_2 = self._set_xml_tag(node_1, "processes")
        node_3 = self._set_xml_tag(node_2, "process")
        self._set_xml_tag(node_3, "process-name", None, None, "v4_MSF_OSPF")
        node_4 = self._set_xml_tag(node_3, "default-vrf")
        if service in (self.name_spine, self.name_leaf):
            self._set_xml_tag(node_4, "router-id")
            node_5 = self._set_xml_tag(node_4, "process-scope")
            node_6 = self._set_xml_tag(node_5, "dead-interval-minimal")
            self._set_xml_tag(node_6, "interval", None, None, "40")
            self._set_xml_tag(node_5, "hello-interval", None, None, "10")
            node_5 = self._set_xml_tag(node_4, "timers")
            node_6 = self._set_xml_tag(node_5, "spf-timer")
            self._set_xml_tag(node_6, "initial-delay", None, None, "200")
            self._set_xml_tag(node_6, "backoff-increment", None, None, "200")
            self._set_xml_tag(node_6, "max-delay", None, None, "200")
        node_5 = self._set_xml_tag(node_4, "area-addresses")
        self._set_xml_tag(node_3, "start")
        return node_5

    @decorater_log
    def _set_infra_ldp(self, xml_obj, router_id=None, service=None):
        '''
        Set the LDP settings on MSF infrastructure side as xml of argument.
        '''
        node_1 = self._set_xml_tag(xml_obj,
                                   "mpls-ldp",
                                   "xmlns",
                                   "http://cisco.com/ns/yang/" +
                                   "Cisco-IOS-XR-mpls-ldp-cfg",
                                   None)
        self._set_xml_tag(node_1, "enable")
        if service in (self.name_spine, self.name_leaf):
            node_2 = self._set_xml_tag(node_1, "global")
            node_3 = self._set_xml_tag(node_2, "session")
            self._set_xml_tag(node_3, "hold-time", None, None, "180")
        node_2 = self._set_xml_tag(node_1, "default-vrf")
        if service in (self.name_spine, self.name_leaf):
            node_3 = self._set_xml_tag(node_2, "global")
            self._set_xml_tag(node_3, "router-id", None, None, router_id)

    @decorater_log
    def _set_if_confs(self, xml_obj):
        '''
        Set interface-configurations and return its object.
        '''
        return self._set_xml_tag(xml_obj,
                                 "interface-configurations",
                                 "xmlns",
                                 "http://cisco.com/ns/yang/" +
                                 "Cisco-IOS-XR-ifmgr-cfg",
                                 None)

    @decorater_log
    def _set_mp_bgp(self, xml_obj, as_number=None, router_id=None):
        '''
        Set MP-BGP and return its object.
        '''
        node_4 = self._set_bgp_commmon(xml_obj, as_number)

        node_5 = self._set_xml_tag(node_4, "default-vrf")
        node_6 = self._set_xml_tag(node_5, "global")
        node_7 = self._set_xml_tag(node_6, "global-timers")
        self._set_xml_tag(node_7, "keepalive", None, None, "30")
        self._set_xml_tag(node_7, "hold-time", None, None, "90")
        self._set_xml_tag(node_6, "router-id", None, None, router_id)
        node_7 = self._set_xml_tag(node_6, "update-delay")
        self._set_xml_tag(node_7, "delay", None, None, "0")
        self._set_xml_tag(node_7, "always", None, None, "false")
        node_7 = self._set_xml_tag(node_6, "global-afs")
        self._set_bgp_global_af(node_7)

        node_6 = self._set_xml_tag(node_5, "bgp-entity")
        node_7 = self._set_xml_tag(node_6, "neighbors")
        return node_7

    @decorater_log
    def _set_bgp_global_af(self, xml_obj):
        '''
        Set global-af of MP-BGP settings under global-afs.
        '''
        node_8 = self._set_xml_tag(xml_obj, "global-af")
        self._set_xml_tag(node_8, "af-name", None, None, "vp-nv4-unicast")
        self._set_xml_tag(node_8, "enable")

    @decorater_log
    def _set_bgp_commmon(self, xml_obj, as_number=None):
        '''
        Set BGP common section and return its object.
        '''
        node_1 = self._set_xml_tag(xml_obj,
                                   "bgp",
                                   "xmlns",
                                   "http://cisco.com/ns/yang/" +
                                   "Cisco-IOS-XR-ipv4-bgp-cfg",
                                   None)
        node_2 = self._set_xml_tag(node_1, "instance")
        self._set_xml_tag(node_2, "instance-name", None, None, "default")
        node_3 = self._set_xml_tag(node_2, "instance-as")
        self._set_xml_tag(node_3, "as", None, None, "0")
        node_4 = self._set_xml_tag(node_3, "four-byte-as")
        self._set_xml_tag(node_4, "as", None, None, as_number)
        self._set_xml_tag(node_4, "bgp-running")
        return node_4

    @decorater_log
    def _set_merge_slice_vrf(self, xml_obj, vrf_name=None, rt=None):
        '''
        Set VRF of L3Slice.
        '''
        node_1 = self._set_xml_tag(xml_obj,
                                   "vrfs",
                                   "xmlns",
                                   "http://cisco.com/ns/yang/" +
                                   "Cisco-IOS-XR-infra-rsi-cfg",
                                   None)
        node_2 = self._set_xml_tag(node_1, "vrf")
        self._set_xml_tag(node_2, "vrf-name", None, None, vrf_name)
        self._set_xml_tag(node_2, "create")
        node_3 = self._set_xml_tag(node_2, "afs")
        self._set_vrf_af(node_3, rt)
        return node_3

    @decorater_log
    def _set_vrf_af(self, xml_obj, rt=None, af_name="ipv4"):
        node_4 = self._set_xml_tag(xml_obj, "af")
        self._set_xml_tag(node_4, "af-name", None, None, af_name)
        self._set_xml_tag(node_4, "saf-name", None, None, "unicast")
        self._set_xml_tag(node_4, "topology-name", None, None, "default")
        self._set_xml_tag(node_4, "create")
        node_5 = self._set_xml_tag(node_4,
                                   "bgp",
                                   "xmlns",
                                   "http://cisco.com/ns/yang/" +
                                   "Cisco-IOS-XR-ipv4-bgp-cfg",
                                   None)
        self._set_xml_tag(
            node_5, "import-route-policy", None, None, "VRF_policy")
        node_6 = self._set_xml_tag(node_5, "import-route-targets")
        node_7 = self._set_xml_tag(node_6, "route-targets")
        node_8 = self._set_xml_tag(node_7, "route-target")
        self._set_xml_tag(node_8, "type", None, None, "as")
        node_9 = self._set_xml_tag(node_8, "as-or-four-byte-as")
        self._set_xml_tag(node_9, "as-xx", None, None, "0")
        self._set_xml_tag(node_9, "as")
        self._set_xml_tag(node_9, "as-index")
        self._set_xml_tag(node_9, "stitching-rt", None, None, "0")

        self._set_xml_tag(
            node_5, "export-route-policy", None, None, "VRF_policy")
        node_6 = self._set_xml_tag(node_5, "export-route-targets")
        node_7 = self._set_xml_tag(node_6, "route-targets")
        node_8 = self._set_xml_tag(node_7, "route-target")
        self._set_xml_tag(node_8, "type", None, None, "as")
        node_9 = self._set_xml_tag(node_8, "as-or-four-byte-as")
        self._set_xml_tag(node_9, "as-xx", None, None, "0")
        self._set_xml_tag(node_9, "as")
        self._set_xml_tag(node_9, "as-index")
        self._set_xml_tag(node_9, "stitching-rt", None, None, "0")

    @decorater_log
    def _set_router_static_common(self, xml_obj, vrf_name=None):
        '''
        Set common section for router-static.
        '''
        node_1 = self._set_xml_tag(xml_obj,
                                   "router-static",
                                   "xmlns",
                                   "http://cisco.com/ns/yang/" +
                                   "Cisco-IOS-XR-ip-static-cfg",
                                   None)
        node_2 = self._set_xml_tag(node_1, "vrfs")
        node_3 = self._set_xml_tag(node_2, "vrf")
        self._set_xml_tag(node_3, "vrf-name", None, None, vrf_name)
        node_4 = self._set_xml_tag(node_3, "address-family")
        return node_4

    @decorater_log
    def _set_slice_bgp(self, xml_obj, **params):
        '''
        Shuld be set in case that VLANIF uses BGP.
        Argument.
            params : Variable argument
                     (parameter group necessary for bgp settings )
                vrf_name     : VRF name
                as_number    : AS number
                vrf_rd       : VRF's RD
                vrf_router_id: ROUTER No. of VRF
        '''
        node_4 = self._set_bgp_commmon(xml_obj, params.get("as_number"))
        node_5 = self._set_xml_tag(node_4, "vrfs")
        node_6 = self._set_xml_tag(node_5, "vrf")
        self._set_xml_tag(
            node_6, "vrf-name", None, None, params.get("vrf_name"))
        self._set_bgp_vrf_global(node_6)

        node_7 = self._set_xml_tag(node_6, "vrf-neighbors")
        return node_7

    def _set_bgp_vrf_global(self, xml_obj, rd=None, router_id=None):
        '''
        Conduct vrf-global settings inside bgp.
        '''
        node_7 = self._set_xml_tag(xml_obj, "vrf-global")
        self._set_xml_tag(node_7, "exists")
        node_8 = self._set_xml_tag(node_7, "route-distinguisher")
        self._set_xml_tag(node_8, "type", None, None, "as")
        self._set_xml_tag(node_8, "as-xx", None, None, "0")
        self._set_xml_tag(node_8, "as")
        self._set_xml_tag(node_8, "as-index")
        self._set_xml_tag(node_7, "router-id")
        node_8 = self._set_xml_tag(node_7, "vrf-global-afs")
        self._set_bgp_vrf_global_af(node_8)
        return node_8

    def _set_bgp_vrf_global_af(self, xml_obj, ip_version=4):
        '''
        Conduct af settings of vrf-global inside bgp.
        '''
        af_name = "ipv%(ip_ver)d-unicast" % {"ip_ver": ip_version}
        policy = "v%(ip_ver)d_Redist_To_BGP_in_VRF" % {"ip_ver": ip_version}

        node_9 = self._set_xml_tag(xml_obj, "vrf-global-af")
        self._set_xml_tag(node_9, "af-name", None, None, af_name)
        self._set_xml_tag(node_9, "enable")
        node_10 = self._set_xml_tag(node_9, "label-mode")
        self._set_xml_tag(
            node_10, "label-allocation-mode", None, None, "per-vrf")
        node_10 = self._set_xml_tag(node_9, "connected-routes")
        self._set_xml_tag(node_10, "route-policy-name", None, None, policy)
        node_10 = self._set_xml_tag(node_9, "static-routes")
        self._set_xml_tag(node_10, "route-policy-name", None, None, policy)

    @decorater_log
    def _set_slice_vrrp(self, xml_obj, **params):
        '''
        Shuld be set in case that VLANIF uses VRRP.
        Argument.
            params : variable argument
                    (parameter group necessary for bgp settings )
                vrf_name     : VRF name
                as_number    : AS number
                vrf_rd       : VRF's RD
                vrf_router_id: ROUTER No. of VRF
        '''
        node_1 = self._set_xml_tag(xml_obj,
                                   "vrrp",
                                   "xmlns",
                                   "http://cisco.com/ns/yang/" +
                                   "Cisco-IOS-XR-ipv4-vrrp-cfg",
                                   None)
        node_2 = self._set_xml_tag(node_1, "interfaces")
        return node_2

    @decorater_log
    def _get_owner(self, if_name):
        '''
        Obtain the value to be set to the owner from IF name.
        '''
        return_val = None
        for ownernameKey in CiscoDriver.__cisco_proper_config.keys():
            if ownernameKey in if_name:
                return_val = \
                    CiscoDriver.__cisco_proper_config.get(ownernameKey)
                break
        return return_val

    @decorater_log
    def _set_internal_links(self, if_node, phy_ifs, lag_ifs, lag_mem_ifs):
        '''
        Conduct all the IF settings of internal Link.
        (regardless of physical or LAG)
        '''
        for tmp_if in phy_ifs:
            self._set_internal_link(if_node, tmp_if, self._if_type_phy)
        for tmp_if in lag_ifs:
            self._set_internal_link(if_node, tmp_if, self._if_type_lag)
        for tmp_if in lag_mem_ifs:
            self._set_lag_mem_if(if_node, tmp_if)

    @decorater_log
    def _set_internal_link(self, if_node, if_info, if_type):
        '''
        Conduct IF settings of internal Link.
        '''
        if if_type == self._if_type_phy:
            node_2 = self._set_xml_tag(if_node, "interface-configuration")
            self._set_xml_tag(node_2, "active", None, None, "act")
            self._set_xml_tag(node_2,
                              "interface-name",
                              None,
                              None,
                              if_info["IF-NAME"])
        else:
            node_2 = self._set_lag_if(if_node, if_info)
        node_3 = self._set_xml_tag(node_2, "mtus")
        node_4 = self._set_xml_tag(node_3, "mtu")
        self._set_xml_tag(node_4,
                          "owner",
                          None,
                          None,
                          self._get_owner(if_info["IF-NAME"]))
        self._set_xml_tag(node_4, "mtu", None, None, "4110")
        self._set_internal_link_qos(node_2)
        node_3 = self._set_xml_tag(node_2,
                                   "ipv4-network",
                                   "xmlns",
                                   "http://cisco.com/ns/yang/" +
                                   "Cisco-IOS-XR-ipv4-io-cfg",
                                   None)
        node_4 = self._set_xml_tag(node_3, "addresses")
        node_5 = self._set_xml_tag(node_4, "primary")
        self._set_xml_tag(node_5,
                          "address",
                          None,
                          None,
                          if_info["IF-ADDR"])
        self._set_xml_tag(node_5,
                          "netmask",
                          None,
                          None,
                          if_info["IF-PREFIX"])
        if if_type == self._if_type_phy:
            self._set_up_physical_if(node_2, if_info["IF-NAME"])
        return node_2

    @decorater_log
    def _set_up_physical_if(self, if_node, if_name):
        '''
        Establish physical IF. (set no shutdown)
        '''
        if not self._check_new_breakifs(if_name):
            self._set_xml_tag(if_node,
                              "shutdown",
                              self._ATRI_OPE,
                              self._DELETE,
                              None)

    @decorater_log
    def _check_new_breakifs(self, if_name):
        '''
        Check whether it is the breakoutIF which will be newly set
        when IF name is edit-config.
        '''
        for breakout_prefix in self._base_breakout_if_prefixs:
            if breakout_prefix + "/" in if_name:
                return True
        return False

    @decorater_log
    def _set_internal_link_qos(self, if_node, operation=None):
        attr, attr_val = self._get_attr_from_operation(operation)
        node_3 = self._set_xml_tag(if_node,
                                   "qos",
                                   "xmlns",
                                   "http://cisco.com/ns/yang/" +
                                   "Cisco-IOS-XR-qos-ma-cfg",
                                   None)
        node_4 = self._set_xml_tag(node_3, "input")
        node_5 = self._set_xml_tag(node_4,
                                   "service-policy",
                                   attr,
                                   attr_val,
                                   None)
        self._set_xml_tag(node_5,
                          "service-policy-name",
                          None,
                          None,
                          "in_msf_policy")
        node_4 = self._set_xml_tag(node_3, "output")
        node_5 = self._set_xml_tag(node_4,
                                   "service-policy",
                                   attr,
                                   attr_val,
                                   None)
        self._set_xml_tag(node_5,
                          "service-policy-name",
                          None,
                          None,
                          "out_msf_policy_scheduling")
        return node_3

    @decorater_log
    def _set_del_internal_link(self, if_node, if_info, if_type):
        '''
        Conduct IF settings of internal Link.
        '''
        if if_type == self._if_type_phy:
            node_2 = self._set_xml_tag(if_node, "interface-configuration")
            self._set_xml_tag(node_2, "active", None, None, "act")
            self._set_xml_tag(node_2,
                              "interface-name",
                              None,
                              None,
                              if_info["IF-NAME"])
        else:
            node_2 = self._set_del_lag_if(if_node, if_info)
            return node_2
        node_3 = self._set_xml_tag(node_2, "mtus")
        node_4 = self._set_xml_tag(node_3, "mtu", self._ATRI_OPE, self._DELETE)
        self._set_xml_tag(node_4,
                          "owner",
                          None,
                          None,
                          self._get_owner(if_info["IF-NAME"]))
        self._set_internal_link_qos(node_2, operation=self._DELETE)
        node_3 = self._set_xml_tag(node_2,
                                   "ipv4-network",
                                   "xmlns",
                                   "http://cisco.com/ns/yang/" +
                                   "Cisco-IOS-XR-ipv4-io-cfg",
                                   None)
        node_4 = self._set_xml_tag(node_3, "addresses")
        node_5 = self._set_xml_tag(node_4,
                                   "primary",
                                   self._ATRI_OPE,
                                   self._DELETE)
        self._set_xml_tag(node_5,
                          "address",
                          None,
                          None,
                          if_info["IF-ADDR"])
        self._set_xml_tag(node_5,
                          "netmask",
                          None,
                          None,
                          if_info["IF-PREFIX"])
        self._set_xml_tag(node_2, "shutdown")
        return node_2

    @decorater_log
    def _set_lag_if(self, if_node, lag_if):
        '''
        Set LAGIF. (if_node becomes parent)
        '''
        node_2 = self._set_xml_tag(if_node, "interface-configuration")
        self._set_xml_tag(node_2, "active", None, None, "act")
        self._set_xml_tag(node_2,
                          "interface-name",
                          None,
                          None,
                          lag_if["IF-NAME"])
        self._set_xml_tag(node_2, "interface-virtual")
        if lag_if["LAG-LINKS"] > 0:
            node_3 = self._set_xml_tag(node_2,
                                       "bundle",
                                       "xmlns",
                                       "http://cisco.com/ns/yang/" +
                                       "Cisco-IOS-XR-bundlemgr-cfg",
                                       None)
            node_4 = self._set_xml_tag(node_3, "minimum-active")
            self._set_xml_tag(node_4,
                              "links",
                              None,
                              None,
                              lag_if["LAG-LINKS"])
        return node_2

    @decorater_log
    def _set_update_lag_if(self, if_node, lag_if, lag_type=None):
        '''
        Set LAG IF(if_node becomes parent)
        '''
        node_1 = self._set_xml_tag(if_node, "interface-configuration")
        self._set_xml_tag(node_1, "active", None, None, "act")
        self._set_xml_tag(node_1,
                          "interface-name",
                          None,
                          None,
                          lag_if["IF-NAME"])
        if lag_type == self.name_celag:
            self._set_xml_tag(node_1, "interface-virtual")
        if lag_if["LAG-LINKS"] > 0:
            node_2 = self._set_xml_tag(node_1,
                                       "bundle",
                                       "xmlns",
                                       "http://cisco.com/ns/yang/" +
                                       "Cisco-IOS-XR-bundlemgr-cfg",
                                       None)
            node_3 = self._set_xml_tag(node_2, "minimum-active")
            self._set_xml_tag(node_3,
                              "links",
                              self._ATRI_OPE,
                              self._REPLACE,
                              lag_if["LAG-LINKS"])
        return node_1

    @decorater_log
    def _set_del_lag_if(self, if_node, lag_if):
        '''
        Set the LAGIF for deletion. (if_node becomes parent)
        '''
        node_2 = self._set_xml_tag(if_node,
                                   "interface-configuration",
                                   self._ATRI_OPE,
                                   self._DELETE,
                                   None)
        self._set_xml_tag(node_2, "active", None, None, "act")
        self._set_xml_tag(node_2,
                          "interface-name",
                          None,
                          None,
                          lag_if["IF-NAME"])
        self._set_xml_tag(node_2, "interface-virtual")
        return node_2

    @decorater_log
    def _set_lag_mem_if(self, if_node, lag_mem_if):
        '''
        Set LAG member. (if_node becomes parent)
        '''
        node_2 = self._set_xml_tag(if_node, "interface-configuration")
        self._set_xml_tag(node_2, "active", None, None, "act")
        self._set_xml_tag(node_2,
                          "interface-name",
                          None,
                          None,
                          lag_mem_if["IF-NAME"])
        node_3 = self._set_xml_tag(node_2,
                                   "bundle-member",
                                   "xmlns",
                                   "http://cisco.com/ns/yang/" +
                                   "Cisco-IOS-XR-bundlemgr-cfg",
                                   None)
        node_4 = self._set_xml_tag(node_3, "id")
        self._set_xml_tag(node_4,
                          "bundle-id",
                          None,
                          None,
                          lag_mem_if["LAG-IF-NAME"])
        self._set_xml_tag(node_4, "port-activity", None, None, "active")
        node_3 = self._set_xml_tag(node_2,
                                   "lacp",
                                   "xmlns",
                                   "http://cisco.com/ns/yang/" +
                                   "Cisco-IOS-XR-bundlemgr-cfg",
                                   None)
        self._set_xml_tag(node_3, "period-short", None, None, "true")
        self._set_up_physical_if(node_2, lag_mem_if["IF-NAME"])
        return node_2

    @decorater_log
    def _set_del_lag_mem_if(self, if_node, lag_mem_if):
        '''
        Set LAG member for deletion. (if_node becomes parent)
        '''
        node_2 = self._set_xml_tag(if_node, "interface-configuration")
        self._set_xml_tag(node_2, "active", None, None, "act")
        self._set_xml_tag(node_2,
                          "interface-name",
                          None,
                          None,
                          lag_mem_if["IF-NAME"])
        node_3 = self._set_xml_tag(node_2,
                                   "bundle-member",
                                   "xmlns",
                                   "http://cisco.com/ns/yang/" +
                                   "Cisco-IOS-XR-bundlemgr-cfg",
                                   None)
        node_3.attrib[self._ATRI_OPE] = self._DELETE
        node_3 = self._set_xml_tag(node_2,
                                   "lacp",
                                   "xmlns",
                                   "http://cisco.com/ns/yang/" +
                                   "Cisco-IOS-XR-bundlemgr-cfg",
                                   None)
        node_3.attrib[self._ATRI_OPE] = self._DELETE
        self._set_xml_tag(node_2, "shutdown")

        return node_2

    @decorater_log
    def _set_lag_mem_if_lag_speed(self, if_node, lag_mem_if):
        '''
        Set LAG member(if_node becomes parent) [for increasing LAG speed]
        '''
        node_2 = self._set_xml_tag(if_node, "interface-configuration")
        self._set_xml_tag(node_2, "active", None, None, "act")
        self._set_xml_tag(node_2,
                          "interface-name",
                          None,
                          None,
                          lag_mem_if["IF-NAME"])
        node_3 = self._set_xml_tag(node_2,
                                   "bundle-member",
                                   "xmlns",
                                   "http://cisco.com/ns/yang/" +
                                   "Cisco-IOS-XR-bundlemgr-cfg",
                                   None)
        node_4 = self._set_xml_tag(node_3, "id")
        self._set_xml_tag(node_4,
                          "bundle-id",
                          None,
                          None,
                          lag_mem_if["LAG-IF-NAME"])
        self._set_xml_tag(node_4, "port-activity", None, None, "active")
        node_3 = self._set_xml_tag(node_2,
                                   "lacp",
                                   "xmlns",
                                   "http://cisco.com/ns/yang/" +
                                   "Cisco-IOS-XR-bundlemgr-cfg",
                                   None)
        self._set_xml_tag(node_3, "period-short", None, None, "true")

        return node_2

    @decorater_log
    def _set_del_lag_mem_if_lag_speed(self, if_node, lag_mem_if):
        '''
        Set LAG member to be deleted (if_node becomes parent) [for decreasing LAG speed]
        '''
        node_2 = self._set_xml_tag(if_node, "interface-configuration")
        self._set_xml_tag(node_2, "active", None, None, "act")
        self._set_xml_tag(node_2,
                          "interface-name",
                          None,
                          None,
                          lag_mem_if["IF-NAME"])
        node_3 = self._set_xml_tag(node_2,
                                   "bundle-member",
                                   "xmlns",
                                   "http://cisco.com/ns/yang/" +
                                   "Cisco-IOS-XR-bundlemgr-cfg",
                                   None)
        node_3.attrib[self._ATRI_OPE] = self._DELETE
        node_3 = self._set_xml_tag(node_2,
                                   "lacp",
                                   "xmlns",
                                   "http://cisco.com/ns/yang/" +
                                   "Cisco-IOS-XR-bundlemgr-cfg",
                                   None)
        node_3.attrib[self._ATRI_OPE] = self._DELETE

        return node_2

    @decorater_log
    def _set_lag_mem_if_state(self, if_node, lag_mem_if):
        '''
        Set LAG member(if_node becomes parent)
        '''
        node_2 = self._set_xml_tag(if_node, "interface")
        self._set_xml_tag(node_2,
                          "name",
                          None,
                          None,
                          lag_mem_if["IF-NAME"])
        node_3 = self._set_xml_tag(node_2, "config")
        self._set_xml_tag(node_3,
                          "name",
                          None,
                          None,
                          lag_mem_if["IF-NAME"])
        self._set_xml_tag(node_3,
                          "type",
                          self._REP_ATRI_XMLNS,
                          "urn:ietf:params:xml:ns:yang:" +
                          "iana-if-type",
                          "idx:ethernetCsmacd")
        upstate = "true"
        if lag_mem_if.get("OPERATION") == "delete":
            upstate = "false"
        self._set_xml_tag(node_3,
                          "enabled",
                          None,
                          None,
                          upstate)

        node_4 = self._set_xml_tag(node_2,
                                   "ethernet",
                                   "xmlns",
                                   "http://openconfig.net/yang/" +
                                   "interfaces/ethernet",
                                   None)
        node_5 = self._set_xml_tag(node_4, "config")
        self._set_xml_tag(node_5, "auto-negotiate", None, None, "false")

        return node_2

    @decorater_log
    def _set_if_condition(self, if_node, lag_if):
        '''
        Set IF close/open(if_node becomes parent)
        '''
        node_2 = self._set_xml_tag(if_node, "interface-configuration")
        self._set_xml_tag(node_2, "active", None, None, "act")
        self._set_xml_tag(node_2,
                          "interface-name",
                          None,
                          None,
                          lag_if["IF-NAME"])
        if lag_if["IF-CONDITION"] == "enable":
            self._set_xml_tag(node_2,
                              "shutdown",
                              self._ATRI_OPE,
                              self._DELETE,
                              None)
        else:
            self._set_xml_tag(node_2, "shutdown")
        return node_2

    @decorater_log
    def _set_ospf_area_data(self,
                            areas_node,
                            area_id,
                            inner_if_names,
                            is_lb=False,
                            operation=None):
        '''
        Set each area of IPv4 OSPF settings on MSF infrastructure side.
        (including IF settings of internal Link)
        '''
        attr, attr_val = self._get_attr_from_operation(operation)

        node_6 = self._set_xml_tag(areas_node, "area-area-id")
        self._set_xml_tag(node_6,
                          "area-id",
                          None,
                          None,
                          area_id)
        if operation != self._REPLACE:
            self._set_xml_tag(node_6, "running")
        node_7 = self._set_xml_tag(node_6, "name-scopes")
        if is_lb:
            node_8 = self._set_xml_tag(node_7, "name-scope")
            self._set_xml_tag(
                node_8, "interface-name", None, None, "Loopback0")
            self._set_xml_tag(node_8, "running")
            self._set_xml_tag(node_8, "cost", None, None, "10")
            self._set_xml_tag(node_8, "passive", None, None, "true")
        for tmp_if_name in inner_if_names:
            if operation == self._REPLACE:
                node_8 = self._set_xml_tag(
                    node_7, "name-scope", attr, attr_val)
                self._set_xml_tag(node_8,
                                  "interface-name",
                                  None,
                                  None,
                                  tmp_if_name["IF-NAME"])
                self._set_xml_tag(node_8, "cost", self._ATRI_OPE,
                                  self._REPLACE,
                                  tmp_if_name["IF-COST"])
            else:
                node_8 = self._set_xml_tag(
                    node_7, "name-scope", attr, attr_val)
                self._set_xml_tag(node_8,
                                  "interface-name",
                                  None,
                                  None,
                                  tmp_if_name)
                if operation == self._DELETE:
                    continue
                self._set_xml_tag(node_8, "running")
                self._set_xml_tag(
                    node_8, "network-type", None, None, "point-to-point")
                self._set_xml_tag(node_8, "cost", None, None, "100")

    @decorater_log
    def _set_ldp_inner_if(self, xml_obj, inner_if_names, operation=None):
        '''
        Add internal Link setting to the infrastructure LDP settings.
        '''
        attr, attr_val = self._get_attr_from_operation(operation)
        node_2 = self._find_xml_node(xml_obj,
                                     "mpls-ldp",
                                     "default-vrf")
        if len(inner_if_names) > 0:
            node_3 = self._set_xml_tag(node_2, "interfaces")
            for tmp_if_name in inner_if_names:
                node_4 = self._set_xml_tag(node_3, "interface", attr, attr_val)
                self._set_xml_tag(node_4,
                                  "interface-name",
                                  None,
                                  None,
                                  tmp_if_name)
                if operation == self._DELETE:
                    continue
                self._set_xml_tag(node_4, "enable")
                node_5 = self._set_xml_tag(node_4, "global")
                node_6 = self._set_xml_tag(node_5, "discovery")
                node_7 = self._set_xml_tag(node_6, "link-hello")
                self._set_xml_tag(node_7, "hold-time", None, None, "15")
                self._set_xml_tag(node_7, "interval", None, None, "5")

    @decorater_log
    def _set_mp_bgp_neighbor(self, nbrs_node, rr_addr, as_number):
        '''
        Set the neighbor of MP-BGP.
        '''
        node_8 = self._set_xml_tag(nbrs_node, "neighbor")
        self._set_xml_tag(node_8,
                          "neighbor-address",
                          None,
                          None,
                          rr_addr)
        node_9 = self._set_xml_tag(node_8, "remote-as")
        self._set_xml_tag(node_9, "as-xx", None, None, "0")
        self._set_xml_tag(node_9,
                          "as-yy",
                          None,
                          None,
                          str(as_number))
        self._set_xml_tag(
            node_8, "update-source-interface", None, None, "Loopback0")
        node_9 = self._set_xml_tag(node_8, "neighbor-afs")
        node_10 = self._set_xml_tag(node_9, "neighbor-af")
        self._set_xml_tag(node_10, "af-name", None, None, "vp-nv4-unicast")
        self._set_xml_tag(node_10, "activate")
        self._set_xml_tag(
            node_10, "route-policy-in", None, None, "VPN_import")
        self._set_xml_tag(
            node_10, "route-policy-out", None, None, "VPN_export")

    @decorater_log
    def _set_static_cp_info(self,
                            xml_obj,
                            cps,
                            vrf_name,
                            is_last_cp=False,
                            is_last_static=False,
                            operation=None):
        '''
        Set the router-static and below.
        '''
        if operation == self._DELETE and is_last_cp:
            self._set_xml_tag(xml_obj,
                              "router-static",
                              self._ATRI_OPE,
                              self._DELETE)
            return

        node_1 = self._set_router_static_common(xml_obj, vrf_name)

        if operation == self._DELETE and is_last_static:
            node_2 = self._find_xml_node(xml_obj,
                                         "router-static",
                                         "vrfs",
                                         "vrf")
            node_3 = self._find_xml_node(xml_obj,
                                         "router-static",
                                         "vrfs",
                                         "vrf",
                                         "address-family")
            node_2.remove(node_3)
            node_2.attrib[self._ATRI_OPE] = self._DELETE
            return

        self._set_static_routes(node_1, cps)
        return

    @decorater_log
    def _set_static_routes(self, family_node, cps, ip_ver=4, operation=None):
        '''
        Set the vrfipv4 and below of StaticCP.
        '''
        vrfip_name = "vrfipv4"
        static_ip_name = "STATIC"

        node_5 = self._set_xml_tag(family_node, vrfip_name)
        node_6 = self._set_xml_tag(node_5, "vrf-unicast")
        node_7 = self._set_xml_tag(node_6, "vrf-prefixes")
        for tmp_cp in cps:
            for route in tmp_cp.get(static_ip_name, ()):
                ope = route.get("OPERATION", operation)
                self._set_add_static_route(
                    node_7,
                    route,
                    self._set_vlan_if_name(tmp_cp["L3-CE-IF-NAME"],
                                           tmp_cp["L3-CE-IF-VLAN"]),
                    operation=ope)

    @decorater_log
    def _set_add_static_route(self,
                              vrf_pres_node,
                              static_route,
                              cp_if_name,
                              operation=None):
        '''
        Set the vrf-prefix and below of StaticCP.
        '''
        attr, attr_val = self._get_attr_from_operation(operation)
        node_2 = self._set_xml_tag(vrf_pres_node, "vrf-prefix")
        self._set_xml_tag(node_2,
                          "prefix",
                          None,
                          None,
                          static_route["L3-STATIC-ROUTE-ADD"])
        self._set_xml_tag(node_2,
                          "prefix-length",
                          None,
                          None,
                          static_route["L3-STATIC-ROUTE-PREFIX"])
        node_3 = self._set_xml_tag(node_2, "vrf-route")
        node_4 = self._set_xml_tag(node_3, "vrf-next-hop-table")
        node_5 = self._set_xml_tag(
            node_4,
            "vrf-next-hop-interface-name-next-hop-address",
            attr,
            attr_val)
        self._set_xml_tag(node_5,
                          "interface-name",
                          None,
                          None,
                          cp_if_name)
        self._set_xml_tag(node_5,
                          "next-hop-address",
                          None,
                          None,
                          static_route["L3-STATIC-ROUTE-NEXT"])

    @decorater_log
    def _check_breakout_if_name(self,
                                breakout_ifs=[]):
        for br_if in breakout_ifs:
            re.search("([0-9]{1,}/[0-9]{1,}/[0-9]{1,}/[0-9]{1,}.*)",
                      br_if["IF-NAME"]).groups()[0]
