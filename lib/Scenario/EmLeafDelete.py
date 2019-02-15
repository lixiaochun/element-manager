#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2018 Nippon Telegraph and Telephone Corporation
# Filename: EmLeafDelete.py
'''
Individual scenario for reducing Leaf.
'''
import EmSeparateScenario
from EmCommonDriver import EmCommonDriver
import GlobalModule
from EmCommonLog import decorater_log


class EmLeafDelete(EmSeparateScenario.EmScenario):
    '''
    Class for reducing Leaf.
    '''

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''
        super(EmLeafDelete, self).__init__()

        self.scenario_name = "LeafDelete"

        self.service = GlobalModule.SERVICE_LEAF

        self._xml_ns = "{%s}" % GlobalModule.EM_NAME_SPACES[self.service]

        self.error_code_01 = "104001"
        self.error_code_02 = "104002"
        self.error_code_03 = "204004"

        self.device_type = "device"

    @decorater_log
    def _gen_sub_thread(
            self, device_message,
            transaction_id, order_type, condition, device_name, force):
        '''
        Conduct Leaf reduction control for each device.
        Explanation about parameter:
            device_message: Message for each device
            transaction_id: Transaction ID
            order_type: Order type
            condition: Thread control information
            device_name: Device name
            force: Forced deletion flag (True:Valid,False:Invalid)
        Explanation about return value:
            None
        '''

        GlobalModule.EM_LOGGER.info(
            "%s Scenario:%s Device:%s start",
            self.error_code_01, self.scenario_name, device_name)

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
                self.error_code_03, self.scenario_name, device_name)
            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code_02, self.scenario_name, device_name)
            return

        GlobalModule.EM_LOGGER.debug(
            "write_transaction_device_status_list(1:processing) OK")

        is_comdriver_result = self.com_driver_list[device_name].start(
            device_name)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("start NG")
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:13(Processing failure (temporary))",
                self.error_code_03, self.scenario_name, device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code_02, self.scenario_name, device_name)
            return

        GlobalModule.EM_LOGGER.debug("start OK")

        is_db_result = \
            GlobalModule.EMSYSCOMUTILDB.write_transaction_device_status_list(
                "UPDATE", device_name, transaction_id,
                GlobalModule.TRA_STAT_PROC_END)

        if is_db_result is False:
            GlobalModule.EM_LOGGER.debug(
                "write_transaction_device_status_list(5:Successful completion) NG")
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:13(Processing failure (temporary))",
                self.error_code_03, self.scenario_name, device_name)
            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code_02, self.scenario_name, device_name)
            return

        GlobalModule.EM_LOGGER.debug(
            "write_transaction_device_status_list(5:Successful completion) OK")

        is_comdriver_result = self.com_driver_list[device_name].write_em_info(
            device_name, self.service, order_type, device_message)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("write_em_info NG")
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:14(Processing failure (Other))",
                self.error_code_03, self.scenario_name, device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code_02, self.scenario_name, device_name)
            return

        GlobalModule.EM_LOGGER.debug("write_em_info OK")

        GlobalModule.EM_LOGGER.info(
            "%s Scenario:%s Device:%s end",
            self.error_code_02, self.scenario_name, device_name)
        return

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

        transaction_status_list = [GlobalModule.TRA_STAT_PROC_RUN]

        if transaction_status in transaction_status_list:

            GlobalModule.EM_LOGGER.debug("transaction_status Match")

            return True

        GlobalModule.EM_LOGGER.debug("transaction_status UNMatch")
        return False
