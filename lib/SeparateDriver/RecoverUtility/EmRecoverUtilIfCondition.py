# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmRecoverUtilIfCondition.py
'''
Recovering Utility(for opening and closing IF)
'''

import json
import EmRecoverUtilBase
import GlobalModule
from EmCommonLog import decorater_log


class EmRecoverUtilIfCondition(EmRecoverUtilBase.EmRecoverUtilBase):
    '''
    Recovering Utility
    '''
    __if_condition_disable = "disable"
    __if_type_dict = {
        "physical-interface": "interface-physical",
        "lag": "internal-lag"
    }

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmRecoverUtilIfCondition, self).__init__()
        self.name_if_condition = GlobalModule.SERVICE_IF_CONDITION

    @decorater_log
    def _create_recover_ec_message(self, ec_message, db_info):
        '''
        Message for opening and closing IF in recovering mode is generated.
        Argument:
            ec_message : EC message for resetting service
            db_info : DB information
        Return value:
            result : success：True  fail：False
            EC message for recovering(JSON)
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
                    "interface-physical_value": 0,
                    "interface-physical": [],
                    "internal-lag_value": 0,
                    "internal-lag": []
                }
            }

        self._gen_json_name(return_ec_message, db_info, ec_message)

        self._gen_json_if_condition(return_ec_message, db_info, ec_message)

        if (return_ec_message["device"]["interface-physical_value"] == 0) and\
                (return_ec_message["device"]["internal-lag_value"] == 0):
            self.common_util_log.logging(" ", self.log_level_debug,
                                         "Need not recover Interface-Condition.",
                                         __name__)

            return True, None

        self.common_util_log.logging(
            " ", self.log_level_debug,
            "return_ec_message = %s" % return_ec_message, __name__)

        return True, json.dumps(return_ec_message)

    @decorater_log
    def _create_recover_db_info(self, ec_message, db_info):
        '''
        Information for opening and closing IF in recovering mode is generated.
        Argument:
            ec_message : EC message for resetting service
            db_info : DB information
        Return value:
            result : success：True  fail：False
            DB information for recovering(JSON)
        '''
        return_db_info = db_info.get(self.name_if_condition)
        for phy_if in return_db_info.get("physical-interface"):
            phy_if["if_name"] = self._convert_ifname(
                phy_if.get("if_name"), ec_message, self._if_type_phy)
        for lag_if in return_db_info.get("lag"):
            lag_if["if_name"] = self._convert_ifname(
                lag_if.get("if_name"), ec_message, self._if_type_lag)

        self.common_util_log.logging(
            " ", self.log_level_debug,
            "return_db_info = %s" % return_db_info, __name__)

        return True, json.dumps(return_db_info)

    @decorater_log
    def _gen_json_if_condition(self, json, db_info, ec_message):
        '''
            Based on EC message for resetting servce to increase device in recovering mode
            and DB information, 
            IF status(open/close) is to set to dictionary object which stores EC message. 
            Argument:
                json：dictionary object which stores EC message
                db_info : DB information
                ec_message :  EC message for resetting service to add device in recovering mode
        '''

        self._gen_json_if_condition_type(
            json, db_info, ec_message, "physical-interface", self._if_type_phy)
        json["device"]["interface-physical_value"] = \
            len(json["device"]["interface-physical"])

        self._gen_json_if_condition_type(
            json, db_info, ec_message, "lag", self._if_type_lag)
        json["device"]["internal-lag_value"] = \
            len(json["device"]["internal-lag"])

        self.common_util_log.logging(
            " ", self.log_level_debug,
            "json = %s" % json, __name__)

    @decorater_log
    def _gen_json_if_condition_type(self, json, db_info, ec_message,
                                    db_if_type, convert_if_type):
        '''
            Based on EC message for resetting servce to increase device in recovering mode
            and DB information, 
            IF status(open/close) is to set to dictionary object which stores EC message.
            Argument:
                json：dictionary object which stores EC message
                db_info : DB information
                ec_message : EC message for resetting service to add device in recovering mode
                db_if_type : name of list storing IF information in DB
                convert_if_type ：IF type to be corverted
        '''
        if_conditions_db = db_info.get(self.name_if_condition, {})
        for if_condition_db in if_conditions_db.get(db_if_type, []):
            if_condition_message = \
                {
                    "name": None,
                    "condition": None,
                }
            if if_condition_db.get("condition") == self.__if_condition_disable:
                old_name = if_condition_db.get("if_name")
                name = self._convert_ifname(
                    old_name, ec_message, convert_if_type)
                if_condition_message["name"] = name
                if_condition_message[
                    "condition"] = self.__if_condition_disable

                json["device"][self.__if_type_dict[db_if_type]].append(
                    if_condition_message)
