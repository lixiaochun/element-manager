import EmSeparateScenario
from EmCommonDriver import EmCommonDriver
import GlobalModule
from EmCommonLog import decorater_log


class EmL2SliceGet(EmSeparateScenario.EmScenario):


    @decorater_log
    def __init__(self):

        super(EmL2SliceGet, self).__init__()

    @decorater_log
    def _gen_sub_thread(
            self, device_message,
            transaction_id, order_type, condition, device_name, force):

        GlobalModule.EM_LOGGER.info(
            "104001 Scenario:L2SliceGet Device:%s start", device_name)

        self.com_driver_list[device_name] = EmCommonDriver()

        is_db_result = \
            GlobalModule.EMSYSCOMUTILDB.write_transaction_device_status_list(
                "UPDATE", device_name, transaction_id,
                GlobalModule.TRA_STAT_PROC_RUN)

        if is_db_result is False:
            GlobalModule.EM_LOGGER.debug(
                " write_transaction_device_status_list(1:処理中) NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:L2SliceGet Device:%s NG:13(処理失敗(一時的))",
                device_name)
            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L2SliceGet Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug(
            "write_transaction_device_status_list(1:処理中) OK")

        is_comdriver_result = self.com_driver_list[
            device_name].compare_to_db_info(
                device_name, "l2-slice", order_type, device_message)

        if is_comdriver_result == GlobalModule.COM_COMPARE_UNMATCH:
            GlobalModule.EM_LOGGER.debug("compare_to_db_info NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:L2SliceGet Device:%s NG:11(処理失敗（整合NG）)",
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
                "204004 Scenario:L2SliceGet Device:%s NG:12(処理失敗（保持情報なし）)",
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
                "204004 Scenario:L2SliceGet Device:%s NG:13(処理失敗(一時的))",
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
            GlobalModule.EM_LOGGER.debug("connect_device 装置接続NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:L2SliceGet Device:%s NG:14(処理失敗(その他))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L2SliceGet Device:%s end", device_name)
            return

        elif is_comdriver_result == GlobalModule.COM_CONNECT_NO_RESPONSE:
            GlobalModule.EM_LOGGER.debug("connect_device 装置応答なし")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:L2SliceGet Device:%s NG:13(処理失敗(一時的))",
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
                "204004 Scenario:L2SliceGet Device:%s NG:13(処理失敗(一時的))",
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
                "204004 Scenario:L2SliceGet Device:%s NG:11(処理失敗（整合NG）)",
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
                "204004 Scenario:L2SliceGet Device:%s NG:13(処理失敗(一時的))",
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
                "write_transaction_device_status_list(5:正常終了) NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:L2SliceGet Device:%s NG:13(処理失敗(一時的))",
                device_name)
            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L2SliceGet Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug(
            "write_transaction_device_status_list(5:正常終了) OK")

        GlobalModule.EM_LOGGER.info(
            "104002 Scenario:L2SliceGet Device:%s end", device_name)
        return

    @decorater_log
    def _judg_transaction_status(self, transaction_status):


        GlobalModule.EM_LOGGER.debug(
            "transaction_status:%s", transaction_status)

        transaction_status_list = [GlobalModule.TRA_STAT_PROC_RUN]

        if transaction_status in transaction_status_list:

            GlobalModule.EM_LOGGER.debug("transaction_status Match")


        GlobalModule.EM_LOGGER.debug("transaction_status UNMatch")
