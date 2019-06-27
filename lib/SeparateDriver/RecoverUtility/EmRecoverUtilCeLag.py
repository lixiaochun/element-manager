# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmRecoverUtilCeLag.py
'''
Utility for restoration(LAG addition for CE)
'''

import json
import EmRecoverUtilBase
from EmCommonLog import decorater_log


class EmRecoverUtilCeLag(EmRecoverUtilBase.EmRecoverUtilBase):
    '''
    Utility for restoration
    '''

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmRecoverUtilCeLag, self).__init__()

    @decorater_log
    def _create_recover_ec_message(self, ec_message, db_info):
        '''
        Create CELAG addition EC message for restoration
        Parameter:
            ec_message : EC message for "recover service"
            db_info : DB information
        Return Value :
            ec_message : Success：True  Failure：False
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
    def _create_recover_db_info(self, ec_message, db_info):
        '''
        Create CELAG addition DB information for restoration
        Parameter:
            ec_message : EC message for "recover service"
            db_info : DB information
        Return Value :
            Result : Success：True  Failure：False
            DB information for restoration(JSON)
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
    def _gen_json_ce_lag_if(self, json, db_info, ec_message):
        '''
            Set the LAG information for CE to EC message storage dictionary object
            to be used for restoration based on restoration expansion/EC message for "recover service"
            and DB information
            Explanation about parameter：
                json：EC message storage dictionary object
                db_info : DB information
                ec_message : EC message for restoration expansion/"recover service"
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
