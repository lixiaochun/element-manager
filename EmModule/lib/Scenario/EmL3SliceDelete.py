import threading
import json
from lxml import etree
import EmSeparateScenario
from EmCommonDriver import EmCommonDriver
import GlobalModule
from EmCommonLog import decorater_log


class EmL3SliceDelete(EmSeparateScenario.EmScenario):


    @decorater_log
    def __init__(self):

        super(EmL3SliceDelete, self).__init__()

        self.timeout_flag = False

    @decorater_log
    def _gen_sub_thread(
            self, device_message,
            transaction_id, order_type, condition, device_name, force):

        GlobalModule.EM_LOGGER.info(
            "104001 Scenario:L3SliceDelete Device:%s start", device_name)

        self.com_driver_list[device_name] = EmCommonDriver()

        is_db_result = \
            GlobalModule.EMSYSCOMUTILDB.write_transaction_device_status_list(
                "UPDATE", device_name, transaction_id,
                GlobalModule.TRA_STAT_PROC_RUN)

        if is_db_result is False:
            GlobalModule.EM_LOGGER.debug(
                " write_transaction_device_status_list(1:処理中) NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:L3SliceDelete Device:%s NG:13(処理失敗(一時的))",
                device_name)
            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L3SliceDelete Device:%s end", device_name)
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
                "204004 Scenario:L3SliceDelete Device:%s NG:13(処理失敗(一時的))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L3SliceDelete Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug("start OK")

        is_comdriver_result = self.com_driver_list[device_name].connect_device(
            device_name, "l3-slice", order_type, json_message)

        if is_comdriver_result == GlobalModule.COM_CONNECT_NG:
            GlobalModule.EM_LOGGER.debug("connect_device 装置接続NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:L3SliceDelete Device:%s NG:14(処理失敗(その他))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L3SliceDelete Device:%s end", device_name)
            return

        elif is_comdriver_result == GlobalModule.COM_CONNECT_NO_RESPONSE:
            GlobalModule.EM_LOGGER.debug("connect_device 装置応答なし")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:L3SliceDelete Device:%s NG:13(処理失敗(一時的))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L3SliceDelete Device:%s end", device_name)
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
                "204004 Scenario:L3SliceDelete Device:%s NG:14(処理失敗(その他))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 True, True)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L3SliceDelete Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug(
            "write_transaction_device_status_list(2:Edit-config中) OK")

        is_comdriver_result = self.com_driver_list[
            device_name].delete_device_setting(
                device_name, "l3-slice", order_type, json_message)

        if is_comdriver_result == GlobalModule.COM_DELETE_VALICHECK_NG:
            GlobalModule.EM_LOGGER.debug("delete_device_setting バリデーションチェックNG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:L3SliceDelete Device:%s NG:9(処理失敗(バリチェックNG))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_CHECK,
                                 True, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L3SliceDelete Device:%s end", device_name)
            return

        elif is_comdriver_result == GlobalModule.COM_DELETE_NG:

            if force is not True:
                GlobalModule.EM_LOGGER.debug("強制削除フラグ無効")

                GlobalModule.EM_LOGGER.debug("delete_device_setting 削除異常")
                GlobalModule.EM_LOGGER.warning(
                    "204004 Scenario:L3SliceDelete Device:%s NG:13(処理失敗(一時的))",
                    device_name)

                self._find_subnormal(transaction_id, order_type, device_name,
                                     GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                     True, False)

                GlobalModule.EM_LOGGER.info(
                    "104002 Scenario:L3SliceDelete Device:%s end", device_name)
                return
            else:
                GlobalModule.EM_LOGGER.debug("強制削除フラグ有効")

                is_comdriver_result = self.com_driver_list[
                    device_name].disconnect_device(
                        device_name, "l3-slice", order_type)

                if is_comdriver_result is False:
                    GlobalModule.EM_LOGGER.debug("disconnect_device NG")
                    GlobalModule.EM_LOGGER.warning(
                        "204004 Scenario:L3SliceDelete Device:%s NG:13(処理失敗)",
                        device_name)

                    self._find_subnormal(transaction_id,
                                         order_type,
                                         device_name,
                                         GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                         False, False)

                    GlobalModule.EM_LOGGER.info(
                        "104002 Scenario:L3SliceDelete Device:%s end",
                        device_name)
                    return

                GlobalModule.EM_LOGGER.debug("disconnect_device OK")

                is_db_result = \
                    GlobalModule.EMSYSCOMUTILDB.\
                    write_transaction_device_status_list(
                        "UPDATE", device_name, transaction_id,
                        GlobalModule.TRA_STAT_PROC_END)

                if is_db_result is False:
                    GlobalModule.EM_LOGGER.debug(
                        "write_transaction_device_status_list(5:正常終了) NG")
                    GlobalModule.EM_LOGGER.warning(
                        "204004 Scenario:L3SliceDelete Device:%s NG:13(処理失敗)",
                        device_name)
                    GlobalModule.EM_LOGGER.info(
                        "104002 Scenario:L3SliceDelete Device:%s end",
                        device_name)
                    return

                GlobalModule.EM_LOGGER.debug(
                    "write_transaction_device_status_list(5:正常終了) OK")

                is_comdriver_result = self.com_driver_list[
                    device_name].write_em_info(
                        device_name, "l3-slice", order_type,
                        device_message, force)

                if is_comdriver_result is False:
                    GlobalModule.EM_LOGGER.debug("write_em_info NG")
                    GlobalModule.EM_LOGGER.warning(
                        "204004 Scenario:L3SliceDelete Device:%s" +
                        "NG:12(保持情報なし)",
                        device_name)

                    self._find_subnormal(transaction_id, order_type,
                                         device_name,
                                         GlobalModule.TRA_STAT_PROC_ERR_INF,
                                         False, False)

                    GlobalModule.EM_LOGGER.info(
                        "104002 Scenario:L3SliceDelete Device:%s end",
                        device_name)
                    return

                GlobalModule.EM_LOGGER.debug("write_em_info OK")

                GlobalModule.EM_LOGGER.info(
                    "104002 Scenario:L3SliceDelete Device:%s end", device_name)
                return

        GlobalModule.EM_LOGGER.debug("delete_device_setting OK")

        is_db_result = \
            GlobalModule.EMSYSCOMUTILDB.write_transaction_device_status_list(
                "UPDATE", device_name, transaction_id,
                GlobalModule.TRA_STAT_CONF_COMMIT)

        if is_db_result is False:
            GlobalModule.EM_LOGGER.debug(
                "write_transaction_device_status_list(3:Confirmed-commit中) NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:L3SliceDelete Device:%s NG:14(処理失敗(その他))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 True, True)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L3SliceDelete Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug(
            "write_transaction_device_status_list(3:Confirmed-commit中) OK")

        is_comdriver_result = self.com_driver_list[
            device_name].reserve_device_setting(
                device_name, "l3-slice", order_type)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("reserve_device_setting NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:L3SliceDelete Device:%s NG:13(処理失敗(一時的))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 True, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L3SliceDelete Device:%s end", device_name)
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
                "204004 Scenario:L3SliceDelete Device:%s NG:14(処理失敗(その他))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 True, True)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L3SliceDelete Device:%s end", device_name)
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
                "104002 Scenario:L3SliceDelete Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug("タイムアウト検出なし")

        timer.cancel()

        is_comdriver_result = self.com_driver_list[
            device_name].enable_device_setting(
                device_name, "l3-slice", order_type)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("enable_device_setting NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:L3SliceDelete Device:%s NG:13(処理失敗(一時的))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 True, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L3SliceDelete Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug("enable_device_setting OK")

        is_comdriver_result = self.com_driver_list[
            device_name].disconnect_device(device_name, "l3-slice", order_type)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("disconnect_device NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:L3SliceDelete Device:%s NG:13(処理失敗(一時的))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L3SliceDelete Device:%s end", device_name)
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
                "204004 Scenario:L3SliceDelete Device:%s NG:13(処理失敗(一時的))",
                device_name)
            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L3SliceDelete Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug(
            "write_transaction_device_status_list(5:正常終了) OK")

        is_comdriver_result = self.com_driver_list[device_name].write_em_info(
            device_name, "l3-slice", order_type, device_message)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("write_em_info NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:L3SliceDelete Device:%s NG:14(処理失敗(その他))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L3SliceDelete Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug("write_em_info OK")

        GlobalModule.EM_LOGGER.info(
            "104002 Scenario:L3SliceDelete Device:%s end", device_name)
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
                "device-leaf": {
                    "name": "None",
                    "slice_name": "None",
                    "cp_value": 0,
                    "cp": []
                }
            }


        xml_elm = etree.fromstring(device_message)

        GlobalModule.EM_LOGGER.debug(
            "device_message = %s", etree.tostring(xml_elm, pretty_print=True))

        device_elm = self._find_xml_node(
            xml_elm, ns_l3_slice + "name")
        device_json_message["device-leaf"]["name"] = device_elm.text

        slice_elm = self._find_xml_node(xml_elm, ns_l3_slice + "slice_name")
        device_json_message["device-leaf"]["slice_name"] = slice_elm.text


        cp_tag = ns_l3_slice + "cp"
            cp_list = \
                {
                    "operation": "None",
                    "name": "None",
                    "vlan-id": 0,
                    "vrrp": {
                        "operation": "None"
                    },
                    "bgp": {
                        "operation": "None",
                    },
                    "static": {
                        "route": [],
                        "route6": []
                    },
                    "ospf": {
                        "operation": "None"
                    }
                }

            cp_list["name"] = \
                cp_get.find(ns_l3_slice + "name").text
            cp_list["vlan-id"] = \
                int(cp_get.find(ns_l3_slice + "vlan-id").text)
            operation = cp_get.get("operation")
            if operation == "delete":
                cp_list["operation"] = "delete"
            else:
                cp_list["operation"] = "merge"

            vrrp_elm = self._find_xml_node(cp_get,
                                           ns_l3_slice + "vrrp")
            if vrrp_elm is not None:
                vrrp_operation = vrrp_elm.get("operation")

                if vrrp_operation == "delete":
                    cp_list["vrrp"]["operation"] = "delete"
                else:
                    cp_list["vrrp"]["operation"] = "merge"
            else:
                del cp_list["vrrp"]

            bgp_elm = self._find_xml_node(cp_get,
                                          ns_l3_slice + "bgp")
            if bgp_elm is not None:
                bgp_operation = bgp_elm.get("operation")

                if bgp_operation == "delete":
                    cp_list["bgp"]["operation"] = "delete"
                else:
                    cp_list["bgp"]["operation"] = "merge"
            else:
                del cp_list["bgp"]

            static_elm = self._find_xml_node(cp_get,
                                             ns_l3_slice + "static")
            if static_elm is not None:
                if static_elm.find(ns_l3_slice + "route") is not None:
                    ipv4_tag = ns_l3_slice + "route"
                        route_info = \
                            {
                                "operation": "None",
                                "address": "None",
                                "prefix": 0,
                                "nexthop": "None"
                            }
                        route_operation = route_ipv4.get("operation")
                        if route_operation == "delete":
                            route_info["operation"] = "delete"
                        else:
                            route_info["operation"] = "merge"

                        route_info["address"] = \
                            route_ipv4.find(ns_l3_slice + "address").text
                        route_info["prefix"] = \
                            int(route_ipv4.find(ns_l3_slice + "prefix").text)
                        route_info["nexthop"] = \
                            route_ipv4.find(ns_l3_slice + "next-hop").text

                        cp_list["static"]["route"].append(route_info.copy())

                    route_ipv4_len = len(cp_list["static"]["route"])
                    cp_list["static"]["route_value"] = route_ipv4_len
                else:
                    del cp_list["static"]["route"]

                if static_elm.find(ns_l3_slice + "route6") is not None:
                    ipv6_tag = ns_l3_slice + "route6"
                        route6_info = \
                            {
                                "operation": "None",
                                "address": "None",
                                "prefix": 0,
                                "nexthop": "None"
                            }
                        route6_operation = route_ipv6.get("operation")
                        if route6_operation == "delete":
                            route6_info["operation"] = "delete"
                        else:
                            route6_info["operation"] = "merge"

                        route6_info["address"] = \
                            route_ipv6.find(ns_l3_slice + "address").text
                        route6_info["prefix"] = \
                            int(route_ipv6.find(ns_l3_slice + "prefix").text)
                        route6_info["nexthop"] = \
                            route_ipv6.find(ns_l3_slice + "next-hop").text

                        cp_list["static"]["route6"].append(route6_info.copy())

                    route_ipv6_len = len(cp_list["static"]["route6"])
                    cp_list["static"]["route6_value"] = route_ipv6_len
                else:
                    del cp_list["static"]["route6"]
            else:
                del cp_list["static"]

            ospf_elm = self._find_xml_node(cp_get,
                                           ns_l3_slice + "ospf")
            if ospf_elm is not None:
                ospf_operation = ospf_elm.get("operation")

                if ospf_operation == "delete":
                    cp_list["ospf"]["operation"] = "delete"
                else:
                    cp_list["ospf"]["operation"] = "merge"
            else:
                del cp_list["ospf"]

            device_json_message["device-leaf"]["cp"].append(cp_list)

        device_json_message["device-leaf"]["cp_value"] = \
            len(device_json_message["device-leaf"]["cp"])

        GlobalModule.EM_LOGGER.debug(
            "device__json_message = %s", device_json_message)

        return json.dumps(device_json_message)
