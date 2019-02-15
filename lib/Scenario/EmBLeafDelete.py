#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2018 Nippon Telegraph and Telephone Corporation
# Filename: EmBLeafDelete.py
'''
Individual scenario for B-Leaf reduction.
'''
import threading
from EmBLeafUpdate import EmBLeafUpdate
from EmCommonDriver import EmCommonDriver
import GlobalModule
from EmCommonLog import decorater_log
from lxml import etree


class EmBLeafDelete(EmBLeafUpdate):
    '''
    B-Leaf B-Leaf reduction class
    '''

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
            force: Forced deletion flag
        Explanation about return value:
            None
        '''
        xml_elm = etree.fromstring(device_message)
        ospf_elm = self._find_xml_node(xml_elm, self._xml_ns + "ospf")
        if ospf_elm is not None:
            GlobalModule.EM_LOGGER.debug('OSPF tag EXIST')
            super(EmBLeafDelete, self)._gen_sub_thread(device_message,
                                                       transaction_id,
                                                       order_type,
                                                       condition,
                                                       device_name,
                                                       force)

        else:
            GlobalModule.EM_LOGGER.debug('OSPF tag NOT EXIST')
            self._gen_sub_thread_b_leaf_delete(device_message,
                                               transaction_id,
                                               order_type,
                                               condition,
                                               device_name,
                                               force)

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''
        super(EmBLeafDelete, self).__init__()

        self.scenario_name = "B-LeafDelete"

        self.service = GlobalModule.SERVICE_B_LEAF

        self._xml_ns = "{%s}" % GlobalModule.EM_NAME_SPACES[self.service]

        self.error_code_01 = "104001"
        self.error_code_02 = "104002"
        self.error_code_03 = "204004"

        self.device_type = "device"

    @decorater_log
    def _gen_sub_thread_b_leaf_delete(
            self, device_message,
            transaction_id, order_type, condition, device_name, force):
        '''
        Conduct B-Leaf reduction control for each device.
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
            self.error_code_01, self.scenario_name, device_name)

        self.com_driver_list[device_name] = EmCommonDriver()

        is_db_result = \
            GlobalModule.EMSYSCOMUTILDB.write_transaction_device_status_list(
                "UPDATE", device_name, transaction_id,
                GlobalModule.TRA_STAT_PROC_RUN)

        if is_db_result is False:
            GlobalModule.EM_LOGGER.debug(
                " write_transaction_device_status_list(1: During processing) NG")
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:13(Processing failed (temporal))",
                self.error_code_03, self.scenario_name, device_name)
            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code_02, self.scenario_name, device_name)
            return

        GlobalModule.EM_LOGGER.debug(
            "write_transaction_device_status_list(1: During processing) OK")

        is_comdriver_result = self.com_driver_list[device_name].start(
            device_name)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("start NG")
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:13(Processing failed (temporal))",
                self.error_code_03, self.scenario_name, device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code_02, self.scenario_name, device_name)
            return

        GlobalModule.EM_LOGGER.debug("start OK")

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
                "104002 Scenario:B-LeafDelete Device:%s end",
                device_name)
            return

        GlobalModule.EM_LOGGER.debug("Timeout detection None")

        timer.cancel()

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
        Make judgment on transaction status
        of transaction management information table.
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

    @decorater_log
    def _find_timeout(self, condition):
        '''
        Set timeout flag and launch thread.
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
