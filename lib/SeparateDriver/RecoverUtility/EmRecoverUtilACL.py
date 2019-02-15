# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2018 Nippon Telegraph and Telephone Corporation
# Filename: EmRecoverUtilACL.py
'''
Utility for restoration(ACL configuration)
'''

import json
import EmRecoverUtilBase
from EmCommonLog import decorater_log


class EmRecoverUtilACL(EmRecoverUtilBase.EmRecoverUtilBase):
    '''
    Utility for restoration
    '''

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmRecoverUtilACL, self).__init__()

    @decorater_log
    def _create_recover_ec_message(self, ec_message, db_info):
        '''
        Create ACL configuration message for restoration
        Parameter:
            ec_message : EC message for "recover service"
            db_info : DB information
        Return value :
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
                "device":
                {
                    "name": None,
                    "filter": []
                }
            }

        self._gen_json_name(return_ec_message, db_info, ec_message)

        self._gen_json_filter(return_ec_message, db_info, ec_message)

        if len(return_ec_message["device"].get("filter", [])) == 0:
            self.common_util_log.logging(" ", self.log_level_debug,
                                         "Need not recover ACL.", __name__)

            return True, None

        self.common_util_log.logging(
            " ", self.log_level_debug,
            "return_ec_message = %s" % return_ec_message, __name__)

        return True, json.dumps(return_ec_message)

    @decorater_log
    def _create_recover_db_info(self, ec_message, db_info):
        '''
        Create ACL configuration information for restoration
        Parameter:
            ec_message : EC message for "recover service"
            db_info : DB informaiton
        Return value :
            Result : Success：True  Failure：False
            DB information for restoration(JSON)
        '''
        return_db_info = db_info.get(self.name_acl_filter)
        for acl_info in return_db_info.get("acl-info"):
            acl_info["if-name"] = self._convert_ifname(
                acl_info.get("if-name"), ec_message)

        if return_db_info.get("cp_if_name_list"):
            tmp_if_list = []
            for cp_if_name in return_db_info.get("cp_if_name_list"):
                cp_if_name = self._convert_ifname(cp_if_name, ec_message)
                tmp_if_list.append(cp_if_name)
            return_db_info["cp_if_name_list"] = tmp_if_list

        self.common_util_log.logging(
            " ", self.log_level_debug,
            "return_db_info = %s" % return_db_info, __name__)

        return True, json.dumps(return_db_info)

    @decorater_log
    def _gen_json_filter(self, json, db_info, ec_message):
        '''
            Set the ACL configuration information to EC message storage dictionary object
            to be used for restoration based on EC message for restoration/"recover service"
            and DB information
            Parameter：
                json：EC message storage dictionary object
                db_info : DB information
                ec_message : EC message for restoration/"recover service"
        '''
        acl_filters_db = db_info.get(self.name_acl_filter, {})

        for acl_filter_db in acl_filters_db.get("acl-info", []):
            acl_filter_message = \
                {
                    "filter-id": None,
                    "term": []
                }

            acl_filter_message["filter-id"] = acl_filter_db.get("filter-id")

            self._gen_json_term(acl_filter_message, acl_filter_db, ec_message)

            json["device"]["filter"].append(acl_filter_message)

    @decorater_log
    def _gen_json_term(self, json, db_info, ec_message):
        '''
            Set the term information to EC message storage dictionary object
            to be used for restoration based on EC message for restoration/"recover service"
            and DB information
            Explanation about Parameter：
                json：EC message storage dictionary object
                db_info : DB information
                ec_message : EC message for restoration/"recover service"
        '''
        if_name_db = self._convert_ifname(db_info.get("if-name"), ec_message)
        vlan_id_db = db_info.get("vlan-id")
        vlan_id = None
        if vlan_id_db:
            vlan_id = int(vlan_id_db)
        for term_db in db_info.get("term", []):
            term_message = \
                {
                    "term-name": None,
                    "name": if_name_db,
                    "vlan-id": vlan_id,
                    "action": None,
                    "direction": None
                }
            term_message["term-name"] = term_db.get("term-name")
            term_message["action"] = term_db.get("action")
            term_message["direction"] = term_db.get("direction")
            if term_db.get("source-mac-address"):
                source_mac_address = term_db.get("source-mac-address")
                term_message["source-mac-address"] =\
                    self._analysis_address(source_mac_address)
            if term_db.get("destination-mac-address"):
                destination_mac_address = term_db.get(
                    "destination-mac-address")
                term_message["destination-mac-address"] =\
                    self._analysis_address(destination_mac_address)
            if term_db.get("source-port"):
                term_message["source-port"] = term_db.get("source-port")
            if term_db.get("destination-port"):
                term_message["destination-port"] =\
                    term_db.get("destination-port")
            if term_db.get("source-ip-address"):
                source_ip_address = term_db.get("source-ip-address")
                term_message["source-ip-address"] =\
                    self._analysis_ip_address(source_ip_address)
            if term_db.get("destination-ip-address"):
                destination_ip_address = term_db.get("destination-ip-address")
                term_message["destination-ip-address"] =\
                    self._analysis_ip_address(destination_ip_address)
            if term_db.get("protocol"):
                term_message["protocol"] = term_db.get("protocol")
            if term_db.get("priority"):
                term_message["priority"] = term_db.get("priority")

            json["term"].append(term_message)

    def _analysis_ip_address(self, ec_address):
        '''
            Judge IPv4/IPv6, and divide address and prefix using /
        '''
        tmp_addr = self._analysis_address(ec_address)
        if tmp_addr.get("address").find(':') > -1:
            ip_version = "6"
        else:
            ip_version = "4"
        tmp_addr["ip_version"] = int(ip_version)

        return tmp_addr

    def _analysis_address(self, ec_address):
        '''
            Divide address/prefix
        '''
        address, _, prefix = ec_address.rpartition("/")
        tmp_addr = {
            "address": address,
            "prefix": int(prefix)
        }
        return tmp_addr
