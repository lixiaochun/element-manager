# -*- coding: utf-8 -*-
from EmSeparateDriver import EmSeparateDriver
from EmCommonLog import decorater_log


class JuniperDriver5100(EmSeparateDriver):

    __LAG_TYPE_IN_LINK = 1
    __PORT_MODE_ACCESS = "access"
    __PORT_MODE_TRUNK = "trunk"
    __DELETE = "delete"

    @decorater_log
    def __init__(self):
        self.as_super = super(JuniperDriver5100, self)
        self.as_super.__init__()
        self.list_enable_service = [self.name_spine,
                                    self.name_leaf,
                                    self.name_l2_slice,
                                    self.name_l3_slice,
                                    self.name_celag,
                                    self.name_internal_lag]
        tmp_get_mes = (
        self.get_config_message = {
            self.name_spine: tmp_get_mes,
            self.name_leaf: tmp_get_mes,
            self.name_l2_slice: tmp_get_mes,
            self.name_l3_slice: tmp_get_mes,
            self.name_celag: tmp_get_mes,
            self.name_internal_lag: tmp_get_mes}

    @decorater_log
    def _send_control_signal(self,
                             device_name,
                             message_type,
                             send_message=None,
                             service_type=None,
                             operation=None):
        is_result, message = (self.as_super.
                              _send_control_signal(device_name,
                                                   message_type,
                                                   send_message))
        if not is_result and isinstance(message, str) and "<ok/>" in message:
            is_result = True
        return is_result, message

    @decorater_log
    def _set_conf_device_count(self, ec_message, device_info):
        ret_val = 300
        return ret_val


    @decorater_log
    def _gen_spine_fix_message(self, xml_obj, operation):
        node_1 = self._set_xml_tag(xml_obj,
                                   "configuration",
                                   "xmlns",
                                   None)
        node_2 = self._set_xml_tag(node_1, "system")
        self._set_xml_tag(node_2, "host-name")
        node_3 = self._set_xml_tag(node_2, "ntp")
        node_4 = self._set_xml_tag(node_3, "server")
        self._set_xml_tag(node_4, "address")
        node_4 = self._set_xml_tag(node_3, "source-address")
        node_2 = self._set_xml_tag(node_1, "chassis")
        node_3 = self._set_xml_tag(node_2, "aggregated-devices")
        node_4 = self._set_xml_tag(node_3, "ethernet")
        self._set_xml_tag(node_4, "device-count")
        node_2 = self._set_xml_tag(node_1, "interfaces")

        node_2 = self._set_xml_tag(node_1, "snmp")
        node_3 = self._set_xml_tag(node_2, "community")
        self._set_xml_tag(node_3, "community")
        self._set_xml_tag(node_3, "authorization", None, None, "read-only")
        node_3 = self._set_xml_tag(node_2, "trap-options")
        self._set_xml_tag(node_3, "source-address")
        node_3 = self._set_xml_tag(node_2, "trap-group")
        self._set_xml_tag(node_3, "group-name")
        self._set_xml_tag(node_3, "version", None, None, "v2")
        node_4 = self._set_xml_tag(node_3, "targets")
        self._set_xml_tag(node_4, "target")

        node_2 = self._set_xml_tag(node_1, "routing-options")
        self._set_xml_tag(node_2, "router-id")
        node_3 = self._set_xml_tag(node_2, "forwarding-table")
        node_4 = self._set_xml_tag(node_3, "export", None, None, "ECMP")
        node_3 = self._set_xml_tag(node_2, "multicast")
        node_4 = self._set_xml_tag(node_3, "flow-map")
        self._set_xml_tag(node_4, "map-name", None, None, "Never-Cache")
        node_5 = self._set_xml_tag(node_4, "policy")
        self._set_xml_tag(node_5, "value", None, None, "Multicast_Never")
        node_5 = self._set_xml_tag(node_4, "forwarding-cache")
        node_6 = self._set_xml_tag(node_5, "timeout")
        node_7 = self._set_xml_tag(node_6, "never")
        self._set_xml_tag(node_7, "non-discard-entry-only")

        node_2 = self._set_xml_tag(node_1, "protocols")
        node_3 = self._set_xml_tag(node_2, "mpls")
        self._set_xml_tag(
            node_3, "traffic-engineering", None, None, "bgp-igp-both-ribs")
        self._set_xml_tag(node_3, "ipv6-tunneling")
        node_4 = self._set_xml_tag(node_3, "interface")
        self._set_xml_tag(node_4, "interface_name", None, None, "all")
        node_3 = self._set_xml_tag(node_2, "msdp")
        node_4 = self._set_xml_tag(node_3, "peer")
        self._set_xml_tag(node_4, "address")
        self._set_xml_tag(node_4, "local-address")
        self._set_xml_tag(node_4, "keep-alive", None, None, "30")
        self._set_xml_tag(node_4, "hold-time", None, None, "90")
        self._set_xml_tag(node_4, "sa-hold-time", None, None, "300")
        node_3 = self._set_xml_tag(node_2, "ospf")
        node_4 = self._set_xml_tag(node_3, "area")
        self._set_xml_tag(node_4, "area_id", None, None, "0.0.0.0")
        node_3 = self._set_xml_tag(node_2, "ldp")
        node_4 = self._set_xml_tag(node_3, "interface")
        self._set_xml_tag(node_4, "interface_name", None, None, "all")
        self._set_xml_tag(node_4, "hello-interval", None, None, "5")
        self._set_xml_tag(node_4, "hold-time", None, None, "15")
        node_3 = self._set_xml_tag(node_2, "pim")
        node_4 = self._set_xml_tag(node_3, "rp")
        node_4 = self._set_xml_tag(node_3, "interface")
        self._set_xml_tag(node_4, "interface_name", None, None, "all")

        node_2 = self._set_xml_tag(node_1, "class-of-service")
        node_3 = self._set_xml_tag(node_2, "interfaces")

        return True

    @decorater_log
    def _gen_leaf_fix_message(self, xml_obj, operation):
        node_1 = self._set_xml_tag(xml_obj,
                                   "configuration",
                                   "xmlns",
                                   None)
        node_2 = self._set_xml_tag(node_1, "system")
        self._set_xml_tag(node_2, "host-name")
        node_3 = self._set_xml_tag(node_2, "ntp")
        node_4 = self._set_xml_tag(node_3, "server")
        self._set_xml_tag(node_4, "address")
        self._set_xml_tag(node_3, "source-address")
        node_2 = self._set_xml_tag(node_1, "chassis")
        node_3 = self._set_xml_tag(node_2, "aggregated-devices")
        node_4 = self._set_xml_tag(node_3, "ethernet")
        self._set_xml_tag(node_4, "device-count")
        node_2 = self._set_xml_tag(node_1, "interfaces")

        node_2 = self._set_xml_tag(node_1, "snmp")
        node_3 = self._set_xml_tag(node_2, "community")
        self._set_xml_tag(node_3, "community")
        self._set_xml_tag(node_3, "authorization", None, None, "read-only")
        node_3 = self._set_xml_tag(node_2, "trap-options")
        self._set_xml_tag(node_3, "source-address")
        node_3 = self._set_xml_tag(node_2, "trap-group")
        self._set_xml_tag(node_3, "group-name")
        self._set_xml_tag(node_3, "version", None, None, "v2")
        node_4 = self._set_xml_tag(node_3, "targets")
        self._set_xml_tag(node_4, "target")

        node_2 = self._set_xml_tag(node_1, "routing-options")
        self._set_xml_tag(node_2, "router-id")
        self._set_xml_tag(node_2, "autonomous-system")
        node_3 = self._set_xml_tag(node_2, "forwarding-table")
        self._set_xml_tag(node_3, "export", None, None, "ECMP")
        node_3 = self._set_xml_tag(node_2, "multicast")
        node_4 = self._set_xml_tag(node_3, "flow-map")
        self._set_xml_tag(node_4, "map-name", None, None, "Never-Cache")
        node_5 = self._set_xml_tag(node_4, "policy")
        self._set_xml_tag(node_5, "value", None, None, "Multicast_Never")
        node_5 = self._set_xml_tag(node_4, "forwarding-cache")
        node_6 = self._set_xml_tag(node_5, "timeout")
        node_7 = self._set_xml_tag(node_6, "never")
        self._set_xml_tag(node_7, "non-discard-entry-only")

        node_2 = self._set_xml_tag(node_1, "protocols")
        node_3 = self._set_xml_tag(node_2, "mpls")
        self._set_xml_tag(
            node_3, "traffic-engineering", None, None, "bgp-igp-both-ribs")
        self._set_xml_tag(node_3, "ipv6-tunneling")
        node_4 = self._set_xml_tag(node_3, "interface")
        self._set_xml_tag(node_4, "interface_name", None, None, "all")
        node_3 = self._set_xml_tag(node_2, "bgp")
        node_4 = self._set_xml_tag(node_3, "group")
        self._set_xml_tag(node_4, "group_name", None, None, "VPN")
        self._set_xml_tag(node_4, "type", None, None, "internal")
        self._set_xml_tag(node_4, "local-address")
        self._set_xml_tag(node_4, "hold-time", None, None, "90")
        node_5 = self._set_xml_tag(node_4, "family")
        node_6 = self._set_xml_tag(node_5, "inet-vpn")
        self._set_xml_tag(node_6, "unicast")
        node_6 = self._set_xml_tag(node_5, "inet6-vpn")
        self._set_xml_tag(node_6, "unicast")
        self._set_xml_tag(node_4, "vpn-apply-export")
        self._set_xml_tag(node_4, "peer-as")
        node_3 = self._set_xml_tag(node_2, "ospf")
        node_4 = self._set_xml_tag(node_3, "area")
        self._set_xml_tag(node_4, "area_id", None, None, "0.0.0.0")
        node_3 = self._set_xml_tag(node_2, "vrrp")
        self._set_xml_tag(node_3, "asymmetric-hold-time")
        node_3 = self._set_xml_tag(node_2, "ldp")
        node_4 = self._set_xml_tag(node_3, "interface")
        self._set_xml_tag(node_4, "interface_name", None, None, "all")
        self._set_xml_tag(node_4, "hello-interval", None, None, "5")
        self._set_xml_tag(node_4, "hold-time", None, None, "15")
        node_3 = self._set_xml_tag(node_2, "pim")
        node_4 = self._set_xml_tag(node_3, "rp")
        node_5 = self._set_xml_tag(node_4, "static")
        node_6 = self._set_xml_tag(node_5, "address")
        self._set_xml_tag(node_6, "addr")
        self._set_xml_tag(node_6, "version", None, None, "2")
        node_4 = self._set_xml_tag(node_3, "interface")
        self._set_xml_tag(node_4, "interface_name", None, None, "all")
        node_2 = self._set_xml_tag(node_1, "policy-options")
        node_3 = self._set_xml_tag(node_2, "policy-statement")
        self._set_xml_tag(node_3, "policy_name", None, None, "VPN_export")

        node_4 = self._set_xml_tag(node_3, "term")
        self._set_xml_tag(node_4, "term_name", None, None, "98")
        node_5 = self._set_xml_tag(node_4, "from")
        self._set_xml_tag(node_5, "protocol", None, None, "ospf")
        node_5 = self._set_xml_tag(node_4, "then")
        node_6 = self._set_xml_tag(node_5, "community")
        self._set_xml_tag(node_6, "add")
        self._set_xml_tag(
            node_6, "community-name", None, None, "OSPF_domain_id")
        node_6 = self._set_xml_tag(node_5, "community")
        self._set_xml_tag(node_6, "add")
        self._set_xml_tag(
            node_6, "community-name", None, None, "OSPF_router_id")

        node_4 = self._set_xml_tag(node_3, "term")
        self._set_xml_tag(node_4, "term_name", None, None, "99")
        node_5 = self._set_xml_tag(node_4, "then")
        node_6 = self._set_xml_tag(node_5, "community")
        self._set_xml_tag(node_6, "add")
        self._set_xml_tag(
            node_6, "community-name", None, None, "MSF_belonging_side")

        node_3 = self._set_xml_tag(node_2, "policy-statement")
        self._set_xml_tag(node_3, "policy_name", None, None, "VPN_import")
        node_4 = self._set_xml_tag(node_3, "term")
        self._set_xml_tag(node_4, "term_name", None, None, "high")
        node_5 = self._set_xml_tag(node_4, "from")
        node_6 = self._set_xml_tag(node_5, "community")
        self._set_xml_tag(node_6, "value", None, None, "MSF_belonging_side")
        node_5 = self._set_xml_tag(node_4, "then")
        node_6 = self._set_xml_tag(node_5, "local-preference")
        self._set_xml_tag(node_6, "local-preference", None, None, "200")
        node_6 = self._set_xml_tag(node_5, "accept")
        node_4 = self._set_xml_tag(node_3, "term")
        self._set_xml_tag(node_4, "term_name", None, None, "other")
        node_5 = self._set_xml_tag(node_4, "then")
        node_6 = self._set_xml_tag(node_5, "local-preference")
        self._set_xml_tag(node_6, "local-preference", None, None, "50")
        node_6 = self._set_xml_tag(node_5, "accept")

        node_3 = self._set_xml_tag(node_2, "policy-statement")
        self._set_xml_tag(
            node_3, "policy_name", None, None, "eBGPv4_To_active-CE_export")
        node_4 = self._set_xml_tag(node_3, "term")
        self._set_xml_tag(node_4, "term_name", None, None, "1")
        node_5 = self._set_xml_tag(node_4, "from")
        self._set_xml_tag(node_5, "protocol", None, None, "bgp")
        self._set_xml_tag(node_5, "protocol", None, None, "direct")
        self._set_xml_tag(node_5, "protocol", None, None, "ospf")
        self._set_xml_tag(node_5, "protocol", None, None, "static")
        node_5 = self._set_xml_tag(node_4, "then")
        node_6 = self._set_xml_tag(node_5, "metric")
        self._set_xml_tag(node_6, "metric", None, None, "500")
        self._set_xml_tag(node_5, "origin", None, None, "igp")
        node_6 = self._set_xml_tag(node_5, "community")
        self._set_xml_tag(node_6, "delete")
        self._set_xml_tag(
            node_6, "community-name", None, None, "MSF_community")
        node_6 = self._set_xml_tag(node_5, "community")
        self._set_xml_tag(node_6, "delete")
        self._set_xml_tag(
            node_6, "community-name", None, None, "Target_community")
        node_6 = self._set_xml_tag(node_5, "community")
        self._set_xml_tag(node_6, "delete")
        self._set_xml_tag(
            node_6, "community-name", None, None, "ALL_ext_communities")
        self._set_xml_tag(node_5, "accept")
        node_4 = self._set_xml_tag(node_3, "term")
        self._set_xml_tag(node_4, "term_name", None, None, "2")
        node_5 = self._set_xml_tag(node_4, "then")
        node_6 = self._set_xml_tag(node_5, "reject")

        node_3 = self._set_xml_tag(node_2, "policy-statement")
        self._set_xml_tag(
            node_3, "policy_name", None, None, "eBGPv4_To_standby-CE_export")
        node_4 = self._set_xml_tag(node_3, "term")
        self._set_xml_tag(node_4, "term_name", None, None, "1")
        node_5 = self._set_xml_tag(node_4, "from")
        self._set_xml_tag(node_5, "protocol", None, None, "bgp")
        self._set_xml_tag(node_5, "protocol", None, None, "direct")
        self._set_xml_tag(node_5, "protocol", None, None, "ospf")
        self._set_xml_tag(node_5, "protocol", None, None, "static")
        node_5 = self._set_xml_tag(node_4, "then")
        node_6 = self._set_xml_tag(node_5, "metric")
        self._set_xml_tag(node_6, "metric", None, None, "1000")
        self._set_xml_tag(node_5, "origin", None, None, "igp")
        node_6 = self._set_xml_tag(node_5, "community")
        self._set_xml_tag(node_6, "delete")
        self._set_xml_tag(
            node_6, "community-name", None, None, "MSF_community")
        node_6 = self._set_xml_tag(node_5, "community")
        self._set_xml_tag(node_6, "delete")
        self._set_xml_tag(
            node_6, "community-name", None, None, "Target_community")
        node_6 = self._set_xml_tag(node_5, "community")
        self._set_xml_tag(node_6, "delete")
        self._set_xml_tag(
            node_6, "community-name", None, None, "ALL_ext_communities")
        self._set_xml_tag(node_5, "accept")
        node_4 = self._set_xml_tag(node_3, "term")
        self._set_xml_tag(node_4, "term_name", None, None, "2")
        node_5 = self._set_xml_tag(node_4, "then")
        node_6 = self._set_xml_tag(node_5, "reject")

        node_3 = self._set_xml_tag(node_2, "policy-statement")
        self._set_xml_tag(
            node_3, "policy_name", None, None, "eBGPv4_To_CE_import")
        node_4 = self._set_xml_tag(node_3, "term")
        self._set_xml_tag(node_4, "term_name", None, None, "1")
        node_5 = self._set_xml_tag(node_4, "from")
        self._set_xml_tag(node_5, "protocol", None, None, "bgp")
        node_5 = self._set_xml_tag(node_4, "then")
        node_6 = self._set_xml_tag(node_5, "community")
        self._set_xml_tag(node_6, "delete")
        self._set_xml_tag(
            node_6, "community-name", None, None, "MSF_community")
        self._set_xml_tag(node_5, "accept")

        node_3 = self._set_xml_tag(node_2, "policy-statement")
        self._set_xml_tag(
            node_3, "policy_name", None, None, "eBGPv6_To_active-CE_export")
        node_4 = self._set_xml_tag(node_3, "term")
        self._set_xml_tag(node_4, "term_name", None, None, "1")
        node_5 = self._set_xml_tag(node_4, "from")
        self._set_xml_tag(node_5, "protocol", None, None, "bgp")
        self._set_xml_tag(node_5, "protocol", None, None, "direct")
        self._set_xml_tag(node_5, "protocol", None, None, "ospf")
        self._set_xml_tag(node_5, "protocol", None, None, "static")
        node_5 = self._set_xml_tag(node_4, "then")
        node_6 = self._set_xml_tag(node_5, "metric")
        self._set_xml_tag(node_6, "metric", None, None, "500")
        self._set_xml_tag(node_5, "origin", None, None, "igp")
        node_6 = self._set_xml_tag(node_5, "community")
        self._set_xml_tag(node_6, "delete")
        self._set_xml_tag(
            node_6, "community-name", None, None, "MSF_community")
        node_6 = self._set_xml_tag(node_5, "community")
        self._set_xml_tag(node_6, "delete")
        self._set_xml_tag(
            node_6, "community-name", None, None, "Target_community")
        node_6 = self._set_xml_tag(node_5, "community")
        self._set_xml_tag(node_6, "delete")
        self._set_xml_tag(
            node_6, "community-name", None, None, "ALL_ext_communities")
        self._set_xml_tag(node_5, "accept")
        node_4 = self._set_xml_tag(node_3, "term")
        self._set_xml_tag(node_4, "term_name", None, None, "2")
        node_5 = self._set_xml_tag(node_4, "then")
        node_6 = self._set_xml_tag(node_5, "reject")

        node_3 = self._set_xml_tag(node_2, "policy-statement")
        self._set_xml_tag(
            node_3, "policy_name", None, None, "eBGPv6_To_standby-CE_export")
        node_4 = self._set_xml_tag(node_3, "term")
        self._set_xml_tag(node_4, "term_name", None, None, "1")
        node_5 = self._set_xml_tag(node_4, "from")
        self._set_xml_tag(node_5, "protocol", None, None, "bgp")
        self._set_xml_tag(node_5, "protocol", None, None, "direct")
        self._set_xml_tag(node_5, "protocol", None, None, "ospf")
        self._set_xml_tag(node_5, "protocol", None, None, "static")
        node_5 = self._set_xml_tag(node_4, "then")
        node_6 = self._set_xml_tag(node_5, "metric")
        self._set_xml_tag(node_6, "metric", None, None, "1000")
        self._set_xml_tag(node_5, "origin", None, None, "igp")
        node_6 = self._set_xml_tag(node_5, "community")
        self._set_xml_tag(node_6, "delete")
        self._set_xml_tag(
            node_6, "community-name", None, None, "MSF_community")
        node_6 = self._set_xml_tag(node_5, "community")
        self._set_xml_tag(node_6, "delete")
        self._set_xml_tag(
            node_6, "community-name", None, None, "Target_community")
        node_6 = self._set_xml_tag(node_5, "community")
        self._set_xml_tag(node_6, "delete")
        self._set_xml_tag(
            node_6, "community-name", None, None, "ALL_ext_communities")
        self._set_xml_tag(node_5, "accept")
        node_4 = self._set_xml_tag(node_3, "term")
        self._set_xml_tag(node_4, "term_name", None, None, "2")
        node_5 = self._set_xml_tag(node_4, "then")
        node_6 = self._set_xml_tag(node_5, "reject")

        node_3 = self._set_xml_tag(node_2, "policy-statement")
        self._set_xml_tag(
            node_3, "policy_name", None, None, "eBGPv6_To_CE_import")
        node_4 = self._set_xml_tag(node_3, "term")
        self._set_xml_tag(node_4, "term_name", None, None, "1")
        node_5 = self._set_xml_tag(node_4, "from")
        self._set_xml_tag(node_5, "protocol", None, None, "bgp")
        node_5 = self._set_xml_tag(node_4, "then")
        node_6 = self._set_xml_tag(node_5, "community")
        self._set_xml_tag(node_6, "delete")
        self._set_xml_tag(
            node_6, "community-name", None, None, "MSF_community")
        self._set_xml_tag(node_5, "accept")

        node_4 = self._set_xml_tag(node_2, "community")
        self._set_xml_tag(
            node_4, "community_name", None, None, "MSF_community")
        node_5 = self._set_xml_tag(node_4, "members")
        self._set_xml_tag(node_5, "value")
        node_4 = self._set_xml_tag(node_2, "community")
        self._set_xml_tag(
            node_4, "community_name", None, None, "Target_community")
        node_5 = self._set_xml_tag(node_4, "members")
        self._set_xml_tag(node_5, "value", None, None, "target:*:*")
        node_4 = self._set_xml_tag(node_2, "community")
        self._set_xml_tag(
            node_4, "community_name", None, None, "MSF_belonging_side")
        node_5 = self._set_xml_tag(node_4, "members")
        self._set_xml_tag(node_5, "value")
        node_4 = self._set_xml_tag(node_2, "community")
        self._set_xml_tag(
            node_4, "community_name", None, None, "OSPF_domain_id")
        node_5 = self._set_xml_tag(node_4, "members")
        self._set_xml_tag(node_5, "value", None, None, "0x0005:64050:0")
        node_4 = self._set_xml_tag(node_2, "community")
        self._set_xml_tag(
            node_4, "community_name", None, None, "OSPF_router_id")
        node_5 = self._set_xml_tag(node_4, "members")
        self._set_xml_tag(node_5, "value")
        node_4 = self._set_xml_tag(node_2, "community")
        self._set_xml_tag(node_4,
                          "community_name",
                          None,
                          None,
                          "ALL_ext_communities")
        node_5 = self._set_xml_tag(node_4, "members")
        self._set_xml_tag(node_5, "value", None, None, "0x*:*:*")

        node_2 = self._set_xml_tag(node_1, "class-of-service")
        node_3 = self._set_xml_tag(node_2, "interfaces")

        node_2 = self._set_xml_tag(node_1, "switch-options")
        self._set_xml_tag(node_2, "vtep-source-interface", None, None, "lo0.0")

        return True

    @decorater_log
    def _gen_l2_slice_fix_message(self, xml_obj, operation):
        node_1 = self._set_xml_tag(xml_obj,
                                   "configuration",
                                   "xmlns",
                                   None)
        self._set_xml_tag(node_1, "interfaces")

        self._set_xml_tag(node_1, "vlans")

        node_2 = self._set_xml_tag(node_1, "class-of-service")
        self._set_xml_tag(node_2, "interfaces")
        return True

    @decorater_log
    def _gen_l3_slice_fix_message(self, xml_obj, operation):
        node_1 = self._set_xml_tag(xml_obj,
                                   "configuration",
                                   "xmlns",
                                   None)
        self._set_xml_tag(node_1, "interfaces")
        node_2 = self._set_xml_tag(node_1, "routing-instances")
        node_3 = self._set_xml_tag(node_2, "instance")
        self._set_xml_tag(node_3, "name")
        if operation != self.__DELETE:
            self._set_xml_tag(node_3, "instance-type", None, None, "vrf")
            node_4 = self._set_xml_tag(node_3, "route-distinguisher")
            self._set_xml_tag(node_4, "rd-type")
            node_4 = self._set_xml_tag(node_3, "vrf-target")
            self._set_xml_tag(node_4, "community")
            self._set_xml_tag(node_3, "vrf-table-label")
            self._set_xml_tag(node_3, "no-vrf-propagate-ttl")
        node_4 = self._set_xml_tag(node_3, "routing-options")
        if operation != self.__DELETE:
            self._set_xml_tag(node_4, "router-id")
        node_2 = self._set_xml_tag(node_1, "class-of-service")
        self._set_xml_tag(node_2, "interfaces")

        return True

    @decorater_log
    def _gen_ce_lag_fix_message(self, xml_obj, operation):
        node_1 = self._set_xml_tag(xml_obj,
                                   "configuration",
                                   "xmlns",
                                   None)
        self._set_xml_tag(node_1, "interfaces")
        return True

    @decorater_log
    def _gen_internal_fix_lag_message(self, xml_obj, operation):
        node_1 = self._set_xml_tag(xml_obj,
                                   "configuration",
                                   "xmlns",
                                   None)
        self._set_xml_tag(node_1, "interfaces")
        node_2 = self._set_xml_tag(node_1, "protocols")
        node_3 = self._set_xml_tag(node_2, "ospf")
        node_4 = self._set_xml_tag(node_3, "area")
        self._set_xml_tag(node_4, "area_id", None, None, "0.0.0.0")
        node_2 = self._set_xml_tag(node_1, "class-of-service")
        self._set_xml_tag(node_2, "interfaces")
        return True


    @staticmethod
    @decorater_log
    def _set_cidr_ip_address(address, prefix):
        return address + "/" + str(prefix)

    @decorater_log
    def _gen_spine_variable_message(self,
                                    xml_obj,
                                    device_info,
                                    ec_message,
                                    operation):
        is_variable_value = True
        dev_reg_info = {}
        dev_reg_info["SP-SPINE-NAME"] = ec_message["device"].get("name")
        dev_reg_info["SP-NTP-SERVER"] = \
            ec_message["device"]["ntp"].get("server-address")

        dev_reg_info["SP-SNMP-SERVER"] = \
            ec_message["device"]["snmp"].get("server-address")
        dev_reg_info["SP-SNMP-COMMUNITY"] = \
            ec_message["device"]["snmp"].get("community")
        dev_reg_info["SP-LB-IF-ADDR"] = \
            ec_message["device"]["loopback-interface"].get("address")
        dev_reg_info["SP-LB-IF-PREFIX"] = \
            ec_message["device"]["loopback-interface"].get("prefix")
        dev_reg_info["SP-RP-SELF-ADDR"] = \
            ec_message["device"]["l2-vpn"]["pim"].get("self-rp-address")
        dev_reg_info["SP-RP-OTHER-ADDR"] = \
            ec_message["device"]["l2-vpn"]["pim"].get("other-rp-address")
        dev_reg_info["SP-MNG-IF-ADDR"] = \
            ec_message["device"]["management-interface"].get("address")
        dev_reg_info["SP-MNG-IF-PREFIX"] = \
            ec_message["device"]["management-interface"].get("prefix")
        if ec_message["device"].get("msdp") is not None:
            dev_reg_info["SP-MSDP-PEER-ADDR"] = \
                ec_message["device"]["msdp"]["peer"].get("address")
            dev_reg_info["SP-MSDP-LOCAL-ADDR"] = \
                ec_message["device"]["msdp"]["peer"].get("local-address")
        else:
            dev_reg_info["SP-MSDP-PEER-ADDR"] = None
            dev_reg_info["SP-MSDP-LOCAL-ADDR"] = None

        dev_reg_info["SP-DEVICE-COUNT"] = (
            self._set_conf_device_count(ec_message, dev_reg_info))

        for key in dev_reg_info.keys():
            if dev_reg_info[key] is None and \
                    key not in ["SP-RP-SELF-ADDR", "SP-RP-OTHER-ADDR",
                                "SP-MSDP-PEER-ADDR", "SP-MSDP-LOCAL-ADDR"]:
                is_variable_value = False
                break

        lag_ifs = []
        lag_mem_ifs = []
        if (ec_message["device"].get("internal-lag") is not None and
                len(ec_message["device"]["internal-lag"]) > 0):
            for lag in ec_message["device"]["internal-lag"]:
                if (lag.get("name") is None or
                        lag.get("address") is None or
                        (self._conversion_cidr2mask
                         (lag.get("prefix")) is None) or
                        lag.get("minimum-links") is None or
                        lag.get("link-speed") is None):
                    is_variable_value = False
                    break
                tmp = \
                    {"SP-INTERNAL-LAG-IF-NAME": lag["name"],
                     "SP-INTERNAL-LAG-IF-ADDR": lag["address"],
                     "SP-INTERNAL-LAG-IF-PREFIX": lag["prefix"],
                     "SP-INTERNAL-LAG-LINKS": lag["minimum-links"],
                     "SP-INTERNAL-LAG-SPEED": lag["link-speed"]}
                lag_ifs.append(tmp)

                if not lag.get("internal-interface") \
                        or len(lag["internal-interface"]) == 0:
                    is_variable_value = False

                for lag_mem in lag["internal-interface"]:
                    if lag_mem["name"] is None:
                        is_variable_value = False
                        break
                    tmp2 = \
                        {"SP-INTERNAL-IF-NAME": lag_mem["name"],
                         "SP-INTERNAL-LAG-IF-NAME": lag["name"]}
                    lag_mem_ifs.append(tmp2)

        if is_variable_value is False:
            return False

        self._set_xml_tag_variable(xml_obj,
                                   "host-name",
                                   dev_reg_info["SP-SPINE-NAME"],
                                   "configuration",
                                   "system")
        self._set_xml_tag_variable(xml_obj,
                                   "address",
                                   dev_reg_info["SP-NTP-SERVER"],
                                   "configuration",
                                   "system",
                                   "ntp",
                                   "server")
        self._set_xml_tag_variable(xml_obj,
                                   "source-address",
                                   dev_reg_info["SP-MNG-IF-ADDR"],
                                   "configuration",
                                   "system",
                                   "ntp")
        self._set_xml_tag_variable(xml_obj,
                                   "device-count",
                                   str(dev_reg_info["SP-DEVICE-COUNT"]),
                                   "configuration",
                                   "chassis",
                                   "aggregated-devices",
                                   "ethernet")

        if_node = self._find_xml_node(xml_obj, "configuration", "interfaces")

        for lag_mem_if in lag_mem_ifs:
            node_1 = self._set_xml_tag(if_node, "interface")
            self._set_xml_tag(node_1,
                              "interface_name",
                              None,
                              None,
                              lag_mem_if["SP-INTERNAL-IF-NAME"])
            node_2 = self._set_xml_tag(node_1, "ether-options")
            node_3 = self._set_xml_tag(node_2, "ieee-802.3ad")
            self._set_xml_tag(node_3,
                              "bundle",
                              None,
                              None,
                              lag_mem_if["SP-INTERNAL-LAG-IF-NAME"])

        for lag_if in lag_ifs:
            node_1 = self._set_xml_tag(if_node, "interface")
            self._set_xml_tag(node_1,
                              "interface_name",
                              None,
                              None,
                              lag_if["SP-INTERNAL-LAG-IF-NAME"])
            self._set_xml_tag(node_1, "mtu", None, None, "4110")
            node_2 = self._set_xml_tag(node_1, "aggregated-ether-options")
            self._set_xml_tag(node_2,
                              "minimum-links",
                              None,
                              None,
                              lag_if["SP-INTERNAL-LAG-LINKS"])
            self._set_xml_tag(node_2,
                              "link-speed",
                              None,
                              None,
                              lag_if["SP-INTERNAL-LAG-SPEED"])
            node_3 = self._set_xml_tag(node_2, "lacp")
            self._set_xml_tag(node_3, "active")
            self._set_xml_tag(node_3, "periodic", None, None, "fast")
            node_2 = self._set_xml_tag(node_1, "unit")
            self._set_xml_tag(node_2, "name", None, None, "0")
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
                              self._set_cidr_ip_address(
                                  lag_if["SP-INTERNAL-LAG-IF-ADDR"],
                                  lag_if["SP-INTERNAL-LAG-IF-PREFIX"]))
            node_4 = self._set_xml_tag(node_3, "mpls")

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
                          self._set_cidr_ip_address(
                              dev_reg_info["SP-LB-IF-ADDR"],
                              dev_reg_info["SP-LB-IF-PREFIX"]))
        if dev_reg_info["SP-RP-SELF-ADDR"] is not None:
            node_5 = self._set_xml_tag(node_4, "address")
            self._set_xml_tag(node_5,
                              "source",
                              None,
                              None,
                              self._set_cidr_ip_address(
                                  dev_reg_info["SP-RP-SELF-ADDR"],
                                  dev_reg_info["SP-LB-IF-PREFIX"]))
        node_1 = self._set_xml_tag(if_node, "interface")
        self._set_xml_tag(node_1, "interface_name", None, None, "vme")
        node_2 = self._set_xml_tag(node_1, "unit")
        self._set_xml_tag(node_2, "name", None, None, "0")
        node_3 = self._set_xml_tag(node_2, "family")
        node_4 = self._set_xml_tag(node_3, "inet")
        node_5 = self._set_xml_tag(node_4, "address")
        self._set_xml_tag(node_5,
                          "source",
                          None,
                          None,
                          self._set_cidr_ip_address(
                              dev_reg_info["SP-MNG-IF-ADDR"],
                              dev_reg_info["SP-MNG-IF-PREFIX"]))

        self._set_xml_tag_variable(xml_obj,
                                   "community",
                                   dev_reg_info["SP-SNMP-COMMUNITY"],
                                   "configuration",
                                   "snmp",
                                   "community")
        self._set_xml_tag_variable(xml_obj,
                                   "source-address",
                                   dev_reg_info["SP-MNG-IF-ADDR"],
                                   "configuration",
                                   "snmp",
                                   "trap-options")
        self._set_xml_tag_variable(xml_obj,
                                   "group-name",
                                   dev_reg_info["SP-SNMP-COMMUNITY"],
                                   "configuration",
                                   "snmp",
                                   "trap-group")
        self._set_xml_tag_variable(xml_obj,
                                   "target",
                                   dev_reg_info["SP-SNMP-SERVER"],
                                   "configuration",
                                   "snmp",
                                   "trap-group",
                                   "targets")
        self._set_xml_tag_variable(xml_obj,
                                   "router-id",
                                   dev_reg_info["SP-LB-IF-ADDR"],
                                   "configuration",
                                   "routing-options")

        if dev_reg_info["SP-MSDP-PEER-ADDR"] is not None \
           and dev_reg_info["SP-MSDP-LOCAL-ADDR"] is not None:
            self._set_xml_tag_variable(xml_obj,
                                       "address",
                                       dev_reg_info["SP-MSDP-PEER-ADDR"],
                                       "configuration",
                                       "protocols",
                                       "msdp",
                                       "peer")
            self._set_xml_tag_variable(xml_obj,
                                       "local-address",
                                       dev_reg_info["SP-MSDP-LOCAL-ADDR"],
                                       "configuration",
                                       "protocols",
                                       "msdp",
                                       "peer")
        else:
            node_1 = self._find_xml_node(xml_obj, "configuration", "protocols")
            node_2 = self._find_xml_node(node_1, "msdp")
            node_1.remove(node_2)

        if_node = self._find_xml_node(xml_obj,
                                      "configuration",
                                      "protocols",
                                      "ospf",
                                      "area")
        for lag_if in lag_ifs:
            node_1 = self._set_xml_tag(if_node, "interface")
            self._set_xml_tag(node_1,
                              "interface_name",
                              None,
                              None,
                              "%s.0" % (lag_if["SP-INTERNAL-LAG-IF-NAME"],))
            self._set_xml_tag(node_1, "metric", None, None, "100")
            self._set_xml_tag(node_1, "priority", None, None, "20")
        node_1 = self._set_xml_tag(if_node, "interface")
        self._set_xml_tag(node_1, "interface_name", None, None, "lo0.0")
        self._set_xml_tag(node_1, "passive")
        self._set_xml_tag(node_1, "metric", None, None, "10")
        node_1 = self._find_xml_node(xml_obj,
                                     "configuration",
                                     "protocols",
                                     "pim",
                                     "rp")
        if dev_reg_info["SP-RP-OTHER-ADDR"] is not None:
            node_2 = self._set_xml_tag(node_1, "static")
            node_3 = self._set_xml_tag(node_2, "address")
            self._set_xml_tag(node_3,
                              "addr",
                              None,
                              None,
                              dev_reg_info["SP-RP-OTHER-ADDR"])
            self._set_xml_tag(node_3, "version", None, None, "2")
        if dev_reg_info["SP-RP-SELF-ADDR"] is not None:
            node_2 = self._set_xml_tag(node_1, "local")
            self._set_xml_tag(node_2,
                              "address",
                              None,
                              None,
                              dev_reg_info["SP-RP-SELF-ADDR"])
        if_node = self._find_xml_node(xml_obj,
                                      "configuration",
                                      "class-of-service",
                                      "interfaces")

        if not lag_ifs:
            node_1 = self._find_xml_node(xml_obj,
                                         "configuration")
            if_node = self._find_xml_node(xml_obj,
                                          "configuration",
                                          "class-of-service")
            node_1.remove(if_node)

        for lag_if in lag_ifs:
            node_1 = self._set_xml_tag(if_node, "interface")
            self._set_xml_tag(node_1,
                              "interface_name",
                              None,
                              None,
                              lag_if["SP-INTERNAL-LAG-IF-NAME"])
            node_2 = self._set_xml_tag(node_1, "forwarding-class-set")
            self._set_xml_tag(node_2,
                              "class-name",
                              None,
                              None,
                              "fcs_unicast_af_and_be_class")
            node_3 = self._set_xml_tag(
                node_2, "output-traffic-control-profile")
            self._set_xml_tag(node_3,
                              "profile-name",
                              None,
                              None,
                              "tcp_unicast_af_and_be")
            node_2 = self._set_xml_tag(node_1, "forwarding-class-set")
            self._set_xml_tag(node_2,
                              "class-name",
                              None,
                              None,
                              "fcs_unicast_ef_class")
            node_3 = self._set_xml_tag(
                node_2, "output-traffic-control-profile")
            self._set_xml_tag(node_3,
                              "profile-name",
                              None,
                              None,
                              "tcp_unicast_ef")
            node_2 = self._set_xml_tag(node_1, "forwarding-class-set")
            self._set_xml_tag(node_2,
                              "class-name",
                              None,
                              None,
                              "fcs_multicast_class")
            node_3 = self._set_xml_tag(
                node_2, "output-traffic-control-profile")
            self._set_xml_tag(node_3,
                              "profile-name",
                              None,
                              None,
                              "tcp_multicast")
            node_2 = self._set_xml_tag(node_1, "unit")
            self._set_xml_tag(node_2, "interface_unit_number", None, None, "0")
            node_3 = self._set_xml_tag(node_2, "rewrite-rules")
            node_4 = self._set_xml_tag(node_3, "exp")
            node_5 = self._set_xml_tag(
                node_4, "rewrite-rule-name", None, None, "msf_mpls_exp_remark")
            node_2 = self._set_xml_tag(node_1, "classifiers")
            node_3 = self._set_xml_tag(node_2, "dscp")
            self._set_xml_tag(node_3,
                              "classifier-dscp-name",
                              None,
                              None,
                              "msf_unicast_dscp_classify")
            node_2 = self._set_xml_tag(node_1, "rewrite-rules")
            node_3 = self._set_xml_tag(node_2, "dscp")
            self._set_xml_tag(node_3,
                              "rewrite-rule-name",
                              None,
                              None,
                              "msf_dscp_remark")
        return True

    @decorater_log
    def _gen_leaf_variable_message(self,
                                   xml_obj,
                                   device_info,
                                   ec_message,
                                   operation):
        is_variable_value = True
        dev_reg_info = {}
        dev_reg_info["LF-LEAF-NAME"] = ec_message["device"].get("name")
        dev_reg_info["LF-NTP-SERVER"] = \
            ec_message["device"]["ntp"].get("server-address")

        dev_reg_info["LF-SNMP-SERVER"] = \
            ec_message["device"]["snmp"].get("server-address")
        dev_reg_info["LF-SNMP-COMMUNITY"] = \
            ec_message["device"]["snmp"].get("community")
        dev_reg_info["LF-LB-IF-ADDR"] = \
            ec_message["device"]["loopback-interface"].get("address")
        dev_reg_info["LF-LB-IF-PREFIX"] = \
            ec_message["device"]["loopback-interface"].get("prefix")
        dev_reg_info["LF-MNG-IF-ADDR"] = \
            ec_message["device"]["management-interface"].get("address")
        dev_reg_info["LF-MNG-IF-PREFIX"] = \
            ec_message["device"]["management-interface"].get("prefix")
        if ec_message["device"].get("l3-vpn") is not None:
            dev_reg_info["LF-AS-NUMBER"] = \
                ec_message["device"]["l3-vpn"]["as"].get("as-number")
            dev_reg_info["LF-BGP-COM-WILD"] = \
                ec_message["device"]["l3-vpn"]["bgp"].get("community-wildcard")
            dev_reg_info["LF-BGP-COMMUNITY"] = \
                ec_message["device"]["l3-vpn"]["bgp"].get("community")
        else:
            dev_reg_info["LF-AS-NUMBER"] = None
            dev_reg_info["LF-BGP-COM-WILD"] = None
            dev_reg_info["LF-BGP-COMMUNITY"] = None
        if ec_message["device"].get("l2-vpn") is not None:
            dev_reg_info["LF-RP-ADDR"] = \
                ec_message["device"]["l2-vpn"]["pim"].get("rp-address")
        else:
            dev_reg_info["LF-RP-ADDR"] = None

        dev_reg_info["LF-DEVICE-COUNT"] = (
            self._set_conf_device_count(ec_message, dev_reg_info))

        for key in dev_reg_info.keys():
            if dev_reg_info[key] is None \
                    and key not in ["LF-AS-NUMBER",
                                    "LF-BGP-COM-WILD",
                                    "LF-BGP-COMMUNITY",
                                    "LF-RP-ADDR"]:
                is_variable_value = False
                break

        is_l3_vpn = True
        if ec_message["device"].get("l3-vpn") is None:
            is_l3_vpn = False
        elif dev_reg_info["LF-AS-NUMBER"] is None:
            is_variable_value = False

        is_l2_vpn = True
        if ec_message["device"].get("l2-vpn") is None:
            is_l2_vpn = False
        elif dev_reg_info["LF-RP-ADDR"] is None:
            is_variable_value = False

        if is_l3_vpn:
            l3v_lbb_infos = []
            l3v = ec_message["device"]["l3-vpn"]["bgp"]

            if not l3v.get("neighbor") \
                    or len(l3v["neighbor"]) == 0:
                is_variable_value = False

            else:
                for nbrs in l3v["neighbor"]:
                    if nbrs.get("address") is None \
                            or l3v.get("community") is None \
                            or l3v.get("community-wildcard") is None:
                        is_variable_value = False
                        break
                    tmp = \
                        {"LF-RR-ADDR": nbrs["address"],
                         "LF-BGP-COMMUNITY": l3v["community"],
                         "LF-BGP-COM-WILD": l3v["community-wildcard"]}
                    l3v_lbb_infos.append(tmp)

        lag_ifs = []
        lag_mem_ifs = []

        if (ec_message["device"].get("internal-lag") is not None and
                len(ec_message["device"]["internal-lag"]) > 0):
            for lag in ec_message["device"]["internal-lag"]:
                if lag.get("name") is None \
                        or lag.get("address") is None \
                        or self._conversion_cidr2mask(lag.get("prefix")) is None \
                        or lag.get("minimum-links") is None \
                        or lag.get("link-speed") is None:
                    is_variable_value = False
                    break
                tmp = \
                    {"LF-INTERNAL-LAG-IF-NAME": lag["name"],
                     "LF-INTERNAL-LAG-IF-ADDR": lag["address"],
                     "LF-INTERNAL-LAG-IF-PREFIX": lag["prefix"],
                     "LF-INTERNAL-LAG-LINKS": lag["minimum-links"],
                     "LF-INTERNAL-LAG-SPEED": lag["link-speed"]}
                lag_ifs.append(tmp)

                if not lag.get("internal-interface") \
                        or len(lag["internal-interface"]) == 0:
                    is_variable_value = False

                else:
                    for lag_mem in lag["internal-interface"]:
                        if lag_mem.get("name") is None:
                            is_variable_value = False
                            break
                        tmp2 = \
                            {"LF-INTERNAL-IF-NAME": lag_mem["name"],
                             "LF-INTERNAL-LAG-IF-NAME": lag["name"]}
                        lag_mem_ifs.append(tmp2)

        if is_variable_value is False:
            return False

        self._set_xml_tag_variable(xml_obj,
                                   "host-name",
                                   dev_reg_info["LF-LEAF-NAME"],
                                   "configuration",
                                   "system")
        self._set_xml_tag_variable(xml_obj,
                                   "address",
                                   dev_reg_info["LF-NTP-SERVER"],
                                   "configuration",
                                   "system",
                                   "ntp",
                                   "server")
        self._set_xml_tag_variable(xml_obj,
                                   "source-address",
                                   dev_reg_info["LF-MNG-IF-ADDR"],
                                   "configuration",
                                   "system",
                                   "ntp")
        self._set_xml_tag_variable(xml_obj,
                                   "device-count",
                                   str(dev_reg_info["LF-DEVICE-COUNT"]),
                                   "configuration",
                                   "chassis",
                                   "aggregated-devices",
                                   "ethernet")

        if_node = self._find_xml_node(xml_obj, "configuration", "interfaces")

        for lag_mem_if in lag_mem_ifs:
            node_1 = self._set_xml_tag(if_node, "interface")
            self._set_xml_tag(node_1,
                              "interface_name",
                              None,
                              None,
                              lag_mem_if["LF-INTERNAL-IF-NAME"])
            node_2 = self._set_xml_tag(node_1, "ether-options")
            node_3 = self._set_xml_tag(node_2, "ieee-802.3ad")
            self._set_xml_tag(node_3,
                              "bundle",
                              None,
                              None,
                              lag_mem_if["LF-INTERNAL-LAG-IF-NAME"])

        for lag_if in lag_ifs:
            node_1 = self._set_xml_tag(if_node, "interface")
            self._set_xml_tag(node_1,
                              "interface_name",
                              None,
                              None,
                              lag_if["LF-INTERNAL-LAG-IF-NAME"])
            self._set_xml_tag(node_1, "mtu", None, None, "4110")
            node_2 = self._set_xml_tag(node_1, "aggregated-ether-options")
            self._set_xml_tag(node_2,
                              "minimum-links",
                              None,
                              None,
                              lag_if["LF-INTERNAL-LAG-LINKS"])
            self._set_xml_tag(node_2,
                              "link-speed",
                              None,
                              None,
                              lag_if["LF-INTERNAL-LAG-SPEED"])
            node_3 = self._set_xml_tag(node_2, "lacp")
            self._set_xml_tag(node_3, "active")
            self._set_xml_tag(node_3, "periodic", None, None, "fast")
            node_2 = self._set_xml_tag(node_1, "unit")
            self._set_xml_tag(node_2, "name", None, None, "0")
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
                              self._set_cidr_ip_address(
                                  lag_if["LF-INTERNAL-LAG-IF-ADDR"],
                                  lag_if["LF-INTERNAL-LAG-IF-PREFIX"]))
            if is_l3_vpn:
                node_4 = self._set_xml_tag(node_3, "mpls")

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
                          self._set_cidr_ip_address(
                              dev_reg_info["LF-LB-IF-ADDR"],
                              dev_reg_info["LF-LB-IF-PREFIX"]))

        node_1 = self._set_xml_tag(if_node, "interface")
        self._set_xml_tag(node_1, "interface_name", None, None, "vme")
        node_2 = self._set_xml_tag(node_1, "unit")
        self._set_xml_tag(node_2, "name", None, None, "0")
        node_3 = self._set_xml_tag(node_2, "family")
        node_4 = self._set_xml_tag(node_3, "inet")
        node_5 = self._set_xml_tag(node_4, "address")
        self._set_xml_tag(node_5,
                          "source",
                          None,
                          None,
                          self._set_cidr_ip_address(
                              dev_reg_info["LF-MNG-IF-ADDR"],
                              dev_reg_info["LF-MNG-IF-PREFIX"]))

        self._set_xml_tag_variable(xml_obj,
                                   "community",
                                   dev_reg_info["LF-SNMP-COMMUNITY"],
                                   "configuration",
                                   "snmp",
                                   "community")
        self._set_xml_tag_variable(xml_obj,
                                   "source-address",
                                   dev_reg_info["LF-MNG-IF-ADDR"],
                                   "configuration",
                                   "snmp",
                                   "trap-options")
        self._set_xml_tag_variable(xml_obj,
                                   "group-name",
                                   dev_reg_info["LF-SNMP-COMMUNITY"],
                                   "configuration",
                                   "snmp",
                                   "trap-group")
        self._set_xml_tag_variable(xml_obj,
                                   "target",
                                   dev_reg_info["LF-SNMP-SERVER"],
                                   "configuration",
                                   "snmp",
                                   "trap-group",
                                   "targets")
        self._set_xml_tag_variable(xml_obj,
                                   "router-id",
                                   dev_reg_info["LF-LB-IF-ADDR"],
                                   "configuration",
                                   "routing-options")
        if is_l3_vpn:
            self._set_xml_tag_variable(xml_obj,
                                       "autonomous-system",
                                       str(dev_reg_info["LF-AS-NUMBER"]),
                                       "configuration",
                                       "routing-options")
        else:
            node_1 = self._find_xml_node(xml_obj,
                                         "configuration", "routing-options")
            node_1.remove(node_1.find("autonomous-system"))

        node_1 = self._find_xml_node(xml_obj, "configuration", "protocols")
        if is_l3_vpn:
            node_2 = self._find_xml_node(node_1, "bgp", "group")
            self._set_xml_tag_variable(node_2,
                                       "local-address",
                                       dev_reg_info["LF-LB-IF-ADDR"])
            self._set_xml_tag_variable(node_2,
                                       "peer-as",
                                       str(dev_reg_info["LF-AS-NUMBER"]))
            for l3v_lbb in l3v_lbb_infos:
                node_3 = self._set_xml_tag(node_2, "neighbor")
                self._set_xml_tag(node_3,
                                  "address",
                                  None,
                                  None,
                                  l3v_lbb["LF-RR-ADDR"])
                node_4 = self._set_xml_tag(node_3, "import")
                self._set_xml_tag(node_4, "value", None, None, "VPN_import")
                node_4 = self._set_xml_tag(node_3, "export")
                self._set_xml_tag(node_4, "value", None, None, "VPN_export")
        else:
            node_1.remove(node_1.find("mpls"))
            node_1.remove(node_1.find("bgp"))
            node_1.remove(node_1.find("vrrp"))
            node_1.remove(node_1.find("ldp"))

        if_node = self._find_xml_node(xml_obj,
                                      "configuration",
                                      "protocols",
                                      "ospf",
                                      "area")
        for lag_if in lag_ifs:
            node_1 = self._set_xml_tag(if_node, "interface")
            self._set_xml_tag(node_1,
                              "interface_name",
                              None,
                              None,
                              lag_if["LF-INTERNAL-LAG-IF-NAME"] + ".0")
            self._set_xml_tag(node_1, "metric", None, None, "100")
            self._set_xml_tag(node_1, "priority", None, None, "10")
        node_1 = self._set_xml_tag(if_node, "interface")
        self._set_xml_tag(node_1, "interface_name", None, None, "lo0.0")
        self._set_xml_tag(node_1, "passive")
        self._set_xml_tag(node_1, "metric", None, None, "10")

        if is_l2_vpn:
            self._set_xml_tag_variable(xml_obj,
                                       "addr",
                                       dev_reg_info["LF-RP-ADDR"],
                                       "configuration",
                                       "protocols",
                                       "pim",
                                       "rp",
                                       "static",
                                       "address")
        else:
            node_1 = self._find_xml_node(xml_obj,
                                         "configuration",
                                         "protocols")
            node_1.remove(node_1.find("pim"))

        if is_l3_vpn:
            node_1 = self._find_xml_node(
                xml_obj, "configuration", "policy-options")
            for node in node_1.findall("community"):
                if node.find("community_name").text == "MSF_community":
                    self._set_xml_tag_variable(
                        node,
                        "value",
                        dev_reg_info["LF-BGP-COM-WILD"],
                        "members")
                elif node.find("community_name").text == "MSF_belonging_side":
                    self._set_xml_tag_variable(
                        node,
                        "value",
                        dev_reg_info["LF-BGP-COMMUNITY"],
                        "members")
                elif node.find("community_name").text == "OSPF_router_id":
                    self._set_xml_tag_variable(
                        node,
                        "value",
                        "0x0107:%s:0" % (dev_reg_info["LF-LB-IF-ADDR"],),
                        "members")
        else:
            node_1 = self._find_xml_node(xml_obj, "configuration")
            node_1.remove(self._find_xml_node(node_1, "policy-options"))

        if_node = self._find_xml_node(xml_obj,
                                      "configuration",
                                      "class-of-service",
                                      "interfaces")
        if not lag_ifs:
            node_1 = self._find_xml_node(xml_obj,
                                         "configuration")
            if_node = self._find_xml_node(xml_obj,
                                          "configuration",
                                          "class-of-service")
            node_1.remove(if_node)

        for lag_if in lag_ifs:
            node_1 = self._set_xml_tag(if_node, "interface")
            self._set_xml_tag(node_1,
                              "interface_name",
                              None,
                              None,
                              lag_if["LF-INTERNAL-LAG-IF-NAME"])
            node_2 = self._set_xml_tag(node_1, "forwarding-class-set")
            self._set_xml_tag(node_2,
                              "class-name",
                              None,
                              None,
                              "fcs_unicast_af_and_be_class")
            node_3 = self._set_xml_tag(
                node_2, "output-traffic-control-profile")
            self._set_xml_tag(node_3,
                              "profile-name",
                              None,
                              None,
                              "tcp_unicast_af_and_be")
            node_2 = self._set_xml_tag(node_1, "forwarding-class-set")
            self._set_xml_tag(node_2,
                              "class-name",
                              None,
                              None,
                              "fcs_unicast_ef_class")
            node_3 = self._set_xml_tag(
                node_2, "output-traffic-control-profile")
            self._set_xml_tag(node_3,
                              "profile-name",
                              None,
                              None,
                              "tcp_unicast_ef")
            node_2 = self._set_xml_tag(node_1, "forwarding-class-set")
            self._set_xml_tag(node_2,
                              "class-name",
                              None,
                              None,
                              "fcs_multicast_class")
            node_3 = self._set_xml_tag(
                node_2, "output-traffic-control-profile")
            self._set_xml_tag(node_3,
                              "profile-name",
                              None,
                              None,
                              "tcp_multicast")
            node_2 = self._set_xml_tag(node_1, "unit")
            self._set_xml_tag(node_2, "interface_unit_number", None, None, "0")
            node_3 = self._set_xml_tag(node_2, "rewrite-rules")
            node_4 = self._set_xml_tag(node_3, "exp")
            node_5 = self._set_xml_tag(
                node_4, "rewrite-rule-name", None, None, "msf_mpls_exp_remark")
            node_2 = self._set_xml_tag(node_1, "classifiers")
            node_3 = self._set_xml_tag(node_2, "dscp")
            self._set_xml_tag(node_3,
                              "classifier-dscp-name",
                              None,
                              None,
                              "msf_unicast_dscp_classify")
            node_2 = self._set_xml_tag(node_1, "rewrite-rules")
            node_3 = self._set_xml_tag(node_2, "dscp")
            self._set_xml_tag(node_3,
                              "rewrite-rule-name",
                              None,
                              None,
                              "msf_dscp_remark")

        if is_l2_vpn is False:
            node_1 = self._find_xml_node(xml_obj, "configuration")
            node_1.remove(node_1.find("switch-options"))

        return True

    @staticmethod
    @decorater_log
    def _get_l2_info_from_ec(device_info, if_name, vlan_id):
        return_val = None
        tmp = {"port_mode": None, "vni": None, "multicast_group": None}
        for cp in device_info["cp"]:
            if cp["vlan"].get("port_mode") is None \
                    or cp["vxlan"].get("vni") is None \
                    or cp["vxlan"].get("mc_group") is None:
                return_val = None
                break
            if cp["if_name"] == if_name and \
                    cp["vlan"]["vlan_id"] == vlan_id:
                tmp["port-mode"] = cp["vlan"]["port_mode"].lower()
                tmp["vni"] = cp["vxlan"]["vni"]
                tmp["multicast-group"] = cp["vxlan"]["mc_group"]
                return_val = tmp
                break
        return return_val

    @decorater_log
    def _gen_l2_slice_variable_message(self,
                                       xml_obj,
                                       device_info,
                                       ec_message,
                                       operation):

        is_variable_value = True
        ec_mes_dev = None
        cp_ifs = []
        if operation == self.__DELETE:
            if device_info.get("cp") is None:
                return False

            dev = ec_message["device-leaf"]["name"]
            for cp in device_info["cp"]:
                if cp["device_name"] == dev:
                    ec_mes_dev = dev
                if ec_mes_dev is None:
                    return False

        if ec_message["device-leaf"].get("cp") is None \
                or len(ec_message["device-leaf"]["cp"]) == 0:
            return False

        for cp in ec_message["device-leaf"]["cp"]:
            if operation == self.__DELETE:
                if cp["name"] is None \
                        or cp["operation"] is None \
                        or cp["vlan-id"] is None:
                    is_variable_value = False
                    break
                tmp_db = self._get_l2_info_from_ec(device_info,
                                                   cp["name"],
                                                   cp["vlan-id"])
                if tmp_db is None:
                    is_variable_value = False
                    break
                tmp = \
                    {"L2-CE-IF-NAME": cp["name"],
                     "L2-VLAN-ID": cp["vlan-id"],
                     "L2-PORT-MODE": tmp_db["port-mode"],
                     "L2-VNI": tmp_db["vni"],
                     "L2-MC-GROUP": tmp_db["multicast-group"]}
            else:
                if cp.get("name") is None \
                        or cp.get("vlan-id") is None \
                        or cp.get("port-mode") is None \
                        or cp.get("vni") is None \
                        or cp.get("multicast-group") is None:
                    is_variable_value = False
                    break
                tmp = \
                    {"L2-CE-IF-NAME":  cp["name"],
                     "L2-VLAN-ID": cp["vlan-id"],
                     "L2-PORT-MODE": cp["port-mode"],
                     "L2-VNI":  cp["vni"],
                     "L2-MC-GROUP": cp["multicast-group"]}
            cp_ifs.append(tmp)

        if is_variable_value is False:
            return False

        if operation == self.__DELETE:
            vlan_count_db = {}
            vlan_count_cp = {}
            t_list = []
            vlan_id_db = {}
            vlan_id_cp = {}
            v_list = []
            for cp in device_info["cp"]:
                if vlan_count_db.get(cp["if_name"]):
                    vlan_count_db[cp["if_name"]] += 1
                else:
                    vlan_count_db[cp["if_name"]] = 1
                if vlan_id_db.get(cp["vlan"]["vlan_id"]):
                    vlan_id_db[cp["vlan"]["vlan_id"]] += 1
                else:
                    vlan_id_db[cp["vlan"]["vlan_id"]] = 1
            for cp_if in cp_ifs:
                if vlan_count_cp.get(cp_if["L2-CE-IF-NAME"]):
                    vlan_count_cp[cp_if["L2-CE-IF-NAME"]] += 1
                else:
                    vlan_count_cp[cp_if["L2-CE-IF-NAME"]] = 1
                if vlan_id_cp.get(cp_if["L2-VLAN-ID"]):
                    vlan_id_cp[cp_if["L2-VLAN-ID"]] += 1
                else:
                    vlan_id_cp[cp_if["L2-VLAN-ID"]] = 1
            for if_name, v_count in vlan_count_cp.items():
                if v_count == vlan_count_db.get(if_name, -1):
                    t_list.append(if_name)
            for vlan_id, v_count in vlan_id_cp.items():
                if v_count == vlan_id_db.get(vlan_id, -1):
                    v_list.append(vlan_id)

            return self._gen_l2_slice_del_variable_message(xml_obj,
                                                           cp_ifs,
                                                           all_vlan_del=t_list,
                                                           del_vlans=v_list)

        node_1 = self._find_xml_node(xml_obj, "configuration", "interfaces")
        if_name_list = []
        for cp_if in cp_ifs:
            if cp_if.get("L2-CE-IF-NAME") in if_name_list:
                if_name = cp_if.get("L2-CE-IF-NAME")
                for node_2 in node_1.findall("interface"):
                    node_3 = node_2.find("name")
                    if if_name == node_3.text if node_3 is not None else None:
                        node_3 = self._find_xml_node(node_2,
                                                     "unit",
                                                     "family",
                                                     "ethernet-switching",
                                                     "vlan")
                        self._set_xml_tag(node_3,
                                          "members",
                                          None,
                                          None,
                                          cp_if["L2-VLAN-ID"])
                        break
                continue
            if_name_list.append(cp_if["L2-CE-IF-NAME"])
            node_2 = self._set_xml_tag(node_1, "interface")
            self._set_xml_tag(
                node_2, "name", None, None, cp_if["L2-CE-IF-NAME"])
            mtu_val = None
            if cp_if["L2-PORT-MODE"] == self.__PORT_MODE_ACCESS:
                mtu_val = "4110"
            elif cp_if["L2-PORT-MODE"] == self.__PORT_MODE_TRUNK:
                mtu_val = "4114"
            self._set_ope_delete_tag(node_2, "mtu", operation, mtu_val)
            node_3 = self._set_ope_delete_tag(node_2, "unit", operation)
            self._set_xml_tag(node_3, "name", None, None, "0")
            node_4 = self._set_xml_tag(node_3, "family")
            node_5 = self._set_xml_tag(node_4, "ethernet-switching")
            node_6 = self._set_ope_delete_tag(node_5, "vlan", operation)
            self._set_xml_tag(
                node_6, "members", None, None, cp_if["L2-VLAN-ID"])
            self._set_xml_tag(
                node_5, "interface-mode", None, None, cp_if["L2-PORT-MODE"])
            node_6 = self._set_xml_tag(node_5, "filter")
            self._set_xml_tag(
                node_6, "input", None, None, "input_l2_ce_filter")
        node_1 = self._find_xml_node(xml_obj, "configuration", "vlans")
        for cp_if in cp_ifs:
            node_2 = self._set_ope_delete_tag(node_1, "vlan", operation)
            self._set_xml_tag(
                node_2, "name", None, None, "vlan" + str(cp_if["L2-VLAN-ID"]))
            node_3 = self._set_xml_tag(node_2, "vxlan")
            self._set_xml_tag(
                node_3, "vni", None, None, cp_if["L2-VNI"])
            self._set_xml_tag(
                node_3, "multicast-group", None, None, cp_if["L2-MC-GROUP"])
            self._set_xml_tag(
                node_2, "vlan-id", None, None, cp_if["L2-VLAN-ID"])

        node_1 = self._find_xml_node(
            xml_obj, "configuration", "class-of-service", "interfaces")

        if not cp_ifs:
            node_1 = self._find_xml_node(xml_obj,
                                         "configuration")
            if_node = self._find_xml_node(xml_obj,
                                          "configuration",
                                          "class-of-service")
            node_1.remove(if_node)

        for cp_if in cp_ifs:
            node_2 = self._set_ope_delete_tag(node_1, "interface", operation)
            self._set_xml_tag(
                node_2, "interface_name", None, None, cp_if["L2-CE-IF-NAME"])

            node_3 = self._set_xml_tag(node_2, "forwarding-class-set")
            self._set_xml_tag(node_3,
                              "class-name",
                              None,
                              None,
                              "fcs_unicast_af_and_be_class")
            node_4 = self._set_xml_tag(
                node_3, "output-traffic-control-profile")
            self._set_xml_tag(
                node_4, "profile-name", None, None, "tcp_unicast_af_and_be")

            node_3 = self._set_xml_tag(node_2, "forwarding-class-set")
            self._set_xml_tag(
                node_3, "class-name", None, None, "fcs_unicast_ef_class")
            node_4 = self._set_xml_tag(
                node_3, "output-traffic-control-profile")
            self._set_xml_tag(
                node_4, "profile-name", None, None, "tcp_unicast_ef")

            node_3 = self._set_xml_tag(node_2, "forwarding-class-set")
            self._set_xml_tag(
                node_3, "class-name", None, None, "fcs_multicast_class")
            node_4 = self._set_xml_tag(
                node_3, "output-traffic-control-profile")
            self._set_xml_tag(
                node_4, "profile-name", None, None, "tcp_multicast")

            if cp_if["L2-PORT-MODE"] == self.__PORT_MODE_TRUNK:
                node_3 = self._set_xml_tag(node_2, "unit")
                self._set_xml_tag(
                    node_3, "interface_unit_number", None, None, "0")
                node_4 = self._set_xml_tag(node_3, "classifiers")
                node_5 = self._set_xml_tag(node_4, "ieee-802.1")
                self._set_xml_tag(node_5,
                                  "classifier-name",
                                  None,
                                  None,
                                  "ce_l2_cos_classify")
                node_4 = self._set_xml_tag(node_3, "rewrite-rules")
                node_5 = self._set_xml_tag(node_4, "ieee-802.1")
                self._set_xml_tag(
                    node_5,
                    "rewrite-rule-name",
                    None,
                    None,
                    "ce_l2_cos_remark")

        return True

    @decorater_log
    def _gen_l2_slice_del_variable_message(self,
                                           xml_obj,
                                           cp_ifs,
                                           all_vlan_del=None,
                                           del_vlans=None):
        operation = self.__DELETE
        if all_vlan_del is None:
            all_vlan_del = []
        if del_vlans is None:
            del_vlans = []
        cos_ifs = tuple(all_vlan_del)

        node_1 = self._find_xml_node(xml_obj, "configuration", "interfaces")
        if_name_list = []
        for cp_if in cp_ifs:
            if cp_if.get("L2-CE-IF-NAME") in if_name_list:
                if_name = cp_if.get("L2-CE-IF-NAME")
                for node_2 in node_1.findall("interface"):
                    node_3 = node_2.find("name")
                    if if_name == node_3.text if node_3 is not None else None:
                        node_3 = self._find_xml_node(node_2,
                                                     "unit",
                                                     "family",
                                                     "ethernet-switching",
                                                     "vlan")
                        if node_3 is not None:
                            self._set_xml_tag(node_3,
                                              "members",
                                              None,
                                              None,
                                              cp_if["L2-VLAN-ID"])
                        break
                continue
            if_name_list.append(cp_if["L2-CE-IF-NAME"])
            node_2 = self._set_xml_tag(node_1, "interface")
            self._set_xml_tag(
                node_2, "name", None, None, cp_if["L2-CE-IF-NAME"])
            if cp_if["L2-CE-IF-NAME"] in all_vlan_del:
                if cp_if["L2-PORT-MODE"] is not None:
                    self._set_ope_delete_tag(node_2, "mtu", operation)
                node_3 = self._set_ope_delete_tag(node_2, "unit", operation)
                self._set_xml_tag(node_3, "name", None, None, "0")
                continue
            node_3 = self._set_xml_tag(node_2, "unit")
            self._set_xml_tag(node_3, "name", None, None, "0")
            node_4 = self._set_xml_tag(node_3, "family")
            node_5 = self._set_xml_tag(node_4, "ethernet-switching")
            node_6 = self._set_xml_tag(node_5, "vlan")
            self._set_ope_delete_tag(
                node_6, "members", operation, cp_if["L2-VLAN-ID"])
        if len(del_vlans) == 0:
            node_1 = self._find_xml_node(xml_obj, "configuration")
            node_2 = self._find_xml_node(xml_obj, "configuration", "vlans")
            node_1.remove(node_2)
        else:
            node_1 = self._find_xml_node(xml_obj, "configuration", "vlans")
        for vlan_id in del_vlans:
            node_2 = self._set_ope_delete_tag(node_1, "vlan", operation)
            self._set_xml_tag(
                node_2, "name", None, None, "vlan" + str(vlan_id))

        node_1 = self._find_xml_node(
            xml_obj, "configuration", "class-of-service", "interfaces")

        if not cos_ifs:
            node_1 = self._find_xml_node(xml_obj,
                                         "configuration")
            if_node = self._find_xml_node(xml_obj,
                                          "configuration",
                                          "class-of-service")
            node_1.remove(if_node)

        for if_name in cos_ifs:
            node_2 = self._set_ope_delete_tag(node_1, "interface", operation)
            self._set_xml_tag(
                node_2, "interface_name", None, None, if_name)

        return True

    @decorater_log
    def _gen_l3_slice_variable_message(self,
                                       xml_obj,
                                       device_info,
                                       ec_message,
                                       operation):

        is_bgp = False
        is_static = False
        is_ospf = False
        is_cp_delete = False
        del_prefix_list={}

        is_variable_value = True
        ec_mes_dev = None
        cp_ifs = []
        if operation == self.__DELETE:
            if ec_message["device-leaf"].get("name") is None:
                return False

            dev = ec_message["device-leaf"]["name"]
            if dev == device_info["device"]["device_name"]:
                ec_mes_dev = dev
            if ec_mes_dev is None:
                return False

        if ec_message["device-leaf"].get("cp") is None \
                or len(ec_message["device-leaf"]["cp"]) == 0:
            return False

        del_cp_val = 0
        tmp_del_prefix_list={}
        for cp in ec_message["device-leaf"]["cp"]:
            is_cp_del = bool(cp.get("operation") == self.__DELETE)
            if operation == self.__DELETE:

                if cp.get("name") is None \
                        or cp.get("vlan-id") is None:
                    is_variable_value = False
                    break


                del_cp_val += 1 if is_cp_del else 0
                if del_cp_val:
                    is_cp_delete = True

                tmp_db = None
                for db_val in device_info["cp"]:
                    if db_val["if_name"] == cp["name"] and \
                            db_val["vlan"]["vlan_id"] == cp["vlan-id"]:

                        if db_val["ce_ipv6"].get("address") is not None \
                                and db_val["ce_ipv6"].get("prefix") is None \
                                or db_val["ce_ipv4"].get("address") is not None \
                                and db_val["ce_ipv4"].get("prefix") is None:
                            is_variable_value = False
                            break

                        tmp_db = {
                            "address6": db_val["ce_ipv6"].get("address"),
                            "prefix6": db_val["ce_ipv6"].get("prefix"),
                            "address": db_val["ce_ipv4"].get("address"),
                            "prefix": db_val["ce_ipv4"].get("prefix"),
                            "mtu": db_val.get("mtu_size"),
                            "ospf_metric": db_val.get("metric"),
                            "bgp": db_val["protocol_flags"].get("bgp"),
                            "ospf": db_val["protocol_flags"].get("ospf"),
                            "static": db_val["protocol_flags"].get("static"),
                            "vrrp": db_val["protocol_flags"].get("vrrp")}
                        break
                if tmp_db is None:
                    is_variable_value = False
                    break
                tmp = \
                    {"L3-CE-IF-OPERATION": cp.get("operation"),
                     "L3-CE-IF-CPDEL": is_cp_del,
                     "L3-CE-IF-NAME":  cp["name"],
                     "L3-CE-IF-VLAN": cp["vlan-id"],
                     "L3-CE-IF-ADDR6": tmp_db["address6"],
                     "L3-CE-IF-PREFIX6": tmp_db["prefix6"],
                     "L3-CE-IF-ADDR": tmp_db["address"],
                     "L3-CE-IF-PREFIX":  tmp_db["prefix"],
                     "L3-CE-IF-MTU":  tmp_db["mtu"],
                     "L3-CE-IF-BGPFLAG":  tmp_db["bgp"],
                     "L3-CE-IF-OSPFFLAG":  tmp_db["ospf"],
                     "L3-CE-IF-STATICFLAG":  tmp_db["static"],
                     "L3-CE-IF-VRRPFLAG":  tmp_db["vrrp"]}

                if "ospf" in cp or is_cp_del:
                    is_ospf = True
                    tmp["L3-OSPF-CP-METRIC"] = tmp_db.get("ospf_metric")

                if "vrrp" in cp:
                    if tmp["L3-CE-IF-VRRPFLAG"] is True:
                        tmp_db = None
                        for db_val in device_info["vrrp_detail"]:
                            if db_val["if_name"] == cp["name"] and \
                                    db_val["vlan_id"] == cp["vlan-id"]:
                                if db_val.get("gropu_id") is None \
                                        or db_val.get("priority") is None:
                                    is_variable_value = False
                                    break

                                tmp_db = {
                                    "group-id": db_val["gropu_id"],
                                    "virtual-address":
                                    db_val["virtual"].get("ipv4_address"),
                                    "virtual-address6":
                                    db_val["virtual"].get("ipv6_address"),
                                    "priority": db_val["priority"],
                                    "track_if": db_val["track_if_name"]}
                                break
                        if tmp_db is None:
                            is_variable_value = False
                            break

                        tmp_list = []
                        for track in db_val["track_if_name"]:
                            tmp_list.append(
                                {"L3-VRRP-VIRT-IF": track})

                        tmp["VRRP"] = {"L3-VRRP-GROUP-ID":
                                       tmp_db["group-id"],
                                       "L3-VRRP-VIRT-ADDR6":
                                       tmp_db["virtual-address6"],
                                       "L3-VRRP-VIRT-ADDR":
                                       tmp_db["virtual-address"],
                                       "L3-VRRP-VIRT-PRI":
                                       tmp_db["priority"],
                                       "track": tmp_list}

                if "bgp" in cp or is_cp_del:
                    if tmp["L3-CE-IF-BGPFLAG"] is True:
                        is_bgp = True
                        tmp_db = None
                        for db_val in device_info["bgp_detail"]:
                            if db_val["if_name"] == cp["name"] and \
                                    db_val["vlan_id"] == cp["vlan-id"]:

                                if db_val.get("as_number") is None:
                                    is_variable_value = False
                                    break
                                if (db_val["local"].
                                        get("ipv4_address") is not None and
                                        db_val["remote"].
                                        get("ipv4_address") is None or
                                        db_val["local"].
                                        get("ipv6_address") is not None and
                                        db_val["remote"].
                                        get("ipv6_address") is None):
                                    is_variable_value = False
                                    break

                                tmp_db = {"remote-as-number":
                                          db_val["as_number"],
                                          "local-address":
                                          db_val["local"].get("ipv4_address"),
                                          "remote-address":
                                          db_val["remote"].get("ipv4_address"),
                                          "local-address6":
                                          db_val["local"].get("ipv6_address"),
                                          "remote-address6":
                                          db_val["remote"].get("ipv6_address")}
                                break

                        if tmp_db is None:
                            is_variable_value = False
                            break
                        else:
                            tmp["BGP"] = {"L3-BGP-PEER-AS":
                                          tmp_db["remote-as-number"],
                                          "L3-BGP-RADD":
                                          tmp_db["remote-address"],
                                          "L3-BGP-LADD":
                                          tmp_db["local-address"],
                                          "L3-BGP-RADD6":
                                          tmp_db["remote-address6"],
                                          "L3-BGP-LADD6":
                                          tmp_db["local-address6"]}

                if is_cp_del and tmp.get("L3-CE-IF-STATICFLAG"):
                    tmp_db = None
                    tmp_list = []
                    tmp_list2 = []
                    for db_val in device_info["static_detail"]:
                        if db_val["if_name"] == cp["name"] and \
                                db_val["vlan_id"] == cp["vlan-id"]:

                            if (db_val.get("ipv4") and
                                    db_val["ipv4"].get("address")):
                                tmp_list.append(
                                    {"L3-STATIC-ROUTE-ADD":
                                     db_val["ipv4"].get("address"),
                                     "L3-STATIC-ROUTE-PREFIX":
                                     db_val["ipv4"].get("prefix"),
                                     "L3-STATIC-ROUTE-NEXT":
                                     db_val["ipv4"].get("nexthop")})
                                tmpname=self._set_cidr_ip_address(db_val["ipv4"].get("address"),db_val["ipv4"].get("prefix"))
                                if tmp_del_prefix_list.get(tmpname) is None:
                                    tmp_del_prefix_list.update({tmpname:1})
                                else:
                                    tmp_del_prefix_list.update({tmpname:tmp_del_prefix_list.get(tmpname)+1})
                            if (db_val.get("ipv6") and
                                    db_val["ipv6"].get("address")):
                                tmp_list2.append(
                                    {"L3-STATIC-ROUTE-ADD6":
                                     db_val["ipv6"].get("address"),
                                     "L3-STATIC-ROUTE-PREFIX6":
                                     db_val["ipv6"].get("prefix"),
                                     "L3-STATIC-ROUTE-NEXT6":
                                     db_val["ipv6"].get("nexthop")})
                                tmpname=self._set_cidr_ip_address(db_val["ipv6"].get("address"),db_val["ipv6"].get("prefix"))
                                if tmp_del_prefix_list.get(tmpname) is None:
                                    tmp_del_prefix_list.update({tmpname:1})
                                else:
                                    tmp_del_prefix_list.update({tmpname:tmp_del_prefix_list.get(tmpname)+1})
                    if len(tmp_list) + len(tmp_list2) > 0:
                        is_static = True
                        tmp["STATIC"] = {
                            "route": tmp_list, "route6": tmp_list2}
            else:
                if cp.get("name") is None \
                        or cp.get("vlan-id") is None:
                    is_variable_value = False
                    break
                if cp["ce-interface"].get("address6") is not None \
                        and cp["ce-interface"].get("prefix6") is None \
                        or cp["ce-interface"].get("address") is not None \
                        and cp["ce-interface"].get("prefix") is None:
                    is_variable_value = False
                    break
                tmp = \
                    {"L3-CE-IF-NAME":  cp["name"],
                     "L3-CE-IF-VLAN": cp["vlan-id"],
                     "L3-CE-IF-ADDR6": cp["ce-interface"].get("address6"),
                     "L3-CE-IF-PREFIX6": cp["ce-interface"].get("prefix6"),
                     "L3-CE-IF-ADDR": cp["ce-interface"].get("address"),
                     "L3-CE-IF-PREFIX":  cp["ce-interface"].get("prefix"),
                     "L3-CE-IF-MTU":  cp["ce-interface"].get("mtu")}
                if "vrrp" in cp:
                    tmp_list = []
                    if cp["vrrp"].get("track") is not None:
                        for track in cp["vrrp"]["track"]["interface"]:
                            tmp_list.append(
                                {"L3-VRRP-VIRT-IF": track["name"]})
                    if cp["vrrp"].get("group-id") is None \
                            or cp["vrrp"].get("priority") is None:
                        is_variable_value = False
                        break
                    tmp["VRRP"] = {"L3-VRRP-GROUP-ID":
                                   cp["vrrp"].get("group-id"),
                                   "L3-VRRP-VIRT-ADDR6":
                                   cp["vrrp"].get("virtual-address6"),
                                   "L3-VRRP-VIRT-ADDR":
                                   cp["vrrp"].get("virtual-address"),
                                   "L3-VRRP-VIRT-PRI":
                                   cp["vrrp"].get("priority"),
                                   "track": tmp_list}
                if "bgp" in cp:
                    is_bgp = True
                    if cp["bgp"].get("remote-as-number") is None:
                        is_variable_value = False
                        break
                    if cp["bgp"].get("local-address") is not None \
                            and cp["bgp"].get("remote-address") is None \
                            or cp["bgp"].get("local-address6") is not None \
                            and cp["bgp"].get("remote-address6") is None:
                        is_variable_value = False
                        break
                    tmp["BGP"] = {"L3-BGP-PEER-AS":
                                  cp["bgp"].get("remote-as-number"),
                                  "L3-BGP-MASTER":
                                  cp["bgp"].get("master"),
                                  "L3-BGP-RADD":
                                  cp["bgp"].get("remote-address"),
                                  "L3-BGP-LADD":
                                  cp["bgp"].get("local-address"),
                                  "L3-BGP-RADD6":
                                  cp["bgp"].get("remote-address6"),
                                  "L3-BGP-LADD6":
                                  cp["bgp"].get("local-address6")}

                if "ospf" in cp:
                    if cp["ospf"].get("metric") is None:
                        is_variable_value = False
                    else:
                        is_ospf = True
                        tmp["L3-OSPF-CP-METRIC"] = cp["ospf"]["metric"]

            if "static" in cp and not is_cp_del:
                is_static = True
                tmp_list = []
                if cp["static"].get("route") is not None:
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
                        tmpname=self._set_cidr_ip_address(route.get("address"),route.get("prefix"))
                        if tmp_del_prefix_list.get(tmpname) is None:
                            tmp_del_prefix_list.update({tmpname:1})
                        else:
                            tmp_del_prefix_list.update({tmpname:tmp_del_prefix_list.get(tmpname)+1})
                tmp_list2 = []
                if cp["static"].get("route6") is not None:
                    for route in cp["static"]["route6"]:
                        if route.get("address") is None \
                                or route.get("prefix") is None \
                                or route.get("nexthop") is None:
                            is_variable_value = False
                            break
                        tmp_list2.append(
                            {"L3-STATIC-ROUTE-ADD6": route["address"],
                             "L3-STATIC-ROUTE-PREFIX6": route["prefix"],
                             "L3-STATIC-ROUTE-NEXT6": route["nexthop"]})
                        tmpname=self._set_cidr_ip_address(route.get("address"),route.get("prefix"))
                        if tmp_del_prefix_list.get(tmpname) is None:
                            tmp_del_prefix_list.update({tmpname:1})
                        else:
                            tmp_del_prefix_list.update({tmpname:tmp_del_prefix_list.get(tmpname)+1})
                tmp["STATIC"] = {"route": tmp_list, "route6": tmp_list2}

            cp_ifs.append(tmp)

        if operation == self.__DELETE:
            if len(device_info["vrf_detail"]) < 1:
                is_variable_value = False
            else:
                db_vrf = None
                vrf_dtl = device_info["vrf_detail"] if len(cp_ifs) > 0 else []
                for vrfs in vrf_dtl:
                    if (vrfs.get("if_name") ==
                            cp_ifs[0].get("L3-CE-IF-NAME") and
                            vrfs.get("vlan_id") ==
                            cp_ifs[0].get("L3-CE-IF-VLAN")):
                        db_vrf = vrfs
                        break
                if db_vrf is None \
                        or db_vrf.get("vrf_name") is None \
                        or db_vrf.get("rt") is None \
                        or db_vrf.get("rd") is None \
                        or db_vrf.get("router_id") is None:
                    is_variable_value = False
                else:
                    vrf_dtl_info = {}
                    vrf_dtl_info["L3-VRF-NAME"] = db_vrf["vrf_name"]
                    vrf_dtl_info["L3-VRF-RT"] = db_vrf["rt"]
                    vrf_dtl_info["L3-VRF-RD"] = db_vrf["rd"]
                    vrf_dtl_info["L3-VRF-ROUTER-ID"] = db_vrf["router_id"]
        else:
            tmp_ec = ec_message["device-leaf"]["vrf"]
            if tmp_ec.get("vrf-name") is None \
                    or tmp_ec.get("rt") is None \
                    or tmp_ec.get("rd") is None \
                    or tmp_ec.get("router-id") is None:
                is_variable_value = False
            else:
                vrf_dtl_info = {}
                vrf_dtl_info["L3-VRF-NAME"] = tmp_ec["vrf-name"]
                vrf_dtl_info["L3-VRF-RT"] = tmp_ec["rt"]
                vrf_dtl_info["L3-VRF-RD"] = tmp_ec["rd"]
                vrf_dtl_info["L3-VRF-ROUTER-ID"] = tmp_ec["router-id"]

        if is_variable_value is False:
            return False

        cp_count_slice = 0
        for cp in device_info["cp"]:
            if cp["slice_name"] == ec_message["device-leaf"]["slice_name"]:
                cp_count_slice += 1

        is_all_del = bool(del_cp_val == cp_count_slice)

        if operation == self.__DELETE:
            vlan_count_db = {}
            vlan_list_db = {}
            vlan_count_cp = {}
            vlan_list_cp = {}
            t_list = []
            vlan_tag = {}
            for cp in device_info["cp"]:
                if vlan_count_db.get(cp["if_name"]):
                    vlan_count_db[cp["if_name"]] += 1
                    vlan_list_db[cp["if_name"]].append(
                        cp["vlan"].get("vlan_id", 0))
                else:
                    vlan_count_db[cp["if_name"]] = 1
                    vlan_list_db[cp["if_name"]] = [
                        cp["vlan"].get("vlan_id", 0)]
            for cp_if in cp_ifs:
                if not cp_if["L3-CE-IF-CPDEL"]:
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
                    t_list.append(if_name)
            for if_name, v_list in vlan_list_cp.items():
                db_vlan = vlan_list_db.get(if_name, [])
                vlan_tag[if_name] = True
                for vlan in v_list:
                    if vlan in db_vlan:
                        db_vlan.remove(vlan)
                for d_vlan in db_vlan:
                    if not d_vlan:
                        vlan_tag[if_name] = False
                        break

            all_del_prefix_list={}
            if tmp_del_prefix_list:
                for db_val in device_info["static_detail"]:
                    if (db_val.get("ipv4") and
                            db_val["ipv4"].get("address")):
                                tmpname=self._set_cidr_ip_address(db_val["ipv4"].get("address"),db_val["ipv4"].get("prefix"))
                                if all_del_prefix_list.get(tmpname) is None:
                                    all_del_prefix_list.update({tmpname:1})
                                else:
                                    all_del_prefix_list.update({tmpname:all_del_prefix_list.get(tmpname)+1})
                    if (db_val.get("ipv6") and
                            db_val["ipv6"].get("address")):
                                tmpname=self._set_cidr_ip_address(db_val["ipv6"].get("address"),db_val["ipv6"].get("prefix"))
                                if all_del_prefix_list.get(tmpname) is None:
                                    all_del_prefix_list.update({tmpname:1})
                                else:
                                    all_del_prefix_list.update({tmpname:all_del_prefix_list.get(tmpname)+1})
                for del_nexthop in tmp_del_prefix_list.keys() :
                    if tmp_del_prefix_list.get(del_nexthop, False) and all_del_prefix_list.get(del_nexthop, False):
                        if tmp_del_prefix_list.get(del_nexthop) == all_del_prefix_list.get(del_nexthop):
                            del_prefix_list.update({del_nexthop:True})
                        else:
                            del_prefix_list.update({del_nexthop:False})
                
                self.common_util_log.logging(
                    " ", self.log_level_debug,
                    "[tmp_del_prefix_list]", tmp_del_prefix_list)
                self.common_util_log.logging(
                    " ", self.log_level_debug,
                    "[all_del_prefix_list]", all_del_prefix_list)
                self.common_util_log.logging(
                    " ", self.log_level_debug,
                    "[del_prefix_list]", del_prefix_list)
            return \
                self._gen_l3_slice_del_variable_message(xml_obj,
                                                        cp_ifs,
                                                        vrf_dtl_info,
                                                        is_static=is_static,
                                                        is_ospf=is_ospf,
                                                        is_bgp=is_bgp,
                                                        is_all_del=is_all_del,
                                                        all_del_if=t_list,
                                                        v_tagging=vlan_tag,
                                                        is_cp_del=is_cp_delete,
                                                        del_prefix_list=del_prefix_list)

        node_1 = self._find_xml_node(xml_obj, "configuration", "interfaces")
        if_name_list = []
        for cp_if in cp_ifs:

            if cp_if.get("L3-CE-IF-NAME") in if_name_list:
                if_name = cp_if.get("L3-CE-IF-NAME")
                for if_node in node_1.findall("interface"):
                    if_n_node = if_node.find("name")
                    if if_name == (if_n_node.text
                                   if if_n_node is not None else None):
                        node_2 = if_node
                        break
            else:
                if_name_list.append(cp_if["L3-CE-IF-NAME"])

                node_2 = self._set_xml_tag(node_1, "interface")
                self._set_xml_tag(
                    node_2, "name", None, None, cp_if["L3-CE-IF-NAME"])
                if cp_if["L3-CE-IF-VLAN"] != 0:
                    self._set_ope_delete_tag(
                        node_2, "vlan-tagging", operation)
                mtu_val = None
                if cp_if["L3-CE-IF-MTU"] is None:
                    pass
                elif cp_if["L3-CE-IF-VLAN"] == 0:
                    mtu_val = int(cp_if["L3-CE-IF-MTU"]) + 14
                    self._set_ope_delete_tag(node_2, "mtu", operation, mtu_val)
                else:
                    self._set_ope_delete_tag(node_2, "mtu", operation, "4114")

            node_3 = self._set_ope_delete_tag(node_2, "unit", operation)
            self._set_xml_tag(
                node_3, "name", None, None, cp_if["L3-CE-IF-VLAN"])
            node_4 = self._set_xml_tag(node_3, "family")

            if cp_if["L3-CE-IF-ADDR6"] is not None:
                node_5 = self._set_xml_tag(node_4, "inet6")
                node_6 = self._set_xml_tag(node_5, "filter")
                node_7 = self._set_xml_tag(node_6, "input")
                self._set_xml_tag(
                    node_7, "filter-name", None, None, "ipv6_filter_input")
                node_6 = self._set_xml_tag(node_5, "address")
                self._set_xml_tag(node_6,
                                  "name",
                                  None,
                                  None,
                                  self._set_cidr_ip_address(
                                      cp_if["L3-CE-IF-ADDR6"],
                                      cp_if["L3-CE-IF-PREFIX6"]))
                self._gen_l3_vrrp_message(node_6, cp_if, True)
                if cp_if["L3-CE-IF-MTU"] is None:
                    pass
                elif cp_if["L3-CE-IF-VLAN"] == 0:
                    pass
                else:
                    self._set_ope_delete_tag(
                        node_5, "mtu", operation, cp_if["L3-CE-IF-MTU"])

            if cp_if["L3-CE-IF-ADDR"] is not None:
                node_5 = self._set_xml_tag(node_4, "inet")
                node_6 = self._set_xml_tag(node_5, "filter")
                node_7 = self._set_xml_tag(node_6, "input")
                self._set_xml_tag(
                    node_7, "filter-name", None, None, "ipv4_filter_input")
                node_6 = self._set_xml_tag(node_5, "address")
                self._set_xml_tag(node_6,
                                  "name",
                                  None,
                                  None,
                                  self._set_cidr_ip_address(
                                      cp_if["L3-CE-IF-ADDR"],
                                      cp_if["L3-CE-IF-PREFIX"]))
                self._gen_l3_vrrp_message(node_6, cp_if, False)
                if cp_if["L3-CE-IF-MTU"] is None:
                    pass
                elif cp_if["L3-CE-IF-VLAN"] == 0:
                    pass
                else:
                    self._set_ope_delete_tag(
                        node_5, "mtu", operation, cp_if["L3-CE-IF-MTU"])

            if cp_if["L3-CE-IF-VLAN"] != 0:
                self._set_xml_tag(
                    node_3, "vlan-id", None, None, cp_if["L3-CE-IF-VLAN"])

        node_1 = self._find_xml_node(xml_obj,
                                     "configuration",
                                     "routing-instances",
                                     "instance")
        self._set_xml_tag_variable(node_1,
                                   "name",
                                   vrf_dtl_info["L3-VRF-NAME"])
        for cp_if in cp_ifs:
            node_2 = self._set_ope_delete_tag(
                node_1, "interface", operation, None)
            node_3 = self._set_xml_tag(
                node_2,
                "name",
                None,
                None,
                "%s.%s" % (cp_if["L3-CE-IF-NAME"], cp_if["L3-CE-IF-VLAN"]))

        self._set_xml_tag_variable(node_1,
                                   "rd-type",
                                   vrf_dtl_info["L3-VRF-RD"],
                                   "route-distinguisher")
        self._set_xml_tag_variable(node_1,
                                   "community",
                                   vrf_dtl_info["L3-VRF-RT"],
                                   "vrf-target")
        self._set_xml_tag_variable(node_1,
                                   "router-id",
                                   vrf_dtl_info["L3-VRF-ROUTER-ID"],
                                   "routing-options")
        node_2 = self._find_xml_node(node_1, "routing-options")
        if is_static:
            self._gen_l3_static_message(
                node_2, cp_ifs, vrf_dtl_info, operation, del_prefix_list)

        if is_bgp or is_ospf:
            node_2 = self._set_xml_tag(node_1, "protocols")
            if is_bgp:
                self._gen_l3_bgp_message(
                    node_2, cp_ifs, operation)
            if is_ospf:
                self._gen_l3_ospf_message(
                    node_2, cp_ifs, operation)

        node_1 = self._find_xml_node(
            xml_obj, "configuration", "class-of-service", "interfaces")

        if not cp_ifs:
            node_1 = self._find_xml_node(xml_obj,
                                         "configuration")
            if_node = self._find_xml_node(xml_obj,
                                          "configuration",
                                          "class-of-service")
            node_1.remove(if_node)

        for cp_if in cp_ifs:
            node_2 = self._set_ope_delete_tag(node_1, "interface", operation)
            self._set_xml_tag(
                node_2, "interface_name", None, None, cp_if["L3-CE-IF-NAME"])

            node_3 = self._set_xml_tag(node_2, "forwarding-class-set")
            self._set_xml_tag(node_3,
                              "class-name",
                              None,
                              None,
                              "fcs_unicast_af_and_be_class")
            node_4 = self._set_xml_tag(
                node_3, "output-traffic-control-profile")
            self._set_xml_tag(
                node_4, "profile-name", None, None, "tcp_unicast_af_and_be")

            node_3 = self._set_xml_tag(node_2, "forwarding-class-set")
            self._set_xml_tag(
                node_3, "class-name", None, None, "fcs_unicast_ef_class")
            node_4 = self._set_xml_tag(
                node_3, "output-traffic-control-profile")
            self._set_xml_tag(
                node_4, "profile-name", None, None, "tcp_unicast_ef")

            node_3 = self._set_xml_tag(node_2, "forwarding-class-set")
            self._set_xml_tag(
                node_3, "class-name", None, None, "fcs_multicast_class")
            node_4 = self._set_xml_tag(
                node_3, "output-traffic-control-profile")
            self._set_xml_tag(
                node_4, "profile-name", None, None, "tcp_multicast")

            node_3 = self._set_xml_tag(node_2, "classifiers")
            node_4 = self._set_xml_tag(node_3, "dscp")
            self._set_xml_tag(node_4,
                              "classifier-dscp-name",
                              None,
                              None,
                              "ce_unicast_dscp_classify")
            node_3 = self._set_xml_tag(node_2, "rewrite-rules")
            node_4 = self._set_xml_tag(node_3, "dscp")
            self._set_xml_tag(node_4,
                              "rewrite-rule-name",
                              None,
                              None,
                              "ce_dscp_remark")

        return True

    @decorater_log
    def _gen_l3_slice_del_variable_message(self,
                                           xml_obj,
                                           cp_ifs,
                                           vrf_dtl_info,
                                           **is_protocol):
        operation = self.__DELETE

        is_static = is_protocol.get("is_static", False)
        is_bgp = is_protocol.get("is_bgp", False)
        is_ospf = is_protocol.get("is_ospf", False)
        is_all_del = is_protocol.get("is_all_del", False)
        if_del_list = is_protocol.get("all_del_if", [])
        v_tagging = is_protocol.get("v_tagging", {})
        is_cp_del = is_protocol.get("is_cp_del", False)
        del_prefix_list = is_protocol.get("del_prefix_list", {})

        node_1 = self._find_xml_node(xml_obj, "configuration", "interfaces")
        if_name_list = []
        if is_cp_del:
            tmp_cp = cp_ifs
        else:
            tmp_cp = []
            node_2 = self._find_xml_node(xml_obj, "configuration")
            node_2.remove(node_1)
        for cp_if in tmp_cp:
            if not cp_if["L3-CE-IF-CPDEL"]:
                continue

            if cp_if.get("L3-CE-IF-NAME") in if_name_list:
                if_name = cp_if.get("L3-CE-IF-NAME")
                for if_node in node_1.findall("interface"):
                    if_n_node = if_node.find("name")
                    if if_name == (if_n_node.text
                                   if if_n_node is not None else None):
                        node_2 = if_node
                        break
            else:
                if_name_list.append(cp_if["L3-CE-IF-NAME"])
                node_2 = self._set_xml_tag(node_1, "interface")
                self._set_xml_tag(
                    node_2, "name", None, None, cp_if["L3-CE-IF-NAME"])
                if cp_if["L3-CE-IF-NAME"] not in if_name_list:
                    if_name_list.append(cp_if["L3-CE-IF-NAME"])
                if cp_if["L3-CE-IF-NAME"] in if_del_list:
                    if v_tagging.get(cp_if["L3-CE-IF-NAME"]):
                        if cp_if.get("L3-CE-IF-VLAN") is not 0:
                            self._set_ope_delete_tag(
                                node_2, "vlan-tagging", operation)
                    if cp_if["L3-CE-IF-MTU"] is not None:
                        self._set_ope_delete_tag(node_2, "mtu", operation)
            node_3 = self._set_ope_delete_tag(node_2, "unit", operation)
            self._set_xml_tag(
                node_3, "name", None, None, cp_if["L3-CE-IF-VLAN"])

        node_1 = self._find_xml_node(xml_obj,
                                     "configuration",
                                     "routing-instances",
                                     "instance")
        self._set_xml_tag_variable(node_1,
                                   "name",
                                   vrf_dtl_info["L3-VRF-NAME"])

        if is_all_del:
            for node_2 in node_1:
                if node_2.tag != "name":
                    node_1.remove(node_2)
                    node_1.attrib["operation"] = "delete"
        else:
            if is_cp_del:
                for cp_if in cp_ifs:
                    if not cp_if.get("L3-CE-IF-CPDEL"):
                        continue
                    node_2 = self._set_ope_delete_tag(
                        node_1, "interface", operation, None)
                    node_3 = self._set_xml_tag(
                        node_2,
                        "name",
                        None,
                        None,
                        "%s.%s" % (cp_if["L3-CE-IF-NAME"],
                                   cp_if["L3-CE-IF-VLAN"]))
            node_2 = self._find_xml_node(node_1, "routing-options")
            if is_static:
                self._gen_l3_static_message(
                    node_2, cp_ifs, vrf_dtl_info, operation, del_prefix_list)
            if not len(node_2):
                node_1.remove(node_2)
            if is_bgp or is_ospf:
                node_2 = self._set_xml_tag(node_1, "protocols")
                if is_bgp:
                    self._gen_l3_bgp_message(
                        node_2, cp_ifs, operation)
                if is_ospf:
                    self._gen_l3_ospf_message(
                        node_2, cp_ifs, operation)
                if not len(node_2):
                    node_1.remove(node_2)

        node_1 = self._find_xml_node(
            xml_obj, "configuration", "class-of-service", "interfaces")

        if not if_del_list:
            node_1 = self._find_xml_node(xml_obj,
                                         "configuration")
            if_node = self._find_xml_node(xml_obj,
                                          "configuration",
                                          "class-of-service")
            node_1.remove(if_node)

        for if_name in if_del_list:
            node_2 = self._set_ope_delete_tag(node_1, "interface", operation)
            self._set_xml_tag(
                node_2, "interface_name", None, None, if_name)
        return True

    @decorater_log
    def _gen_l3_bgp_message(self, xml_obj, cp_ifs, operation):
        is_bgp = False
        for cp_if in cp_ifs:
            if cp_if.get("BGP") is not None:
                is_bgp = True
                break
        if not is_bgp:
            return

        node_1 = self._set_xml_tag(xml_obj, "bgp")
        for cp_if in cp_ifs:
            if cp_if.get("BGP") is None:
                continue

            bgp = cp_if["BGP"]
            if bgp["L3-BGP-RADD"] is not None:
                node_2 = self._set_xml_tag(node_1, "group")
                self._set_xml_tag(node_2, "name", None, None, "RI_eBGPv4")
                node_3 = self._set_ope_delete_tag(
                    node_2, "neighbor", operation, None)
                self._set_xml_tag(
                    node_3, "name", None, None, bgp["L3-BGP-RADD"])
                if operation == self.__DELETE:
                    continue
                self._set_xml_tag(
                    node_3, "import", None, None, "eBGPv4_To_CE_import")
                if bgp.get("L3-BGP-MASTER") is None:
                    self._set_xml_tag(node_3,
                                      "export",
                                      None,
                                      None,
                                      "eBGPv4_To_standby-CE_export")
                else:
                    self._set_xml_tag(node_3,
                                      "export",
                                      None,
                                      None,
                                      "eBGPv4_To_active-CE_export")
                self._set_xml_tag(
                    node_3, "peer-as", None, None, bgp["L3-BGP-PEER-AS"])
                self._set_xml_tag(
                    node_3, "local-address", None, None, bgp["L3-BGP-LADD"])
                self._set_xml_tag(
                    node_3, "as-override")
                node_3 = self._set_xml_tag(node_2, "family")
                node_4 = self._set_xml_tag(node_3, "inet")
                self._set_xml_tag(node_4, "unicast")
                node_3 = self._set_xml_tag(
                    node_2, "type", None, None, "external")

            if bgp["L3-BGP-RADD6"] is not None:
                node_2 = self._set_xml_tag(node_1, "group")
                self._set_xml_tag(node_2, "name", None, None, "RI_eBGPv6")
                node_3 = self._set_ope_delete_tag(
                    node_2, "neighbor", operation, None)
                self._set_xml_tag(
                    node_3, "name", None, None, bgp["L3-BGP-RADD6"])
                if operation == self.__DELETE:
                    continue
                self._set_xml_tag(
                    node_3, "import", None, None, "eBGPv6_To_CE_import")
                if bgp["L3-BGP-MASTER"] is None:
                    self._set_xml_tag(node_3,
                                      "export",
                                      None,
                                      None,
                                      "eBGPv6_To_standby-CE_export")
                else:
                    self._set_xml_tag(node_3,
                                      "export",
                                      None,
                                      None,
                                      "eBGPv6_To_active-CE_export")
                self._set_xml_tag(
                    node_3, "peer-as", None, None, bgp["L3-BGP-PEER-AS"])
                self._set_xml_tag(
                    node_3, "local-address", None, None, bgp["L3-BGP-LADD6"])
                self._set_xml_tag(
                    node_3, "as-override")
                node_3 = self._set_xml_tag(node_2, "family")
                node_4 = self._set_xml_tag(node_3, "inet6")
                self._set_xml_tag(node_4, "unicast")
                node_3 = self._set_xml_tag(
                    node_2, "type", None, None, "external")

    @decorater_log
    def _gen_l3_ospf_message(self, xml_obj, cp_ifs, operation):
        is_ospf_ipv4 = False
        is_ospf_ipv6 = False
        ospf3_list = []
        ospf_list = []
        for cp_if in cp_ifs:
            if cp_if.get("L3-OSPF-CP-METRIC") is not None:
                if cp_if.get("L3-CE-IF-ADDR6") is not None:
                    is_ospf_ipv6 = True
                    ospf3_list.append(cp_if)
                if cp_if.get("L3-CE-IF-ADDR") is not None:
                    is_ospf_ipv4 = True
                    ospf_list.append(cp_if)

        if not is_ospf_ipv4 and not is_ospf_ipv6:
            return

        if is_ospf_ipv6:
            node_1 = self._set_xml_tag(xml_obj, "ospf3")
            if operation != self.__DELETE:
                node_2 = self._set_xml_tag(node_1, "domain-id")
                self._set_xml_tag(node_2, "domain-id", None, None, "64050")
                self._set_xml_tag(node_1,
                                  "import",
                                  None,
                                  None,
                                  "v6_OSPF_To_CE_import")
                self._set_xml_tag(node_1,
                                  "export",
                                  None,
                                  None,
                                  "v6_OSPF_To_CE_export")
            node_2 = self._set_xml_tag(node_1, "area")
            self._set_xml_tag(node_2, "name", None, None, "0.0.0.0")

            for cp_if in ospf3_list:
                node_3 = self._set_ope_delete_tag(
                    node_2, "interface", operation, None)
                self._set_xml_tag(node_3,
                                  "name",
                                  None,
                                  None,
                                  cp_if["L3-CE-IF-NAME"] + "." +
                                  str(cp_if["L3-CE-IF-VLAN"]))
                if operation != self.__DELETE:
                    self._set_xml_tag(node_3,
                                      "metric",
                                      None,
                                      None,
                                      cp_if["L3-OSPF-CP-METRIC"])
                    self._set_xml_tag(node_3, "priority", None, None, "10")

        if is_ospf_ipv4:
            node_1 = self._set_xml_tag(xml_obj, "ospf")
            if operation != self.__DELETE:
                node_2 = self._set_xml_tag(node_1, "domain-id")
                self._set_xml_tag(node_2, "domain-id", None, None, "64050")
                self._set_xml_tag(node_1,
                                  "import",
                                  None,
                                  None,
                                  "v4_OSPF_To_CE_import")
                self._set_xml_tag(node_1,
                                  "export",
                                  None,
                                  None,
                                  "v4_OSPF_To_CE_export")
            node_2 = self._set_xml_tag(node_1, "area")
            self._set_xml_tag(node_2, "name", None, None, "0.0.0.0")

            for cp_if in ospf_list:
                node_3 = self._set_ope_delete_tag(
                    node_2, "interface", operation, None)
                self._set_xml_tag(node_3,
                                  "name",
                                  None,
                                  None,
                                  cp_if["L3-CE-IF-NAME"] + "." +
                                  str(cp_if["L3-CE-IF-VLAN"]))
                if operation != self.__DELETE:
                    self._set_xml_tag(node_3,
                                      "metric",
                                      None,
                                      None,
                                      cp_if["L3-OSPF-CP-METRIC"])
                    self._set_xml_tag(node_3, "priority", None, None, "10")

    @decorater_log
    def _gen_l3_static_message(self, xml_obj, cp_ifs, vrf_dtl_info, operation, del_prefix_list):

        static_routes = []
        static_routes6 = []
        tmp_addr = None
        for cp_if in cp_ifs:
            if cp_if.get("STATIC") is not None:
                for route in cp_if["STATIC"]["route6"]:
                    if route.get("L3-STATIC-ROUTE-ADD6") is not None:
                        tmp_addr = \
                            self._set_cidr_ip_address(
                                route["L3-STATIC-ROUTE-ADD6"],
                                route["L3-STATIC-ROUTE-PREFIX6"])
                        tmp = {"addr": tmp_addr,
                               "next": route["L3-STATIC-ROUTE-NEXT6"]}
                        static_routes6.append(tmp)
                for route in cp_if["STATIC"]["route"]:
                    if route.get("L3-STATIC-ROUTE-ADD") is not None:
                        tmp_addr = \
                            self._set_cidr_ip_address(
                                route["L3-STATIC-ROUTE-ADD"],
                                route["L3-STATIC-ROUTE-PREFIX"])
                        tmp = {"addr": tmp_addr,
                               "next": route["L3-STATIC-ROUTE-NEXT"]}
                        static_routes.append(tmp)

        if not static_routes and not static_routes6:
            return

        if len(static_routes6) > 0:
            node_1 = self._set_xml_tag(xml_obj, "rib")
            self._set_xml_tag(node_1,
                              "name",
                              None,
                              None,
                              vrf_dtl_info["L3-VRF-NAME"] + ".inet6.0")
            node_2 = self._set_xml_tag(node_1, "static")
            double_write_check_ipv6=[]
            for s_route in static_routes6:
                if operation != self.__DELETE:
                    node_3 = self._set_ope_delete_tag(
                        node_2, "route", operation, None)
                    self._set_xml_tag(node_3, "name", None, None, s_route["addr"])
                    node_4 = self._set_ope_delete_tag(
                        node_3, "qualified-next-hop", operation, None)
                    self._set_xml_tag(
                        node_4, "nexthop", None, None, s_route["next"])
                else:
                    if not s_route["addr"] in double_write_check_ipv6 and del_prefix_list.get(s_route["addr"], True):
                        node_3 = self._set_ope_delete_tag(
                            node_2, "route", operation, None)
                        self._set_xml_tag(node_3, "name", None, None, s_route["addr"])
                        double_write_check_ipv6.append(s_route["addr"])
                    elif not s_route["addr"] in double_write_check_ipv6 and not del_prefix_list.get(s_route["addr"], True):
                        node_3 = self._set_ope_delete_tag(
                            node_2, "route", "notdel", None)
                        self._set_xml_tag(node_3, "name", None, None, s_route["addr"])
                        node_4 = self._set_ope_delete_tag(
                            node_3, "qualified-next-hop", operation, None)
                        self._set_xml_tag(
                            node_4, "nexthop", None, None, s_route["next"])

        if len(static_routes) > 0:
            node_1 = self._set_xml_tag(xml_obj, "rib")
            self._set_xml_tag(node_1,
                              "name",
                              None,
                              None,
                              vrf_dtl_info["L3-VRF-NAME"] + ".inet.0")
            node_2 = self._set_xml_tag(node_1, "static")
            double_write_check_ipv4=[]
            for s_route in static_routes:
                if operation != self.__DELETE:
                    node_3 = self._set_ope_delete_tag(
                        node_2, "route", operation, None)
                    self._set_xml_tag(node_3, "name", None, None, s_route["addr"])
                    node_4 = self._set_ope_delete_tag(
                        node_3, "qualified-next-hop", operation, None)
                    self._set_xml_tag(
                        node_4, "nexthop", None, None, s_route["next"])
                else:
                    if not s_route["addr"] in double_write_check_ipv4 and del_prefix_list.get(s_route["addr"], False):
                        node_3 = self._set_ope_delete_tag(
                            node_2, "route", operation, None)
                        self._set_xml_tag(node_3, "name", None, None, s_route["addr"])
                        double_write_check_ipv4.append(s_route["addr"])
                    elif not del_prefix_list.get(s_route["addr"], True):
                        node_3 = self._set_ope_delete_tag(
                            node_2, "route", "notdel", None)
                        self._set_xml_tag(node_3, "name", None, None, s_route["addr"])
                        node_4 = self._set_ope_delete_tag(
                            node_3, "qualified-next-hop", operation, None)
                        self._set_xml_tag(
                            node_4, "nexthop", None, None, s_route["next"])

    @decorater_log
    def _gen_l3_vrrp_message(self, xml_obj, cp_if, is_ipv6=True):
        vrrp = cp_if.get("VRRP")
        if vrrp is None:
            return

        if is_ipv6 and vrrp.get("L3-VRRP-VIRT-ADDR6") is not None:
            node_1 = self._set_xml_tag(xml_obj, "vrrp-inet6-group")
            self._set_xml_tag(node_1,
                              "group_id",
                              None,
                              None,
                              vrrp["L3-VRRP-GROUP-ID"])
            self._set_xml_tag(node_1,
                              "virtual-inet6-address",
                              None,
                              None,
                              vrrp["L3-VRRP-VIRT-ADDR6"])
            self._set_xml_tag(node_1,
                              "priority",
                              None,
                              None,
                              vrrp["L3-VRRP-VIRT-PRI"])
            self._set_xml_tag(
                node_1, "inet6-advertise-interval", None, None, "1000")
            node_2 = self._set_xml_tag(node_1, "preempt")
            self._set_xml_tag(node_2, "hold-time", None, None, "180")
            if vrrp.get("track") is not None:
                if len(vrrp["track"]) != 0:
                    node_2 = self._set_xml_tag(node_1, "track")
                    for track in vrrp["track"]:
                        node_3 = self._set_xml_tag(node_2, "interface")
                        self._set_xml_tag(node_3,
                                          "interface_name",
                                          None,
                                          None,
                                          track["L3-VRRP-VIRT-IF"])
                        self._set_xml_tag(
                            node_3, "priority-cost", None, None, "10")
        elif is_ipv6 is False and vrrp.get("L3-VRRP-VIRT-ADDR") is not None:
            node_1 = self._set_xml_tag(xml_obj, "vrrp-group")
            self._set_xml_tag(node_1,
                              "group_id",
                              None,
                              None,
                              vrrp["L3-VRRP-GROUP-ID"])
            self._set_xml_tag(node_1,
                              "virtual-address",
                              None,
                              None,
                              vrrp["L3-VRRP-VIRT-ADDR"])
            self._set_xml_tag(node_1,
                              "priority",
                              None,
                              None,
                              vrrp["L3-VRRP-VIRT-PRI"])
            self._set_xml_tag(node_1, "advertise-interval", None, None, "1")
            node_2 = self._set_xml_tag(node_1, "preempt")
            self._set_xml_tag(node_2, "hold-time", None, None, "180")
            if vrrp.get("track") is not None:
                if len(vrrp["track"]) != 0:
                    node_2 = self._set_xml_tag(node_1, "track")
                    for track in vrrp["track"]:
                        node_3 = self._set_xml_tag(node_2, "interface")
                        self._set_xml_tag(node_3,
                                          "interface_name",
                                          None,
                                          None,
                                          track["L3-VRRP-VIRT-IF"])
                        self._set_xml_tag(
                            node_3, "priority-cost", None, None, "10")

    @decorater_log
    def _gen_ce_lag_variable_message(self,
                                     xml_obj,
                                     device_info,
                                     ec_message,
                                     operation):
        is_variable_value = True
        ec_mes_dev = None
        lag_ifs = []
        lag_mem_ifs = []
        if operation == self.__DELETE:
            dev = ec_message["device"]["name"]
            if dev == device_info["device"]["device_name"]:
                ec_mes_dev = dev
            if ec_mes_dev is None:
                return False

        if not ec_message["device"].get("ce-lag-interface") \
                or len(ec_message["device"]["ce-lag-interface"]) == 0:
            is_variable_value = False

        for lag in ec_message["device"]["ce-lag-interface"]:
            if operation == self.__DELETE:
                if lag.get("name") is None \
                        or lag.get("minimum-links") is None:
                    is_variable_value = False
                    break
                tmp = \
                    {"CL-LAG-IF-NAME":  lag["name"],
                     "CL-LAG-LINKS": lag["minimum-links"],
                     "CL-LAG-SPEED": None}
                for db_lag in device_info["lag"]:
                    if db_lag.get("if_name") == lag.get("name"):
                        tmp["CL-LAG-SPEED"] = db_lag.get("link_speed")
                if tmp["CL-LAG-SPEED"] is None:
                    is_variable_value = False
                    break

                for db_lag_mem in device_info["lag_member"]:
                    if (db_lag_mem.get("lag_if_name") is None or
                            db_lag_mem.get("if_name") is None):
                        is_variable_value = False
                        break
                    if db_lag_mem["lag_if_name"] == lag["name"]:
                        lag_mem_ifs.append(
                            {"CL-IF-NAME": db_lag_mem["if_name"],
                             "CL-LAG-IF-NAME": lag["name"]})
            else:
                if lag.get("name") is None \
                        or lag.get("minimum-links") is None \
                        or lag.get("link-speed") is None:
                    is_variable_value = False
                    break
                tmp = \
                    {"CL-LAG-IF-NAME":  lag["name"],
                     "CL-LAG-LINKS": lag["minimum-links"],
                     "CL-LAG-SPEED": lag["link-speed"]}

                if not lag.get("leaf-interface") \
                        or len(lag["leaf-interface"]) == 0:
                    is_variable_value = False

                for b_if in lag["leaf-interface"]:
                    if b_if["name"] is None:
                        is_variable_value = False
                        break
                    lag_mem_ifs.append(
                        {"CL-IF-NAME": b_if["name"],
                         "CL-LAG-IF-NAME": lag["name"]})
            lag_ifs.append(tmp)

        if is_variable_value is False:
            return False

        if operation == self.__DELETE:
            return self._gen_ce_lag_del_variable_message(xml_obj,
                                                         lag_ifs,
                                                         lag_mem_ifs)

        if_node = self._find_xml_node(xml_obj, "configuration", "interfaces")

        for lag_mem_if in lag_mem_ifs:
            node_1 = self._set_ope_delete_tag(if_node, "interface", operation)
            self._set_xml_tag(node_1,
                              "interface_name",
                              None,
                              None,
                              lag_mem_if["CL-IF-NAME"])
            node_2 = self._set_xml_tag(node_1, "ether-options")
            node_3 = self._set_xml_tag(node_2, "ieee-802.3ad")
            self._set_xml_tag(node_3,
                              "bundle",
                              None,
                              None,
                              lag_mem_if["CL-LAG-IF-NAME"])

        for lag_if in lag_ifs:
            node_1 = self._set_ope_delete_tag(if_node, "interface", operation)
            self._set_xml_tag(node_1,
                              "interface_name",
                              None,
                              None,
                              lag_if["CL-LAG-IF-NAME"])
            node_2 = self._set_xml_tag(node_1, "aggregated-ether-options")
            self._set_xml_tag(node_2,
                              "minimum-links",
                              None,
                              None,
                              lag_if["CL-LAG-LINKS"])
            self._set_xml_tag(node_2,
                              "link-speed",
                              None,
                              None,
                              lag_if["CL-LAG-SPEED"])
            node_3 = self._set_xml_tag(node_2, "lacp")
            self._set_xml_tag(node_3, "active")
            self._set_xml_tag(node_3, "periodic", None, None, "fast")

        return True

    @decorater_log
    def _gen_ce_lag_del_variable_message(self, xml_obj, lag_ifs, lag_mem_ifs):
        operation = self.__DELETE

        if_node = self._find_xml_node(xml_obj, "configuration", "interfaces")
        for lag_mem_if in lag_mem_ifs:
            node_1 = self._set_ope_delete_tag(if_node, "interface", operation)
            self._set_xml_tag(node_1,
                              "interface_name",
                              None,
                              None,
                              lag_mem_if["CL-IF-NAME"])
        for lag_if in lag_ifs:
            node_1 = self._set_ope_delete_tag(if_node, "interface", operation)
            self._set_xml_tag(node_1,
                              "interface_name",
                              None,
                              None,
                              lag_if["CL-LAG-IF-NAME"])
        return True

    @decorater_log
    def _gen_internal_lag_variable_message(self,
                                           xml_obj,
                                           device_info,
                                           ec_message,
                                           operation):
        l3_vpn = "l3"
        is_variable_value = True
        ec_mes_dev = None
        lag_ifs = []
        lag_mem_ifs = []
        if operation == self.__DELETE:
            dev = ec_message["device"]["name"]
            if dev == device_info["device"]["device_name"]:
                ec_mes_dev = dev
            if ec_mes_dev is None:
                return False
        if "vpn-type" in ec_message["device"]:
            vpn_type = ec_message["device"]["vpn-type"]
        else:
            vpn_type = None

        if ec_message["device"].get("internal-lag") is None \
                or len(ec_message["device"]["internal-lag"]) == 0:
            is_variable_value = False

        for lag in ec_message["device"]["internal-lag"]:
            if operation == self.__DELETE:
                if lag.get("name") is None \
                        or lag.get("minimum-links") is None:
                    is_variable_value = False
                    break
                tmp = \
                    {"IL-LAG-IF-NAME":  lag["name"],
                     "IL-LAG-LINKS": lag["minimum-links"],
                     "IL-LAG-SPEED": None,
                     "IL-LAG-ADDR": None,
                     "IL-LAG-PREFIX": None}
                for db_lag in device_info["lag"]:
                    if db_lag.get("link_speed") is None \
                            or db_lag["internal_link"].get("address") is None \
                            or db_lag["internal_link"].get("prefix") is None:
                        is_variable_value = False
                        break

                    if db_lag["if_name"] == lag["name"]:
                        tmp["IL-LAG-SPEED"] = db_lag["link_speed"]
                        tmp["IL-LAG-ADDR"] = db_lag["internal_link"]["address"]
                        tmp["IL-LAG-PREFIX"] = \
                            db_lag["internal_link"]["prefix"]
                        break
                if tmp["IL-LAG-ADDR"] is None:
                    is_variable_value = False
                    break
                for b_if in lag["internal-interface"]:
                    if b_if["name"] is None:
                        is_variable_value = False
                        break
                    lag_mem_ifs.append(
                        {"IL-IF-NAME": b_if["name"],
                         "IL-LAG-IF-NAME": lag["name"]})
            else:
                if lag.get("name") is None \
                        or lag.get("minimum-links") is None \
                        or lag.get("link-speed") is None \
                        or lag.get("address") is None \
                        or lag.get("prefix") is None:
                    is_variable_value = False
                    break
                tmp = \
                    {"IL-LAG-IF-NAME":  lag["name"],
                     "IL-LAG-LINKS": lag["minimum-links"],
                     "IL-LAG-SPEED": lag["link-speed"],
                     "IL-LAG-ADDR": lag["address"],
                     "IL-LAG-PREFIX": lag["prefix"]}

                if lag.get("internal-interface") is None \
                        or len(lag["internal-interface"]) == 0:
                    is_variable_value = False
                    break

                for b_if in lag["internal-interface"]:
                    if b_if["name"] is None:
                        is_variable_value = False
                        break
                    lag_mem_ifs.append(
                        {"IL-IF-NAME": b_if["name"],
                         "IL-LAG-IF-NAME": lag["name"]})
            lag_ifs.append(tmp)

        if is_variable_value is False:
            return False

        if operation == self.__DELETE:
            return self._gen_internal_lag_del_variable_message(xml_obj,
                                                               lag_ifs,
                                                               lag_mem_ifs)

        if_node = self._find_xml_node(xml_obj, "configuration", "interfaces")

        for lag_mem_if in lag_mem_ifs:
            node_1 = self._set_ope_delete_tag(if_node, "interface", operation)
            self._set_xml_tag(node_1,
                              "interface_name",
                              None,
                              None,
                              lag_mem_if["IL-IF-NAME"])
            node_2 = self._set_xml_tag(node_1, "ether-options")
            node_3 = self._set_xml_tag(node_2, "ieee-802.3ad")
            self._set_xml_tag(node_3,
                              "bundle",
                              None,
                              None,
                              lag_mem_if["IL-LAG-IF-NAME"])

        for lag_if in lag_ifs:
            node_1 = self._set_ope_delete_tag(if_node, "interface", operation)
            self._set_xml_tag(node_1,
                              "interface_name",
                              None,
                              None,
                              lag_if["IL-LAG-IF-NAME"])
            self._set_xml_tag(node_1, "mtu", None, None, "4110")
            node_2 = self._set_xml_tag(node_1, "aggregated-ether-options")
            self._set_xml_tag(node_2,
                              "minimum-links",
                              None,
                              None,
                              lag_if["IL-LAG-LINKS"])
            self._set_xml_tag(node_2,
                              "link-speed",
                              None,
                              None,
                              lag_if["IL-LAG-SPEED"])
            node_3 = self._set_xml_tag(node_2, "lacp")
            self._set_xml_tag(node_3, "active")
            self._set_xml_tag(node_3, "periodic", None, None, "fast")
            node_2 = self._set_xml_tag(node_1, "unit")
            self._set_xml_tag(node_2, "name", None, None, "0")
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
                              self._set_cidr_ip_address(
                                  lag_if["IL-LAG-ADDR"],
                                  lag_if["IL-LAG-PREFIX"]))
            if vpn_type is None or vpn_type == l3_vpn:
                node_4 = self._set_xml_tag(node_3, "mpls")

        node_1 = self._find_xml_node(xml_obj,
                                     "configuration",
                                     "protocols",
                                     "ospf",
                                     "area")
        for lag_if in lag_ifs:
            node_2 = self._set_ope_delete_tag(node_1, "interface", operation)
            self._set_xml_tag(node_2,
                              "interface_name",
                              None,
                              None,
                              "%s.0" % lag_if["IL-LAG-IF-NAME"])
            self._set_xml_tag(node_2,
                              "metric",
                              None,
                              None,
                              "100")
            self._set_xml_tag(node_2,
                              "priority",
                              None,
                              None,
                              "10" if vpn_type is not None else "20")

        if_node = self._find_xml_node(xml_obj,
                                      "configuration",
                                      "class-of-service",
                                      "interfaces")

        if not lag_ifs:
            node_1 = self._find_xml_node(xml_obj,
                                         "configuration")
            if_node = self._find_xml_node(xml_obj,
                                          "configuration",
                                          "class-of-service")
            node_1.remove(if_node)

        for lag_if in lag_ifs:
            node_1 = self._set_ope_delete_tag(if_node, "interface", operation)
            self._set_xml_tag(node_1,
                              "interface_name",
                              None,
                              None,
                              lag_if["IL-LAG-IF-NAME"])
            node_2 = self._set_xml_tag(node_1, "forwarding-class-set")
            self._set_xml_tag(node_2,
                              "class-name",
                              None,
                              None,
                              "fcs_unicast_af_and_be_class")
            node_3 = self._set_xml_tag(
                node_2, "output-traffic-control-profile")
            self._set_xml_tag(node_3,
                              "profile-name",
                              None,
                              None,
                              "tcp_unicast_af_and_be")
            node_2 = self._set_xml_tag(node_1, "forwarding-class-set")
            self._set_xml_tag(node_2,
                              "class-name",
                              None,
                              None,
                              "fcs_unicast_ef_class")
            node_3 = self._set_xml_tag(
                node_2, "output-traffic-control-profile")
            self._set_xml_tag(node_3,
                              "profile-name",
                              None,
                              None,
                              "tcp_unicast_ef")
            node_2 = self._set_xml_tag(node_1, "forwarding-class-set")
            self._set_xml_tag(node_2,
                              "class-name",
                              None,
                              None,
                              "fcs_multicast_class")
            node_3 = self._set_xml_tag(
                node_2, "output-traffic-control-profile")
            self._set_xml_tag(node_3,
                              "profile-name",
                              None,
                              None,
                              "tcp_multicast")
            node_2 = self._set_xml_tag(node_1, "unit")
            self._set_xml_tag(node_2, "interface_unit_number", None, None, "0")
            node_3 = self._set_xml_tag(node_2, "rewrite-rules")
            node_4 = self._set_xml_tag(node_3, "exp")
            node_5 = self._set_xml_tag(
                node_4, "rewrite-rule-name", None, None, "msf_mpls_exp_remark")
            node_2 = self._set_xml_tag(node_1, "classifiers")
            node_3 = self._set_xml_tag(node_2, "dscp")
            self._set_xml_tag(node_3,
                              "classifier-dscp-name",
                              None,
                              None,
                              "msf_unicast_dscp_classify")
            node_2 = self._set_xml_tag(node_1, "rewrite-rules")
            node_3 = self._set_xml_tag(node_2, "dscp")
            self._set_xml_tag(node_3,
                              "rewrite-rule-name",
                              None,
                              None,
                              "msf_dscp_remark")

        return True

    @decorater_log
    def _gen_internal_lag_del_variable_message(self,
                                               xml_obj,
                                               lag_ifs,
                                               lag_mem_ifs):
        operation = self.__DELETE

        if_node = self._find_xml_node(xml_obj, "configuration", "interfaces")

        for lag_mem_if in lag_mem_ifs:
            node_1 = self._set_ope_delete_tag(if_node, "interface", operation)
            self._set_xml_tag(node_1,
                              "interface_name",
                              None,
                              None,
                              lag_mem_if["IL-IF-NAME"])

        for lag_if in lag_ifs:
            node_1 = self._set_ope_delete_tag(if_node, "interface", operation)
            self._set_xml_tag(node_1,
                              "interface_name",
                              None,
                              None,
                              lag_if["IL-LAG-IF-NAME"])

        node_1 = self._find_xml_node(xml_obj,
                                     "configuration",
                                     "protocols",
                                     "ospf",
                                     "area")
        for lag_if in lag_ifs:
            node_2 = self._set_ope_delete_tag(node_1, "interface", operation)
            self._set_xml_tag(node_2,
                              "interface_name",
                              None,
                              None,
                              "%s.0" % lag_if["IL-LAG-IF-NAME"])

        if_node = self._find_xml_node(xml_obj,
                                      "configuration",
                                      "class-of-service",
                                      "interfaces")
        if not lag_ifs:
            node_1 = self._find_xml_node(xml_obj,
                                         "configuration")
            if_node = self._find_xml_node(xml_obj,
                                          "configuration",
                                          "class-of-service")
            node_1.remove(if_node)

        for lag_if in lag_ifs:
            node_1 = self._set_ope_delete_tag(if_node, "interface", operation)
            self._set_xml_tag(node_1,
                              "interface_name",
                              None,
                              None,
                              lag_if["IL-LAG-IF-NAME"])
        return True


    @decorater_log
    def _comparsion_sw_db_l2_slice(self, message, db_info):
        class ns_xml(object):
            class ns_list(object):
                xnm = "xnm"

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

        port_mtu = {self.__PORT_MODE_ACCESS: 4110,
                    self.__PORT_MODE_TRUNK: 4114}

        is_return = True

        ns_p = ns_xml(ns_xml.ns_list.xnm)

        cp_list = []
        if_list = []
        device_name = None
        for tmp_cp in (db_info.get("cp")
                       if db_info.get("cp") is not None else []):
            cp_info = {"if_name": None,
                       "vlan_id": None,
                       "port_mode": None,
                       "vni": None,
                       "multicast_group": None}.copy()
            if not device_name:
                device_name = tmp_cp.get("device_name")
            cp_info["if_name"] = tmp_cp.get("if_name")
            cp_info["vlan_id"] = (tmp_cp["vlan"].get("vlan_id")
                                  if tmp_cp.get("vlan") else None)
            cp_info["port_mode"] = (tmp_cp["vlan"].get("port_mode")
                                    if tmp_cp.get("vlan") else None)
            cp_info["vni"] = (tmp_cp["vxlan"].get("vni")
                              if tmp_cp.get("vxlan") else None)
            cp_info["multicast_group"] = (tmp_cp["vxlan"].get("mc_group")
                                          if tmp_cp.get("vxlan") else None)
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
                    (if_name.text if if_name is not None else None,), __name__)
                break

            mtu = ns_p.ns_find_node(interface, "mtu")

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
                        if (self._comparsion_pair(
                                if_name, db_cp.get("if_name")) and
                                self._comparsion_pair(mtu, db_mtu) and
                                self._comparsion_pair(
                                    port_mode, db_cp.get("port_mode")) and
                                self._comparsion_pair(
                                    vlan, db_cp.get("vlan_id"))):
                            match_flg = True
                            break
                    if not match_flg:
                        self.common_util_log.logging(
                            device_name, self.log_level_debug,
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
            mc_group = ns_p.ns_find_node(vlan, "vxlan", "multicast-group")
            vlan_id = ns_p.ns_find_node(vlan, "vlan-id")

            is_match = False
            for db_cp in cp_list:
                if(self._comparsion_pair(
                        vlan_name, "vlan%s" % (db_cp.get("vlan_id"),)) and
                   self._comparsion_pair(vni, db_cp.get("vni")) and
                   self._comparsion_pair(mc_group,
                                         db_cp.get("multicast_group")) and
                   self._comparsion_pair(vlan_id, db_cp.get("vlan_id"))):
                    is_match = True
                    break

            if not is_match:
                is_return = False
                self.common_util_log.logging(
                    device_name, self.log_level_debug,
                    (vlan_name.text if vlan_name is not None else None,
                     vni.text if vni is not None else None,
                     mc_group.text if mc_group is not None else None,
                     vlan_id.text if vlan_id is not None else None,),
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
                    (if_name.text if if_name is not None else None,), __name__)
                break
            unit = ns_p.ns_find_node(interface, "unit")
            if unit is not None:
                is_ok = False
                for db_cp in cp_list:
                    if (self._comparsion_pair(if_name, db_cp["if_name"]) and
                            ("%s" % (db_cp["port_mode"],)).lower() ==
                            self.__PORT_MODE_TRUNK):
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
        class ns_xml(object):

            class ns_list(object):
                xnm = "xnm"
            n_sp_dict = {ns_list.xnm:

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
                        cp_dict["vrrp_group_id"] = vrrp.get("gropu_id")
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
                     (node_3.text, tmp_list)), __name__)
                is_return = False
                break

        return is_return
