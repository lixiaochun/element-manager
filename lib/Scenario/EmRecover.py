#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2018 Nippon Telegraph and Telephone Corporation
# Filename: EmRecoverNode.py
'''
Base scenario for recover
'''

import json
import threading
from lxml import etree
import EmSeparateScenario
from EmCommonDriver import EmCommonDriver
import GlobalModule
from EmCommonLog import decorater_log


class EmRecover(EmSeparateScenario.EmScenario):

    '''
    Base scenario class for recover
    '''


    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmRecover, self).__init__()

        self.error_code_01 = "104001"
        self.error_code_02 = "204004"
        self.error_code_03 = "104002"

        self.timeout_flag = False

        self.device_type = "device"

    @decorater_log
    def _gen_sub_thread(
            self, device_message,
            transaction_id, order_type, condition, device_name, force):
        '''
        Control recovery processing.
        Explanation about parameter :
            device_message: Message for each device
            transaction_id: Transaction ID
            order_type: Order type
            condition: Thread control information
            device_name: Device name
            force: Forced deletion flag
        Explanation about return value :
            None
        '''

        GlobalModule.EM_LOGGER.info(
            "%s Scenario:%s Device:%s start",
            self.error_code_01, self.scenario_name, device_name)

        self.com_driver_list[device_name] = EmCommonDriver()

        order_type = "merge"

        is_db_result = \
            GlobalModule.EMSYSCOMUTILDB.write_transaction_device_status_list(
                "UPDATE", device_name, transaction_id,
                GlobalModule.TRA_STAT_PROC_RUN)

        if is_db_result is False:
            GlobalModule.EM_LOGGER.debug(
                " write_transaction_device_status_list(1:processing) NG")
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:13(Processing failure (temporary))",
                self.error_code_02, self.scenario_name, device_name)
            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code_03, self.scenario_name, device_name)
            return

        GlobalModule.EM_LOGGER.debug(
            "write_transaction_device_status_list(1:processing) OK")

        GlobalModule.EM_LOGGER.debug(
            "Start Getting Registered info")
        result_info, table_info =\
            GlobalModule.EMSYSCOMUTILDB.read_device_registered_info(
                device_name)
        if result_info is False:  
            GlobalModule.EM_LOGGER.debug(
                "read_device_registered_info NG")
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:13(Processing failure (temporary))",
                self.error_code_02, self.scenario_name, device_name)
            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code_03, self.scenario_name, device_name)
            return
        if table_info == "" or table_info is None:
            GlobalModule.EM_LOGGER.debug(
                " read_device_registered_info data not found NG")
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:13(rocessing failure (temporary))",
                self.error_code_02, self.scenario_name, device_name)
            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code_03, self.scenario_name, device_name)
            return
        table_info_dict = {}
        for element in table_info:
            table_info_dict.update(element)

        json_message = self._creating_json(device_message, table_info_dict)
        GlobalModule.EM_LOGGER.debug("json_message =%s", json_message)

        is_comdriver_result = self.com_driver_list[device_name].start(
            "", json_message)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("start NG")
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:13(rocessing failure (temporary))",
                self.error_code_02, self.scenario_name, device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code_03, self.scenario_name, device_name)
            return

        GlobalModule.EM_LOGGER.debug("start OK")


        is_comdriver_result = self.com_driver_list[device_name].connect_device(
            "", self.service, order_type, json_message)

        if is_comdriver_result == GlobalModule.COM_CONNECT_NG:
            GlobalModule.EM_LOGGER.debug("connect_device Device Connection NG")
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:14(Processing failure (Other))",
                self.error_code_02, self.scenario_name, device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code_03, self.scenario_name, device_name)
            return

        elif is_comdriver_result == GlobalModule.COM_CONNECT_NO_RESPONSE:
            GlobalModule.EM_LOGGER.debug("connect_device no reply")
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:13(Processing failure (temporary))",
                self.error_code_02, self.scenario_name, device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code_03, self.scenario_name, device_name)
            return

        GlobalModule.EM_LOGGER.debug("connect_device OK")

        is_db_result = \
            GlobalModule.EMSYSCOMUTILDB.write_transaction_device_status_list(
                "UPDATE", device_name, transaction_id,
                GlobalModule.TRA_STAT_EDIT_CONF)

        if is_db_result is False:
            GlobalModule.EM_LOGGER.debug(
                "write_transaction_device_status_list(2:Edit-config) NG")
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:14(Processing failure (Other))",
                self.error_code_02, self.scenario_name, device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 True, True)

            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code_03, self.scenario_name, device_name)
            return

        GlobalModule.EM_LOGGER.debug(
            "write_transaction_device_status_list(2:Edit-config) OK")

        is_comdriver_result = self.com_driver_list[
            device_name].update_device_setting(
                device_name, self.service, order_type, json_message)

        if is_comdriver_result == GlobalModule.COM_UPDATE_VALICHECK_NG:
            GlobalModule.EM_LOGGER.debug(
                "update_device_setting validation check NG")
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:9(Processing failure(validation check NG))",
                self.error_code_02, self.scenario_name, device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_CHECK,
                                 True, False)

            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code_03, self.scenario_name, device_name)
            return

        elif is_comdriver_result == GlobalModule.COM_UPDATE_NG:
            GlobalModule.EM_LOGGER.debug("update_device_setting update error")
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:13(Processing failure (temporary))",
                self.error_code_02, self.scenario_name, device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 True, False)

            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code_03, self.scenario_name, device_name)
            return

        GlobalModule.EM_LOGGER.debug("update_device_setting OK")

        is_db_result = \
            GlobalModule.EMSYSCOMUTILDB.write_transaction_device_status_list(
                "UPDATE", device_name, transaction_id,
                GlobalModule.TRA_STAT_CONF_COMMIT)

        if is_db_result is False:
            GlobalModule.EM_LOGGER.debug(
                "write_transaction_device_status_list(3:Confirmed-commit) NG")
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:14(Processing failure (Other))",
                self.error_code_02, self.scenario_name, device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 True, True)

            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code_03, self.scenario_name, device_name)
            return

        GlobalModule.EM_LOGGER.debug(
            "write_transaction_device_status_list(3:Confirmed-commit) OK")

        is_comdriver_result = self.com_driver_list[
            device_name].reserve_device_setting(
                device_name, self.service, order_type)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("reserve_device_setting NG")
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:13(Processing failure (temporary))",
                self.error_code_02, self.scenario_name, device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 True, False)

            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code_03, self.scenario_name, device_name)
            return

        GlobalModule.EM_LOGGER.debug("reserve_device_setting OK")

        is_config_result, return_value = \
            GlobalModule.EM_CONFIG.read_sys_common_conf(
                "Timer_confirmed-commit")
        is_config_result_second, return_value_em_offset = \
            GlobalModule.EM_CONFIG.read_sys_common_conf(
                "Timer_confirmed-commit_em_offset")

        if is_config_result is True and is_config_result_second is True:
            GlobalModule.EM_LOGGER.debug("read_sys_common_conf OK")

            return_value = (return_value + return_value_em_offset) / 1000

        else:
            GlobalModule.EM_LOGGER.debug("read_sys_common_conf NG")

            return_value = 600

        timer = threading.Timer(return_value, self._find_timeout,
                                args=[condition])
        timer.start()

        is_db_result = \
            GlobalModule.EMSYSCOMUTILDB.write_transaction_device_status_list(
                "UPDATE", device_name, transaction_id,
                GlobalModule.TRA_STAT_COMMIT)

        if is_db_result is False:
            timer.cancel()

            GlobalModule.EM_LOGGER.debug(
                "write_transaction_device_status_list(4:Commit) NG")
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:14(Processing failure (Other))",
                self.error_code_02, self.scenario_name, device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 True, True)

            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code_03, self.scenario_name, device_name)
            return

        GlobalModule.EM_LOGGER.debug(
            "write_transaction_device_status_list(4:Commit) OK")

        GlobalModule.EM_LOGGER.debug("Condition wait")
        condition.acquire()
        condition.wait()
        condition.release()
        GlobalModule.EM_LOGGER.debug("Condition notify restart")

        if self.timeout_flag is True:
            GlobalModule.EM_LOGGER.info(
                "104003 Rollback for Device:%s", device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_ROLL_BACK_END,
                                 True, False)

            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code_03, self.scenario_name, device_name)
            return

        GlobalModule.EM_LOGGER.debug("No timeout detection")

        timer.cancel()

        is_comdriver_result = self.com_driver_list[
            device_name].enable_device_setting(
                device_name, self.service, order_type)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("enable_device_setting NG")
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:13(Processing failure (temporary))",
                self.error_code_02, self.scenario_name, device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 True, False)

            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code_03, self.scenario_name, device_name)
            return

        GlobalModule.EM_LOGGER.debug("enable_device_setting OK")

        is_comdriver_result = self.com_driver_list[
            device_name].disconnect_device(
                device_name, self.service, order_type)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("disconnect_device NG")
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:13(Processing failure (temporary))",
                self.error_code_02, self.scenario_name, device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code_03, self.scenario_name, device_name)
            return

        GlobalModule.EM_LOGGER.debug("disconnect_device OK")

        is_db_result = \
            GlobalModule.EMSYSCOMUTILDB.write_transaction_device_status_list(
                "UPDATE", device_name, transaction_id,
                GlobalModule.TRA_STAT_PROC_END)

        if is_db_result is False:
            GlobalModule.EM_LOGGER.debug(
                "write_transaction_device_status_list(5:Successful completion) NG")
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:13(Processing failure (temporary))",
                self.error_code_02, self.scenario_name, device_name)
            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code_03, self.scenario_name, device_name)
            return

        GlobalModule.EM_LOGGER.debug(
            "write_transaction_device_status_list(5:Successful completion) OK")

        is_comdriver_result = self._write_em_info(
            device_name, self.service, order_type, device_message)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("write_em_info NG")
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:14(Processing failure (Other))",
                self.error_code_02, self.scenario_name, device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code_03, self.scenario_name, device_name)
            return

        GlobalModule.EM_LOGGER.debug("write_em_info OK")

        GlobalModule.EM_LOGGER.info(
            "%s Scenario:%s Device:%s end",
            self.error_code_03, self.scenario_name, device_name)
        return

    @decorater_log
    def _find_timeout(self, condition):
        '''
        Set time out flag and launch thread.
        Explanation about parameter:
            condition: Thread control information
        Explanation about return value:
            None
        '''

        GlobalModule.EM_LOGGER.debug("Timeout detected")

        self.timeout_flag = True

        GlobalModule.EM_LOGGER.debug("Condition acquire notify release")
        condition.acquire()
        condition.notify()
        condition.release()

    @decorater_log
    def _judg_transaction_status(self, transaction_status):
        '''
        Make judgment on transaction status of transaction management information table.
        Explanation about parameter:
            transaction_status: Transaction status
        Explanation about return value:
            Necessity for updating transaction status : boolean (True:Update necessary,False:Update unnecessary)
        '''


        GlobalModule.EM_LOGGER.debug(
            "transaction_status:%s", transaction_status)

        transaction_status_list = [GlobalModule.TRA_STAT_PROC_RUN,
                                   GlobalModule.TRA_STAT_EDIT_CONF,
                                   GlobalModule.TRA_STAT_CONF_COMMIT,
                                   GlobalModule.TRA_STAT_COMMIT]

        if transaction_status in transaction_status_list:

            GlobalModule.EM_LOGGER.debug("transaction_status Match")

            return True  

        GlobalModule.EM_LOGGER.debug("transaction_status UNMatch")
        return False  

    @decorater_log
    def _creating_json(self, device_message, table_info_dict):
        '''
        Generates JSON using EC message (XML) divided for each device and
        device registration information acquired from DB.
        Explanation about parameter:
            device_message: Message for each device
            table_info_dict: Device registration information acquired from DB
        Explanation about return value:
            device_json_message: JSON message
        '''

        device_json_message = \
            {
                "device":
                {
                    "name": None,
                    "node-type": None,
                    "equipment":
                    {
                        "platform": None,
                        "os": None,
                        "firmware": None,
                        "loginid": None,
                        "password": None
                    },
                    "management-interface":
                    {
                        "address": None,
                        "prefix": 0
                    },
                    "physical-ifs_value": 0,
                    "physical-ifs": [],
                    "lag-ifs_value": 0,
                    "lag-ifs": []
                }
            }

        xml_elm = etree.fromstring(device_message)

        GlobalModule.EM_LOGGER.debug(
            "device_message = %s", etree.tostring(xml_elm, pretty_print=True))

        self._gen_json_name(
            device_json_message, xml_elm, self._xml_ns)

        self._gen_json_node_type(
            device_json_message, xml_elm, self._xml_ns)

        self._gen_json_equipment(
            device_json_message, xml_elm, self._xml_ns)

        self._gen_json_management(
            device_json_message, xml_elm, self._xml_ns,
            table_info_dict)

        self._gen_json_if_convert_table(
            device_json_message, xml_elm, self._xml_ns, "physical-ifs")

        self._gen_json_if_convert_table(
            device_json_message, xml_elm, self._xml_ns, "lag-ifs")

        GlobalModule.EM_LOGGER.debug(
            "device__json_message = %s", device_json_message)

        return json.dumps(device_json_message)

    @decorater_log
    def _gen_json_name(self, json, xml, xml_ns):
        '''
            Obtain name information from xml message to be analyzed and
            set it for EC message storage dictionary object.
            Explanation about paramete：
                json：Dictionary object for EC message storage
                xml：Xml message to be analyzed
                xml_ns：Name space
        '''

        name_elm = self._find_xml_node(xml, xml_ns + "name")
        json["device"]["name"] = name_elm.text

    @decorater_log
    def _gen_json_node_type(self, json, xml, xml_ns):
        '''
            Obtain device type information from xml message to be analyzed and
            set it for EC message storage dictionary object.
            Explanation about paramete：
                json：Dictionary object for EC message storage
                xml：Xml message to be analyzed
                xml_ns：Name space
        '''

        name_elm = self._find_xml_node(xml, xml_ns + "node-type")
        json["device"]["node-type"] = name_elm.text

    @decorater_log
    def _gen_json_equipment(self, json, xml, xml_ns):
        '''
            Obtain device connection information from xml message to be analyzed and
            set it for EC message storage dictionary object.
            Explanation about paramete：
                json：Dictionary object for EC message storage
                xml：Xml message to be analyzed
                xml_ns：Name space
        '''

        equ_elm = self._find_xml_node(xml, xml_ns + "equipment")
        equ_json = json["device"]["equipment"]
        equ_json["platform"] = \
            equ_elm.find(xml_ns + "platform").text
        equ_json["os"] = \
            equ_elm.find(xml_ns + "os").text
        equ_json["firmware"] = \
            equ_elm.find(xml_ns + "firmware").text
        equ_json["loginid"] = \
            equ_elm.find(xml_ns + "loginid").text
        equ_json["password"] = \
            equ_elm.find(xml_ns + "password").text

    @decorater_log
    def _gen_json_management(self, json, xml, xml_ns, db_info):
        '''
            Obtain management IF information from xml message to be analyzed and
            set it for EC message storage dictionary object.
            Explanation about paramete：
                json：Dictionary object for EC message storage
                xml：Xml message to be analyzed
                xml_ns：Name space
                db_info：DB information
        '''
        man_json = json["device"]["management-interface"]
        man_json["address"] = db_info.get("mgmt_if_address")
        man_json["prefix"] = db_info.get("mgmt_if_prefix")

    @decorater_log
    def _gen_json_if_convert_table(self,
                                   json,
                                   xml,
                                   xml_ns,
                                   convert_table_name):
        '''
            Obtain Conversion table (PhyicalIF/LAGIF) from xml message to be analyzed and
            set it for EC message storage dictionary object.
            Explanation about paramete：
                json：Dictionary object for EC message storage
                xml：Xml message to be analyzed
                xml_ns：Name space
                convert_table_name：Conversion table name
        '''
        if_convert_elm = self._find_xml_node(xml,
                                             xml_ns + convert_table_name)

        if if_convert_elm is not None:
            if_convert_tag = xml_ns + convert_table_name
            for if_convert in xml.findall(".//" + if_convert_tag):
                name = if_convert.find(xml_ns + "name").text
                old_name = if_convert.find(xml_ns + "old-name").text
                json["device"][convert_table_name].append(
                    {"name": name,
                     "old-name": old_name})
        json["device"][convert_table_name + "_value"] = \
            len(json["device"][convert_table_name])

    @decorater_log
    def _write_em_info(self, device_name, service, order_type, device_message):
        '''
        EM Information Update
            Gets launched from each scenario individual processing,
            and launches EM designation information reading of common utility (DB) across the system
            To implement it from the derivative side.
        Argument:
            device_name: str equipment name
            service_type: str type of service
            order_type: str type of order
            ec_message: str EC message (xml)
        Return value:
            boolean method results.
                true: Normal
                false: Abnormal
        '''
        pass
