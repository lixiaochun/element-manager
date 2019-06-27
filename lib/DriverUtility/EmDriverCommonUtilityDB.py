#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmDriverCommonUtilityDB.py
'''
Common utility (DB) module for the driver.
'''
import json
import datetime
import traceback
import GlobalModule
from EmCommonLog import decorater_log
from EmCommonLog import decorater_log_in_out


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
    _table_acl = "ACLInfo"
    _table_acl_detail = "ACLDetailInfo"
    _table_dummy_vlan_if = "DummyVlanIfInfo"
    _table_multi_homing = "MultiHomingInfo"
    _table_config_info = "DeviceConfigrationinfo"

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
        self._name_recover_node = GlobalModule.SERVICE_RECOVER_NODE
        self._name_recover_service = GlobalModule.SERVICE_RECOVER_SERVICE
        self._name_acl_filter = GlobalModule.SERVICE_ACL_FILTER
        self._name_if_condition = GlobalModule.SERVICE_IF_CONDITION

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
            self._name_recover_node: (self._get_recover_node_info,
                                      self._json_leaf),
            self._name_recover_service: (self._get_recover_service_info,
                                         self._json_recover_service),
            self._name_acl_filter: (self._get_acl_filter_info,
                                    self._json_acl_filter),
            self._name_if_condition: (self._get_if_condition_info,
                                      self._json_if_condition),
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
            self._table_acl:
            GlobalModule.DB_CONTROL.read_acl_info,
            self._table_acl_detail:
            GlobalModule.DB_CONTROL.read_acl_detail_info,
            self._table_dummy_vlan_if:
            GlobalModule.DB_CONTROL.read_dummy_vlan_if_info,
            self._table_multi_homing:
            GlobalModule.DB_CONTROL.read_multi_homing_info,
            self._table_config_info:
            GlobalModule.DB_CONTROL.read_device_configration_info,
        }

        self._write_db = {
            self._table_config_info:
            GlobalModule.DB_CONTROL.write_device_configration_info,
        }

        self._device_types = {1: self._name_spine, 2: self._name_leaf}

        self._vpn_types = {2: "l2", 3: "l3"}

        self._port_cond = {1: "enable", 0: "disable"}

        self._if_types = {self._if_type_physical: "physical-if",
                          self._if_type_lag: "lag-if", }

        self._port_mode_text = {1: "access", 2: "trunk"}

    @decorater_log_in_out
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

    @decorater_log_in_out
    def read_device_os(self, device_name):
        '''
        Obtains OS name based on Device Name from Driver Individual Part
        Explanation about parameter:
            device_name: Device name
       Explanation about return value:
            Device type : str
            VPN type : str
        '''
        db_info = self._get_db_infos(device_name, [self._table_device])
        device = db_info[1][self._table_device][0]
        os_name = device["os"]
        return os_name

    @decorater_log_in_out
    def read_device_driver_info(self, device_name):
        '''
        Obtain driver information  from individual part by using device name.
        Explanation about parameter:
            device_name: device name
        Explanation about return value:
            platform_name : str
            os : str
            firm_version : str
        '''
        db_info = self._get_db_infos(device_name, [self._table_device])
        device = db_info[1][self._table_device][0]
        platform_name = device["platform_name"]
        os_name = device["os"]
        firm_version = device["firm_version"]
        return platform_name, os_name, firm_version

    @decorater_log_in_out
    def read_latest_device_configuration(self, device_name, **filter_data):
        '''
        Obtain  newest device config from config information table.
        Explanation about parameter:
            device_name: device name str
            filter_data: refined condition dict(variable argument)
        Explanation about return value:
            newest device config : str
        '''
        try:
            db_func = self._get_db[self._table_config_info]
            is_ok, conf_rows = db_func(device_name=device_name)
            if not is_ok:
                raise IOError("Failed to get data from DeviceConfigrationinfo")
            if not conf_rows:
                return None, None

            conf_rows = [row for row in conf_rows
                         if self._check_filter_date(row, filter_data)]
            if not conf_rows:
                raise ValueError("No config with matching filter")

            def key_date(row):
                wk_date = "{0}{1}".format(row.get("working_date"),
                                          row.get("working_time"))
                date_format = "%Y%m%d%H%M%S"
                return datetime.datetime.strptime(wk_date, date_format)

            sort_row = sorted(conf_rows, key=key_date)
            latest_row = sort_row[-1]
            GlobalModule.EM_LOGGER.debug("latest config:%s", latest_row)
            latest_config = latest_row["config_file"]
            latest_date = "{0}{1}".format(latest_row["working_date"],
                                          latest_row["working_time"])
        except Exception as exc_info:
            GlobalModule.EM_LOGGER.warning(
                "208003 Get Latest Device Configuration Error")
            GlobalModule.EM_LOGGER.debug("ERROR ; %s", exc_info)
            GlobalModule.EM_LOGGER.debug(
                "Traceback ; %s", traceback.format_exc())
            raise
        return latest_config, latest_date

    @staticmethod
    def _check_filter_date(row, filter_data):
        for key, value in filter_data.items():
            if row.get(key) != value:
                return False
        return True

    @decorater_log_in_out
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

    @decorater_log_in_out
    def write_device_config_info(self,
                                 device_name,
                                 device_config,
                                 platform_name=None):
        '''
        Gets called when information is registered in device by driver individual part.
        Write information into DB.
        Explanation about parameter:
            device_name: dvice namae
            device_config：device config
            platform_name：platform name
        Explanation about return value:
            result : Boolean
        '''
        param = self._set_device_config_param(
            device_name, device_config, platform_name)
        is_ok = GlobalModule.DB_CONTROL.write_device_configration_info(**param)

        return is_ok

    @decorater_log
    def _set_device_config_param(self,
                                 device_name,
                                 device_config=None,
                                 platform_name=None):
        '''
        Return device config table to be registered.
        Explanation about parameter:
            param_list:parameter list
            device_name: device name
            device_config：device config
        Explanation about return value:
            result : Boolean
        '''
        date = datetime.datetime.now()
        working_date = date.strftime('%Y%m%d')
        working_time = date.strftime('%H%M%S')

        device_config_param = dict.fromkeys(["db_control",
                                             "device_name",
                                             "working_date",
                                             "working_time",
                                             "platform_name",
                                             "vrf_name",
                                             "practice_system",
                                             "log_type",
                                             "get_timing",
                                             "config_file",
                                             ])
        device_config_param["db_control"] = "INSERT"
        device_config_param["device_name"] = device_name
        device_config_param["working_date"] = working_date
        device_config_param["working_time"] = working_time
        device_config_param["platform_name"] = platform_name
        device_config_param["config_file"] = device_config
        device_config_param["get_timing"] = 2

        return device_config_param

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
        get_tables = [self._table_device,
                      self._table_vlan_if,
                      self._table_lag_if,
                      self._table_dummy_vlan_if,
                      self._table_vrf,
                      self._table_multi_homing,
                      self._table_acl,
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
    def _get_recover_node_info(self, device_name):
        '''
        Acquire necessary information for "recover node"
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
                      ]

        return self._get_db_infos(device_name, get_tables)

    @decorater_log
    def _get_recover_service_info(self, device_name):
        '''
        Acquire necessary information for "recover service"
        Explanation about parameter:
            device_name: Device name
        Explanation about return value:
            Acquisition result : Boolean
            Edit information : {DB name:({Item name: value})}
        '''
        get_tables = [self._table_device,
                      self._table_lag_if,
                      self._table_lag_mem,
                      self._table_phy_if,
                      self._table_inner_link,
                      self._table_cluster_link,
                      self._table_breakout,
                      self._table_l3vpn_bgp,
                      self._table_vlan_if,
                      self._table_vrf,
                      self._table_bgp,
                      self._table_static,
                      self._table_vrrp,
                      self._table_vrrp_track,
                      self._table_acl,
                      self._table_acl_detail,
                      self._table_dummy_vlan_if,
                      self._table_multi_homing,
                      ]

        return self._get_db_infos(device_name, get_tables)

    @decorater_log
    def _get_acl_filter_info(self, device_name):
        '''
        Acquires information required for ACL configuration
        Explanation about Return Value:
            Acquisition result : Boolean
            Edit information : {DB name:({Item name: Value})}
        '''
        get_tables = [self._table_acl,
                      self._table_acl_detail,
                      self._table_vlan_if,
                      ]

        return self._get_db_infos(device_name, get_tables)

    @decorater_log
    def _get_if_condition_info(self, device_name):
        '''
        Obtain  necessary information to open/close IF.
        Explanation about parameter:
            device_name: device name
        Explanation about return value:
            Result : Boolean
            edited information : ({DB name:({Item name: Value})})
        '''
        get_tables = [self._table_device,
                      self._table_phy_if,
                      self._table_lag_if,
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

        t_table = db_info.get(self._table_device, ({},))[0]
        json_item = {}
        json_item["platform_name"] = t_table.get("platform_name")
        json_item["os_name"] = t_table.get("os")
        json_item["firm_version"] = t_table.get("firm_version")
        json_item["as_number"] = t_table.get("as_number")
        json_item["loopback_if_address"] = t_table.get("loopback_if_address")
        json_item["cluster_ospf_area"] = t_table.get("cluster_ospf_area")
        json_return["device"] = json_item

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
            json_item["clag-id"] = row.get("clag_id")
            json_item["speed"] = row.get("speed")
            json_item["irb_ipv4_address"] = row.get("irb_ipv4_address")
            json_item["irb_ipv4_prefix"] = row.get("irb_ipv4_prefix")
            json_item["virtual_mac_address"] = row.get("virtual_mac_address")
            json_item["virtual_gateway_address"] = row.get(
                "virtual_gateway_address")
            json_item["virtual_gateway_prefix"] = row.get(
                "virtual_gateway_prefix")
            json_item["qos"] = self._get_json_common_qos(row)
            json_item["q_in_q"] = row.get("q_in_q")
            json_list_item.append(json_item)
        json_return["cp"] = json_list_item

        t_table = db_info.get(self._table_lag_if, ())
        json_list_item = []
        for row in t_table:
            json_item = {}
            json_item["if_name"] = row["lag_if_name"]
            json_item["links"] = row["minimum_links"]
            json_item["link_speed"] = row["link_speed"]
            json_list_item.append(json_item)
        json_return["lag"] = json_list_item

        t_table = db_info.get(self._table_dummy_vlan_if, ())

        json_list_item = []

        json_return["dummy_cp_value"] = len(t_table)
        for row in t_table:
            json_item = {}
            json_item["device_name"] = row["device_name"]
            json_item["slice_name"] = row["slice_name"]
            json_item["vlan"] = {
                "vlan_id": row["vlan_id"]}
            json_item["vni"] = row.get("vni")
            json_item["vrf"] = {
                "vrf_name": row["vrf_name"],
                "vrf_id": row["vrf_id"]}
            json_item["irb_ipv4_address"] = row.get("irb_ipv4_address")
            json_item["irb_ipv4_prefix"] = row.get("irb_ipv4_prefix")
            json_item["vrf_name"] = row["vrf_name"]
            json_item["vrf_id"] = row["vrf_id"]
            json_item["rt"] = row["rt"]
            json_item["rd"] = row["rd"]
            json_item["router_id"] = row["router_id"]
            json_item["loopback"] = {
                "address": row["vrf_loopback_interface_address"],
                "prefix": row["vrf_loopback_interface_prefix"]}

            json_list_item.append(json_item)
        json_return["dummy_cp"] = json_list_item

        t_table = db_info.get(self._table_vrf, ())

        json_list_item = []

        json_return["vrf_detail_value"] = len(t_table)
        for row in t_table:
            json_item = {}
            json_item["if_name"] = row["if_name"]
            json_item["vlan_id"] = row["vlan_id"]
            json_item["slice_name"] = row["slice_name"]
            json_item["vrf_name"] = row["vrf_name"]
            json_item["vrf_id"] = row["vrf_id"]
            json_item["rt"] = row["rt"]
            json_item["rd"] = row["rd"]
            json_item["router_id"] = row["router_id"]
            json_item["l3_vni"] = {
                "vni": row["l3_vni"],
                "vlan_id": row["l3_vlan_id"]}
            json_item["loopback"] = {
                "address": row["vrf_loopback_interface_address"],
                "prefix": row["vrf_loopback_interface_prefix"]}
            json_list_item.append(json_item)
        json_return["vrf_detail"] = json_list_item

        t_table = db_info.get(self._table_multi_homing)
        json_item = {}
        if t_table:
            t_table = t_table[0]
            json_item["anycast_id"] = t_table["anycast_id"]
            json_item["anycast_address"] = t_table["anycast_address"]
            json_item["clag_if"] = {
                "address": t_table["clag_if_address"],
                "prefix": t_table["clag_if_prefix"]}
            json_item["backup_address"] = t_table["backup_address"]
            json_item["peer_address"] = t_table["peer_address"]
        json_return["multi_homing"] = json_item

        t_table = db_info.get(self._table_acl, ())

        json_list_item = []

        json_return["acl_value"] = len(t_table)
        for row in t_table:
            json_item = {}
            json_item["acl_id"] = row["acl_id"]
            json_item["if_name"] = row["if_name"]
            json_item["vlan_id"] = row["vlan_id"]
            json_list_item.append(json_item)
        json_return["acl_info"] = json_list_item

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
        json_item["platform_name"] = t_table.get("platform_name")
        json_item["os_name"] = t_table.get("os")
        json_item["firm_version"] = t_table.get("firm_version")
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
            json_item["qos"] = self._get_json_common_qos(row)
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
            json_item["group_id"] = row["vrrp_group_id"]
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
            json_item["master"] = row["master"]
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
            json_item["type"] = row["lag_type"]
            json_item["lag_if_id"] = row["lag_if_id"]
            json_item["links"] = row["minimum_links"]
            json_item["link_speed"] = row["link_speed"]
            json_item["condition"] = row.get("condition")
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

        t_table = db_info.get(self._table_lag_if, ())
        json_list_item = []
        json_return["lag_value"] = len(t_table)
        for row in t_table:
            json_item = {}
            json_item["if_name"] = row["lag_if_name"]
            json_item["type"] = row["lag_type"]
            json_item["lag_if_id"] = row["lag_if_id"]
            json_item["links"] = row["minimum_links"]
            json_item["link_speed"] = row["link_speed"]
            json_list_item.append(json_item)
        json_return["lag"] = json_list_item

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
    def _json_recover_service(self, db_info):
        '''
        Recover Service API data shaping
            Called out from DB after obtaining data.
        Explanation about parameter:
            db_info : DB information obtained({DB name:({Item name: value})})
        Explanation about return value:
            API data letter strings(json format) ; str
            (API data list(JSON format).xlsm
                Refer to Recover Service acquisition sheet)
        '''
        json_return = {}
        json_return[self._name_leaf] = json.loads(self._json_leaf(db_info))
        json_return[self._name_ce_lag] = json.loads(self._json_ce_lag(db_info))
        json_return[self._name_cluster_link] = json.loads(
            self._json_cluster_link(db_info))
        json_return[self._name_l2_slice] = json.loads(
            self._json_l2_slice(db_info))
        json_return[self._name_l3_slice] = json.loads(
            self._json_l3_slice(db_info))
        json_return[self._name_acl_filter] = json.loads(
            self._json_acl_filter(db_info))
        json_return[self._name_if_condition] = json.loads(
            self._json_if_condition(db_info))
        return json.dumps(json_return)

    @decorater_log
    def _json_if_condition(self, db_info):
        '''
        Open/Close IF and Form API data.
                        Gets called after data obtained from DB.
            db_info : Acquired DB information({DB name:({Item name: Value})})
        Return value explanation:
            API data string(json format) ; str
            (API data list(JSON format).xlsm  Refer to LAG information acquisition sheet for CE)
        '''
        json_return = {}

        t_table = db_info.get(self._table_lag_if, ())
        json_list_item = []
        json_return["lag_value"] = len(t_table)
        for row in t_table:
            json_item = {}
            json_item["if_name"] = row["lag_if_name"]
            json_item["type"] = row["lag_type"]
            json_item["links"] = row["minimum_links"]
            json_item["link_speed"] = row["link_speed"]
            json_item["condition"] = self._port_cond.get(row.get("condition"))
            json_list_item.append(json_item)
        json_return["lag"] = json_list_item

        t_table = db_info.get(self._table_phy_if, ())
        json_return["physical-interface_value"] = len(t_table)
        tmp_json_list = []
        for row in t_table:
            tmp_json = {}
            tmp_json["if_name"] = row.get("if_name")
            tmp_json["condition"] = self._port_cond.get(row.get("condition"))
            tmp_json_list.append(tmp_json)
        json_return["physical-interface"] = tmp_json_list

        json_return["device"] = None
        if json_return.get("lag_value", 0) > 0:
            json_return["device"] = t_table[0].get("device_name")

        return json.dumps(json_return)

    @decorater_log
    def _json_acl_filter(self, db_info):
        '''
        ACL Configuration  API Data Shaping
            Gets called after data obtained from DB
        Parameter explanation:
            db_info : Acquired DB information({DB name:({Item name: Value})})
        Return value explanation:
            API data string(json format) ; str
            (API data list(JSON format).xlsm  Refer to LAG information acquisition sheet for CE)
        '''
        t_table = db_info.get(self._table_acl, ())
        t_acl_detail_table = db_info.get(self._table_acl_detail, ())

        json_obj = {}
        json_list_item = []

        for row in t_table:
            json_item = {}
            json_item["device-name"] = row["device_name"]
            json_item["filter-id"] = row["acl_id"]
            json_item["if-name"] = row["if_name"]
            json_item["vlan-id"] = row["vlan_id"]

            term_mems = []
            term_mems = self._select_row(t_acl_detail_table,
                                         acl_id=row["acl_id"])
            tmp_mem_list = []
            for term_mem in term_mems:
                tmp_mem = {}
                tmp_mem["term-name"] = term_mem["term_name"]
                tmp_mem["action"] = term_mem["action"]
                tmp_mem["direction"] = term_mem["direction"]
                tmp_mem["source-mac-address"] = term_mem["source_mac_address"]
                tmp_mem["destination-mac-address"] = term_mem[
                    "destination_mac_address"]
                tmp_mem["source-ip-address"] = term_mem["source_ip_address"]
                tmp_mem["destination-ip-address"] = term_mem[
                    "destination_ip_address"]
                tmp_mem["source-port"] = term_mem["source_port"]
                tmp_mem["destination-port"] = term_mem["destination_port"]
                tmp_mem["protocol"] = term_mem["protocol"]
                tmp_mem["priority"] = term_mem["acl_priority"]
                tmp_mem_list.append(tmp_mem)
                json_item["term"] = tmp_mem_list
            json_list_item.append(json_item)
        json_obj["acl-info"] = json_list_item
        t_table = db_info.get(self._table_vlan_if, ())
        cp_if_list = []
        for row in t_table:
            cp_if_list.append(row["if_name"])
        json_obj["cp_if_name_list"] = cp_if_list
        return json.dumps(json_obj)

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
        if t_table.get("vpn_type") is not None:
            json_item["vpn_type"] = t_table.get("vpn_type")
        if t_table.get("as_number") is not None:
            json_item["as_number"] = t_table.get("as_number")
        if t_table.get("q_in_q_type") is not None:
            json_item["q-in-q"] = t_table.get("q_in_q_type")

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
            json_item["cost"] = row["cost"]
            json_item["vlan_id"] = row["vlan_id"]

            if json_item["if_type"] == self._if_type_lag:
                t_lag_table = db_info.get(self._table_lag_if, ())
                for lag_if in t_lag_table:
                    if lag_if.get("lag_if_name") == json_item["if_name"]:
                        json_item["lag_if_id"] = lag_if.get("lag_if_id")
                        break
                lag_mems = []
                lag_mems = self._select_row(mem_table,
                                            lag_if_name=json_item["if_name"])
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

    @decorater_log
    def _get_json_common_qos(self, db_info):
        '''
        Obtain VlanQoS information by processing the VlanInfo.
        Called out when obtaining L2/L3 slice information.
        Explanation about parameter:
            db_info : DB information obtained
        Explanation about return value:
            API data letter strings(json format) ; dict
        '''

        json_item = {}
        json_item["inflow_shaping_rate"] = db_info.get("inflow_shaping_rate")
        json_item["outflow_shaping_rate"] = db_info.get("outflow_shaping_rate")
        json_item["remark_menu"] = db_info.get("remark_menu")
        json_item["egress_queue_menu"] = db_info.get("egress_queue_menu")
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
            GlobalModule.EM_LOGGER.debug("is_target = %s", is_target)
            if is_target:
                tmp_row.append(row)
        return tmp_row
