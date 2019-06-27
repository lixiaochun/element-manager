#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmOrderflowControl.py
'''
Order flow control module.
'''
import Queue
import threading
import datetime
import time
import uuid
import imp
import copy
import os
import traceback

import GlobalModule
from EmCommonLog import decorater_log
from EmCommonLog import decorater_log_in_out
import PluginLoader
from EmNetconfResponse import EmNetconfResponse


class EmOrderflowControl(threading.Thread):
    '''
    Order flow control class.
    '''

    timeout_flag = False  
    rpc_name = '{urn:ietf:params:xml:ns:netconf:base:1.0}'

    _target_scenario_module = None
    _target_scenario_class_ins = None

    _log_str_trans_status = {
        GlobalModule.TRA_STAT_PROC_ERR_ORDER:
        "Processing failure(Inadequate request)",
        GlobalModule.TRA_STAT_PROC_RUN: "processing",
        GlobalModule.TRA_STAT_EDIT_CONF: "Edit-config",
        GlobalModule.TRA_STAT_CONF_COMMIT: "Confirmed-commit",
        GlobalModule.TRA_STAT_COMMIT: "Commit",
        GlobalModule.TRA_STAT_PROC_END: "Finished successfully",
    }

    @decorater_log
    def __init__(self):
        '''
        Constructor
        Argument:
            None
        Explanation about return value:
            None           
        '''
        self._load_message_plugins()

        self.stop_event = threading.Event()

        super(EmOrderflowControl, self).__init__()
        self.daemon = True
        self.que_event = Queue.Queue(10)
        self.start()

        self._wait_for_remaining_order_completion()

        init_order_mgmtinfo_result =\
            GlobalModule.EMSYSCOMUTILDB.initialize_order_mgmt_info()

        if not init_order_mgmtinfo_result:
            raise IOError('Failed deleteing order control information.')

    @decorater_log_in_out
    def run(self):
        '''
        Launched as default after Thread is launched by Thread object.
        Method foe override.
        '''

        while not self.stop_event.is_set():
            self._run_main()

    def _run_main(self):
        '''
        Loop processing for run method
        '''
        try:
            que_item = self.que_event.get(block=True, timeout=0.01)

            ec_message = que_item[0]
            session_id = que_item[1]

            self._order_main(ec_message, session_id)

            self.que_event.task_done()
        except Queue.Empty:
            pass
        except (StopIteration, IOError, StandardError) as exc_info:
            GlobalModule.EM_LOGGER.debug("ERROR:", exc_info.message)
            self.que_event.task_done()

    @decorater_log_in_out
    def execute(self, ec_message, session_id):
        '''
        Receives request from Netconf server, executes transaction to process message.
        Explanation about parameter:
            ec_message:EC message
            session_id:Session ID
        Explanation about return value:
            None
        '''
        try:
            self.que_event.put((ec_message, session_id), block=False)
        except Queue.Full:
            GlobalModule.EM_LOGGER.debug("que_event is full")
            order_result = GlobalModule.ORDER_RES_PROC_ERR_TEMP
            self._send_response(order_result=order_result,
                                ec_message=ec_message,
                                session_id=session_id)

    @staticmethod
    @decorater_log_in_out
    def get_transaction_presence():
        '''
        Obtain presence of transaction in progress
        Explanation about parameter:
            None
        Explanation about return value:
            Availability of transaction information:boolean
        '''
        read_tras_list_result, transaction_id_list = \
            GlobalModule.EMSYSCOMUTILDB.read_transactionid_list()

        if not read_tras_list_result:
            raise IOError('Failed getting Transaction ID list.')
        else:
            return False if transaction_id_list is not None else True

    @decorater_log_in_out
    def stop(self):
        '''
        Stop thread.
        Explanation about parameter:
            None
        Explanation about return value:
            None
        '''
        self.stop_event.set()
        self.join()

    @decorater_log_in_out
    def _order_main(self, ec_message, session_id):
        '''
        Wait for request from Netconf server, conduct order control after receiving request.
        Explanation about parameter:
            ec_message:EC message
            session_id:Session ID
        Explanation about return value:
            None           
        
        '''
        transaction_id = self._issue_transaction_id()

        order_contents = self._get_order_contents(ec_message)

        order_info = (
            self._analysis_order_info(transaction_id=transaction_id,
                                      ec_message=ec_message,
                                      session_id=session_id,
                                      order_contents=order_contents)
        )
        service_kind = order_info[0]
        order_kind = order_info[1]
        device_num = order_info[2]
        scenario_name = order_info[3]
        order_timer = order_info[4]

        transaction_status = GlobalModule.TRA_STAT_PROC_RUN
        self._replace_transaction_status(
            transaction_id,
            transaction_status,
            service_kind,
            order_kind,
            order_contents,
            ec_message=ec_message,
            session_id=session_id,
            scenario_name=scenario_name
        )

        order_timer_set = order_timer / 1000

        timer = threading.Timer(order_timer_set, self._find_timeout)
        timer.start()

        GlobalModule.EM_LOGGER.debug('Timer of waiting order start.')

        self._load_scenario_module(scenario_name)

        self._start_scenario(transaction_id=transaction_id,
                             ec_message=ec_message,
                             session_id=session_id,
                             scenario_name=scenario_name,
                             timer=timer,
                             service_kind=service_kind,
                             order_kind=order_kind,
                             order_contents=order_contents)

        GlobalModule.EM_LOGGER.debug('Monitoring(processing)')
        self._monitoring(transaction_id=transaction_id,
                         ec_message=ec_message,
                         session_id=session_id,
                         scenario_name=scenario_name,
                         timer=timer,
                         service_kind=service_kind,
                         order_kind=order_kind,
                         order_contents=order_contents,
                         transaction_status=transaction_status,
                         device_num=device_num)

        transaction_status = GlobalModule.TRA_STAT_EDIT_CONF
        self._replace_transaction_status(
            transaction_id,
            transaction_status,
            service_kind,
            order_kind,
            order_contents,
            before_status=GlobalModule.TRA_STAT_PROC_RUN,
            timer=timer,
            ec_message=ec_message,
            session_id=session_id,
            scenario_name=scenario_name
        )

        self._target_scenario_class_ins.notify(ec_message,
                                               transaction_id,
                                               order_kind)

        GlobalModule.EM_LOGGER.debug('Monitoring(Edit-config)')
        self._monitoring(transaction_id=transaction_id,
                         ec_message=ec_message,
                         session_id=session_id,
                         scenario_name=scenario_name,
                         timer=timer,
                         service_kind=service_kind,
                         order_kind=order_kind,
                         order_contents=order_contents,
                         transaction_status=transaction_status,
                         device_num=device_num)

        transaction_status = GlobalModule.TRA_STAT_CONF_COMMIT
        self._replace_transaction_status(
            transaction_id,
            transaction_status,
            service_kind,
            order_kind,
            order_contents,
            before_status=GlobalModule.TRA_STAT_EDIT_CONF,
            timer=timer,
            ec_message=ec_message,
            session_id=session_id,
            scenario_name=scenario_name
        )

        GlobalModule.EM_LOGGER.debug('Monitoring(Confirmed-commit)')
        self._monitoring(transaction_id=transaction_id,
                         ec_message=ec_message,
                         session_id=session_id,
                         scenario_name=scenario_name,
                         timer=timer,
                         service_kind=service_kind,
                         order_kind=order_kind,
                         order_contents=order_contents,
                         transaction_status=transaction_status,
                         device_num=device_num)

        transaction_status = GlobalModule.TRA_STAT_COMMIT
        self._replace_transaction_status(
            transaction_id,
            transaction_status,
            service_kind,
            order_kind,
            order_contents,
            before_status=GlobalModule.TRA_STAT_CONF_COMMIT,
            timer=timer,
            ec_message=ec_message,
            session_id=session_id,
            scenario_name=scenario_name
        )

        self._target_scenario_class_ins.notify(ec_message,
                                               transaction_id,
                                               order_kind)

        GlobalModule.EM_LOGGER.debug('Monitoring(Commit)')
        self._monitoring(transaction_id=transaction_id,
                         ec_message=ec_message,
                         session_id=session_id,
                         scenario_name=scenario_name,
                         timer=timer,
                         service_kind=service_kind,
                         order_kind=order_kind,
                         order_contents=order_contents,
                         transaction_status=transaction_status,
                         device_num=device_num)

        transaction_status = GlobalModule.TRA_STAT_PROC_END
        self._replace_transaction_status(
            transaction_id,
            transaction_status,
            service_kind,
            order_kind,
            order_contents,
            before_status=GlobalModule.TRA_STAT_COMMIT,
            timer=timer,
            ec_message=ec_message,
            session_id=session_id,
            scenario_name=scenario_name
        )

        self._target_scenario_class_ins.notify(ec_message,
                                               transaction_id,
                                               order_kind)

        order_result = GlobalModule.ORDER_RES_OK
        self._processing_on_order_ok(
            transaction_id=transaction_id,
            order_result=order_result,
            ec_message=ec_message,
            session_id=session_id,
            scenario_name=scenario_name,
            timer=timer,
            service_kind=service_kind,
            order_kind=order_kind,
            order_contents=order_contents,
        )

    @decorater_log
    def _load_scenario_module(self, scenario_name):
        '''
        Search all files  in  scenario deirectory if the scenario file exists, 
        import and  instantiate the senario files.

        Explanation about parameter:
            scenario_name:scenario  name (str)
        Explanation about return value:
            None
        '''
        scenario_name_em = 'Em' + scenario_name
        GlobalModule.EM_LOGGER.debug('Generate start class name.:%s',
                                     scenario_name_em)

        lib_path = GlobalModule.EM_LIB_PATH
        GlobalModule.EM_LOGGER.debug('enviroment value path:%s', lib_path)

        mod_dir = self._search_file("{0}.py".format(scenario_name_em),
                                    os.path.join(lib_path, 'Scenario'))
        GlobalModule.EM_LOGGER.debug('Search dir = %s', mod_dir)
        filepath, filename, data = imp.find_module(scenario_name_em, [mod_dir])
        GlobalModule.EM_LOGGER.debug('Search module.')

        self._target_scenario_module = (
            imp.load_module(scenario_name_em, filepath, filename, data))
        GlobalModule.EM_LOGGER.debug('Read module.')

        self._target_scenario_class_ins = (
            getattr(self._target_scenario_module, scenario_name_em)())
        GlobalModule.EM_LOGGER.debug('Create instance.')

    @staticmethod
    @decorater_log
    def _search_file(file_name, root_dir):
        '''
        Search all files in  scenario deirectory if the scenario file exists, 
        return the directory path.
        Explanation about parameter:
            file_name:File name (str)
            root_dir:Directory path (str)
        Explanation about return value:
            Directory path of module file (str)
        '''
        for root, dirs, files in os.walk(root_dir):
            GlobalModule.EM_LOGGER.debug(
                "Search:root={0},dirs={1},files={2}".format(root, dirs, files))
            for file_data in files:
                if file_data == file_name:
                    return root
        return None

    @decorater_log
    def _start_scenario(self,
                        transaction_id=None,
                        ec_message=None,
                        session_id=None,
                        scenario_name=None,
                        timer=None,
                        service_kind=None,
                        order_kind=None,
                        order_contents=None):
        '''
        Start scenarion.
        Explanation about parameter:
            transaction_id:transaction ID
            ec_message:EC message
            session_id:Session ID
            scenario_name:Scenario Name
            timer:Timer thread
            service_kind:Service type
            order_kind:Order type
            order_contents:order contents
        Explanation about return value:
            None
        '''
        order_kind_sc = None if order_kind == "get" else order_kind
        scenario_start_result = (
            self._target_scenario_class_ins.execute(ec_message,
                                                    transaction_id,
                                                    order_kind_sc)
        )
        if not scenario_start_result:
            order_result = GlobalModule.ORDER_RES_PROC_ERR_OTH
            self._processing_on_order_failure(
                transaction_id=transaction_id,
                order_result=order_result,
                ec_message=ec_message,
                session_id=session_id,
                scenario_name=scenario_name,
                timer=timer,
                service_kind=service_kind,
                order_kind=order_kind,
                order_contents=order_contents,
            )
            raise StandardError('Failed in starting scenario.')

    @decorater_log
    def _replace_transaction_status(self,
                                    transaction_id,
                                    transaction_status,
                                    service_kind,
                                    order_kind,
                                    order_contents,
                                    before_status=None,
                                    timer=None,
                                    ec_message=None,
                                    session_id=None,
                                    scenario_name=None):
        '''
        Initiate transaction status write process in  system common utility
        (order management information) and write value.
        Explanation about parameter:
            transaction_id:transaction ID
            transaction_status:transaction status
            service_kind:service type
            order_kind:order type
            order_contents:order contents
            before_status:transaction status (before replaced)
            timer:Timer thread
            ec_message:EC message
            session_id:Session ID
            scenario_name:Scenario Name
        Explanation about return value:
            writing result of trasanction status: True or False
        '''
        db_control = 'UPDATE'
        old_str = self._log_str_trans_status.get(before_status,
                                                 "init state")
        new_str = self._log_str_trans_status.get(transaction_status,
                                                 "init state")
        log_txt = "Transaction status update({0}=>{1})".format(old_str,
                                                               new_str)
        GlobalModule.EM_LOGGER.debug(log_txt)
        write_tra_stat_result = (
            GlobalModule.EMSYSCOMUTILDB.write_transaction_status(
                db_control,
                transaction_id,
                transaction_status,
                service_kind,
                order_kind,
                order_contents))
        if not write_tra_stat_result:
            if timer:
                timer.cancel()
            order_result = GlobalModule.ORDER_RES_PROC_ERR_OTH
            self._send_response(transaction_id,
                                order_result,
                                ec_message,
                                session_id,
                                scenario_name=scenario_name)
            log_svs = self._txt_log_service(scenario_name)
            GlobalModule.EM_LOGGER.info('103004 Service:%s Error', log_svs)
            raise IOError('Transaction status writring is failed.')

        return write_tra_stat_result

    @decorater_log
    def _analysis_order_info(self,
                             transaction_id=None,
                             ec_message=None,
                             session_id=None,
                             order_contents=None):
        '''
        Analyze order information(EC message) and obtain service type, etc.
        Explanation about parameter:
            transaction_id:transaction ID
            ec_message:EC message
            session_id:Session ID
            order_contents:order contents
        Explanation about return value:
            None
        '''

        try:
            service_kind, order_kind, device_num = (
                self._analysis_em_scenario(ec_message)
            )
        except ValueError:
            order_result = GlobalModule.ORDER_RES_PROC_ERR_ORDER
            self._send_response(transaction_id,
                                order_result,
                                ec_message,
                                session_id)
            GlobalModule.EM_LOGGER.debug('Order Analysis Error')
            raise StopIteration('Service type, Order type, ' +
                                'Analysis of device number is failed.')

        scenario_select_result, scenario_name, order_timer = (
            self._select_em_scenario(service_kind, order_kind)
        )
        GlobalModule.EM_LOGGER.debug(
            'Scenario name:%s Timer of waiting order:%s',
            scenario_name, order_timer)

        if (not scenario_select_result or
                scenario_name == '' or order_timer == ''):
            GlobalModule.EM_LOGGER.warning('203005 No Applicable Service')

            transaction_status = GlobalModule.TRA_STAT_PROC_ERR_ORDER
            self._replace_transaction_status(
                transaction_id,
                transaction_status,
                service_kind,
                order_kind,
                order_contents,
                ec_message=ec_message,
                session_id=session_id,
                scenario_name=scenario_name)

            order_result = GlobalModule.ORDER_RES_PROC_ERR_ORDER
            self._processing_on_order_failure(
                transaction_id=transaction_id,
                order_result=order_result,
                ec_message=ec_message,
                session_id=session_id,
                scenario_name=scenario_name,
                timer=None,
                service_kind=service_kind,
                order_kind=order_kind,
                order_contents=order_contents,
            )
            raise StandardError('Failed in Scenario select.')
        else:
            GlobalModule.EM_LOGGER.info(
                '103001 Service:%s start', scenario_name)
        return service_kind, order_kind, device_num, scenario_name, order_timer

    @decorater_log
    def _analysis_em_scenario(self, ec_message):
        '''
        Analyze eceived Netconf message and obtain scenarion information.
        
        Explanation about parameter:
            ec_message:EC message byte
        Explanation about return value:
            service type:str
            order type:order_kind
            number of devices:str
        '''
        get_plugin = None
        try:
            for plugin in self.plugin_analysis_message:
                if plugin.check_used_plugin(ec_message, self.rpc_name):
                    get_plugin = plugin.get_plugin_ins()
                    break
            if not get_plugin:
                GlobalModule.EM_LOGGER.debug(
                    "Failed to get plugin / ec_message:%s, plugins:%s",
                    ec_message, self.plugin_analysis_message)
                raise Exception("Failed to get plugin")
            get_plugin.rpc_name = self.rpc_name
            service_kind, order_kind, device_num, device_type = (
                get_plugin.analysis_scenario_from_recv_message(ec_message))
        except Exception:
            GlobalModule.EM_LOGGER.error(
                "303010 Error Execute Plugin for Analysis Message")
            GlobalModule.EM_LOGGER.debug(
                "Traceback:%s", traceback.format_exc())
            raise
        GlobalModule.EM_LOGGER.debug(
            'analysis result Service:%s Order:%s Device_Num:%s Device_type:%s',
            service_kind, order_kind, device_num, device_type)
        return service_kind, order_kind, device_num

    @staticmethod
    @decorater_log
    def _select_em_scenario(service_kind, order_kind):
        '''
        Obtain scenario name, timer value from config based on Service type and Order type as the key information.
        Explanation about parameter:
            service_kind:Service type
            order_kind:Order type
        Explanation about return value:
            Result of reading scenario definition : True or False
            Scenario name:str
            Order timer value:int
        '''

        result, _ = GlobalModule.EM_CONFIG.read_service_conf(service_kind)
        if not result:
            return False, None, None

        scenario_result, scenario_name, order_timer =\
            GlobalModule.EM_CONFIG.read_scenario_conf(service_kind, order_kind)

        return scenario_result, scenario_name, order_timer

    @decorater_log
    def _monitoring(self,
                    transaction_id=None,
                    ec_message=None,
                    session_id=None,
                    scenario_name=None,
                    timer=None,
                    service_kind=None,
                    order_kind=None,
                    order_contents=None,
                    transaction_status=None,
                    device_num=None):
        '''
        Monitor transaction.
        Explanation about parameter:
            transaction_id:transaction ID
            ec_message:EC message
            session_id:Session ID
            scenario_name:Scenario Name
            timer:Timer thread
            service_kind:Service type
            order_kind:Order type
            order_contents:order contents
            transaction_status:transaction status
            device_num:Number of devices
        Explanation about return value:
            None
        '''
        is_ok, order_result = self._monitor_transaction(transaction_id,
                                                        transaction_status,
                                                        device_num)
        if not is_ok:
            self._processing_on_order_failure(
                transaction_id=transaction_id,
                order_result=order_result,
                ec_message=ec_message,
                session_id=session_id,
                scenario_name=scenario_name,
                timer=timer,
                service_kind=service_kind,
                order_kind=order_kind,
                order_contents=order_contents,
            )
            GlobalModule.EM_LOGGER.warning('203006 Order Service Error')
            raise StandardError('Failed in transaction monitoring.')

    @decorater_log
    def _monitor_transaction(self, transaction_id, tra_mng_stat, device_num):
        '''
        Monitor order management information DB regularly, notify the sync instruction to individual processing of each scenario.
        Explanation about parameter:
            transaction_id:Transaction ID
            tra_mng_stat:Transaction status
            device_num:　Number of devices
        Explanation about return value:
            Method result : True or False
            Order result : int           
        '''

        retry_flg = True

        monitor_time = self._get_timer_config('Timer_transaction_db_watch',
                                              100)
        GlobalModule.EM_LOGGER.debug('Transaction DB Watch Timer = %s',
                                     monitor_time)

        retry_timer = float(monitor_time) / 1000

        while retry_flg:
            result = self._monitor_device_status(transaction_id,
                                                 tra_mng_stat,
                                                 device_num,
                                                 retry_timer)
            retry_flg = result[0]
            is_monitor_result = result[1]
            order_result = result[2]
        return is_monitor_result, order_result

    @decorater_log
    def _monitor_device_status(self,
                               transaction_id=None,
                               tra_mng_stat=None,
                               device_num=None,
                               retry_timer=None):
        '''
        Monitor order management information DB periodically and notify each scenario ndividual process
        of synchronization request.
        (loop process in monitor_transaction method)
        
        Explanation about parameter:
            transaction_id:transaction ID
            tra_mng_stat:transaction status
            device_num:number of devices
        Explanation about return value:
            loop continuation flag: True or False (True if loop continues)
            method result : True or False
            order result : int (if loop continues, None)
        '''
        is_retry = False
        roll_cnt = 0
        error_cnt = 0
        if EmOrderflowControl.timeout_flag:
            EmOrderflowControl.timeout_flag = False
            GlobalModule.EM_LOGGER.debug('Monitor Timeout')
            order_result = GlobalModule.ORDER_RES_PROC_ERR_OTH
            return False, False, order_result

        read_mtd = (
            GlobalModule.EMSYSCOMUTILDB.read_transaction_device_status_list)
        is_ok, dev_con_list = read_mtd(transaction_id)

        if not is_ok:
            GlobalModule.EM_LOGGER.debug(
                'Read DeviceStatusMgmtInfo Error')
            order_result = GlobalModule.ORDER_RES_PROC_ERR_OTH
            return False, False, order_result

        dev_num = len(dev_con_list) if dev_con_list is not None else -1

        if dev_con_list is None:
            GlobalModule.EM_LOGGER.debug('Device List None')
            is_retry = True
        elif dev_num != device_num:
            GlobalModule.EM_LOGGER.debug('Device Num Unmatch')
            is_retry = True
        else:
            for dev_mng in dev_con_list:
                dev_mng_tra_stat = dev_mng['transaction_status']
                if dev_mng_tra_stat < GlobalModule.TRA_STAT_ROLL_BACK:
                    if dev_mng_tra_stat <= tra_mng_stat:
                        is_retry = True
                else:
                    roll_cnt, error_cnt = (
                        self._count_roleback_error_status(dev_con_list)
                    )
                    if ((dev_mng_tra_stat in (
                            GlobalModule.TRA_STAT_ROLL_BACK_END,
                            GlobalModule.TRA_STAT_PROC_ERR_STOP_RETRY,
                            GlobalModule.TRA_STAT_PROC_ERR_STOP_NO_RETRY,)
                         ) and roll_cnt == dev_num):
                        anaiy_order = (
                            self._analysis_order_manage(dev_mng_tra_stat))
                        order_result = anaiy_order
                        GlobalModule.EM_LOGGER.debug('RollBack')
                        return False, False, order_result
                    elif ((dev_mng_tra_stat >
                            GlobalModule.TRA_STAT_ROLL_BACK_END)
                            and ((roll_cnt + error_cnt) == dev_num)):
                        anaiy_order = (
                            self._analysis_order_manage(dev_mng_tra_stat))
                        order_result = anaiy_order
                        GlobalModule.EM_LOGGER.debug('Other RollBack or Error')
                        return False,  False, order_result
                    else:
                        is_retry = True
        if not is_retry:
            GlobalModule.EM_LOGGER.debug('Monitor NoRetry')
            order_result = GlobalModule.ORDER_RES_OK
        else:
            GlobalModule.EM_LOGGER.debug('Monitor Retry')
            order_result = None
            time.sleep(retry_timer)
        return is_retry, True, order_result

    @staticmethod
    @decorater_log
    def _count_roleback_error_status(dev_con_list=[]):
        '''
        Count number of rollback completions and occurred erros
        '''
        roll_cnt = 0
        error_cnt = 0
        for dev_mng_roll in dev_con_list:
            dev_mng_roll_tra_stat = dev_mng_roll['transaction_status']
            if dev_mng_roll_tra_stat in (
                    GlobalModule.TRA_STAT_ROLL_BACK_END,
                    GlobalModule.TRA_STAT_PROC_END,
                    GlobalModule.TRA_STAT_PROC_ERR_STOP_RETRY,
                    GlobalModule.TRA_STAT_PROC_ERR_STOP_NO_RETRY,):
                roll_cnt += 1
            elif dev_mng_roll_tra_stat > GlobalModule.TRA_STAT_ROLL_BACK_END:
                error_cnt += 1
        return roll_cnt, error_cnt

    @staticmethod
    @decorater_log
    def _analysis_order_manage(dev_mng_tra_stat):
        '''
        Analyze order management information.
            Explanation about parameter:
            dev_mng_tra_stat: transaction status

            result:int
                1:Finished successfully
                2:Rollback completed
                3:Processing has failed.(Validation check NG)
                4:Processing has failed.(Inadequate request)
                5:Processing has failed.(Matching NG)
                6:Processing has failed.(Stored information None)
                7:Processing has failed.(Temporary)
                8:Processing has failed.(Other)
                9:Processing has failed.(Config could be obtained before operation)
               10:Processing has failed.(Device setting error)
               11:Processing has failed.(Config could be obtained after operation)
        '''

        anaiy_order = GlobalModule.ORDER_RES_OK

        if dev_mng_tra_stat == GlobalModule.TRA_STAT_ROLL_BACK_END:
            anaiy_order = GlobalModule.ORDER_RES_ROLL_BACK_END

        elif dev_mng_tra_stat == GlobalModule.TRA_STAT_PROC_ERR_CHECK:
            anaiy_order = GlobalModule.ORDER_RES_PROC_ERR_SET_DEV

        elif dev_mng_tra_stat == GlobalModule.TRA_STAT_PROC_ERR_ORDER:
            anaiy_order = GlobalModule.ORDER_RES_PROC_ERR_ORDER

        elif dev_mng_tra_stat == GlobalModule.TRA_STAT_PROC_ERR_MATCH:
            anaiy_order = GlobalModule.ORDER_RES_PROC_ERR_MATCH

        elif dev_mng_tra_stat == GlobalModule.TRA_STAT_PROC_ERR_INF:
            anaiy_order = GlobalModule.ORDER_RES_PROC_ERR_INF

        elif dev_mng_tra_stat == GlobalModule.TRA_STAT_PROC_ERR_TEMP:
            anaiy_order = GlobalModule.ORDER_RES_PROC_ERR_TEMP

        elif dev_mng_tra_stat == GlobalModule.TRA_STAT_PROC_ERR_OTH:
            anaiy_order = GlobalModule.ORDER_RES_PROC_ERR_OTH

        elif dev_mng_tra_stat == GlobalModule.TRA_STAT_PROC_ERR_GET_BEF_CONF:
            anaiy_order = GlobalModule.ORDER_RES_PROC_ERR_GET_BEF_CONF

        elif dev_mng_tra_stat == GlobalModule.TRA_STAT_PROC_ERR_SET_DEV:
            anaiy_order = GlobalModule.ORDER_RES_PROC_ERR_SET_DEV

        elif dev_mng_tra_stat == GlobalModule.TRA_STAT_PROC_ERR_GET_AFT_CONF:
            anaiy_order = GlobalModule.ORDER_RES_PROC_ERR_GET_AFT_CONF

        return anaiy_order

    @staticmethod
    @decorater_log
    def _find_timeout():
        '''
        Response NG to Netconf server whem waiting timer for order completion has been timed out. 
        Explanation about parameter:
           None
        Explanation about return value:
           None
        '''

        GlobalModule.EM_LOGGER.debug('Timeout detection')

        EmOrderflowControl.timeout_flag = True

    @decorater_log
    def _processing_on_order_ok(self,
                                transaction_id=None,
                                order_result=GlobalModule.ORDER_RES_OK,
                                ec_message=None,
                                session_id=None,
                                scenario_name=None,
                                timer=None,
                                service_kind=None,
                                order_kind=None,
                                order_contents=None,
                                ):
        '''
        Process when the order failed.
        Explanation about parameter:
            transaction_id : transaction ID (uuid)
            order_result : order result (int)
            ec_message : EC message (byte)
            session_id : session ID (uuid)
            scenario_name : sceario name(for log output) (str)
            timer : Timer object
            service_kind : service type (str)
            order_kind : order type (str)
            order_contents : order contents (str)
        Explanation about return value:
            None
        '''
        self._processing_at_end_of_order(
            transaction_id=transaction_id,
            order_result=order_result,
            ec_message=ec_message,
            session_id=session_id,
            scenario_name=scenario_name,
            timer=timer,
            service_kind=service_kind,
            order_kind=order_kind,
            order_contents=order_contents,
        )
        tmp = self._txt_log_service(scenario_name)
        GlobalModule.EM_LOGGER.info('103003 Service:%s end', tmp)

    @decorater_log
    def _processing_on_order_failure(self,
                                     transaction_id=None,
                                     order_result=None,
                                     ec_message=None,
                                     session_id=None,
                                     scenario_name=None,
                                     timer=None,
                                     service_kind=None,
                                     order_kind=None,
                                     order_contents=None,
                                     ):
        '''
        Process when the order failed.
        Explanation about parameter:
            transaction_id : transaction ID (uuid)
            order_result : order result (int)
            ec_message : EC message (byte)
            session_id : session ID (uuid)
            scenario_name : sceario name(for log output) (str)
            timer : Timer object
            service_kind : service type (str)
            order_kind : order type (str)
            order_contents : order contents (str)
        Explanation about return value:
            None
        '''
        self._processing_at_end_of_order(
            transaction_id=transaction_id,
            order_result=order_result,
            ec_message=ec_message,
            session_id=session_id,
            scenario_name=scenario_name,
            timer=timer,
            service_kind=service_kind,
            order_kind=order_kind,
            order_contents=order_contents,
        )
        tmp = self._txt_log_service(scenario_name)
        GlobalModule.EM_LOGGER.info('103004 Service:%s Error', tmp)

    @decorater_log
    def _processing_at_end_of_order(self,
                                    transaction_id=None,
                                    order_result=None,
                                    ec_message=None,
                                    session_id=None,
                                    scenario_name=None,
                                    timer=None,
                                    service_kind=None,
                                    order_kind=None,
                                    order_contents=None,
                                    ):
        '''
        Terminate Order.
        Explanation about parameter:
            transaction_id : transaction ID (uuid)
            order_result : order result (int)
            ec_message : EC message (byte)
            session_id : session ID (uuid)
            scenario_name : sceario name(for log output) (str)
            timer : Timer object
            service_kind : service type (str)
            order_kind : order type (str)
            order_contents : order contents (str)
        Explanation about return value:
            None
        '''
        if timer:
            timer.cancel()
        self._send_response(transaction_id,
                            order_result,
                            ec_message,
                            session_id,
                            scenario_name=scenario_name)
        GlobalModule.EMSYSCOMUTILDB.write_device_status_list(
            transaction_id)
        GlobalModule.EMSYSCOMUTILDB.write_transaction_status(
            db_contolorer='DELETE',
            transaction_id=transaction_id,
            transaction_status=0,
            service_type=service_kind,
            order_type=order_kind,
            order_text=order_contents)

    @decorater_log
    def _send_response(self,
                       transaction_id=None,
                       order_result=None,
                       ec_message=None,
                       session_id=None,
                       scenario_name=None):
        '''
        Send response.
        Explanation about parameter:
            transaction_id : transaction ID (uuid)
            order_result : order result (int)
            ec_message : EC message (byte)
            session_id : session ID (uuid)
            scenario_name : scenario name(for log output) (str)
        Explanation about return value:
            None
        '''
        response_info = EmNetconfResponse(order_result=order_result,
                                          ec_message=ec_message,
                                          session_id=session_id)
        sys_db = GlobalModule.EMSYSCOMUTILDB
        is_ok, dev_con_list = (
            sys_db.read_transaction_device_status_list(transaction_id))
        for dev_info in (dev_con_list if (is_ok and dev_con_list) else ()):
            device_name = dev_info["device_name"]
            device_status = dev_info["transaction_status"]
            response_info.store_device_scenario_results(
                device_name=device_name,
                transaction_result=device_status)
        GlobalModule.NETCONFSSH.send_response(order_result,
                                              ec_message,
                                              session_id,
                                              response_info=response_info)
        scenario_name = self._txt_log_service(scenario_name)
        log_txt = "103002 Service:{0} result:{1}".format(scenario_name,
                                                         order_result)
        GlobalModule.EM_LOGGER.info(log_txt)

    @staticmethod
    @decorater_log
    def _txt_log_service(scenario_name):
        '''
        Create string included in Service:XX  in Info log.
        Explanation about parameter:
            scenario_name : scenario name(for log output) (str)
        Explanation about return value:
            output string (str)
        '''
        no_svs_txt = "no scenario (before scenario load)"
        return scenario_name if scenario_name else no_svs_txt

    @staticmethod
    @decorater_log
    def _issue_transaction_id():
        '''
        Issue transaction ID.
        Explanation about return value:
            transaction ID : uuid
        '''
        return uuid.uuid4()

    @staticmethod
    @decorater_log
    def _get_now_date():
        '''
        Obtain current time.
        Explanation about return value:
            Current time : datetime
        '''
        return datetime.datetime.now()

    @decorater_log
    def _get_order_contents(self, ec_message=None):
        '''
        Create time stamp and  order contents.
        Explanation about parameter:
            ec_message:EC mesage (byte)
        Explanation about return value:
            order contents : str
        '''
        current_time = self._get_now_date()
        current_time_str = datetime.datetime.strftime(current_time,
                                                      '%Y-%m-%d %H:%M:%S.%f')
        ec_message_str = copy.deepcopy(ec_message)
        ec_message_str = ec_message_str.read()
        return "{0} {1}".format(current_time_str, ec_message_str)

    @decorater_log
    def _load_message_plugins(self):
        '''
        Load Plugin.
        Explanation about parameter:
                        None
        Explanation about return value:
            None
        '''
        GlobalModule.EM_LOGGER.info(
            '103008 Start Loading Plugin for Analysis Message')
        plugin_dir_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "OfcPluginMessage")
        try:
            plugins = PluginLoader.load_plugins(plugin_dir_path, "OfcPlugin")
        except Exception:
            GlobalModule.EM_LOGGER.error(
                '303009 Error Loading Plugin for Analysis Message')
            raise
        GlobalModule.EM_LOGGER.debug('load plugins = %s', plugins)

        def key_weight(mod):
            return mod.plugin_weight

        self.plugin_analysis_message = sorted(plugins,
                                              key=key_weight,
                                              reverse=True)
        GlobalModule.EM_LOGGER.debug('plugin list = %s',
                                     self.plugin_analysis_message)

    @decorater_log
    def _get_timedate_of_order(self, transaction_id):
        '''
        Obtain time(time stamp) related to order.
        Explanation about parameter:
            transaction_id : transaction ID (uuid)
        Explanation about return value:
            detected time stamp ; datetime
        '''
        return_value = None
        read_method = (
            GlobalModule.EMSYSCOMUTILDB.read_transaction_device_status_list)
        is_ok, dev_con_list = read_method(transaction_id)
        if not is_ok:
            raise IOError('Failed getting device status.')
        if dev_con_list:
            read_method = GlobalModule.EMSYSCOMUTILDB.read_transaction_info
            is_ok, tra_table_inf = read_method(transaction_id)
            if not is_ok:
                raise IOError('Failed getting table information.')
            if tra_table_inf:
                order_reg_time_str = tra_table_inf[0]['order_text'][0:26]
                return_value = (
                    datetime.datetime.strptime(order_reg_time_str,
                                               '%Y-%m-%d %H:%M:%S.%f'))
        return return_value

    @decorater_log
    def _get_order_regist_time(self, transaction_id_list):
        '''
        Obtain time stamps of which  number is the same as that of transaction list
        and obtain maiximum value of time stamps.
        Explanation about parameter:
            transaction_id_list : list of transaction IDs (list)
        Explanation about return value:
            maximum value of each transaction time stamp: datetime
        '''
        order_reg_time_int = (
            datetime.datetime(2001, 01, 01, 01, 01, 01, 000001))
        order_reg_time_flg = False
        for transaction_id in transaction_id_list:
            tmp_time = self._get_timedate_of_order(transaction_id)
            if tmp_time and (tmp_time > order_reg_time_int):
                order_reg_time_int = tmp_time
                order_reg_time_flg = True
        return_val = order_reg_time_int if order_reg_time_flg else None
        return return_val

    @decorater_log
    def _wait_for_remaining_order_completion(self):
        '''
        Wait for the order that has not been completed.
        Explanation about parameter:
            None
        Explanation about return value:
            None
        '''
        read_tras_list_result, transaction_id_list = (
            GlobalModule.EMSYSCOMUTILDB.read_transactionid_list())
        if not read_tras_list_result:
            raise IOError('Failed getting Transaction ID list.')

        if not transaction_id_list:
            return

        conf_timeout_value = self._get_wait_time_for_order()

        order_reg_time_int = self._get_order_regist_time(transaction_id_list)

        if not order_reg_time_int:
            sleee_time = conf_timeout_value / 1000
            GlobalModule.EM_LOGGER.debug('wait %s seconds', sleee_time)
            time.sleep(sleee_time)
        else:
            current_time = self._get_now_date()

            diff_time = (
                (current_time - order_reg_time_int).total_seconds() * 1000)

            if 0 < diff_time < conf_timeout_value:
                sleee_time = (conf_timeout_value - diff_time) / 1000
                GlobalModule.EM_LOGGER.debug('wait %s seconds', sleee_time)
                time.sleep(sleee_time)
            else:
                GlobalModule.EM_LOGGER.debug('no wait')

    @decorater_log
    def _get_wait_time_for_order(self):
        '''
        Decide waiting time(timer value) for remaining transaction at initialization phase.
        Explanation about parameter:
            None
        Explanation about return value:
            waiting time : int
        '''

        conf_timeout = (
            self._get_timer_config('Timer_confirmed-commit'))
        conn_timeout = (
            self._get_timer_config('Timer_connect_get_before_config'))
        disconn_timeout = (
            self._get_timer_config('Timer_disconnect_get_after_config'))

        wait_time = (int(conf_timeout) +
                     int(conn_timeout) +
                     int(disconn_timeout))
        GlobalModule.EM_LOGGER.debug('wait time = %s', wait_time)
        return wait_time

    @staticmethod
    @decorater_log
    def _get_timer_config(conf_key, default_value=None):
        '''
        Obtain specified timer value from config management part.
        Explanation about parameter:
            conf_key : config key name (str) 
        Explanation about return value:
            timer value(int)
        '''
        sys_com_result, conf_timeout_value = (
            GlobalModule.EM_CONFIG.read_sys_common_conf(conf_key))
        if ((not sys_com_result or conf_timeout_value is None)
                and default_value is not None):
            conf_timeout_value = default_value
        elif not sys_com_result:
            raise IOError('Failed reading system common define.')
        elif conf_timeout_value is None:
            raise IOError('timer value is None ("%s")', conf_key)
        return conf_timeout_value
