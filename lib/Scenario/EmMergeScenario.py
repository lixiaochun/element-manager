#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmMargeScenario.py
'''
Class which is common for scenario creation.
'''
import threading
import traceback
import EmSeparateScenario
from EmCommonDriver import EmCommonDriver
import GlobalModule
from EmCommonLog import decorater_log


class EmMergeScenario(EmSeparateScenario.EmScenario):
    '''
    Class which is common for scenario creation.
    '''


    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmMergeScenario, self).__init__()

        self._xml_ns = ""

        self.timeout_flag = False

        self._scenario_name = ""

        self.service = ""

        self.error_code01 = "104001"
        self.error_code02 = "204004"
        self.error_code03 = "104002"

    @decorater_log
    def _gen_sub_thread(self,
                        device_message=None,
                        transaction_id=None,
                        order_type=None,
                        condition=None,
                        device_name=None,
                        force=False):
        ''' 
        Controlls  generation for each device
        Explanation about parameter:
            device_message: Message for each device(byte)
            transaction_id: Transaction ID (uuid)
            order_type: Order type(int)
            condition: Treaf control information  (condition object)
            device_name: Device name (str)
            force: Flag of deletion to be forced(boolean)
        Explanation about return value:
            None           
        '''
        try:
            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s start",
                self.error_code01, self._scenario_name, device_name)
            self._process_scenario(device_message,
                                   transaction_id,
                                   order_type,
                                   condition,
                                   device_name,
                                   force)
        except Exception as exc_info:
            GlobalModule.EM_LOGGER.debug("Scenario Error:%s", exc_info.message)
        finally:
            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code03, self._scenario_name, device_name)

    @decorater_log
    def _process_scenario(self,
                          device_message=None,
                          transaction_id=None,
                          order_type=None,
                          condition=None,
                          device_name=None,
                          force=False):
        '''
        Executes scenario process for each device
        Explanation about parameter:
            device_message: Message for each device(byte)
            transaction_id: Transaction ID (uuid)
            order_type: Order type(int)
            condition: Treaf control information  (condition object)
            device_name: Device name (str)
            force: Flag of deletion to be forced(boolean)
        Explanation about return value:
            None
        '''

        self.com_driver_list[device_name] = EmCommonDriver()

        self._device_state_transition(
            device_name=device_name,
            order_type=order_type,
            transaction_id=transaction_id,
            transition_state=GlobalModule.TRA_STAT_PROC_RUN,
            failure_state=GlobalModule.TRA_STAT_PROC_ERR_TEMP)
            
        try:
            json_message = self._creating_json(device_message)
        except Exception:
            GlobalModule.EM_LOGGER.debug("receive message parse NG")
            GlobalModule.EM_LOGGER.debug("Traceback:%s",
                                         traceback.format_exc())
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:4" +
                "(Processing failure (Inadequate request))",
                self.error_code02, self._scenario_name, device_name)
            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_ORDER,
                                 False, False)
            raise
        else:
            GlobalModule.EM_LOGGER.debug("json_message =%s", json_message)

        self._start_common_driver(device_name=device_name,
                                  order_type=order_type,
                                  transaction_id=transaction_id,
                                  json_message=json_message)

        self._connect_device(device_name=device_name,
                             order_type=order_type,
                             transaction_id=transaction_id,
                             json_message=json_message)

        self._device_state_transition_with_timer(
            device_name=device_name,
            order_type=order_type,
            transaction_id=transaction_id,
            transition_state=GlobalModule.TRA_STAT_EDIT_CONF,
            failure_state=GlobalModule.TRA_STAT_PROC_ERR_OTH,
            is_connected=True,
            get_timer_method=self._get_timer_value_for_connect,
            condition=condition,
            is_roleback=True,
            is_retry=True)

        self._setting_device(device_name=device_name,
                             order_type=order_type,
                             transaction_id=transaction_id,
                             json_message=json_message)

        self._device_state_transition(
            device_name=device_name,
            order_type=order_type,
            transaction_id=transaction_id,
            transition_state=GlobalModule.TRA_STAT_CONF_COMMIT,
            failure_state=GlobalModule.TRA_STAT_PROC_ERR_OTH,
            is_connected=True)

        self._reserve_device(device_name=device_name,
                             order_type=order_type,
                             transaction_id=transaction_id)

        self._device_state_transition_with_timer(
            device_name=device_name,
            order_type=order_type,
            transaction_id=transaction_id,
            transition_state=GlobalModule.TRA_STAT_COMMIT,
            failure_state=GlobalModule.TRA_STAT_PROC_ERR_OTH,
            is_connected=True,
            get_timer_method=self._get_timer_value_for_confirmed_commit,
            condition=condition,
            is_roleback=True)

        self._enable_device(device_name=device_name,
                            order_type=order_type,
                            transaction_id=transaction_id)

        self._disconnect_device(device_name=device_name,
                                order_type=order_type,
                                transaction_id=transaction_id)

        self._device_state_transition_with_timer(
            device_name=device_name,
            order_type=order_type,
            transaction_id=transaction_id,
            transition_state=GlobalModule.TRA_STAT_PROC_END,
            failure_state=GlobalModule.TRA_STAT_PROC_ERR_OTH,
            is_connected=False,
            get_timer_method=self._get_timer_value_for_disconnect,
            condition=condition,
            is_roleback=False)

        self._register_the_setting_in_em(device_name=device_name,
                                         order_type=order_type,
                                         device_message=device_message,
                                         transaction_id=transaction_id)

        GlobalModule.EM_LOGGER.debug("scenario all ok.")

    @decorater_log
    def _start_common_driver(self,
                             device_name=None,
                             order_type=None,
                             transaction_id=None,
                             json_message=None):
        '''
        Starts Driver common part process.
        Explanation about parameter:
            device_name: Device name (str)
            order_type: Order type(int)
            transaction_id: Transaction ID (uuid)
            json_message: EC Message with json type
        Explanation about return value:
        '''
        com_driver = self.com_driver_list[device_name]
        is_comdriver_result = com_driver.start(device_name, json_message)

        self._check_start_common_driver(device_name,
                                        order_type,
                                        transaction_id,
                                        is_comdriver_result)

    @decorater_log
    def _check_start_common_driver(self,
                                   device_name=None,
                                   order_type=None,
                                   transaction_id=None,
                                   is_result=True):
        '''
        Checks result of drive common start process.
        Explanation about parameter:
            device_name: Device name (str)
            order_type: Order type(str)
            transaction_id: Transaction ID (uuid)
            is_result: Result (True)
        Explanation about return value:
            None
        '''
        if is_result == GlobalModule.COM_START_OK:
            GlobalModule.EM_LOGGER.debug("start OK")
        else:
            GlobalModule.EM_LOGGER.debug("start NG")
            if is_result == GlobalModule.COM_START_NO_DEVICE_NG:
                GlobalModule.EM_LOGGER.warning(
                    "%s Scenario:%s Device:%s NG:12" +
                    "(Processing failure (Stored information None))",
                    self.error_code02, self._scenario_name, device_name)
                self._find_subnormal(transaction_id, order_type, device_name,
                                     GlobalModule.TRA_STAT_PROC_ERR_INF,
                                     False, False)
            else:
                GlobalModule.EM_LOGGER.warning(
                    "%s Scenario:%s Device:%s NG:14" +
                    "(Processing failure (other))",
                    self.error_code02, self._scenario_name, device_name)
                self._find_subnormal(transaction_id, order_type, device_name,
                                     GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                     False, False)
            raise Exception("common_driver_start NG")

    @decorater_log
    def _connect_device(self,
                        device_name=None,
                        order_type=None,
                        transaction_id=None,
                        json_message=None):
        '''
        Connects with device.
        Explanation about parameter:
            device_name: Device name (str)
            order_type: Order type(str)
            transaction_id: Transaction ID (uuid)
            json_message: EC message with json type (str)
        Explanation about return value:            
            None
        '''
        com_driver = self.com_driver_list[device_name]
        is_ok = com_driver.connect_device(device_name,
                                          self.service,
                                          order_type,
                                          json_message)
        if is_ok == GlobalModule.COM_CONNECT_OK:
            GlobalModule.EM_LOGGER.debug("connect_device OK")
        else:
            if is_ok == GlobalModule.COM_CONNECT_NG:
                GlobalModule.EM_LOGGER.debug("connect_device NG")
            else:
                GlobalModule.EM_LOGGER.debug("connect_device no reply")
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:12" +
                "(Processing failure (Stored information None))",
                self.error_code02, self._scenario_name, device_name)
            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_INF,
                                 False, False)
            raise Exception("connect_device NG")

    @decorater_log
    def _setting_device(self,
                        device_name=None,
                        order_type=None,
                        transaction_id=None,
                        json_message=None):
        '''
        Sets device.
        Explanation about parameter:
            device_name: Device name (str)
            order_type: Order type(str)
            transaction_id: Transaction ID (uuid)
            json_message: EC message with json type (str)
        Explanation about return value:            
            None           
        '''
        com_driver = self.com_driver_list[device_name]
        is_result = com_driver.update_device_setting(device_name,
                                                     self.service,
                                                     order_type,
                                                     json_message)
        if is_result == GlobalModule.COM_UPDATE_OK:
            GlobalModule.EM_LOGGER.debug("update_device_setting OK")
        else:
            if is_result == GlobalModule.COM_UPDATE_VALICHECK_NG:
                GlobalModule.EM_LOGGER.debug(
                    "update_device_setting validation check NG")
                GlobalModule.EM_LOGGER.warning(
                    "%s Scenario:%s Device:%s NG:9" +
                    "(Processing failure (validation check NG))",
                    self.error_code02, self._scenario_name, device_name)

                self._find_subnormal(transaction_id, order_type, device_name,
                                     GlobalModule.TRA_STAT_PROC_ERR_CHECK,
                                     True, False)
            else:

                GlobalModule.EM_LOGGER.debug("update_device_setting update NG")
                GlobalModule.EM_LOGGER.warning(
                    "%s Scenario:%s Device:%s NG:16" +
                    "(Processing failure (device setting NG))",
                    self.error_code02, self._scenario_name, device_name)
                self._find_subnormal(transaction_id, order_type, device_name,
                                     GlobalModule.TRA_STAT_PROC_ERR_SET_DEV,
                                     True, False)
            raise Exception("update_device_setting NG")

    @decorater_log
    def _reserve_device(self,
                        device_name=None,
                        order_type=None,
                        transaction_id=None):
        '''
        Reserves device setting
        Explanation about parameter:
            device_name: Device name (str)
            order_type: Order type(str)
            transaction_id: Transaction ID (uuid)
        Explanation about return value:            
            None
        '''
        com_driver = self.com_driver_list[device_name]
        is_ok = com_driver.reserve_device_setting(device_name,
                                                  self.service,
                                                  order_type)
        if is_ok:
            GlobalModule.EM_LOGGER.debug("reserve_device_setting OK")
        else:
            GlobalModule.EM_LOGGER.debug("reserve_device_setting NG")
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:16" +
                "(Processing failure (device setting NG))",
                self.error_code02, self._scenario_name, device_name)
            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_SET_DEV,
                                 True, False)
            raise Exception("reserve_device_setting NG")

    @decorater_log
    def _enable_device(self,
                       device_name=None,
                       order_type=None,
                       transaction_id=None):
        '''
        Enables device setting
        Explanation about parameter:
            device_name: Device name (str)
            order_type: Order type(str)
            transaction_id: Transaction ID (uuid)
        Explanation about return value:            
            None
        '''
        com_driver = self.com_driver_list[device_name]
        is_ok = com_driver.enable_device_setting(device_name,
                                                 self.service,
                                                 order_type)

        if is_ok:
            GlobalModule.EM_LOGGER.debug("enable_device_setting OK")
        else:
            GlobalModule.EM_LOGGER.debug("enable_device_setting NG")
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:14" +
                "(Processing failure (other))",
                self.error_code02, self._scenario_name, device_name)
            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 True, False)
            raise Exception("enable_device_setting NG")

    @decorater_log
    def _disconnect_device(self,
                           device_name=None,
                           order_type=None,
                           transaction_id=None,
                           service_type=None,
                           is_only_disconnect=False):
        '''
        Disconnectes device.
        Explanation about parameter:
            device_name: Device name (str)
            order_type: Order type(str)
            transaction_id: Transaction ID (uuid)
            service_type: Serice type(if it is required) (int)
            is_only_disconnect: True, if only disconnection is executed (boolean)           
        Explanation about return value:            
            None
        '''
        service_type = service_type if service_type else self.service
        com_driver = self.com_driver_list[device_name]
        is_ok = com_driver.disconnect_device(device_name,
                                             service_type,
                                             order_type)
        if is_ok:
            GlobalModule.EM_LOGGER.debug("disconnect_device OK")
        else:
            GlobalModule.EM_LOGGER.debug("disconnect_device NG")
            GlobalModule.EM_LOGGER.debug("get after setting config NG")
            if not is_only_disconnect:
                GlobalModule.EM_LOGGER.warning(
                    "%s Scenario:%s Device:%s NG:17" +
                    "(Processing failure (get after config NG))",
                    self.error_code02, self._scenario_name, device_name)

                self._find_subnormal(
                    transaction_id, order_type, device_name,
                    GlobalModule.TRA_STAT_PROC_ERR_GET_AFT_CONF,
                    False, False)
                raise Exception("disconnect_device NG")

    @decorater_log
    def _register_the_setting_in_em(self,
                                    device_name=None,
                                    order_type=None,
                                    device_message=None,
                                    transaction_id=None,):
        '''
        Registers information in DB.
        Explanation about parameter:
            device_name: Device name (str)
            order_type: Order type(str)
            device_message: EC message for device(byte)
            transaction_id: Transaction ID (uuid)          
        Explanation about return value:            
            None
        '''
        com_driver = self.com_driver_list[device_name]
        is_ok = com_driver.write_em_info(device_name,
                                         self.service,
                                         order_type,
                                         device_message)

        if is_ok:
            GlobalModule.EM_LOGGER.debug("write_em_info OK")
        else:
            GlobalModule.EM_LOGGER.debug("write_em_info NG")
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:14" +
                "(Processing failure (other))",
                self.error_code02, self._scenario_name, device_name)
            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                 False, False)
            raise Exception("write_em_info NG")

    @decorater_log
    def _device_state_transition(self,
                                 device_name=None,
                                 order_type=None,
                                 transaction_id=None,
                                 transition_state=None,
                                 failure_state=None,
                                 is_connected=False,
                                 timer=None,
                                 ):
        '''
        Registers information in DB.
        Explanation about parameter:
            device_name: Device name (str)
            order_type: Order type (str)
            transaction_id: Transaction ID (uuid) 
            transition_state: Executing status(next status) (int)
            failure_state: Next status in case of failure (int)
            is_connected: Connecting status or not(If yes,True) (boolean)
            timer: Timer object(if it is available, stop this process)         
        Explanation about return value:            
            None
        '''
        log_txt_states = {
            GlobalModule.TRA_STAT_PROC_RUN: "processing",
            GlobalModule.TRA_STAT_EDIT_CONF: "Edit-config",
            GlobalModule.TRA_STAT_CONF_COMMIT: "Confirmed-commit",
            GlobalModule.TRA_STAT_COMMIT: "Commit",
            GlobalModule.TRA_STAT_PROC_END: "Successful completion",
            GlobalModule.TRA_STAT_PROC_ERR_TEMP:
            "Processing failure (temporary)",
            GlobalModule.TRA_STAT_PROC_ERR_OTH: "Processing failure (Other)",
        }
        log_state = log_txt_states.get(transition_state)
        log_err_state = log_txt_states.get(failure_state)
        debug_log_txt = "write_transaction_device_status_list(%s:%s) %s"


        is_ok = (
            GlobalModule.EMSYSCOMUTILDB.write_transaction_device_status_list(
                "UPDATE",
                device_name,
                transaction_id,
                transition_state))

        if is_ok:
            GlobalModule.EM_LOGGER.debug(
                debug_log_txt, transition_state, log_state, "OK")
        else:
            if timer:
                timer.cancel()
            GlobalModule.EM_LOGGER.debug(
                debug_log_txt, transition_state, log_state, "NG")
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:%s(Processing failure (%s))",
                self.error_code02,
                self._scenario_name,
                device_name,
                failure_state,
                log_err_state)
            if is_connected:
                self._find_subnormal(transaction_id,
                                     order_type,
                                     device_name,
                                     GlobalModule.TRA_STAT_PROC_ERR_OTH,
                                     True,
                                     True)
            raise Exception(
                debug_log_txt % (transition_state, log_state, "NG"))

    @decorater_log
    def _device_state_transition_with_timer(self,
                                            device_name=None,
                                            order_type=None,
                                            transaction_id=None,
                                            transition_state=None,
                                            failure_state=None,
                                            is_connected=False,
                                            get_timer_method=None,
                                            condition=None,
                                            is_roleback=True,
                                            is_retry=False):
        '''
        Waits for timer after it moves  to status in which device information is specified.
        Waits for receiving order.   
        Explanation about parameter:
            device_name: Device name (str)
            order_type: Order type (str)
            transaction_id: Transaction ID (uuid) 
            transition_state: Executing status(next status) (int)
            failure_state: Next status in case of failure (int)
            is_connected: Connecting status or not(If yes,True) (boolean)
                        get_timer_method: Method for acquiring timer value (method)
            condition: Thread control information (thread object)
            is_roleback: Rollback is needed? (If yes,True) (boolean)
            is_retry : Flag on whether network operater is needed or not(If not, True) (boolean)         
        Explanation about return value:            
            None
        '''
        timer_value = get_timer_method()
        self._initialize_timeout_flag()

        timer = threading.Timer(timer_value,
                                self._find_timeout,
                                args=[condition])
        try:
            timer.start()
            self._device_state_transition(
                device_name=device_name,
                order_type=order_type,
                transaction_id=transaction_id,
                transition_state=transition_state,
                failure_state=failure_state,
                is_connected=is_connected,
                timer=timer)

            GlobalModule.EM_LOGGER.debug("Condition wait")
            condition.acquire()
            condition.wait()
            condition.release()
            GlobalModule.EM_LOGGER.debug("Condition notify restart")

            if self.timeout_flag:
                GlobalModule.EM_LOGGER.debug("timeout detection")
                if is_roleback:
                    GlobalModule.EM_LOGGER.info(
                        "104003 Rollback for Device:%s", device_name)
                    if is_retry:
                        trans = GlobalModule.TRA_STAT_PROC_ERR_STOP_RETRY
                    else:
                        trans = GlobalModule.TRA_STAT_PROC_ERR_STOP_NO_RETRY
                    self._find_subnormal(
                        transaction_id, order_type, device_name,
                        trans, True, False)
                else:
                    GlobalModule.EM_LOGGER.debug(
                        "Device is disconnected. Rollback is impossible.")
                raise Exception("Timeout occurred")
            else:
                GlobalModule.EM_LOGGER.debug("no timeout detection")
        finally:
            timer.cancel()

    @decorater_log
    def _initialize_timeout_flag(self):
        '''
        Initializes timeout_flag
        '''
        self.timeout_flag = False

    @decorater_log
    def _get_timer_value_for_connect(self):
        '''
        Gets Timer value for connection
        Explanation about parameter:
            None
        Explanation about return value:
            waiting time for connection; int
        '''
        is_config_result, return_value = (
            GlobalModule.EM_CONFIG.read_sys_common_conf(
                "Timer_connect_get_before_config"))

        if is_config_result:
            GlobalModule.EM_LOGGER.debug("read_sys_common_conf OK")
            return_value = int(return_value) / 1000
        else:
            GlobalModule.EM_LOGGER.debug("read_sys_common_conf NG")
            return_value = 600
        GlobalModule.EM_LOGGER.debug("connect wait %s", return_value)
        return return_value

    @decorater_log
    def _get_timer_value_for_confirmed_commit(self):
        '''
        Gets Timer value for confirmed-commit
        Explanation about parameter:
            None
        Explanation about return value:
            waiting time for confirmed-commit ; int
        '''
        is_config_result, return_value = (
            GlobalModule.EM_CONFIG.read_sys_common_conf(
                "Timer_confirmed-commit"))
        is_config_result_second, return_value_em_offset = (
            GlobalModule.EM_CONFIG.read_sys_common_conf(
                "Timer_confirmed-commit_em_offset"))


        if is_config_result and is_config_result_second:
            GlobalModule.EM_LOGGER.debug("read_sys_common_conf OK")
            return_value = (return_value + return_value_em_offset) / 1000
        else:
            GlobalModule.EM_LOGGER.debug("read_sys_common_conf NG")
            return_value = 600
        GlobalModule.EM_LOGGER.debug("confirmed commit wait %s", return_value)
        return return_value

    @decorater_log
    def _get_timer_value_for_disconnect(self):
        '''
        Gets Timer value for disconnection
        Explanation about parameter:
            None
        Explanation about return value:
            waiting time for disconnection ; int
        '''
        is_config_result, return_value = (
            GlobalModule.EM_CONFIG.read_sys_common_conf(
                "Timer_disconnect_get_after_config"))

        if is_config_result:
            GlobalModule.EM_LOGGER.debug("read_sys_common_conf OK")
            return_value = int(return_value) / 1000
        else:
            GlobalModule.EM_LOGGER.debug("read_sys_common_conf NG")
            return_value = 600
        GlobalModule.EM_LOGGER.debug("disconnect wait %s", return_value)
        return return_value

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
    def _gen_json_name(self, json, xml, xml_ns):
        '''
            Obtain device name from xml message to be analyzed and
            set it for EC message storage dictionary object.
            Explanation about parameter:
                json:dictionary object for EC message storage
                xml:xml message to be analyzed
                xml_ns:Name space
                service:Service name
                order:Order name
        '''

        name_elm = self._find_xml_node(xml, xml_ns + "name")
        json["device"]["name"] = name_elm.text
