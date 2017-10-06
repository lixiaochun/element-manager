# -*- coding: utf-8 -*-
from lxml import etree
import GlobalModule
from EmCommonLog import decorater_log


class EmSysCommonUtilityDB(object):

    class __service(object):
        spine = "spine"
        leaf = "leaf"
        l2_slice = "l2-slice"
        l3_slice = "l3-slice"
        ce_lag = "ce-lag"
        internal_lag = "internal-lag"

    _namespace = {
    }

    class __orders(object):
        delete = "delete"
        get = "get"
        merge = "merge"

    _tran_mang_service = (
        {
            __orders.delete: {
                __service.spine: 8,
                __service.leaf: 7,
                __service.l2_slice: 2,
                __service.l3_slice: 4,
                __service.ce_lag: 12,
                __service.internal_lag: 10
            },
            __orders.get: {
                __service.spine: 15,
                __service.leaf: 15,
                __service.l2_slice: 15,
                __service.l3_slice: 15,
                __service.ce_lag: 15,
                __service.internal_lag: 15
            },
            __orders.merge: {
                __service.spine: 6,
                __service.leaf: 5,
                __service.l2_slice: 1,
                __service.l3_slice: 3,
                __service.ce_lag: 11,
                __service.internal_lag: 9
            }
        }
    )

    _tran_mang_order = {
        __orders.delete: 3,
        __orders.get: 2,
        __orders.merge: 1
    }

    __db_delete = "DELETE"

    @decorater_log
    def __init__(self):
        pass


    @staticmethod
    @decorater_log
    def read_transactionid_list():

        result, data = GlobalModule.DB_CONTROL.read_transactionid_list()
        if result is True:
            if len(data) == 0:
                data = None
            return True, data
        else:
            GlobalModule.EM_LOGGER.warning(
            return False, None

    @staticmethod
    @decorater_log
    def read_transaction_info(transaction_id):
        result, data = GlobalModule.DB_CONTROL.read_transaction_mgmt_info(
            transaction_id)
        if result is True:
            if len(data) == 0:
                data = None
            return True, data
        else:
            GlobalModule.EM_LOGGER.warning(
            return False, None

    @staticmethod
    @decorater_log
    def initialize_order_mgmt_info():
        result = GlobalModule.DB_CONTROL.initialize_order_mgmt_info()
        if result is True:
            return True
        else:
            GlobalModule.EM_LOGGER.warning(
            return False

    @decorater_log
    def write_transaction_status(self,
                                 db_contolorer,
                                 transaction_id,
                                 transaction_status=None,
                                 service_type=None,
                                 order_type=None,
                                 order_text=None):
        order_key = order_type if order_type is not None else self.__orders.get

        tmp_service_type = (
            self._tran_mang_service.get(order_key).get(service_type)
            if self._tran_mang_service.get(order_key) else None)

        tmp_order_type = self._tran_mang_order.get(order_key)

        result = (
            GlobalModule.DB_CONTROL.
            write_transaction_mgmt_info(db_contolorer,
                                        transaction_id,
                                        transaction_status,
                                        tmp_service_type,
                                        tmp_order_type,
                                        order_text)
        )
        if result:
            GlobalModule.EM_LOGGER.debug(
                transaction_id, transaction_status)
        else:
            GlobalModule.EM_LOGGER.warning(
        return result

    @staticmethod
    @decorater_log
    def read_transaction_device_status_list(transaction_id):
        result, data = GlobalModule.DB_CONTROL.read_device_status_mgmt_info(
            transaction_id)
        if result is True:
            if len(data) == 0:
                data = None
            return True, data
        else:
            GlobalModule.EM_LOGGER.warning(
            return False, None

    @staticmethod
    @decorater_log
    def write_transaction_device_status_list(db_contolorer,
                                             device_name,
                                             transaction_id,
                                             transaction_status=None):
        result = GlobalModule.\
            DB_CONTROL.write_device_status_mgmt_info(db_contolorer,
                                                     device_name,
                                                     transaction_id,
                                                     transaction_status)
        if result is True:
                                         device_name, transaction_status)
            return True
        else:
            GlobalModule.EM_LOGGER.warning(
            return False

    @decorater_log
    def write_em_info(self,
                      db_controlorer,
                      device_name,
                      service_type,
                      ec_message,
                      is_write_force=False):
        add_param = []
        if service_type == self.__service.spine:
            set_db_info_function = self.__set_db_function_info_spine
        elif service_type == self.__service.leaf:
            set_db_info_function = self.__set_db_function_info_leaf
        elif service_type == self.__service.l2_slice:
            set_db_info_function = self.__set_db_function_info_l2_slice
            add_param.append(is_write_force)
        elif service_type == self.__service.l3_slice:
            set_db_info_function = self.__set_db_function_info_l3_slice
            add_param.append(is_write_force)
        elif service_type == self.__service.ce_lag:
            set_db_info_function = self.__set_db_function_info_ce_lag
        elif service_type == self.__service.internal_lag:
            set_db_info_function = self.__set_db_function_info_internal_lag
        else:
            GlobalModule.EM_LOGGER.warning(
            return False

        try:
            xml_obj = etree.fromstring(ec_message)
            param_set_db = [xml_obj, db_controlorer, device_name]
            param_set_db.extend(add_param)
            funcs, params = set_db_info_function(*param_set_db)
        except Exception, ex_mes:
            GlobalModule.EM_LOGGER.warning(
            GlobalModule.EM_LOGGER.debug("error_mes = %s" % (ex_mes,))
            return False

        GlobalModule.EM_LOGGER.debug(

        is_ok = GlobalModule.DB_CONTROL.write_simultaneous_table(funcs, params)
        if not is_ok:
            GlobalModule.EM_LOGGER.warning(

        return is_ok

    @staticmethod
    @decorater_log
    def read_separate_driver_info(device_name):
        result, data0 = GlobalModule.DB_CONTROL.read_device_regist_info(
            device_name)
        if result is True:
            if len(data0) == 0:
                return True, None

            data = (platform_name, os, firm_version)

            return True, data
        else:
            GlobalModule.EM_LOGGER.warning(
            return False, None

    @staticmethod
    @decorater_log
    def read_device_registered_info(device_name):
        result, data = GlobalModule.DB_CONTROL.read_device_regist_info(
            device_name)
        if result is True:
            if len(data) == 0:
                data = None
            return True, data
        else:
            GlobalModule.EM_LOGGER.warning(
            return False, None

    @staticmethod
    @decorater_log
    def write_device_status_list(transaction_id):
        result = (GlobalModule.DB_CONTROL.
                  delete_device_status_mgmt_info_linked_tr_id(transaction_id))
        if not result:
            GlobalModule.EM_LOGGER.warning(
        return result

    @staticmethod
    @decorater_log
    def read_em_info(device_name,
                     service_type):

        if service_type == "l3-slice":

            result1, data1 = GlobalModule.DB_CONTROL.read_vrf_detail_info(
                device_name)
            result2, data2 = GlobalModule.DB_CONTROL.read_cp_info(device_name)
            result3, data3 = GlobalModule\
                .DB_CONTROL.read_static_route_detail_info(device_name)
            result4, data4 = GlobalModule\
                .DB_CONTROL.read_bgp_detail_info(device_name)
            result5, data5 = GlobalModule.DB_CONTROL.read_vrrp_detail_info(
                device_name)
            result6, data6 = GlobalModule.DB_CONTROL.read_vrrp_trackif_info(
                device_name)

            if (result1 is True and result2 is True and result3 is True and
                    result4 is True and result5 is True and result6 is True):

                data = (data1, data2, data3, data4, data5, data6)
                data_all =\
                    data1 or data2 or data3 or data4 or data5 or data6
                if len(data_all) == 0:
                    data = None

                return True, data
            else:
                GlobalModule.EM_LOGGER.warning(
                return False, None

        elif service_type == "l2-slice":

            result, data = GlobalModule.DB_CONTROL.read_cp_info(device_name)

            if result is True:

                if len(data) == 0:
                    data = None

                return True, data
            else:
                GlobalModule.EM_LOGGER.warning(
                return False, None

        elif service_type == "spine":

            result1, data1 = GlobalModule\
                .DB_CONTROL.read_device_regist_info(device_name)
            result2, data2 = GlobalModule.DB_CONTROL.read_lagif_info(
                device_name)
            result3, data3 = GlobalModule.DB_CONTROL.read_lagmemberif_info(
                device_name)

            if result1 is True and result2 is True and result3 is True:

                data = (data1, data2, data3)
                data_all = data1 or data2 or data3
                if len(data_all) == 0:
                    data = None
                return True, data
            else:
                GlobalModule.EM_LOGGER.warning(
                return False, None

        elif service_type == "leaf":

            result1, data1 = GlobalModule.DB_CONTROL\
                .read_device_regist_info(device_name)
            result2, data2 = GlobalModule.DB_CONTROL.read_lagif_info(
                device_name)
            result3, data3 = GlobalModule.DB_CONTROL.read_lagmemberif_info(
                device_name)
            result4, data4 = GlobalModule.DB_CONTROL\
                .read_l3vpn_leaf_bgp_basic_info(device_name)

            if result1 is True and result2 is True and result3 is True\
                    and result4 is True:

                data = (data1, data2, data3, data4)
                data_all = data1 or data2 or data3 or data4
                if len(data_all) == 0:
                    data = None

                return True, data
            else:
                GlobalModule.EM_LOGGER.warning(
                return False, None

        elif service_type == "ce-lag":

            result1, data1 = GlobalModule.DB_CONTROL.read_lagif_info(
                device_name)
            result2, data2 = GlobalModule.DB_CONTROL.read_lagmemberif_info(
                device_name)

            if result1 is True and result2 is True:

                data = (data1, data2)
                data_all = data1 or data2
                if len(data_all) == 0:
                    data = None

                return True, data
            else:
                GlobalModule.EM_LOGGER.warning(
                return False, None

        elif service_type == "internal-lag":

            result1, data1 = GlobalModule.DB_CONTROL.read_lagif_info(
                device_name)
            result2, data2 = GlobalModule.DB_CONTROL.read_lagmemberif_info(
                device_name)
            result3, data3 = GlobalModule.DB_CONTROL\
                .read_device_regist_info(device_name)

            if result1 is True and result2 is True and result3 is True:

                data = (data1, data2, data3)
                data_all = data1 or data2 or data3
                if len(data_all) == 0:
                    data = None
                return True, data
            else:
                GlobalModule.EM_LOGGER.warning(
                return False, None

        else:
            return False, None


    @decorater_log
    def __set_db_function_info_spine(self, ec_mes, db_control, device_name):
        func_list = []
        param_list = []

        service = self.__service.spine

        tmp_func, tmp_param = (
            self.__get_func_device_regist_info(ec_mes, db_control, service))
        func_list.extend(tmp_func)
        param_list.extend(tmp_param)

        if db_control == self.__db_delete:
            tmp_func, tmp_param = self.__get_func_all_del_lag(ec_mes, service)
        else:
            tmp_func, tmp_param = (
                self.__get_func_lagif_info(
                    ec_mes, db_control, self.__service.internal_lag, service))
        func_list.extend(tmp_func)
        param_list.extend(tmp_param)

        if db_control == self.__db_delete:
            func_list.reverse()
            param_list.reverse()

        return func_list, param_list

    @decorater_log
    def __set_db_function_info_leaf(self, ec_mes, db_control, device_name):
        func_list = []
        param_list = []

        service = self.__service.leaf

        tmp_func, tmp_param = (
            self.__get_func_device_regist_info(ec_mes, db_control, service))
        func_list.extend(tmp_func)
        param_list.extend(tmp_param)

        if db_control == self.__db_delete:
            tmp_func, tmp_param = self.__get_func_all_del_lag(ec_mes, service)
        else:
            tmp_func, tmp_param = (
                self.__get_func_lagif_info(
                    ec_mes, db_control, self.__service.internal_lag, service))
        func_list.extend(tmp_func)
        param_list.extend(tmp_param)

        tmp_func, tmp_param = (
            self.__get_func_l3vpn_leaf_bgp_basic_info(ec_mes,
                                                      db_control,
                                                      service))
        func_list.extend(tmp_func)
        param_list.extend(tmp_param)

        if db_control == self.__db_delete:
            func_list.reverse()
            param_list.reverse()

        return func_list, param_list

    @decorater_log
    def __set_db_function_info_l2_slice(self,
                                        ec_mes,
                                        db_control,
                                        device_name,
                                        is_write_force=False):
        func_list = []
        param_list = []

        service = self.__service.l2_slice

        if db_control == self.__db_delete:
            tmp_func, tmp_param = (
                self.__get_func_l2_del(ec_mes,  service, is_write_force))
        else:
            tmp_func, tmp_param = (
                self.__get_func_cp_info(ec_mes, db_control, service))
        func_list.extend(tmp_func)
        param_list.extend(tmp_param)

        if db_control == self.__db_delete:
            func_list.reverse()
            param_list.reverse()

        return func_list, param_list

    @decorater_log
    def __set_db_function_info_l3_slice(self,
                                        ec_mes,
                                        db_control,
                                        device_name,
                                        is_write_force=False):
        func_list = []
        param_list = []

        service = self.__service.l3_slice

        if db_control == self.__db_delete:
            tmp_func, tmp_param = (
                self.__get_func_l3_del(ec_mes, service, is_write_force))
        else:
            tmp_func, tmp_param = (
                self.__get_func_cp_info(ec_mes, db_control, service))
        func_list.extend(tmp_func)
        param_list.extend(tmp_param)

        if db_control == self.__db_delete:
            func_list.reverse()
            param_list.reverse()

        return func_list, param_list

    @decorater_log
    def __set_db_function_info_ce_lag(self,
                                      ec_mes,
                                      db_control,
                                      device_name):
        func_list = []
        param_list = []

        service = self.__service.ce_lag

        tmp_func, tmp_param = (
            self.__get_func_lagif_info(ec_mes, db_control, service, service))
        func_list.extend(tmp_func)
        param_list.extend(tmp_param)

        if db_control == self.__db_delete:
            func_list.reverse()
            param_list.reverse()

        return func_list, param_list

    @decorater_log
    def __set_db_function_info_internal_lag(self,
                                            ec_mes,
                                            db_control,
                                            device_name):
        func_list = []
        param_list = []

        service = self.__service.internal_lag
        db_vpn_type = {"l2": 2,
                       "l3": 3}

        leaf_device_type = 2

        tmp_func, tmp_param = (
            self.__get_func_lagif_info(ec_mes, db_control, service, service))
        func_list.extend(tmp_func)
        param_list.extend(tmp_param)

        ok, dev_regist = (
            GlobalModule.DB_CONTROL.read_device_regist_info(device_name))
        if not (ok and len(dev_regist) > 0):
            raise ValueError(
                "failed get to dev_regist_info at %s" % (device_name,))
        if (db_control != self.__db_delete and
                dev_regist[0].get("device_type") == leaf_device_type):
            name_s = "{%s}" % (self._namespace.get(service),)
            tmp_reg = dev_regist[0].copy()
            if ec_mes.find(name_s + "vpn-type") is not None:
                vpn_type = ec_mes.find(name_s + "vpn-type").text.lower()
                tmp_reg["vpn_type"] = db_vpn_type[vpn_type]
                tmp_reg["db_control"] = "UPDATE"
                func_list.append(
                    GlobalModule.DB_CONTROL.write_device_regist_info)
                param_list.append(tmp_reg)

        if db_control == self.__db_delete:
            func_list.reverse()
            param_list.reverse()

        return func_list, param_list

    @decorater_log
    def __get_param(self, node, tag, val_class):
        return_val = None
        if node is not None:
            node_tag = node.find(tag)
            if node_tag is not None:
                return_val = self.__parse(node_tag.text, val_class)
        return return_val

    @staticmethod
    @decorater_log
    def __parse(value, val_class):
        return_val = None
        if value is not None:
            try:
                return_val = val_class(value)
            except ValueError:
                raise
        return return_val

    @decorater_log
    def __get_func_device_regist_info(self, dev_node, db_control, dev_type):
        name_s = "{%s}" % (self._namespace.get(dev_type),)

        regist_param = dict.fromkeys(["db_control",
                                      "device_name",
                                      "device_type",
                                      "platform_name",
                                      "os",
                                      "firm_version",
                                      "username",
                                      "password",
                                      "mgmt_if_address",
                                      "mgmt_if_prefix",
                                      "loopback_if_address",
                                      "loopback_if_prefix",
                                      "snmp_server_address",
                                      "snmp_community",
                                      "ntp_server_address",
                                      "msdp_peer_address",
                                      "msdp_local_address",
                                      "as_number",
                                      "pim_other_rp_address",
                                      "pim_self_rp_address",
                                      "pim_rp_address",
                                      "vpn_type"])
        db_dev_type = {self.__service.spine: 1, self.__service.leaf: 2}

        func_list = []
        param_list = []

        regist_param["db_control"] = db_control

        regist_param["device_type"] = db_dev_type.get(dev_type)

        regist_param["device_name"] = self.__get_param(
            dev_node, name_s + "name", str)

        node_1 = dev_node.find(name_s + "equipment")
        regist_param["platform_name"] = (
            self.__get_param(node_1, name_s + "platform", str))
        regist_param["os"] = (
            self.__get_param(node_1, name_s + "os", str))
        regist_param["firm_version"] = (
            self.__get_param(node_1, name_s + "firmware", str))
        regist_param["username"] = (
            self.__get_param(node_1, name_s + "loginid", str))
        regist_param["password"] = (
            self.__get_param(node_1, name_s + "password", str))

        node_1 = dev_node.find(name_s + "management-interface")
        regist_param["mgmt_if_address"] = (
            self.__get_param(node_1, name_s + "address", str))
        regist_param["mgmt_if_prefix"] = (
            self.__get_param(node_1, name_s + "prefix", str))

        node_1 = dev_node.find(name_s + "loopback-interface")
        regist_param["loopback_if_address"] = (
            self.__get_param(node_1, name_s + "address", str))
        regist_param["loopback_if_prefix"] = (
            self.__get_param(node_1, name_s + "prefix", str))

        node_1 = dev_node.find(name_s + "snmp")
        regist_param["snmp_server_address"] = (
            self.__get_param(node_1, name_s + "server-address", str))
        regist_param["snmp_community"] = (
            self.__get_param(node_1, name_s + "community", str))

        node_1 = dev_node.find(name_s + "ntp")
        regist_param["ntp_server_address"] = (
            self.__get_param(node_1, name_s + "server-address", str))

        if dev_node.find(name_s + "msdp") is not None:
            node_1 = dev_node.find(
                name_s + "msdp").find(name_s + "peer")
            regist_param["msdp_peer_address"] = (
                self.__get_param(node_1, name_s + "address", str))
            regist_param["msdp_local_address"] = (
                self.__get_param(node_1, name_s + "local-address", str))

        if dev_node.find(name_s + "l3-vpn") is not None:
            node_1 = dev_node.find(name_s + "l3-vpn").find(name_s + "as")
            regist_param["as_number"] = (
                self.__get_param(node_1, name_s + "as-number", int))

        if dev_node.find(name_s + "l2-vpn") is not None:
            node_1 = dev_node.find(name_s + "l2-vpn").find(name_s + "pim")
            regist_param["pim_other_rp_address"] = (
                self.__get_param(node_1, name_s + "other-rp-address", str))
            regist_param["pim_self_rp_address"] = (
                self.__get_param(node_1, name_s + "self-rp-address", str))
            regist_param["pim_rp_address"] = (
                self.__get_param(node_1, name_s + "rp-address", str))

        func_list.append(GlobalModule.DB_CONTROL.write_device_regist_info)
        param_list.append(regist_param)
        return func_list, param_list

    @decorater_log
    def __get_func_lagif_info(self, dev_node, db_control, lag_type, service):
        name_s = "{%s}" % (self._namespace.get(service),)

        db_lag_type = {self.__service.ce_lag: 2,
                       self.__service.internal_lag: 1}
        lag_if_node_tag = {self.__service.ce_lag: "ce-lag-interface",
                           self.__service.internal_lag:
                           "internal-lag-interface"}
        lag_mem_node_tag = {self.__service.ce_lag: "leaf-interface",
                            self.__service.internal_lag: "internal-interface"}

        func_list = []
        param_list = []

        device_name = self.__get_param(dev_node, name_s + "name", str)

        if_counts = {}
        if db_control == self.__db_delete and \
                service == self.__service.internal_lag:
            is_ok, db_lag_mem = \
                GlobalModule.DB_CONTROL.read_lagmemberif_info(device_name)
            if not is_ok:
                           (device_name,))
                GlobalModule.EM_LOGGER.debug(err_mes)
                raise ValueError("DB Control ERROR")
            for lag_mem in db_lag_mem:
                if lag_mem["lag_if_name"] in if_counts:
                    if_counts[lag_mem["lag_if_name"]] += 1
                else:
                    if_counts[lag_mem["lag_if_name"]] = 1

        lag_if_nodes = dev_node.findall(name_s +
                                        lag_if_node_tag.get(
                                            lag_type, "none-interface"))
        for lag_if_node in lag_if_nodes:
            lagif_param = dict.fromkeys(["db_control",
                                         "device_name",
                                         "lag_if_name",
                                         "lag_type",
                                         "minimum_links",
                                         "link_speed",
                                         "internal_link_ip_address"])
            lagif_param["db_control"] = db_control
            lagif_param["device_name"] = device_name
            lag_if_name = self.__get_param(lag_if_node, name_s + "name", str)
            lagif_param["lag_if_name"] = lag_if_name
            lagif_param["lag_type"] = db_lag_type.get(lag_type)
            lagif_param["minimum_links"] = (
                self.__get_param(lag_if_node, name_s + "minimum-links", int))
            lagif_param["link_speed"] = (
                self.__get_param(lag_if_node, name_s + "link-speed", str))
            lagif_param["internal_link_ip_address"] = (
                self.__get_param(lag_if_node, name_s + "address", str))
            lagif_param["internal_link_ip_prefix"] = (
                self.__get_param(lag_if_node, name_s + "prefix", str))

            if_nodes = lag_if_node.findall(name_s +
                                           lag_mem_node_tag.get(
                                               lag_type, "none-interface"))

            if db_control != self.__db_delete and len(if_nodes) == 0:
                           (lag_if_name,))
                GlobalModule.EM_LOGGER.debug(err_mes)
                raise ValueError("Interface node do not find")

            if (db_control != self.__db_delete or
                    if_nodes[0].text is None or
                    len(if_nodes) == if_counts.get(lag_if_name)):
                func_list.append(
                    GlobalModule.DB_CONTROL.write_lagif_info)
                param_list.append(lagif_param)

            for if_node in if_nodes:
                lagmemberif_param = dict.fromkeys(["db_control",
                                                   "lag_if_name",
                                                   "if_name",
                                                   "device_name"])
                lagmemberif_param["db_control"] = db_control
                lagmemberif_param["device_name"] = device_name
                lagmemberif_param["lag_if_name"] = lag_if_name
                lagmemberif_param["if_name"] = (
                    self.__get_param(if_node, name_s + "name", str))
                func_list.append(
                    GlobalModule.DB_CONTROL.write_lagmemberif_info)
                param_list.append(lagmemberif_param)

        return func_list, param_list

    @decorater_log
    def __get_func_l3vpn_leaf_bgp_basic_info(self,
                                             dev_node,
                                             db_control,
                                             service):
        name_s = "{%s}" % (self._namespace.get(service),)

        func_list = []
        param_list = []

        device_name = self.__get_param(dev_node, name_s + "name", str)

        if ((dev_node.find(name_s + "l3-vpn") is not None) and
                (dev_node.find(name_s + "l3-vpn").find(name_s + "bgp")
                 is not None)):
            node_1 = dev_node.find(name_s + "l3-vpn").find(name_s + "bgp")
            community = self.__get_param(node_1, name_s + "community", str)
            wildcard = self.__get_param(
                node_1, name_s + "community-wildcard", str)
            neighbor_nodes = node_1.findall(name_s + "neighbor")
            for neighbor_node in neighbor_nodes:
                l3vpn_param = dict.fromkeys(["db_control",
                                             "device_name",
                                             "neighbor_ipv4",
                                             "bgp_community_value",
                                             "bgp_community_wildcard"])
                l3vpn_param["db_control"] = db_control
                l3vpn_param["device_name"] = device_name
                l3vpn_param["neighbor_ipv4"] = (
                    self.__get_param(neighbor_node, name_s + "address", str))
                l3vpn_param["bgp_community_value"] = community
                l3vpn_param["bgp_community_wildcard"] = wildcard
                func_list.append(
                    GlobalModule.DB_CONTROL.write_l3vpn_leaf_bgp_basic_info)
                param_list.append(l3vpn_param)
        elif (dev_node.find(name_s + "l3-vpn") is None and
              db_control == self.__db_delete):
            l3vpn_param = dict.fromkeys(["db_control",
                                         "device_name",
                                         "neighbor_ipv4",
                                         "bgp_community_value",
                                         "bgp_community_wildcard"])
            l3vpn_param["db_control"] = db_control
            l3vpn_param["device_name"] = device_name
            func_list.append(
                GlobalModule.DB_CONTROL.write_l3vpn_leaf_bgp_basic_info)
            param_list.append(l3vpn_param)

        return func_list, param_list

    @decorater_log
    def __get_func_cp_info(self,
                           dev_node,
                           db_control,
                           slice_type):
        name_s = "{%s}" % (self._namespace.get(slice_type),)

        db_slice_type = {self.__service.l2_slice: 2,
                         self.__service.l3_slice: 3}

        db_port_mode = {"access": 1, "trunk": 2}

        func_list = []
        param_list = []

        device_name = self.__get_param(dev_node, name_s + "name", str)

        slice_name = self.__get_param(dev_node, name_s + "slice_name", str)

        if slice_type == self.__service.l3_slice:
            tmp_node = dev_node.find(name_s + "vrf")
            vrf_name = self.__get_param(tmp_node, name_s + "vrf-name", str)
            vrf_rt = self.__get_param(tmp_node, name_s + "rt", str)
            vrf_rd = self.__get_param(tmp_node, name_s + "rd", str)
            vrf_route_id = (
                self.__get_param(tmp_node, name_s + "router-id", str))

        for cp_node in dev_node.findall(name_s + "cp"):
            cp_param = dict.fromkeys(["db_control",
                                      "device_name",
                                      "if_name",
                                      "vlan_id",
                                      "slice_name",
                                      "slice_type",
                                      "port_mode",
                                      "vni",
                                      "multicast_group",
                                      "ipv4_address",
                                      "ipv4_prefix",
                                      "ipv6_address",
                                      "ipv6_prefix",
                                      "bgp_flag",
                                      "ospf_flag",
                                      "static_flag",
                                      "direct_flag",
                                      "vrrp_flag",
                                      "mtu_size",
                                      "metric"])
            tmp_func_list = []
            tmp_param_list = []
            cp_param["db_control"] = db_control
            cp_param["device_name"] = device_name
            cp_param["slice_name"] = slice_name
            cp_param["slice_type"] = db_slice_type.get(slice_type)
            cp_param["if_name"] = (
                self.__get_param(cp_node, name_s + "name", str))
            cp_param["vlan_id"] = (
                self.__get_param(cp_node, name_s + "vlan-id", int))
            tmp = self.__get_param(cp_node, name_s + "port-mode", str)
            cp_param["port_mode"] = (
                db_port_mode.get(tmp.lower()) if tmp else None)

            if slice_type == self.__service.l2_slice:
                cp_param["vni"] = self.__get_param(
                    cp_node, name_s + "vni", int)
                cp_param["multicast_group"] = (
                    self.__get_param(cp_node, name_s + "multicast-group", str))

            if slice_type == self.__service.l3_slice:
                vrf_param = dict.fromkeys(["db_control",
                                           "device_name",
                                           "if_name",
                                           "vlan_id",
                                           "slice_name",
                                           "vrf_name",
                                           "rt",
                                           "rd",
                                           "router_id"])
                vrf_param["db_control"] = db_control
                vrf_param["device_name"] = device_name
                vrf_param["slice_name"] = slice_name
                vrf_param["if_name"] = cp_param["if_name"]
                vrf_param["vlan_id"] = cp_param["vlan_id"]
                vrf_param["vrf_name"] = vrf_name
                vrf_param["rt"] = vrf_rt
                vrf_param["rd"] = vrf_rd
                vrf_param["router_id"] = vrf_route_id
                tmp_func_list.append(
                    GlobalModule.DB_CONTROL.write_vrf_detail_info)
                tmp_param_list.append(vrf_param)

                tmp_node = cp_node.find(name_s + "ce-interface")
                cp_param["ipv4_address"] = (
                    self.__get_param(tmp_node, name_s + "address", str))
                cp_param["ipv4_prefix"] = (
                    self.__get_param(tmp_node, name_s + "prefix", int))
                cp_param["ipv6_address"] = (
                    self.__get_param(tmp_node, name_s + "address6", str))
                cp_param["ipv6_prefix"] = (
                    self.__get_param(tmp_node, name_s + "prefix6", int))
                cp_param["mtu_size"] = self.__get_param(
                    tmp_node, name_s + "mtu", int)

                cp_param["ospf_flag"] = False
                if cp_node.find(name_s + "ospf") is not None:
                    cp_param["ospf_flag"] = True
                    cp_param["metric"] = (
                        self.__get_param(cp_node.find(name_s + "ospf"),
                                         name_s + "metric", int))

                cp_param["vrrp_flag"] = False
                if cp_node.find(name_s + "vrrp")is not None:
                    cp_param["vrrp_flag"] = True
                    self.__set_vrrp_param(tmp_func_list,
                                          tmp_param_list,
                                          cp_node.find(name_s + "vrrp"),
                                          name_s,
                                          db_control,
                                          device_name,
                                          slice_name,
                                          cp_param["if_name"],
                                          cp_param["vlan_id"])

                cp_param["bgp_flag"] = False
                if cp_node.find(name_s + "bgp") is not None:
                    cp_param["bgp_flag"] = True
                    self.__set_bgp_param(tmp_func_list,
                                         tmp_param_list,
                                         cp_node.find(name_s + "bgp"),
                                         name_s,
                                         db_control,
                                         device_name,
                                         slice_name,
                                         cp_param["if_name"],
                                         cp_param["vlan_id"])

                cp_param["static_flag"] = False
                if cp_node.find(name_s + "static") is not None:
                    cp_param["static_flag"] = True
                    self.__set_static_param(tmp_func_list,
                                            tmp_param_list,
                                            cp_node.find(name_s + "static"),
                                            name_s,
                                            db_control,
                                            device_name,
                                            slice_name,
                                            cp_param["if_name"],
                                            cp_param["vlan_id"])

                cp_param["direct_flag"] = (not cp_param["ospf_flag"] and
                                           not cp_param["vrrp_flag"] and
                                           not cp_param["bgp_flag"] and
                                           not cp_param["static_flag"])
            func_list.append(
                GlobalModule.DB_CONTROL.write_cp_info)
            param_list.append(cp_param)
            func_list.extend(tmp_func_list)
            param_list.extend(tmp_param_list)

        return func_list, param_list

    @decorater_log
    def __get_func_l2_del(self,
                          dev_node,
                          slice_type,
                          is_write_force=False):
        name_s = "{%s}" % (self._namespace.get(slice_type),)

        db_control = self.__db_delete

        func_list = []
        param_list = []

        device_name = self.__get_param(dev_node, name_s + "name", str)

        slice_name = self.__get_param(dev_node, name_s + "slice_name", str)

        ok, db_cp_info = GlobalModule.DB_CONTROL.read_cp_info(device_name)
        if not ok:
                       (device_name,))
            GlobalModule.EM_LOGGER.debug(err_mes)
            raise ValueError("DB Control ERROR")

        if is_write_force and (db_cp_info is None or len(db_cp_info) <= 0):
                       (device_name, db_cp_info))
            GlobalModule.EM_LOGGER.debug(err_mes)
            raise ValueError("CP COUNT ZERO ERROR")

        for cp_node in dev_node.findall(name_s + "cp"):
            if_name = self.__get_param(cp_node, name_s + "name", str)
            vlan_id = self.__get_param(cp_node, name_s + "vlan-id", int)
            cp_param = self.__get_key_recode(db_cp_info,
                                             device_name=device_name,
                                             if_name=if_name,
                                             vlan_id=vlan_id,
                                             slice_name=slice_name)
            if cp_param is None:
                GlobalModule.EM_LOGGER.debug(
                    (device_name, if_name, vlan_id, slice_name)
                )
                raise ValueError("DB UNKNOWN CP DELETE OPERATION ERROR")
            cp_param["db_control"] = db_control
            func_list.append(
                GlobalModule.DB_CONTROL.write_cp_info)
            param_list.append(cp_param)

        return func_list, param_list

    @decorater_log
    def __get_func_l3_del(self,
                          dev_node,
                          slice_type,
                          is_write_force=False):
        name_s = "{%s}" % (self._namespace.get(slice_type),)

        db_control = self.__db_delete

        key_ope = "operation"
        val_del = "delete"

        func_list = []
        param_list = []

        device_name = self.__get_param(dev_node, name_s + "name", str)

        slice_name = self.__get_param(dev_node, name_s + "slice_name", str)

        ok, db_cp_info = GlobalModule.DB_CONTROL.read_cp_info(device_name)
        if not ok:
            GlobalModule.EM_LOGGER.debug(
            raise ValueError("DB Control (CPINFO) ERROR")
        ok, db_vrrp = GlobalModule.DB_CONTROL.read_vrrp_detail_info(
            device_name)
        if not ok:
            GlobalModule.EM_LOGGER.debug(
                (device_name,))
            raise ValueError("DB Control (VRRP_DETAIL) ERROR")
        ok, db_static = \
            GlobalModule.DB_CONTROL.read_static_route_detail_info(device_name)
        if not ok:
            GlobalModule.EM_LOGGER.debug(
                (device_name,))
            raise ValueError("DB Control (STATIC_DETAIL) ERROR")

        if is_write_force and (db_cp_info is None or len(db_cp_info) <= 0):
                       (device_name, db_cp_info))
            GlobalModule.EM_LOGGER.debug(err_mes)
            raise ValueError("CP COUNT ZERO ERROR")

        cp_del_count = cp_count = 0
        for row in db_cp_info:
            cp_count += 1 if row.get("slice_name") == slice_name else 0

        static_db_counts = {}
        for row in db_static:
            if row.get("slice_name") != slice_name:
                continue
            tmp_key = (row.get("if_name"), row.get("vlan_id"))
            if tmp_key in static_db_counts:
                static_db_counts[tmp_key] += 1
            else:
                static_db_counts[tmp_key] = 1

        for cp_node in dev_node.findall(name_s + "cp"):
            tmp_func_list = []
            tmp_param_list = []
            is_cp_del = False
            if_name = self.__get_param(cp_node, name_s + "name", str)
            vlan_id = self.__get_param(cp_node, name_s + "vlan-id", int)
            if cp_node.get(key_ope) == val_del:
                is_cp_del = True
                cp_del_count += 1
            cp_param = self.__get_key_recode(db_cp_info,
                                             device_name=device_name,
                                             if_name=if_name,
                                             vlan_id=vlan_id,
                                             slice_name=slice_name)
            if cp_param is None:
                GlobalModule.EM_LOGGER.debug(
                    (device_name, if_name, vlan_id, slice_name)
                )
                raise ValueError
            cp_param["db_control"] = (self.__db_delete
                                      if is_cp_del else "UPDATE")
            if is_cp_del or cp_node.find(name_s + "ospf") is not None:
                cp_param["ospf_flag"] = False
                cp_param["metric"] = None
            if is_cp_del or cp_node.find(name_s + "bgp") is not None:
                cp_param["bgp_flag"] = False
                self.__set_bgp_param(tmp_func_list,
                                     tmp_param_list,
                                     cp_node.find(name_s + "bgp"),
                                     name_s,
                                     db_control,
                                     device_name,
                                     slice_name,
                                     if_name,
                                     vlan_id)
            if is_cp_del or cp_node.find(name_s + "static") is not None:
                if is_cp_del:
                    cp_param["static_flag"] = False
                    sr_param = dict.fromkeys(["db_control",
                                              "device_name",
                                              "if_name",
                                              "vlan_id",
                                              "slice_name",
                                              "address_type",
                                              "address",
                                              "prefix",
                                              "nexthop"])
                    sr_param["db_control"] = db_control
                    sr_param["device_name"] = device_name
                    sr_param["slice_name"] = slice_name
                    sr_param["if_name"] = if_name
                    sr_param["vlan_id"] = vlan_id
                    tmp_func_list.append(GlobalModule.DB_CONTROL.
                                         write_static_route_detail_info)
                    tmp_param_list.append(sr_param)
                else:
                    route_nodes = cp_node.find(name_s + "static")
                    tmp_count = 0
                    for route_node in route_nodes:
                        if route_node.get("operation") == "delete":
                            tmp_count += 1
                    if static_db_counts[(if_name, vlan_id)] == tmp_count:
                        cp_param["static_flag"] = False

                    self.__set_static_param(tmp_func_list,
                                            tmp_param_list,
                                            route_nodes,
                                            name_s,
                                            db_control,
                                            device_name,
                                            slice_name,
                                            if_name,
                                            vlan_id)

            if is_cp_del or cp_node.find(name_s + "vrrp") is not None:
                cp_param["vrrp_flag"] = False
                self.__set_vrrp_param(tmp_func_list,
                                      tmp_param_list,
                                      cp_node.find(name_s + "vrrp"),
                                      name_s,
                                      db_control,
                                      device_name,
                                      slice_name,
                                      if_name,
                                      vlan_id)
                vrrp_row = self.__get_key_recode(db_vrrp,
                                                 device_name=device_name,
                                                 if_name=if_name,
                                                 vlan_id=vlan_id,
                                                 slice_name=slice_name)
                if vrrp_row is not None:
                    tr_param = dict.fromkeys(["db_control",
                                              "vrrp_group_id",
                                              "track_if_name"])
                    tr_param["db_control"] = db_control
                    tr_param["vrrp_group_id"] = vrrp_row.get("vrrp_group_id")
                    if tr_param not in tmp_param_list:
                        tmp_func_list.append(GlobalModule.DB_CONTROL.
                                             write_vrrp_trackif_info)
                        tmp_param_list.append(tr_param)

            if is_cp_del:
                vrf_param = dict.fromkeys(["db_control",
                                           "device_name",
                                           "if_name",
                                           "vlan_id",
                                           "slice_name",
                                           "vrf_name",
                                           "rt",
                                           "rd",
                                           "router_id"])
                vrf_param["db_control"] = db_control
                vrf_param["device_name"] = device_name
                vrf_param["slice_name"] = slice_name
                vrf_param["if_name"] = if_name
                vrf_param["vlan_id"] = vlan_id
                tmp_func_list.append(
                    GlobalModule.DB_CONTROL.write_vrf_detail_info)
                tmp_param_list.append(vrf_param)

            cp_param["direct_flag"] = (not cp_param["ospf_flag"] and
                                       not cp_param["vrrp_flag"] and
                                       not cp_param["bgp_flag"] and
                                       not cp_param["static_flag"])
            func_list.append(
                GlobalModule.DB_CONTROL.write_cp_info)
            param_list.append(cp_param)
            func_list.extend(tmp_func_list)
            param_list.extend(tmp_param_list)

        return func_list, param_list

    @decorater_log
    def __set_bgp_param(self,
                        func_list,
                        param_list,
                        bgp_node,
                        name_s,
                        db_control,
                        device_name,
                        slice_name,
                        if_name,
                        vlan_id):
        tmp_node = bgp_node
        bgp_param = dict.fromkeys(["db_control",
                                   "device_name",
                                   "if_name",
                                   "vlan_id",
                                   "slice_name",
                                   "remote_as_number",
                                   "local_ipv4_address",
                                   "remote_ipv4_address",
                                   "local_ipv6_address",
                                   "remote_ipv6_address"])
        bgp_param["db_control"] = db_control
        bgp_param["device_name"] = device_name
        bgp_param["slice_name"] = slice_name
        bgp_param["if_name"] = if_name
        bgp_param["vlan_id"] = vlan_id
        if db_control != self.__db_delete and bgp_node is not None:
            bgp_param["remote_as_number"] = (
                self.__get_param(tmp_node,
                                 name_s + "remote-as-number", int))
            bgp_param["local_ipv4_address"] = (
                self.__get_param(tmp_node,
                                 name_s + "local-address", str))
            bgp_param["remote_ipv4_address"] = (
                self.__get_param(tmp_node,
                                 name_s + "remote-address", str))
            bgp_param["local_ipv6_address"] = (
                self.__get_param(tmp_node,
                                 name_s + "local-address6", str))
            bgp_param["remote_ipv6_address"] = (
                self.__get_param(tmp_node,
                                 name_s + "remote-address6", str))
        func_list.append(GlobalModule.DB_CONTROL.
                         write_bgp_detail_info)
        param_list.append(bgp_param)

    @decorater_log
    def __set_static_param(self,
                           func_list,
                           param_list,
                           static_node,
                           name_s,
                           db_control,
                           device_name,
                           slice_name,
                           if_name,
                           vlan_id):
        tmp_node = static_node
        route_nodes = []
        route_nodes.extend(
            tmp_node.findall(name_s + "route")
            if tmp_node.find(name_s + "route") is not None else []
        )
        route_nodes.extend(
            tmp_node.findall(name_s + "route6")
            if tmp_node.find(name_s + "route6") is not None else []
        )
        for route_node in route_nodes:
            if (db_control == self.__db_delete and
                    route_node.get("operation") != "delete"):
                continue

            sr_param = dict.fromkeys(["db_control",
                                      "device_name",
                                      "if_name",
                                      "vlan_id",
                                      "slice_name",
                                      "address_type",
                                      "address",
                                      "prefix",
                                      "nexthop"])
            sr_param["db_control"] = db_control
            sr_param["device_name"] = device_name
            sr_param["slice_name"] = slice_name
            sr_param["if_name"] = if_name
            sr_param["vlan_id"] = vlan_id
            if route_node.tag == (name_s + "route6"):
                sr_param["address_type"] = 6
            else:
                sr_param["address_type"] = 4
            sr_param["address"] = self.__get_param(route_node,
                                                   name_s +
                                                   "address",
                                                   str)
            sr_param["prefix"] = self.__get_param(route_node,
                                                  name_s +
                                                  "prefix",
                                                  int)
            sr_param["nexthop"] = self.__get_param(route_node,
                                                   name_s +
                                                   "next-hop",
                                                   str)
            func_list.append(GlobalModule.DB_CONTROL.
                             write_static_route_detail_info)
            param_list.append(sr_param)

    @decorater_log
    def __set_vrrp_param(self,
                         func_list,
                         param_list,
                         vrrp_node,
                         name_s,
                         db_control,
                         device_name,
                         slice_name,
                         if_name,
                         vlan_id):
        tmp_node = vrrp_node
        vrrp_param = dict.fromkeys(["db_control",
                                    "device_name",
                                    "if_name",
                                    "vlan_id",
                                    "slice_name",
                                    "vrrp_group_id",
                                    "virtual_ipv4_address",
                                    "virtual_ipv6_address",
                                    "priority"])
        vrrp_param["db_control"] = db_control
        vrrp_param["device_name"] = device_name
        vrrp_param["slice_name"] = slice_name
        vrrp_param["if_name"] = if_name
        vrrp_param["vlan_id"] = vlan_id
        if db_control != self.__db_delete and vrrp_node is not None:
            vrrp_group_id = (
                self.__get_param(tmp_node, name_s + "group-id", int))
            vrrp_param["vrrp_group_id"] = vrrp_group_id
            vrrp_param["virtual_ipv4_address"] = (
                self.__get_param(tmp_node,
                                 name_s + "virtual-address", str))
            vrrp_param["virtual_ipv6_address"] = (
                self.__get_param(tmp_node,
                                 name_s + "virtual-address6", str))
            vrrp_param["priority"] = (
                self.__get_param(tmp_node, name_s + "priority", int))
        func_list.append(
            GlobalModule.DB_CONTROL.write_vrrp_detail_info)
        param_list.append(vrrp_param)
        if (db_control != self.__db_delete and vrrp_node is not None and
                tmp_node.find(name_s + "track") is not None):
            for track in (tmp_node.find(name_s + "track")
                          .findall(name_s + "interface")):
                tr_param = dict.fromkeys(["db_control",
                                          "vrrp_group_id",
                                          "track_if_name"])
                tr_param["db_control"] = db_control
                tr_param["vrrp_group_id"] = vrrp_group_id
                tr_param["track_if_name"] = (
                    self.__get_param(track, name_s + "name", str))
                if tr_param not in param_list:
                    func_list.append(GlobalModule.DB_CONTROL.
                                     write_vrrp_trackif_info)
                    param_list.append(tr_param)

    @staticmethod
    @decorater_log
    def __get_key_recode(db_rows, **keyvalues):
        return_row = None
        for row in db_rows:
            tmp_row = row.copy()
            tmp_row.update(keyvalues)
            if row == tmp_row:
                return_row = tmp_row
                break
        return return_row

    @decorater_log
    def __get_func_all_del_lag(self, dev_node, service):

        name_s = "{%s}" % (self._namespace.get(service),)
        func_list = []
        param_list = []
        device_name = self.__get_param(dev_node, name_s + "name", str)

        lagif_param = dict.fromkeys(["db_control",
                                     "device_name",
                                     "lag_if_name",
                                     "lag_type",
                                     "minimum_links",
                                     "link_speed",
                                     "internal_link_ip_address"])
        lagif_param["db_control"] = self.__db_delete
        lagif_param["device_name"] = device_name
        func_list.append(
            GlobalModule.DB_CONTROL.write_lagif_info)
        param_list.append(lagif_param)

        lagmemberif_param = dict.fromkeys(["db_control",
                                           "lag_if_name",
                                           "if_name",
                                           "device_name"])
        lagmemberif_param["db_control"] = self.__db_delete
        lagmemberif_param["device_name"] = device_name
        func_list.append(
            GlobalModule.DB_CONTROL.write_lagmemberif_info)
        param_list.append(lagmemberif_param)

        return func_list, param_list
