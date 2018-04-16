#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2018 Nippon Telegraph and Telephone Corporation
# Filename: EmMargeScenario.py
'''
Class which is common for scenario creation.
'''
import threading
import EmSeparateScenario
from EmCommonDriver import EmCommonDriver
import GlobalModule
from EmCommonLog import decorater_log


class EmMergeScenario(EmSeparateScenario.EmScenario):
    '''
    Class which is common for scenario creation.
    '''

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''
        super(EmMergeScenario, self).__init__()
        self._xml_ns = ""
        self.timeout_flag = False
        self._scenario_name = ""
        self.service = ""
        self.error_code01 = "104001"
        self.error_code02 = "204004"
        self.error_code03 = "104002"

    @decorater_log
    def _gen_sub_thread(
            self, device_message,
            transaction_id, order_type, condition, device_name, force):
        '''
        Conduct creation control for each device.
        Explanation about parameter:
            device_message: Message for each device
            transaction_id: Transaction ID
            order_type: Order type
            condition: Thread control information
            device_name: Device name
            force: Forced deletion flag
        Explanation about return value:
            None
        '''

        GlobalModule.EM_LOGGER.info(
            "%s Scenario:%s Device:%s start",
            self.error_code01, self._scenario_name, device_name)

        self.com_driver_list[device_name] = EmCommonDriver()

        is_db_result = \
            GlobalModule.EMSYSCOMUTILDB.write_transaction_device_status_list(
                "UPDATE", device_name, transaction_id,
                GlobalModule.TRA_STAT_PROC_RUN)

        if is_db_result is False:
            GlobalModule.EM_LOGGER.debug(
                " write_transaction_device_status_list(1:processing) NG")
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:13(Processing failure (temporary))",
                self.error_code02, self._scenario_name, device_name)
            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code03, self._scenario_name, device_name)
            return

        GlobalModule.EM_LOGGER.debug(
            "write_transaction_device_status_list(1:processing) OK")

        json_message = self._creating_json(device_message)
        GlobalModule.EM_LOGGER.debug("json_message =%s", json_message)

        is_comdriver_result = self.com_driver_list[device_name].start(
            device_name, json_message)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("start NG")
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:13(Processing failure (temporary))",
                self.error_code02, self._scenario_name, device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code03, self._scenario_name, device_name)
            return

        GlobalModule.EM_LOGGER.debug("start OK")

        is_comdriver_result = self.com_driver_list[device_name].connect_device(
            device_name, self.service, order_type, json_message)

        if is_comdriver_result == GlobalModule.COM_CONNECT_NG:
            GlobalModule.EM_LOGGER.debug("connect_device NG")
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:14(Processing failure (Other))",
                self.error_code02, self._scenario_name, device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code03, self._scenario_name, device_name)
            return

        elif is_comdriver_result == GlobalModule.COM_CONNECT_NO_RESPONSE:
            GlobalModule.EM_LOGGER.debug("connect_device no reply")
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:13(Processing failure (temporary))",
                self.error_code02, self._scenario_name, device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code03, self._scenario_name, device_name)
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
                self.error_code02, self._scenario_name, device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 True, True)

            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code03, self._scenario_name, device_name)
            return

        GlobalModule.EM_LOGGER.debug(
            "write_transaction_device_status_list(2:Edit-config) OK")

        is_comdriver_result = self.com_driver_list[
            device_name].update_device_setting(
                device_name, self.service, order_type, json_message)

        if is_comdriver_result == GlobalModule.COM_UPDATE_VALICHECK_NG:
            GlobalModule.EM_LOGGER.debug("update_device_setting validation check NG")
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:9(Processing failure(validation check NG))",
                self.error_code02, self._scenario_name, device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_CHECK,
                                 True, False)

            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code03, self._scenario_name, device_name)
            return

        elif is_comdriver_result == GlobalModule.COM_UPDATE_NG:
            GlobalModule.EM_LOGGER.debug("update_device_setting error")
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:13(Processing failure (temporary))",
                self.error_code02, self._scenario_name, device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 True, False)

            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code03, self._scenario_name, device_name)
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
                self.error_code02, self._scenario_name, device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 True, True)

            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code03, self._scenario_name, device_name)
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
                self.error_code02, self._scenario_name, device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 True, False)

            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code03, self._scenario_name, device_name)
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
                self.error_code02, self._scenario_name, device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 True, True)

            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code03, self._scenario_name, device_name)
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
                self.error_code03, self._scenario_name, device_name)
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
                self.error_code02, self._scenario_name, device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 True, False)

            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code03, self._scenario_name, device_name)
            return

        GlobalModule.EM_LOGGER.debug("enable_device_setting OK")

        is_comdriver_result = self.com_driver_list[
            device_name].disconnect_device(
                device_name, self.service, order_type)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("disconnect_device NG")
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:13(Processing failure (temporary))",
                self.error_code02, self._scenario_name, device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code03, self._scenario_name, device_name)
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
                self.error_code02, self._scenario_name, device_name)
            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code03, self._scenario_name, device_name)
            return

        GlobalModule.EM_LOGGER.debug(
            "write_transaction_device_status_list(5:Successful completion) OK")

        is_comdriver_result = self.com_driver_list[device_name].write_em_info(
            device_name, self.service, order_type, device_message)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("write_em_info NG")
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:14(Processing failure (Other))",
                self.error_code02, self._scenario_name, device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code03, self._scenario_name, device_name)
            return

        GlobalModule.EM_LOGGER.debug("write_em_info OK")

        GlobalModule.EM_LOGGER.info(
            "%s Scenario:%s Device:%s end",
            self.error_code03, self._scenario_name, device_name)
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
        Make judgment on transaction status of
        transaction management information table.
        Explanation about parameter:
            transaction_status: Transaction status
        Explanation about return value:
            Necessity for updating transaction status :
                boolean (True:Update necessary,False:Update unnecessary)
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
    def _gen_json_name(self, json, xml, xml_ns):
        '''
            Obtain device name from xml message to be analyzed and
            set it for EC message storage dictionary object.
            Explanation about parameter:
                json:dictionary object for EC message storage
                xml:xml message to be analyzed
                xml_ns:Name space
                service:Service name
                order:Order name
        '''

        name_elm = self._find_xml_node(xml, xml_ns + "name")
        json["device"]["name"] = name_elm.text
