# -*- coding: utf-8 -*-

import imp
import json
import copy
from os import path

import xmltodict

import GlobalModule
from EmCommonLog import decorater_log

import threading

mutex = threading.RLock()


class EmCommonDriver(object):


    @decorater_log
    def write_em_info(self, device_name, service_type,
                      order_type, ec_message, is_write_force=False):
        if order_type == "delete":
            db_control_order = "DELETE"
        elif order_type == "merge":
            db_control_order = "UPDATE"
        else:
            GlobalModule.EM_LOGGER.debug(
                "******    DB Writing Result: FAILED. Control order is invalid\
                (EM selected info writing)")
            return False

        result = GlobalModule.EMSYSCOMUTILDB.write_em_info(
            db_control_order, device_name, service_type,
            ec_message, is_write_force)

        GlobalModule.EM_LOGGER.debug(
            "******    DB Writing Result(boolean): %s \
            (EM selected info writing)" % result)
        return result

    @decorater_log
    def start(self, device_name, ec_message=None):
        GlobalModule.EM_LOGGER.debug("******    Start Getting Registered Info")

        result_db, table_info =\
            GlobalModule.EMSYSCOMUTILDB.read_separate_driver_info(device_name)


            GlobalModule.EM_LOGGER.warning(
                "206011    Driver Definition Reading Error")
            return False
        else:
                GlobalModule.EM_LOGGER.debug(
                    "******    Getting Registered Info Success")
                try:
                    res_conf, self.__driver_path, driver_class =\
                        GlobalModule.EM_CONFIG.read_driver_conf(
                            table_info[0],
                            table_info[1],
                            table_info[2])
                except (KeyError, ValueError):
                    GlobalModule.EM_LOGGER.warning(
                        "206011    Driver Definition Reading Error")
                    return False
                GlobalModule.EM_LOGGER.debug(
                    "******    Driver Definition Read from EC Message")
                try:
                    ec_message_copy = copy.deepcopy(ec_message)
                    table_info_dict = ec_message_copy["device"]["equipment"]
                    res_conf, self.__driver_path, driver_class =\
                        GlobalModule.EM_CONFIG.read_driver_conf(
                            table_info_dict["platform"],
                            table_info_dict["os"],
                            table_info_dict["firmware"])
                except (KeyError, ValueError):
                    GlobalModule.EM_LOGGER.warning(
                        "206011    Driver Definition Reading Error")
                    return False
                GlobalModule.EM_LOGGER.warning(
                    "206011    Driver Definition Reading Error")
                return False

        if res_conf is False:
            GlobalModule.EM_LOGGER.warning(
                "206012    Individual Driver Judgment Error")
            return False
        else:
            self.__driver_path = path.normpath(
            path_py, name = path.split(self.__driver_path)

            GlobalModule.EM_LOGGER.info(
                "106001    Driver: %s Select" % name)

            try:
                global mutex
                mutex.acquire()

                GlobalModule.EM_LOGGER.debug(
                    "[%s] Lock acquired" % threading.currentThread().ident)

                GlobalModule.EM_LOGGER.debug(
                    "******    Start Searching Module")
                filepath, filename, data = imp.find_module(
                    driver_class, [path_py])
                GlobalModule.EM_LOGGER.debug(
                    "******    Start Loading Module")
                self.__target_module = imp.load_module(
                    driver_class, filepath, filename, data)
                GlobalModule.EM_LOGGER.debug(
                    "******    Set Module to Instance")
                self.__target_driver_class_ins =\
                    getattr(self.__target_module, driver_class)()

            except (AttributeError, ImportError, IOError) as e:
                GlobalModule.EM_LOGGER.warning(
                    "206003    Driver Select NG")
                GlobalModule.EM_LOGGER.warning(
                    "206003    %s" % (str(e)))
                return False

            finally:
                mutex.release()
                GlobalModule.EM_LOGGER.debug(
                    "[%s] Lock released" % threading.currentThread().ident)

            GlobalModule.EM_LOGGER.debug(
                "******    Loading Module Success")
            return True

    @decorater_log
    def connect_device(self, device_name, service_type=None,
                       order_type=None, ec_message=None):
        GlobalModule.EM_LOGGER.debug(
            "******    Start Getting Registered info")
        result_info, table_info =\
            GlobalModule.EMSYSCOMUTILDB.read_device_registered_info(
                device_name)

            GlobalModule.EM_LOGGER.debug(
                "******    DB Access Failed at DB Info Reading")
            GlobalModule.EM_LOGGER.warning(
                "206004    Driver Individual Connecting Control Error")
            return GlobalModule.COM_CONNECT_NO_RESPONSE
            if table_info != "" and table_info is not None:
                table_info_dict = {}
                for element in table_info:
                    table_info_dict.update(element)
                try:
                    device_info_python = {
                        "device_info": {
                            "platform_name": table_info_dict["platform_name"],
                            "os": table_info_dict["os"],
                            "firm_version": table_info_dict["firm_version"],
                            "username": table_info_dict["username"],
                            "password": table_info_dict["password"],
                            "mgmt_if_address": table_info_dict[
                                "mgmt_if_address"],
                            "mgmt_if_prefix": table_info_dict["mgmt_if_prefix"]
                        }
                    }
                except (KeyError, ValueError):
                    GlobalModule.EM_LOGGER.debug(
                        "******    DB Info Parse Failed(get registered info)")
                    GlobalModule.EM_LOGGER.warning(
                        "206004    Driver Individual Connecting Control Error")
                    return GlobalModule.COM_CONNECT_NO_RESPONSE
                GlobalModule.EM_LOGGER.debug(
                    "******    Reading Info from EC Message...\
                    (getting registered info)")
                try:
                    table_info_dict = {}
                    ec_message_copy = copy.deepcopy(ec_message)
                    element = json_data["device"]["equipment"]
                    table_info_dict.update(element)
                    element = json_data["device"]["management-interface"]
                    table_info_dict.update(element)
                    device_info_python = {
                        "device_info": {
                            "platform_name": table_info_dict["platform"],
                            "os": table_info_dict["os"],
                            "firm_version": table_info_dict["firmware"],
                            "username": table_info_dict["loginid"],
                            "password": table_info_dict["password"],
                            "mgmt_if_address": table_info_dict[
                                "address"],
                            "mgmt_if_prefix": table_info_dict["prefix"]}
                    }
                except (KeyError, ValueError):
                    GlobalModule.EM_LOGGER.debug(
                        "******  EC Message Parse Failed(get registered info)")
                    GlobalModule.EM_LOGGER.warning(
                        "206004    Driver Individual Connecting Control Error")
                    return GlobalModule.COM_CONNECT_NO_RESPONSE

        device_info = json.dumps(device_info_python)

        GlobalModule.EM_LOGGER.debug(
            "******    Start Access Target Driver")
        result_connect = self.__target_driver_class_ins.connect_device(
            device_name, device_info, service_type, order_type)
        if result_connect != GlobalModule.COM_CONNECT_OK:
            GlobalModule.EM_LOGGER.warning(
                "206004    Driver Individual Connecting Control Error")
        return result_connect

    @decorater_log
    def update_device_setting(self, device_name, service_type,
                              order_type, diff_info):
        GlobalModule.EM_LOGGER.debug(
            "******    Start Driver Edit")
        result = self.__target_driver_class_ins.update_device_setting(
            device_name, service_type, order_type, diff_info)
        if result != GlobalModule.COM_UPDATE_OK:
            GlobalModule.EM_LOGGER.warning(
                "206005    Driver Individual Edit Control Error")
            return result
        else:
            GlobalModule.EM_LOGGER.debug(
                "******    Driver Edit Success")
            return result

    @decorater_log
    def delete_device_setting(self, device_name, service_type,
                              order_type, diffrence_info):
        result = self.__target_driver_class_ins.delete_device_setting(
            device_name, service_type, order_type, diffrence_info)
        if result != GlobalModule.COM_UPDATE_OK:
            GlobalModule.EM_LOGGER.warning(
                "206013    Driver Individual Delete Control Error")
            return result
        else:
            GlobalModule.EM_LOGGER.debug(
                "******    Driver delete Success")
            return result

    @decorater_log
    def reserve_device_setting(self, device_name, service_type,
                               order_type):
        result = self.__target_driver_class_ins.reserve_device_setting(
            device_name, service_type, order_type)
        if result is False:
            GlobalModule.EM_LOGGER.warning(
                "206006    Driver Individual PreCommit Control Error")
            return False
        else:
            GlobalModule.EM_LOGGER.debug(
                "******    Driver Precommit Success")
            return True

    @decorater_log
    def enable_device_setting(self, device_name, service_type, order_type):
        result = self.__target_driver_class_ins.enable_device_setting(
            device_name, service_type, order_type)
        if result is False:
            GlobalModule.EM_LOGGER.warning(
                "206007    Driver Individual Commit Control Error")
            return False
        else:
            GlobalModule.EM_LOGGER.debug(
                "******    Driver Commit Success")
            return True

    @decorater_log
    def disconnect_device(self, device_name,
                          service_type, order_type):
        result = self.__target_driver_class_ins.disconnect_device(
            device_name, service_type, order_type)
        if result is False:
            GlobalModule.EM_LOGGER.warning(
                "206008    Driver Individual Disconnecting Control Error")
            return False
        else:
            GlobalModule.EM_LOGGER.debug(
                "******    Driver Disconnecting Success")
            return True

    @decorater_log
    def get_device_setting(self, device_name, service_type, order_type):
        result, responce = self.__target_driver_class_ins.get_device_setting(
            device_name, service_type, order_type)
        if result is True:
            GlobalModule.EM_LOGGER.debug(
                "******    Driver Get Success")
            return True, responce
        else:
            GlobalModule.EM_LOGGER.warning(
                "206009    Driver Individual Get Control Error")
            return False, None

    @decorater_log
    def compare_to_db_info(self, device_name, service_type,
                           order_type, ec_message):
        res_db, table_info = GlobalModule.EMSYSCOMUTILDB.read_em_info(
            device_name, service_type)
        if res_db is True:
            ec_message_copy = copy.deepcopy(ec_message)
            res_comp = self.__comp_db_info_in_each_table(
                ec_message_copy, table_info)
            if res_comp is True:
                GlobalModule.EM_LOGGER.debug(
                    "******    EC-DB Adjustment Success")
                return GlobalModule.COM_COMPARE_MATCH
            else:
                GlobalModule.EM_LOGGER.warning(
                    "206002    EC-DB Adjustment Error")
                return GlobalModule.COM_COMPARE_UNMATCH
        else:
            GlobalModule.EM_LOGGER.debug(
                "******    DB Reading Failed (EM selected info redfing)")
            return GlobalModule.COM_COMPARE_NO_INFO

    @decorater_log
    def compare_to_device_setting(self, device_name, service_type,
                                  order_type, device_signal):
        result = self.__target_driver_class_ins.execute_comparing(
            device_name, service_type, order_type, device_signal)

        if result is False:
            GlobalModule.EM_LOGGER.warning(
                "206010    Driver Individual Adjustment Error")
            return False
        else:
            GlobalModule.EM_LOGGER.debug(
                "******    SW-DB Info Matching Success )")
            return True

    @decorater_log
    def __init__(self):
        pass

    @decorater_log
    def __comp_db_info_in_each_table(self, ec_message, table_info):
        ec_xml = xmltodict.parse(ec_message)
        if table_info is None:
            return False
            if isinstance(ec_xml["device-leaf"]["cp"], list):
                return False
            return self. __comp_db_info_in_table(
                ec_xml, table_info[0], 0)
            table_num = 0
            for element in table_info:
                result =\
                    self. __comp_db_info_in_table(
                        ec_xml, element, table_num)
                if result is False:
                    return False
                table_num += 1

    @decorater_log
    def __comp_db_info_in_table(self, ec_xml, table_info, table_num):
        device_leaf_element = ec_xml["device-leaf"]
        if "@xmlns" not in device_leaf_element:
            return False
        else:
            service_url = device_leaf_element["@xmlns"]
        if "l2-slice" in service_url:
            ec1 = 2
            db1 = table_info["slice_type"]
            if ec1 != db1:
                GlobalModule.EM_LOGGER.debug(
                    "スライスタイプで整合NG@L2スライス")
                return False
            if not self.__compare_dict_elements(
                    table_info, "slice_name",
                    device_leaf_element, "slice_name"):
                return False
            if not self.__compare_dict_elements(
                    table_info, "device_name",
                    device_leaf_element, "name"):
                return False
            if not isinstance(device_leaf_element["cp"], list):
                cp_info_element = device_leaf_element["cp"]
            else:
                cp_info_element = None
                for element in device_leaf_element["cp"]:
                    if_name = False
                    vlan_id = False
                    if self.__compare_dict_elements(
                            table_info, "if_name", element, "name"):
                        if_name = True
                    if self.__compare_dict_elements(
                            table_info, "vlan_id", element, "vlan-id"):
                        vlan_id = True
                    if if_name and vlan_id:
                        cp_info_element = element
                if cp_info_element is None:
                    GlobalModule.EM_LOGGER.debug(
                        "当該DBに対するCPなしでNG@L2スライス")
                    return False
            ec6 = cp_info_element.get("port-mode")
            db6 = table_info.get("port_mode")
            if (ec6 is not None) or (db6 is not None):
                GlobalModule.EM_LOGGER.debug(
                    "port-modeの整合@L2スライス DB: %s, EC: %s",
                    str(db6), str(ec6))
                if db6 == 1 and ec6 == "access":
                    pass
                elif db6 == 2 and ec6 == "trunk":
                    pass
                else:
                    return False
            if not self.__compare_dict_elements(
                    table_info, "vni", cp_info_element, "vni"):
                return False
            if not self.__compare_dict_elements(
                    table_info, "multicast_group",
                    cp_info_element, "multicast-group"):
                return False
            return True
                table_info = table_info[0]
                if "vrf" in device_leaf_element:
                    vrf_dict = device_leaf_element["vrf"]
                    if not self.__compare_dict_elements(
                            table_info, "vrf_name",
                            vrf_dict, "vrf-name"):
                        return False
                    if not self.__compare_dict_elements(
                            table_info, "rd",
                            vrf_dict, "rd"):
                        return False
                    if not self.__compare_dict_elements(
                            table_info, "router_id",
                            vrf_dict, "router-id"):
                        return False
                    return False
                ec1 = 3
                db1 = table_info[0]["slice_type"]
                if ec1 != db1:
                    return False
                if not self.__compare_dict_elements(
                        table_info[0], "slice_name",
                        device_leaf_element, "slice_name"):
                    return False
                if not self.__compare_dict_elements(
                        table_info[0], "device_name",
                        device_leaf_element, "name"):
                    return False
                for cp_info_element in device_leaf_element["cp"]:
                    cp_loop_flag = True
                        cp_info_element = device_leaf_element["cp"]
                            GlobalModule.EM_LOGGER.debug(
                                "CP単数のとき、DBのCP情報が複数あってNG")
                            return False
                        cp_loop_flag = False
                        cp_len = len(device_leaf_element["cp"])
                        db_len = len(table_info)
                            GlobalModule.EM_LOGGER.debug(
                                "CPの数と、DBのCP情報の数が不一致でNG")
                            return False
                        table_info_elem = None
                        for table_element in table_info:
                            if_name = False
                            vlan_id = False
                            if self.__compare_dict_elements(
                                    table_element, "if_name",
                                    cp_info_element, "name"):
                                if_name = True
                            if self.__compare_dict_elements(
                                    table_element, "vlan_id",
                                    cp_info_element, "vlan-id"):
                                vlan_id = True
                            if if_name and vlan_id:
                                table_info_elem = table_element
                                break
                        if table_info_elem is None:
                            GlobalModule.EM_LOGGER.debug(
                                "同じ主キーをもったテーブルを発見できずNG@CP")
                            return False
                    if "ce-interface" in cp_info_element:
                        ce_i_dict = cp_info_element[
                            "ce-interface"]
                        if ce_i_dict is None:
                            ce_i_dict = {}
                        if ("address" not in ce_i_dict) and\
                                (table_info_elem.get("ipv4_address") is None):
                            pass
                        elif not self.__compare_dict_elements(
                                table_info_elem, "ipv4_address",
                                ce_i_dict, "address"):
                            return False
                        else:
                            pass
                        if ("prefix" not in ce_i_dict) and\
                                (table_info_elem.get("ipv4_prefix") is None):
                            pass
                        elif not self.__compare_dict_elements(
                                table_info_elem, "ipv4_prefix",
                                ce_i_dict, "prefix"):
                            return False
                        else:
                            pass
                        if ("address6" not in ce_i_dict) and\
                                (table_info_elem.get("ipv6_address") is None):
                            pass
                        elif not self.__compare_dict_elements(
                                table_info_elem, "ipv6_address",
                                ce_i_dict, "address6"):
                            return False
                        else:
                            pass
                        if ("prefix6" not in ce_i_dict) and\
                                (table_info_elem.get("ipv6_prefix") is None):
                            pass
                        elif not self.__compare_dict_elements(
                                table_info_elem, "ipv6_prefix",
                                ce_i_dict, "prefix6"):
                            return False
                        else:
                            pass
                        if ("mtu" not in ce_i_dict) and\
                                (table_info_elem.get("mtu_size") is None):
                            pass
                        elif not self.__compare_dict_elements(
                                table_info_elem, "mtu_size", ce_i_dict, "mtu"):
                            return False
                        return False
                    if table_info_elem["vrrp_flag"] is not None:
                        if "vrrp" in cp_info_element:
                            ec11 = True
                            db11 = table_info_elem["vrrp_flag"]
                        else:
                            ec11 = False
                            db11 = table_info_elem["vrrp_flag"]
                        if ec11 != db11:
                            GlobalModule.EM_LOGGER.debug(
                                "VRRPFLUG整合でNG@CP")
                            return False
                        return False
                    if table_info_elem["static_flag"] is not None:
                        if "static" in cp_info_element:
                            ec12 = True
                            db12 = table_info_elem["static_flag"]
                        else:
                            ec12 = False
                            db12 = table_info_elem["static_flag"]
                        if ec12 != db12:
                            GlobalModule.EM_LOGGER.debug(
                                "STATICFLUG整合でNG@CP")
                            return False
                        return False
                    if table_info_elem["ospf_flag"] is not None:
                        if "ospf" in cp_info_element:
                            ospf_dict = cp_info_element["ospf"]
                            if not self.__compare_dict_elements(
                                    table_info_elem, "metric",
                                    ospf_dict, "metric"):
                                return False
                        else:
                            ec13 = False
                            db13 = table_info_elem["ospf_flag"]
                            if ec13 != db13:
                                return False
                        return False
                    if not cp_loop_flag:
                        break
            else:
                if len(table_info) == 0:
                    pass
                    check_num = 0
                    cp_loop_flag = True
                    for cp_info_element in device_leaf_element["cp"]:
                        if not isinstance(device_leaf_element["cp"], list):
                            cp_info_element = device_leaf_element["cp"]
                            cp_loop_flag = False
                        if "static" in cp_info_element:
                            static_dict = cp_info_element["static"]
                        else:
                            continue
                        if "route" in static_dict:
                            route_list = static_dict["route"]
                            route_roopflag = True
                            for route_element in route_list:
                                if not isinstance(route_list, list):
                                    route_element = route_list
                                    route_roopflag = False
                                table_info_elem = None
                                for element in table_info:
                                    if_name = False
                                    vlan_id = False
                                    address = False
                                    prefix = False
                                    nexthop = False
                                    address_type = False
                                    if self.__compare_dict_elements(
                                            element, "if_name",
                                            cp_info_element, "name"):
                                        if_name = True
                                    if self.__compare_dict_elements(
                                            element, "vlan_id",
                                            cp_info_element, "vlan-id"):
                                        vlan_id = True
                                    ec1 = 4
                                    db1 = element["address_type"]
                                    if ec1 == db1:
                                        address_type = True
                                    if self.__compare_dict_elements(
                                            element, "address",
                                            route_element, "address"):
                                        address = True
                                    if self.__compare_dict_elements(
                                            element, "prefix",
                                            route_element, "prefix"):
                                        prefix = True
                                    if self.__compare_dict_elements(
                                            element, "nexthop",
                                            route_element, "next-hop"):
                                        nexthop = True
                                    if if_name and vlan_id and address_type and\
                                            address and prefix and nexthop:
                                        table_info_elem = element
                                        break
                                if table_info_elem is None:
                                    GlobalModule.EM_LOGGER.debug(
                                        "当該CPに対するテーブルが見つからずNG@STATIC IPv4")
                                    return False
                                check_num += 1
                                if not route_roopflag:
                                    break
                        if "route6" in static_dict:
                            route_list = static_dict["route6"]
                            route_roopflag = True
                            for route_element in route_list:
                                if not isinstance(route_list, list):
                                    route_element = route_list
                                    route_roopflag = False
                                table_info_elem = None
                                for element in table_info:
                                    if_name = False
                                    vlan_id = False
                                    address = False
                                    prefix = False
                                    nexthop = False
                                    address_type = False
                                    if self.__compare_dict_elements(
                                            element, "if_name",
                                            cp_info_element, "name"):
                                        if_name = True
                                    if self.__compare_dict_elements(
                                            element, "vlan_id",
                                            cp_info_element, "vlan-id"):
                                        vlan_id = True
                                    ec1 = 6
                                    db1 = element["address_type"]
                                    if ec1 == db1:
                                        address_type = True
                                    if self.__compare_dict_elements(
                                            element, "address",
                                            route_element, "address"):
                                        address = True
                                    if self.__compare_dict_elements(
                                            element, "prefix",
                                            route_element, "prefix"):
                                        prefix = True
                                    if self.__compare_dict_elements(
                                            element, "nexthop",
                                            route_element, "next-hop"):
                                        nexthop = True
                                    if if_name and vlan_id and address_type and\
                                            address and prefix and nexthop:
                                        table_info_elem = element
                                        break
                                if table_info_elem is None:
                                    GlobalModule.EM_LOGGER.debug(
                                        "当該CPに対するテーブルが見つからずNG@STATIC IPv6")
                                    return False
                                check_num += 1
                                if not route_roopflag:
                                    break
                        if not cp_loop_flag:
                            break
                    if check_num != len(table_info):
                        GlobalModule.EM_LOGGER.debug(
                            "DBとチェックしたSTATICの数があわずNG")
                        return False
                    GlobalModule.EM_LOGGER.debug("BGP整合開始")
                    investigate_flag = False
                    for table_info_elem in table_info:
                        investigate_flag = True
                        if not isinstance(device_leaf_element["cp"], list):
                            cp_info_element = device_leaf_element["cp"]
                            GlobalModule.EM_LOGGER.debug(
                                "CPが単数の場合@BGP")
                            cp_info_element = None
                            for element in device_leaf_element["cp"]:
                                GlobalModule.EM_LOGGER.debug(
                                    "CPが複数の場合@BGP")
                                if "bgp" not in element:
                                    continue
                                if_name = False
                                vlan_id = False
                                if self.__compare_dict_elements(
                                        table_info_elem, "if_name",
                                        element, "name"):
                                    if_name = True
                                if self.__compare_dict_elements(
                                        table_info_elem, "vlan_id",
                                        element, "vlan-id"):
                                    vlan_id = True
                                if if_name and vlan_id:
                                    cp_info_element = element
                                    break
                            if cp_info_element is None:
                                GlobalModule.EM_LOGGER.debug(
                                    "当該テーブルに対するCP情報がないのでNG@BGP")
                                return False
                        if "bgp" in cp_info_element:
                            bgp_dict = cp_info_element["bgp"]
                            investigate_flag = False
                        else:
                            GlobalModule.EM_LOGGER.debug(
                                "BGPテーブルがあるのにCPにはなくてNG")
                            return False
                        if not self.__compare_dict_elements(
                                table_info_elem, "remote_as_number",
                                bgp_dict, "remote-as-number"):
                            return False
                        else:
                            pass
                        if ("local-address" not in bgp_dict) and\
                                (table_info_elem.get("local_ipv4_address") is
                                 None):
                            pass
                        elif not self.__compare_dict_elements(
                                table_info_elem, "local_ipv4_address",
                                bgp_dict, "local-address"):
                            return False
                        else:
                            pass
                        if ("remote-address" not in bgp_dict) and\
                                (table_info_elem.get("remote_ipv4_address") is
                                 None):
                            pass
                        elif not self.__compare_dict_elements(
                                table_info_elem, "remote_ipv4_address",
                                bgp_dict, "remote-address"):
                            return False
                        else:
                            pass
                        if ("local-address6" not in bgp_dict) and\
                                (table_info_elem.get("local_ipv6_address") is
                                 None):
                            pass
                        elif not self.__compare_dict_elements(
                                table_info_elem, "local_ipv6_address",
                                bgp_dict, "local-address6"):
                            return False
                        else:
                            pass
                        if ("remote-address6" not in bgp_dict) and\
                                (table_info_elem.get("remote_ipv6_address") is
                                 None):
                            pass
                        elif not self.__compare_dict_elements(
                                table_info_elem, "remote_ipv6_address",
                                bgp_dict, "remote-address6"):
                            return False
                        else:
                            pass
                    if investigate_flag:
                        return False
                    investigate_flag = False
                    for table_info_elem in table_info:
                        investigate_flag = True
                        if not isinstance(device_leaf_element["cp"], list):
                            cp_info_element = device_leaf_element["cp"]
                        else:
                            cp_info_element = None
                            for element in device_leaf_element["cp"]:
                                GlobalModule.EM_LOGGER.debug(
                                    "CPが複数の場合@VRRP")
                                if "vrrp" not in element:
                                    continue
                                if_name = False
                                vlan_id = False
                                if self.__compare_dict_elements(
                                        table_info_elem, "if_name",
                                        element, "name"):
                                    if_name = True
                                if self.__compare_dict_elements(
                                        table_info_elem, "vlan_id",
                                        element, "vlan-id"):
                                    vlan_id = True
                                if if_name and vlan_id:
                                    cp_info_element = element
                                    break
                            if cp_info_element is None:
                                GlobalModule.EM_LOGGER.debug(
                                    "当該テーブルに対するCP情報がないのでNG@VRRP")
                                return False
                        investigate_flag = False
                        if "vrrp" in cp_info_element:
                            vrrp_detail_dict = cp_info_element["vrrp"]
                            investigate_flag = False
                        else:
                            break
                        if not self.__compare_dict_elements(
                                table_info_elem, "vrrp_group_id",
                                vrrp_detail_dict, "group-id"):
                            return False
                        if ("virtual-address" not in vrrp_detail_dict) and\
                                (table_info_elem.get("virtual_ipv4_address") is
                                 None):
                            pass
                        elif not self.__compare_dict_elements(
                                table_info_elem, "virtual_ipv4_address",
                                vrrp_detail_dict, "virtual-address"):
                            return False
                        else:
                            pass
                        if ("virtual-address6" not in vrrp_detail_dict) and\
                                (table_info_elem.get("virtual_ipv6_address") is
                                 None):
                            pass
                        elif not self.__compare_dict_elements(
                                table_info_elem, "virtual_ipv6_address",
                                vrrp_detail_dict, "virtual-address6"):
                            return False
                        else:
                            pass
                        if not self.__compare_dict_elements(
                                table_info_elem, "priority",
                                vrrp_detail_dict, "priority"):
                            return False
                    if investigate_flag:
                        return False
                    cp_loop_flag = True
                    for cp_info_element in device_leaf_element["cp"]:
                        if not isinstance(device_leaf_element["cp"], list):
                            cp_info_element = device_leaf_element["cp"]
                            cp_loop_flag = False
                        if "vrrp" in cp_info_element:
                            vrrp_dict = cp_info_element["vrrp"]
                        else:
                            continue
                        if "track" in vrrp_dict:
                            vrrp_interface_dict = vrrp_dict["track"]
                        else:
                            continue
                        vi_name_list = vrrp_interface_dict["interface"]
                        if_roopflag = True
                        for vn_element_dict in vi_name_list:
                            if not isinstance(vi_name_list, list):
                                vn_element_dict = vi_name_list
                                if_roopflag = False
                            table_info_elem = None
                            for element in table_info:
                                vrrp_group_id = False
                                track_if_name = False
                                if self.__compare_dict_elements(
                                        element, "vrrp_group_id",
                                        vrrp_dict, "group-id"):
                                    vrrp_group_id = True
                                if self.__compare_dict_elements(
                                        element, "track_if_name",
                                        vn_element_dict, "name"):
                                    track_if_name = True
                                if vrrp_group_id and track_if_name:
                                    table_info_elem = element
                                    break
                            if table_info_elem is None:
                                GlobalModule.EM_LOGGER.debug(
                                    "当該VRRP TRACKに対するDBを発見できずNG")
                                return False
                            if not self.__compare_dict_elements(
                                    table_info_elem, "track_if_name",
                                    vn_element_dict, "name"):
                                return False
                            check_num += 1
                            if not if_roopflag:
                                break
                        if not cp_loop_flag:
                            break
                    if check_num != len(table_info):
                        GlobalModule.EM_LOGGER.debug(
                            "整合した数がDBとXMLであわずNG@VRRP TRACK")
                        return False
            return True
        else:
            return False

    @staticmethod
    @decorater_log
    def __compare_dict_elements(dict1, key1, dict2, key2):
        target_1 = dict1.get(key1)
        target_2 = dict2.get(key2)
        if isinstance(target_1, int):
            target_1 = str(target_1)
        GlobalModule.EM_LOGGER.debug(
            "比較対象の実態 DB(%s): %s EC(%s): %s",
            key1, target_1, key2, str(target_2))
        GlobalModule.EM_LOGGER.debug(
            "比較対象の型 DB: %s, EC:%s", str(type(target_1)), str(type(target_2)))
        return (target_1 is not None) and (target_2 is not None)\
            and(target_1 == target_2)
