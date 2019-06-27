# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmRecoverUtilClusterLink.py
'''
Utility for restoration(Inter-cluster link creation)
'''

import json
import EmRecoverUtilBase
from EmCommonLog import decorater_log


class EmRecoverUtilClusterLink(EmRecoverUtilBase.EmRecoverUtilBase):
    '''
    Utility for restoration
    '''

    @decorater_log
    def __init__(self):
        '''   
        Constructor
        '''

        super(EmRecoverUtilClusterLink, self).__init__()

    @decorater_log
    def _create_recover_ec_message(self, ec_message, db_info):
        '''
        Create inter-cluster link generation EC message for restoration
        Parameter:
            ec_message : EC message for "recover service"
            db_info : DB information
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
    def _create_recover_db_info(self, ec_message, db_info):
        '''
        Create inter-cluster link creation DB information for restoration
        Parameter:
            ec_message : EC message for "recover service"
            db_info : DB information
        Return Value :
            Result : Success：True  Failure：False
            DB information for restoration(JSON)
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
    def _gen_json_cluster_link_phy(self, json, db_info, ec_message):
        '''
            Set the inter-cluster link information (physical) to the EC message storage dictionary object
            to be used for restoration based on restoration expansion/EC message for "recover service"
            and DB information
            Explanation about parameter：
                json：EC message storage dictionary object
                db_info : DB information
                ec_message : EC message for restoration expansion/"recover service"
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
            Set the inter-cluster link information (LAG) to the EC message storage dictionary object
            to be used for restoration based on restoration expansion/EC message for "recover service"
            and DB information
            Explanation about parameter：
                json：EC message storage dictionary object
                db_info : DB information
                ec_message : EC message for restoration expansion/"recover service"
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
