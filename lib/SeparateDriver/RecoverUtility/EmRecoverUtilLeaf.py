# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2018 Nippon Telegraph and Telephone Corporation
# Filename: EmRecoverUtilLeaf.py
'''
Utility for restoration(Leaf expansion)
'''

import json
import EmRecoverUtilBase
from EmCommonLog import decorater_log


class EmRecoverUtilLeaf(EmRecoverUtilBase.EmRecoverUtilBase):
    '''
    Utility for restoration
    '''

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmRecoverUtilLeaf, self).__init__()

    @decorater_log
    def _create_recover_ec_message(self, ec_message, db_info):
        '''
        EC message for restoration
        Parameter:
            ec_message : EC message for restoration expansion
            db_info : DB information
        Return Value :
            Result : Success�FTrue  Failure�FFalse
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
