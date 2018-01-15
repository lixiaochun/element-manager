#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2017 Nippon Telegraph and Telephone Corporation
# Filename: EmInternalLinkDelete.py
'''
Individual scenario for deleting IF for internal Link.   
'''
import threading
import json
from lxml import etree
import EmSeparateScenario
from EmCommonDriver import EmCommonDriver
import GlobalModule
from EmCommonLog import decorater_log


class EmInternalLinkDelete(EmSeparateScenario.EmScenario):
    '''
    Class for deleting IF for internal Link.  
    '''



    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmInternalLinkDelete, self).__init__()

        self.service = GlobalModule.SERVICE_INTERNAL_LINK

        self._xml_ns = "{%s}" % GlobalModule.EM_NAME_SPACES[self.service]

        self.timeout_flag = False

        self.device_type = "device"

    @decorater_log
    def _gen_sub_thread(
            self, device_message,
            transaction_id, order_type, condition, device_name, force):
        '''
        Conduct IF deletion control for internal link for each device. 
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
            "104001 Scenario:InternalLinkDelete Device:%s start", device_name)

        self.com_driver_list[device_name] = EmCommonDriver()

        is_db_result = \
            GlobalModule.EMSYSCOMUTILDB.write_transaction_device_status_list(
                "UPDATE", device_name, transaction_id,
                GlobalModule.TRA_STAT_PROC_RUN)

        if is_db_result is False:
            GlobalModule.EM_LOGGER.debug(
                " write_transaction_device_status_list(1:processing) NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:InternalLinkDelete Device:%s \
                    NG:13(Processing failure (temporary))",
                device_name)
            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:InternalLinkDelete Device:%s end",
                device_name)
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
                "204004 Scenario:InternalLinkDelete Device:%s \
                    NG:13(Processing failure (temporary))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:InternalLinkDelete Device:%s end",
                device_name)
            return

        GlobalModule.EM_LOGGER.debug("start OK")

        is_comdriver_result = self.com_driver_list[device_name].connect_device(
            device_name, "internal-link", order_type, json_message)

        if is_comdriver_result == GlobalModule.COM_CONNECT_NG:
            GlobalModule.EM_LOGGER.debug("connect_device NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:InternalLinkDelete Device:%s \
                    NG:14(Processing failure (Other))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:InternalLinkDelete Device:%s end",
                device_name)
            return

        elif is_comdriver_result == GlobalModule.COM_CONNECT_NO_RESPONSE:
            GlobalModule.EM_LOGGER.debug("connect_device no reply")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:InternalLinkDelete Device:%s \
                    NG:13(Processing failure (temporary))", device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:InternalLinkDelete Device:%s end",
                device_name)
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
                "204004 Scenario:InternalLinkDelete Device:%s \
                    NG:14(Processing failure (Other))", device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 True, True)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:InternalLinkDelete Device:%s end",
                device_name)
            return

        GlobalModule.EM_LOGGER.debug(
            "write_transaction_device_status_list(2:Edit-config) OK")

        is_comdriver_result = self.com_driver_list[
            device_name].delete_device_setting(
                device_name, "internal-link", order_type, json_message)

        if is_comdriver_result == GlobalModule.COM_DELETE_VALICHECK_NG:
            GlobalModule.EM_LOGGER.debug("delete_device_setting validation checkNG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:InternalLinkDelete Device:%s \
                NG:9(Processing failure(validation checkNG))", device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_CHECK,
                                 True, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:InternalLinkDelete Device:%s end",
                device_name)
            return

        elif is_comdriver_result == GlobalModule.COM_DELETE_NG:
            GlobalModule.EM_LOGGER.debug("delete_device_setting error")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:InternalLinkDelete Device:%s \
                    NG:13(Processing failure (temporary))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 True, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:InternalLinkDelete Device:%s end",
                device_name)
            return

        GlobalModule.EM_LOGGER.debug("delete_device_setting OK")

        is_db_result = \
            GlobalModule.EMSYSCOMUTILDB.write_transaction_device_status_list(
                "UPDATE", device_name, transaction_id,
                GlobalModule.TRA_STAT_CONF_COMMIT)

        if is_db_result is False:
            GlobalModule.EM_LOGGER.debug(
                "write_transaction_device_status_list(3:Confirmed-commit) NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:InternalLinkDelete Device:%s \
                    NG:14(Processing failure (Other))", device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 True, True)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:InternalLinkDelete Device:%s end",
                device_name)
            return

        GlobalModule.EM_LOGGER.debug(
            "write_transaction_device_status_list(3:Confirmed-commit) OK")

        is_comdriver_result = self.com_driver_list[
            device_name].reserve_device_setting(
                device_name, "internal-link", order_type)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("reserve_device_setting NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:InternalLinkDelete Device:%s \
                NG:13(Processing failure (temporary))", device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 True, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:InternalLinkDelete Device:%s end",
                device_name)
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
                "204004 Scenario:InternalLinkDelete Device:%s \
                    NG:14(Processing failure (Other))",
                device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 True, True)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:InternalLinkDelete Device:%s end",
                device_name)
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
                "104002 Scenario:InternalLinkDelete Device:%s end",
                device_name)
            return

        GlobalModule.EM_LOGGER.debug("No timeout detection")

        timer.cancel()

        is_comdriver_result = self.com_driver_list[
            device_name].enable_device_setting(
                device_name, "internal-link", order_type)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("enable_device_setting NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:InternalLinkDelete Device:%s \
                    NG:13(Processing failure (temporary))", device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 True, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:InternalLinkDelete Device:%s end",
                device_name)
            return

        GlobalModule.EM_LOGGER.debug("enable_device_setting OK")

        is_comdriver_result = self.com_driver_list[
            device_name].disconnect_device(
                device_name, "internal-link", order_type)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("disconnect_device NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:InternalLinkDelete Device:%s \
                NG:13(Processing failure (temporary))", device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_TEMP,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:InternalLinkDelete Device:%s end",
                device_name)
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
                "204004 Scenario:InternalLinkDelete Device:%s \
                    NG:13(Processing failure (temporary))",
                device_name)
            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:InternalLinkDelete Device:%s end",
                device_name)
            return

        GlobalModule.EM_LOGGER.debug(
            "write_transaction_device_status_list(5:Successful completion) OK")

        is_comdriver_result = self.com_driver_list[device_name].write_em_info(
            device_name, "internal-link", order_type, device_message)

        if is_comdriver_result is False:
            GlobalModule.EM_LOGGER.debug("write_em_info NG")
            GlobalModule.EM_LOGGER.warning(
                "204004 Scenario:InternalLinkDelete Device:%s \
                    NG:14(Processing failure (Other))", device_name)

            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 False, False)

            GlobalModule.EM_LOGGER.info(
                "104002 Scenario:InternalLinkDelete Device:%s end",
                device_name)
            return

        GlobalModule.EM_LOGGER.debug("write_em_info OK")

        GlobalModule.EM_LOGGER.info(
            "104002 Scenario:InternalLinkDelete Device:%s end", device_name)
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
    def __creating_json(self, device_message):
        '''
        Convert EC message (XML) divided for each device into JSON. 
        Explanation about parameter：
            device_message: Message for each device
        Explanation about return value
            device_json_message: JSON message
        '''

        device_json_message = {
            "device":
            {
                "name": None,
                "internal-physical_value": 0,
                "internal-physical": [],
                "internal-lag_value": 0,
                "internal-lag": []
            }
        }

        xml_elm = etree.fromstring(device_message)

        GlobalModule.EM_LOGGER.debug(
            "device_message = %s", etree.tostring(xml_elm, pretty_print=True))

        self._gen_json_name(
            device_json_message, xml_elm, self._xml_ns)

        self._gen_json_internal_if(
            device_json_message, xml_elm, self._xml_ns)

        GlobalModule.EM_LOGGER.debug(
            "device__json_message = %s", device_json_message)

        return json.dumps(device_json_message)

    @decorater_log
    def _gen_json_name(self, json, xml, xml_ns):
        '''
            Obtain device name from xml message to be analyzed 
            and set it for EC message storage dictionary object. 
            Explanation about parameter：
                json：dictionary object for EC message storage 
                xml：xml message to be analyzed 
                xml_ns：Name space
        '''

        name_elm = self._find_xml_node(xml, xml_ns + "name")
        json["device"]["name"] = name_elm.text

    @decorater_log
    def _gen_json_internal_if(self, json, xml, xml_ns):
        '''
            Obtain IF information for internal Link from xml message to be analyzed 
            and set it for EC message storage dictionary object. 
            Explanation about parameter：
                json：dictionary object for EC message storage 
                xml：xml message to be analyzed 
                xml_ns：Name space
        '''

        internal_if_elm = self._find_xml_node(xml,
                                              xml_ns + "internal-interface")

        if internal_if_elm is not None:
            internal_if_tag = xml_ns + "internal-interface"
            for internal_if_lag in xml.findall(".//" + internal_if_tag):
                if internal_if_lag.find(xml_ns + "type") is not None:
                    internal_if_type = internal_if_lag.find(
                        xml_ns + "type").text
                    if internal_if_type == "physical-if":
                        GlobalModule.EM_LOGGER.debug(
                            "Test _gen_json_internal_phy Start")
                        self._gen_json_internal_phy(
                            json, xml_ns, internal_if_lag)
                    elif internal_if_type == "lag-if":
                        GlobalModule.EM_LOGGER.debug(
                            "Test _gen_json_internal_lag Start")
                        self._gen_json_internal_lag(
                            json, xml_ns, internal_if_lag)

        json["device"]["internal-physical_value"] = \
            len(json["device"]["internal-physical"])

        json["device"]["internal-lag_value"] = \
            len(json["device"]["internal-lag"])

    @decorater_log
    def _gen_json_internal_phy(self, json, xml_ns, internal_phy):
        '''
            Obtain physical IF information for internal Link from xml message to be analyzed 
            and set it for EC message storage dictionary object. 
            Explanation about parameter：
                json：dictionary object for EC message storage
                xml_ns：Name space
                internal_phy：xml message to be analyzed
        '''

        internal_phy_name = internal_phy.find(xml_ns + "name").text
        json["device"]["internal-physical"].append(
            {"name": internal_phy_name})

    @decorater_log
    def _gen_json_internal_lag(self, json, xml_ns, itnal_lag):
        '''
            Obtain LAG information for internal Link from xml message to be analyzed 
and set it for EC message storage dictionary object. 
            Explanation about parameter：
                json：dictionary object for EC message storage
                xml_ns：Name space
                itnal_lag：xml message to be analyzed
        '''
        internal_lag_message = {
            "name": None,
            "minimum-links": 0,
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
        internal_lag_message["minimum-links"] = \
            int(itnal_lag.find(xml_ns + "minimum-links").text)

        json["device"][
            "internal-lag"].append(internal_lag_message)
