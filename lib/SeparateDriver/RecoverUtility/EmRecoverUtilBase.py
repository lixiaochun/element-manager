# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmRecoverUtilBase.py
'''
Utility for restoration(Base)
'''
import json
import sys
import copy
import traceback
import GlobalModule
from EmCommonLog import decorater_log
from EmCommonLog import decorater_log_in_out
from EmDriverCommonUtilityLog import EmDriverCommonUtilityLog


class EmRecoverUtilBase(object):
    '''
    Utility for restoration
    Called from individual section on driver (base class).
    '''

    log_level_debug = "DEBUG"
    log_level_warn = "WARN"
    log_level_info = "INFO"
    log_level_error = "ERROR"

    _if_type_phy = "physical-if"
    _if_type_lag = "lag-if"

    _if_type_phy_num = 1
    _if_type_lag_num = 2

    _slice_type_l2 = 2
    _slice_type_l3 = 3

    _lag_type_inner_num = 1
    _lag_type_ce_num = 2

    def __init__(self):
        '''
        Constructor
        '''
        self.name_spine = GlobalModule.SERVICE_SPINE
        self.name_leaf = GlobalModule.SERVICE_LEAF
        self.name_l2_slice = GlobalModule.SERVICE_L2_SLICE
        self.name_l3_slice = GlobalModule.SERVICE_L3_SLICE
        self.name_ce_lag = GlobalModule.SERVICE_CE_LAG
        self.name_internal_link = GlobalModule.SERVICE_INTERNAL_LINK
        self.name_b_leaf = GlobalModule.SERVICE_B_LEAF
        self.name_breakout = GlobalModule.SERVICE_BREAKOUT
        self.name_cluster_link = GlobalModule.SERVICE_CLUSTER_LINK
        self.name_recover_node = GlobalModule.SERVICE_RECOVER_NODE
        self.name_recover_service = GlobalModule.SERVICE_RECOVER_SERVICE
        self.name_acl_filter = GlobalModule.SERVICE_ACL_FILTER

        self.common_util_log = EmDriverCommonUtilityLog()

    @decorater_log_in_out
    def create_recover_message(self, ec_message_str,
                               db_info_str, service_type):
        '''
        Create EC message or DB information of operation to be used for restoration expansion or "recover service"

        Parameter:
            ec_message : EC message for restoration expansion
            db_info : DB information
            service_type : Restoration expansion or Recover service
        Return Value :
            Result : Boolean
            DB message for restoration which has been created(in case of "recover service" only)
            EC message for restoration which has been created
        '''
        try:
            ec_message = json.loads(ec_message_str)
            db_info = json.loads(db_info_str)
            recover_db_info = None
            ret, recover_ec_message = self._create_recover_ec_message(
                ec_message, db_info)
            if ret and recover_ec_message is not None and\
                    service_type == self.name_recover_service:
                ret, recover_db_info = self._create_recover_db_info(
                    ec_message, db_info)
            return ret, recover_db_info, recover_ec_message
        except Exception, ex_message:
            if 'ec_message' in locals():
                device_name = ec_message.get("name")
            else:
                device_name = 'device_name is undefined'
            self.common_util_log.logging(
                device_name, self.log_level_debug,
                "ERROR %s\n%s" %
                (ex_message, traceback.format_exc()), __name__)
            sys.exc_info()
            return False, None, None

    @decorater_log
    def _gen_json_name(self, json, db_info, ec_message, device_tag=None):
        '''
            Set the device name to the EC message storage dictionary object
            to be used for restoration based on EC message for restoration expansion/"recover service"
            and DB information
            Explanation about parameter：
                json：EC message storage dictionary object
                db_info : DB information
                ec_message : EC message for restoration expansion/"recover service"
                device_tag : device tag（default: device）
        '''
        if device_tag is None:
            device_tag = "device"
        json[device_tag]["name"] = ec_message.get("device", {}).get("name")

    @decorater_log
    def _gen_json_equipment(self, json, db_info, ec_message):
        '''
            Set the device connection information to the EC message storage dictionary object
            to be used for restoration based on EC message for restoration expansion/"recover service"
            and DB information
            Explanation about parameter：
                json：EC message storage dictionary object
                db_info : DB information
                ec_message : EC message for restoration expansion/"recover service"
        '''
        equipment = ec_message.get("device", {}).get("equipment")
        db_q_in_q = db_info.get("device", {}).get("q-in-q")
        if equipment and db_q_in_q:
            equipment["q-in-q"] = db_q_in_q
        json["device"]["equipment"] = equipment

    @decorater_log
    def _gen_json_breakout(self, json, db_info, ec_message):
        '''
            Set the breakout IF Information to the EC message storage dictionary object
            to be used for restoration based on EC message for restoration expansion/"recover service"
            and DB information
            Explanation about parameter：
                json：EC message storage dictionary object
                db_info : DB information
                ec_message : EC message for restoration expansion/"recover service"
        '''

        json["device"]["breakout-interface_value"] = \
            db_info.get("breakout_info").get("interface_value")
        for breakout_db in db_info.get("breakout_info", {}).get(
                "interface", ()):
            base_interface = self._convert_ifname(
                breakout_db.get("base-interface"),
                ec_message, self._if_type_phy)
            speed = breakout_db.get("speed")
            breakout_num = breakout_db.get("breakout-num")
            json["device"]["breakout-interface"].append(
                {"base-interface": base_interface,
                 "speed": speed,
                 "breakout-num": breakout_num})

    @decorater_log
    def _gen_json_internal_phys(self, json, db_info, ec_message):
        '''
            Set the Internal Link Information (Physical) to the EC message storage dictionary object
            to be used for restoration based on EC message for restoration expansion/"recover service"
            and DB information
            Explanation about parameter：
                json：EC message storage dictionary object
                db_info : DB information
                ec_message : EC message for restoration expansion/"recover service"
        '''
        for internal_if_db in db_info.get("internal-link", ()):
            if internal_if_db.get("if_type") == self._if_type_phy_num:
                name = self._convert_ifname(
                    internal_if_db.get("if_name"),
                    ec_message, self._if_type_phy)
                opposite_node_name = self._get_opposite_node_name(
                    name, ec_message)

                vlan_id = internal_if_db.get("vlan_id")
                address = internal_if_db.get("ip_address")
                prefix = internal_if_db.get("ip_prefix")
                cost = internal_if_db.get("cost", 100)
                if not cost:
                    cost = 100
                json["device"]["internal-physical"].append(
                    {"name": name,
                     "opposite-node-name": opposite_node_name,
                     "vlan-id": vlan_id,
                     "address": address,
                     "prefix": prefix,
                     "cost": cost})
        json["device"]["internal-physical_value"] = \
            len(json["device"]["internal-physical"])

    @decorater_log
    def _gen_json_internal_lag(self, json, db_info, ec_message):
        '''
            Set the Internal Link Information (LAG) to the EC message storage dictionary object
            to be used for restoration based on EC message for restoration expansion/"recover service"
            and DB information
            Explanation about parameter：
                json：EC message storage dictionary object
                db_info : DB information
                ec_message : EC message for restoration expansion/"recover service"
        '''
        for internal_if_db in db_info.get("internal-link", ()):
            if internal_if_db.get("if_type") == self._if_type_lag_num:
                internal_lag = \
                    {
                        "name": None,
                        "opposite-node-name": None,
                        "lag-id": None,
                        "vlan-id": None,
                        "minimum-links": 0,
                        "link-speed": None,
                        "address": None,
                        "prefix": 0,
                        "cost": None,
                        "internal-interface_value": 0,
                        "internal-interface": []
                    }
                name = self._convert_ifname(
                    internal_if_db.get("if_name"),
                    ec_message, self._if_type_lag)
                opposite_node_name = self._get_opposite_node_name(
                    name, ec_message)

                internal_lag["name"] = name
                internal_lag["opposite-node-name"] = opposite_node_name
                internal_lag["lag-id"] = internal_if_db.get("lag_if_id")
                internal_lag["vlan-id"] = internal_if_db.get("vlan_id")
                internal_lag[
                    "minimum-links"] = internal_if_db.get("member_value")
                internal_lag["link-speed"] = internal_if_db.get("speed")
                internal_lag["address"] = internal_if_db.get("ip_address")
                internal_lag["prefix"] = internal_if_db.get("ip_prefix")
                cost = internal_if_db.get("cost", 100)
                if not cost:
                    cost = 100
                internal_lag["cost"] = cost

                for lag_mem_db in internal_if_db.get("member", ()):
                    member_if_name = self._convert_ifname(
                        lag_mem_db.get("if_name"),
                        ec_message, self._if_type_phy)
                    internal_interface = {"name": member_if_name}
                    internal_lag[
                        "internal-interface"].append(internal_interface)
                internal_lag[
                    "internal-interface_value"] = \
                    len(internal_lag["internal-interface"])

                json["device"]["internal-lag"].append(internal_lag)

        json["device"][
            "internal-lag_value"] = len(json["device"]["internal-lag"])

    @decorater_log
    def _get_opposite_node_name(self, if_name, ec_message):
        '''
            Obtain opposite device name based on EC message for restoration expansion/"recover service"
            and DB information
            Explanation about parameter：
　　　　　　　　if_name : internal link IF name after recovery
                ec_message : EC message for restoration expansion/"recover service"    
        '''
        opposite_node_name = "Recover"

        ec_internal_if_nodes = ec_message.get(
            "device").get("internal-interface", [])
        if ec_internal_if_nodes:
            for ec_internal_if_node in ec_internal_if_nodes:
                ec_internal_if_name = ec_internal_if_node.get("name")
                if if_name == ec_internal_if_name:
                    opposite_node_name = ec_internal_if_node.get(
                        "opposite-node-name")
        return opposite_node_name

    @decorater_log
    def _gen_json_management(self, json, db_info, ec_message):
        '''
            Set the Management IF to the EC message storage dictionary object
            to be used for restoration based on EC message for restoration expansion/"recover service"
            and DB information
            Explanation about parameter：
                json：EC message storage dictionary object
                db_info : DB information
                ec_message : EC message for restoration expansion/"recover service"
        '''
        tmp = db_info.get("device").get("management_if")
        json["device"]["management-interface"]["address"] = tmp.get("address")
        json["device"]["management-interface"]["prefix"] = tmp.get("prefix")

    @decorater_log
    def _gen_json_loopback(self, json, db_info, ec_message):
        '''
            Set the Loopback IF to the EC message storage dictionary object
            to be used for restoration based on EC message for restoration expansion/"recover service"
            and DB information
            Explanation about parameter：
                json：EC message storage dictionary object
                db_info : DB information
                ec_message : EC message for restoration expansion/"recover service"
        '''
        tmp = db_info.get("device").get("loopback_if")
        json["device"]["loopback-interface"]["address"] = tmp.get("address")
        json["device"]["loopback-interface"]["prefix"] = tmp.get("prefix")

    @decorater_log
    def _gen_json_snmp(self, json, db_info, ec_message):
        '''
            Set the SNMP server information to the EC message storage dictionary object
            to be used for restoration based on EC message for restoration expansion/"recover service"
            and DB information
            Explanation about parameter：
                json：EC message storage dictionary object
                db_info : DB information
                ec_message : EC message for restoration expansion/"recover service"
        '''
        tmp = db_info.get("device").get("snmp")
        json["device"]["snmp"]["server-address"] = tmp.get("address")
        json["device"]["snmp"]["community"] = tmp.get("community")

    @decorater_log
    def _gen_json_ntp(self, json, db_info, ec_message):
        '''
            Set the NTP server information to the EC message storage dictionary object
            to be used for restoration based on EC message for restoration expansion/"recover service"
            and DB information
            Explanation about parameter：
                json：EC message storage dictionary object
                db_info : DB information
                ec_message : EC message for restoration expansion/"recover service"
        '''
        tmp = db_info.get("device").get("ntp")
        json["device"]["ntp"]["server-address"] = tmp.get("address")

    @decorater_log
    def _gen_json_ospf(self, json, db_info, ec_message):
        '''
            Set the OSPF information to the EC message storage dictionary object
            to be used for restoration based on EC message for restoration expansion/"recover service"
            and DB information
            Explanation about parameter：
                json：EC message storage dictionary object
                db_info : DB information
                ec_message : EC message for restoration expansion/"recover service"
        '''
        ospf_db = db_info.get("device").get("ospf")

        json["device"]["ospf"]["area-id"] = ospf_db.get("area_id")

        router_id = ospf_db.get("virtual_link").get("router_id")
        address = ospf_db.get("range").get("address")
        prefix = ospf_db.get("range").get("prefix")

        if router_id is not None:
            json["device"]["ospf"]["virtual-link"]["router-id"] = router_id
        else:
            if json["device"]["ospf"].get("virtual-link") is not None:
                del json["device"]["ospf"]["virtual-link"]
        if address is not None:
            json["device"]["ospf"]["range"]["address"] = address
        if prefix is not None:
            json["device"]["ospf"]["range"]["prefix"] = prefix

    @decorater_log
    def _gen_json_vpn(self, json, db_info, ec_message):
        '''
            Set the VPN information to the EC message storage dictionary object
            to be used for restoration based on EC message for restoration expansion/"recover service"
            and DB information
            Explanation about parameter：
                json：EC message storage dictionary object
                db_info : DB information
                ec_message : EC message for restoration expansion/"recover service"
        '''
        bgp_neighbor = db_info.get("l3_vpn_bgpbasic")

        if db_info.get("device").get("vpn_type") == self._slice_type_l2:
            vpn = "l2-vpn"
        elif db_info.get("device").get("vpn_type") == self._slice_type_l3:
            vpn = "l3-vpn"
        else:
            vpn = None

        if vpn is not None:
            device_json_message = {
                vpn: {
                    "bgp": [],
                    "as": {
                        "as-number": 0
                    }
                }
            }
            bgp_message = {
                "neighbor": [],
                "community": None,
                "community-wildcard": None
            }
            for neighbor in bgp_neighbor.get("neighbor", ()):
                neighbor_addr = neighbor.get("neighbor", {}).get("address")
                bgp_message["neighbor"].append({"address": neighbor_addr})
            community = bgp_neighbor.get("bgp_community").get("value")
            community_wildcard = bgp_neighbor.get(
                "bgp_community").get("wildcard")
            bgp_message["community"] = community
            bgp_message["community-wildcard"] = community_wildcard
            device_json_message[vpn]["bgp"] = bgp_message
            device_json_message[vpn]["as"]["as-number"] = db_info.get(
                "device").get("as_number")
            json["device"].update(device_json_message)

    @decorater_log
    def _gen_json_slice_name(self, json, db_info, ec_message, slice_name):
        '''
            Set the Slice name to the EC message storage dictionary object
            to be used for restoration based on EC message for restoration expansion/"recover service"
            and DB information
            Explanation about parameter：
                json：EC message storage dictionary object
                db_info : DB information
                ec_message : EC message for restoration expansion/"recover service"
                slice_name : Slice name to be recovered
        '''
        json["device-leaf"]["slice_name"] = slice_name

    @decorater_log
    def _gen_json_vrf(self, json, db_info, ec_message, slice_name,
                      slice_type=GlobalModule.SERVICE_L3_SLICE):
        '''
            Set the VRF information to the EC message storage dictionary object
            to be used for restoration based on EC message for restoration expansion/"recover service"
            and DB information
            Explanation about parameter：
                json：EC message storage dictionary object
                db_info : DB information
                ec_message : EC message for restoration expansion/"recover service"
                slice_name : Slice name to be recovered
        '''
        db_info = db_info.get(slice_type)
        tmp_vrf = {}
        for vrf in db_info.get("vrf_detail", ()):
            if vrf.get("slice_name") == slice_name:
                json["device-leaf"]["vrf"]["vrf-name"] = vrf.get("vrf_name")
                json["device-leaf"]["vrf"]["rt"] = vrf.get("rt")
                json["device-leaf"]["vrf"]["rd"] = vrf.get("rd")
                json["device-leaf"]["vrf"]["router-id"] = vrf.get("router_id")
                tmp_vrf = vrf
                break
        if slice_type == self.name_l2_slice:
            self._gen_json_vrf_l2(json, tmp_vrf, db_info, slice_name)

        if not json["device-leaf"]["vrf"].get("vrf-name", ()):
            del json["device-leaf"]["vrf"]

    @decorater_log
    def _gen_json_vrf_l2(self, json, vrf_detail_info, db_info, slice_name):
        '''
            Set the VRF information to the EC message storage dictionary object
            to be used for restoration based on EC message for restoration expansion/"recover service"
            and DB information
            Explanation about parameter：
                json：EC message storage dictionary object
                vrf_detail_info  : DB information（VRF information）
                db_info : DB information
                slice_name : Slice name to be recovered
        '''
        tmp_vrf_info = copy.deepcopy(vrf_detail_info)
        if not json["device-leaf"]["vrf"].get("vrf-name", ()):
            for dummy_cp in db_info.get("dummy_cp", ()):
                if dummy_cp.get("slice_name") == slice_name:
                    tmp_vrf_info = copy.deepcopy(dummy_cp)
                    json["device-leaf"]["vrf"]["vrf-name"] = \
                        tmp_vrf_info.get("vrf_name")
                    json["device-leaf"]["vrf"]["rt"] = tmp_vrf_info.get("rt")
                    json["device-leaf"]["vrf"]["rd"] = tmp_vrf_info.get("rd")
                    json["device-leaf"]["vrf"]["router-id"] = \
                        tmp_vrf_info.get("router_id")

        json["device-leaf"]["vrf"]["vrf-id"] = tmp_vrf_info.get("vrf_id")

        lp_info = \
            {
                "address": None,
                "prefix": 0
            }
        lp_info["address"] = tmp_vrf_info.get("loopback", {}).get("address")
        lp_info["prefix"] = tmp_vrf_info.get("loopback", {}).get("prefix")
        json["device-leaf"]["vrf"]["loopback"] = lp_info

        l3_vni_info = \
            {
                "vni-id": 0,
                "vlan-id": 0
            }
        l3_vni_info["vni-id"] = tmp_vrf_info.get("l3_vni", {}).get("vni")
        l3_vni_info["vlan-id"] = tmp_vrf_info.get("l3_vni", {}).get("vlan_id")
        json["device-leaf"]["vrf"]["l3-vni"] = l3_vni_info

    @decorater_log
    def _create_qos_info(self, cp_info, ec_message):
        '''
            Create QoS information used for restoration EC message based on CP information of DB
            Explanation about parameter：
                cp_info : CP information (DB)
                ec_message : EC message for restoration expansion/"recover service"
        Return Value :
            Result : QoS information used for restoration EC message (dict)
        '''
        db_qos = cp_info.get("qos", {})
        ec_qos = ec_message.get("device", {}).get("qos", {})

        return_qos = {
            "inflow-shaping-rate": None,
            "outflow-shaping-rate": None,
            "remark-menu": None,
            "egress-menu": None
        }

        inflow_shaping_rate = ec_qos.get("inflow-shaping-rate")
        if inflow_shaping_rate:
            if inflow_shaping_rate.get("operation") != "delete":
                return_qos[
                    "inflow-shaping-rate"] = inflow_shaping_rate.get("value")
        else:
            return_qos[
                "inflow-shaping-rate"] = db_qos.get("inflow_shaping_rate")

        outflow_shaping_rate = ec_qos.get("outflow-shaping-rate")
        if outflow_shaping_rate:
            if outflow_shaping_rate.get("operation") != "delete":
                return_qos[
                    "outflow-shaping-rate"] = outflow_shaping_rate.get("value")
        else:
            return_qos[
                "outflow-shaping-rate"] = db_qos.get("outflow_shaping_rate")

        remark_menu = ec_qos.get("remark-menu")
        if remark_menu:
            if remark_menu.get("operation") != "delete":
                return_qos["remark-menu"] = remark_menu.get("value")
        else:
            return_qos["remark-menu"] = db_qos.get("remark_menu")

        egress_menu = ec_qos.get("egress-menu")
        if egress_menu:
            if egress_menu.get("operation") != "delete":
                return_qos["egress-menu"] = egress_menu.get("value")
        else:
            return_qos["egress-menu"] = db_qos.get("egress_queue_menu")

        return return_qos

    @decorater_log
    def _convert_ifname(self, old_ifname, recover_ec_message, if_type="all"):
        '''
        In accordance with the interface name conversion table,
        the interface name before the restoration is converted
        into the interface name after restoration.
        Parameter:
            old_ifname : IF name before restoration
            recover_ec_message : EC message for restoration expansion/"recover service"（IF Name Conversion Table）
            if_type : IF type
        Return Value :
            IF name after restoration
        Exception :
            ValueError : Conversion failed
        '''
        converted_if_name = None
        if if_type == self._if_type_phy or if_type == "all":
            for if_info in recover_ec_message.get(
                    "device").get("physical-ifs", []):
                if if_info.get("old-name") == old_ifname:
                    converted_if_name = if_info.get("name")
                    break
        if converted_if_name is None and \
                (if_type == self._if_type_lag or if_type == "all"):
            for if_info in recover_ec_message.get("device").get("lag-ifs", []):
                if if_info.get("old-name") == old_ifname:
                    converted_if_name = if_info.get("name")
                    break
        if converted_if_name is None:
            self.common_util_log.logging(
                " ", self.log_level_debug,
                "if convert error. old_name=%s" % old_ifname,
                __name__)
            raise ValueError(old_ifname + " " + if_type)
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "if convert success. old_name=%s new_name=%s" %
            (old_ifname, converted_if_name), __name__)
        return converted_if_name
