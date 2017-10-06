# -*- coding: utf-8 -*-
import json
from lxml import etree
from EmSeparateDriver import EmSeparateDriver
from EmCommonLog import decorater_log
from codecs import BOM_UTF8
import os
import GlobalModule


class CiscoDriver(EmSeparateDriver):
    
    __cisco_proper_config = {}

    __POLICY_3 = \
        "route-policy VPN_export\nset community " + \
        "MSF_belonging_side additive\nend-policy\n"
    __POLICY_4 = \
        "route-policy VPN_import\n" + \
        "if community matches-any MSF_belonging_side then\n" + \
        "  set local-preference 200\n" + \
        "  pass\n" + \
        "else\n" + \
        "  set local-preference 50\n" + \
        "  pass\n" + \
        "endif\n" + \
        "end-policy\n"
    __POLICY_5 = \
        "route-policy eBGPv4_To_CE_import\n" + \
        "if community matches-any MSF_community then\n" + \
        "  delete community in MSF_community\n" + \
        "else\n" + \
        "  pass\n" + \
        "endif\n" + \
        "end-policy\n"
    __POLICY_6 = \
        "route-policy eBGPv4_To_active-CE_export\n" + \
        " if community matches-any MSF_community then\n" + \
        "  delete community in MSF_community\n" + \
        " endif\n" + \
        " set med 500\n" + \
        " set origin igp\n" + \
        " pass\n" + \
        " end-policy\n"
    __POLICY_7 = \
        "route-policy eBGPv4_To_standby-CE_export\n" + \
        " if community matches-any MSF_community then\n" + \
        "  delete community in MSF_community\n" + \
        " endif\n" + \
        " set med 1000\n" + \
        " set origin igp\n" + \
        " pass\n" + \
        " end-policy\n"

    _XC_ATRI_OPE = "xc:operation"
    _ATRI_OPE = "xc_operation"
    _DELETE = "delete"
    _XC_NS = "xc"
    _XC_NS_MAP = "urn:ietf:params:xml:ns:netconf:base:1.0"

    @decorater_log
    def connect_device(self,
                       device_name, device_info, service_type, order_type):
        tmp_device_info = None
        if device_info is not None:
            tmp_json = json.loads(device_info)
            if tmp_json.get("device_info") is not None:
                tmp_json["device_info"]["port_number"] = 22
            tmp_device_info = json.dumps(tmp_json)
        return self.as_super.connect_device(device_name,
                                            tmp_device_info,
                                            service_type,
                                            order_type)

    @decorater_log
    def __init__(self):
        self.as_super = super(CiscoDriver, self)
        self.as_super.__init__()
        if not CiscoDriver.__cisco_proper_config:
            try:
            except IOError:
                raise
            
            tmp_list=[]           
            for value in conf_list:
                    tmp_line = value.strip()
                    tmp_list.append(tmp_line)
            
            index = 0
            for item in tmp_list:
                tmp = item.split(splitter_conf)[1]
                tmp_value_list.append(tmp)
            max_index = len(tmp_value_list) - 1
            while index < max_index:
                tmp_key = tmp_value_list[index]
                tmp_value = tmp_value_list[index + 1]
                conf_dict[tmp_key] = tmp_value
                index += 2
            CiscoDriver.__cisco_proper_config = conf_dict
            self.common_util_log.logging(
                " ", self.log_level_debug,
                "Update proper config:", CiscoDriver.__cisco_proper_config)
        else:
            pass
        self.list_enable_service = [self.name_spine,
                                    self.name_leaf,
                                    self.name_l3_slice,
                                    self.name_celag,
                                    self.name_internal_lag]
        self.get_config_message = {
            self.name_spine: (
            ),
            self.name_leaf: (
            ),
            self.name_l3_slice: (
            ),
            self.name_celag: (
            ),
            self.name_internal_lag: (
            )}

    @staticmethod
    @decorater_log
    def __policy_1(lf_bgp_com_wild):
        policy = "community-set MSF_community\n" + \
                 "%s\n" % (lf_bgp_com_wild,) + \
                 "end-set\n"
        return policy

    @staticmethod
    @decorater_log
    def __policy_2(lf_bgp_community):
        policy = "community-set MSF_belonging_side\n" + \
                 "%s\n" % (lf_bgp_community,) + \
                 "end-set\n"
        return policy

    @decorater_log
    def _send_control_signal(self,
                             device_name,
                             message_type,
                             send_message=None,
                             service_type=None,
                             operation=None):
        if (message_type == "edit-config" and
                service_type in (self.name_celag, self.name_internal_lag) and
                operation == "delete" and send_message is not None):
            send_xml = etree.fromstring(send_message)
            is_one_node = bool(len(send_xml) == 1)
            lag_mem = self._gen_top_node_edit_config()
            lag_mem.append(send_xml[-1])
            send_mes_1 = self._replace_xc_delete(etree.tostring(lag_mem))
            is_result, message = \
                self.as_super._send_control_signal(device_name,
                                                   message_type,
                                                   send_mes_1)
            if not is_result:
                return False, None
            elif is_one_node:
                return is_result, message
            else:
                send_mes_2 = self._replace_xc_delete(etree.tostring(send_xml))
                return (self.as_super.
                        _send_control_signal(device_name,
                                             message_type,
                                             send_mes_2))
        else:
            tmp_send = self._replace_xc_delete(send_message)
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
    def _gen_top_node_edit_config(self):
        str_map = {"ns": self._XC_NS,
                   "tag": self._send_message_top_tag,
                   "nsmap": self._XC_NS_MAP}
        return etree.fromstring(xml_str % str_map)

    @decorater_log
    def _gen_spine_fix_message(self, xml_obj, operation):
        node_1 = self._set_xml_tag(xml_obj,
                                   "host-names",
                                   "xmlns",
                                   "Cisco-IOS-XR-shellutil-cfg",
                                   None)
        self._set_xml_tag(node_1, "host-name")
        node_1 = self._set_xml_tag(xml_obj,
                                   "snmp",
                                   "xmlns",
                                   "Cisco-IOS-XR-snmp-agent-cfg",
                                   None)
        node_2 = self._set_xml_tag(node_1, "trap-hosts")
        node_3 = self._set_xml_tag(node_2, "trap-host")
        self._set_xml_tag(node_3, "ip-address")
        node_4 = self._set_xml_tag(node_3, "default-user-communities")
        node_5 = self._set_xml_tag(node_4, "default-user-community")
        self._set_xml_tag(node_5, "community-name")
        self._set_xml_tag(node_5, "version", None, None, "2c")
        self._set_xml_tag(node_5, "basic-trap-types", None, None, "0")
        self._set_xml_tag(node_5, "advanced-trap-types1", None, None, "0")
        self._set_xml_tag(node_5, "advanced-trap-types2", None, None, "0")

        node_2 = self._set_xml_tag(node_1, "administration")
        node_3 = self._set_xml_tag(node_2, "default-communities")
        node_4 = self._set_xml_tag(node_3, "default-community")
        self._set_xml_tag(node_4, "community-name")

        node_1 = self._set_xml_tag(xml_obj,
                                   "interface-configurations",
                                   "xmlns",
                                   "Cisco-IOS-XR-ifmgr-cfg",
                                   None)
        node_2 = self._set_xml_tag(node_1, "interface-configuration")
        self._set_xml_tag(node_2, "active", None, None, "act")
        self._set_xml_tag(node_2, "interface-name", None, None, "Loopback0")
        self._set_xml_tag(node_2, "interface-virtual")
        node_3 = self._set_xml_tag(node_2,
                                   "ipv4-network",
                                   "xmlns",
                                   "Cisco-IOS-XR-ipv4-io-cfg",
                                   None)
        node_4 = self._set_xml_tag(node_3, "addresses")
        node_5 = self._set_xml_tag(node_4, "primary")
        self._set_xml_tag(node_5, "address")
        self._set_xml_tag(node_5, "netmask")

        node_2 = self._set_xml_tag(node_1, "interface-configuration")
        self._set_xml_tag(node_2, "active", None, None, "act")
        self._set_xml_tag(
            node_2, "interface-name", None, None, "MgmtEth0/RP0/CPU0/0")
        node_3 = self._set_xml_tag(node_2,
                                   "ipv4-network",
                                   "xmlns",
                                   "Cisco-IOS-XR-ipv4-io-cfg",
                                   None)
        node_4 = self._set_xml_tag(node_3, "addresses")
        node_5 = self._set_xml_tag(node_4, "primary")
        self._set_xml_tag(node_5, "address")
        self._set_xml_tag(node_5, "netmask")


        node_1 = self._set_xml_tag(xml_obj,
                                   "ospf",
                                   "xmlns",
                                   "Cisco-IOS-XR-ipv4-ospf-cfg",
                                   None)
        node_2 = self._set_xml_tag(node_1, "processes")
        node_3 = self._set_xml_tag(node_2, "process")
        self._set_xml_tag(node_3, "process-name", None, None, "v4_MSF_OSPF")
        node_4 = self._set_xml_tag(node_3, "default-vrf")
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
        node_6 = self._set_xml_tag(node_5, "area-area-id")
        self._set_xml_tag(node_6, "area-id", None, None, "0")
        self._set_xml_tag(node_6, "running")
        node_7 = self._set_xml_tag(node_6, "name-scopes")
        node_8 = self._set_xml_tag(node_7, "name-scope")
        self._set_xml_tag(node_8, "interface-name", None, None, "Loopback0")
        self._set_xml_tag(node_8, "running")
        self._set_xml_tag(node_8, "cost", None, None, "10")
        self._set_xml_tag(node_8, "passive", None, None, "true")
        self._set_xml_tag(node_3, "start")

        node_1 = self._set_xml_tag(xml_obj,
                                   "mpls-ldp",
                                   "xmlns",
                                   "Cisco-IOS-XR-mpls-ldp-cfg",
                                   None)
        self._set_xml_tag(node_1, "enable")
        node_2 = self._set_xml_tag(node_1, "global")
        node_3 = self._set_xml_tag(node_2, "session")
        self._set_xml_tag(node_3, "hold-time", None, None, "180")
        node_2 = self._set_xml_tag(node_1, "default-vrf")
        node_3 = self._set_xml_tag(node_2, "global")
        self._set_xml_tag(node_3, "router-id")
        node_3 = self._set_xml_tag(node_2, "interfaces")

        node_1 = self._set_xml_tag(xml_obj,
                                   "mfwd",
                                   "xmlns",
                                   "Cisco-IOS-XR-ipv4-mfwd-cfg",
                                   None)
        node_2 = self._set_xml_tag(node_1, "default-context")
        node_3 = self._set_xml_tag(node_2, "ipv4")
        self._set_xml_tag(node_3, "multicast-forwarding")
        self._set_xml_tag(node_3, "interfaces")

        node_1 = self._set_xml_tag(xml_obj,
                                   "pim",
                                   "xmlns",
                                   "Cisco-IOS-XR-ipv4-pim-cfg",
                                   None)
        node_2 = self._set_xml_tag(node_1, "default-context")
        node_3 = self._set_xml_tag(node_2, "ipv4")
        node_4 = self._set_xml_tag(node_3, "sparse-mode-rp-addresses")
        node_5 = self._set_xml_tag(node_4, "sparse-mode-rp-address")
        self._set_xml_tag(node_5, "rp-address")
        node_4 = self._set_xml_tag(node_3, "interfaces")
        node_5 = self._set_xml_tag(node_4, "interface")
        self._set_xml_tag(node_5, "interface-name", None, None, "Loopback0")
        self._set_xml_tag(node_5, "enable")
        self._set_xml_tag(node_5, "interface-enable", None, None, "true")

        return True

    @decorater_log
    def _gen_leaf_fix_message(self, xml_obj, operation):
        node_1 = self._set_xml_tag(xml_obj,
                                   "host-names",
                                   "xmlns",
                                   "Cisco-IOS-XR-shellutil-cfg",
                                   None)
        self._set_xml_tag(node_1, "host-name")
        node_1 = self._set_xml_tag(xml_obj,
                                   "snmp",
                                   "xmlns",
                                   "Cisco-IOS-XR-snmp-agent-cfg",
                                   None)
        node_2 = self._set_xml_tag(node_1, "trap-hosts")
        node_3 = self._set_xml_tag(node_2, "trap-host")
        self._set_xml_tag(node_3, "ip-address")
        node_4 = self._set_xml_tag(node_3, "default-user-communities")
        node_5 = self._set_xml_tag(node_4, "default-user-community")
        self._set_xml_tag(node_5, "community-name")
        self._set_xml_tag(node_5, "version", None, None, "2c")
        self._set_xml_tag(node_5, "basic-trap-types", None, None, "0")
        self._set_xml_tag(node_5, "advanced-trap-types1", None, None, "0")
        self._set_xml_tag(node_5, "advanced-trap-types2", None, None, "0")

        node_2 = self._set_xml_tag(node_1, "administration")
        node_3 = self._set_xml_tag(node_2, "default-communities")
        node_4 = self._set_xml_tag(node_3, "default-community")
        self._set_xml_tag(node_4, "community-name")

        node_1 = self._set_xml_tag(xml_obj,
                                   "interface-configurations",
                                   "xmlns",
                                   "Cisco-IOS-XR-ifmgr-cfg",
                                   None)
        node_2 = self._set_xml_tag(node_1, "interface-configuration")
        self._set_xml_tag(node_2, "active", None, None, "act")
        self._set_xml_tag(node_2, "interface-name", None, None, "Loopback0")
        self._set_xml_tag(node_2, "interface-virtual")
        node_3 = self._set_xml_tag(node_2,
                                   "ipv4-network",
                                   "xmlns",
                                   "Cisco-IOS-XR-ipv4-io-cfg",
                                   None)
        node_4 = self._set_xml_tag(node_3, "addresses")
        node_5 = self._set_xml_tag(node_4, "primary")
        self._set_xml_tag(node_5, "address")
        self._set_xml_tag(node_5, "netmask")

        node_2 = self._set_xml_tag(node_1, "interface-configuration")
        self._set_xml_tag(node_2, "active", None, None, "act")
        self._set_xml_tag(
            node_2, "interface-name", None, None, "MgmtEth0/RP0/CPU0/0")
        node_3 = self._set_xml_tag(node_2,
                                   "ipv4-network",
                                   "xmlns",
                                   "Cisco-IOS-XR-ipv4-io-cfg",
                                   None)
        node_4 = self._set_xml_tag(node_3, "addresses")
        node_5 = self._set_xml_tag(node_4, "primary")
        self._set_xml_tag(node_5, "address")
        self._set_xml_tag(node_5, "netmask")


        node_1 = self._set_xml_tag(xml_obj,
                                   "routing-policy",
                                   "xmlns",
                                   "Cisco-IOS-XR-policy-repository-cfg",
                                   None)
        node_2 = self._set_xml_tag(node_1, "sets")
        node_3 = self._set_xml_tag(node_2, "community-sets")

        node_2 = self._set_xml_tag(node_1, "route-policies")

        node_3 = self._set_xml_tag(node_2, "route-policy")
        self._set_xml_tag(
            node_3, "route-policy-name", None, None, "VPN_export")
        self._set_xml_tag(
            node_3, "rpl-route-policy", None, None, self.__POLICY_3)
        node_3 = self._set_xml_tag(node_2, "route-policy")
        self._set_xml_tag(
            node_3, "route-policy-name", None, None, "VPN_import")
        self._set_xml_tag(
            node_3, "rpl-route-policy", None, None, self.__POLICY_4)
        node_3 = self._set_xml_tag(node_2, "route-policy")
        self._set_xml_tag(node_3,
                          "route-policy-name",
                          None,
                          None,
                          "eBGPv4_To_active-CE_export")
        self._set_xml_tag(
            node_3, "rpl-route-policy", None, None, self.__POLICY_6)
        node_3 = self._set_xml_tag(node_2, "route-policy")
        self._set_xml_tag(node_3,
                          "route-policy-name",
                          None,
                          None,
                          "eBGPv4_To_standby-CE_export")
        self._set_xml_tag(
            node_3, "rpl-route-policy", None, None, self.__POLICY_7)
        node_3 = self._set_xml_tag(node_2, "route-policy")
        self._set_xml_tag(node_3,
                          "route-policy-name",
                          None,
                          None,
                          "eBGPv4_To_CE_import")
        self._set_xml_tag(
            node_3, "rpl-route-policy", None, None, self.__POLICY_5)

        node_1 = self._set_xml_tag(xml_obj,
                                   "ospf",
                                   "xmlns",
                                   "Cisco-IOS-XR-ipv4-ospf-cfg",
                                   None)
        node_2 = self._set_xml_tag(node_1, "processes")
        node_3 = self._set_xml_tag(node_2, "process")
        self._set_xml_tag(node_3, "process-name", None, None, "v4_MSF_OSPF")
        node_4 = self._set_xml_tag(node_3, "default-vrf")
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
        node_6 = self._set_xml_tag(node_5, "area-area-id")
        self._set_xml_tag(node_6, "area-id", None, None, "0")
        self._set_xml_tag(node_6, "running")
        node_7 = self._set_xml_tag(node_6, "name-scopes")
        node_8 = self._set_xml_tag(node_7, "name-scope")
        self._set_xml_tag(node_8, "interface-name", None, None, "Loopback0")
        self._set_xml_tag(node_8, "running")
        self._set_xml_tag(node_8, "cost", None, None, "10")
        self._set_xml_tag(node_8, "passive", None, None, "true")

        self._set_xml_tag(node_3, "start")

        node_1 = self._set_xml_tag(xml_obj,
                                   "bgp",
                                   "xmlns",
                                   "Cisco-IOS-XR-ipv4-bgp-cfg",
                                   None)
        node_2 = self._set_xml_tag(node_1, "instance")
        self._set_xml_tag(node_2, "instance-name", None, None, "default")
        node_3 = self._set_xml_tag(node_2, "instance-as")
        self._set_xml_tag(node_3, "as", None, None, "0")
        node_4 = self._set_xml_tag(node_3, "four-byte-as")
        self._set_xml_tag(node_4, "as")
        self._set_xml_tag(node_4, "bgp-running")
        node_5 = self._set_xml_tag(node_4, "default-vrf")
        node_6 = self._set_xml_tag(node_5, "global")
        node_7 = self._set_xml_tag(node_6, "global-timers")
        self._set_xml_tag(node_7, "keepalive", None, None, "30")
        self._set_xml_tag(node_7, "hold-time", None, None, "90")
        self._set_xml_tag(node_6, "router-id")
        node_7 = self._set_xml_tag(node_6, "update-delay")
        self._set_xml_tag(node_7, "delay", None, None, "0")
        self._set_xml_tag(node_7, "always", None, None, "false")
        node_7 = self._set_xml_tag(node_6, "global-afs")
        node_8 = self._set_xml_tag(node_7, "global-af")
        self._set_xml_tag(node_8, "af-name", None, None, "vp-nv4-unicast")
        self._set_xml_tag(node_8, "enable")
        node_6 = self._set_xml_tag(node_5, "bgp-entity")
        node_7 = self._set_xml_tag(node_6, "neighbors")

        node_1 = self._set_xml_tag(xml_obj,
                                   "mpls-ldp",
                                   "xmlns",
                                   "Cisco-IOS-XR-mpls-ldp-cfg",
                                   None)
        self._set_xml_tag(node_1, "enable")
        node_2 = self._set_xml_tag(node_1, "global")
        node_3 = self._set_xml_tag(node_2, "session")
        self._set_xml_tag(node_3, "hold-time", None, None, "180")
        node_2 = self._set_xml_tag(node_1, "default-vrf")
        node_3 = self._set_xml_tag(node_2, "global")
        self._set_xml_tag(node_3, "router-id")
        node_3 = self._set_xml_tag(node_2, "interfaces")
        return True

    @decorater_log
    def _gen_l2_slice_fix_message(self, xml_obj, operation):
        self.common_util_log.logging(
            " ",
            self.log_level_error,
            self.Logmessage["Call_NG_Method"] %
            ("_gen_l2_slice_fix_message"),
            __name__)
        return False

    @decorater_log
    def _gen_l3_slice_fix_message(self, xml_obj, operation):
        if operation == "delete":
            self._gen_l3_slice_delete_fix_message(xml_obj)
        else:
            self._gen_l3_slice_merge_fix_message(xml_obj)
        return True

    @decorater_log
    def _gen_l3_slice_merge_fix_message(self, xml_obj):
        node_1 = self._set_xml_tag(xml_obj,
                                   "vrfs",
                                   "xmlns",
                                   "Cisco-IOS-XR-infra-rsi-cfg",
                                   None)
        node_2 = self._set_xml_tag(node_1, "vrf")
        self._set_xml_tag(node_2, "vrf-name")
        self._set_xml_tag(node_2, "create")
        node_3 = self._set_xml_tag(node_2, "afs")
        node_4 = self._set_xml_tag(node_3, "af")
        self._set_xml_tag(node_4, "af-name", None, None, "ipv4")
        self._set_xml_tag(node_4, "saf-name", None, None, "unicast")
        self._set_xml_tag(node_4, "topology-name", None, None, "default")
        self._set_xml_tag(node_4, "create")
        node_5 = self._set_xml_tag(node_4,
                                   "bgp",
                                   "xmlns",
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

        node_1 = self._set_xml_tag(xml_obj,
                                   "interface-configurations",
                                   "xmlns",
                                   "Cisco-IOS-XR-ifmgr-cfg",
                                   None)

        node_1 = self._set_xml_tag(xml_obj,
                                   "router-static",
                                   "xmlns",
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
                                   "ospf",
                                   "xmlns",
                                   "Cisco-IOS-XR-ipv4-ospf-cfg",
                                   None)
        node_2 = self._set_xml_tag(node_1, "processes")
        node_3 = self._set_xml_tag(node_2, "process")
        self._set_xml_tag(node_3, "process-name", None, None, "v4_VRF_OSPF")
        node_4 = self._set_xml_tag(node_3, "default-vrf")
        node_5 = self._set_xml_tag(node_4, "process-scope")
        node_6 = self._set_xml_tag(node_5, "dead-interval-minimal")
        self._set_xml_tag(node_6, "interval", None, None, "40")
        self._set_xml_tag(node_5, "hello-interval", None, None, "10")
        node_5 = self._set_xml_tag(node_4, "timers")
        node_6 = self._set_xml_tag(node_5, "spf-timer")
        self._set_xml_tag(node_6, "initial-delay", None, None, "200")
        self._set_xml_tag(node_6, "backoff-increment", None, None, "200")
        self._set_xml_tag(node_6, "max-delay", None, None, "2000")

        node_4 = self._set_xml_tag(node_3, "vrfs")
        node_5 = self._set_xml_tag(node_4, "vrf")
        self._set_xml_tag(node_5, "vrf-name")
        self._set_xml_tag(node_5, "vrf-start")
        self._set_xml_tag(node_5, "router-id")

        node_6 = self._set_xml_tag(node_5, "domain-id")
        node_7 = self._set_xml_tag(node_6, "primary-domain-id")
        self._set_xml_tag(node_7, "domain-id-type", None, None, "type0005")
        self._set_xml_tag(node_7, "domain-id-name", None, None, "FA3200000000")

        node_6 = self._set_xml_tag(node_5, "process-scope")
        node_7 = self._set_xml_tag(node_6, "distribute-list")
        self._set_xml_tag(node_7,
                          "route-policy-name",
                          None,
                          None,
                          "v4_OSPF_To_CE_import")

        tmp_node = self._set_xml_tag(node_5, "redistribution")
        node_6 = self._set_xml_tag(tmp_node, "redistributes")
        node_7 = self._set_xml_tag(node_6, "redistribute")
        self._set_xml_tag(node_7, "protocol-name", None, None, "connected")
        node_8 = self._set_xml_tag(
            node_7, "connected-or-static-or-dagr-or" +
            "-subscriber-or-mobile-or-rip")
        self._set_xml_tag(node_8, "classful", None, None, "false")
        self._set_xml_tag(node_8,
                          "route-policy-name",
                          None,
                          None,
                          "v4_Redist_To_OSPF_in_VRF")
        self._set_xml_tag(
            node_8, "bgp-preserve-default-info", None, None, "false")
        self._set_xml_tag(
            node_8, "ospf-redist-lsa-type", None, None, "external")

        node_7 = self._set_xml_tag(node_6, "redistribute")
        self._set_xml_tag(node_7, "protocol-name", None, None, "static")
        node_8 = self._set_xml_tag(
            node_7, "connected-or-static-or-dagr-or" +
            "-subscriber-or-mobile-or-rip")
        self._set_xml_tag(node_8, "classful", None, None, "false")
        self._set_xml_tag(node_8,
                          "route-policy-name",
                          None,
                          None,
                          "v4_Redist_To_OSPF_in_VRF")
        self._set_xml_tag(
            node_8, "bgp-preserve-default-info", None, None, "false")
        self._set_xml_tag(
            node_8, "ospf-redist-lsa-type", None, None, "external")
        node_7 = self._set_xml_tag(node_6, "redistribute")
        self._set_xml_tag(node_7, "protocol-name", None, None, "bgp")
        node_8 = self._set_xml_tag(node_7, "bgp")
        self._set_xml_tag(node_8, "instance-name", None, None, "bgp")
        self._set_xml_tag(node_8, "as-xx", None, None, "0")
        self._set_xml_tag(node_8, "as-yy")
        self._set_xml_tag(node_8, "classful", None, None, "false")
        self._set_xml_tag(node_8,
                          "route-policy-name",
                          None,
                          None,
                          "v4_Redist_To_OSPF_in_VRF")
        self._set_xml_tag(
            node_8, "bgp-preserve-default-info", None, None, "false")
        self._set_xml_tag(
            node_8, "ospf-redist-lsa-type", None, None, "external")

        node_6 = self._set_xml_tag(node_5, "area-addresses")
        node_7 = self._set_xml_tag(node_6, "area-area-id")
        self._set_xml_tag(node_7, "area-id", None, None, "0")
        self._set_xml_tag(node_7, "running")
        node_8 = self._set_xml_tag(node_7, "name-scopes")
        self._set_xml_tag(node_3, "start")

        node_1 = self._set_xml_tag(xml_obj,
                                   "bgp",
                                   "xmlns",
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
        node_7 = self._set_xml_tag(node_6, "vrf-global")
        self._set_xml_tag(node_7, "exists")
        node_8 = self._set_xml_tag(node_7, "route-distinguisher")
        self._set_xml_tag(node_8, "type", None, None, "as")
        self._set_xml_tag(node_8, "as-xx", None, None, "0")
        self._set_xml_tag(node_8, "as")
        self._set_xml_tag(node_8, "as-index")
        self._set_xml_tag(node_7, "router-id")
        node_8 = self._set_xml_tag(node_7, "vrf-global-afs")
        node_9 = self._set_xml_tag(node_8, "vrf-global-af")
        self._set_xml_tag(node_9, "af-name", None, None, "ipv4-unicast")
        self._set_xml_tag(node_9, "enable")
        node_10 = self._set_xml_tag(node_9, "label-mode")
        self._set_xml_tag(
            node_10, "label-allocation-mode", None, None, "per-vrf")
        node_10 = self._set_xml_tag(node_9, "connected-routes")
        self._set_xml_tag(node_10,
                          "route-policy-name",
                          None,
                          None,
                          "v4_Redist_To_BGP_in_VRF")
        node_10 = self._set_xml_tag(node_9, "static-routes")
        self._set_xml_tag(node_10,
                          "route-policy-name",
                          None,
                          None,
                          "v4_Redist_To_BGP_in_VRF")
        node_10 = self._set_xml_tag(node_9, "ospf-routes")
        node_11 = self._set_xml_tag(node_10, "ospf-route")
        self._set_xml_tag(node_11, "instance-name", None, None, "v4_VRF_OSPF")
        self._set_xml_tag(node_11,
                          "route-policy-name",
                          None,
                          None,
                          "v4_Redist_To_BGP_in_VRF")
        node_7 = self._set_xml_tag(node_6, "vrf-neighbors")

        node_1 = self._set_xml_tag(xml_obj,
                                   "vrrp",
                                   "xmlns",
                                   "Cisco-IOS-XR-ipv4-vrrp-cfg",
                                   None)
        node_2 = self._set_xml_tag(node_1, "interfaces")

        return True

    @decorater_log
    def _gen_l3_slice_delete_fix_message(self, xml_obj):
        node_1 = self._set_xml_tag(xml_obj,
                                   "vrfs",
                                   "xmlns",
                                   "Cisco-IOS-XR-infra-rsi-cfg",
                                   None)
        node_2 = self._set_xml_tag(
            node_1, "vrf", self._ATRI_OPE, self._DELETE, None)
        self._set_xml_tag(node_2, "vrf-name")

        node_1 = self._set_xml_tag(xml_obj,
                                   "interface-configurations",
                                   "xmlns",
                                   "Cisco-IOS-XR-ifmgr-cfg",
                                   None)

        node_1 = self._set_xml_tag(xml_obj,
                                   "router-static",
                                   "xmlns",
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
                                   "ospf",
                                   "xmlns",
                                   "Cisco-IOS-XR-ipv4-ospf-cfg",
                                   None)
        node_2 = self._set_xml_tag(node_1, "processes")
        node_3 = self._set_xml_tag(node_2, "process")
        self._set_xml_tag(node_3, "process-name", None, None, "v4_VRF_OSPF")
        node_4 = self._set_xml_tag(node_3, "vrfs")
        node_5 = self._set_xml_tag(node_4, "vrf")
        self._set_xml_tag(node_5, "vrf-name")
        self._set_xml_tag(node_5, "vrf-start")
        node_6 = self._set_xml_tag(node_5, "area-addresses")
        node_7 = self._set_xml_tag(node_6, "area-area-id")
        self._set_xml_tag(node_7, "area-id", None, None, "0")
        self._set_xml_tag(node_7, "running")
        self._set_xml_tag(node_7, "name-scopes")
        self._set_xml_tag(node_3, "start")

        node_1 = self._set_xml_tag(xml_obj,
                                   "bgp",
                                   "xmlns",
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
                                   "Cisco-IOS-XR-ipv4-vrrp-cfg",
                                   None)
        node_2 = self._set_xml_tag(node_1, "interfaces")
        return True

    @decorater_log
    def _gen_ce_lag_fix_message(self, xml_obj, operation):

        return True

    @decorater_log
    def _gen_internal_fix_lag_message(self, xml_obj, operation):

        self._set_xml_tag(xml_obj,
                          "interface-configurations",
                          "xmlns",
                          "Cisco-IOS-XR-ifmgr-cfg",
                          None)

        node_1 = self._set_xml_tag(xml_obj,
                                   "ospf",
                                   "xmlns",
                                   "Cisco-IOS-XR-ipv4-ospf-cfg",
                                   None)
        node_2 = self._set_xml_tag(node_1, "processes")
        node_3 = self._set_xml_tag(node_2, "process")
        self._set_xml_tag(node_3, "process-name", None, None, "v4_MSF_OSPF")
        node_4 = self._set_xml_tag(node_3, "default-vrf")
        node_5 = self._set_xml_tag(node_4, "area-addresses")
        node_6 = self._set_xml_tag(node_5, "area-area-id")
        self._set_xml_tag(node_6, "area-id", None, None, "0")
        self._set_xml_tag(node_6, "running")
        self._set_xml_tag(node_6, "name-scopes")

        node_1 = self._set_xml_tag(xml_obj,
                                   "mpls-ldp",
                                   "xmlns",
                                   "Cisco-IOS-XR-mpls-ldp-cfg",
                                   None)
        self._set_xml_tag(node_1, "enable")
        node_2 = self._set_xml_tag(node_1, "default-vrf")
        self._set_xml_tag(node_2, "interfaces")


        node_1 = self._set_xml_tag(xml_obj,
                                   "mfwd",
                                   "xmlns",
                                   "Cisco-IOS-XR-ipv4-mfwd-cfg",
                                   None)
        node_2 = self._set_xml_tag(node_1, "default-context")
        node_3 = self._set_xml_tag(node_2, "ipv4")
        self._set_xml_tag(node_3, "multicast-forwarding")
        self._set_xml_tag(node_3, "interfaces")

        node_1 = self._set_xml_tag(xml_obj,
                                   "pim",
                                   "xmlns",
                                   "Cisco-IOS-XR-ipv4-pim-cfg",
                                   None)
        node_2 = self._set_xml_tag(node_1, "default-context")
        node_3 = self._set_xml_tag(node_2, "ipv4")
        node_4 = self._set_xml_tag(node_3, "sparse-mode-rp-addresses")
        node_5 = self._set_xml_tag(node_4, "sparse-mode-rp-address")
        self._set_xml_tag(node_5, "rp-address")
        node_4 = self._set_xml_tag(node_3, "interfaces")

        return True

    @decorater_log
    def _gen_spine_variable_message(self,
                                    xml_obj,
                                    device_info,
                                    ec_message,
                                    operation):
        is_variable_value = True
        dev_reg_info = {}
        dev_reg_info["SP-SPINE-NAME"] = ec_message["device"].get("name")
        dev_reg_info["SP-SNMP-SERVER"] = \
            ec_message["device"]["snmp"].get("server-address")
        dev_reg_info["SP-SNMP-COMMUNITY"] = \
            ec_message["device"]["snmp"].get("community")
        dev_reg_info["SP-LB-IF-ADDR"] = \
            ec_message["device"]["loopback-interface"].get("address")
        dev_reg_info["SP-LB-IF-PREFIX"] = \
            self._conversion_cidr2mask(
                ec_message["device"]["loopback-interface"].get("prefix"))
        dev_reg_info["SP-MNG-IF-ADDR"] = \
            ec_message["device"]["management-interface"].get("address")
        dev_reg_info["SP-MNG-IF-PREFIX"] = \
            self._conversion_cidr2mask(
                ec_message["device"]["management-interface"].get("prefix"))
        dev_reg_info["SP-RP-OTHER-ADDR"] = (
            ec_message["device"]["l2-vpn"]["pim"].get("other-rp-address"))
        for chk_item in dev_reg_info.values():
            if chk_item is None:
                is_variable_value = False
                break

        lag_ifs = []
        lag_mem_ifs = []

        if (ec_message["device"].get("internal-lag") is not None and
                len(ec_message["device"]["internal-lag"]) > 0):
            for lag in ec_message["device"].get("internal-lag"):
                if lag.get("name") is None \
                        or lag.get("address") is None \
                        or self._conversion_cidr2mask(lag.get("prefix")) is None \
                        or lag.get("minimum-links") is None:
                    is_variable_value = False
                    break
                tmp = \
                    {"SP-INTERNAL-LAG-IF-NAME": lag["name"],
                     "SP-INTERNAL-LAG-IF-ADDR": lag["address"],
                     "SP-INTERNAL-LAG-IF-PREFIX":
                         self._conversion_cidr2mask(
                             lag["prefix"]),
                     "SP-INTERNAL-LAG-LINKS": lag["minimum-links"]}
                lag_ifs.append(tmp)

                if not lag.get("internal-interface") \
                        or len(lag["internal-interface"]) == 0:
                    is_variable_value = False
                    break

                for lag_mem in lag["internal-interface"]:
                    if lag_mem.get("name") is None:
                        is_variable_value = False
                        break
                    tmp2 = \
                        {"SP-INTERNAL-IF-NAME": lag_mem["name"],
                         "SP-INTERNAL-LAG-IF-NAME":
                         lag["name"].lstrip("Bundle-Ether")}
                    if tmp2 not in lag_mem_ifs:
                        lag_mem_ifs.append(tmp2)

        if is_variable_value is False:
            return False

        self._set_xml_tag_variable(xml_obj,
                                   "host-name",
                                   dev_reg_info["SP-SPINE-NAME"],
                                   "host-names")

        self._set_xml_tag_variable(xml_obj,
                                   "ip-address",
                                   dev_reg_info["SP-SNMP-SERVER"],
                                   "snmp",
                                   "trap-hosts",
                                   "trap-host")

        self._set_xml_tag_variable(xml_obj,
                                   "community-name",
                                   dev_reg_info["SP-SNMP-COMMUNITY"],
                                   "snmp",
                                   "trap-hosts",
                                   "trap-host",
                                   "default-user-communities",
                                   "default-user-community")

        self._set_xml_tag_variable(xml_obj,
                                   "community-name",
                                   dev_reg_info["SP-SNMP-COMMUNITY"],
                                   "snmp",
                                   "administration",
                                   "default-communities",
                                   "default-community")

        if_node = self._find_xml_node(xml_obj, "interface-configurations")
        if_nodes = if_node.findall("interface-configuration")
        for tmp_if in if_nodes:
            tmp_tag = tmp_if.find("interface-name")
            if tmp_tag.text == "Loopback0":
                node = self._find_xml_node(
                    tmp_if, "ipv4-network", "addresses", "primary")
                self._set_xml_tag_variable(node,
                                           "address",
                                           dev_reg_info["SP-LB-IF-ADDR"])
                self._set_xml_tag_variable(node,
                                           "netmask",
                                           dev_reg_info["SP-LB-IF-PREFIX"])
            elif tmp_tag.text == "MgmtEth0/RP0/CPU0/0":
                node = self._find_xml_node(
                    tmp_if, "ipv4-network", "addresses", "primary")
                self._set_xml_tag_variable(node,
                                           "address",
                                           dev_reg_info["SP-MNG-IF-ADDR"])
                self._set_xml_tag_variable(node,
                                           "netmask",
                                           dev_reg_info["SP-MNG-IF-PREFIX"])

        for lag_if in lag_ifs:
            node_2 = self._set_xml_tag(if_node, "interface-configuration")
            self._set_xml_tag(node_2, "active", None, None, "act")
            self._set_xml_tag(node_2,
                              "interface-name",
                              None,
                              None,
                              lag_if["SP-INTERNAL-LAG-IF-NAME"])
            self._set_xml_tag(node_2, "interface-virtual")
            node_3 = self._set_xml_tag(node_2, "mtus")
            node_4 = self._set_xml_tag(node_3, "mtu")
            self._set_xml_tag(node_4, "owner", None, None, "etherbundle")
            self._set_xml_tag(node_4, "mtu", None, None, "4110")
            node_3 = self._set_xml_tag(node_2,
                                       "qos",
                                       "xmlns",
                                       "Cisco-IOS-XR-qos-ma-cfg",
                                       None)
            node_4 = self._set_xml_tag(node_3, "input")
            node_5 = self._set_xml_tag(node_4, "service-policy")
            self._set_xml_tag(node_5,
                              "service-policy-name",
                              None,
                              None,
                              "in_msf_policy")
            node_4 = self._set_xml_tag(node_3, "output")
            node_5 = self._set_xml_tag(node_4, "service-policy")
            self._set_xml_tag(node_5,
                              "service-policy-name",
                              None,
                              None,
                              "out_msf_policy")
            node_3 = self._set_xml_tag(node_2,
                                       "ipv4-network",
                                       "xmlns",
                                       "Cisco-IOS-XR-ipv4-io-cfg",
                                       None)
            node_4 = self._set_xml_tag(node_3, "addresses")
            node_5 = self._set_xml_tag(node_4, "primary")
            self._set_xml_tag(node_5,
                              "address",
                              None,
                              None,
                              lag_if["SP-INTERNAL-LAG-IF-ADDR"])
            self._set_xml_tag(node_5,
                              "netmask",
                              None,
                              None,
                              lag_if["SP-INTERNAL-LAG-IF-PREFIX"])
            node_3 = self._set_xml_tag(node_2,
                                       "bundle",
                                       "xmlns",
                                       "Cisco-IOS-XR-bundlemgr-cfg",
                                       None)
            node_4 = self._set_xml_tag(node_3, "minimum-active")
            self._set_xml_tag(node_4,
                              "links",
                              None,
                              None,
                              lag_if["SP-INTERNAL-LAG-LINKS"])

        for lag_mem_if in lag_mem_ifs:
            node_2 = self._set_xml_tag(if_node, "interface-configuration")
            self._set_xml_tag(node_2, "active", None, None, "act")
            self._set_xml_tag(node_2,
                              "interface-name",
                              None,
                              None,
                              lag_mem_if["SP-INTERNAL-IF-NAME"])
            node_3 = self._set_xml_tag(node_2,
                                       "bundle-member",
                                       "xmlns",
                                       "Cisco-IOS-XR-bundlemgr-cfg",
                                       None)
            node_4 = self._set_xml_tag(node_3, "id")
            self._set_xml_tag(node_4,
                              "bundle-id",
                              None,
                              None,
                              lag_mem_if["SP-INTERNAL-LAG-IF-NAME"])
            self._set_xml_tag(node_4, "port-activity", None, None, "active")
            node_3 = self._set_xml_tag(node_2,
                                       "lacp",
                                       "xmlns",
                                       "Cisco-IOS-XR-bundlemgr-cfg",
                                       None)
            self._set_xml_tag(node_3, "period-short", None, None, "true")
            self._set_xml_tag(node_2,
                              "shutdown",
                              self._ATRI_OPE,
                              self._DELETE,
                              None)

        self._set_xml_tag_variable(xml_obj,
                                   "router-id",
                                   dev_reg_info["SP-LB-IF-ADDR"],
                                   "ospf",
                                   "processes",
                                   "process",
                                   "default-vrf")

        node_7 = self._find_xml_node(xml_obj,
                                     "ospf",
                                     "processes",
                                     "process",
                                     "default-vrf",
                                     "area-addresses",
                                     "area-area-id",
                                     "name-scopes")
        for lag_if in lag_ifs:
            node_8 = self._set_xml_tag(node_7, "name-scope")
            self._set_xml_tag(node_8,
                              "interface-name",
                              None,
                              None,
                              lag_if["SP-INTERNAL-LAG-IF-NAME"])
            self._set_xml_tag(node_8, "running")
            self._set_xml_tag(node_8, "cost", None, None, "100")
            self._set_xml_tag(node_8, "priority", None, None, "20")

        self._set_xml_tag_variable(xml_obj,
                                   "router-id",
                                   dev_reg_info["SP-LB-IF-ADDR"],
                                   "mpls-ldp",
                                   "default-vrf",
                                   "global")

        node_3 = self._find_xml_node(xml_obj,
                                     "mpls-ldp",
                                     "default-vrf",
                                     "interfaces")
        if len(lag_ifs) == 0:
            node_2 = self._find_xml_node(xml_obj,
                                         "mpls-ldp",
                                         "default-vrf")
            node_2.remove(node_3)
        else:
            for lag_if in lag_ifs:
                node_4 = self._set_xml_tag(node_3, "interface")
                self._set_xml_tag(node_4,
                                  "interface-name",
                                  None,
                                  None,
                                  lag_if["SP-INTERNAL-LAG-IF-NAME"])
                self._set_xml_tag(node_4, "enable")
                node_5 = self._set_xml_tag(node_4, "global")
                node_6 = self._set_xml_tag(node_5, "discovery")
                node_7 = self._set_xml_tag(node_6, "link-hello")
                self._set_xml_tag(node_7, "hold-time", None, None, "15")
                self._set_xml_tag(node_7, "interval", None, None, "5")

        node_1 = self._find_xml_node(xml_obj,
                                     "mfwd",
                                     "default-context",
                                     "ipv4",
                                     "interfaces")
        for lag_if in lag_ifs:
            node_2 = self._set_xml_tag(node_1, "interface")
            self._set_xml_tag(node_2,
                              "interface-name",
                              None,
                              None,
                              lag_if["SP-INTERNAL-LAG-IF-NAME"])
            self._set_xml_tag(node_2,
                              "enable-on-interface",
                              None,
                              None,
                              "true")

        self._set_xml_tag_variable(xml_obj,
                                   "rp-address",
                                   dev_reg_info["SP-RP-OTHER-ADDR"],
                                   "pim",
                                   "default-context",
                                   "ipv4",
                                   "sparse-mode-rp-addresses",
                                   "sparse-mode-rp-address")
        node_1 = self._find_xml_node(xml_obj,
                                     "pim",
                                     "default-context",
                                     "ipv4",
                                     "interfaces")
        for lag_if in lag_ifs:
            node_2 = self._set_xml_tag(node_1, "interface")
            self._set_xml_tag(node_2,
                              "interface-name",
                              None,
                              None,
                              lag_if["SP-INTERNAL-LAG-IF-NAME"])
            self._set_xml_tag(node_2, "enable")
            self._set_xml_tag(node_2,
                              "interface-enable",
                              None,
                              None,
                              "true")
        return True

    @decorater_log
    def _gen_leaf_variable_message(self,
                                   xml_obj,
                                   device_info,
                                   ec_message,
                                   operation):
        is_variable_value = True
        dev_reg_info = {}
        dev_reg_info["LF-SPINE-NAME"] = ec_message["device"].get("name")
        dev_reg_info["LF-SNMP-SERVER"] = \
            ec_message["device"]["snmp"].get("server-address")
        dev_reg_info["LF-SNMP-COMMUNITY"] = \
            ec_message["device"]["snmp"].get("community")
        dev_reg_info["LF-LB-IF-ADDR"] = \
            ec_message["device"]["loopback-interface"].get("address")
        dev_reg_info["LF-LB-IF-PREFIX"] = \
            self._conversion_cidr2mask(
                ec_message["device"]["loopback-interface"].get("prefix"))
        dev_reg_info["LF-MNG-IF-ADDR"] = \
            ec_message["device"]["management-interface"].get("address")
        dev_reg_info["LF-MNG-IF-PREFIX"] = \
            self._conversion_cidr2mask(
                ec_message["device"]["management-interface"].get("prefix"))
        dev_reg_info["LF-AS-NUMBER"] = \
            ec_message["device"]["l3-vpn"]["as"].get("as-number")

        for chk_item in dev_reg_info.values():
            if chk_item is None:
                is_variable_value = False
                break

        l3v_lbb_infos = []
        l3v = ec_message["device"]["l3-vpn"]["bgp"]

        for nbrs in l3v["neighbor"]:
            if nbrs["address"] is None \
                    or l3v.get("community") is None \
                    or l3v.get("community-wildcard") is None:
                is_variable_value = False
            else:
                tmp = \
                    {"LF-RR-ADDR": nbrs["address"],
                     "LF-BGP-COMMUNITY": l3v["community"],
                     "LF-BGP-COM-WILD": l3v["community-wildcard"]}
                l3v_lbb_infos.append(tmp)

        lag_ifs = []
        lag_mem_ifs = []

        if (ec_message["device"].get("internal-lag") is not None and
                len(ec_message["device"]["internal-lag"]) > 0):
            for lag in ec_message["device"].get("internal-lag"):
                if lag.get("name") is None \
                        or lag.get("address") is None \
                        or self._conversion_cidr2mask(lag.get("prefix")) is None \
                        or lag.get("minimum-links") is None:
                    is_variable_value = False
                    break
                tmp = \
                    {"LF-INTERNAL-LAG-IF-NAME": lag["name"],
                     "LF-INTERNAL-LAG-IF-ADDR": lag["address"],
                     "LF-INTERNAL-LAG-IF-PREFIX":
                         self._conversion_cidr2mask(
                             lag["prefix"]),
                     "LF-INTERNAL-LAG-LINKS": lag["minimum-links"]}
                lag_ifs.append(tmp)

                if not lag.get("internal-interface") \
                        or len(lag["internal-interface"]) == 0:
                    is_variable_value = False

                for lag_mem in lag["internal-interface"]:
                    if lag_mem["name"] is None:
                        is_variable_value = False
                        break
                    tmp2 = \
                        {"LF-INTERNAL-IF-NAME": lag_mem["name"],
                         "LF-INTERNAL-LAG-IF-NAME":
                         lag["name"].lstrip("Bundle-Ether")}
                    if tmp2 not in lag_mem_ifs:
                        lag_mem_ifs.append(tmp2)

        if is_variable_value is False:
            return False

        self._set_xml_tag_variable(xml_obj,
                                   "host-name",
                                   dev_reg_info["LF-SPINE-NAME"],
                                   "host-names")

        self._set_xml_tag_variable(xml_obj,
                                   "ip-address",
                                   dev_reg_info["LF-SNMP-SERVER"],
                                   "snmp",
                                   "trap-hosts",
                                   "trap-host")

        self._set_xml_tag_variable(xml_obj,
                                   "community-name",
                                   dev_reg_info["LF-SNMP-COMMUNITY"],
                                   "snmp",
                                   "trap-hosts",
                                   "trap-host",
                                   "default-user-communities",
                                   "default-user-community")

        self._set_xml_tag_variable(xml_obj,
                                   "community-name",
                                   dev_reg_info["LF-SNMP-COMMUNITY"],
                                   "snmp",
                                   "administration",
                                   "default-communities",
                                   "default-community")

        if_node = self._find_xml_node(xml_obj, "interface-configurations")
        if_nodes = if_node.findall("interface-configuration")
        for tmp_if in if_nodes:
            tmp_tag = tmp_if.find("interface-name")
            if tmp_tag.text == "Loopback0":
                node = self._find_xml_node(
                    tmp_if, "ipv4-network", "addresses", "primary")
                self._set_xml_tag_variable(node,
                                           "address",
                                           dev_reg_info["LF-LB-IF-ADDR"])
                self._set_xml_tag_variable(node,
                                           "netmask",
                                           dev_reg_info["LF-LB-IF-PREFIX"])
            elif tmp_tag.text == "MgmtEth0/RP0/CPU0/0":
                node = self._find_xml_node(
                    tmp_if, "ipv4-network", "addresses", "primary")
                self._set_xml_tag_variable(node,
                                           "address",
                                           dev_reg_info["LF-MNG-IF-ADDR"])
                self._set_xml_tag_variable(node,
                                           "netmask",
                                           dev_reg_info["LF-MNG-IF-PREFIX"])

        for lag_if in lag_ifs:
            node_2 = self._set_xml_tag(if_node, "interface-configuration")
            self._set_xml_tag(node_2, "active", None, None, "act")
            self._set_xml_tag(node_2,
                              "interface-name",
                              None,
                              None,
                              lag_if["LF-INTERNAL-LAG-IF-NAME"])
            self._set_xml_tag(node_2, "interface-virtual")
            node_3 = self._set_xml_tag(node_2, "mtus")
            node_4 = self._set_xml_tag(node_3, "mtu")
            self._set_xml_tag(node_4, "owner", None, None, "etherbundle")
            self._set_xml_tag(node_4, "mtu", None, None, "4110")
            node_3 = self._set_xml_tag(node_2,
                                       "qos",
                                       "xmlns",
                                       "Cisco-IOS-XR-qos-ma-cfg",
                                       None)
            node_4 = self._set_xml_tag(node_3, "input")
            node_5 = self._set_xml_tag(node_4, "service-policy")
            self._set_xml_tag(node_5,
                              "service-policy-name",
                              None,
                              None,
                              "in_msf_policy")
            node_4 = self._set_xml_tag(node_3, "output")
            node_5 = self._set_xml_tag(node_4, "service-policy")
            self._set_xml_tag(node_5,
                              "service-policy-name",
                              None,
                              None,
                              "out_msf_policy")
            node_3 = self._set_xml_tag(node_2,
                                       "ipv4-network",
                                       "xmlns",
                                       "Cisco-IOS-XR-ipv4-io-cfg",
                                       None)
            node_4 = self._set_xml_tag(node_3, "addresses")
            node_5 = self._set_xml_tag(node_4, "primary")
            self._set_xml_tag(node_5,
                              "address",
                              None,
                              None,
                              lag_if["LF-INTERNAL-LAG-IF-ADDR"])
            self._set_xml_tag(node_5,
                              "netmask",
                              None,
                              None,
                              lag_if["LF-INTERNAL-LAG-IF-PREFIX"])
            node_3 = self._set_xml_tag(node_2,
                                       "bundle",
                                       "xmlns",
                                       "Cisco-IOS-XR-bundlemgr-cfg",
                                       None)
            node_4 = self._set_xml_tag(node_3, "minimum-active")
            self._set_xml_tag(node_4,
                              "links",
                              None,
                              None,
                              lag_if["LF-INTERNAL-LAG-LINKS"])

        for lag_mem_if in lag_mem_ifs:
            node_2 = self._set_xml_tag(if_node, "interface-configuration")
            self._set_xml_tag(node_2, "active", None, None, "act")
            self._set_xml_tag(node_2,
                              "interface-name",
                              None,
                              None,
                              lag_mem_if["LF-INTERNAL-IF-NAME"])
            node_3 = self._set_xml_tag(node_2,
                                       "bundle-member",
                                       "xmlns",
                                       "Cisco-IOS-XR-bundlemgr-cfg",
                                       None)
            node_4 = self._set_xml_tag(node_3, "id")
            self._set_xml_tag(node_4,
                              "bundle-id",
                              None,
                              None,
                              lag_mem_if["LF-INTERNAL-LAG-IF-NAME"])
            self._set_xml_tag(node_4, "port-activity", None, None, "active")
            node_3 = self._set_xml_tag(node_2,
                                       "lacp",
                                       "xmlns",
                                       "Cisco-IOS-XR-bundlemgr-cfg",
                                       None)
            self._set_xml_tag(node_3, "period-short", None, None, "true")
            self._set_xml_tag(node_2,
                              "shutdown",
                              self._ATRI_OPE,
                              self._DELETE,
                              None)

        node_3 = self._find_xml_node(xml_obj,
                                     "routing-policy",
                                     "sets",
                                     "community-sets")
        node_4 = self._set_xml_tag(node_3, "community-set")
        self._set_xml_tag(
            node_4, "set-name", None, None, "MSF_community")
        self._set_xml_tag(node_4,
                          "rpl-community-set",
                          None,
                          None,
                          self.__policy_1(l3v_lbb_infos[0]["LF-BGP-COM-WILD"]))
        node_4 = self._set_xml_tag(node_3, "community-set")
        self._set_xml_tag(
            node_4, "set-name", None, None, "MSF_belonging_side")
        self._set_xml_tag(node_4,
                          "rpl-community-set",
                          None,
                          None,
                          self.__policy_2(
                              l3v_lbb_infos[0]["LF-BGP-COMMUNITY"]))

        self._set_xml_tag_variable(xml_obj,
                                   "router-id",
                                   dev_reg_info["LF-LB-IF-ADDR"],
                                   "ospf",
                                   "processes",
                                   "process",
                                   "default-vrf")

        node_7 = self._find_xml_node(xml_obj,
                                     "ospf",
                                     "processes",
                                     "process",
                                     "default-vrf",
                                     "area-addresses",
                                     "area-area-id",
                                     "name-scopes")
        for lag_if in lag_ifs:
            node_8 = self._set_xml_tag(node_7, "name-scope")
            self._set_xml_tag(node_8,
                              "interface-name",
                              None,
                              None,
                              lag_if["LF-INTERNAL-LAG-IF-NAME"])
            self._set_xml_tag(node_8, "running")
            self._set_xml_tag(node_8, "cost", None, None, "100")
            self._set_xml_tag(node_8, "priority", None, None, "10")

        self._set_xml_tag_variable(xml_obj,
                                   "as",
                                   str(dev_reg_info["LF-AS-NUMBER"]),
                                   "bgp",
                                   "instance",
                                   "instance-as",
                                   "four-byte-as")

        self._set_xml_tag_variable(xml_obj,
                                   "router-id",
                                   dev_reg_info["LF-LB-IF-ADDR"],
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
            node_8 = self._set_xml_tag(node_7, "neighbor")
            self._set_xml_tag(node_8,
                              "neighbor-address",
                              None,
                              None,
                              l3v_lbb["LF-RR-ADDR"])
            node_9 = self._set_xml_tag(node_8, "remote-as")
            self._set_xml_tag(node_9, "as-xx", None, None, "0")
            self._set_xml_tag(node_9,
                              "as-yy",
                              None,
                              None,
                              str(dev_reg_info["LF-AS-NUMBER"]))
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

        self._set_xml_tag_variable(xml_obj,
                                   "router-id",
                                   dev_reg_info["LF-LB-IF-ADDR"],
                                   "mpls-ldp",
                                   "default-vrf",
                                   "global")

        node_3 = self._find_xml_node(xml_obj,
                                     "mpls-ldp",
                                     "default-vrf",
                                     "interfaces")
        if len(lag_ifs) == 0:
            node_2 = self._find_xml_node(xml_obj,
                                         "mpls-ldp",
                                         "default-vrf")
            node_2.remove(node_3)
        else:
            for lag_if in lag_ifs:
                node_4 = self._set_xml_tag(node_3, "interface")
                self._set_xml_tag(node_4,
                                  "interface-name",
                                  None,
                                  None,
                                  lag_if["LF-INTERNAL-LAG-IF-NAME"])
                self._set_xml_tag(node_4, "enable")
                node_5 = self._set_xml_tag(node_4, "global")
                node_6 = self._set_xml_tag(node_5, "discovery")
                node_7 = self._set_xml_tag(node_6, "link-hello")
                self._set_xml_tag(node_7, "hold-time", None, None, "15")
                self._set_xml_tag(node_7, "interval", None, None, "5")
        return True

    @decorater_log
    def _gen_l2_slice_variable_message(self,
                                       xml_obj,
                                       device_info,
                                       ec_message,
                                       operation):
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
        return_val = False
        if operation == "delete":
            return_val = self._gen_del_l3_slice_variable_message(
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
        is_ospf = False
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
                    or cp["vlan-id"] is None:
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
                    if track["name"] is None:
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
                for route in cp["static"]["route"]:
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
            if "ospf" in cp:
                if cp["ospf"].get("metric") is None:
                    is_variable_value = False
                    break
                is_ospf = True
                tmp["L3-OSPF-CP-METRIC"] = cp["ospf"]["metric"]
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
                                           "Cisco-IOS-XR-qos-ma-cfg",
                                           None)
                node_4 = self._set_xml_tag(node_3, "input")
                node_5 = self._set_xml_tag(node_4, "service-policy")
                self._set_xml_tag(
                    node_5, "service-policy-name", None, None, "in_ce_policy")
                node_4 = self._set_xml_tag(node_3, "output")
                node_5 = self._set_xml_tag(node_4, "service-policy")
                self._set_xml_tag(
                    node_5, "service-policy-name", None, None, "out_ce_policy")
                node_3 = self._set_xml_tag(node_2,
                                           "vrf",
                                           "xmlns",
                                           "Cisco-IOS-XR-infra-rsi-cfg",
                                           vrf_dtl_info["L3-VRF-NAME"])
                node_3 = self._set_xml_tag(node_2,
                                           "ipv4-network",
                                           "xmlns",
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
                                           "ipv4-packet-filter",
                                           "xmlns",
                                           "Cisco-IOS-XR-ip-pfilter-cfg",
                                           None)
                node_4 = self._set_xml_tag(node_3, "inbound")
                self._set_xml_tag(
                    node_4, "acl-name-array", None, None, "ipv4_filter_input")
                self._set_xml_tag(
                    node_4, "is-common-array", None, None, "false")
            elif "Bundle-Ether" not in cp["L3-CE-IF-NAME"] \
                    and cp["L3-CE-IF-VLAN"] == "0":
                node_2 = self._set_xml_tag(node_1, "interface-configuration")
                self._set_xml_tag(node_2, "active", None, None, "act")
                self._set_xml_tag(
                    node_2, "interface-name", None, None, cp["L3-CE-IF-NAME"])
                if cp["L3-CE-IF-MTU"] is not None:
                    node_3 = self._set_xml_tag(node_2, "mtus")
                    node_4 = self._set_xml_tag(node_3, "mtu")
                    for ownernameKey in CiscoDriver.__cisco_proper_config.keys():
                        if ownernameKey in cp["L3-CE-IF-NAME"]:
                            self._set_xml_tag(
                                node_4, "owner", None, None, CiscoDriver.__cisco_proper_config.get(ownernameKey))
                    self._set_xml_tag(node_4,
                                      "mtu",
                                      None,
                                      None,
                                      int(cp["L3-CE-IF-MTU"]) + 14)
                node_3 = self._set_xml_tag(node_2,
                                           "qos",
                                           "xmlns",
                                           "Cisco-IOS-XR-qos-ma-cfg",
                                           None)
                node_4 = self._set_xml_tag(node_3, "input")
                node_5 = self._set_xml_tag(node_4, "service-policy")
                self._set_xml_tag(
                    node_5, "service-policy-name", None, None, "in_ce_policy")
                node_4 = self._set_xml_tag(node_3, "output")
                node_5 = self._set_xml_tag(node_4, "service-policy")
                self._set_xml_tag(
                    node_5, "service-policy-name", None, None, "out_ce_policy")
                node_3 = self._set_xml_tag(node_2,
                                           "vrf",
                                           "xmlns",
                                           "Cisco-IOS-XR-infra-rsi-cfg",
                                           vrf_dtl_info["L3-VRF-NAME"])
                node_3 = self._set_xml_tag(node_2,
                                           "ipv4-network",
                                           "xmlns",
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
                                           "ipv4-packet-filter",
                                           "xmlns",
                                           "Cisco-IOS-XR-ip-pfilter-cfg",
                                           None)
                node_4 = self._set_xml_tag(node_3, "inbound")
                self._set_xml_tag(
                    node_4, "acl-name-array", None, None, "ipv4_filter_input")
                self._set_xml_tag(
                    node_4, "is-common-array", None, None, "false")
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
                        for ownernameKey in CiscoDriver.__cisco_proper_config.keys():
                            if ownernameKey in cp["L3-CE-IF-NAME"]:
                                self._set_xml_tag(
                                    node_4, "owner", None, None, CiscoDriver.__cisco_proper_config.get(ownernameKey))
                    self._set_xml_tag(node_4,
                                      "mtu",
                                      None,
                                      None,
                                      "4114")
                node_3 = self._set_xml_tag(node_2,
                                           "qos",
                                           "xmlns",
                                           "Cisco-IOS-XR-qos-ma-cfg",
                                           None)
                node_4 = self._set_xml_tag(node_3, "input")
                node_5 = self._set_xml_tag(node_4, "service-policy")
                self._set_xml_tag(
                    node_5, "service-policy-name", None, None, "in_ce_policy")
                node_4 = self._set_xml_tag(node_3, "output")
                node_5 = self._set_xml_tag(node_4, "service-policy")
                self._set_xml_tag(
                    node_5, "service-policy-name", None, None, "out_ce_policy")
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
                                           "Cisco-IOS-XR-infra-rsi-cfg",
                                           vrf_dtl_info["L3-VRF-NAME"])
                node_3 = self._set_xml_tag(node_2,
                                           "ipv4-network",
                                           "xmlns",
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
                                           "Cisco-IOS-XR-l2-eth-infra-cfg",
                                           None)
                node_4 = self._set_xml_tag(node_3, "vlan-identifier")
                self._set_xml_tag(
                    node_4, "vlan-type", None, None, "vlan-type-dot1q")
                self._set_xml_tag(
                    node_4, "first-tag", None, None, cp["L3-CE-IF-VLAN"])

                node_3 = self._set_xml_tag(node_2,
                                           "ipv4-packet-filter",
                                           "xmlns",
                                           "Cisco-IOS-XR-ip-pfilter-cfg",
                                           None)
                node_4 = self._set_xml_tag(node_3, "inbound")
                self._set_xml_tag(
                    node_4, "acl-name-array", None, None, "ipv4_filter_input")
                self._set_xml_tag(
                    node_4, "is-common-array", None, None, "false")

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
                                         "address-family",
                                         "vrfipv4",
                                         "vrf-unicast",
                                         "vrf-prefixes")
            for cp in cp_infos:
                if cp.get("STATIC") is None:
                    continue
                for route in cp["STATIC"]:
                    node_2 = self._set_xml_tag(node_1, "vrf-prefix")
                    self._set_xml_tag(node_2,
                                      "prefix",
                                      None,
                                      None,
                                      route["L3-STATIC-ROUTE-ADD"])
                    self._set_xml_tag(node_2,
                                      "prefix-length",
                                      None,
                                      None,
                                      route["L3-STATIC-ROUTE-PREFIX"])
                    node_3 = self._set_xml_tag(node_2, "vrf-route")
                    node_4 = self._set_xml_tag(node_3, "vrf-next-hop-table")
                    node_5 = self._set_xml_tag(
                        node_4, "vrf-next-hop-interface-name-next-hop-address")
                    if cp["L3-CE-IF-VLAN"] == "0":
                        self._set_xml_tag(node_5,
                                          "interface-name",
                                          None,
                                          None,
                                          cp["L3-CE-IF-NAME"])
                    else:
                        self._set_xml_tag(node_5,
                                          "interface-name",
                                          None,
                                          None,
                                          cp["L3-CE-IF-NAME"] + "." +
                                          cp["L3-CE-IF-VLAN"])
                    self._set_xml_tag(node_5,
                                      "next-hop-address",
                                      None,
                                      None,
                                      route["L3-STATIC-ROUTE-NEXT"])

        if is_ospf is False:
            xml_obj.remove(xml_obj.find("ospf"))
        else:
            node_1 = self._find_xml_node(xml_obj,
                                         "ospf",
                                         "processes",
                                         "process")
            if not new_slice or cp_count > 0:
                node_1.remove(node_1.find("default-vrf"))

            node_2 = self._find_xml_node(node_1,
                                         "vrfs",
                                         "vrf")
            self._set_xml_tag_variable(node_2,
                                       "vrf-name",
                                       vrf_dtl_info["L3-VRF-NAME"])
            if new_slice is not True:
                node_2.remove(node_2.find("router-id"))
            else:
                self._set_xml_tag_variable(node_2,
                                           "router-id",
                                           vrf_dtl_info["L3-VRF-ROUTER-ID"])

            node_3 = self._find_xml_node(node_2,
                                         "redistribution",
                                         "redistributes")
            for node_4 in node_3.findall("redistribute"):
                if node_4.find("protocol-name").text == "bgp":
                    self._set_xml_tag_variable(node_4,
                                               "as-yy",
                                               str(lf_as_number),
                                               "bgp")

            node_3 = self._find_xml_node(node_2,
                                         "area-addresses",
                                         "area-area-id",
                                         "name-scopes")
            for cp in cp_infos:
                if cp.get("L3-OSPF-CP-METRIC") is None:
                    continue
                node_4 = self._set_xml_tag(node_3, "name-scope")
                self._set_xml_tag(node_4,
                                  "interface-name",
                                  None,
                                  None,
                                  self._set_vlan_if_name(
                                      cp["L3-CE-IF-NAME"],
                                      cp["L3-CE-IF-VLAN"]))
                self._set_xml_tag(node_4, "running")
                self._set_xml_tag(node_4,
                                  "cost",
                                  None,
                                  None,
                                  cp["L3-OSPF-CP-METRIC"])
                self._set_xml_tag(node_4, "priority", None, None, "10")

        if is_bgp is False:
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
            if not new_bgp:
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
                                  self._set_vlan_if_name(cp["L3-CE-IF-NAME"],
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
                self._set_xml_tag(node_5, "as-override", None, None, "true")

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
                tmp["mtu_size"] = cp["mtu_size"]
                tmp["protocol_flags"] = cp["protocol_flags"]
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
        is_ospf = False
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
                     "L3-CE-IF-CP_DEL":  bool(cp["operation"] == "delete"),
                     "L3-CE-IF-OPE": cp["operation"]}
            else:
                tmp_db = None
                continue

            cp_del = bool(cp["operation"] == "delete")
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
                    static = cp["static"]["route"]
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

            if (cp_del and p_flg.get("ospf")) or "ospf" in cp:
                is_ospf = True

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
            if cp["vlan"].get("vlan_id", "0") == "0":
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
        slice_ospf_cp_count = 0
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

                if device_cp["protocol_flags"]["ospf"] is True:

                    if device_cp.get("metric") is not None:
                        slice_ospf_cp_count += 1

        device_bgp_cp_count = 0
        device_static_cp_count = 0
        device_ospf_cp_count = 0
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

                                bgp_nei.append(bgp["remote"]["ipv4_address"])

                    if device_cp["protocol_flags"]["ospf"] is True:
                        if is_ospf is True:
                            device_ospf_cp_count += 1

        is_last_bgp = False
        is_last_static = False
        is_last_ospf = False
        if slice_bgp_cp_count == device_bgp_cp_count:
            is_last_bgp = True

        if slice_static_cp_count == device_static_cp_count:
            is_last_static = True

        if slice_ospf_cp_count == device_ospf_cp_count:
            is_last_ospf = True

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
                                           "Cisco-IOS-XR-qos-ma-cfg",
                                           None)
                node_4 = self._set_xml_tag(node_3, "input")
                node_5 = self._set_xml_tag(node_4,
                                           "service-policy",
                                           self._ATRI_OPE,
                                           self._DELETE,
                                           None)
                self._set_xml_tag(
                    node_5, "service-policy-name", None, None, "in_ce_policy")
                node_4 = self._set_xml_tag(node_3, "output")
                node_5 = self._set_xml_tag(node_4,
                                           "service-policy",
                                           self._ATRI_OPE,
                                           self._DELETE,
                                           None)
                self._set_xml_tag(
                    node_5, "service-policy-name", None, None, "out_ce_policy")
                node_3 = self._set_xml_tag(node_2,
                                           "vrf",
                                           "xmlns",
                                           "Cisco-IOS-XR-infra-rsi-cfg",
                                           vrf_dtl_info["L3-VRF-NAME"])
                node_3.attrib[self._ATRI_OPE] = self._DELETE
                node_3 = self._set_xml_tag(node_2,
                                           "ipv4-network",
                                           "xmlns",
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
                node_3 = self._set_xml_tag(node_2,
                                           "ipv4-packet-filter",
                                           "xmlns",
                                           "Cisco-IOS-XR-ip-pfilter-cfg",
                                           None)
                node_4 = self._set_xml_tag(
                    node_3, "inbound", self._ATRI_OPE, self._DELETE, None)
                self._set_xml_tag(
                    node_4, "acl-name-array", None, None, "ipv4_filter_input")
                self._set_xml_tag(
                    node_4, "is-common-array", None, None, "false")
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
                    for ownernameKey in CiscoDriver.__cisco_proper_config.keys():
                        if ownernameKey in cp["L3-CE-IF-NAME"]:
                            self._set_xml_tag(
                                node_4, "owner", None, None, CiscoDriver.__cisco_proper_config.get(ownernameKey))
                node_3 = self._set_xml_tag(node_2,
                                           "qos",
                                           "xmlns",
                                           "Cisco-IOS-XR-qos-ma-cfg",
                                           None)
                node_4 = self._set_xml_tag(node_3, "input")
                node_5 = self._set_xml_tag(node_4,
                                           "service-policy",
                                           self._ATRI_OPE,
                                           self._DELETE,
                                           None)
                self._set_xml_tag(
                    node_5, "service-policy-name", None, None, "in_ce_policy")
                node_4 = self._set_xml_tag(node_3, "output")
                node_5 = self._set_xml_tag(node_4,
                                           "service-policy",
                                           self._ATRI_OPE,
                                           self._DELETE,
                                           None)
                self._set_xml_tag(
                    node_5, "service-policy-name", None, None, "out_ce_policy")
                node_3 = self._set_xml_tag(node_2,
                                           "vrf",
                                           "xmlns",
                                           "Cisco-IOS-XR-infra-rsi-cfg",
                                           vrf_dtl_info["L3-VRF-NAME"])
                node_3.attrib[self._ATRI_OPE] = self._DELETE
                node_3 = self._set_xml_tag(node_2,
                                           "ipv4-network",
                                           "xmlns",
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
                node_3 = self._set_xml_tag(node_2,
                                           "ipv4-packet-filter",
                                           "xmlns",
                                           "Cisco-IOS-XR-ip-pfilter-cfg",
                                           None)
                node_4 = self._set_xml_tag(
                    node_3, "inbound", self._ATRI_OPE, self._DELETE, None)
                self._set_xml_tag(
                    node_4, "acl-name-array", None, None, "ipv4_filter_input")
                self._set_xml_tag(
                    node_4, "is-common-array", None, None, "false")
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
                            for ownernameKey in CiscoDriver.__cisco_proper_config.keys():
                                if ownernameKey in cp["L3-CE-IF-NAME"]:
                                    self._set_xml_tag(
                                        node_4, "owner", None, None, CiscoDriver.__cisco_proper_config.get(ownernameKey))
                    node_3 = self._set_xml_tag(node_2,
                                               "qos",
                                               "xmlns",
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
                                      "in_ce_policy")
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
                                      "out_ce_policy")
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
                node_1 = self._find_xml_node(xml_obj,
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
                        node_2 = self._set_xml_tag(node_1,
                                                   "vrf-prefix",
                                                   None,
                                                   None,
                                                   None)
                        self._set_xml_tag(node_2,
                                          "prefix",
                                          None,
                                          None,
                                          route["L3-STATIC-ROUTE-ADD"])
                        self._set_xml_tag(node_2,
                                          "prefix-length",
                                          None,
                                          None,
                                          route["L3-STATIC-ROUTE-PREFIX"])
                        node_3 = self._set_xml_tag(node_2, "vrf-route")
                        node_4 = self._set_xml_tag(
                            node_3, "vrf-next-hop-table")
                        node_5 = self._set_xml_tag(
                            node_4,
                            "vrf-next-hop-interface-name-next-hop-address",
                            self._ATRI_OPE,
                            self._DELETE,
                            None)
                        if cp["L3-CE-IF-VLAN"] == "0":
                            self._set_xml_tag(node_5,
                                              "interface-name",
                                              None,
                                              None,
                                              cp["L3-CE-IF-NAME"])
                        else:
                            self._set_xml_tag(node_5,
                                              "interface-name",
                                              None,
                                              None,
                                              cp["L3-CE-IF-NAME"] + "." +
                                              cp["L3-CE-IF-VLAN"])
                        self._set_xml_tag(node_5,
                                          "next-hop-address",
                                          None,
                                          None,
                                          route["L3-STATIC-ROUTE-NEXT"])

        if is_ospf is False:
            xml_obj.remove(xml_obj.find("ospf"))
        else:
            node_1 = self._find_xml_node(xml_obj,
                                         "ospf",
                                         "processes",
                                         "process")
            node_2 = self._find_xml_node(node_1,
                                         "vrfs",
                                         "vrf")
            self._set_xml_tag_variable(node_2,
                                       "vrf-name",
                                       vrf_dtl_info["L3-VRF-NAME"])
            if is_last_cp:
                node_1.remove(node_1.find("vrfs"))
                node_1.remove(node_1.find("start"))
                node_1.attrib[self._ATRI_OPE] = self._DELETE
            elif is_last_ospf:
                node_2.remove(node_2.find("vrf-start"))
                node_2.remove(node_2.find("area-addresses"))
                node_2.attrib[self._ATRI_OPE] = self._DELETE
            else:
                node_3 = self._find_xml_node(node_2,
                                             "area-addresses",
                                             "area-area-id",
                                             "name-scopes")
                for cp in cp_infos:
                    if (not cp["L3-CE-IF-CP_DEL"] or
                            not cp["L3-CE-IF-P_FLAGS"].get("ospf")):
                        continue
                    node_4 = self._set_xml_tag(node_3,
                                               "name-scope",
                                               self._ATRI_OPE,
                                               self._DELETE,
                                               None)
                    self._set_xml_tag(node_4,
                                      "interface-name",
                                      None,
                                      None,
                                      self._set_vlan_if_name(
                                          cp["L3-CE-IF-NAME"],
                                          cp["L3-CE-IF-VLAN"]))
        if is_bgp is False:
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
            elif is_last_bgp:
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
    def _gen_ce_lag_variable_message(self,
                                     xml_obj,
                                     device_info,
                                     ec_message,
                                     operation):
        return_val = False
        if operation == "delete":
            return_val = self._gen_del_ce_lag_variable_message(
                xml_obj, ec_message, device_info)
        else:
            return_val = self._gen_add_ce_lag_variable_message(
                xml_obj, ec_message)
        return return_val

    @decorater_log
    def _gen_add_ce_lag_variable_message(self,
                                         xml_obj,
                                         ec_message):

        is_variable_value = True

        lag_ifs = []
        lag_mem_ifs = []
        if not ec_message["device"].get("ce-lag-interface") \
                or len(ec_message["device"]["ce-lag-interface"]) == 0:
            is_variable_value = False

        for lag in ec_message["device"]["ce-lag-interface"]:
            if lag.get("name") is None \
                    or lag.get("minimum-links") is None:
                is_variable_value = False
                break
            tmp = \
                {"CL-INTERNAL-LAG-IF-NAME": lag["name"],
                 "CL-INTERNAL-LAG-LINKS": lag["minimum-links"]}
            lag_ifs.append(tmp)
            if not lag.get("leaf-interface") \
                    or len(lag["leaf-interface"]) == 0:
                is_variable_value = False

            for lag_mem in lag["leaf-interface"]:
                if lag_mem["name"] is None:
                    is_variable_value = False
                    break
                tmp_2 = \
                    {"CL-INTERNAL-IF-NAME": lag_mem["name"],
                     "CL-INTERNAL-LAG-IF-NAME":
                     lag["name"].lstrip("Bundle-Ether")}
                lag_mem_ifs.append(tmp_2)

        if is_variable_value is False:
            return False

        if_node = self._set_xml_tag(xml_obj,
                                    "interface-configurations",
                                    "xmlns",
                                    "Cisco-IOS-XR-ifmgr-cfg",
                                    None)

        for lag_if in lag_ifs:
            node_2 = self._set_xml_tag(if_node, "interface-configuration")
            self._set_xml_tag(node_2, "active", None, None, "act")
            self._set_xml_tag(node_2,
                              "interface-name",
                              None,
                              None,
                              lag_if["CL-INTERNAL-LAG-IF-NAME"])
            self._set_xml_tag(node_2, "interface-virtual")
            node_3 = self._set_xml_tag(node_2,
                                       "bundle",
                                       "xmlns",
                                       "Cisco-IOS-XR-bundlemgr-cfg",
                                       None)
            node_4 = self._set_xml_tag(node_3, "minimum-active")
            self._set_xml_tag(node_4,
                              "links",
                              None,
                              None,
                              lag_if["CL-INTERNAL-LAG-LINKS"])

        for lag_mem_if in lag_mem_ifs:
            node_2 = self._set_xml_tag(if_node, "interface-configuration")
            self._set_xml_tag(node_2, "active", None, None, "act")
            self._set_xml_tag(node_2,
                              "interface-name",
                              None,
                              None,
                              lag_mem_if["CL-INTERNAL-IF-NAME"])
            node_3 = self._set_xml_tag(node_2,
                                       "bundle-member",
                                       "xmlns",
                                       "Cisco-IOS-XR-bundlemgr-cfg",
                                       None)
            node_4 = self._set_xml_tag(node_3, "id")
            self._set_xml_tag(node_4,
                              "bundle-id",
                              None,
                              None,
                              lag_mem_if["CL-INTERNAL-LAG-IF-NAME"])
            self._set_xml_tag(node_4, "port-activity", None, None, "active")
            node_3 = self._set_xml_tag(node_2,
                                       "lacp",
                                       "xmlns",
                                       "Cisco-IOS-XR-bundlemgr-cfg",
                                       None)
            self._set_xml_tag(node_3, "period-short", None, None, "true")
            self._set_xml_tag(node_2,
                              "shutdown",
                              self._ATRI_OPE,
                              self._DELETE,
                              None)

        return True

    @decorater_log
    def _gen_del_ce_lag_variable_message(self,
                                         xml_obj,
                                         ec_message,
                                         device_info):

        is_variable_value = True

        lag_ifs = []
        lag_mem_ifs = []
        lag_name_list = []
        if not ec_message["device"].get("ce-lag-interface") \
                or len(ec_message["device"]["ce-lag-interface"]) == 0:
            is_variable_value = False

        for lag in ec_message["device"]["ce-lag-interface"]:
            if lag.get("name") is None \
                    or lag.get("minimum-links") is None:
                is_variable_value = False
                break
            tmp = \
                {"CL-INTERNAL-LAG-IF-NAME": lag["name"],
                 "CL-INTERNAL-LAG-LINKS": lag["minimum-links"]}
            lag_ifs.append(tmp)
            lag_name_list.append(lag["name"])

        if len(device_info["lag_member"]) == 0:
            is_variable_value = False

        for db_if in device_info["lag_member"]:
            if db_if["if_name"] is None:
                is_variable_value = False
                break
            elif db_if["lag_if_name"] not in lag_name_list:
                continue
            tmp_2 = {"CL-INTERNAL-IF-NAME": db_if["if_name"]}
            if tmp_2 not in lag_mem_ifs:
                lag_mem_ifs.append(tmp_2)

        if is_variable_value is False:
            return False

        if_node = self._set_xml_tag(xml_obj,
                                    "interface-configurations",
                                    "xmlns",
                                    "Cisco-IOS-XR-ifmgr-cfg",
                                    None)

        for lag_if in lag_ifs:
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
                              lag_if["CL-INTERNAL-LAG-IF-NAME"])
            self._set_xml_tag(node_2, "interface-virtual")

        if_node = self._set_xml_tag(xml_obj,
                                    "interface-configurations",
                                    "xmlns",
                                    "Cisco-IOS-XR-ifmgr-cfg",
                                    None)

        for lag_if in lag_ifs:
            node_2 = self._set_xml_tag(if_node, "interface-configuration")
            self._set_xml_tag(node_2, "active", None, None, "act")
            self._set_xml_tag(node_2,
                              "interface-name",
                              None,
                              None,
                              lag_if["CL-INTERNAL-LAG-IF-NAME"])
            self._set_xml_tag(node_2, "interface-virtual")
            if lag_if["CL-INTERNAL-LAG-LINKS"] != 0:
                node_3 = self._set_xml_tag(node_2,
                                           "bundle",
                                           "xmlns",
                                           "Cisco-IOS-XR-bundlemgr-cfg",
                                           None)
                node_4 = self._set_xml_tag(node_3, "minimum-active")
                self._set_xml_tag(node_4,
                                  "links",
                                  None,
                                  None,
                                  lag_if["CL-INTERNAL-LAG-LINKS"])

        for lag_mem_if in lag_mem_ifs:
            node_2 = self._set_xml_tag(if_node, "interface-configuration")
            self._set_xml_tag(node_2, "active", None, None, "act")
            self._set_xml_tag(node_2,
                              "interface-name",
                              None,
                              None,
                              lag_mem_if["CL-INTERNAL-IF-NAME"])
            node_3 = self._set_xml_tag(node_2,
                                       "bundle-member",
                                       "xmlns",
                                       "Cisco-IOS-XR-bundlemgr-cfg",
                                       None)
            node_3.attrib[self._ATRI_OPE] = self._DELETE
            node_3 = self._set_xml_tag(node_2,
                                       "lacp",
                                       "xmlns",
                                       "Cisco-IOS-XR-bundlemgr-cfg",
                                       None)
            node_3.attrib[self._ATRI_OPE] = self._DELETE
            self._set_xml_tag(node_2, "shutdown")

        return True

    @decorater_log
    def _gen_internal_lag_variable_message(self,
                                           xml_obj,
                                           device_info,
                                           ec_message,
                                           operation):
        return_val = False
        if operation == "delete":
            return_val = self._gen_del_internal_lag_variable_message(
                xml_obj, ec_message, device_info)
        else:
            return_val = self._gen_add_internal_lag_variable_message(
                xml_obj, ec_message, device_info)
        return return_val

    @decorater_log
    def _gen_add_internal_lag_variable_message(self,
                                               xml_obj,
                                               ec_message,
                                               device_info):
        is_spine = bool(
            device_info["device"].get("device_type") == self.name_spine)
        rp_addr = device_info["device"].get("pim_other_rp_address")

        lag_ifs = []
        lag_mem_ifs = []
        if not ec_message["device"].get("internal-lag") \
                or len(ec_message["device"]["internal-lag"]) == 0:
            return False

        for lag in ec_message["device"]["internal-lag"]:
            if lag.get("name") is None or lag.get("address") is None \
                    or self._conversion_cidr2mask(lag.get("prefix")) is None \
                    or lag.get("minimum-links") is None:
                return False
            tmp = \
                {"IL-LAG-IF-NAME": lag["name"],
                 "IL-LAG-IF-ADDR": lag["address"],
                 "IL-LAG-IF-PREFIX": self._conversion_cidr2mask(lag["prefix"]),
                 "IL-LAG-LINKS": lag["minimum-links"]}
            lag_ifs.append(tmp)
            if not lag.get("internal-interface") \
                    or len(lag["internal-interface"]) == 0:
                return False

            for lag_mem in lag["internal-interface"]:
                if lag_mem["name"] is None:
                    return False
                tmp_2 = \
                    {"IL-IF-NAME": lag_mem["name"],
                     "IL-LAG-IF-NAME": lag["name"].lstrip("Bundle-Ether")}
                lag_mem_ifs.append(tmp_2)

        if_node = self._find_xml_node(xml_obj, "interface-configurations")

        for lag_if in lag_ifs:
            node_1 = self._set_xml_tag(if_node, "interface-configuration")
            self._set_xml_tag(node_1, "active", None, None, "act")
            self._set_xml_tag(node_1,
                              "interface-name",
                              None,
                              None,
                              lag_if["IL-LAG-IF-NAME"])
            self._set_xml_tag(node_1, "interface-virtual")
            node_2 = self._set_xml_tag(node_1, "mtus")
            node_3 = self._set_xml_tag(node_2, "mtu")
            self._set_xml_tag(node_3, "owner", None, None, "etherbundle")
            self._set_xml_tag(node_3, "mtu", None, None, "4110")

            node_3 = self._set_xml_tag(node_1,
                                       "qos",
                                       "xmlns",
                                       "Cisco-IOS-XR-qos-ma-cfg",
                                       None)
            node_4 = self._set_xml_tag(node_3, "input")
            node_5 = self._set_xml_tag(node_4, "service-policy")
            self._set_xml_tag(node_5,
                              "service-policy-name",
                              None,
                              None,
                              "in_msf_policy")
            node_4 = self._set_xml_tag(node_3, "output")
            node_5 = self._set_xml_tag(node_4, "service-policy")
            self._set_xml_tag(node_5,
                              "service-policy-name",
                              None,
                              None,
                              "out_msf_policy")

            node_2 = self._set_xml_tag(node_1,
                                       "ipv4-network",
                                       "xmlns",
                                       "Cisco-IOS-XR-ipv4-io-cfg",
                                       None)
            node_3 = self._set_xml_tag(node_2, "addresses")
            node_4 = self._set_xml_tag(node_3, "primary")
            self._set_xml_tag(node_4,
                              "address",
                              None,
                              None,
                              lag_if["IL-LAG-IF-ADDR"])
            self._set_xml_tag(node_4,
                              "netmask",
                              None,
                              None,
                              lag_if["IL-LAG-IF-PREFIX"])

            node_2 = self._set_xml_tag(node_1,
                                       "bundle",
                                       "xmlns",
                                       "Cisco-IOS-XR-bundlemgr-cfg",
                                       None)
            node_3 = self._set_xml_tag(node_2, "minimum-active")
            self._set_xml_tag(node_3,
                              "links",
                              None,
                              None,
                              lag_if["IL-LAG-LINKS"])

        for lag_mem_if in lag_mem_ifs:
            node_1 = self._set_xml_tag(if_node, "interface-configuration")
            self._set_xml_tag(node_1, "active", None, None, "act")
            self._set_xml_tag(node_1,
                              "interface-name",
                              None,
                              None,
                              lag_mem_if["IL-IF-NAME"])
            node_2 = self._set_xml_tag(node_1,
                                       "bundle-member",
                                       "xmlns",
                                       "Cisco-IOS-XR-bundlemgr-cfg",
                                       None)
            node_3 = self._set_xml_tag(node_2, "id")
            self._set_xml_tag(node_3,
                              "bundle-id",
                              None,
                              None,
                              lag_mem_if["IL-LAG-IF-NAME"])
            self._set_xml_tag(node_3, "port-activity", None, None, "active")
            node_2 = self._set_xml_tag(node_1,
                                       "lacp",
                                       "xmlns",
                                       "Cisco-IOS-XR-bundlemgr-cfg",
                                       None)
            self._set_xml_tag(node_2, "period-short", None, None, "true")
            self._set_xml_tag(node_1,
                              "shutdown",
                              self._ATRI_OPE,
                              self._DELETE,
                              None)

        node_0 = self._find_xml_node(xml_obj,
                                     "ospf",
                                     "processes",
                                     "process")
        self._set_xml_tag(node_0, "start")
        node_1 = self._find_xml_node(node_0,
                                     "default-vrf",
                                     "area-addresses",
                                     "area-area-id",
                                     "name-scopes")
        for lag_if in lag_ifs:
            node_2 = self._set_xml_tag(node_1, "name-scope")
            self._set_xml_tag(node_2,
                              "interface-name",
                              None,
                              None,
                              lag_if["IL-LAG-IF-NAME"])
            self._set_xml_tag(node_2, "running")
            self._set_xml_tag(node_2, "cost", None, None, "100")
            self._set_xml_tag(node_2, "priority", None, None, "20")

        node_1 = self._find_xml_node(xml_obj,
                                     "mpls-ldp",
                                     "default-vrf",
                                     "interfaces")
        for lag_if in lag_ifs:
            node_2 = self._set_xml_tag(node_1, "interface")
            self._set_xml_tag(node_2,
                              "interface-name",
                              None,
                              None,
                              lag_if["IL-LAG-IF-NAME"])
            self._set_xml_tag(node_2, "enable")
            node_3 = self._set_xml_tag(node_2, "global")
            node_4 = self._set_xml_tag(node_3, "discovery")
            node_5 = self._set_xml_tag(node_4, "link-hello")
            self._set_xml_tag(node_5, "hold-time", None, None, "15")
            self._set_xml_tag(node_5, "interval", None, None, "5")

        if is_spine:
            node_1 = self._find_xml_node(xml_obj,
                                         "mfwd",
                                         "default-context",
                                         "ipv4",
                                         "interfaces")
            for lag_if in lag_ifs:
                node_2 = self._set_xml_tag(node_1, "interface")
                self._set_xml_tag(node_2,
                                  "interface-name",
                                  None,
                                  None,
                                  lag_if["IL-LAG-IF-NAME"])
                self._set_xml_tag(node_2,
                                  "enable-on-interface",
                                  None,
                                  None,
                                  "true")

            self._set_xml_tag_variable(xml_obj,
                                       "rp-address",
                                       rp_addr,
                                       "pim",
                                       "default-context",
                                       "ipv4",
                                       "sparse-mode-rp-addresses",
                                       "sparse-mode-rp-address")
            node_1 = self._find_xml_node(xml_obj,
                                         "pim",
                                         "default-context",
                                         "ipv4",
                                         "interfaces")
            for lag_if in lag_ifs:
                node_2 = self._set_xml_tag(node_1, "interface")
                self._set_xml_tag(node_2,
                                  "interface-name",
                                  None,
                                  None,
                                  lag_if["IL-LAG-IF-NAME"])
                self._set_xml_tag(node_2, "enable")
                self._set_xml_tag(node_2,
                                  "interface-enable",
                                  None,
                                  None,
                                  "true")
        else:
            xml_obj.remove(self._find_xml_node(xml_obj, "mfwd"))
            xml_obj.remove(self._find_xml_node(xml_obj, "pim"))

        return True

    @decorater_log
    def _check_all_del_lag(self, lag_name, lag_mem_ifs, device_info):
        del_count = 0
        db_count = 0
        for lag_mem in lag_mem_ifs:
            del_count += 1 if lag_mem.get("IL-LAG-IF-NAME") == lag_name else 0
        for db_lag_mem in device_info.get("lag_member"):
            db_count += 1 if db_lag_mem.get("lag_if_name") == lag_name else 0
        return bool(del_count == db_count)

    @decorater_log
    def _gen_del_internal_lag_variable_message(self,
                                               xml_obj,
                                               ec_message,
                                               device_info):
        is_spine = bool(
            device_info["device"].get("device_type") == self.name_spine)
        rp_addr = device_info["device"].get("pim_other_rp_address")

        lag_ifs = []
        lag_ifs_for_mem = []
        lag_mem_ifs = []
        if not ec_message["device"].get("internal-lag") \
                or len(ec_message["device"]["internal-lag"]) == 0:
            return False

        for lag in ec_message["device"]["internal-lag"]:
            if lag.get("name") is None or lag.get("minimum-links") is None:
                return False
            tmp = \
                {"IL-LAG-IF-NAME": lag["name"],
                 "IL-LAG-LINKS": lag["minimum-links"]}
            lag_ifs_for_mem.append(tmp)

            for lag_mem in lag["internal-interface"]:
                if lag_mem.get("name") is None:
                    return False
                tmp_2 = \
                    {"IL-IF-NAME": lag_mem["name"],
                     "IL-LAG-IF-NAME": lag["name"]}
                lag_mem_ifs.append(tmp_2)

        for lag in lag_ifs_for_mem:
            if self._check_all_del_lag(lag["IL-LAG-IF-NAME"],
                                       lag_mem_ifs,
                                       device_info):
                lag_ifs.append(lag.copy())

        if len(lag_ifs) > 0:
            if_node = self._find_xml_node(xml_obj, "interface-configurations")

            for lag_if in lag_ifs:
                node_1 = self._set_xml_tag(if_node,
                                           "interface-configuration",
                                           self._ATRI_OPE,
                                           self._DELETE)
                self._set_xml_tag(node_1, "active", None, None, "act")
                self._set_xml_tag(node_1,
                                  "interface-name",
                                  None,
                                  None,
                                  lag_if["IL-LAG-IF-NAME"])
                self._set_xml_tag(node_1, "interface-virtual")

            node_1 = self._find_xml_node(xml_obj,
                                         "ospf",
                                         "processes",
                                         "process",
                                         "default-vrf",
                                         "area-addresses",
                                         "area-area-id",
                                         "name-scopes")
            for lag_if in lag_ifs:
                node_2 = self._set_xml_tag(
                    node_1, "name-scope", self._ATRI_OPE, self._DELETE)
                self._set_xml_tag(node_2,
                                  "interface-name",
                                  None,
                                  None,
                                  lag_if["IL-LAG-IF-NAME"])

            node_1 = self._find_xml_node(xml_obj,
                                         "mpls-ldp",
                                         "default-vrf",
                                         "interfaces")
            for lag_if in lag_ifs:
                node_2 = self._set_xml_tag(
                    node_1, "interface", self._ATRI_OPE, self._DELETE)
                self._set_xml_tag(node_2,
                                  "interface-name",
                                  None,
                                  None,
                                  lag_if["IL-LAG-IF-NAME"])

            if is_spine:
                node_1 = self._find_xml_node(xml_obj,
                                             "mfwd",
                                             "default-context",
                                             "ipv4",
                                             "interfaces")
                for lag_if in lag_ifs:
                    node_2 = self._set_xml_tag(node_1,
                                               "interface",
                                               self._ATRI_OPE,
                                               self._DELETE)
                    self._set_xml_tag(node_2,
                                      "interface-name",
                                      None,
                                      None,
                                      lag_if["IL-LAG-IF-NAME"])

                self._set_xml_tag_variable(xml_obj,
                                           "rp-address",
                                           rp_addr,
                                           "pim",
                                           "default-context",
                                           "ipv4",
                                           "sparse-mode-rp-addresses",
                                           "sparse-mode-rp-address")
                node_1 = self._find_xml_node(xml_obj,
                                             "pim",
                                             "default-context",
                                             "ipv4",
                                             "interfaces")
                for lag_if in lag_ifs:
                    node_2 = self._set_xml_tag(node_1,
                                               "interface",
                                               self._ATRI_OPE,
                                               self._DELETE)
                    self._set_xml_tag(node_2,
                                      "interface-name",
                                      None,
                                      None,
                                      lag_if["IL-LAG-IF-NAME"])
            else:
                xml_obj.remove(self._find_xml_node(xml_obj, "mfwd"))
                xml_obj.remove(self._find_xml_node(xml_obj, "pim"))
        else:
            for node_1 in xml_obj:
                xml_obj.remove(node_1)

        if_node = self._set_xml_tag(xml_obj,
                                    "interface-configurations",
                                    "xmlns",
                                    "Cisco-IOS-XR-ifmgr-cfg",
                                    None)

        for lag_if in lag_ifs_for_mem:
            node_1 = self._set_xml_tag(if_node, "interface-configuration")
            self._set_xml_tag(node_1, "active", None, None, "act")
            self._set_xml_tag(node_1,
                              "interface-name",
                              None,
                              None,
                              lag_if["IL-LAG-IF-NAME"])
            self._set_xml_tag(node_1, "interface-virtual")
            node_2 = self._set_xml_tag(node_1,
                                       "bundle",
                                       "xmlns",
                                       "Cisco-IOS-XR-bundlemgr-cfg",
                                       None)
            node_3 = self._set_xml_tag(node_2, "minimum-active")
            self._set_xml_tag(node_3,
                              "links",
                              None,
                              None,
                              lag_if["IL-LAG-LINKS"])

        for lag_mem_if in lag_mem_ifs:
            node_1 = self._set_xml_tag(if_node, "interface-configuration")
            self._set_xml_tag(node_1, "active", None, None, "act")
            self._set_xml_tag(node_1,
                              "interface-name",
                              None,
                              None,
                              lag_mem_if["IL-IF-NAME"])
            node_2 = self._set_xml_tag(node_1,
                                       "bundle-member",
                                       "xmlns",
                                       "Cisco-IOS-XR-bundlemgr-cfg",
                                       None)
            node_2.attrib[self._ATRI_OPE] = self._DELETE
            node_2 = self._set_xml_tag(node_1,
                                       "lacp",
                                       "xmlns",
                                       "Cisco-IOS-XR-bundlemgr-cfg",
                                       None)
            node_2.attrib[self._ATRI_OPE] = self._DELETE
            self._set_xml_tag(node_1, "shutdown")

        return True

    @decorater_log
    def _validation_l3_slice(self, device_info):
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
        class ns_xml(object):
            class ns_list(object):
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
                         ns_list.bgp:
                         ns_list.ifmgr:
                         ns_list.qos:
                         ns_list.io:
                         ns_list.pfilter:
                          "Cisco-IOS-XR-ip-pfilter-cfg"),
                         ns_list.l2_eth:
                          "Cisco-IOS-XR-l2-eth-infra-cfg"),
                         ns_list.static:
                         ns_list.ospf:
                         ns_list.vrrp:

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
                        group_id = db_vrrp.get("gropu_id")
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
