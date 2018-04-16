# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2018 Nippon Telegraph and Telephone Corporation
# Filename: EmSeparateDriver.py
'''
Recovery utility
'''
import copy
import json
import sys
import traceback
import GlobalModule
from EmCommonLog import decorater_log
from EmNetconfProtocol import EmNetconfProtocol
from EmDriverCommonUtilityDB import EmDriverCommonUtilityDB
from EmDriverCommonUtilityLog import EmDriverCommonUtilityLog


class EmRecoverUtil(object):
    '''
    Recovery utility
    Launch from the Individual section on deriver (base class),
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
        Constructor.
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

        self.common_util_log = EmDriverCommonUtilityLog()

    @decorater_log
    def create_recover_leaf(self, ec_message_str, db_info_str):
        '''
        Creation of EC message of operation used for "reciver node" (Leaf addition)
        Parameter:
            ec_message : EC message（recover node）
            db_info : DB information
        Return value :
            result : Boolean
            Generated recovery EC message
        '''
        try:
            ec_message = json.loads(ec_message_str)
            db_info = json.loads(db_info_str)
            return self._create_recover_leaf_ec_message(ec_message, db_info)
        except Exception, ex_message:
            self.common_util_log.logging(
                ec_message.get("name"), self.log_level_debug,
                "ERROR %s\n%s" %
                (ex_message, traceback.format_exc()), __name__)
            sys.exc_info()
            return False, None

    @decorater_log
    def create_recover_b_leaf(self, ec_message_str, db_info_str):
        '''
        Creation of EC message of operation used for "reciver node" (B-Leaf addition)
        Parameter:
            ec_message : EC message（recover node）
            db_info : DB information
        Return value :
            result : Boolean
            Generated recovery EC message
        '''
        try:
            ec_message = json.loads(ec_message_str)
            db_info = json.loads(db_info_str)
            return self._create_recover_b_leaf_ec_message(ec_message, db_info)
        except Exception, ex_message:
            self.common_util_log.logging(
                ec_message.get("name"), self.log_level_debug,
                "ERROR %s\n%s" %
                (ex_message, traceback.format_exc()), __name__)
            return False, None

    @decorater_log
    def create_recover_ce_lag(self, ec_message_str, db_info_str):
        '''
        Creation of EC/DB message of operation used for "reciver service" (CELAG addition)
        Parameter:
            ec_message : EC message（recover service）
            db_info : DB information
        Return value :
            result : Boolean
            Generated recovery DB message
            Generated recovery EC message
        '''
        try:
            recover_node_info = None
            ec_message = json.loads(ec_message_str)
            db_info = json.loads(db_info_str)
            ret, recover_ec_message = self._create_recover_ce_lag_ec_message(
                ec_message, db_info)
            if ret and recover_ec_message is not None:
                ret, recover_node_info = self._create_recover_ce_lag_db_info(
                    ec_message, db_info)
            return ret, recover_node_info, recover_ec_message
        except Exception, ex_message:
            self.common_util_log.logging(
                ec_message.get("name"), self.log_level_debug,
                "ERROR %s\n%s" %
                (ex_message, traceback.format_exc()), __name__)
            return False, None, None

    @decorater_log
    def create_recover_cluster_link(self, ec_message_str, db_info_str):
        '''
        Creation of EC/DB message of operation used for "reciver service" (Cluster-link addition)
        Parameter:
            ec_message : EC message（recover service）
            db_info : DB information
        Return value :
            result : Boolean
            Generated recovery DB message
            Generated recovery EC message
        '''
        try:
            recover_node_info = None
            ec_message = json.loads(ec_message_str)
            db_info = json.loads(db_info_str)
            ret, recover_ec_message = \
                self._create_recover_cluster_link_ec_message(
                    ec_message, db_info)
            if ret and recover_ec_message is not None:
                ret, recover_node_info = \
                    self._create_recover_cluster_link_db_info(
                        ec_message, db_info)

            return ret, recover_node_info, recover_ec_message
        except Exception, ex_message:
            self.common_util_log.logging(
                ec_message.get("name"), self.log_level_debug,
                "ERROR %s\n%s" %
                (ex_message, traceback.format_exc()), __name__)
            return False, None, None

    @decorater_log
    def create_recover_l2_slice(self, ec_message_str, db_info_str):
        '''
        Creation of EC/DB message of operation used for "reciver service" (L2-slice evpn control)
        Parameter:
            ec_message : EC message（recover service）
            db_info : DB information
        Return value :
            result : Boolean
            Generated recovery DB message
            Generated recovery EC message
        '''
        recover_db_info_list = []
        recover_ec_message_list = []

        try:
            ret = True
            ec_message = json.loads(ec_message_str)
            db_info = json.loads(db_info_str)

            slice_name_set = set()
            cp_list = db_info.get(self.name_l2_slice).get("cp", [])
            for cp in cp_list:
                slice_name_set.add(cp.get("slice_name"))
            unrecovered_slice_name_set = copy.deepcopy(slice_name_set)
            req_convert = True
            for slice_name in slice_name_set:
                db_info_for_update = copy.deepcopy(db_info)
                ret, recover_ec_message = \
                    self._create_recover_l2_slice_ec_message(
                        ec_message, db_info, slice_name)
                if not ret:
                    return False, None, None
                if recover_ec_message is not None:
                    ret, recover_db_info = self._create_recover_l2_slice_db_info(
                        ec_message, db_info_for_update, slice_name,
                        unrecovered_slice_name_set, req_convert)
                    if not ret:
                        return False, None, None
                req_convert = False

                recover_ec_message_list.append(recover_ec_message)
                recover_db_info_list.append(recover_db_info)

                unrecovered_slice_name_set.remove(slice_name)

            return ret, recover_db_info_list, recover_ec_message_list
        except Exception, ex_message:
            self.common_util_log.logging(
                ec_message.get("name"), self.log_level_debug,
                "ERROR %s\n%s" %
                (ex_message, traceback.format_exc()), __name__)
            return False, None, None

    @decorater_log
    def create_recover_l3_slice(self, ec_message_str, db_info_str):
        '''
        Creation of EC/DB message of operation used for "reciver service" (L3-slice addition)
        Parameter:
            ec_message : EC message（recover service）
            db_info : DB information
        Return value :
            result : Boolean
            Generated recovery DB message
            Generated recovery EC message
        '''
        recover_db_info_list = []
        recover_ec_message_list = []

        try:
            ret = True
            ec_message = json.loads(ec_message_str)
            db_info = json.loads(db_info_str)

            slice_name_set = set()
            cp_list = db_info.get(self.name_l3_slice).get("cp", [])
            for cp in cp_list:
                slice_name_set.add(cp.get("slice_name"))
            unrecovered_slice_name_set = copy.copy(slice_name_set)

            req_convert = True
            for slice_name in slice_name_set:
                db_info_for_update = copy.deepcopy(db_info)
                ret, recover_ec_message = \
                    self._create_recover_l3_slice_ec_message(
                        ec_message, db_info, slice_name)
                if not ret:
                    return False, None, None
                if recover_ec_message is not None:
                    ret, recover_db_info = self._create_recover_l3_slice_db_info(
                        ec_message, db_info_for_update, slice_name,
                        unrecovered_slice_name_set, req_convert)
                    if not ret:
                        return False, None, None
                req_convert = False

                recover_ec_message_list.append(recover_ec_message)
                recover_db_info_list.append(recover_db_info)

                unrecovered_slice_name_set.remove(slice_name)

            return ret, recover_db_info_list, recover_ec_message_list
        except Exception, ex_message:
            self.common_util_log.logging(
                ec_message.get("name"), self.log_level_debug,
                "ERROR %s\n%s" %
                (ex_message, traceback.format_exc()), __name__)
            return False, None, None

    @decorater_log
    def _create_recover_leaf_ec_message(self, ec_message, db_info):
        '''
        Perform "Leaf Addition" EC message generation in restoration
        Parameter:
            ec_message : EC message（recover node）
            db_info : DB information
        Return value :
            result : Boolean
            Generated recovery EC message（JSON）
        '''
        self.common_util_log.logging(
            " ", self.log_level_debug, "db_info = %s" % db_info, __name__)
        self.common_util_log.logging(
            " ", self.log_level_debug, "ec_message = %s" % ec_message, __name__)

        return_ec_message = \
            {
                "device":
                {
                    "name": None,
                    "equipment":
                    {
                        "platform": None,
                        "os": None,
                        "firmware": None,
                        "loginid": None,
                        "password": None
                    },
                    "breakout-interface_value": 0,
                    "breakout-interface": [],
                    "internal-physical_value": 0,
                    "internal-physical": [],
                    "internal-lag_value": 0,
                    "internal-lag": [],
                    "management-interface":
                    {
                        "address": None,
                        "prefix": 0
                    },
                    "loopback-interface":
                    {
                        "address": None,
                        "prefix": 0
                    },
                    "snmp":
                    {
                        "server-address": None,
                        "community": None
                    },
                    "ntp":
                    {
                        "server-address": None
                    },
                    "ospf":
                    {
                        "area-id": None,
                    }
                }
            }

        self._gen_json_name(return_ec_message, db_info, ec_message)

        self._gen_json_equipment(return_ec_message, db_info, ec_message)

        self._gen_json_breakout(return_ec_message, db_info, ec_message)

        self._gen_json_internal_phys(return_ec_message, db_info, ec_message)

        self._gen_json_internal_lag(return_ec_message, db_info, ec_message)

        self._gen_json_management(return_ec_message, db_info, ec_message)

        self._gen_json_loopback(return_ec_message, db_info, ec_message)

        self._gen_json_snmp(return_ec_message, db_info, ec_message)

        self._gen_json_ntp(return_ec_message, db_info, ec_message)

        self._gen_json_vpn(return_ec_message, db_info, ec_message)

        self._gen_json_ospf(return_ec_message, db_info, ec_message)

        self.common_util_log.logging(
            " ", self.log_level_debug,
            "return_ec_message = %s" % return_ec_message, __name__)

        return True, json.dumps(return_ec_message)

    @decorater_log
    def _create_recover_b_leaf_ec_message(self, ec_message, db_info):
        '''
        Perform "B-Leaf Addition" EC message generation in restoration
        Parameter:
            ec_message : EC message（recover node）
            db_info : DB information
        Return value :
            result : Boolean
            Generated recovery EC message（JSON）
        '''
        self.common_util_log.logging(
            " ", self.log_level_debug, "db_info = %s" % db_info, __name__)
        self.common_util_log.logging(
            " ", self.log_level_debug, "ec_message = %s" % ec_message, __name__)

        return_ec_message = \
            {
                "device":
                {
                    "name": None,
                    "equipment":
                    {
                        "platform": None,
                        "os": None,
                        "firmware": None,
                        "loginid": None,
                        "password": None
                    },
                    "breakout-interface_value": 0,
                    "breakout-interface": [],
                    "internal-physical_value": 0,
                    "internal-physical": [],
                    "internal-lag_value": 0,
                    "internal-lag": [],
                    "management-interface":
                    {
                        "address": None,
                        "prefix": 0
                    },
                    "loopback-interface":
                    {
                        "address": None,
                        "prefix": 0
                    },
                    "snmp":
                    {
                        "server-address": None,
                        "community": None
                    },
                    "ntp":
                    {
                        "server-address": None
                    },
                    "ospf":
                    {
                        "area-id": None,
                        "virtual-link":
                        {
                            "router-id": None
                        },
                        "range":
                        {
                            "address": None,
                            "prefix": None
                        }
                    }
                }
            }

        self._gen_json_name(return_ec_message, db_info, ec_message)

        self._gen_json_equipment(return_ec_message, db_info, ec_message)

        self._gen_json_breakout(return_ec_message, db_info, ec_message)

        self._gen_json_internal_phys(return_ec_message, db_info, ec_message)

        self._gen_json_internal_lag(return_ec_message, db_info, ec_message)

        self._gen_json_management(return_ec_message, db_info, ec_message)

        self._gen_json_loopback(return_ec_message, db_info, ec_message)

        self._gen_json_snmp(return_ec_message, db_info, ec_message)

        self._gen_json_ntp(return_ec_message, db_info, ec_message)

        self._gen_json_vpn(return_ec_message, db_info, ec_message)

        self._gen_json_ospf(return_ec_message, db_info, ec_message)

        self.common_util_log.logging(
            " ", self.log_level_debug,
            "return_ec_message = %s" % return_ec_message, __name__)

        return True, json.dumps(return_ec_message)

    @decorater_log
    def _create_recover_ce_lag_ec_message(self, ec_message, db_info):
        '''
        Perform "CELAG Addition" EC message generation in restoration
        Parameter:
            ec_message : EC message（recover service）
            db_info : DB information
        Return value :
            result : Boolean
            Generated recovery EC message（JSON）
        '''
        self.common_util_log.logging(
            " ", self.log_level_debug, "db_info = %s" % db_info, __name__)
        self.common_util_log.logging(
            " ", self.log_level_debug, "ec_message = %s" % ec_message, __name__)

        return_ec_message = \
            {
                "device":
                {
                    "name": None,
                    "ce-lag-interface_value": 0,
                    "ce-lag-interface": []
                }
            }

        self._gen_json_name(return_ec_message, db_info, ec_message)

        self._gen_json_ce_lag_if(return_ec_message, db_info, ec_message)

        if return_ec_message["device"]["ce-lag-interface_value"] == 0:
            self.common_util_log.logging(" ", self.log_level_debug,
                                         "Need not recover CE-LAG.", __name__)

            return True, None

        self.common_util_log.logging(
            " ", self.log_level_debug,
            "return_ec_message = %s" % return_ec_message, __name__)

        return True, json.dumps(return_ec_message)

    @decorater_log
    def _create_recover_ce_lag_db_info(self, ec_message, db_info):
        '''
        Perform "CELAG Addition" DB information generation in restoration
        Parameter:
            ec_message : EC message（recover service）
            db_info : DB information
        Return value :
            result : Boolean
            Generated recovery DB information（JSON）
        '''
        return_db_info = db_info.get(self.name_ce_lag)
        for lag_if in return_db_info.get("lag"):
            lag_if["if_name"] = self._convert_ifname(
                lag_if.get("if_name"), ec_message, self._if_type_lag)
        for lag_mem_if in return_db_info.get("lag_member"):
            lag_mem_if["lag_if_name"] = self._convert_ifname(
                lag_mem_if.get("lag_if_name"), ec_message, self._if_type_lag)
            lag_mem_if["if_name"] = self._convert_ifname(
                lag_mem_if.get("if_name"), ec_message, self._if_type_phy)

        self.common_util_log.logging(
            " ", self.log_level_debug,
            "return_db_info = %s" % return_db_info, __name__)

        return True, json.dumps(return_db_info)

    @decorater_log
    def _create_recover_cluster_link_ec_message(self, ec_message, db_info):
        '''
        Perform "Cluster link Addition" EC message generation in restoration
        Parameter:
            ec_message : EC message（recover service）
            db_info : DB information
        Return value :
            result : Boolean
            Generated recovery EC message（JSON）
        '''
        self.common_util_log.logging(
            " ", self.log_level_debug, "db_info = %s" % db_info, __name__)
        self.common_util_log.logging(
            " ", self.log_level_debug, "ec_message = %s" % ec_message, __name__)

        return_ec_message = \
            {
                "device":
                {
                    "name": None,
                    "cluster-link-physical-interface_value": 0,
                    "cluster-link-physical-interface": [],
                    "cluster-link-lag-interface_value": 0,
                    "cluster-link-lag-interface": []
                }
            }

        self._gen_json_name(return_ec_message, db_info, ec_message)

        self._gen_json_cluster_link_phy(return_ec_message, db_info, ec_message)

        self._gen_json_cluster_link_lag(return_ec_message, db_info, ec_message)

        if return_ec_message["device"][
                "cluster-link-physical-interface_value"] == 0 and \
            return_ec_message["device"][
                "cluster-link-lag-interface_value"] == 0:
            self.common_util_log.logging(
                " ", self.log_level_debug,
                "Need not recover CLUSTER-LINK.", __name__)
            return True, None

        self.common_util_log.logging(
            " ", self.log_level_debug,
            "return_ec_message = %s" % return_ec_message, __name__)

        return True, json.dumps(return_ec_message)

    @decorater_log
    def _create_recover_cluster_link_db_info(self, ec_message, db_info):
        '''
        Perform "Cluster link Addition" DB information generation in restoration
        Parameter:
            ec_message : EC message（recover service）
            db_info : DB information
        Return value :
            result : Boolean
            Generated recovery DB information（JSON）
        '''
        return_db_info = db_info.get(self.name_cluster_link)
        for cl_if in return_db_info.get("cluster-link_info"):
            if cl_if.get("type") == self._if_type_phy:
                if_type = self._if_type_phy
            else:
                if_type = self._if_type_lag
            cl_if["name"] = self._convert_ifname(
                cl_if.get("name"), ec_message, if_type)
        for phys_if in return_db_info.get("physical-interface"):
            phys_if["name"] = self._convert_ifname(
                phys_if.get("name"), ec_message, self._if_type_phy)
        for lag_if in return_db_info.get("lag"):
            lag_if["if_name"] = self._convert_ifname(
                lag_if.get("if_name"), ec_message, self._if_type_lag)
        for lag_mem_if in return_db_info.get("lag_member"):
            lag_mem_if["lag_if_name"] = self._convert_ifname(
                lag_mem_if.get("lag_if_name"), ec_message, self._if_type_lag)
            lag_mem_if["if_name"] = self._convert_ifname(
                lag_mem_if.get("if_name"), ec_message, self._if_type_phy)

        self.common_util_log.logging(
            " ", self.log_level_debug,
            "return_db_info = %s" % return_db_info, __name__)

        return True, json.dumps(return_db_info)

    @decorater_log
    def _create_recover_l2_slice_ec_message(self, ec_message,
                                            db_info, slice_name):
        '''
        Perform "L2 slice Evpn control" EC message generation in restoration
        Parameter:
            ec_message : EC message（recover service）
            db_info : DB information
            slice_name : Slice name
        Return value :
            result : Boolean
            Generated recovery EC message（JSON）
        '''
        self.common_util_log.logging(
            " ", self.log_level_debug, "db_info = %s" % db_info, __name__)
        self.common_util_log.logging(
            " ", self.log_level_debug, "ec_message = %s" % ec_message, __name__)

        return_ec_message = \
            {
                "device-leaf":
                {
                    "name": None,
                    "slice_name": None,
                    "merge_cp_value": 0,
                    "delete_cp_value": 0,
                    "replace_cp_value": 0,
                    "cp": []
                }
            }

        self._gen_json_name(
            return_ec_message, db_info, ec_message, "device-leaf")

        self._gen_json_slice_name(
            return_ec_message, db_info, ec_message, slice_name)

        self._gen_json_l2_cp(
            return_ec_message, db_info, ec_message, slice_name)

        if return_ec_message["device-leaf"]["merge_cp_value"] == 0:
            self.common_util_log.logging(
                " ", self.log_level_debug,
                "Need not recover L2-SLICE.", __name__)
            return True, None

        self.common_util_log.logging(
            " ", self.log_level_debug,
            "return_ec_message = %s" % return_ec_message, __name__)

        return True, json.dumps(return_ec_message)

    @decorater_log
    def _create_recover_l2_slice_db_info(self, ec_message, db_info,
                                         slice_name,
                                         unrecovered_slice_name_set,
                                         req_convert):
        '''
        Perform "L2 slice Evpn control" DB information generation in restoration
        Parameter:
            ec_message : EC message（recover service）
            db_info : DB information
            slice_name : Slice name
            unrecovered_slice_name_set : Unrecovered slice name（Set）
            req_convert : Conversion request flag（device information/interface information）
        Return value :
            result : Boolean
            Generated recovery DB information（JSON）
        '''
        return_db_info = db_info.get(self.name_l2_slice)
        if req_convert:
            return_db_info["device"]["platform_name"] = \
                ec_message.get("device").get("equipment").get("platform")
            return_db_info["device"]["os_name"] = \
                ec_message.get("device").get("equipment").get("os")
            return_db_info["device"]["firm_version"] = \
                ec_message.get("device").get("equipment").get("firmware")
            for cp in return_db_info.get("cp"):
                cp["if_name"] = self._convert_ifname(
                    cp.get("if_name"), ec_message)
            for lag in return_db_info.get("lag"):
                lag["if_name"] = self._convert_ifname(
                    lag.get("if_name"), ec_message, self._if_type_lag)

        for cp in return_db_info.get("cp")[:]:
            if cp.get("slice_name") in unrecovered_slice_name_set:
                return_db_info.get("cp").remove(cp)
        return_db_info["cp_value"] = len(return_db_info["cp"])

        self.common_util_log.logging(
            " ", self.log_level_debug,
            "return_db_info = %s" % return_db_info, __name__)

        return True, json.dumps(return_db_info)

    @decorater_log
    def _create_recover_l3_slice_ec_message(self, ec_message, db_info,
                                            slice_name):
        '''
        Perform "L3 slice Evpn control" EC message generation in restoration
        Parameter:
            ec_message : EC message（recover service）
            db_info : DB information
            slice_name : Slice name
        Return value :
            result : Boolean
            Generated recovery EC message（JSON）
        '''
        self.common_util_log.logging(
            " ", self.log_level_debug, "db_info = %s" % db_info, __name__)
        self.common_util_log.logging(
            " ", self.log_level_debug, "ec_message = %s" % ec_message, __name__)

        return_ec_message = \
            {
                "device-leaf": {
                    "name": None,
                    "slice_name": None,
                    "vrf": {},
                    "cp_value": 0,
                    "cp": []
                }
            }

        self._gen_json_name(
            return_ec_message, db_info, ec_message, "device-leaf")

        self._gen_json_slice_name(
            return_ec_message, db_info, ec_message, slice_name)

        self._gen_json_vrf(
            return_ec_message, db_info, ec_message, slice_name)

        self._gen_json_l3_cp(
            return_ec_message, db_info, ec_message, slice_name)

        if return_ec_message["device-leaf"]["cp_value"] == 0:
            self.common_util_log.logging(
                " ", self.log_level_debug,
                "Need not recover L3-SLICE.", __name__)
            return True, None

        self.common_util_log.logging(
            " ", self.log_level_debug,
            "return_ec_message = %s" % return_ec_message, __name__)

        return True, json.dumps(return_ec_message)

    @decorater_log
    def _create_recover_l3_slice_db_info(self, ec_message, db_info,
                                         slice_name,
                                         unrecovered_slice_name_set,
                                         req_convert):
        '''
        Perform "L3 slice Addition" DB information generation in restoration
        Parameter:
            ec_message : EC message（recover service）
            db_info : DB information
            slice_name : Slice name
            unrecovered_slice_name_set : Unrecovered slice name（Set）
            req_convert : Conversion request flag（device information/interface information）
        Return value :
            result : Boolean
            Generated recovery DB information（JSON）
        '''
        return_db_info = db_info.get(self.name_l3_slice)

        if req_convert:
            return_db_info["device"]["platform_name"] = \
                ec_message.get("device").get("equipment").get("platform")
            return_db_info["device"]["os_name"] = \
                ec_message.get("device").get("equipment").get("os")
            return_db_info["device"]["firm_version"] = \
                ec_message.get("device").get("equipment").get("firmware")
            for cp in return_db_info.get("cp"):
                cp["if_name"] = self._convert_ifname(
                    cp.get("if_name"), ec_message, "all")
            for vrf in return_db_info.get("vrf_detail"):
                vrf["if_name"] = self._convert_ifname(
                    vrf.get("if_name"), ec_message, "all")
            for vrrp in return_db_info.get("vrrp_detail"):
                vrrp["if_name"] = self._convert_ifname(
                    vrrp.get("if_name"), ec_message, "all")
                converted_track_if_list = []
                for track_if in vrrp.get("track_if_name"):
                    converted_track_if_list.append(
                        self._convert_ifname(track_if, ec_message, "all"))
                vrrp["track_if_name"] = converted_track_if_list
            for bgp in return_db_info.get("bgp_detail"):
                bgp["if_name"] = self._convert_ifname(
                    bgp.get("if_name"), ec_message, "all")
            for static in return_db_info.get("static_detail"):
                static["if_name"] = self._convert_ifname(
                    static.get("if_name"), ec_message, "all")

        for cp in return_db_info.get("cp")[:]:
            if cp.get("slice_name") in unrecovered_slice_name_set:
                return_db_info.get("cp").remove(cp)
        for vrf in return_db_info.get("vrf_detail")[:]:
            if vrf.get("slice_name") in unrecovered_slice_name_set:
                return_db_info.get("vrf_detail").remove(vrf)
        for vrrp in return_db_info.get("vrrp_detail")[:]:
            if vrrp.get("slice_name") in unrecovered_slice_name_set:
                return_db_info.get("vrrp_detail").remove(vrrp)
        for bgp in return_db_info.get("bgp_detail")[:]:
            if bgp.get("slice_name") in unrecovered_slice_name_set:
                return_db_info.get("bgp_detail").remove(bgp)
        for static in return_db_info.get("static_detail")[:]:
            if static.get("slice_name") in unrecovered_slice_name_set:
                return_db_info.get("static_detail").remove(static)

        return_db_info["cp_value"] = len(return_db_info["cp"])
        return_db_info["vrf_detail_value"] = len(return_db_info["vrf_detail"])
        return_db_info["vrrp_detail_value"] = len(
            return_db_info["vrrp_detail"])
        return_db_info["bgp_detail_value"] = len(return_db_info["bgp_detail"])
        return_db_info["static_detail_value"] = len(
            return_db_info["static_detail"])

        self.common_util_log.logging(
            " ", self.log_level_debug,
            "return_db_info = %s" % return_db_info, __name__)

        return True, json.dumps(return_db_info)

    @decorater_log
    def _gen_json_name(self, json, db_info, ec_message, device_tag=None):
        '''
            Based on the EC message(recover node / recover service) and DB information,
            set device name in the EC message dictionary object used for recovery.
            Explanation about parameter :
                json：EC message dictionary object
                db_info : DB information
                ec_message : EC message(recover node / recover service)
                device_tag : device tag（default:device）
        '''
        if device_tag is None:
            device_tag = "device"
        json[device_tag]["name"] = ec_message.get("device", {}).get("name")

    @decorater_log
    def _gen_json_equipment(self, json, db_info, ec_message):
        '''
            Based on the EC message(recover node / recover service) and DB information,
            set device connection information in the EC message dictionary object used for recovery.
            Explanation about parameter :
                json：EC message dictionary object
                db_info : DB information
                ec_message : EC message(recover node / recover service)
        '''
        json["device"]["equipment"] = ec_message.get(
            "device", {}).get("equipment")

    @decorater_log
    def _gen_json_breakout(self, json, db_info, ec_message):
        '''
            Based on the EC message(recover node / recover service) and DB information,
            set breakoutIF informatio in the EC message dictionary object used for recovery.
            Explanation about parameter :
                json：EC message dictionary object
                db_info : DB information
                ec_message : EC message(recover node / recover service)
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
            Based on the EC message(recover node / recover service) and DB information,
            set IF information for internal Link(physical) in the EC message dictionary object used for recovery.
            Explanation about parameter :
                json：EC message dictionary object
                db_info : DB information
                ec_message : EC message(recover node / recover service)
        '''
        for internal_if_db in db_info.get("internal-link", ()):
            if internal_if_db.get("if_type") == self._if_type_phy_num:
                name = self._convert_ifname(
                    internal_if_db.get("if_name"),
                    ec_message, self._if_type_phy)
                opposite_node_name = None
                address = internal_if_db.get("ip_address")
                prefix = internal_if_db.get("ip_prefix")
                json["device"]["internal-physical"].append(
                    {"name": name,
                     "opposite-node-name": opposite_node_name,
                     "address": address,
                     "prefix": prefix})
        json["device"]["internal-physical_value"] = \
            len(json["device"]["internal-physical"])

    @decorater_log
    def _gen_json_internal_lag(self, json, db_info, ec_message):
        '''
            Based on the EC message(recover node / recover service) and DB information,
            set IF information for internal Link(LAG) in the EC message dictionary object used for recovery.
            Explanation about parameter :
                json：EC message dictionary object
                db_info : DB information
                ec_message : EC message(recover node / recover service)
        '''
        for internal_if_db in db_info.get("internal-link", ()):
            if internal_if_db.get("if_type") == self._if_type_lag_num:
                internal_lag = \
                    {
                        "name": None,
                        "opposite-node-name": None,
                        "lag-id": None,
                        "minimum-links": 0,
                        "link-speed": None,
                        "address": None,
                        "prefix": 0,
                        "internal-interface_value": 0,
                        "internal-interface": []
                    }
                name = self._convert_ifname(
                    internal_if_db.get("if_name"),
                    ec_message, self._if_type_lag)
                internal_lag["name"] = name
                internal_lag["opposite-node-name"] = None
                internal_lag["lag-id"] = internal_if_db.get("lag_if_id")
                internal_lag[
                    "minimum-links"] = internal_if_db.get("member_value")
                internal_lag["link-speed"] = internal_if_db.get("speed")
                internal_lag["address"] = internal_if_db.get("ip_address")
                internal_lag["prefix"] = internal_if_db.get("ip_prefix")

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
    def _gen_json_management(self, json, db_info, ec_message):
        '''
            Based on the EC message(recover node / recover service) and DB information,
            set management IF information in the EC message dictionary object used for recovery.
            Explanation about parameter :
                json：EC message dictionary object
                db_info : DB information
                ec_message : EC message(recover node / recover service)
        '''
        tmp = db_info.get("device").get("management_if")
        json["device"]["management-interface"]["address"] = tmp.get("address")
        json["device"]["management-interface"]["prefix"] = tmp.get("prefix")

    @decorater_log
    def _gen_json_loopback(self, json, db_info, ec_message):
        '''
            Based on the EC message(recover node / recover service) and DB information,
            set loopback IF information in the EC message dictionary object used for recovery.
            Explanation about parameter :
                json：EC message dictionary object
                db_info : DB information
                ec_message : EC message(recover node / recover service)
        '''
        tmp = db_info.get("device").get("loopback_if")
        json["device"]["loopback-interface"]["address"] = tmp.get("address")
        json["device"]["loopback-interface"]["prefix"] = tmp.get("prefix")

    @decorater_log
    def _gen_json_snmp(self, json, db_info, ec_message):
        '''
            Based on the EC message(recover node / recover service) and DB information,
            set SNMP information in the EC message dictionary object used for recovery.
            Explanation about parameter :
                json：EC message dictionary object
                db_info : DB information
                ec_message : EC message(recover node / recover service)
        '''
        tmp = db_info.get("device").get("snmp")
        json["device"]["snmp"]["server-address"] = tmp.get("address")
        json["device"]["snmp"]["community"] = tmp.get("community")

    @decorater_log
    def _gen_json_ntp(self, json, db_info, ec_message):
        '''
            Based on the EC message(recover node / recover service) and DB information,
            set NTP information in the EC message dictionary object used for recovery.
            Explanation about parameter :
                json：EC message dictionary object
                db_info : DB information
                ec_message : EC message(recover node / recover service)
        '''
        tmp = db_info.get("device").get("ntp")
        json["device"]["ntp"]["server-address"] = tmp.get("address")

    @decorater_log
    def _gen_json_ospf(self, json, db_info, ec_message):
        '''
            Based on the EC message(recover node / recover service) and DB information,
            set OSPF information in the EC message dictionary object used for recovery.
            Explanation about parameter :
                json：EC message dictionary object
                db_info : DB information
                ec_message : EC message(recover node / recover service)
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
            Based on the EC message(recover node / recover service) and DB information,
            set VPN information in the EC message dictionary object used for recovery.
            Explanation about parameter :
                json：EC message dictionary object
                db_info : DB information
                ec_message : EC message(recover node / recover service)
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
    def _gen_json_ce_lag_if(self, json, db_info, ec_message):
        '''
            Based on the EC message(recover node / recover service) and DB information,
            set CE-LAG information in the EC message dictionary object used for recovery.
            Explanation about parameter :
                json：EC message dictionary object
                db_info : DB information
                ec_message : EC message(recover node / recover service)
        '''
        ce_lags_db = db_info.get(self.name_ce_lag, {})

        for ce_lag_db in ce_lags_db.get("lag", []):
            if ce_lag_db.get("type") == self._lag_type_ce_num:
                ce_lag_message = \
                    {
                        "name": None,
                        "lag-id": None,
                        "minimum-links": 0,
                        "link-speed": None,
                        "leaf-interface_value": 0,
                        "leaf-interface": []
                    }
                old_lag_name = ce_lag_db.get("if_name")
                name = self._convert_ifname(
                    old_lag_name, ec_message, self._if_type_lag)
                ce_lag_message["name"] = name
                ce_lag_message["lag-id"] = ce_lag_db.get("lag_if_id")
                ce_lag_message["minimum-links"] = ce_lag_db.get("links")
                ce_lag_message["link-speed"] = ce_lag_db.get("link_speed")

                for lag_mem_db in ce_lags_db.get("lag_member"):
                    if lag_mem_db.get("lag_if_name") == old_lag_name:
                        old_lag_mem = lag_mem_db.get("if_name")
                        member_if_name = self._convert_ifname(
                            old_lag_mem, ec_message, self._if_type_phy)
                        internal_if_name = {"name": member_if_name}
                        ce_lag_message[
                            "leaf-interface"].append(internal_if_name)

                ce_lag_message["leaf-interface_value"] = \
                    len(ce_lag_message["leaf-interface"])

                json["device"]["ce-lag-interface"].append(ce_lag_message)

        json["device"]["ce-lag-interface_value"] = \
            len(json["device"]["ce-lag-interface"])

    @decorater_log
    def _gen_json_cluster_link_phy(self, json, db_info, ec_message):
        '''
            Based on the EC message(recover node / recover service) and DB information,
            set Cluster link information(Physical) in the EC message dictionary object used for recovery.
            Explanation about parameter :
                json：EC message dictionary object
                db_info : DB information
                ec_message : EC message(recover node / recover service)
        '''
        cluster_links_db = db_info.get(self.name_cluster_link, {})

        for cluster_link_db in cluster_links_db.get("cluster-link_info", []):
            if cluster_link_db.get("type") == self._if_type_phy:
                old_name = cluster_link_db.get("name")
                name = self._convert_ifname(
                    old_name, ec_message, self._if_type_phy)
                address = cluster_link_db.get("address")
                prefix = cluster_link_db.get("prefix")
                condition = None
                for phys in cluster_links_db.get("physical-interface", []):
                    if phys.get("name") == old_name:
                        condition = phys.get("condition")
                        break
                metric = cluster_link_db.get("ospf").get("metric")
                json["device"]["cluster-link-physical-interface"].append(
                    {"name": name,
                     "address": address,
                     "prefix": prefix,
                     "condition": condition,
                     "ospf": {"metric": metric}})

        json["device"]["cluster-link-physical-interface_value"] = len(
            json["device"]["cluster-link-physical-interface"])

    @decorater_log
    def _gen_json_cluster_link_lag(self, json, db_info, ec_message):
        '''
            Based on the EC message(recover node / recover service) and DB information,
            set Cluster link information(LAG) in the EC message dictionary object used for recovery.
            Explanation about parameter :
                json：EC message dictionary object
                db_info : DB information
                ec_message : EC message(recover node / recover service)
        '''
        cluster_links_db = db_info.get(self.name_cluster_link, {})

        for cluster_link_db in cluster_links_db.get("cluster-link_info", []):
            if cluster_link_db.get("type") == self._if_type_lag:
                cl_link_list = \
                    {
                        "name": None,
                        "address": None,
                        "prefix": None,
                        "leaf-interface_value": 0,
                        "leaf-interface": [],
                        "ospf": None
                    }
                old_lag_name = cluster_link_db.get("name")
                name = self._convert_ifname(
                    old_lag_name, ec_message, self._if_type_lag)
                cl_link_list["name"] = name
                cl_link_list["address"] = cluster_link_db.get("address")
                cl_link_list["prefix"] = cluster_link_db.get("prefix")

                for lag_mem_db in cluster_links_db.get("lag_member", []):
                    if lag_mem_db.get("lag_if_name") == old_lag_name:
                        old_lag_mem = lag_mem_db.get("if_name")
                        member_if_name = self._convert_ifname(
                            old_lag_mem, ec_message, self._if_type_phy)
                        condition = None
                        for phys in cluster_links_db.get(
                                "physical-interface", []):
                            if phys.get("name") == old_lag_mem:
                                condition = phys.get("condition")
                                break
                        cl_link_list["leaf-interface"].append({
                            "name": member_if_name,
                            "condition": condition})
                cl_link_list["leaf-interface_value"] = \
                    len(cl_link_list["leaf-interface"])

                metric = cluster_link_db.get("ospf").get("metric")
                cl_link_list["ospf"] = {"metric": metric}

                json["device"][
                    "cluster-link-lag-interface"].append(cl_link_list)

        json["device"]["cluster-link-lag-interface_value"] = \
            len(json["device"]["cluster-link-lag-interface"])

    @decorater_log
    def _gen_json_slice_name(self, json, db_info, ec_message, slice_name):
        '''
            Based on the EC message(recover node / recover service) and DB information,
            set Slice name information in the EC message dictionary object used for recovery.
            Explanation about parameter :
                json：EC message dictionary object
                db_info : DB information
                ec_message : EC message(recover node / recover service)
                slice_name : Recovery target slice name
        '''
        json["device-leaf"]["slice_name"] = slice_name

    @decorater_log
    def _gen_json_vrf(self, json, db_info, ec_message, slice_name):
        '''
            Based on the EC message(recover node / recover service) and DB information,
            set VRF information in the EC message dictionary object used for recovery.
            Explanation about parameter :
                json：EC message dictionary object
                db_info : DB information
                ec_message : EC message(recover node / recover service)
                slice_name : Recovery target slice name
        '''
        l3_db_info = db_info.get(self.name_l3_slice)
        for vrf in l3_db_info.get("vrf_detail", ()):
            if vrf.get("slice_name") == slice_name:
                json["device-leaf"]["vrf"]["vrf-name"] = vrf.get("vrf_name")
                json["device-leaf"]["vrf"]["rt"] = vrf.get("rt")
                json["device-leaf"]["vrf"]["rd"] = vrf.get("rd")
                json["device-leaf"]["vrf"]["router-id"] = vrf.get("router_id")
                break

    @decorater_log
    def _gen_json_l2_cp(self, json, db_info, ec_message, slice_name):
        '''
            Based on the EC message(recover node / recover service) and DB information,
            set L2CP information in the EC message dictionary object used for recovery.
            Explanation about parameter :
                json：EC message dictionary object
                db_info : DB information
                ec_message : EC message(recover node / recover service)
                slice_name : Recovery target slice name
        '''
        l2_db_info = db_info.get(self.name_l2_slice)

        for cp_info in l2_db_info.get("cp", ()):
            if cp_info.get("slice_name") != slice_name:
                continue
            cp_message = \
                {
                    "operation": None,
                    "name": None,
                    "vlan-id": 0,
                    "port-mode": None,
                    "vni": 0,
                    "esi": None,
                    "system-id": None,
                    "qos": None
                }
            cp_message["operation"] = "merge"
            old_if_name = cp_info.get("if_name")
            name = self._convert_ifname(old_if_name, ec_message, "all")
            cp_message["name"] = name
            cp_message["vlan-id"] = cp_info.get("vlan").get("vlan_id")
            cp_message["port-mode"] = cp_info.get("vlan").get("port_mode")
            cp_message["vni"] = cp_info.get("vni")
            cp_message["esi"] = cp_info.get("esi")
            cp_message["system-id"] = cp_info.get("system-id")
            cp_message["qos"] = self._create_qos_info(cp_info, ec_message)
            json["device-leaf"]["cp"].append(cp_message)

        json["device-leaf"]["merge_cp_value"] = len(json["device-leaf"]["cp"])
        json["device-leaf"]["delete_cp_value"] = 0
        json["device-leaf"]["replace_cp_value"] = 0

    @decorater_log
    def _create_qos_info(self, cp_info, ec_message):
        '''
            Based on the CP information of the DB, the QoS information
            used for the restoration EC message is generated
            Explanation about parameter :
                cp_info : CP information(DB)
                ec_message : EC message(recover node / recover service)
        Return value :
            QoS information used for recovery EC message(dict)
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
    def _gen_json_l3_cp(self, json, db_info, ec_message, slice_name):
        '''
            Based on the EC message(recover node / recover service) and DB information,
            set L3CP information in the EC message dictionary object used for recovery.
            Explanation about parameter :
                json：EC message dictionary object
                db_info : DB information
                ec_message : EC message(recover node / recover service)
                slice_name : Recovery target slice name
        '''
        l3_db_info = db_info.get(self.name_l3_slice)

        for cp_info in l3_db_info.get("cp", ()):
            if cp_info.get("slice_name") != slice_name:
                continue
            cp_message = \
                {
                    "operation": None,
                    "name": None,
                    "vlan-id": 0,
                    "ce-interface": {},
                    "vrrp": {
                        "track": {
                            "interface": []
                        }
                    },
                    "bgp": {},
                    "static": {
                        "route": [],
                        "route6": []
                    }
                }

            cp_message["operation"] = "merge"
            old_if_name = cp_info.get("if_name")
            name = self._convert_ifname(old_if_name, ec_message, "all")
            cp_message["name"] = name
            cp_message["vlan-id"] = cp_info.get("vlan").get("vlan_id")

            self._gen_json_l3cp_ce_interface(
                cp_message, cp_info, ec_message, slice_name)

            if cp_info.get("protocol_flags").get("vrrp"):
                self._gen_json_l3cp_vrrp(
                    cp_message, l3_db_info, ec_message, slice_name, cp_info)
            else:
                del cp_message["vrrp"]

            if cp_info.get("protocol_flags").get("bgp"):
                self._gen_json_l3cp_bgp(
                    cp_message, l3_db_info, ec_message, slice_name, cp_info)
            else:
                del cp_message["bgp"]

            if cp_info.get("protocol_flags").get("static"):
                self._gen_json_l3cp_static(
                    cp_message, l3_db_info, ec_message, slice_name, cp_info)
            else:
                del cp_message["static"]

            cp_message["qos"] = self._create_qos_info(cp_info, ec_message)
            json["device-leaf"]["cp"].append(cp_message)

        json["device-leaf"]["cp_value"] = len(json["device-leaf"]["cp"])

    @decorater_log
    def _gen_json_l3cp_ce_interface(self, cp_message, cp_info,
                                    ec_message, slice_name):
        '''
            Based on the EC message(recover node / recover service) and DB information,
            set Interface information for CE in the EC message dictionary object used for recovery.
            Explanation about parameter :
                cp_message：EC message dictionary object
                cp_info : DB information
                ec_message : EC message(recover node / recover service)
                slice_name : Recovery target slice name
        '''
        if cp_info.get("ce_ipv4").get("address") is not None:
            cp_message["ce-interface"][
                "address"] = cp_info.get("ce_ipv4").get("address")
            cp_message["ce-interface"][
                "prefix"] = cp_info.get("ce_ipv4").get("prefix")
        if cp_info.get("ce_ipv6").get("address") is not None:
            cp_message["ce-interface"][
                "address6"] = cp_info.get("ce_ipv6").get("address")
            cp_message["ce-interface"][
                "prefix6"] = cp_info.get("ce_ipv6").get("prefix")
        cp_message["ce-interface"]["mtu"] = cp_info.get("mtu_size")

    @decorater_log
    def _gen_json_l3cp_vrrp(self, cp_message, l3_db_info,
                            ec_message, slice_name, cp_info):
        '''
            Based on the EC message(recover node / recover service) and DB information,
            set VRRP information in the EC message dictionary object used for recovery.
            Explanation about parameter :
                cp_message：EC message dictionary object
                l3_db_info : DB information
                ec_message : EC message(recover node / recover service)
                slice_name : Recovery target slice name
                cp_info : DB information(CP）
        '''
        for vrrp in l3_db_info.get("vrrp_detail", ()):
            if cp_info.get("if_name") == vrrp.get("if_name") and \
                    cp_info.get("vlan").get(
                "vlan_id") == vrrp.get("vlan_id") and \
                    cp_info.get("slice_name") == vrrp.get("slice_name"):
                cp_message["vrrp"]["group-id"] = vrrp.get("gropu_id")
                if vrrp.get("virtual").get("ipv4_address") is not None:
                    cp_message["vrrp"][
                        "virtual-address"] = \
                        vrrp.get("virtual").get("ipv4_address")
                if vrrp.get("virtual").get("ipv6_address") is not None:
                    cp_message["vrrp"][
                        "virtual-address6"] = \
                        vrrp.get("virtual").get("ipv6_address")
                cp_message["vrrp"]["priority"] = vrrp.get("priority")
                for track_if in vrrp.get("track_if_name", []):
                    converted_track_if = self._convert_ifname(
                        track_if, ec_message, "all")
                    cp_message["vrrp"]["track"][
                        "interface"].append({"name": converted_track_if})
                cp_message["vrrp"]["track"]["track_interface_value"] = len(
                    cp_message["vrrp"]["track"]["interface"])
                break

    @decorater_log
    def _gen_json_l3cp_bgp(self, cp_message, l3_db_info,
                           ec_message, slice_name, cp_info):
        '''
            Based on the EC message(recover node / recover service) and DB information,
            set BGP information in the EC message dictionary object used for recovery.
            Explanation about parameter :
                cp_message：EC message dictionary object
                l3_db_info : DB information
                ec_message : EC message(recover node / recover service)
                slice_name : Recovery target slice name
                cp_info : DB information(CP）
        '''
        for bgp in l3_db_info.get("bgp_detail", ()):
            if cp_info.get("if_name") == bgp.get("if_name") and \
                    cp_info.get("vlan").get("vlan_id") == \
                    bgp.get("vlan_id") and \
                    cp_info.get("slice_name") == bgp.get("slice_name"):
                if bgp.get("master"):
                    cp_message["bgp"]["master"] = "ON"
                cp_message["bgp"]["remote-as-number"] = bgp.get("as_number")
                if bgp.get("local").get("ipv4_address") is not None:
                    cp_message["bgp"][
                        "local-address"] = bgp.get("local").get("ipv4_address")
                if bgp.get("remote").get("ipv4_address") is not None:
                    cp_message["bgp"]["remote-address"] = \
                        bgp.get("remote").get("ipv4_address")
                if bgp.get("local").get("ipv6_address") is not None:
                    cp_message["bgp"]["local-address6"] = \
                        bgp.get("local").get("ipv6_address")
                if bgp.get("remote").get("ipv6_address") is not None:
                    cp_message["bgp"]["remote-address6"] = \
                        bgp.get("remote").get("ipv6_address")
                break

    @decorater_log
    def _gen_json_l3cp_static(self, cp_message, l3_db_info,
                              ec_message, slice_name, cp_info):
        '''
            Based on the EC message(recover node / recover service) and DB information,
            set Static route information in the EC message dictionary object used for recovery.
            Explanation about parameter :
                cp_message：EC message dictionary object
                l3_db_info : DB information
                ec_message : EC message(recover node / recover service)
                slice_name : Recovery target slice name
                cp_info : DB information(CP）
        '''
        for static in l3_db_info.get("static_detail", ()):
            if cp_info.get("if_name") == static.get("if_name") and \
                    cp_info.get("vlan").get("vlan_id") == \
                    static.get("vlan_id") and \
                    cp_info.get("slice_name") == static.get("slice_name"):

                if static.get("ipv4").get("address") is not None:
                    route4 = \
                        {
                            "address": None,
                            "prefix": 0,
                            "nexthop": None
                        }
                    route4["address"] = static.get("ipv4").get("address")
                    route4["prefix"] = static.get("ipv4").get("prefix")
                    route4["nexthop"] = static.get("ipv4").get("nexthop")
                    cp_message["static"]["route"].append(route4)

                if static.get("ipv6").get("address") is not None:
                    route6 = \
                        {
                            "address": None,
                            "prefix": 0,
                            "nexthop": None
                        }
                    route6["address"] = static.get("ipv6").get("address")
                    route6["prefix"] = static.get("ipv6").get("prefix")
                    route6["nexthop"] = static.get("ipv6").get("nexthop")
                    cp_message["static"]["route6"].append(route6)

        cp_message["static"]["route_value"] = len(
            cp_message["static"]["route"])
        cp_message["static"]["route6_value"] = len(
            cp_message["static"]["route6"])

        if cp_message["static"]["route_value"] == 0:
            del cp_message["static"]["route"]
        if cp_message["static"]["route6_value"] == 0:
            del cp_message["static"]["route6"]

    @decorater_log
    def _convert_ifname(self, old_ifname, recover_ec_message, if_type="all"):
        '''
        Convert IF name before restoration to IF name after recovery, using IF name conversion table.
        Parameter:
            old_ifname : IF name before recovery
            recover_ec_message : EC message(recover node / recover service)（including IF name conversion table）
            if_type : IF type
        Return value :
            IF name after recovery
        Exception :
            ValueError : Conversion failure
        '''
        converted_if_name = None
        if if_type == self._if_type_phy or if_type == "all":
            for if_info in recover_ec_message.get("device").get("physical-ifs", []):
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
