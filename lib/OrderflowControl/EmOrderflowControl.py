#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2018 Nippon Telegraph and Telephone Corporation
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
import re

from lxml import etree

import GlobalModule
from EmCommonLog import decorater_log
from EmCommonLog import decorater_log_in_out
from EmSeparateScenario import EmScenario


class EmOrderflowControl(threading.Thread):
    '''
    Order flow control class.

    '''

    timeout_flag = False
    rpc_name = '{urn:ietf:params:xml:ns:netconf:base:1.0}'

    __target_scenario_module = None
    __target_scenario_class_ins = None

    @decorater_log
    def __init__(self):
        '''
        Constructor
        Argument:
            None
        Explanation about return value:
            None
        '''
        order_reg_time_int =\
            datetime.datetime(2001, 01, 01, 01, 01, 01, 000001)
        order_reg_time_flg = 0

        self.stop_event = threading.Event()

        super(EmOrderflowControl, self).__init__()
        self.daemon = True
        self.que_event = Queue.Queue(10)
        self.start()

        read_tras_list_result, transaction_id_list = \
            GlobalModule.EMSYSCOMUTILDB.read_transactionid_list()

        if read_tras_list_result is False:
            raise IOError('Failed getting Transaction ID list.')

        else:
            if transaction_id_list is not None:
                for transaction_id in transaction_id_list:
                    read_tra_dev_list_result, dev_con_list =\
                        GlobalModule.EMSYSCOMUTILDB.\
                        read_transaction_device_status_list(
                            transaction_id)

                    sys_com_result, conf_timeout_value = \
                        GlobalModule.EM_CONFIG.\
                        read_sys_common_conf('Timer_confirmed-commit')

                    if read_tra_dev_list_result is False:
                        raise IOError('Failed getting device status.')

                    elif sys_com_result is False:
                        raise IOError('Failed reading system common define.')

                    elif conf_timeout_value is None:
                        raise IOError('confirm-timeout timer value is None.')

                    else:
                        if dev_con_list is not None:
                            read_tra_inf_result, tra_table_inf = \
                                GlobalModule.EMSYSCOMUTILDB.\
                                read_transaction_info(transaction_id)

                            if read_tra_inf_result is False:
                                raise IOError(
                                    'Failed getting table information.')

                            elif tra_table_inf is None:
                                pass

                            else:
                                order_reg_time_str =\
                                    tra_table_inf[0]['order_text'][0:26]

                                order_reg_time_int_temp = \
                                    datetime.datetime.\
                                    strptime(order_reg_time_str,
                                             '%Y-%m-%d %H:%M:%S.%f')

                                if order_reg_time_int_temp >\
                                        order_reg_time_int:
                                    order_reg_time_int =\
                                        order_reg_time_int_temp

                                order_reg_time_flg += 1

                if order_reg_time_flg == 0:
                    time.sleep(conf_timeout_value / 1000)

                else:
                    current_time = datetime.datetime.now()

                    diff_time =\
                        (current_time - order_reg_time_int).\
                        total_seconds() * 1000

                    if 0 < diff_time < conf_timeout_value:
                        time.sleep((conf_timeout_value - diff_time) / 1000)

        init_order_mgmtinfo_result =\
            GlobalModule.EMSYSCOMUTILDB.initialize_order_mgmt_info()

        if init_order_mgmtinfo_result is False:
            raise IOError('Failed deleteing order control information.')

    @decorater_log_in_out
    def run(self):
        '''
        Launched as default after Thread is launched by Thread object.
        Method foe override.
        '''

        while not self.stop_event.is_set():
            try:
                que_item = self.que_event.get(block=True, timeout=0.01)

                ec_message = que_item[0]
                session_id = que_item[1]

                self._order_main(ec_message, session_id)

                self.que_event.task_done()
            except Queue.Empty:
                pass
            except (StopIteration, IOError, StandardError):
                self.que_event.task_done()

    @decorater_log
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
            order_result = GlobalModule.ORDER_RES_PROC_ERR_OTH

            GlobalModule.NETCONFSSH.send_response(
                order_result, ec_message, session_id)

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

        if read_tras_list_result is False:
            raise IOError('Failed getting Transaction ID list.')

        else:
            if transaction_id_list is not None:
                return False

            else:
                return True

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

    @decorater_log
    def _order_main(self, ec_message, session_id):
        '''
        Wait for request from Netconf server, conduct order control after receiving request.
        Explanation about parameter:
            ec_message:EC message
            session_id:Session ID
        Explanation about return value:
            None
        '''

        transaction_id = uuid.uuid4()

        current_time = datetime.datetime.now()

        current_time_str = datetime.datetime.strftime(
            current_time, '%Y-%m-%d %H:%M:%S.%f')

        ec_message_str = copy.deepcopy(ec_message)
        ec_message_str = ec_message_str.read()

        order_contents = current_time_str + ' ' + ec_message_str

        try:
            service_kind, order_kind, device_num =\
                self._analysis_em_scenario(ec_message)
        except ValueError:
            order_result = GlobalModule.ORDER_RES_PROC_ERR_ORDER

            GlobalModule.NETCONFSSH.send_response(
                order_result, ec_message, session_id)

            GlobalModule.EM_LOGGER.debug('result:%s', order_result)

            GlobalModule.EM_LOGGER.debug('Order Analysis Error')

            raise StopIteration(
                'Service type, Order type, Analysis of device number is failed.')

        scenario_select_result, scenario_name, order_timer =\
            self._select_em_scenario(service_kind, order_kind)

        GlobalModule.EM_LOGGER.debug(
            'Scenario name:%s Timer of waiting order:%s', scenario_name, order_timer)

        if scenario_select_result is False\
                or scenario_name == '' or order_timer == '':
            GlobalModule.EM_LOGGER.warning('203005 No Applicable Service')

            db_control = 'UPDATE'
            transaction_status = GlobalModule.TRA_STAT_PROC_ERR_ORDER

            rep_tra_stat_result = self._replace_transaction_status(
                db_control,
                transaction_id,
                transaction_status,
                service_kind,
                order_kind,
                order_contents)

            if rep_tra_stat_result is False:
                order_result = GlobalModule.ORDER_RES_PROC_ERR_OTH

                GlobalModule.NETCONFSSH.send_response(
                    order_result, ec_message, session_id)

                GlobalModule.EM_LOGGER.info(
                    '103002 Service:%s result:%s', scenario_name, order_result)

                GlobalModule.EM_LOGGER.info(
                    '103004 Service:%s Error', scenario_name)

                raise IOError('Transaction status writring is failed.')

            else:
                order_result = GlobalModule.ORDER_RES_PROC_ERR_ORDER

                GlobalModule.NETCONFSSH.send_response(
                    order_result, ec_message, session_id)

                GlobalModule.EM_LOGGER.info(
                    '103002 Service:%s result:%s', scenario_name, order_result)

                db_control = 'DELETE'

                GlobalModule.EMSYSCOMUTILDB.write_device_status_list(
                    transaction_id)

                db_control = 'DELETE'
                transaction_status = 0

                self._replace_transaction_status(
                    db_control,
                    transaction_id,
                    transaction_status,
                    service_kind,
                    order_kind,
                    order_contents)

                GlobalModule.EM_LOGGER.info(
                    '103004 Service:%s Error', scenario_name)

                raise StandardError('Failed in Scenario select.')

        else:
            GlobalModule.EM_LOGGER.info(
                '103001 Service:%s start', scenario_name)

        db_control = 'UPDATE'
        transaction_status = GlobalModule.TRA_STAT_PROC_RUN

        GlobalModule.EM_LOGGER.debug(
            'Transaction status update(init state -> processing)')

        rep_tra_stat_result = self._replace_transaction_status(
            db_control,
            transaction_id,
            transaction_status,
            service_kind,
            order_kind,
            order_contents)

        if rep_tra_stat_result is False:
            order_result = GlobalModule.ORDER_RES_PROC_ERR_OTH

            GlobalModule.NETCONFSSH.send_response(
                order_result, ec_message, session_id)

            GlobalModule.EM_LOGGER.info(
                '103002 Service:%s result:%s', scenario_name, order_result)

            GlobalModule.EM_LOGGER.info(
                '103004 Service:%s Error', scenario_name)

            raise IOError('Transaction status writring is failed.')

        order_timer_set = order_timer / 1000

        timer = threading.Timer(order_timer_set, self._find_timeout)
        timer.start()

        GlobalModule.EM_LOGGER.debug('Timer of waiting order start.')

        scenario_name_em = 'Em' + scenario_name

        GlobalModule.EM_LOGGER.debug(
            'Generate start class name.:%s', scenario_name_em)

        lib_path = GlobalModule.EM_LIB_PATH

        GlobalModule.EM_LOGGER.debug('enviroment value path:%s', lib_path)

        filepath, filename, data =\
            imp.find_module(scenario_name_em,
                            [os.path.join(lib_path, 'Scenario')])

        GlobalModule.EM_LOGGER.debug('Search module.')

        self.__target_scenario_module =\
            imp.load_module(scenario_name_em, filepath, filename, data)

        GlobalModule.EM_LOGGER.debug('Read module.')

        self.__target_scenario_class_ins =\
            getattr(self.__target_scenario_module, scenario_name_em)()

        GlobalModule.EM_LOGGER.debug('Create instance.')

        if order_kind == "get":
            order_kind_sc = None
        else:
            order_kind_sc = order_kind

        scenario_start_result = self.__target_scenario_class_ins.execute(
            ec_message, transaction_id, order_kind_sc)

        if scenario_start_result is False:
            timer.cancel()

            order_result = GlobalModule.ORDER_RES_PROC_ERR_OTH

            GlobalModule.NETCONFSSH.send_response(
                order_result, ec_message, session_id)

            GlobalModule.EM_LOGGER.info(
                '103002 Service:%s result:%s', scenario_name, order_result)

            db_control = 'DELETE'

            GlobalModule.EMSYSCOMUTILDB.write_device_status_list(
                transaction_id)

            db_control = 'DELETE'
            transaction_status = 0

            self._replace_transaction_status(
                db_control,
                transaction_id,
                transaction_status,
                service_kind,
                order_kind,
                order_contents)

            GlobalModule.EM_LOGGER.info(
                '103004 Service:%s Error', scenario_name)

            raise StandardError('Failed in starting scenario.')

        GlobalModule.EM_LOGGER.debug('Monitoring(processing)')
        monitor_result, order_result = self._monitor_transaction(
            transaction_id, transaction_status, device_num)

        if monitor_result is False:
            timer.cancel()

            GlobalModule.NETCONFSSH.send_response(
                order_result, ec_message, session_id)

            GlobalModule.EM_LOGGER.info(
                '103002 Service:%s result:%s', scenario_name, order_result)

            db_control = 'DELETE'

            GlobalModule.EMSYSCOMUTILDB.write_device_status_list(
                transaction_id)

            db_control = 'DELETE'
            transaction_status = 0

            self._replace_transaction_status(
                db_control,
                transaction_id,
                transaction_status,
                service_kind,
                order_kind,
                order_contents)

            GlobalModule.EM_LOGGER.info(
                '103004 Service:%s Error', scenario_name)

            GlobalModule.EM_LOGGER.warning('203006 Order Service Error')

            raise StandardError('Failed in transaction monitoring.')

        db_control = 'UPDATE'
        transaction_status = GlobalModule.TRA_STAT_EDIT_CONF

        GlobalModule.EM_LOGGER.debug(
            'Transaction status update(processing -> Edit-config)')

        rep_tra_stat_result = self._replace_transaction_status(
            db_control,
            transaction_id,
            transaction_status,
            service_kind,
            order_kind,
            order_contents)

        if rep_tra_stat_result is False:
            timer.cancel()

            order_result = GlobalModule.ORDER_RES_PROC_ERR_OTH

            GlobalModule.NETCONFSSH.send_response(
                order_result, ec_message, session_id)

            GlobalModule.EM_LOGGER.info(
                '103002 Service:%s result:%s', scenario_name, order_result)

            GlobalModule.EM_LOGGER.info(
                '103004 Service:%s Error', scenario_name)

            raise IOError('Transaction status writring is failed.')

        GlobalModule.EM_LOGGER.debug('Monitoring(Edit-config)')
        monitor_result, order_result = self._monitor_transaction(
            transaction_id, transaction_status, device_num)

        if monitor_result is False:
            timer.cancel()

            GlobalModule.NETCONFSSH.send_response(
                order_result, ec_message, session_id)

            GlobalModule.EM_LOGGER.info(
                '103002 Service:%s result:%s', scenario_name, order_result)

            db_control = 'DELETE'

            GlobalModule.EMSYSCOMUTILDB.write_device_status_list(
                transaction_id)

            db_control = 'DELETE'
            transaction_status = 0

            self._replace_transaction_status(
                db_control,
                transaction_id,
                transaction_status,
                service_kind,
                order_kind,
                order_contents)

            GlobalModule.EM_LOGGER.info(
                '103004 Service:%s Error', scenario_name)

            GlobalModule.EM_LOGGER.warning('203006 Order Service Error')

            raise StandardError('Failed in transaction monitoring.')

        db_control = 'UPDATE'
        transaction_status = GlobalModule.TRA_STAT_CONF_COMMIT

        GlobalModule.EM_LOGGER.debug(
            'Transaction status update(Edit-config -> Confirmed-commit)')

        rep_tra_stat_result = self._replace_transaction_status(
            db_control,
            transaction_id,
            transaction_status,
            service_kind,
            order_kind,
            order_contents)

        if rep_tra_stat_result is False:
            timer.cancel()

            order_result = GlobalModule.ORDER_RES_PROC_ERR_OTH

            GlobalModule.NETCONFSSH.send_response(
                order_result, ec_message, session_id)

            GlobalModule.EM_LOGGER.info(
                '103002 Service:%s result:%s', scenario_name, order_result)

            GlobalModule.EM_LOGGER.info(
                '103004 Service:%s Error', scenario_name)

            raise IOError('Transaction status writring is failed.')

        GlobalModule.EM_LOGGER.debug('Monitoring(Confirmed-commit)')
        monitor_result, order_result = self._monitor_transaction(
            transaction_id, transaction_status, device_num)

        if monitor_result is False:
            timer.cancel()

            GlobalModule.NETCONFSSH.send_response(
                order_result, ec_message, session_id)

            GlobalModule.EM_LOGGER.info(
                '103002 Service:%s result:%s', scenario_name, order_result)

            db_control = 'DELETE'

            GlobalModule.EMSYSCOMUTILDB.write_device_status_list(
                transaction_id)

            db_control = 'DELETE'
            transaction_status = 0

            self._replace_transaction_status(
                db_control,
                transaction_id,
                transaction_status,
                service_kind,
                order_kind,
                order_contents)

            GlobalModule.EM_LOGGER.info(
                '103004 Service:%s Error', scenario_name)

            GlobalModule.EM_LOGGER.warning('203006 Order Service Error')

            raise StandardError('Failed in transaction monitoring.')

        db_control = 'UPDATE'
        transaction_status = GlobalModule.TRA_STAT_COMMIT

        GlobalModule.EM_LOGGER.debug(
            'Transaction status update(Confirmed-commit -> Commit)')

        rep_tra_stat_result = self._replace_transaction_status(
            db_control,
            transaction_id,
            transaction_status,
            service_kind,
            order_kind,
            order_contents)

        if rep_tra_stat_result is False:
            timer.cancel()

            order_result = GlobalModule.ORDER_RES_PROC_ERR_OTH

            GlobalModule.NETCONFSSH.send_response(
                order_result, ec_message, session_id)

            GlobalModule.EM_LOGGER.info(
                '103002 Service:%s result:%s', scenario_name, order_result)

            GlobalModule.EM_LOGGER.info(
                '103004 Service:%s Error', scenario_name)

            raise IOError('Transaction status writring is failed.')

        self.__target_scenario_class_ins.notify(ec_message,
                                                transaction_id,
                                                order_kind)

        GlobalModule.EM_LOGGER.debug('Monitoring(Commit)')
        monitor_result, order_result = self._monitor_transaction(
            transaction_id, transaction_status, device_num)

        if monitor_result is False:
            timer.cancel()

            GlobalModule.NETCONFSSH.send_response(
                order_result, ec_message, session_id)

            GlobalModule.EM_LOGGER.info(
                '103002 Service:%s result:%s', scenario_name, order_result)

            db_control = 'DELETE'

            GlobalModule.EMSYSCOMUTILDB.write_device_status_list(
                transaction_id)

            db_control = 'DELETE'
            transaction_status = 0

            self._replace_transaction_status(
                db_control,
                transaction_id,
                transaction_status,
                service_kind,
                order_kind,
                order_contents)

            GlobalModule.EM_LOGGER.info(
                '103004 Service:%s Error', scenario_name)

            GlobalModule.EM_LOGGER.warning('203006 Order Service Error')

            raise StandardError('Failed in transaction monitoring.')

        db_control = 'UPDATE'
        transaction_status = GlobalModule.TRA_STAT_PROC_END

        GlobalModule.EM_LOGGER.debug(
            'Transaction status update(Commit -> Finished successfully)')

        rep_tra_stat_result = self._replace_transaction_status(
            db_control,
            transaction_id,
            transaction_status,
            service_kind,
            order_kind,
            order_contents)

        if rep_tra_stat_result is False:
            timer.cancel()

            order_result = GlobalModule.ORDER_RES_PROC_ERR_OTH

            GlobalModule.NETCONFSSH.send_response(
                order_result, ec_message, session_id)

            GlobalModule.EM_LOGGER.info(
                '103002 Service:%s result:%s', scenario_name, order_result)

            GlobalModule.EM_LOGGER.info(
                '103004 Service:%s Error', scenario_name)

            raise IOError('Transaction status writring is failed.')

        timer.cancel()

        order_result = GlobalModule.ORDER_RES_OK

        GlobalModule.NETCONFSSH.send_response(
            order_result, ec_message, session_id)

        GlobalModule.EM_LOGGER.info(
            '103002 Service:%s result:%s', scenario_name, order_result)

        db_control = 'DELETE'

        GlobalModule.EMSYSCOMUTILDB.write_device_status_list(
            transaction_id)

        db_control = 'DELETE'
        transaction_status = 0

        self._replace_transaction_status(
            db_control,
            transaction_id,
            transaction_status,
            service_kind,
            order_kind,
            order_contents)

        GlobalModule.EM_LOGGER.info(
            '103003 Service:%s end', scenario_name)

    @staticmethod
    @decorater_log
    def _replace_transaction_status(
            db_control,
            transaction_id,
            transaction_status,
            service_kind,
            order_kind,
            order_contents):
        '''
        Launch transaction status (order management information) writing in common utility for the system and write the value.
        Explanation about parameter:
            db_control:DB control (registration, update)
            transaction_id:Transaction ID
            transaction_status:Transaction status
            service_kind:Service type
            order_kind:Order type
            order_contents:Order contents
        Explanation about return value:
            Result after filling-in transaction status : True or False
        '''

        write_tra_stat_result = \
            GlobalModule.EMSYSCOMUTILDB.write_transaction_status(
                db_control,
                transaction_id,
                transaction_status,
                service_kind,
                order_kind,
                order_contents)

        return write_tra_stat_result

    @decorater_log
    def _analysis_em_scenario(self, ec_message):

        service_kind = None
        device_type = None
        device_num = None

        context = copy.deepcopy(ec_message)
        context = etree.iterparse(context, events=('start', 'end'))

        for event, element in context:
            if (event == 'start' and
                    (element.tag == self.rpc_name + 'config' or
                     element.tag == self.rpc_name + 'filter')):
                config_ptn = element.tag

                service_kind, device_type, sys_ns = \
                    self._analysis_service(element)

                device_num = self._count_device(element, sys_ns + device_type)

                order_kind = self._analysis_netconf_operation(
                    context, service_kind, config_ptn, self.rpc_name, sys_ns)
                break

        GlobalModule.EM_LOGGER.debug(
            'analysis result Service:%s Order:%s Device_Num:%s',
            service_kind, order_kind, device_num)

        return service_kind, order_kind, device_num

    @decorater_log
    def _analysis_service(self, element):
        '''
        Analize Service type in received Netconf.
        Explanation about parameter:
            element:config section
        Explanation about return value:
            Service type:str
            Device type:str
            Service name space:str
        '''
        svs_dev_type = self._get_device_type(element)

        for service in GlobalModule.EM_SERVICE_LIST:
            sys_ns = "{%s}" % (GlobalModule.EM_NAME_SPACES[service],)
            if element[0].tag == sys_ns + service:
                return service, svs_dev_type, sys_ns

        GlobalModule.EM_LOGGER.debug('Service Kind ERROR')
        raise ValueError('Failed to acquire service')

    @staticmethod
    @decorater_log
    def _get_device_type(element):
        '''
        Analize Device type in received Netconf.
        Explanation about parameter:
            element:config section
        Explanation about return value:
            Device type:str
        '''

        dev_type = ""
        pattern_with_ope = "<(.*device.*) operation=.*>"
        pattern = "<(.*device.*)>"
        xml_str = etree.tostring(element)
        match_obj = re.search(pattern_with_ope, xml_str)
        if not match_obj:
            match_obj = re.search(pattern, xml_str)
        if match_obj:
            dev_type = match_obj.groups()[0]
            GlobalModule.EM_LOGGER.debug('device type:%s' % (dev_type,))
        else:
            GlobalModule.EM_LOGGER.debug(
                'Error! device type getting fault')
            raise ValueError('Failed to acquire device type')
        return dev_type

    @staticmethod
    @decorater_log
    def _count_device(element, device_type):
        '''
        Count receiving Netconf device
        Explanation about parameter:
            element:config section
            device_type:Device type
        Explanation about return value:
            Device count:int
        '''
        device_list = element[0].findall(device_type)
        if len(device_list) > 0:
            device_num = len(device_list)
        else:
            GlobalModule.EM_LOGGER.debug('device count is fault')
            raise ValueError('Failed to counting device')
        return device_num

    @staticmethod
    @decorater_log
    def _analysis_netconf_operation(context,
                                    service_kind,
                                    config_ptn,
                                    rpc_name,
                                    svc_ns):
        '''
        Analyze operation type of receiving Netconf.
        Explanation about parameter:
            context:config section
            service_kind:Service type
            config_ptn: Config pattern
            rpc_name:RPC name space
            svc_ns:Service name space
        Explanation about return value:
            Order type:str
        '''

        for event, element in context:
            if (event == 'start' and
                    element.items() == [('operation', 'replace')]):
                order_kind = 'replace'
                break

            if (event == 'start' and
                    element.items() == [('operation', 'delete')]):
                order_kind = 'delete'
                break

            elif event == 'end' and element.tag == svc_ns + service_kind:
                order_kind = (
                    'merge' if config_ptn == rpc_name + 'config' else 'get')
                break
        return order_kind

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
        if result is False:
            return False, None, None

        scenario_result, scenario_name, order_timer =\
            GlobalModule.EM_CONFIG.read_scenario_conf(service_kind, order_kind)

        return scenario_result, scenario_name, order_timer

    @decorater_log
    def _monitor_transaction(self, transaction_id, tra_mng_stat, device_num):
        '''
        Monitor order management information DB regularly, notify the sync instruction to individual processing of each scenario.
        Explanation about parameter:
            transaction_id:Transaction ID
            tra_mng_stat:Transaction status
        Explanation about return value:
            Method result : True or False
            Order result : int
        '''

        retry_flg = 'retry'
        retry_cnt = 0
        roll_cnt = 0

        sys_com_result, monitor_time_value = \
            GlobalModule.EM_CONFIG.\
            read_sys_common_conf('Timer_transaction_db_watch')

        if sys_com_result is False:
            GlobalModule.EM_LOGGER.debug('Read Config Error')
            monitor_time_value = 100

        elif monitor_time_value is None:
            GlobalModule.EM_LOGGER.debug('Transaction DB Watch None')
            monitor_time_value = 100

        retry_timer = float(monitor_time_value) / 1000

        while retry_flg == 'retry':
            if EmOrderflowControl.timeout_flag is False:
                read_tra_dev_list_result, dev_con_list =\
                    GlobalModule.EMSYSCOMUTILDB.\
                    read_transaction_device_status_list(transaction_id)

                if read_tra_dev_list_result is False:
                    GlobalModule.EM_LOGGER.debug(
                        'Read DeviceStatusMgmtInfo Error')
                    order_result = GlobalModule.ORDER_RES_PROC_ERR_OTH
                    return False, order_result

                if dev_con_list is not None:
                    if len(dev_con_list) == device_num:
                        for dev_mng in dev_con_list:
                            if 'transaction_status' in dev_mng:
                                dev_mng_tra_stat =\
                                    dev_mng['transaction_status']
                                if dev_mng_tra_stat <\
                                        GlobalModule.TRA_STAT_ROLL_BACK:
                                    if dev_mng_tra_stat <= tra_mng_stat:
                                        retry_cnt += 1
                                else:
                                    for dev_mng_roll in dev_con_list:
                                        if 'transaction_status' in\
                                                dev_mng_roll:
                                            dev_mng_roll_tra_stat =\
                                                dev_mng_roll[
                                                    'transaction_status']
                                            if dev_mng_roll_tra_stat ==\
                                               GlobalModule.\
                                               TRA_STAT_ROLL_BACK_END:
                                                roll_cnt += 1
                                            elif dev_mng_roll_tra_stat ==\
                                                    GlobalModule.\
                                                    TRA_STAT_PROC_END:
                                                roll_cnt += 1

                                    if dev_mng_tra_stat ==\
                                       GlobalModule.TRA_STAT_ROLL_BACK_END:
                                        if roll_cnt == len(dev_con_list):
                                            anaiy_order =\
                                                self._analysis_order_manage(
                                                    dev_mng_tra_stat)
                                            order_result = anaiy_order
                                            GlobalModule.EM_LOGGER.debug(
                                                'RollBack')
                                            return False, order_result
                                        else:
                                            retry_cnt += 1
                                            roll_cnt = 0
                                    elif dev_mng_tra_stat >\
                                            GlobalModule.\
                                            TRA_STAT_ROLL_BACK_END:
                                        if roll_cnt == (len(dev_con_list) - 1):
                                            anaiy_order =\
                                                self._analysis_order_manage(
                                                    dev_mng_tra_stat)
                                            order_result = anaiy_order
                                            GlobalModule.EM_LOGGER.debug(
                                                'Other RollBack')
                                            return False, order_result
                                        else:
                                            retry_cnt += 1
                                            roll_cnt = 0
                                    else:
                                        retry_cnt += 1
                                        roll_cnt = 0

                    else:
                        GlobalModule.EM_LOGGER.debug('Device Num Unmatch')
                        retry_cnt += 1

                else:
                    GlobalModule.EM_LOGGER.debug('Device List None')
                    retry_cnt += 1

                if retry_cnt == 0:
                    GlobalModule.EM_LOGGER.debug('Monitor NoRetry')
                    retry_flg = 'notretry'
                else:
                    GlobalModule.EM_LOGGER.debug('Monitor Retry')
                    retry_flg = 'retry'
                    retry_cnt = 0
                    roll_cnt = 0
                    time.sleep(retry_timer)

            else:
                EmOrderflowControl.timeout_flag = False

                GlobalModule.EM_LOGGER.debug('Monitor Timeout')
                order_result = GlobalModule.ORDER_RES_PROC_ERR_OTH
                return False, order_result

        GlobalModule.EM_LOGGER.debug('Monitor Success')
        order_result = GlobalModule.ORDER_RES_OK
        return True, order_result

    @staticmethod
    @decorater_log
    def _analysis_order_manage(dev_mng_tra_stat):
        '''
        Analyze order management information.
        Explanation about parameter:
            dev_mng_tra_stat:Transaction status
        Explanation about return value:
            Analysis result:int
                1:Finished successfully
                2:Rollback completed
                3:Processing has failed.(Validation check NG)
                4:Processing has failed.(Inadequate request)
                5:Processing has failed.(Matching NG)
                6:Processing has failed.(Stored information None)
                7:Processing has failed.(Temporary)
                8:Processing has failed.(Other)
        '''

        anaiy_order = GlobalModule.ORDER_RES_OK

        if dev_mng_tra_stat == GlobalModule.TRA_STAT_ROLL_BACK_END:
            anaiy_order = GlobalModule.ORDER_RES_ROLL_BACK_END

        elif dev_mng_tra_stat == GlobalModule.TRA_STAT_PROC_ERR_CHECK:
            anaiy_order = GlobalModule.ORDER_RES_PROC_ERR_CHECK

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

        return anaiy_order

    @staticmethod
    @decorater_log
    def _find_timeout():
        '''
        In case that order completion waiting timer has timed out, send "NG" to Netconf server.
        Explanation about parameter:
            None
        Explanation about return value:
            None
        '''

        GlobalModule.EM_LOGGER.debug('Timeout detection')

        EmOrderflowControl.timeout_flag = True
