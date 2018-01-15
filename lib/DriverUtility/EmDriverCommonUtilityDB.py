#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2017 Nippon Telegraph and Telephone Corporation
# Filename: EmDriverCommonUtilityDB.py
'''
Common utility (DB) module for the driver.
'''
import json
import GlobalModule
from EmCommonLog import decorater_log


class EmDriverCommonUtilityDB(object):
    '''
    Common utility (DB) class of driver.
    '''

    _table_device = "DeviceRegistrationInfo"
    _table_lag_if = "LagIfInfo"
    _table_lag_mem = "LagMemberIfInfo"
    _table_phy_if = "PhysicalIfInfo"
    _table_inner_link = "InnerLinkIfInfo"
    _table_cluster_link = "ClusterLinkIfInfo"
    _table_breakout = "BreakoutIfInfo"
    _table_l3vpn_bgp = "L3VpnLeafBgpBasicInfo"
    _table_vlan_if = "VlanIfInfo"
    _table_vrf = "VrfDetailInfo"
    _table_bgp = "BgpDetailInfo"
    _table_static = "StaticRouteDetailInfo"
    _table_vrrp = "VrrpDetailInfo"
    _table_vrrp_track = "VrrpTrackIfInfo"

    _if_type_physical = 1
    _if_type_lag = 2
    _if_type_breakout = 1

    @decorater_log
    def __init__(self):
        '''
        Constructor.
        '''
        self._name_spine = GlobalModule.SERVICE_SPINE
        self._name_leaf = GlobalModule.SERVICE_LEAF
        self._name_l2_slice = GlobalModule.SERVICE_L2_SLICE
        self._name_l3_slice = GlobalModule.SERVICE_L3_SLICE
        self._name_ce_lag = GlobalModule.SERVICE_CE_LAG
        self._name_internal_link = GlobalModule.SERVICE_INTERNAL_LINK
        self._name_b_leaf = GlobalModule.SERVICE_B_LEAF
        self._name_breakout = GlobalModule.SERVICE_BREAKOUT
        self._name_cluster_link = GlobalModule.SERVICE_CLUSTER_LINK

        self._get_functions = {
            self._name_spine: (self._get_spine_info,
                               self._json_spine),
            self._name_leaf: (self._get_leaf_info,
                              self._json_leaf),
            self._name_l2_slice: (self._get_l2_slice_info,
                                  self._json_l2_slice),
            self._name_l3_slice: (self._get_l3_slice_info,
                                  self._json_l3_slice),
            self._name_ce_lag: (self._get_ce_lag_info,
                                self._json_ce_lag),
            self._name_internal_link: (self._get_internal_link_info,
                                       self._json_internal_link),
            self._name_b_leaf: (self._get_leaf_info,
                                self._json_leaf),
            self._name_breakout: (self._get_breakout_info,
                                  self._json_breakout),
            self._name_cluster_link: (self._get_cluster_link_info,
                                      self._json_cluster_link),
        }

        self._get_db = {
            self._table_device:
            GlobalModule.DB_CONTROL.read_device_regist_info,
            self._table_lag_if:
            GlobalModule.DB_CONTROL.read_lagif_info,
            self._table_lag_mem:
            GlobalModule.DB_CONTROL.read_lagmemberif_info,
            self._table_phy_if:
            GlobalModule.DB_CONTROL.read_physical_if_info,
            self._table_inner_link:
            GlobalModule.DB_CONTROL.read_inner_link_if_info,
            self._table_cluster_link:
            GlobalModule.DB_CONTROL.read_cluster_link_if_info,
            self._table_breakout:
            GlobalModule.DB_CONTROL.read_breakout_if_info,
            self._table_l3vpn_bgp:
            GlobalModule.DB_CONTROL.read_leaf_bgp_basic_info,
            self._table_vlan_if:
            GlobalModule.DB_CONTROL.read_vlanif_info,
            self._table_vrf:
            GlobalModule.DB_CONTROL.read_vrf_detail_info,
            self._table_bgp:
            GlobalModule.DB_CONTROL.read_bgp_detail_info,
            self._table_static:
            GlobalModule.DB_CONTROL.read_static_route_detail_info,
            self._table_vrrp:
            GlobalModule.DB_CONTROL.read_vrrp_detail_info,
            self._table_vrrp_track:
            GlobalModule.DB_CONTROL.read_vrrp_trackif_info,
        }

        self._device_types = {1: self._name_spine, 2: self._name_leaf}

        self._vpn_types = {2: "l2", 3: "l3"}

        self._port_cond = {1: "enable", 0: "disable"}

        self._if_types = {self._if_type_physical: "physical-if",
                          self._if_type_lag: "lag-if", }

        self._port_mode_text = {1: "access", 2: "trunk"}

    @decorater_log
    def read_device_type(self, device_name):
        '''
        Obtain the Device type and VPN type from the device name of the individual section on driver.
        Explanation about parameter:
            device_name: Device_name
        Explanation about return value:
            Device type : str
            VPN type : str
        '''
        db_info = self._get_db_infos(device_name, [self._table_device])
        device = db_info[1][self._table_device][0]
        dev_type_num = device["device_type"]
        dev_type = self._device_types.get(dev_type_num, None)
        vpn_type_num = device["vpn_type"]
        vpn_type = self._vpn_types.get(vpn_type_num, None)
        return dev_type, vpn_type

    @decorater_log
    def read_configureddata_info(self, device_name, service_name):
        '''
        Called out from individual section on driver when message to the device is created.
        Gives the Edit information of the device from DB.  
        Explanation about parameter:
            device_name: Device name
            service_name: Service name
        Explanation about return value:
            Acquisition result : Boolean
            Edit information : {DB name:({Item name:value})}
        '''
        if service_name not in self._get_functions:
            GlobalModule.EM_LOGGER.warning(
                "1 208001 Service Classification Error")
            return False, None

        get_db_func, conv_json_func = self._get_functions[service_name]

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

    @decorater_log
    def _get_db_infos(self, device_name, tables):
        '''
        Obtain the table list data from the DB control. 
        Explanation about parameter:
            device_name: Device name
            tables: Table list (list)
        Explanation about return value:
            Acquisition result : Boolean
            Edit information : {DB name:({Item name: value})}
        '''
        tmp_info = {}
        for table in tables:
            is_ok, tmp_db = self._get_db[table](device_name=device_name)
            if not is_ok:
                return False, {"ERROR ! FAULT DB": table}
            tmp_info[table] = tmp_db
        return True, tmp_info

    @decorater_log
    def _get_spine_info(self, device_name):
        '''
        Obtain the Spine information
            Called out if the Service name is Spine-related when obtaining the Edit information. 
            Explanation about parameter:
            device_name: Device name
        Explanation about return value:
            Acquisition result : Boolean
            Edit information : {DB name:({Item name: value})}
        '''
        get_tables = [self._table_device,
                      self._table_lag_if,
                      self._table_lag_mem,
                      self._table_breakout,
                      self._table_inner_link,
                      self._table_phy_if,
                      ]

        return self._get_db_infos(device_name, get_tables)

    @decorater_log
    def _get_leaf_info(self, device_name):
        '''
        Obtain Leaf information
            Called out if the Service name is Leaf-related when obtaining the Edit information.
        Explanation about parameter:
            device_name: Device name
        Explanation about return value:
            Acquisition result : Boolean
            Edit information : {DB name:({Item name: value})}
        '''
        get_tables = [self._table_device,
                      self._table_lag_if,
                      self._table_lag_mem,
                      self._table_breakout,
                      self._table_l3vpn_bgp,
                      self._table_inner_link,
                      self._table_phy_if,
                      ]

        return self._get_db_infos(device_name, get_tables)

    @decorater_log
    def _get_l2_slice_info(self, device_name):
        '''
        Obtain L2 slice information. 
            Called out if the Service name is L2 slice-related when obtaining the Edit information.
        Explanation about parameter:
            device_name: Device name
        Explanation about return value:
            Acquisition result : Boolean
            Edit information : {DB name:({Item name: value})}
        '''
        get_tables = [self._table_vlan_if,
                      self._table_lag_if,
                      ]

        return self._get_db_infos(device_name, get_tables)

    @decorater_log
    def _get_l3_slice_info(self, device_name):
        '''
        Obtain L3 slice information.
            Called out if the Service name is L3 slice-related when obtaining the Edit information.
        Explanation about parameter:
            device_name: Device name
        Explanation about return value:
            Acquisition result : Boolean
            Edit information : {DB name:({Item name: value})}
        '''
        get_tables = [self._table_device,
                      self._table_vlan_if,
                      self._table_vrf,
                      self._table_bgp,
                      self._table_static,
                      self._table_vrrp,
                      self._table_vrrp_track,
                      ]

        return self._get_db_infos(device_name, get_tables)

    @decorater_log
    def _get_ce_lag_info(self, device_name):
        '''
        Obtain LAG information for CE. 
            Called out if the Service name is related to LAG for CE when obtaining the Edit information.
            Explanation about parameter:
            device_name: Device name
        Explanation about return value:
            Acquisition result : Boolean
            Edit information : {DB name:({Item name: value})}
        '''
        get_tables = [self._table_lag_if,
                      self._table_lag_mem,
                      ]

        return self._get_db_infos(device_name, get_tables)

    @decorater_log
    def _get_internal_link_info(self, device_name):
        '''
        Obtain LAG information for internal Link  
            Called out if the Service name is related to LAG for internal Link when obtaining the Edit information.
            Explanation about parameter:
            device_name: Device name
        Explanation about return value:
            Acquisition result : Boolean
            Edit information : {DB name:({Item name: value})}
        '''
        get_tables = [self._table_device,
                      self._table_lag_if,
                      self._table_lag_mem,
                      self._table_inner_link,
                      ]

        return self._get_db_infos(device_name, get_tables)

    @decorater_log
    def _get_breakout_info(self, device_name):
        '''
        Obtain breakout information
            Called out if the Service name is related to breakout when obtaining the Edit information.
        Explanation about parameter:
            device_name: Device name
        Explanation about return value:
            Acquisition result : Boolean
            Edit information : {DB name:({Item name: value})}
        '''
        get_tables = [self._table_breakout,
                      ]

        return self._get_db_infos(device_name, get_tables)

    @decorater_log
    def _get_cluster_link_info(self, device_name):
        '''
        Obtain Link information among the clusters
            Called out if the Service name is related to Link among the clusters when obtaining the Edit information.
            Explanation about parameter:
            device_name: Device name
        Explanation about return value:
            Acquisition result : Boolean
            Edit information : {DB name:({Item name: value})}
        '''
        get_tables = [self._table_cluster_link,
                      self._table_lag_if,
                      self._table_lag_mem,
                      self._table_phy_if,
                      ]

        return self._get_db_infos(device_name, get_tables)

    @decorater_log
    def _json_spine(self, db_info):
        '''
        Spine API data shaping
            Called out from DB after obtaining data.
        Explanation about parameter:
            db_info : DB information obtained ({DB name:({Item name: value})})
        Explanation about return value:
            API data letter strings (json format) ; str
            (API data list(JSON format).xlsm Refer to Spine information acquisition sheet)
        '''
        json_return = {}

        json_return["device"] = self._get_json_common_device_data(db_info)
        json_return["device"]["ospf"] = \
            self._get_json_common_area_id_data(db_info)

        json_return["internal-link"] = \
            self._get_json_common_internal_link_data(db_info)

        json_return["breakout_info"] = self._get_json_common_breakout(db_info)

        json_return["device_count"] = len(
            self._select_row(json_return["internal-link"],
                             if_type=self._if_type_lag))

        return json.dumps(json_return)

    @decorater_log
    def _json_leaf(self, db_info):
        '''
        Leaf API data shaping
            Called out from DB after obtaining data.
        Explanation about parameter:
            db_info : DB information obtained({DB name:({Item name: value})})
        Explanation about return value:
            API data letter strings(json format) ; str
            (API data list(JSON format).xlsm Refer to Leaf information acquisition sheet)
        '''
        json_return = {}

        json_return["device"] = self._get_json_common_device_data(db_info)
        tmp_ospf = {}
        tmp_ospf.update(self._get_json_common_area_id_data(db_info))
        t_table = db_info.get(self._table_device, ({},))[0]
        tmp_json = {}
        tmp_json["virtual_link"] = {
            "router_id": t_table.get("virtual_link_id")}
        tmp_ospf.update(tmp_json)
        tmp_json = {}
        tmp_json["range"] = {
            "address": t_table.get("ospf_range_area_address"),
            "prefix": t_table.get("ospf_range_area_prefix")}
        tmp_ospf.update(tmp_json)
        json_return["device"]["ospf"] = tmp_ospf

        json_return["internal-link"] = \
            self._get_json_common_internal_link_data(db_info)

        json_return["breakout_info"] = self._get_json_common_breakout(db_info)

        t_table = db_info.get(self._table_l3vpn_bgp, ())
        tmp_json_list = []
        tmp_bgp_comm_val = None
        tmp_bgp_comm_wild = None
        for row in t_table:
            tmp_json = {}
            tmp_json["neighbor"] = {"address": row.get("neighbor_ipv4")}
            tmp_json_list.append(tmp_json)
            tmp_bgp_comm_val = row.get("bgp_community_value")
            tmp_bgp_comm_wild = row.get("bgp_community_wildcard")
        tmp_json = {"neighbor_value": len(tmp_json_list),
                    "neighbor": tmp_json_list,
                    "bgp_community": {"value": tmp_bgp_comm_val,
                                      "wildcard": tmp_bgp_comm_wild}}
        json_return["l3_vpn_bgpbasic"] = tmp_json

        json_return["device_count"] = len(
            self._select_row(json_return["internal-link"],
                             if_type=self._if_type_lag))

        return json.dumps(json_return)

    @decorater_log
    def _json_l2_slice(self, db_info):
        '''
        L2 slice API data shaping
            Called out from DB after obtaining data.
        Explanation about parameter:
            db_info : DB information obtained({DB name:({Item name: value})})
        Explanation about return value:
            API data letter strings(json format) ; str
            (API data list(JSON format).xlsm L2 slice information acquisition)
        '''
        json_return = {}
        t_table = db_info.get(self._table_vlan_if, ())

        json_list_item = []
        json_return["cp_value"] = len(t_table)
        for row in t_table:
            if int(row["slice_type"]) != 2:
                continue
            json_item = {}
            json_item["device_name"] = row["device_name"]
            json_item["if_name"] = row["if_name"]
            json_item["slice_name"] = row["slice_name"]
            json_item["vlan"] = {
                "vlan_id": row["vlan_id"],
                "port_mode": self._port_mode_text.get(row["port_mode"])}
            json_item["vni"] = row.get("vni")
            json_item["esi"] = row.get("esi")
            json_item["system-id"] = row.get("system_id")
            json_list_item.append(json_item)
        json_return["cp"] = json_list_item

        t_table = db_info.get(self._table_lag_if, ())
        json_list_item = []
        for row in t_table:
            json_item = {}
            json_item["if_name"] = row["lag_if_name"]
            json_item["links"] = row["minimum_links"]
            json_list_item.append(json_item)
        json_return["lag"] = json_list_item

        return json.dumps(json_return)

    @decorater_log
    def _json_l3_slice(self, db_info):
        '''
        L3 slice API data shaping
            Called out from DB after obtaining data.
        Explanation about parameter:
            db_info : DB information obtained({DB name:({Item name: value})})
        Explanation about return value:
            API data letter strings(json format) ; str
            (API data list(JSON format).xlsm L3 slice information acquisition)
        '''
        json_return = {}

        t_table = db_info.get(self._table_device, ({},))[0]
        json_item = {}
        json_item["device_name"] = t_table.get("device_name")
        json_item["as_number"] = t_table.get("as_number")
        json_return["device"] = json_item

        t_table = db_info.get(self._table_vlan_if, ())
        json_list_item = []
        json_return["cp_value"] = len(t_table)
        for row in t_table:
            if int(row["slice_type"]) != 3:
                continue
            json_item = {}
            json_item["if_name"] = row["if_name"]
            json_item["slice_name"] = row["slice_name"]
            json_item["vlan"] = {"vlan_id": row["vlan_id"],
                                 "port_mode":
                                 self._port_mode_text.get(row["port_mode"])}
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

        t_table = db_info.get(self._table_vrf, ())
        json_list_item = []
        json_return["vrf_detail_value"] = len(t_table)
        for row in t_table:
            json_item = {}
            json_item["if_name"] = row["if_name"]
            json_item["vlan_id"] = row["vlan_id"]
            json_item["slice_name"] = row["slice_name"]
            json_item["vrf_name"] = row["vrf_name"]
            json_item["rt"] = row["rt"]
            json_item["rd"] = row["rd"]
            json_item["router_id"] = row["router_id"]
            json_list_item.append(json_item)
        json_return["vrf_detail"] = json_list_item

        t_table = db_info.get(self._table_vrrp, ())
        json_list_item = []
        json_return["vrrp_detail_value"] = len(t_table)
        for row in t_table:
            json_item = {}
            json_item["if_name"] = row["if_name"]
            json_item["vlan_id"] = row["vlan_id"]
            json_item["slice_name"] = row["slice_name"]
            json_item["gropu_id"] = row["vrrp_group_id"]
            json_item["virtual"] = \
                {"ipv4_address": row["virtual_ipv4_address"],
                 "ipv6_address": row["virtual_ipv6_address"]}
            json_item["priority"] = row["priority"]
            json_item["track_if_name"] = None
            tmp_list = []
            for tr_name in db_info.get(self._table_vrrp_track, ()):
                if tr_name["vrrp_group_id"] == row["vrrp_group_id"]:
                    tmp_list.append(tr_name["track_if_name"])
            json_item["track_if_name"] = tmp_list
            json_list_item.append(json_item)
        json_return["vrrp_detail"] = json_list_item

        t_table = db_info.get(self._table_bgp, ())
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

        t_table = db_info.get(self._table_static, ())
        static = {"if_name": None, "vlan_id": None,
                  "ipv4": {"address": None, "prefix": None, "nexthop": None},
                  "ipv6": {"address": None, "prefix": None, "nexthop": None}}
        json_list_item = []
        json_return["static_detail_value"] = len(t_table)
        for row in t_table:
            json_item = static.copy()
            json_item["if_name"] = row["if_name"]
            json_item["vlan_id"] = row["vlan_id"]
            json_item["slice_name"] = row["slice_name"]
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

    @decorater_log
    def _json_ce_lag(self, db_info):
        '''
        LAG for CE API data shaping
            Called out from DB after obtaining data.
        Explanation about parameter:
            db_info : DB information obtained({DB name:({Item name: value})})
        Explanation about return value:
            API data letter strings(json format) ; str
            (API data list(JSON format).xlsm Refer to information acquisition sheet of LAG for CE)
        '''
        json_return = {}

        t_table = db_info.get(self._table_lag_if, ())
        json_list_item = []
        json_return["lag_value"] = len(t_table)
        for row in t_table:
            json_item = {}
            json_item["if_name"] = row["lag_if_name"]
            json_item["links"] = row["minimum_links"]
            json_item["link_speed"] = row["link_speed"]
            json_list_item.append(json_item)
        json_return["lag"] = json_list_item

        t_table = db_info.get(self._table_lag_mem, ())
        json_list_item = []
        json_return["lag_member_value"] = len(t_table)
        for row in t_table:
            json_item = {}
            json_item["lag_if_name"] = row["lag_if_name"]
            json_item["if_name"] = row["if_name"]
            json_list_item.append(json_item)
        json_return["lag_member"] = json_list_item

        json_return["device"] = None
        if json_return.get("lag_value", 0) > 0:
            json_return["device"] = t_table[0].get("device_name")

        return json.dumps(json_return)

    @decorater_log
    def _json_internal_link(self, db_info):
        '''
        Internal link API data shaping
            Called out from DB after obtaining data.
        Explanation about parameter:
            db_info : DB information obtained({DB name:({Item name: value})})
        Explanation about return value:
            API data letter strings(json format) ; str
            (API data list(JSON format).xlsm
                Refer to internal link information acquisition sheet)
        '''

        json_return = {}

        t_table = db_info.get(self._table_device, ({},))[0]
        json_return["device"] = {
            "device_name": t_table.get("device_name"),
            "device_type": self._device_types.get(t_table.get("device_type"))}

        json_return["device"]["ospf"] = \
            self._get_json_common_area_id_data(db_info)

        json_return["internal-link"] = \
            self._get_json_common_internal_link_data(db_info)

        return json.dumps(json_return)

    @decorater_log
    def _json_breakout(self, db_info):
        '''
        breakout API data shaping
            Called out from DB after obtaining data.
        Explanation about parameter:
            db_info : DB information obtained({DB name:({Item name: value})})
        Explanation about return value:
            API data letter strings(json format) ; str
            (API data list(JSON format).xlsm
                Refer to breakout information acquisition sheet)
        '''
        json_return = {}

        json_return["breakout_info"] = self._get_json_common_breakout(db_info)

        return json.dumps(json_return)

    @decorater_log
    def _json_cluster_link(self, db_info):
        '''
        Link among clusters API data shaping
            Called out from DB after obtaining data.
        Explanation about parameter:
            db_info : DB information obtained({DB name:({Item name: value})})
        Explanation about return value:
            API data letter strings(json format) ; str
            (API data list(JSON format).xlsm
                Refer to link among clusters acquisition sheet)
        '''
        json_return = {}

        t_table = db_info.get(self._table_cluster_link, ())
        json_return["cluster-link_value"] = len(t_table)
        tmp_json_list = []
        for row in t_table:
            tmp_json = {}
            tmp_json["device_name"] = row.get("device_name")
            tmp_json["name"] = row.get("if_name")
            tmp_json["type"] = self._if_types.get(row.get("if_type"))
            tmp_json["address"] = row.get("cluster_link_ip_address")
            tmp_json["prefix"] = row.get("cluster_link_ip_prefix")
            tmp_json["ospf"] = {"metric": row.get("igp_cost")}
            tmp_json_list.append(tmp_json)
        json_return["cluster-link_info"] = tmp_json_list

        t_table = db_info.get(self._table_phy_if, ())
        json_return["physical-interface_value"] = len(t_table)
        tmp_json_list = []
        for row in t_table:
            tmp_json = {}
            tmp_json["name"] = row.get("if_name")
            tmp_json["condition"] = self._port_cond.get(row.get("condition"))
            tmp_json_list.append(tmp_json)
        json_return["physical-interface"] = tmp_json_list

        t_table = db_info.get(self._table_lag_if, ())
        json_return["lag_value"] = len(t_table)
        tmp_json_list = []
        for row in t_table:
            tmp_json = {}
            tmp_json["if_name"] = row.get("lag_if_name")
            tmp_json["type"] = row.get("lag_type")
            tmp_json["links"] = row.get("minimum_links")
            tmp_json["link_speed"] = row.get("link_speed")
            tmp_json_list.append(tmp_json)
        json_return["lag"] = tmp_json_list

        t_table = db_info.get(self._table_lag_mem, ())
        json_return["lag_member_value"] = len(t_table)
        tmp_json_list = []
        for row in t_table:
            tmp_json = {}
            tmp_json["lag_if_name"] = row.get("lag_if_name")
            tmp_json["if_name"] = row.get("if_name")
            tmp_json_list.append(tmp_json)
        json_return["lag_member"] = tmp_json_list

        return json.dumps(json_return)

    @decorater_log
    def _get_json_common_device_data(self, db_info):
        '''
        Obtain device information by processing the DeviceRegistrationInfo. 
        Called out when obtaining device information.  
        Explanation about parameter:
            db_info : DB information obtained
        Explanation about return value:
            API data letter strings(json format) ; dict
        '''
        t_table = db_info.get(self._table_device, ({},))[0]

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
        return json_item

    @decorater_log
    def _get_json_common_area_id_data(self, db_info):
        '''
        Obtain area_id information by processing the DeviceRegistrationInfo. 
        Called out when obtaining area_id information.
        Explanation about parameter:
            db_info : DB information obtained
        Explanation about return value:
            API data letter strings(json format) ; dict
        '''
        t_table = db_info.get(self._table_device, ({},))[0]

        json_item = {}
        json_item["area_id"] = t_table.get("cluster_ospf_area")
        return json_item

    @decorater_log
    def _get_json_common_internal_link_data(self, db_info):
        '''
        Obtain internal-link information.
            Called out when obtaining internal-link information.
        Explanation about parameter:
            db_info : DB information obtained
        Explanation about return value:
            API data letter strings(json format) ; dict
        '''
        t_table = db_info.get(self._table_inner_link, ())
        mem_table = db_info.get(self._table_lag_mem, ())

        json_list_item = []
        for row in t_table:
            json_item = {}
            json_item["if_name"] = row["if_name"]
            json_item["if_type"] = row["if_type"]
            json_item["speed"] = row["link_speed"]
            json_item["ip_address"] = row["internal_link_ip_address"]
            json_item["ip_prefix"] = row["internal_link_ip_prefix"]
            if json_item["if_type"] == self._if_type_lag:
                lag_mems = []
                for lag_row in mem_table:
                    lag_mems = self._select_row(mem_table,
                                                device_name=lag_row[
                                                    "device_name"],
                                                lag_if_name=lag_row[
                                                    "lag_if_name"])
                json_item["member_value"] = len(lag_mems)
                tmp_mem_list = []
                for lag_mem in lag_mems:
                    tmp_mem = {}
                    tmp_mem["if_name"] = lag_mem["if_name"]
                    tmp_mem_list.append(tmp_mem)
                json_item["member"] = tmp_mem_list
            json_list_item.append(json_item)
        return json_list_item

    @decorater_log
    def _get_json_common_breakout(self, db_info):
        '''
        Obtain breakout information by processing the BreakoutIfInfo. 
        Called out when obtaining area_id information.
            Called out when obtaining breakout information. 
        Explanation about parameter:
            db_info : DB information obtained
        Explanation about return value:
            API data letter strings(json format) ; dict
        '''
        t_table = db_info.get(self._table_breakout, ())

        json_item = {}
        json_item["interface_value"] = len(t_table)
        tmp_ifs = []
        for row in t_table:
            tmp_breakout_if = {}
            tmp_breakout_if["base-interface"] = row.get("base_interface")
            tmp_breakout_if["speed"] = row.get("speed")
            tmp_breakout_if["breakout-num"] = row.get("breakout_num")
            tmp_ifs.append(tmp_breakout_if)
        json_item["interface"] = tmp_ifs
        return json_item

    @staticmethod
    @decorater_log
    def _select_row(rows, **filters):
        '''
        Extract only the line which contains keyword from the line data list of DB.
        '''
        tmp_row = []
        for row in rows:
            is_target = True
            for filter_key in filters.keys():
                if row.get(filter_key) != filters[filter_key]:
                    is_target = False
                    break
            if is_target:
                tmp_row.append(row)
        return tmp_row
