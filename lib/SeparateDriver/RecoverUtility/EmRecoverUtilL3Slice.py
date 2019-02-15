# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2018 Nippon Telegraph and Telephone Corporation
# Filename: EmRecoverUtilL3Slice.py
'''
Utility for restoration(L3 slice addition)
'''

import copy
import json
import traceback
import EmRecoverUtilBase
from EmCommonLog import decorater_log


class EmRecoverUtilL3Slice(EmRecoverUtilBase.EmRecoverUtilBase):
    '''
    Utility for restoration
    '''

    _vrrp_master = 100
    _vrrp_slave = 95

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmRecoverUtilL3Slice, self).__init__()

    @decorater_log
    def create_recover_message(self, ec_message_str,
                               db_info_str, service_type):
        '''
        Create EC message, or DB information for operation to be used for restoration expansion (L3 slice addition)
        Parameter:
            ec_message : EC message for "recover service"
            db_info : DB information
            service_type : Restoration expansion or "recover service"
        Return value :
            Result : Boolean
            DB message list for restoration which has been created
            EC message list for restoration which has been created
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
    def _create_recover_ec_message(self, ec_message, db_info,
                                   slice_name):
        '''
        Create L3 slice EVPN control EC message for restoration
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
    def _create_recover_db_info(self, ec_message, db_info,
                                slice_name,
                                unrecovered_slice_name_set,
                                req_convert):
        '''
        Create L3 slice creation DB information for restoration
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
    def _gen_json_l3_cp(self, json, db_info, ec_message, slice_name):
        '''
            Set the L3CP information to the EC message storage dictionary object
            to be used for restoration based on EC message for restoration expansion/"recover service"
            and DB information
            Explanation about parameter：
                json：EC message storage dictionary object
                db_info : DB information
                ec_message : EC message for restoration expansion/"recover service"
                slice_name : Slice name to be recovered
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
            Set the IF information for CE to the EC message storage dictionary object
            to be used for restoration based on EC message for restoration expansion/"recover service"
            and DB information
            Explanation about parameter：
                cp_message：EC message storage dictionary object
                cp_info : DB information
                ec_message : EC message for restoration expansion/"recover service"
                slice_name : Slice name to be recovered
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
            Set the static information to the EC message storage dictionary object
            to be used for restoration based on EC message for restoration expansion/"recover service"
            and DB information
            Explanation about parameter：
                cp_message：EC message storage dictionary object
                l3_db_info : DB information
                ec_message : EC message for restoration expansion/"recover service"
                slice_name : Slice name to be recovered
                cp_info : DB information(CP）
        '''
        for vrrp in l3_db_info.get("vrrp_detail", ()):
            if cp_info.get("if_name") == vrrp.get("if_name") and \
                    cp_info.get("vlan").get(
                "vlan_id") == vrrp.get("vlan_id") and \
                    cp_info.get("slice_name") == vrrp.get("slice_name"):
                cp_message["vrrp"]["group-id"] = vrrp.get("group_id")
                if vrrp.get("virtual").get("ipv4_address") is not None:
                    cp_message["vrrp"][
                        "virtual-address"] = \
                        vrrp.get("virtual").get("ipv4_address")
                if vrrp.get("virtual").get("ipv6_address") is not None:
                    cp_message["vrrp"][
                        "virtual-address6"] = \
                        vrrp.get("virtual").get("ipv6_address")
                cp_message["vrrp"]["priority"] = vrrp.get("priority")
                if vrrp.get("priority") == self._vrrp_master:
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
            Set the BGP information to the EC message storage dictionary object
            to be used for restoration based on EC message for restoration expansion/"recover service"
            and DB information
            Explanation about parameter：
                cp_message：EC message storage dictionary object
                l3_db_info : DB information
                ec_message : EC message for restoration expansion/"recover service"
                slice_name : Slice name to be recovered
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
            Set the static information to the EC message storage dictionary object
            to be used for restoration based on EC message for restoration expansion/"recover service"
            and DB information
            Explanation about parameter：
                cp_message：EC message storage dictionary object
                l3_db_info : DB information
                ec_message : EC message for restoration expansion/"recover service"
                slice_name : Slice name to be recovered
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
