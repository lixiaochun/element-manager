# -*- coding: utf-8 -*-
import Queue
import threading
import datetime
import time
import uuid
import imp
import copy
import os

from lxml import etree

import GlobalModule
from EmCommonLog import decorater_log
from EmSeparateScenario import EmScenario


class EmOrderflowControl(threading.Thread):


    __target_scenario_module = None
    __target_scenario_class_ins = None

    @decorater_log
    def __init__(self):

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

        else:
            if transaction_id_list is not None:
                for transaction_id in transaction_id_list:
                    read_tra_dev_list_result, dev_con_list =\
                        GlobalModule.EMSYSCOMUTILDB.\
                        read_transaction_device_status_list(
                            transaction_id)

                    sys_com_result, conf_timeout_value = \
                        GlobalModule.EM_CONFIG.\

                    if read_tra_dev_list_result is False:

                    elif sys_com_result is False:

                    elif conf_timeout_value is None:

                    else:
                        if dev_con_list is not None:
                            read_tra_inf_result, tra_table_inf = \
                                GlobalModule.EMSYSCOMUTILDB.\
                                read_transaction_info(transaction_id)

                            if read_tra_inf_result is False:

                            elif tra_table_inf is None:
                                pass

                            else:
                                order_reg_time_str =\

                                order_reg_time_int_temp = \
                                    datetime.datetime.\
                                    strptime(order_reg_time_str,

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

    @decorater_log
    def run(self):

        while not self.stop_event.is_set():
            try:
                que_item = self.que_event.get(block=True, timeout=0.01)

                ec_message = que_item[0]
                session_id = que_item[1]

                self.__order_main(ec_message, session_id)

                self.que_event.task_done()
            except Queue.Empty:
                pass
            except (StopIteration, IOError, StandardError):
                self.que_event.task_done()

    @decorater_log
    def execute(self, ec_message, session_id):

        try:
            self.que_event.put((ec_message, session_id), block=False)
        except Queue.Full:
            order_result = GlobalModule.ORDER_RES_PROC_ERR_OTH

            GlobalModule.NETCONFSSH.send_response(
                order_result, ec_message, session_id)

    @staticmethod
    @decorater_log
    def get_transaction_presence():

        read_tras_list_result, transaction_id_list = \
            GlobalModule.EMSYSCOMUTILDB.read_transactionid_list()

        if read_tras_list_result is False:

        else:
            if transaction_id_list is not None:
                return False

            else:
                return True

    @decorater_log
    def stop(self):

        self.stop_event.set()
        self.join()

    @decorater_log
    def __order_main(self, ec_message, session_id):

        transaction_id = uuid.uuid4()

        current_time = datetime.datetime.now()

        current_time_str = datetime.datetime.strftime(

        ec_message_str = copy.deepcopy(ec_message)
        ec_message_str = ec_message_str.read()


        try:
            service_kind, order_kind, device_num =\
                self.__analysis_em_scenario(ec_message)
        except ValueError:
            order_result = GlobalModule.ORDER_RES_PROC_ERR_ORDER

            GlobalModule.NETCONFSSH.send_response(
                order_result, ec_message, session_id)




        scenario_select_result, scenario_name, order_timer =\
            self.__select_em_scenario(service_kind, order_kind)

        GlobalModule.EM_LOGGER.debug(

        if scenario_select_result is False\

            transaction_status = GlobalModule.TRA_STAT_PROC_ERR_ORDER

            rep_tra_stat_result = self.__replace_transaction_status(
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

                GlobalModule.EM_LOGGER.info(


            else:
                order_result = GlobalModule.ORDER_RES_PROC_ERR_ORDER

                GlobalModule.NETCONFSSH.send_response(
                    order_result, ec_message, session_id)

                GlobalModule.EM_LOGGER.info(


                GlobalModule.EMSYSCOMUTILDB.write_device_status_list(
                    transaction_id)

                transaction_status = 0

                self.__replace_transaction_status(
                    db_control,
                    transaction_id,
                    transaction_status,
                    service_kind,
                    order_kind,
                    order_contents)

                GlobalModule.EM_LOGGER.info(


        else:
            GlobalModule.EM_LOGGER.info(

        transaction_status = GlobalModule.TRA_STAT_PROC_RUN

        GlobalModule.EM_LOGGER.debug(

        rep_tra_stat_result = self.__replace_transaction_status(
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

            GlobalModule.EM_LOGGER.info(


        order_timer_set = order_timer / 1000

        timer = threading.Timer(order_timer_set, self.__find_timeout)
        timer.start()




        lib_path = os.environ.get("EM_LIB_PATH")


        filepath, filename, data =\


        self.__target_scenario_module =\
            imp.load_module(scenario_name_em, filepath, filename, data)


        self.__target_scenario_class_ins =\
            getattr(self.__target_scenario_module, scenario_name_em)()


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


            GlobalModule.EMSYSCOMUTILDB.write_device_status_list(
                transaction_id)

            transaction_status = 0

            self.__replace_transaction_status(
                db_control,
                transaction_id,
                transaction_status,
                service_kind,
                order_kind,
                order_contents)

            GlobalModule.EM_LOGGER.info(


        monitor_result, order_result = self.__monitor_transaction(
            transaction_id, transaction_status, device_num)

        if monitor_result is False:
            timer.cancel()

            GlobalModule.NETCONFSSH.send_response(
                order_result, ec_message, session_id)

            GlobalModule.EM_LOGGER.info(


            GlobalModule.EMSYSCOMUTILDB.write_device_status_list(
                transaction_id)

            transaction_status = 0

            self.__replace_transaction_status(
                db_control,
                transaction_id,
                transaction_status,
                service_kind,
                order_kind,
                order_contents)

            GlobalModule.EM_LOGGER.info(



        transaction_status = GlobalModule.TRA_STAT_EDIT_CONF

        GlobalModule.EM_LOGGER.debug(

        rep_tra_stat_result = self.__replace_transaction_status(
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

            GlobalModule.EM_LOGGER.info(


        monitor_result, order_result = self.__monitor_transaction(
            transaction_id, transaction_status, device_num)

        if monitor_result is False:
            timer.cancel()

            GlobalModule.NETCONFSSH.send_response(
                order_result, ec_message, session_id)

            GlobalModule.EM_LOGGER.info(


            GlobalModule.EMSYSCOMUTILDB.write_device_status_list(
                transaction_id)

            transaction_status = 0

            self.__replace_transaction_status(
                db_control,
                transaction_id,
                transaction_status,
                service_kind,
                order_kind,
                order_contents)

            GlobalModule.EM_LOGGER.info(



        transaction_status = GlobalModule.TRA_STAT_CONF_COMMIT

        GlobalModule.EM_LOGGER.debug(

        rep_tra_stat_result = self.__replace_transaction_status(
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

            GlobalModule.EM_LOGGER.info(


        monitor_result, order_result = self.__monitor_transaction(
            transaction_id, transaction_status, device_num)

        if monitor_result is False:
            timer.cancel()

            GlobalModule.NETCONFSSH.send_response(
                order_result, ec_message, session_id)

            GlobalModule.EM_LOGGER.info(


            GlobalModule.EMSYSCOMUTILDB.write_device_status_list(
                transaction_id)

            transaction_status = 0

            self.__replace_transaction_status(
                db_control,
                transaction_id,
                transaction_status,
                service_kind,
                order_kind,
                order_contents)

            GlobalModule.EM_LOGGER.info(



        transaction_status = GlobalModule.TRA_STAT_COMMIT

        GlobalModule.EM_LOGGER.debug(

        rep_tra_stat_result = self.__replace_transaction_status(
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

            GlobalModule.EM_LOGGER.info(


        self.__target_scenario_class_ins.notify(ec_message,
                                                transaction_id,
                                                order_kind)

        monitor_result, order_result = self.__monitor_transaction(
            transaction_id, transaction_status, device_num)

        if monitor_result is False:
            timer.cancel()

            GlobalModule.NETCONFSSH.send_response(
                order_result, ec_message, session_id)

            GlobalModule.EM_LOGGER.info(


            GlobalModule.EMSYSCOMUTILDB.write_device_status_list(
                transaction_id)

            transaction_status = 0

            self.__replace_transaction_status(
                db_control,
                transaction_id,
                transaction_status,
                service_kind,
                order_kind,
                order_contents)

            GlobalModule.EM_LOGGER.info(



        transaction_status = GlobalModule.TRA_STAT_PROC_END

        GlobalModule.EM_LOGGER.debug(

        rep_tra_stat_result = self.__replace_transaction_status(
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

            GlobalModule.EM_LOGGER.info(


        timer.cancel()

        order_result = GlobalModule.ORDER_RES_OK

        GlobalModule.NETCONFSSH.send_response(
            order_result, ec_message, session_id)

        GlobalModule.EM_LOGGER.info(


        GlobalModule.EMSYSCOMUTILDB.write_device_status_list(
            transaction_id)

        transaction_status = 0

        self.__replace_transaction_status(
            db_control,
            transaction_id,
            transaction_status,
            service_kind,
            order_kind,
            order_contents)

        GlobalModule.EM_LOGGER.info(

    @staticmethod
    @decorater_log
    def __replace_transaction_status(
            db_control,
            transaction_id,
            transaction_status,
            service_kind,
            order_kind,
            order_contents):

        write_tra_stat_result = \
            GlobalModule.EMSYSCOMUTILDB.write_transaction_status(
                db_control,
                transaction_id,
                transaction_status,
                service_kind,
                order_kind,
                order_contents)

        return write_tra_stat_result

    @staticmethod
    @decorater_log
    def __analysis_em_scenario(ec_message):


        context = copy.deepcopy(ec_message)

        for event, element in context:
                config_ptn = element.tag







                else:

                device_list = element[0].findall(device_type)
                if len(device_list) > 0:
                    device_num = len(device_list)
                else:

                for event, element in context:
                        break

                        if config_ptn == rpc_name + "config":
                        else:
                        break

        GlobalModule.EM_LOGGER.debug(
            service_kind, order_kind, device_num)

        return service_kind, order_kind, device_num

    @staticmethod
    @decorater_log
    def __select_em_scenario(service_kind, order_kind):

        scenario_result, scenario_name, order_timer =\
            GlobalModule.EM_CONFIG.read_scenario_conf(service_kind, order_kind)

        return scenario_result, scenario_name, order_timer

    def __monitor_transaction(self, transaction_id, tra_mng_stat, device_num):

        retry_cnt = 0
        roll_cnt = 0

        sys_com_result, monitor_time_value = \
            GlobalModule.EM_CONFIG.\

        if sys_com_result is False:
            monitor_time_value = 100

        elif monitor_time_value is None:
            monitor_time_value = 100

        retry_timer = float(monitor_time_value) / 1000

            if EmOrderflowControl.timeout_flag is False:
                read_tra_dev_list_result, dev_con_list =\
                    GlobalModule.EMSYSCOMUTILDB.\
                    read_transaction_device_status_list(transaction_id)

                if read_tra_dev_list_result is False:
                    GlobalModule.EM_LOGGER.debug(
                    order_result = GlobalModule.ORDER_RES_PROC_ERR_OTH
                    return False, order_result

                if dev_con_list is not None:
                    if len(dev_con_list) == device_num:
                        for dev_mng in dev_con_list:
                                dev_mng_tra_stat =\
                                if dev_mng_tra_stat <\
                                        GlobalModule.TRA_STAT_ROLL_BACK:
                                    if dev_mng_tra_stat <= tra_mng_stat:
                                        retry_cnt += 1
                                else:
                                    for dev_mng_roll in dev_con_list:
                                                dev_mng_roll:
                                            dev_mng_roll_tra_stat =\
                                                dev_mng_roll[
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
                                                self.__analysis_order_manage(
                                                    dev_mng_tra_stat)
                                            order_result = anaiy_order
                                            GlobalModule.EM_LOGGER.debug(
                                            return False, order_result
                                        else:
                                            retry_cnt += 1
                                            roll_cnt = 0
                                    elif dev_mng_tra_stat >\
                                            GlobalModule.\
                                            TRA_STAT_ROLL_BACK_END:
                                        if roll_cnt == (len(dev_con_list) - 1):
                                            anaiy_order =\
                                                self.__analysis_order_manage(
                                                    dev_mng_tra_stat)
                                            order_result = anaiy_order
                                            GlobalModule.EM_LOGGER.debug(
                                            return False, order_result
                                        else:
                                            retry_cnt += 1
                                            roll_cnt = 0
                                    else:
                                        retry_cnt += 1
                                        roll_cnt = 0

                    else:
                        retry_cnt += 1

                else:
                    retry_cnt += 1

                if retry_cnt == 0:
                else:
                    retry_cnt = 0
                    roll_cnt = 0
                    time.sleep(retry_timer)

            else:
                EmOrderflowControl.timeout_flag = False

                order_result = GlobalModule.ORDER_RES_PROC_ERR_OTH
                return False, order_result

        order_result = GlobalModule.ORDER_RES_OK
        return True, order_result

    @staticmethod
    @decorater_log
    def __analysis_order_manage(dev_mng_tra_stat):

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
    def __find_timeout():


        EmOrderflowControl.timeout_flag = True
