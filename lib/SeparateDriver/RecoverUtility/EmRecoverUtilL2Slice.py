# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2018 Nippon Telegraph and Telephone Corporation
# Filename: EmRecoverUtilL2Slice.py
'''
Utility for restoration(L2 slice EVPN control)
'''

import copy
import json
import traceback
import EmRecoverUtilBase
from EmCommonLog import decorater_log


class EmRecoverUtilL2Slice(EmRecoverUtilBase.EmRecoverUtilBase):
    '''
    Utility for restoration
    '''

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmRecoverUtilL2Slice, self).__init__()

    @decorater_log
    def create_recover_message(self, ec_message_str,
                               db_info_str, service_type):
        '''
        Create EC message, or DB information for operation to be used for restoration expansion（L2 slice EVPN control)
        Parameter :
            ec_message : EC message for "recover service"
            EC message for restoration(JSON)
            service_type : Restoration expansion or "Recover service"
        Return Value :
            Result : Boolean
            List of DB message for restoration which has been created
            List of EC message for restoration which has been created
        '''
        recover_db_info_list = []
        recover_ec_message_list = []

        try:
            ret = True
            ec_message = json.loads(ec_message_str)
            db_info = json.loads(db_info_str)

            slice_name_set = set()
            cp_list = db_info.get(self.name_l2_slice).get("cp", [])
            dummy_cp_list = db_info.get(self.name_l2_slice).get("dummy_cp", [])
            for cp in cp_list:
                slice_name_set.add(cp.get("slice_name"))
            for cp in dummy_cp_list:
                slice_name_set.add(cp.get("slice_name"))
            unrecovered_slice_name_set = copy.deepcopy(slice_name_set)
            req_convert = True
            for slice_name in slice_name_set:
                db_info_for_update = copy.deepcopy(db_info)
                ret, recover_ec_message = \
                    self._create_recover_ec_message(
                        ec_message, db_info, slice_name)
                if not ret:
                    return False, None, None
                if recover_ec_message is not None:
                    ret, recover_db_info = self._create_recover_db_info(
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
    def _create_recover_ec_message(self, ec_message,
                                   db_info, slice_name):
        '''
        Create L2 slice EVPN control EC message for restoration
        Parameter:
            ec_message : EC message for "recover service"
            db_info : DB information
            slice_name : Slice name
        Return Value :
            Result : Success：True  Failure：False
            EC message for restoration(JSON)
        '''
        self.common_util_log.logging(
            " ", self.log_level_debug, "db_info = %s" % db_info, __name__)
        self.common_util_log.logging(
            " ", self.log_level_debug, "ec_message = %s" %
            ec_message, __name__)

        return_ec_message = \
            {
                "device-leaf":
                {
                    "name": None,
                    "slice_name": None,
                    "vrf": {},
                    "merge_cp_value": 0,
                    "delete_cp_value": 0,
                    "replace_cp_value": 0,
                    "cp": [],
                    "dummy_cp": []
                }
            }

        self._gen_json_name(
            return_ec_message, db_info, ec_message, "device-leaf")

        self._gen_json_slice_name(
            return_ec_message, db_info, ec_message, slice_name)

        self._gen_json_vrf(
            return_ec_message, db_info, ec_message, slice_name,
            slice_type=self.name_l2_slice)

        self._gen_json_l2_cp(
            return_ec_message, db_info, ec_message, slice_name)

        self._gen_json_l2_dummy_cp(
            return_ec_message, db_info, ec_message, slice_name)

        self._gen_json_multi_homing(
            return_ec_message, db_info, ec_message, slice_name)

        self.common_util_log.logging(
            " ", self.log_level_debug,
            "return_ec_message = %s" % return_ec_message, __name__)

        if len(return_ec_message["device-leaf"].get("cp", [])) == 0 and \
                len(return_ec_message["device-leaf"].get("dummy_cp", [])) == 0:
            return True, None

        return True, json.dumps(return_ec_message)

    @decorater_log
    def _create_recover_db_info(self, ec_message, db_info,
                                slice_name,
                                unrecovered_slice_name_set,
                                req_convert):
        '''
        Create L2 slice EVPN control DB information for restoration
        Parameter:
            ec_message : EC message for "recover service"
            db_info : DB information
            slice_name : Slice name
            unrecovered_slice_name_set : Unrecovered slide
            req_convert : Model related information/IF name conversion necessity
        Return Value :
            Result : Success：True  Failure：False
            DB information for restoration(JSON)
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
            if return_db_info.get("vrf_detail"):
                for vrf in return_db_info.get("vrf_detail"):
                    vrf["if_name"] = self._convert_ifname(
                        vrf.get("if_name"), ec_message, "all")
            for lag in return_db_info.get("lag"):
                lag["if_name"] = self._convert_ifname(
                    lag.get("if_name"), ec_message, self._if_type_lag)
            if return_db_info.get("acl_info"):
                for vrf in return_db_info.get("acl_info"):
                    vrf["if_name"] = self._convert_ifname(
                        vrf.get("if_name"), ec_message, "all")

        for cp in return_db_info.get("cp")[:]:
            if cp.get("slice_name") in unrecovered_slice_name_set:
                return_db_info.get("cp").remove(cp)
        for dummy_cp in return_db_info.get("dummy_cp")[:]:
            if dummy_cp.get("slice_name") in unrecovered_slice_name_set:
                return_db_info.get("dummy_cp").remove(dummy_cp)
        for vrf in return_db_info.get("vrf_detail")[:]:
            if vrf.get("slice_name") in unrecovered_slice_name_set:
                return_db_info.get("vrf_detail").remove(vrf)
        return_db_info["cp_value"] = len(return_db_info["cp"])
        return_db_info["dummy_cp_value"] = len(return_db_info["dummy_cp"])
        return_db_info["vrf_detail_value"] = len(return_db_info["vrf_detail"])

        self.common_util_log.logging(
            " ", self.log_level_debug,
            "return_db_info = %s" % return_db_info, __name__)

        return True, json.dumps(return_db_info)

    @decorater_log
    def _gen_json_l2_cp(self, json, db_info, ec_message, slice_name):
        '''
            Set the L2 CP information to the EC message storage dictionary object
            to be used for restoration based on EC message for restoration expansion/"recover service"
            and DB information
            Explanation about parameter：
                json：EC message storage dictionary object
                db_info : DB information
                ec_message : EC message for restoration expansion/"recover service"
                slice_name : Slice name to be recovered
        '''
        l2_db_info = db_info.get(self.name_l2_slice, {})

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
                    "clag-id": None,
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
            if cp_info.get("clag-id"):
                cp_message["clag-id"] = cp_info.get("clag-id")
            if cp_info.get("speed"):
                cp_message["speed"] = cp_info.get("speed")
            cp_message["qos"] = self._create_qos_info(cp_info, ec_message)
            irb_dict = self._create_irb_info(cp_info, ec_message)
            if irb_dict["physical-ip-address"]["address"]:
                cp_message["irb"] = irb_dict
            json["device-leaf"]["cp"].append(cp_message)

        json["device-leaf"]["merge_cp_value"] = len(json["device-leaf"]["cp"])
        json["device-leaf"]["delete_cp_value"] = 0
        json["device-leaf"]["replace_cp_value"] = 0

        if len(json["device-leaf"]["cp"]) == 0:
            del json["device-leaf"]["cp"]

    @decorater_log
    def _gen_json_l2_dummy_cp(self, json, db_info, ec_message, slice_name):
        '''
            Set the L2 dummy CP information to the EC message storage dictionary object
            to be used for restoration based on EC message for restoration expansion/"recover service"
            and DB information
            Explanation about parameter：
                json：EC message storage dictionary object
                db_info : DB information
                ec_message : EC message for restoration expansion/"recover service"
                slice_name : Slice name to be recovered
        '''
        l2_db_info = db_info.get(self.name_l2_slice, {})

        for cp_info in l2_db_info.get("dummy_cp", ()):
            if cp_info.get("slice_name") != slice_name:
                continue
            dmy_cp_message = \
                {
                    "operation": None,
                    "vlan-id": 0,
                    "vni": 0
                }
            dmy_cp_message["operation"] = "merge"
            dmy_cp_message["vlan-id"] = cp_info.get("vlan").get("vlan_id")
            dmy_cp_message["vni"] = cp_info.get("vni")
            dmy_cp_message["irb"] = self._create_irb_info(cp_info, ec_message)
            json["device-leaf"]["dummy_cp"].append(dmy_cp_message)
        if len(json["device-leaf"]["dummy_cp"]) == 0:
            del json["device-leaf"]["dummy_cp"]

    @decorater_log
    def _create_irb_info(self, cp_info, ec_message):
        '''
            Create IRB information to be used for restoration EC message based on CP information of DB
            Explanation about parameter：
                cp_info : CP information (DB)
                ec_message : EC message for restoration expansion/"recover service"
        Return Value :
            Result : IRB information used for restoration EC message(dict)
        '''
        irb_message = \
            {
                "physical-ip-address": None,
                "virtual-mac-address": None
            }

        physical_ip_address = \
            {
                "address": None,
                "prefix": 0
            }
        physical_ip_address["address"] = cp_info.get("irb_ipv4_address")
        physical_ip_address["prefix"] = cp_info.get("irb_ipv4_prefix")
        irb_message["physical-ip-address"] = physical_ip_address

        irb_message["virtual-mac-address"] = cp_info.get("virtual_mac_address")

        if cp_info.get("virtual_gateway_address"):
            virtual_gateway = \
                {
                    "address": None,
                    "prefix": 0
                }
            virtual_gateway["address"] = cp_info.get("virtual_gateway_address")
            virtual_gateway["prefix"] = cp_info.get("virtual_gateway_prefix")
            irb_message["virtual-gateway"] = virtual_gateway

        return irb_message

    @decorater_log
    def _gen_json_multi_homing(self, json, db_info, ec_message, slice_name):
        '''
            Set the multihoming information to the EC message storage dictionary object
            to be used for restoration based on EC message for restoration expansion/"recover service"
            and DB information
            Explanation about parameter：
                json：EC message storage dictionary object
                db_info : DB information
                ec_message : EC message for restoration expansion/"recover service"
                slice_name : Slice name to be recovered
        '''
        l2_db_info = db_info.get(self.name_l2_slice, {})
        multi_homing_db_info = l2_db_info.get("multi_homing", {})

        if multi_homing_db_info.get("anycast_id"):
            multi_home_message = \
                {
                    "anycast": None,
                    "interface": None,
                    "clag": None,
                    "recover": True
                }

            anycast = \
                {
                    "address": None,
                    "id": 0
                }
            anycast["address"] = multi_homing_db_info.get("anycast_address")
            anycast["id"] = multi_homing_db_info.get("anycast_id")
            multi_home_message["anycast"] = anycast

            interface = \
                {
                    "address": None,
                    "prefix": 0
                }
            interface["address"] = multi_homing_db_info.get(
                "clag_if", {}).get("address")
            interface["prefix"] = multi_homing_db_info.get(
                "clag_if", {}).get("prefix")
            multi_home_message["interface"] = interface

            clag = \
                {
                    "backup": None,
                    "peer": None
                }
            backup_addr = multi_homing_db_info.get("backup_address")
            tmp_addr = {"address": backup_addr}
            clag.update({"backup": tmp_addr})
            peer_addr = multi_homing_db_info.get("peer_address")
            tmp_addr = {"address": peer_addr}
            clag.update({"peer": tmp_addr})

            multi_home_message["clag"] = clag

            json["device-leaf"]["multi-homing"] = multi_home_message
