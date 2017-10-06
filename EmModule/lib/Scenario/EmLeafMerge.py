import threading
import json
from lxml import etree
import EmSeparateScenario
from EmCommonDriver import EmCommonDriver
import GlobalModule
from EmCommonLog import decorater_log


class EmLeafMerge(EmSeparateScenario.EmScenario):


    @decorater_log
    def __init__(self):

        super(EmLeafMerge, self).__init__()

        self.timeout_flag = False

    @decorater_log
    def _gen_sub_thread(
            self, device_message,
            transaction_id, order_type, condition, device_name, force):

        GlobalModule.EM_LOGGER.info(
            "104001 Scenario:LeafMerge Device:%s start", device_name)

        self.com_driver_list[device_name] = EmCommonDriver()

        is_db_result = \
            GlobalModule.EMSYSCOMUTILDB.write_transaction_device_status_list(
                "UPDATE", device_name, transaction_id,
                GlobalModule.TRA_STAT_PROC_RUN)

        if is_db_result is False:
            GlobalModule.EM_LOGGER.debug(
                " write_transaction_device_status_list(1:処理中) NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:LeafMerge Device:%s NG:13(処理失敗(一時的))",
                device_name)
            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:LeafMerge Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug(
            "write_transaction_device_status_list(1:処理中) OK")

        json_message = self.__creating_json(device_message)
        GlobalModule.EM_LOGGER.debug("json_message =%s", json_message)

        is_comdriver_result = self.com_driver_list[device_name].start(
            device_name, json_message)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("start NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:LeafMerge Device:%s NG:13(処理失敗(一時的))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:LeafMerge Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug("start OK")

        if ("newly-establish" in device_message) is False:
            GlobalModule.EM_LOGGER.debug("newly-establishフラグなし")

            is_db_result = \
                GlobalModule.EMSYSCOMUTILDB. \
                write_transaction_device_status_list(
                    "UPDATE", device_name, transaction_id,
                    GlobalModule.TRA_STAT_PROC_END)

            if is_db_result is False:
                GlobalModule.EM_LOGGER.debug(
                    "write_transaction_device_status_list(5:正常終了) NG")
                GlobalModule.EM_LOGGER.warning(
                    "204004 Scenario:LeafMerge Device:%s NG:13(処理失敗(一時的))",
                    device_name)
                GlobalModule.EM_LOGGER.info(
                    "104002 Scenario:LeafMerge Device:%s end", device_name)
                return

            GlobalModule.EM_LOGGER.debug(
                "write_transaction_device_status_list(5:正常終了) OK")

            is_comdriver_result = self.com_driver_list[
                device_name].write_em_info(
                    device_name, "leaf", order_type, device_message)

            if is_comdriver_result is False:
                GlobalModule.EM_LOGGER.debug("write_em_info NG")
                GlobalModule.EM_LOGGER.warning(
                    "204004 Scenario:LeafMerge Device:%s NG:14(処理失敗(その他))",
                    device_name)

                self._find_subnormal(transaction_id, order_type, device_name,
                                     GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                     False, False)

                GlobalModule.EM_LOGGER.info(
                    "104002 Scenario:LeafMerge Device:%s end", device_name)
                return

            GlobalModule.EM_LOGGER.debug("write_em_info OK")

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:LeafMerge Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug("newly-establishフラグあり")

        is_comdriver_result = self.com_driver_list[device_name].connect_device(
            device_name, "leaf", order_type, json_message)

        if is_comdriver_result == GlobalModule.COM_CONNECT_NG:
            GlobalModule.EM_LOGGER.debug("connect_device 装置接続NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:LeafMerge Device:%s NG:14(処理失敗(その他))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:LeafMerge Device:%s end", device_name)
            return

        elif is_comdriver_result == GlobalModule.COM_CONNECT_NO_RESPONSE:
            GlobalModule.EM_LOGGER.debug("connect_device 装置応答なし")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:LeafMerge Device:%s NG:13(処理失敗(一時的))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:LeafMerge Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug("connect_device OK")

        is_db_result = \
            GlobalModule.EMSYSCOMUTILDB.write_transaction_device_status_list(
                "UPDATE", device_name, transaction_id,
                GlobalModule.TRA_STAT_EDIT_CONF)

        if is_db_result is False:
            GlobalModule.EM_LOGGER.debug(
                "write_transaction_device_status_list(2:Edit-config中) NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:LeafMerge Device:%s NG:14(処理失敗(その他))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 True, True)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:LeafMerge Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug(
            "write_transaction_device_status_list(2:Edit-config中) OK")

        is_comdriver_result = self.com_driver_list[
            device_name].update_device_setting(
                device_name, "leaf", order_type, json_message)

        if is_comdriver_result == GlobalModule.COM_UPDATE_VALICHECK_NG:
            GlobalModule.EM_LOGGER.debug("update_device_setting バリデーションチェックNG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:LeafMerge Device:%s NG:9(処理失敗(バリチェックNG))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_CHECK,
                                 True, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:LeafMerge Device:%s end", device_name)
            return

        elif is_comdriver_result == GlobalModule.COM_UPDATE_NG:
            GlobalModule.EM_LOGGER.debug("update_device_setting 更新異常")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:LeafMerge Device:%s NG:13(処理失敗(一時的))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 True, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:LeafMerge Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug("update_device_setting OK")

        is_db_result = \
            GlobalModule.EMSYSCOMUTILDB.write_transaction_device_status_list(
                "UPDATE", device_name, transaction_id,
                GlobalModule.TRA_STAT_CONF_COMMIT)

        if is_db_result is False:
            GlobalModule.EM_LOGGER.debug(
                "write_transaction_device_status_list(3:Confirmed-commit中) NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:LeafMerge Device:%s NG:14(処理失敗(その他))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 True, True)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:LeafMerge Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug(
            "write_transaction_device_status_list(3:Confirmed-commit中) OK")

        is_comdriver_result = self.com_driver_list[
            device_name].reserve_device_setting(
                device_name, "leaf", order_type)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("reserve_device_setting NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:LeafMerge Device:%s NG:13(処理失敗(一時的))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 True, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:LeafMerge Device:%s end", device_name)
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
                "write_transaction_device_status_list(4:Commit中) NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:LeafMerge Device:%s NG:14(処理失敗(その他))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 True, True)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:LeafMerge Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug(
            "write_transaction_device_status_list(4:Commit中) OK")

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
                "104002 Scenario:LeafMerge Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug("タイムアウト検出なし")

        timer.cancel()

        is_comdriver_result = self.com_driver_list[
            device_name].enable_device_setting(
                device_name, "leaf", order_type)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("enable_device_setting NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:LeafMerge Device:%s NG:13(処理失敗(一時的))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 True, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:LeafMerge Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug("enable_device_setting OK")

        is_comdriver_result = self.com_driver_list[
            device_name].disconnect_device(device_name, "leaf", order_type)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("disconnect_device NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:LeafMerge Device:%s NG:13(処理失敗(一時的))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:LeafMerge Device:%s end", device_name)
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
                "204004 Scenario:LeafMerge Device:%s NG:13(処理失敗(一時的))",
                device_name)
            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:LeafMerge Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug(
            "write_transaction_device_status_list(5:正常終了) OK")

        is_comdriver_result = self.com_driver_list[device_name].write_em_info(
            device_name, "leaf", order_type, device_message)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("write_em_info NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:LeafMerge Device:%s NG:14(処理失敗(その他))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:LeafMerge Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug("write_em_info OK")

        GlobalModule.EM_LOGGER.info(
            "104002 Scenario:LeafMerge Device:%s end", device_name)
        return

    @decorater_log
    def _find_timeout(self, condition):

        GlobalModule.EM_LOGGER.debug("タイムアウト検出あり")

        self.timeout_flag = True

        GlobalModule.EM_LOGGER.debug("Condition acquire notify release")
        condition.acquire()
        condition.notify()
        condition.release()

    @decorater_log
    def _judg_transaction_status(self, transaction_status):


        GlobalModule.EM_LOGGER.debug(
            "transaction_status:%s", transaction_status)

        transaction_status_list = [GlobalModule.TRA_STAT_PROC_RUN,
                                   GlobalModule.TRA_STAT_EDIT_CONF,
                                   GlobalModule.TRA_STAT_CONF_COMMIT,
                                   GlobalModule.TRA_STAT_COMMIT]

        if transaction_status in transaction_status_list:

            GlobalModule.EM_LOGGER.debug("transaction_status Match")


        GlobalModule.EM_LOGGER.debug("transaction_status UNMatch")

    @decorater_log
    def __creating_json(self, device_message):

        device_json_message = \
            {
                "device":
                {
                    "name": "None",
                    "equipment":
                    {
                        "platform": "None",
                        "os": "None",
                        "firmware": "None",
                        "loginid": "None",
                        "password": "None"
                    },
                    "internal-lag_value": 0,
                    "internal-lag": [],
                    "management-interface": {
                        "address": "None",
                        "prefix": 0
                    },
                    "loopback-interface": {
                        "address": "None",
                        "prefix": 0
                    },
                    "snmp": {
                        "server-address": "None",
                        "community": "None"
                    },
                    "ntp": {
                        "server-address": "None"
                    },
                    "l3-vpn": {
                        "bgp": {
                            "neighbor_value": 0,
                            "neighbor": [],
                            "community": "None",
                            "community-wildcard": "None"
                        },
                        "as": {
                            "as-number": 0
                        },
                    },
                    "l2-vpn": {
                        "pim": {
                            "rp-address": "None"
                        }
                    }
                }
            }


        xml_elm = etree.fromstring(device_message)

        GlobalModule.EM_LOGGER.debug(
            "device_message = %s", etree.tostring(xml_elm, pretty_print=True))

        device_elm = self._find_xml_node(xml_elm, ns_leaf + "name")
        device_json_message["device"]["name"] = device_elm.text

        equ_elm = self._find_xml_node(xml_elm,
                                      ns_leaf + "equipment")
        device_json_message["device"]["equipment"]["platform"] = \
            equ_elm.find(ns_leaf + "platform").text
        device_json_message["device"]["equipment"]["os"] = \
            equ_elm.find(ns_leaf + "os").text
        device_json_message["device"]["equipment"]["firmware"] = \
            equ_elm.find(ns_leaf + "firmware").text
        device_json_message["device"]["equipment"]["loginid"] = \
            equ_elm.find(ns_leaf + "loginid").text
        device_json_message["device"]["equipment"]["password"] = \
            equ_elm.find(ns_leaf + "password").text

        if xml_elm.find(ns_leaf + "internal-lag-interface") is not None:
            lag_tag = ns_leaf + "internal-lag-interface"
                internal_lag_info = {
                    "name": "None",
                    "minimum-links": 0,
                    "link-speed": 0,
                    "address": "None",
                    "prefix": 0,
                    "internal-interface_value": 0,
                    "internal-interface": []
                }

                internal_lag_info["name"] = \
                    lag.find(ns_leaf + "name").text
                internal_lag_info["minimum-links"] = \
                    int(lag.find(ns_leaf + "minimum-links").text)
                internal_lag_info["link-speed"] = \
                    lag.find(ns_leaf + "link-speed").text
                internal_lag_info["address"] = \
                    lag.find(ns_leaf + "address").text
                internal_lag_info["prefix"] = \
                    int(lag.find(ns_leaf + "prefix").text)

                lag_if_tag = ns_leaf + "internal-interface"
                    lag_if_name = lag_if.find(ns_leaf + "name").text

                    internal_lag_info[
                        "internal-interface"].append({"name": lag_if_name})

                internal_lag_info["internal-interface_value"] = \
                    len(internal_lag_info["internal-interface"])

                device_json_message["device"][
                    "internal-lag"].append(internal_lag_info)

            lag_len = len(device_json_message["device"]["internal-lag"])
            device_json_message["device"]["internal-lag_value"] = lag_len

        else:
            del device_json_message["device"]["internal-lag_value"]
            del device_json_message["device"]["internal-lag"]

        man_elm = self._find_xml_node(xml_elm,
                                      ns_leaf + "management-interface")
        device_json_message["device"]["management-interface"]["address"] = \
            man_elm.find(ns_leaf + "address").text
        device_json_message["device"]["management-interface"]["prefix"] = \
            int(man_elm.find(ns_leaf + "prefix").text)

        loop_elm = self._find_xml_node(xml_elm,
                                       ns_leaf + "loopback-interface")
        device_json_message["device"]["loopback-interface"]["address"] = \
            loop_elm.find(ns_leaf + "address").text
        device_json_message["device"]["loopback-interface"]["prefix"] = \
            int(loop_elm.find(ns_leaf + "prefix").text)

        snmp_elm = self._find_xml_node(xml_elm,
                                       ns_leaf + "snmp")
        device_json_message["device"]["snmp"]["server-address"] = \
            snmp_elm.find(ns_leaf + "server-address").text
        device_json_message["device"]["snmp"]["community"] = \
            snmp_elm.find(ns_leaf + "community").text

        ntp_elm = self._find_xml_node(xml_elm,
                                      ns_leaf + "ntp")
        device_json_message["device"]["ntp"]["server-address"] = \
            ntp_elm.find(ns_leaf + "server-address").text

        l3_vpn_elm = self._find_xml_node(xml_elm,
                                         ns_leaf + "l3-vpn")
        if l3_vpn_elm is not None:
            bgp_elm = self._find_xml_node(l3_vpn_elm, ns_leaf + "bgp")

            neighbor_tag = ns_leaf + "neighbor"
                neighbor_addr = neighbor.find(ns_leaf + "address").text
                device_json_message["device"][
                    "l3-vpn"]["bgp"]["neighbor"].append(
                        {"address": neighbor_addr})

            device_json_message["device"]["l3-vpn"]["bgp"][
                "neighbor_value"] = \
                len(device_json_message["device"]["l3-vpn"]["bgp"]["neighbor"])

            device_json_message["device"]["l3-vpn"]["bgp"][
                "community"] = bgp_elm.find(ns_leaf + "community").text

            device_json_message["device"]["l3-vpn"]["bgp"][
                "community-wildcard"] = \
                bgp_elm.find(ns_leaf + "community-wildcard").text

            as_elm = self._find_xml_node(l3_vpn_elm, ns_leaf + "as")

            device_json_message["device"]["l3-vpn"]["as"]["as-number"] = \
                int(as_elm.find(ns_leaf + "as-number").text)
        else:
            del device_json_message["device"]["l3-vpn"]

        l2_vpn_elm = self._find_xml_node(xml_elm,
                                         ns_leaf + "l2-vpn")
        if l2_vpn_elm is not None:
            pim_elm = self._find_xml_node(l2_vpn_elm, ns_leaf + "pim")

            device_json_message["device"]["l2-vpn"]["pim"]["rp-address"] = \
                pim_elm.find(ns_leaf + "rp-address").text
        else:
            del device_json_message["device"]["l2-vpn"]

        GlobalModule.EM_LOGGER.debug(
            "device__json_message = %s", device_json_message)

        return json.dumps(device_json_message)
