#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmCgwshServiceBase.py
'''
Base class for Cgwsh serivce scenario
'''
import copy
from lxml import etree
import datetime

from EmMergeScenario import EmMergeScenario
from EmCommonDriver import EmCommonDriver
import GlobalModule
from EmCommonLog import decorater_log


class EmCgwshServiceBase(EmMergeScenario):
    '''
    Base class for Cgwsh serivce scenario
    '''

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''
        super(EmCgwshServiceBase, self).__init__()

        self.device_type_1 = "nvrInfo"
        self.device_type_2 = "asrInfo"

        self._json_mes = {}

    @decorater_log
    def _connect_device(self,
                        device_name=None,
                        order_type=None,
                        transaction_id=None,
                        json_message=None):
        '''
        Connection process is started.
        Argument:
            device_name: device name (str)
            order_type: order type (str)
            transaction_id: transaction ID (uuid)
            json_message: EC message of json type (str)
        Return value:
            None
        '''
        self._json_mes[device_name] = json_message
        super(EmCgwshServiceBase, self)._connect_device(device_name,
                                                        order_type,
                                                        transaction_id,
                                                        json_message)
        try:
            self._get_device_setting(device_name=device_name,
                                     order_type=order_type,
                                     device_message=json_message,
                                     transaction_id=transaction_id,
                                     is_before=True)
        except Exception as exc_info:
            GlobalModule.EM_LOGGER.debug(exc_info.message)
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:15" +
                "(processing failure (get before config NG))",
                self.error_code02,
                self._scenario_name,
                device_name)
            self._find_subnormal(transaction_id,
                                 order_type,
                                 device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_GET_BEF_CONF,
                                 True,
                                 False)
            raise Exception("get before device config NG")

    @decorater_log
    def _setting_device(self,
                        device_name=None,
                        order_type=None,
                        transaction_id=None,
                        json_message=None):
        '''
        Device config is set.
        Argument:
            device_name: device name (str)
            order_type: order type (str)
            transaction_id: transaction ID (uuid)
            json_message: json type EC message (str)
        Return value:
            result (OK:True,NG:False) : boolean
        '''
        if order_type == GlobalModule.ORDER_DELETE:
            driver_method = (
                self.com_driver_list[device_name].delete_device_setting)
            update_ok = GlobalModule.COM_DELETE_OK
            validation_chack_NG = GlobalModule.COM_DELETE_VALICHECK_NG
            update_NG = GlobalModule.COM_DELETE_NG
            mtd_str = "delete"
        else:
            driver_method = (
                self.com_driver_list[device_name].update_device_setting)
            update_ok = GlobalModule.COM_UPDATE_OK
            validation_chack_NG = GlobalModule.COM_UPDATE_VALICHECK_NG
            update_NG = GlobalModule.COM_UPDATE_NG
            mtd_str = "update"

        is_result = driver_method(device_name,
                                  self.service,
                                  order_type,
                                  json_message)
        if is_result == update_ok:
            GlobalModule.EM_LOGGER.debug("%s_device_setting OK", mtd_str)
        else:
            if is_result == validation_chack_NG:
                GlobalModule.EM_LOGGER.debug(
                    "%s_device_setting validation check NG", mtd_str)
                GlobalModule.EM_LOGGER.warning(
                    "%s Scenario:%s Device:%s NG:9" +
                    "(processing failure (validation check NG))",
                    self.error_code02, self._scenario_name, device_name)

                self._find_subnormal(transaction_id, order_type, device_name,
                                     GlobalModule.TRA_STAT_PROC_ERR_CHECK,
                                     True, False)
            else:
                GlobalModule.EM_LOGGER.debug(
                    "%s_device_setting %s NG", mtd_str, mtd_str)
                GlobalModule.EM_LOGGER.warning(
                    "%s Scenario:%s Device:%s NG:16" +
                    "(processing failure (device setting NG))",
                    self.error_code02, self._scenario_name, device_name)
                self._find_subnormal(transaction_id, order_type, device_name,
                                     GlobalModule.TRA_STAT_PROC_ERR_SET_DEV,
                                     True, False)
            raise Exception("{0}_device_setting NG".format(mtd_str))

    @decorater_log
    def _disconnect_device(self,
                           device_name=None,
                           order_type=None,
                           transaction_id=None,
                           service_type=None,
                           is_only_disconnect=False):
        '''
        Disconnection process is executed.
        Argument:
            device_name: device name (str)
            order_type: order type (str)
            transaction_id: transaction ID (uuid)
            service_type: servive type(if is required) (int)
            is_only_disconnect: True if only disconnction process is excuted (boolean)
        Return value:
            None
        '''
        is_get_ok = True
        try:
            json_message = self._json_mes.get(device_name)
            self._get_device_setting(device_name=device_name,
                                     order_type=order_type,
                                     device_message=json_message,
                                     transaction_id=transaction_id)
        except Exception as exc_info:
            GlobalModule.EM_LOGGER.debug(exc_info.message)
            GlobalModule.EM_LOGGER.debug("get after device config NG")
            is_get_ok = False
        super(EmCgwshServiceBase, self)._disconnect_device(
            device_name=device_name,
            order_type=order_type,
            transaction_id=transaction_id,
            service_type=service_type,
            is_only_disconnect=is_only_disconnect)
        if not is_get_ok and not is_only_disconnect:
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:17" +
                "(Processing failure (get after config NG))",
                self.error_code02,
                self._scenario_name,
                device_name)
            self._find_subnormal(transaction_id,
                                 order_type,
                                 device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_GET_AFT_CONF,
                                 False,
                                 False)
            raise Exception("get after device config NG")

    @decorater_log
    def _register_the_setting_in_em(self,
                                    device_name=None,
                                    order_type=None,
                                    device_message=None,
                                    transaction_id=None,):
        '''
        Information is registred in DB.
        Argument:
            device_name: device name (str)
            order_type: order type (str)
            device_message: EC message for device(byte)
            transaction_id: transaction ID (uuid)
        Return value:
            None
        '''
        pass

    @decorater_log
    def _get_device_setting(self,
                            device_name=None,
                            order_type=None,
                            device_message=None,
                            transaction_id=None,
                            is_before=False):
        '''
        Device informatin is acquired.
        Argument:
            device_name: device name (str)
            order_type: order type (str)
            device_message: json message (str)
            transaction_id: transaction ID (uuid)
            is_before : advanced acquiring  (True: advanced /False:not advanced) (boolean)
        Return value:
            None
        '''
        try:
            com_driver = self.com_driver_list[device_name]
            is_ok, dev_signal = com_driver.get_device_setting(device_name,
                                                              self.service,
                                                              order_type,
                                                              is_before)

            if not is_ok:
                raise Exception("get device setting NG")

            if dev_signal:
                working_date, working_time = self._get_working_datetime()
                method = (
                    GlobalModule.CGWSH_DEV_UTILITY_DB.write_show_config_info)
                is_ok = method(device_name,
                               working_date,
                               working_time,
                               device_message,
                               dev_signal,
                               is_before)
                if not is_ok:
                    raise Exception("write config Info NG")
        except Exception:
            raise
        else:
            GlobalModule.EM_LOGGER.debug("get and write device setting OK")

    @decorater_log
    def _get_working_datetime(self):
        '''
        Working date and time is returned.
        Argument:
            None
        Return value:
            working date : str
            working time : str
        '''
        tmp_date = datetime.datetime.now()
        working_date = tmp_date.strftime("%Y%m%d")
        working_time = tmp_date.strftime("%H%M%S")
        return working_date, working_time

    @decorater_log
    def _analyze_ec_message(self, ec_message):
        '''
        Netconf message is analyzed.
            Netconf message received from order flow control is divided for each devive
        Argument:
            ec_message : Netconf message
        Return value:
            device name:dictionary type of Netconf message in each device
        '''

        device_name_list = []
        device_xml_dict = {}
        device_type_1 = None
        device_type_2 = None

        ec_edit_message = copy.deepcopy(ec_message)

        context = etree.iterparse(ec_edit_message, events=('start', 'end'))

        GlobalModule.EM_LOGGER.debug("SERVICE : %s , NS : %s"
                                     % (self.service, self._xml_ns))

        for event, element in context:
            GlobalModule.EM_LOGGER.debug(
                "Analyze Message event:%s element.tag:%s", event, element.tag)

            if event == "start" and element.tag == self._xml_ns + self.service:
                GlobalModule.EM_LOGGER.debug("SERVICE : %s" % (self.service))
                slice_name = element.find(self._xml_ns + "name").text
                GlobalModule.EM_LOGGER.debug("service name: %s", slice_name)
                ns_value = self._xml_ns
                device_type_1 = self.device_type_1
                device_type_2 = self.device_type_2
                break
            else:
                GlobalModule.EM_LOGGER.debug("Not SERVICE Tag")

        GlobalModule.EM_LOGGER.debug("device_type:%s", device_type_1)
        GlobalModule.EM_LOGGER.debug("device_type:%s", device_type_2)

        for event, element in context:

            GlobalModule.EM_LOGGER.debug("EVENT : %s , ELEMENT : %s"
                                         % (event, element))

            if event == "end" and element.tag in (ns_value + device_type_1,
                                                  ns_value + device_type_2):
                device_tag = (ns_value + "managementInfo" + "/" +
                              ns_value + "hostname")
                device_name = element.find(".//" + device_tag).text
                device_name_list.append(device_name)

                device_xml_dict[device_name] = \
                    self._gen_netconf_message(element, slice_name)
                GlobalModule.EM_LOGGER.debug(
                    "device_xml_dict: %s", device_xml_dict[device_name])
                GlobalModule.EM_LOGGER.debug(
                    "device_name_list: %s", device_name_list)

        return device_name_list, device_xml_dict
