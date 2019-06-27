#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmL2SliceGet.py
'''
Individual scenario for information matching (L2 slice).
'''
import EmSeparateScenario
from EmCommonDriver import EmCommonDriver
import GlobalModule
from EmCommonLog import decorater_log


class EmL2SliceGet(EmSeparateScenario.EmScenario):
    '''
    Class for information matching (L2 slice).
    '''

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmL2SliceGet, self).__init__()

    @decorater_log
    def _gen_sub_thread(
            self, device_message,
            transaction_id, order_type, condition, device_name, force):
        '''
        Conduct information matching (L2 slice) control for each device.
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
            "104001 Scenario:L2SliceGet Device:%s start", device_name)

        self.com_driver_list[device_name] = EmCommonDriver()

        is_db_result = \
            GlobalModule.EMSYSCOMUTILDB.write_transaction_device_status_list(
                "UPDATE", device_name, transaction_id,
                GlobalModule.TRA_STAT_PROC_RUN)

        if is_db_result is False:
            GlobalModule.EM_LOGGER.debug(
                " write_transaction_device_status_list(1:processing) NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:L2SliceGet Device:%s NG:13(Processing failure(temporary))",
                device_name)
            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L2SliceGet Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug(
            "write_transaction_device_status_list(1:processing) OK")

        is_comdriver_result = self.com_driver_list[
            device_name].compare_to_db_info(
                device_name, "l2-slice", order_type, device_message)

        if is_comdriver_result == GlobalModule.COM_COMPARE_UNMATCH:
            GlobalModule.EM_LOGGER.debug("compare_to_db_info NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:L2SliceGet Device:%s NG:11(Processing failure（Consistent NG）)",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_MATCH,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L2SliceGet Device:%s end", device_name)
            return

        elif is_comdriver_result == GlobalModule.COM_COMPARE_NO_INFO:
            GlobalModule.EM_LOGGER.debug("compare_to_db_info NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:L2SliceGet Device:%s NG:12(Processing failure（No retention information）)",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_INF,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L2SliceGet Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug("compare_to_db_info OK")

        is_comdriver_result = self.com_driver_list[device_name].start(
            device_name)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("start NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:L2SliceGet Device:%s NG:13(Processing failure(temporary))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L2SliceGet Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug("start OK")

        is_comdriver_result = self.com_driver_list[device_name].connect_device(
            device_name, "l2-slice", order_type)

        if is_comdriver_result == GlobalModule.COM_CONNECT_NG:
            GlobalModule.EM_LOGGER.debug("connect_device NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:L2SliceGet Device:%s NG:14(Processing failure(Other))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L2SliceGet Device:%s end", device_name)
            return

        elif is_comdriver_result == GlobalModule.COM_CONNECT_NO_RESPONSE:
            GlobalModule.EM_LOGGER.debug("connect_device no reply")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:L2SliceGet Device:%s NG:13(Processing failure(temporary))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L2SliceGet Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug("connect_device OK")

        is_comdriver_result, return_device_signal = \
            self.com_driver_list[device_name].get_device_setting(
                device_name, "l2-slice", order_type)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("get_device_setting NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:L2SliceGet Device:%s NG:13(Processing failure(temporary))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 True, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L2SliceGet Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug("get_device_setting OK")

        is_comdriver_result = self.com_driver_list[
            device_name].compare_to_device_setting(
                device_name, "l2-slice", order_type, return_device_signal)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("compare_to_device_setting NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:L2SliceGet Device:%s NG:11(Processing failure（Consistent NG）)",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_MATCH,
                                 True, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L2SliceGet Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug("compare_to_device_setting OK")

        is_comdriver_result = self.com_driver_list[
            device_name].disconnect_device(device_name, "l2-slice", order_type)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("disconnect_device NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:L2SliceGet Device:%s NG:13(Processing failure(temporary))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L2SliceGet Device:%s end", device_name)
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
                "204004 Scenario:L2SliceGet Device:%s NG:13(Processing failure(temporary))",
                device_name)
            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L2SliceGet Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug(
            "write_transaction_device_status_list(5:Normal end) OK")

        GlobalModule.EM_LOGGER.info(
            "104002 Scenario:L2SliceGet Device:%s end", device_name)
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
