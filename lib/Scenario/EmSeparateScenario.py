#! /usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2017 Nippon Telegraph and Telephone Corporation
# Filename: EmSeparateScenario.py
'''
Individual processing base for each scenario. 
'''
import threading
import Queue
import copy
from lxml import etree
from EmCommonLog import decorater_log
import GlobalModule


class EmScenario(threading.Thread):
    '''
    Individual section of each scenario. (base class) 
    '''

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmScenario, self).__init__()

        self.device_name_list = []

        self.device_cond_dict = {}

        self.device_thread_dict = {}

        self.com_driver_list = {}

        self.force = False

        self.service_type_list = {}
        scenario_conf = \
            GlobalModule.EM_CONFIG.read_service_type_scenario_conf()
        for key, value in scenario_conf.items():
            self.service_type_list[value[2]] = key[0]

        self.daemon = True
        self.que_events = Queue.Queue(10)
        self.start()

    @decorater_log
    def run(self):
        '''
        Get launched as default after launching Thread by Thread object.  
        Method for override. 
        '''
        while True:
            try:
                xml_message, transaction_id, order_type = self.que_events.get()

                self.__scenario_main(xml_message, transaction_id, order_type)

                self.que_events.task_done()

            except Exception as exception:
                GlobalModule.EM_LOGGER.debug(
                    "Scenario Starting Error:%s", str(type(exception)))

                self.que_events.task_done()

            for name in self.device_name_list:
                GlobalModule.EM_LOGGER.debug("Device:%s thread join", name)
                thread_info = self.device_thread_dict.get(name)
                if thread_info is not None:
                    thread_info.join()

            break

    @decorater_log
    def execute(self, ec_message, transaction_id, order_type):
        '''
        Gets launched from order flow control and conduct necessary settings to Queue. 
        Explanation about parameter:
            ec_message: Message for each device
            transaction_id: Transaction ID
            order_type: Order type
        Explanation about return value:
            True:Normal, False:Abnormal
        '''
        try:
            self.que_events.put(
                (ec_message, transaction_id, order_type), block=False)
        except Queue.Full:
            GlobalModule.EM_LOGGER.debug("que_event.put NG(Queue.Full)")
            return False

        GlobalModule.EM_LOGGER.debug("que_event.put OK")
        return True

    @decorater_log
    def notify(self, ec_message, transaction_id, order_type):
        '''
        Launched from order flow control and instructs to continue processing to the child thread. 
        Explanation about parameter:
            ec_message: Message for each device
            transaction_id: Transaction ID
            order_type: Order type
        Explanation about return value:
            None
        '''
        for name in self.device_name_list:
            GlobalModule.EM_LOGGER.debug("Condition acquire notify release")
            device_thread_con = self.device_cond_dict.get(name)
            if device_thread_con is not None:
                device_thread_con.acquire()
                device_thread_con.notify()
                device_thread_con.release()


    @decorater_log
    def __scenario_main(self, ec_message, transaction_id, order_type):
        '''
        Conducts administration for each device n(child thread) at individual control of each scenario. 
        Explanation about parameter:
            ec_message: Message for each device
            transaction_id: Transaction ID
            order_type: Order type
        Explanation about return value:
            None
        '''


        self.device_name_list, device_xml_dict = self._analyze_ec_message(
            ec_message)

        for name in self.device_name_list:
            try:
                self.device_cond_dict[name] = threading.Condition()

                thread = threading.Thread(
                    target=self._gen_sub_thread,
                    args=(device_xml_dict[name],
                          transaction_id,
                          order_type,
                          self.device_cond_dict[name],
                          name,
                          self.force,)
                )
                self.device_thread_dict[name] = thread
                thread.daemon = True
                thread.start()

            except TypeError:
                GlobalModule.EM_LOGGER.debug(
                    "Scenario Starting Error:TypeError, device_name: %s", name)

    @decorater_log
    def _analyze_ec_message(self, ec_message):
        '''
        Netconf message analysis
            Divides the Netconf message from order flow control for each device. 
        Parameter:
            ec_message : Netconf message
        Return valur :
            Device name: Dictionary type Netconf message for each device. 
        '''

        device_name_list = []
        device_xml_dict = {}

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
                device_type = self.device_type
                break
            else:
                GlobalModule.EM_LOGGER.debug("Not SERVICE Tag")

        GlobalModule.EM_LOGGER.debug("device_type:%s", device_type)

        for event, element in context:

            GlobalModule.EM_LOGGER.debug("EVENT : %s , ELEMENT : %s"
                                         % (event, element))

            if event == "end" and \
                    element.tag == ns_value + "force":
                GlobalModule.EM_LOGGER.debug("Enforced deletion flag enabled")
                self.force = True

            if event == "end" and element.tag == ns_value + device_type:
                device_tag = ns_value + "name"
                device_name = element.find(".//" + device_tag).text
                device_name_list.append(device_name)

                device_xml_dict[device_name] = \
                    self._gen_netconf_message(element, slice_name)
                GlobalModule.EM_LOGGER.debug(
                    "device_xml_dict: %s", device_xml_dict[device_name])
                GlobalModule.EM_LOGGER.debug(
                    "device_name_list: %s", device_name_list)

        return device_name_list, device_xml_dict

    @staticmethod
    @decorater_log
    def _gen_netconf_message(element, slice_name=None):
        '''
        Device name：Create Netconf message (json letter string).
        '''
        return etree.tostring(element)

    @decorater_log
    def _gen_sub_thread(
            self, device_message,
            transaction_id, order_type, condition, device_name, force):
        '''
        Conducts control for each device. 
        Explanation about parameter:
            device_message: Message for each device
            transaction_id: Transaction ID
            order_type: Order type
            condition: Thread control information
            force: force: Forced deletion flag (True:Valid,False:Invalid)
        Explanation about return value:
            None
        '''

        GlobalModule.EM_LOGGER.error(
            "304005 Call SeparateScenario IF:_gen_sub_thread NG")

        return False

    @decorater_log
    def _find_timeout(self, condition):
        '''
        Set time out flag and launch thread.  
        Explanation about parameter:
            condition: Thread control information
        Explanation about return value:
            None
        '''

        GlobalModule.EM_LOGGER.error(
            "304005 Call SeparateScenario IF:_find_timeout NG")

        return False

    @decorater_log
    def _judg_transaction_status(self, transaction_status):
        '''
        Make judgment on transaction status of transaction management information table. 
        Explanation about parameter:
            transaction_status: Transaction status
        Explanation about return value:
            Necessity for updating transaction status : boolean (True:Update necessary,False:Update unnecessary)
        '''

        GlobalModule.EM_LOGGER.error(
            "304005 Call SeparateScenario IF:_judg_transaction_status NG")

        return False

    @decorater_log
    def _find_subnormal(
            self, transaction_id, order_type, device_name, transaction_status,
            connect_device_flg, db_ng_flg):
        '''
        Conduct subnormal operation.  
        Explanation about parameter:
            transaction_id: Transaction ID
            order_type: Order type
            device_name: Device name
            transaction_status: Transaction status
            connect_device_flg: Device connection availability flag (True:Device connection available ,False:Device connection unavailable)
            db_ng_flg: DB connection NG flag (True:DB connection NG, False:except for DB connection NG)
        Explanation about return value:
            None
        '''

        GlobalModule.EM_LOGGER.debug("connect_device_flg:%s",
                                     connect_device_flg)
        GlobalModule.EM_LOGGER.debug("db_ng_flg:%s", db_ng_flg)

        is_db_result, return_table_info = \
            GlobalModule.EMSYSCOMUTILDB.read_transaction_info(transaction_id)

        if is_db_result is False:
            GlobalModule.EM_LOGGER.debug("read_transaction_info NG")
            return

        GlobalModule.EM_LOGGER.debug("read_transaction_info OK")

        service_type_num = return_table_info[0]["service_type"]
        GlobalModule.EM_LOGGER.debug(
            "service_type_num: %s", service_type_num)
        GlobalModule.EM_LOGGER.debug(
            "service_type: %s",
            self.service_type_list[service_type_num])

        if connect_device_flg is True:
            GlobalModule.EM_LOGGER.debug("With device connection")

            is_comdriver_result = self.com_driver_list[
                device_name].disconnect_device(
                    device_name,
                    self.service_type_list[service_type_num],
                    order_type)

            if is_comdriver_result is False:
                GlobalModule.EM_LOGGER.debug("disconnect_device NG")

        if db_ng_flg is False:
            GlobalModule.EM_LOGGER.debug("DB connection other than NG")

            is_db_result = \
                GlobalModule.EMSYSCOMUTILDB. \
                write_transaction_device_status_list(
                    "UPDATE", device_name, transaction_id, transaction_status)

            if is_db_result is False:
                GlobalModule.EM_LOGGER.debug(
                    "write_transaction_device_status_list(NG:%d) NG",
                    transaction_status)
                return

            GlobalModule.EM_LOGGER.debug(
                "write_transaction_device_status_list(NG:%d) OK",
                transaction_status)

            need_update = self._judg_transaction_status(
                return_table_info[0]["transaction_status"])

            if need_update is True:
                GlobalModule.EM_LOGGER.debug("Transaction state update required")

                is_db_result = \
                    GlobalModule.EMSYSCOMUTILDB. \
                    write_transaction_status(
                        "UPDATE",
                        transaction_id,
                        transaction_status,
                        self.service_type_list[service_type_num],
                        order_type,
                        return_table_info[0]["order_text"]
                    )

                if is_db_result is False:
                    GlobalModule.EM_LOGGER.debug(
                        "write_transaction_status(NG:%d) NG",
                        transaction_status)
                    return

                GlobalModule.EM_LOGGER.debug(
                    "write_transaction_status(NG:%d) OK", transaction_status)

        return

    @staticmethod
    @decorater_log
    def _find_xml_node(parent, *tags):
        '''
        Designate XML object and search the tag.  
            Called out when node is created under the parent node which says "At variable section."
        Parameter:
            parent : Parent node object
            *tag : Designate tag name one by one. (tag1, tag2, tag3…)
        Return value
            Child node : Node object
        '''
        tmp = parent
        for tag in tags:
            if tmp.find(tag) is not None:
                tmp = tmp.find(tag)
            else:
                return None
        return tmp
