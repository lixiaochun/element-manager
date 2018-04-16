#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2018 Nippon Telegraph and Telephone Corporation
# Filename: EmL3SliceMerge.py
'''
Individual scenario to add L3 slice.
'''
import threading
import json
from lxml import etree
import EmSeparateScenario
from EmCommonDriver import EmCommonDriver
import GlobalModule
from EmCommonLog import decorater_log


class EmL3SliceMerge(EmSeparateScenario.EmScenario):
    '''
    Class for adding L3 slice.
    '''

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''
        super(EmL3SliceMerge, self).__init__()
        self.service = GlobalModule.SERVICE_L3_SLICE
        self._xml_ns = "{%s}" % GlobalModule.EM_NAME_SPACES[self.service]
        self.timeout_flag = False
        self.device_type = "device-leaf"

    @decorater_log
    def _gen_sub_thread(
            self, device_message,
            transaction_id, order_type, condition, device_name, force):
        '''
        Conduct control of adding L3 slice for each device.
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
            "104001 Scenario:L3SliceMerge Device:%s start", device_name)

        self.com_driver_list[device_name] = EmCommonDriver()

        is_db_result = \
            GlobalModule.EMSYSCOMUTILDB.write_transaction_device_status_list(
                "UPDATE", device_name, transaction_id,
                GlobalModule.TRA_STAT_PROC_RUN)

        if is_db_result is False:
            GlobalModule.EM_LOGGER.debug(
                " write_transaction_device_status_list(1:processing) NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:L3SliceMerge Device:%s NG:13(Processing failure (temporary))",
                device_name)
            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L3SliceMerge Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug(
            "write_transaction_device_status_list(1:processing) OK")

        json_message = self.__creating_json(device_message)
        GlobalModule.EM_LOGGER.debug("json_message =%s", json_message)

        is_comdriver_result = self.com_driver_list[device_name].start(
            device_name, json_message)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("start NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:L3SliceMerge Device:%s NG:13(Processing failure (temporary))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L3SliceMerge Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug("start OK")

        is_comdriver_result = self.com_driver_list[device_name].connect_device(
            device_name, "l3-slice", order_type, json_message)

        if is_comdriver_result == GlobalModule.COM_CONNECT_NG:
            GlobalModule.EM_LOGGER.debug("connect_device NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:L3SliceMerge Device:%s NG:14(Processing failure (Other))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L3SliceMerge Device:%s end", device_name)
            return

        elif is_comdriver_result == GlobalModule.COM_CONNECT_NO_RESPONSE:
            GlobalModule.EM_LOGGER.debug("connect_device no reply")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:L3SliceMerge Device:%s NG:13(Processing failure (temporary))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L3SliceMerge Device:%s end", device_name)
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
                "204004 Scenario:L3SliceMerge Device:%s NG:14(Processing failure (Other))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 True, True)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L3SliceMerge Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug(
            "write_transaction_device_status_list(2:Edit-config) OK")

        is_comdriver_result = self.com_driver_list[
            device_name].update_device_setting(
                device_name, "l3-slice", order_type, json_message)

        if is_comdriver_result == GlobalModule.COM_UPDATE_VALICHECK_NG:
            GlobalModule.EM_LOGGER.debug("update_device_setting validation check NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:L3SliceMerge Device:%s NG:9(Processing failure(validation check NG))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_CHECK,
                                 True, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L3SliceMerge Device:%s end", device_name)
            return

        elif is_comdriver_result == GlobalModule.COM_UPDATE_NG:
            GlobalModule.EM_LOGGER.debug("update_device_setting error")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:L3SliceMerge Device:%s NG:13(Processing failure (temporary))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 True, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L3SliceMerge Device:%s end", device_name)
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
                "204004 Scenario:L3SliceMerge Device:%s NG:13(Processing failure (Other))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 True, True)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L3SliceMerge Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug(
            "write_transaction_device_status_list(3:Confirmed-commit) OK")

        is_comdriver_result = self.com_driver_list[
            device_name].reserve_device_setting(
                device_name, "l3-slice", order_type)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("reserve_device_setting NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:L3SliceMerge Device:%s NG:13(Processing failure (temporary))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 True, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L3SliceMerge Device:%s end", device_name)
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
                "204004 Scenario:L3SliceMerge Device:%s NG:13(Processing failure (Other))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 True, True)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L3SliceMerge Device:%s end", device_name)
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
                "104002 Scenario:L3SliceMerge Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug("Timeout detection None")

        timer.cancel()

        is_comdriver_result = self.com_driver_list[
            device_name].enable_device_setting(
                device_name, "l3-slice", order_type)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("enable_device_setting NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:L3SliceMerge Device:%s NG:13(Processing failure (temporary))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 True, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L3SliceMerge Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug("enable_device_setting OK")

        is_comdriver_result = self.com_driver_list[
            device_name].disconnect_device(device_name, "l3-slice", order_type)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("disconnect_device NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:L3SliceMerge Device:%s NG:13(Processing failure (temporary))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L3SliceMerge Device:%s end", device_name)
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
                "204004 Scenario:L3SliceMerge Device:%s NG:13(Processing failure (temporary))",
                device_name)
            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L3SliceMerge Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug(
            "write_transaction_device_status_list(5:Successful completion) OK")

        is_comdriver_result = self.com_driver_list[device_name].write_em_info(
            device_name, "l3-slice", order_type, device_message)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("write_em_info NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:L3SliceMerge Device:%s NG:14(Processing failure (Other))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:L3SliceMerge Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug("write_em_info OK")

        GlobalModule.EM_LOGGER.info(
            "104002 Scenario:L3SliceMerge Device:%s end", device_name)
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
    def __creating_json(self, device_message):
        '''
        Convert EC message (XML) divided for each device into JSON.
        Explanation about parameter:
            device_message: Message for each device
        Explanation about return value
            device_json_message: JSON message
        '''
        device_json_message = \
            {
                "device-leaf": {
                    "name": None,
                    "slice_name": None,
                    "vrf": {},
                    "cp_value": 0,
                    "cp": []
                }
            }

        xml_elm = etree.fromstring(device_message)

        GlobalModule.EM_LOGGER.debug(
            "device_message = %s", etree.tostring(xml_elm, pretty_print=True))

        device_elm = self._find_xml_node(xml_elm, self._xml_ns + "name")
        device_json_message["device-leaf"]["name"] = device_elm.text

        slice_elm = self._find_xml_node(xml_elm, self._xml_ns + "slice_name")
        device_json_message["device-leaf"]["slice_name"] = slice_elm.text

        vrf_elm = self._find_xml_node(xml_elm,
                                      self._xml_ns + "vrf")
        vrf_name = vrf_elm.find(self._xml_ns + "vrf-name").text
        device_json_message["device-leaf"]["vrf"]["vrf-name"] = vrf_name

        vrf_rt = vrf_elm.find(self._xml_ns + "rt").text
        device_json_message["device-leaf"]["vrf"]["rt"] = vrf_rt

        vrf_rd = vrf_elm.find(self._xml_ns + "rd").text
        device_json_message["device-leaf"]["vrf"]["rd"] = vrf_rd

        vrf_router_id = vrf_elm.find(self._xml_ns + "router-id").text
        device_json_message[
            "device-leaf"]["vrf"]["router-id"] = vrf_router_id

        cp_tag = self._xml_ns + "cp"
        for cp_get in xml_elm.findall(".//" + cp_tag):
            cp_list = \
                {
                    "name": None,
                    "vlan-id": 0,
                    "ce-interface": {},
                    "vrrp": {
                        "track": {
                            "interface": []
                        }
                    },
                    "bgp": {},
                    "static": {
                        "route": [],
                        "route6": []
                    },
                    "qos": {}
                }

            cp_list["name"] = \
                cp_get.find(self._xml_ns + "name").text
            cp_list["vlan-id"] = \
                int(cp_get.find(self._xml_ns + "vlan-id").text)

            ce_elm = self._find_xml_node(cp_get,
                                         self._xml_ns + "ce-interface")

            if ce_elm.find(self._xml_ns + "address") is not None:
                ipv4_addr = ce_elm.find(self._xml_ns + "address").text
                cp_list["ce-interface"]["address"] = ipv4_addr

            if ce_elm.find(self._xml_ns + "prefix") is not None:
                ipv4_prefix = int(ce_elm.find(self._xml_ns + "prefix").text)
                cp_list["ce-interface"]["prefix"] = ipv4_prefix

            if ce_elm.find(self._xml_ns + "address6") is not None:
                ipv6_addr = ce_elm.find(self._xml_ns + "address6").text
                cp_list["ce-interface"]["address6"] = ipv6_addr

            if ce_elm.find(self._xml_ns + "prefix6") is not None:
                ipv6_prefix = int(ce_elm.find(self._xml_ns + "prefix6").text)
                cp_list["ce-interface"]["prefix6"] = ipv6_prefix

            if ce_elm.find(self._xml_ns + "mtu") is not None:
                mtu = int(ce_elm.find(self._xml_ns + "mtu").text)
                cp_list["ce-interface"]["mtu"] = mtu

            vrrp_elm = self._find_xml_node(cp_get,
                                           self._xml_ns + "vrrp")
            if vrrp_elm is not None:
                vrrp_group_id = int(
                    vrrp_elm.find(self._xml_ns + "group-id").text)
                cp_list["vrrp"]["group-id"] = vrrp_group_id

                vrrp_priority = int(
                    vrrp_elm.find(self._xml_ns + "priority").text)
                cp_list["vrrp"]["priority"] = vrrp_priority

                if vrrp_elm.find(self._xml_ns + "virtual-address") is not None:
                    vr_addr = vrrp_elm.find(
                        self._xml_ns + "virtual-address").text
                    cp_list["vrrp"]["virtual-address"] = vr_addr

                if vrrp_elm.find(self._xml_ns +
                                 "virtual-address6") is not None:
                    vr_addr6 = vrrp_elm.find(
                        self._xml_ns + "virtual-address6").text
                    cp_list["vrrp"]["virtual-address6"] = vr_addr6

                if vrrp_elm.find(self._xml_ns + "track") is not None:

                    track_elm = self._find_xml_node(
                        vrrp_elm, self._xml_ns + "track")
                    track_tag = self._xml_ns + "interface"
                    for track_if in track_elm.findall(".//" + track_tag):
                        track_if_info = \
                            {
                                "name": None
                            }
                        track_if_info["name"] = \
                            track_if.find(self._xml_ns + "name").text

                        cp_list["vrrp"]["track"][
                            "interface"].append(track_if_info.copy())

                    track_len = len(cp_list["vrrp"]["track"]["interface"])
                    cp_list["vrrp"]["track"][
                        "track_interface_value"] = track_len
                else:
                    del cp_list["vrrp"]["track"]
            else:
                del cp_list["vrrp"]

            bgp_elm = self._find_xml_node(cp_get,
                                          self._xml_ns + "bgp")
            if bgp_elm is not None:
                bgp_remote_as_num = int(
                    bgp_elm.find(self._xml_ns + "remote-as-number").text)
                cp_list["bgp"]["remote-as-number"] = bgp_remote_as_num

                if bgp_elm.find(self._xml_ns + "master") is not None:
                    cp_list["bgp"]["master"] = "ON"

                if bgp_elm.find(self._xml_ns + "local-address") is not None:
                    local_addr = bgp_elm.find(
                        self._xml_ns + "local-address").text
                    cp_list["bgp"]["local-address"] = local_addr

                if bgp_elm.find(self._xml_ns + "remote-address") is not None:
                    remote_addr = bgp_elm.find(
                        self._xml_ns + "remote-address").text
                    cp_list["bgp"]["remote-address"] = remote_addr

                if bgp_elm.find(self._xml_ns + "local-address6") is not None:
                    local_addr6 = bgp_elm.find(
                        self._xml_ns + "local-address6").text
                    cp_list["bgp"]["local-address6"] = local_addr6

                if bgp_elm.find(self._xml_ns + "remote-address6") is not None:
                    remote_addr6 = bgp_elm.find(
                        self._xml_ns + "remote-address6").text
                    cp_list["bgp"]["remote-address6"] = remote_addr6
            else:
                del cp_list["bgp"]

            static_elm = self._find_xml_node(cp_get,
                                             self._xml_ns + "static")
            if static_elm is not None:
                if static_elm.find(self._xml_ns + "route") is not None:
                    ipv4_tag = self._xml_ns + "route"
                    for route_ipv4 in static_elm.findall(".//" + ipv4_tag):
                        route_info = \
                            {
                                "address": None,
                                "prefix": 0,
                                "nexthop": None
                            }
                        route_info["address"] = \
                            route_ipv4.find(self._xml_ns + "address").text
                        route_info["prefix"] = \
                            int(route_ipv4.find(self._xml_ns + "prefix").text)
                        route_info["nexthop"] = \
                            route_ipv4.find(self._xml_ns + "next-hop").text

                        cp_list["static"]["route"].append(route_info.copy())

                    route_ipv4_len = len(cp_list["static"]["route"])
                    cp_list["static"]["route_value"] = route_ipv4_len
                else:
                    del cp_list["static"]["route"]

                if static_elm.find(self._xml_ns + "route6") is not None:
                    ipv6_tag = self._xml_ns + "route6"
                    for route_ipv6 in static_elm.findall(".//" + ipv6_tag):
                        route6_info = \
                            {
                                "address": None,
                                "prefix": 0,
                                "nexthop": None
                            }
                        route6_info["address"] = \
                            route_ipv6.find(self._xml_ns + "address").text
                        route6_info["prefix"] = \
                            int(route_ipv6.find(self._xml_ns + "prefix").text)
                        route6_info["nexthop"] = \
                            route_ipv6.find(self._xml_ns + "next-hop").text

                        cp_list["static"]["route6"].append(route6_info.copy())

                    route_ipv6_len = len(cp_list["static"]["route6"])
                    cp_list["static"]["route6_value"] = route_ipv6_len
                else:
                    del cp_list["static"]["route6"]

            else:
                del cp_list["static"]

            qos_info = self._find_xml_node(cp_get,
                                           self._xml_ns + "qos")
            if qos_info is not None:
                inflow_shaping_rate = qos_info.find(
                    self._xml_ns + "inflow-shaping-rate")
                if inflow_shaping_rate is not None:
                    cp_list["qos"]["inflow-shaping-rate"] = float(
                        inflow_shaping_rate.text)

                outflow_shaping_rate = qos_info.find(
                    self._xml_ns + "outflow-shaping-rate")
                if outflow_shaping_rate is not None:
                    cp_list["qos"]["outflow-shaping-rate"] = float(
                        outflow_shaping_rate.text)

                remark_menu = qos_info.find(self._xml_ns + "remark-menu")
                if remark_menu is not None:
                    cp_list["qos"]["remark-menu"] = remark_menu.text

                egress_menu = qos_info.find(self._xml_ns + "egress-menu")
                if egress_menu is not None:
                    cp_list["qos"]["egress-menu"] = egress_menu.text

            device_json_message["device-leaf"]["cp"].append(cp_list.copy())

        cp_len = len(device_json_message["device-leaf"]["cp"])
        device_json_message["device-leaf"]["cp_value"] = cp_len

        GlobalModule.EM_LOGGER.debug(
            "device__json_message = %s", device_json_message)

        return json.dumps(device_json_message)

    @staticmethod
    @decorater_log
    def _gen_netconf_message(element, slice_name):
        '''
        Device name:Create Netconf message (json letter string).
        '''
        slice_elm = etree.Element("slice_name")
        slice_elm.text = slice_name
        element.append(slice_elm)
        return etree.tostring(element)

    def test(self, mes):
        return self.__creating_json(mes)
