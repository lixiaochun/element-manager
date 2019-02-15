#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2018 Nippon Telegraph and Telephone Corporation
# Filename: EmSpineMerge.py
'''
Individual scenario for Spine expansion.
'''
import threading
import json
from lxml import etree
import EmSeparateScenario
from EmCommonDriver import EmCommonDriver
import GlobalModule
from EmCommonLog import decorater_log


class EmSpineMerge(EmSeparateScenario.EmScenario):
    '''
    Class for Spine expansion
    '''

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmSpineMerge, self).__init__()

        self.service = GlobalModule.SERVICE_SPINE

        self._xml_ns = "{%s}" % GlobalModule.EM_NAME_SPACES[self.service]

        self.timeout_flag = False

        self.device_type = "device"

    @decorater_log
    def _gen_sub_thread(
            self, device_message,
            transaction_id, order_type, condition, device_name, force):
        '''
        Conducts Spine expansion control for each device.
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
            "104001 Scenario:SpineMerge Device:%s start", device_name)

        self.com_driver_list[device_name] = EmCommonDriver()

        is_db_result = \
            GlobalModule.EMSYSCOMUTILDB.write_transaction_device_status_list(
                "UPDATE", device_name, transaction_id,
                GlobalModule.TRA_STAT_PROC_RUN)

        if is_db_result is False:
            GlobalModule.EM_LOGGER.debug(
                " write_transaction_device_status_list(1:processing) NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:SpineMerge Device:%s NG:13(Processing failure (temporary))",
                device_name)
            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:SpineMerge Device:%s end", device_name)
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
                "204004 Scenario:SpineMerge Device:%s NG:13(Processing failure (temporary))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:SpineMerge Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug("start OK")

        if ("newly-establish" in device_message) is False:
            GlobalModule.EM_LOGGER.debug("newly-establish No flag")

            is_db_result = \
                GlobalModule.EMSYSCOMUTILDB. \
                write_transaction_device_status_list(
                    "UPDATE", device_name, transaction_id,
                    GlobalModule.TRA_STAT_PROC_END)

            if is_db_result is False:
                GlobalModule.EM_LOGGER.debug(
                    "write_transaction_device_status_list(5:Successful completion) NG")
                GlobalModule.EM_LOGGER.warning(
                    "204004 Scenario:SpineMerge Device:%s NG:13(Processing failure (temporary))",
                    device_name)
                GlobalModule.EM_LOGGER.info(
                    "104002 Scenario:SpineMerge Device:%s end", device_name)
                return

            GlobalModule.EM_LOGGER.debug(
                "write_transaction_device_status_list(5:Successful completion) OK")

            is_comdriver_result = self.com_driver_list[
                device_name].write_em_info(
                    device_name, self.service, order_type, device_message)

            if is_comdriver_result is False:
                GlobalModule.EM_LOGGER.debug("write_em_info NG")
                GlobalModule.EM_LOGGER.warning(
                    "204004 Scenario:SpineMerge Device:%s NG:14(Processing failure (Other))",
                    device_name)

                self._find_subnormal(transaction_id, order_type, device_name,
                                     GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                     False, False)

                GlobalModule.EM_LOGGER.info(
                    "104002 Scenario:SpineMerge Device:%s end", device_name)
                return

            GlobalModule.EM_LOGGER.debug("write_em_info OK")

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:SpineMerge Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug("newly-establish Flagged")

        is_comdriver_result = self.com_driver_list[device_name].connect_device(
            device_name, self.service, order_type, json_message)

        if is_comdriver_result == GlobalModule.COM_CONNECT_NG:
            GlobalModule.EM_LOGGER.debug("connect_device NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:SpineMerge Device:%s NG:14(Processing failure (Other))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:SpineMerge Device:%s end", device_name)
            return

        elif is_comdriver_result == GlobalModule.COM_CONNECT_NO_RESPONSE:
            GlobalModule.EM_LOGGER.debug("connect_device no reply")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:SpineMerge Device:%s NG:13(Processing failure (temporary))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:SpineMerge Device:%s end", device_name)
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
                "204004 Scenario:SpineMerge Device:%s NG:14(Processing failure (Other))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 True, True)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:SpineMerge Device:%s end", device_name)
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
                "204004 Scenario:SpineMerge Device:%s NG:9(Processing failure(validation check NG))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_CHECK,
                                 True, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:SpineMerge Device:%s end", device_name)
            return

        elif is_comdriver_result == GlobalModule.COM_UPDATE_NG:
            GlobalModule.EM_LOGGER.debug("update_device_setting error")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:SpineMerge Device:%s NG:13(Processing failure (temporary))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 True, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:SpineMerge Device:%s end", device_name)
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
                "204004 Scenario:SpineMerge Device:%s NG:14(Processing failure (Other))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 True, True)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:SpineMerge Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug(
            "write_transaction_device_status_list(3:Confirmed-commit) OK")

        is_comdriver_result = self.com_driver_list[
            device_name].reserve_device_setting(
                device_name, self.service, order_type)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("reserve_device_setting NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:SpineMerge Device:%s NG:13(Processing failure (temporary))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 True, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:SpineMerge Device:%s end", device_name)
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
                "204004 Scenario:SpineMerge Device:%s NG:14(Processing failure (Other))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 True, True)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:SpineMerge Device:%s end", device_name)
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
                "104002 Scenario:SpineMerge Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug("No timeout detection")

        timer.cancel()

        is_comdriver_result = self.com_driver_list[
            device_name].enable_device_setting(
                device_name, self.service, order_type)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("enable_device_setting NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:SpineMerge Device:%s NG:13(Processing failure (temporary))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 True, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:SpineMerge Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug("enable_device_setting OK")

        is_comdriver_result = self.com_driver_list[
            device_name].disconnect_device(device_name, self.service, order_type)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("disconnect_device NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:SpineMerge Device:%s NG:13(Processing failure (temporary))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:SpineMerge Device:%s end", device_name)
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
                "204004 Scenario:SpineMerge Device:%s NG:13(Processing failure (temporary))",
                device_name)
            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:SpineMerge Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug(
            "write_transaction_device_status_list(5:Successful completion) OK")

        is_comdriver_result = self.com_driver_list[device_name].write_em_info(
            device_name, self.service, order_type, device_message)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("write_em_info NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:SpineMerge Device:%s NG:14(Processing failure (Other))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:SpineMerge Device:%s end", device_name)
            return

        GlobalModule.EM_LOGGER.debug("write_em_info OK")

        GlobalModule.EM_LOGGER.info(
            "104002 Scenario:SpineMerge Device:%s end", device_name)
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
    def _creating_json(self, device_message):
        '''
        Convert EC message (XML) divided for each device into JSON.
        Explanation about parameter:
            device_message: Message for each device
        Explanation about return value
            device_json_message: JSON message
        '''

        device_json_message = \
            {
                "device":
                {
                    "name": None,
                    "equipment":
                    {
                        "platform": None,
                        "os": None,
                        "firmware": None,
                        "loginid": None,
                        "password": None
                    },
                    "breakout-interface_value": 0,
                    "breakout-interface": [],
                    "internal-physical_value": 0,
                    "internal-physical": [],
                    "internal-lag_value": 0,
                    "internal-lag": [],
                    "management-interface":
                    {
                        "address": None,
                        "prefix": 0
                    },
                    "loopback-interface":
                    {
                        "address": None,
                        "prefix": 0
                    },
                    "snmp":
                    {
                        "server-address": None,
                        "community": None
                    },
                    "ntp":
                    {
                        "server-address": None
                    },
                    "ospf":
                    {
                        "area-id": None
                    }
                }
            }

        xml_elm = etree.fromstring(device_message)

        GlobalModule.EM_LOGGER.debug(
            "device_message = %s", etree.tostring(xml_elm, pretty_print=True))

        device_json_message["device"]["name"] = \
            self._gen_json_name(xml_elm, self._xml_ns)

        self._gen_json_equipment(
            device_json_message, xml_elm, self._xml_ns)

        self._gen_json_breakout(
            device_json_message, xml_elm, self._xml_ns)

        self._gen_json_internal_if(
            device_json_message, xml_elm, self._xml_ns)

        self._gen_json_management(
            device_json_message, xml_elm, self._xml_ns)

        self._gen_json_loopback(
            device_json_message, xml_elm, self._xml_ns)

        self._gen_json_snmp(
            device_json_message, xml_elm, self._xml_ns)

        self._gen_json_ntp(
            device_json_message, xml_elm, self._xml_ns)

        self._gen_json_ospf(
            device_json_message, xml_elm, self._xml_ns)

        GlobalModule.EM_LOGGER.debug(
            "device__json_message = %s", device_json_message)

        return json.dumps(device_json_message)

    @decorater_log
    def _gen_json_name(self, xml, xml_ns):
        '''
            Obtain name information from xml message to be analyzed and
            set it for EC message storage dictionary object.
            Explanation about parameter:
                json:dictionary object for EC message storage
                xml:xml message to be analyzed
                xml_ns:Name space
        '''

        name_elm = self._find_xml_node(xml, xml_ns + "name")
        return name_elm.text

    @decorater_log
    def _gen_json_equipment(self, json, xml, xml_ns):
        '''
            Obtain device connection information from xml message to
            be analyzed and set it for EC message storage dictionary object.
            Explanation about parameter:
                json:dictionary object for EC message storage
                xml:xml message to be analyzed
                xml_ns:Name space
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
    def _gen_json_breakout(self, json, xml, xml_ns):
        '''
            Obtain breakoutIF information from xml message to be analyzed and
            set it for EC message storage dictionary object.
            Explanation about parameter:
                json:dictionary object for EC message storage
                xml:xml message to be analyzed
                xml_ns:Name space
        '''

        breakout_elm = self._find_xml_node(xml,
                                           xml_ns + "breakout-interface")

        if breakout_elm is not None:
            breakout_tag = xml_ns + "breakout-interface"
            for breakout in xml.findall(".//" + breakout_tag):
                breakout_base = breakout.find(xml_ns + "base-interface").text
                breakout_speed = breakout.find(xml_ns + "speed").text
                breakout_num = int(breakout.find(xml_ns + "breakout-num").text)
                json["device"]["breakout-interface"].append(
                    {"base-interface": breakout_base,
                     "speed": breakout_speed,
                     "breakout-num": breakout_num})
        json["device"]["breakout-interface_value"] = \
            len(json["device"]["breakout-interface"])

    @decorater_log
    def _gen_json_internal_if(self, json, xml, xml_ns):
        '''
            Obtain IF information for internal Link from xml message to
            be analyzed and set it for EC message storage dictionary object.
            Explanation about parameter:
                json:dictionary object for EC message storage
                xml:xml message to be analyzed
                xml_ns:Name space
        '''
        internal_if_elm = self._find_xml_node(xml,
                                              xml_ns + "internal-interface")

        if internal_if_elm is not None:
            internal_if_tag = xml_ns + "internal-interface"
            for internal_if in xml.findall(".//" + internal_if_tag):
                if internal_if.find(xml_ns + "type") is not None:
                    internal_if_type = internal_if.find(xml_ns + "type").text
                    if internal_if_type == "physical-if":
                        self._gen_json_internal_phy(json, xml_ns, internal_if)
                    elif internal_if_type == "lag-if":
                        self._gen_json_internal_lag(json, xml_ns, internal_if)

        json["device"]["internal-physical_value"] = \
            len(json["device"]["internal-physical"])
        json["device"]["internal-lag_value"] = \
            len(json["device"]["internal-lag"])

    @decorater_log
    def _gen_json_internal_phy(self, json, xml_ns, internal_phy):
        '''
            Obtain physical IF information for internal Link
            from xml message to be analyzed and set it
            for EC message storage dictionary object.
            Explanation about parameter:
                json:dictionary object for EC message storage
                xml:xml message to be analyzed
                xml_ns:Name space
                internal_phy:xml message to be analyzed
        '''
        internal_phy_name = internal_phy.find(xml_ns + "name").text
        internal_phy_opp = internal_phy.find(
            xml_ns + "opposite-node-name").text
        internal_phy_vlan = int(internal_phy.find(xml_ns + "vlan-id").text)
        internal_phy_addr = internal_phy.find(xml_ns + "address").text
        internal_phy_pre = int(internal_phy.find(xml_ns + "prefix").text)

        json["device"]["internal-physical"].append(
            {"name": internal_phy_name,
             "opposite-node-name": internal_phy_opp,
             "vlan-id": internal_phy_vlan,
             "address": internal_phy_addr,
             "prefix": internal_phy_pre})

    @decorater_log
    def _gen_json_internal_lag(self, json, xml_ns, itnal_lag):
        '''
            Obtain LAG information for internal Link from xml message to
            be analyzed and set it for EC message storage dictionary object.
            Explanation about parameter:
                json:dictionary object for EC message storage
                xml:xml message to be analyzed
                xml_ns:Name space
                itnal_lag:xml message to be analyzed
        '''
        internal_lag_message = {
            "name": None,
            "opposite-node-name": None,
            "lag-id": 0,
            "vlan-id": 0,
            "minimum-links": 0,
            "link-speed": 0,
            "address": None,
            "prefix": 0,
            "internal-interface_value": 0,
            "internal-interface": []
        }
        itnal_int_tag = xml_ns + "internal-interface"
        for itnal_int in itnal_lag.findall(".//" + itnal_int_tag):
            interface_name = itnal_int.find(xml_ns + "name").text
            internal_if_name = {"name": interface_name}
            internal_lag_message[
                "internal-interface"].append(internal_if_name)

        internal_lag_message["internal-interface_value"] = \
            len(internal_lag_message["internal-interface"])

        internal_lag_message["name"] = \
            itnal_lag.find(xml_ns + "name").text
        internal_lag_message["opposite-node-name"] = \
            itnal_lag.find(xml_ns + "opposite-node-name").text
        internal_lag_message["lag-id"] = \
            int(itnal_lag.find(xml_ns + "lag-id").text)
        internal_lag_message["vlan-id"] = \
            int(itnal_lag.find(xml_ns + "vlan-id").text)
        internal_lag_message["minimum-links"] = \
            int(itnal_lag.find(xml_ns + "minimum-links").text)
        internal_lag_message["link-speed"] = \
            itnal_lag.find(xml_ns + "link-speed").text
        internal_lag_message["address"] = \
            itnal_lag.find(xml_ns + "address").text
        internal_lag_message["prefix"] = \
            int(itnal_lag.find(xml_ns + "prefix").text)

        json["device"][
            "internal-lag"].append(internal_lag_message)

    @decorater_log
    def _gen_json_management(self, json, xml, xml_ns):
        '''
            Obtain management IF information from xml message to be analyzed
            and set it for EC message storage dictionary object.
            Explanation about parameter:
                json:dictionary object for EC message storage
                xml:xml message to be analyzed
                xml_ns:Name space
        '''
        man_elm = self._find_xml_node(xml,
                                      xml_ns + "management-interface")
        man_json = json["device"]["management-interface"]
        man_json["address"] = \
            man_elm.find(xml_ns + "address").text
        man_json["prefix"] = \
            int(man_elm.find(xml_ns + "prefix").text)

    @decorater_log
    def _gen_json_loopback(self, json, xml, xml_ns):
        '''
            Obtain loopback IF information from xml message to be analyzed
            and set it for EC message storage dictionary object.
            Explanation about parameter:
                json:dictionary object for EC message storage
                xml:xml message to be analyzed
                xml_ns:Name space
        '''
        loop_elm = self._find_xml_node(xml,
                                       xml_ns + "loopback-interface")
        loop_json = json["device"]["loopback-interface"]
        loop_json["address"] = \
            loop_elm.find(xml_ns + "address").text
        loop_json["prefix"] = \
            int(loop_elm.find(xml_ns + "prefix").text)

    @decorater_log
    def _gen_json_snmp(self, json, xml, xml_ns):
        '''
            Obtain SNMP information from xml message to be analyzed
            and set it for EC message storage dictionary object.
            Explanation about parameter:
                json:dictionary object for EC message storage
                xml:xml message to be analyzed
                xml_ns:Name space
        '''
        snmp_elm = self._find_xml_node(xml,
                                       xml_ns + "snmp")
        temp_json = json["device"]["snmp"]
        temp_json["server-address"] = \
            snmp_elm.find(xml_ns + "server-address").text
        temp_json["community"] = \
            snmp_elm.find(xml_ns + "community").text

    @decorater_log
    def _gen_json_ntp(self, json, xml, xml_ns):
        '''
            Obtain NTP information from xml message to be analyzed
            and set it for EC message storage dictionary object.
            Explanation about parameter:
                json:dictionary object for EC message storage
                xml:xml message to be analyzed
                xml_ns:Name space
        '''
        ntp_elm = self._find_xml_node(xml,
                                      xml_ns + "ntp")
        json["device"]["ntp"]["server-address"] = \
            ntp_elm.find(xml_ns + "server-address").text

    @decorater_log
    def _gen_json_ospf(self, json, xml, xml_ns):
        '''
            Obtain OSPF information from xml message to be analyzed
            and set it for EC message storage dictionary object.
            Explanation about parameter:
                json:dictionary object for EC message storage
                xml:xml message to be analyzed
                xml_ns:Name space
        '''
        ospf_elm = self._find_xml_node(xml,
                                       xml_ns + "ospf")
        json["device"]["ospf"]["area-id"] = \
            int(ospf_elm.find(xml_ns + "area-id").text)
