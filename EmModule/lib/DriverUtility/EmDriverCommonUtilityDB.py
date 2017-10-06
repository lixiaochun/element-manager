# -*- coding: utf-8 -*-
import json
import GlobalModule
from EmCommonLog import decorater_log


class EmDriverCommonUtilityDB(object):

    __name_spine = "spine"
    __name_leaf = "leaf"
    __name_l2_slice = "l2-slice"
    __name_l3_slice = "l3-slice"
    __name_ce_lag = "ce-lag"
    __name_internal_lag = "internal-lag"

    @decorater_log
    def __init__(self):
        self.__get_functions = {
            self.__name_spine: (self.__get_spine_info,
                                self.__json_spine),
            self.__name_leaf: (self.__get_leaf_info,
                               self.__json_leaf),
            self.__name_l2_slice: (self.__get_l2_slice_info,
                                   self.__json_l2_slice),
            self.__name_l3_slice: (self.__get_l3_slice_info,
                                   self.__json_l3_slice),
            self.__name_ce_lag: (self.__get_ce_lag_info,
                                 self.__json_ce_lag),
            self.__name_internal_lag: (self.__get_internal_lag_info,
                                       self.__json_internal_lag)
        }
        self.device_types = {1: self.__name_spine,
                             2: self.__name_leaf}

    @decorater_log
    def read_configureddata_info(self, device_name, service_name):
        if service_name not in self.__get_functions:
            GlobalModule.EM_LOGGER.warning(
                "1 208001 Service Classification Error")
            return False, None

        get_db_func, conv_json_func = self.__get_functions[service_name]

        json_text = None
        is_result, edit_info = get_db_func(device_name)
        if is_result:
            is_data = False
            for t_table in edit_info.values():
                if t_table is not None and len(t_table) > 0:
                    is_data = True
                    break
            if is_data:
                json_text = conv_json_func(edit_info)
            else:
                json_text = None
        else:
            GlobalModule.EM_LOGGER.warning(
                "2 208002 Get Information Error")

        GlobalModule.EM_LOGGER.debug(
            "DB RESULT : is_result = %s , edit_info = %s ,json_text = %s" %
            (is_result, edit_info, json_text))

        return is_result, json_text

    @staticmethod
    @decorater_log
    def __get_spine_info(device_name):
        spine_info = {}

        is_db_info, tmp_db_info = \
            GlobalModule.DB_CONTROL.read_device_regist_info(
                device_name=device_name)
        if is_db_info is False:
            return False, {"ERROR ! FAULT DB": "DeviceRegistrationInfo"}
        is_db_info, tmp_db_info = GlobalModule.DB_CONTROL.read_lagif_info(
            device_name=device_name)
        if is_db_info is False:
            return False, {"ERROR ! FAULT DB": "LagIfInfo"}
        is_db_info, tmp_db_info = \
            GlobalModule.DB_CONTROL.read_lagmemberif_info(
                device_name=device_name)
        if is_db_info is False:
            return False, {"ERROR ! FAULT DB": "LagMemberIfInfo"}

        return True, spine_info

    @staticmethod
    @decorater_log
    def __get_leaf_info(device_name):
        leaf_info = {}

        is_db_info, tmp_db_info = \
            GlobalModule.DB_CONTROL.read_device_regist_info(
                device_name=device_name)
        if is_db_info is False:
            return False, {"ERROR ! FAULT DB": "DeviceRegistrationInfo"}

        is_db_info, tmp_db_info = GlobalModule.DB_CONTROL.read_lagif_info(
            device_name=device_name)
        if is_db_info is False:
            return False, {"ERROR ! FAULT DB": "LagIfInfo"}

        is_db_info, tmp_db_info = \
            GlobalModule.DB_CONTROL.read_lagmemberif_info(
                device_name=device_name)
        if is_db_info is False:
            return False, {"ERROR ! FAULT DB": "LagMemberIfInfo"}

        is_db_info, tmp_db_info = \
            GlobalModule.DB_CONTROL.read_l3vpn_leaf_bgp_basic_info(
                device_name=device_name)
        if is_db_info is False:
            return False, {"ERROR ! FAULT DB": "L3VpnLeafBgpBasicInfo"}

        return True, leaf_info

    @staticmethod
    @decorater_log
    def __get_l2_slice_info(device_name):
        l2_slice_info = {}

        is_db_info, tmp_db_info = GlobalModule.DB_CONTROL.read_cp_info(
            device_name=device_name)
        if is_db_info is False:
            return False, {"ERROR ! FAULT DB": "CpInfo"}

        return True, l2_slice_info

    @staticmethod
    @decorater_log
    def __get_l3_slice_info(device_name):
        l3_slice_info = {}
        db_control_method = {
                GlobalModule.DB_CONTROL.read_device_regist_info,
                GlobalModule.DB_CONTROL.read_static_route_detail_info
        }

        for key in db_control_method.keys():
            is_db_info, tmp_db_info = \
                db_control_method[key](device_name=device_name)
            if is_db_info is False:
                return False, {"ERROR ! FAULT DB": key}
            l3_slice_info[key] = tmp_db_info

        return True, l3_slice_info

    @staticmethod
    @decorater_log
    def __get_ce_lag_info(device_name):
        ce_lag_info = {}

        is_db_info, tmp_db_info = GlobalModule.DB_CONTROL.read_lagif_info(
            device_name=device_name)
        if is_db_info is False:
            return False, {"ERROR ! FAULT DB": "LagIfInfo"}

        is_db_info, tmp_db_info = \
            GlobalModule.DB_CONTROL.read_lagmemberif_info(
                device_name=device_name)
        if is_db_info is False:
            return False, {"ERROR ! FAULT DB": "LagMemberIfInfo"}
        if LagIfInfo is not None and type(LagIfInfo) is tuple:
            for element in LagIfInfo[:]:
                if lag_type is not None and lag_type != 2:
                    LagIfInfo_tmp = list(LagIfInfo)
                    LagIfInfo_tmp.remove(element)
                    LagIfInfo = tuple(LagIfInfo_tmp)

        return True, ce_lag_info

    @staticmethod
    @decorater_log
    def __get_internal_lag_info(device_name):
        internal_lag_info = {}

        is_db_info, tmp_db_info = \
            GlobalModule.DB_CONTROL.read_device_regist_info(
                device_name=device_name)
        if is_db_info is False:
            return False, {"ERROR ! FAULT DB": "DeviceRegistrationInfo"}

        is_db_info, tmp_db_info = GlobalModule.DB_CONTROL.read_lagif_info(
            device_name=device_name)
        if is_db_info is False:
            return False, {"ERROR ! FAULT DB": "LagIfInfo"}

        is_db_info, tmp_db_info = \
            GlobalModule.DB_CONTROL.read_lagmemberif_info(
                device_name=device_name)
        if is_db_info is False:
            return False, {"ERROR ! FAULT DB": "LagMemberIfInfo"}
        if LagIfInfo is not None and type(LagIfInfo) is tuple:
            for element in LagIfInfo[:]:
                if lag_type is not None and lag_type != 1:
                    LagIfInfo_tmp = list(LagIfInfo)
                    LagIfInfo_tmp.remove(element)
                    LagIfInfo = tuple(LagIfInfo_tmp)

        return True, internal_lag_info

    @staticmethod
    @decorater_log
    def __json_spine(db_info):
        json_spine = {}

        if len(db_info["DeviceRegistrationInfo"]) > 0:
            t_table = db_info["DeviceRegistrationInfo"][0]
        else:
            t_table = {}

        json_item = {}
        json_item["device_name"] = t_table.get("device_name")
        json_item["management_if"] = \
            {"address": t_table.get("mgmt_if_address"),
             "prefix": t_table.get("mgmt_if_prefix")}
        json_item["loopback_if"] = \
            {"address": t_table.get("loopback_if_address"),
             "prefix": t_table.get("loopback_if_prefix")}
        json_item["snmp"] = {"address": t_table.get("snmp_server_address"),
                             "community": t_table.get("snmp_community")}
        json_item["ntp"] = {"address": t_table.get("ntp_server_address")}
        json_item["msdp"] = \
            {"peer_address": t_table.get("msdp_peer_address"),
             "local_address": t_table.get("msdp_local_address")}
        json_item["rp_other"] = {
            "address": t_table.get("pim_other_rp_address")}
        json_item["rp_self"] = {"address": t_table.get("pim_self_rp_address")}
        json_spine["device"] = json_item

        t_table = db_info["LagIfInfo"]
        json_list_item = []
        json_spine["lag_value"] = len(t_table)
        for row in t_table:
            json_item = {}
            json_item["if_name"] = row["lag_if_name"]
            json_item["links"] = row["minimum_links"]
            json_item["link_speed"] = row["link_speed"]
            json_item["internal_link"] = \
                {"address": row["internal_link_ip_address"],
                 "prefix": row["internal_link_ip_prefix"]}
            json_list_item.append(json_item)
        json_spine["lag"] = json_list_item

        t_table = db_info["LagMemberIfInfo"]
        json_list_item = []
        json_spine["lag_member_value"] = len(t_table)
        for row in t_table:
            json_item = {}
            json_item["lag_if_name"] = row["lag_if_name"]
            json_item["if_name"] = row["if_name"]
            json_list_item.append(json_item)
        json_spine["lag_member"] = json_list_item

        json_spine["device_count"] = json_spine["lag_value"] + 1

        return json.dumps(json_spine)

    @staticmethod
    @decorater_log
    def __json_leaf(db_info):
        json_return = {}

        if len(db_info["DeviceRegistrationInfo"]) > 0:
            t_table = db_info["DeviceRegistrationInfo"][0]
        else:
            t_table = {}

        json_item = {}
        json_item["device_name"] = t_table.get("device_name")
        json_item["management_if"] = \
            {"address": t_table.get("mgmt_if_address"),
             "prefix": t_table.get("mgmt_if_prefix")}
        json_item["loopback_if"] = \
            {"address": t_table.get("loopback_if_address"),
             "prefix": t_table.get("loopback_if_prefix")}
        json_item["snmp"] = {"address": t_table.get("snmp_server_address"),
                             "community": t_table.get("snmp_community")}
        json_item["ntp"] = {"address": t_table.get("ntp_server_address")}
        json_item["as_number"] = t_table.get("as_number")
        json_item["rp"] = {"address": t_table.get("pim_rp_address")}
        json_return["device"] = json_item

        t_table = db_info["LagIfInfo"]
        json_list_item = []
        json_return["lag_value"] = len(t_table)
        for row in t_table:
            json_item = {}
            json_item["if_name"] = row["lag_if_name"]
            json_item["links"] = row["minimum_links"]
            json_item["link_speed"] = row["link_speed"]
            json_item["internal_link"] = \
                {"address": row["internal_link_ip_address"],
                 "prefix": row["internal_link_ip_prefix"]}
            json_list_item.append(json_item)
        json_return["lag"] = json_list_item

        t_table = db_info["LagMemberIfInfo"]
        json_list_item = []
        json_return["lag_member_value"] = len(t_table)
        for row in t_table:
            json_item = {}
            json_item["lag_if_name"] = row["lag_if_name"]
            json_item["if_name"] = row["if_name"]
            json_list_item.append(json_item)
        json_return["lag_member"] = json_list_item


        t_table = db_info["L3VpnLeafBgpBasicInfo"]
        json_item = {}
        json_list_item = []
        for row in t_table:
            json_list_item.append({"address": row["neighbor_ipv4"]})
        json_item["neighbor_value"] = len(t_table)
        if len(t_table) > 0:
            t_table = db_info["L3VpnLeafBgpBasicInfo"][0]
        else:
            t_table = {}
        json_item["neighbor"] = json_list_item
        json_item["bgp_community"] = \
            {"value": t_table.get("bgp_community_value"),
             "wildcard": t_table.get("bgp_community_wildcard")}

        json_return["l3_vpn_bgpbasic"] = json_item

        json_return["device_count"] = json_return["lag_value"] + 1

        return json.dumps(json_return)

    port_mode_text = {1: "access", 2: "trunk"}

    @decorater_log
    def __json_l2_slice(self, db_info):
        json_return = {}
        t_table = db_info["CpInfo"]

        json_list_item = []
        json_return["cp_value"] = len(t_table)
        for row in t_table:
            json_item = {}
            json_item["device_name"] = row["device_name"]
            json_item["slice_name"] = row["slice_name"]
            json_item["if_name"] = row["if_name"]
            json_item["vlan"] = \
                {"vlan_id": row["vlan_id"],
                 "port_mode": self.port_mode_text.get(row["port_mode"])}
            json_item["vxlan"] = {"vni": row["vni"],
                                  "mc_group": row["multicast_group"]}
            json_list_item.append(json_item)
        json_return["cp"] = json_list_item

        return json.dumps(json_return)

    @decorater_log
    def __json_l3_slice(self, db_info):
        json_return = {}

        if len(db_info["DeviceRegistrationInfo"]) > 0:
            t_table = db_info["DeviceRegistrationInfo"][0]
        else:
            t_table = {}
        json_item = {}
        json_item["device_name"] = t_table.get("device_name")
        json_item["as_number"] = t_table.get("as_number")
        json_return["device"] = json_item

        t_table = db_info["CpInfo"]
        json_list_item = []
        json_return["cp_value"] = len(t_table)
        for row in t_table:
            json_item = {}
            json_item["if_name"] = row["if_name"]
            json_item["slice_name"] = row["slice_name"]
            json_item["vlan"] = {"vlan_id": row["vlan_id"],
                                 "port_mode":
                                 self.port_mode_text.get(row["port_mode"])}
            json_item["ce_ipv4"] = {"address": row["ipv4_address"],
                                    "prefix": row["ipv4_prefix"]}
            json_item["ce_ipv6"] = {"address": row["ipv6_address"],
                                    "prefix": row["ipv6_prefix"]}
            json_item["mtu_size"] = row["mtu_size"]
            json_item["metric"] = row["metric"]
            json_item["protocol_flags"] = {"bgp": row["bgp_flag"],
                                           "ospf": row["ospf_flag"],
                                           "static": row["static_flag"],
                                           "direct": row["direct_flag"],
                                           "vrrp": row["vrrp_flag"]}
            json_list_item.append(json_item)
        json_return["cp"] = json_list_item

        t_table = db_info["VrfDetailInfo"]
        json_list_item = []
        json_return["vrf_detail_value"] = len(t_table)
        for row in t_table:
            json_item = {}
            json_item["if_name"] = row["if_name"]
            json_item["vlan_id"] = row["vlan_id"]
            json_item["vrf_name"] = row["vrf_name"]
            json_item["rt"] = row["rt"]
            json_item["rd"] = row["rd"]
            json_item["router_id"] = row["router_id"]
            json_list_item.append(json_item)
        json_return["vrf_detail"] = json_list_item

        t_table = db_info["VrrpDetailInfo"]
        json_list_item = []
        json_return["vrrp_detail_value"] = len(t_table)
        for row in t_table:
            json_item = {}
            json_item["if_name"] = row["if_name"]
            json_item["vlan_id"] = row["vlan_id"]
            json_item["gropu_id"] = row["vrrp_group_id"]
            json_item["virtual"] = \
                {"ipv4_address": row["virtual_ipv4_address"],
                 "ipv6_address": row["virtual_ipv6_address"]}
            json_item["priority"] = row["priority"]
            json_item["track_if_name"] = None
            tmp_list = []
            for tr_name in db_info["VrrpTrackIfInfo"]:
                if tr_name["vrrp_group_id"] == row["vrrp_group_id"]:
                    tmp_list.append(tr_name["track_if_name"])
            json_item["track_if_name"] = tmp_list
            json_list_item.append(json_item)
        json_return["vrrp_detail"] = json_list_item

        t_table = db_info["BgpDetailInfo"]
        json_list_item = []
        json_return["bgp_detail_value"] = len(t_table)
        for row in t_table:
            json_item = {}
            json_item["if_name"] = row["if_name"]
            json_item["vlan_id"] = row["vlan_id"]
            json_item["slice_name"] = row["slice_name"]
            json_item["as_number"] = row["remote_as_number"]
            json_item["remote"] = \
                {"ipv4_address": row["remote_ipv4_address"],
                 "ipv6_address": row["remote_ipv6_address"]}
            json_item["local"] = \
                {"ipv4_address": row["local_ipv4_address"],
                 "ipv6_address": row["local_ipv6_address"]}
            json_list_item.append(json_item)
        json_return["bgp_detail"] = json_list_item

        t_table = db_info["StaticRouteDetailInfo"]
        static = {"if_name": None, "vlan_id": None,
                  "ipv4": {"address": None, "prefix": None, "nexthop": None},
                  "ipv6": {"address": None, "prefix": None, "nexthop": None}}
        json_list_item = []
        json_return["static_detail_value"] = len(t_table)
        for row in t_table:
            json_item = static.copy()
            json_item["if_name"] = row["if_name"]
            json_item["vlan_id"] = row["vlan_id"]
            if row["address_type"] == 4:
                json_item["ipv4"] = {"address": row["address"],
                                     "prefix": row["prefix"],
                                     "nexthop": row["nexthop"]}
            elif row["address_type"] == 6:
                json_item["ipv6"] = {"address": row["address"],
                                     "prefix": row["prefix"],
                                     "nexthop": row["nexthop"]}
            json_list_item.append(json_item)
        json_return["static_detail"] = json_list_item

        return json.dumps(json_return)

    @staticmethod
    @decorater_log
    def __json_ce_lag(db_info):
        json_return = {}

        if len(db_info["LagIfInfo"]) > 0:
            json_return["device"] = {
                "device_name": db_info["LagIfInfo"][0]["device_name"]}
        else:
            json_return["device"] = {
                "device_name": db_info["LagMemberIfInfo"][0]["device_name"]}

        t_table = db_info["LagIfInfo"]
        json_list_item = []
        json_return["lag_value"] = len(t_table)
        for row in t_table:
            json_item = {}
            json_item["if_name"] = row["lag_if_name"]
            json_item["links"] = row["minimum_links"]
            json_item["link_speed"] = row["link_speed"]
            json_item["internal_link"] = \
                {"address": row["internal_link_ip_address"],
                 "prefix": row["internal_link_ip_prefix"]}
            json_list_item.append(json_item)
        json_return["lag"] = json_list_item

        t_table = db_info["LagMemberIfInfo"]
        json_list_item = []
        json_return["lag_member_value"] = len(t_table)
        for row in t_table:
            json_item = {}
            json_item["lag_if_name"] = row["lag_if_name"]
            json_item["if_name"] = row["if_name"]
            json_list_item.append(json_item)
        json_return["lag_member"] = json_list_item

        return json.dumps(json_return)

    @decorater_log
    def __json_internal_lag(self, db_info):

        json_return = {}

        t_table = db_info["DeviceRegistrationInfo"][0]
        json_return["device"] = {
            "device_name": t_table.get("device_name"),
            "device_type": self.device_types.get(t_table.get("device_type")),
            "pim_other_rp_address": t_table.get("pim_other_rp_address")}

        t_table = db_info["LagIfInfo"]
        json_list_item = []
        json_return["lag_value"] = len(t_table)
        for row in t_table:
            json_item = {}
            json_item["if_name"] = row["lag_if_name"]
            json_item["links"] = row["minimum_links"]
            json_item["link_speed"] = row["link_speed"]
            json_item["internal_link"] = \
                {"address": row["internal_link_ip_address"],
                 "prefix": row["internal_link_ip_prefix"]}
            json_list_item.append(json_item)
        json_return["lag"] = json_list_item

        t_table = db_info["LagMemberIfInfo"]
        json_list_item = []
        json_return["lag_member_value"] = len(t_table)
        for row in t_table:
            json_item = {}
            json_item["lag_if_name"] = row["lag_if_name"]
            json_item["if_name"] = row["if_name"]
            json_list_item.append(json_item)
        json_return["lag_member"] = json_list_item

        return json.dumps(json_return)
