import threading
import Queue
import copy
from lxml import etree
from EmCommonLog import decorater_log
import GlobalModule


class EmScenario(threading.Thread):

    @decorater_log
    def __init__(self):

        super(EmScenario, self).__init__()

        self.device_name_list = []

        self.device_cond_dict = {}

        self.device_thread_dict = {}

        self.com_driver_list = {}

        self.force = False

        self.ns_internal_lag = \

        self.service_type_list = {1: "l2-slice", 2: "l2-slice",
                                  3: "l3-slice", 4: "l3-slice",
                                  5: "leaf", 6: "spine",
                                  7: "leaf", 8: "spine",
                                  9: "internal-lag", 10: "internal-lag",
                                  11: "ce-lag", 12: "ce-lag",
                                  15: "l2-slice"}

        self.daemon = True
        self.que_events = Queue.Queue(10)
        self.start()

    @decorater_log
    def run(self):
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
        for name in self.device_name_list:
            GlobalModule.EM_LOGGER.debug("Condition acquire notify release")
            device_thread_con = self.device_cond_dict.get(name)
            if device_thread_con is not None:
                device_thread_con.acquire()
                device_thread_con.notify()
                device_thread_con.release()


    @decorater_log
    def __scenario_main(self, ec_message, transaction_id, order_type):


        self.device_name_list, device_xml_dict = self.__analyze_ec_message(
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
    def __analyze_ec_message(self, ec_message):

        device_name_list = []
        device_xml_dict = {}

        ec_edit_message = copy.deepcopy(ec_message)


        for event, element in context:
            GlobalModule.EM_LOGGER.debug(
                "メッセージ分析 event:%s element.tag:%s", event, element.tag)

            if event == "start" and element.tag == self.l2_slice + "l2-slice":
                GlobalModule.EM_LOGGER.debug("l2-sliceサービス")
                slice_name = element.find(self.l2_slice + "name").text
                GlobalModule.EM_LOGGER.debug("service name: %s", slice_name)
                ns_value = self.l2_slice
                device_type = "device-leaf"
                break
            elif event == "start" and \
                    element.tag == self.l3_slice + "l3-slice":
                GlobalModule.EM_LOGGER.debug("l3-sliceサービス")
                slice_name = element.find(self.l3_slice + "name").text
                GlobalModule.EM_LOGGER.debug("service name: %s", slice_name)
                ns_value = self.l3_slice
                device_type = "device-leaf"
                break
            elif event == "start" and element.tag == self.ns_spine + "spine":
                GlobalModule.EM_LOGGER.debug("spineサービス")
                ns_value = self.ns_spine
                device_type = "device"
                break
            elif event == "start" and element.tag == self.ns_leaf + "leaf":
                GlobalModule.EM_LOGGER.debug("leafサービス")
                ns_value = self.ns_leaf
                device_type = "device"
                break
            elif event == "start" and \
                    element.tag == self.ns_internal_lag + "internal-lag":
                GlobalModule.EM_LOGGER.debug("internal-lagサービス")
                ns_value = self.ns_internal_lag
                device_type = "device"
                break
            elif event == "start" and element.tag == self.ns_ce_lag + "ce-lag":
                GlobalModule.EM_LOGGER.debug("ce-lagサービス")
                ns_value = self.ns_ce_lag
                device_type = "device"
                break
            else:
                GlobalModule.EM_LOGGER.debug("サービス種別外TAG")

        GlobalModule.EM_LOGGER.debug("device_type:%s", device_type)

        for event, element in context:

            if event == "end" and \
                    element.tag == ns_value + "force":
                GlobalModule.EM_LOGGER.debug("強制削除フラグ有効")
                self.force = True

            if device_type == "device-leaf":
                if event == "end" and \
                        element.tag == ns_value + "device-leaf":
                    GlobalModule.EM_LOGGER.debug("l2-slice, l3-sliceサービス用")

                    device_tag = ns_value + "name"

                    device_name_list.append(device_name)

                    slice_elm = etree.Element("slice_name")
                    slice_elm.text = slice_name
                    element.append(slice_elm)

                    device_xml_dict[device_name] = etree.tostring(element)
                    GlobalModule.EM_LOGGER.debug(
                        "device_xml_dict: %s", device_xml_dict[device_name])
                    GlobalModule.EM_LOGGER.debug(
                        "device_name_list: %s", device_name_list)

            if device_type == "device":
                if event == "end" and element.tag == ns_value + "device":
                    GlobalModule.EM_LOGGER.debug(
                        "spine, leaf, ce-lag, internal-lagサービス用")

                    device_tag = ns_value + "name"

                    device_name_list.append(device_name)

                    device_xml_dict[device_name] = etree.tostring(element)
                    GlobalModule.EM_LOGGER.debug(
                        "device_xml_dict: %s", device_xml_dict[device_name])
                    GlobalModule.EM_LOGGER.debug(
                        "device_name_list: %s", device_name_list)

        return device_name_list, device_xml_dict

    @decorater_log
    def _gen_sub_thread(
            self, device_message,
            transaction_id, order_type, condition, device_name, force):

        GlobalModule.EM_LOGGER.error(
            "304005 Call SeparateScenario IF:_gen_sub_thread NG")

        return False

    @decorater_log
    def _find_timeout(self, condition):

        GlobalModule.EM_LOGGER.error(
            "304005 Call SeparateScenario IF:_find_timeout NG")

        return False

    @decorater_log
    def _judg_transaction_status(self, transaction_status):

        GlobalModule.EM_LOGGER.error(
            "304005 Call SeparateScenario IF:_judg_transaction_status NG")

        return False

    @decorater_log
    def _find_subnormal(
            self, transaction_id, order_type, device_name, transaction_status,
            connect_device_flg, db_ng_flg):

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
            GlobalModule.EM_LOGGER.debug("装置接続あり")

            is_comdriver_result = self.com_driver_list[
                device_name].disconnect_device(
                    device_name,
                    self.service_type_list[service_type_num],
                    order_type)

            if is_comdriver_result is False:
                GlobalModule.EM_LOGGER.debug("disconnect_device NG")

        if db_ng_flg is False:
            GlobalModule.EM_LOGGER.debug("DB接続NG以外")

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
                GlobalModule.EM_LOGGER.debug("トランザクション状態更新要")

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
        tmp = parent
        for tag in tags:
            if tmp.find(tag) is not None:
                tmp = tmp.find(tag)
            else:
                return None
        return tmp
