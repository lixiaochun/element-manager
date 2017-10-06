# -*- coding: utf-8 -*-
import json
import socket
import struct
import re
import traceback
from lxml import etree
from EmCommonLog import decorater_log
from EmNetconfProtocol import EmNetconfProtocol
from EmDriverCommonUtilityDB import EmDriverCommonUtilityDB
from EmDriverCommonUtilityLog import EmDriverCommonUtilityLog


class EmSeparateDriver(object):

    Logmessage = {"XML_PARSE": "XML Parser Error",
                  "Control_Classification": "Control Classification Error",
                  "Signal_Editing": "Signal Editing Error",
                  "info_compare": "Information Compare Error",
                  "Interworking": "Interworking Error",
                  "Validation": "Validation Error",
                  "Call_NG_Method": "Call EmSeparateDriver IF: %s NG",
                  "NetConf_Fault": "Could not %s Device ERROR"}

    name_spine = "spine"
    name_leaf = "leaf"
    name_l2_slice = "l2-slice"
    name_l3_slice = "l3-slice"
    name_celag = "ce-lag"
    name_internal_lag = "internal-lag"

    log_level_debug = "DEBUG"
    log_level_warn = "WARN"
    log_level_info = "INFO"
    log_level_error = "ERROR"

    re_rpc_error = re.compile("<rpc-error>")

    _send_message_top_tag = "config"


    @decorater_log
    def __init__(self):
        self.net_protocol = EmNetconfProtocol()
        self.common_util_db = EmDriverCommonUtilityDB()
        self.common_util_log = EmDriverCommonUtilityLog()
        self.list_enable_service = []
        self.get_config_message = {}

    @decorater_log
    def connect_device(self, device_name,
                       device_info, service_type, order_type):
        self.common_util_log.logging(
            device_name, self.log_level_debug,
            "order_type=%s" % (order_type,), __name__)
        if self._check_service_type(device_name, service_type) is False:
        return self.net_protocol.connect_device(device_info)

    @decorater_log
    def update_device_setting(self, device_name,
                              service_type, order_type, ec_message=None):
        self.common_util_log.logging(
            device_name, self.log_level_debug,
            "order_type=%s" % (order_type,), __name__)
        if self._check_service_type(device_name, service_type) is False or \
                self._send_control_signal(device_name, "discard-changes")[0] is False or \
                self._send_control_signal(device_name, "lock")[0] is False:
            return self._update_error
        is_db_result, device_info = \
            self.common_util_db.read_configureddata_info(
                device_name, service_type)
        if is_db_result is False:
            return self._update_error
        is_message_result, send_message = self._gen_message(
            device_name, service_type, device_info, ec_message)
        if is_message_result is False:
            return self._update_error
        if self._validation(device_name, service_type, ec_message) is False:
            return self._update_validation_ng
        if (self._send_control_signal(device_name,
                                      "edit-config",
                                      send_message,
                                      service_type)[0] is False or
                self._send_control_signal(device_name,
                                          "validate")[0] is False):
            return self._update_error
        else:
            return self._update_ok

    @decorater_log
    def delete_device_setting(self, device_name,
                              service_type, order_type, ec_message=None):
        self.common_util_log.logging(
            device_name, self.log_level_debug,
            "order_type=%s" % (order_type,), __name__)
        if self._check_service_type(device_name, service_type) is False or \
                self._send_control_signal(device_name, "discard-changes")[0] is False or \
                self._send_control_signal(device_name, "lock")[0] is False:
            return self._update_error
        is_db_result, device_info = \
            self.common_util_db.read_configureddata_info(
                device_name, service_type)
        if is_db_result is False:
            return self._update_error
        is_message_result, send_message = self._gen_message(
            device_name, service_type, device_info, ec_message, "delete")
        if is_message_result is False:
            return self._update_error
        if self._validation(device_name, service_type, ec_message) is False:
            return self._update_validation_ng
        if (self._send_control_signal(device_name,
                                      "edit-config",
                                      send_message,
                                      service_type,
                                      "delete")[0] is False or
                self._send_control_signal(device_name,
                                          "validate")[0] is False):
            return self._update_error
        else:
            return self._update_ok

    @decorater_log
    def reserve_device_setting(self, device_name, service_type, order_type):
        self.common_util_log.logging(
            device_name, self.log_level_debug,
            "order_type=%s" % (order_type,), __name__)
        if self._check_service_type(device_name, service_type) is False:
            return False
        return self._send_control_signal(device_name, "confirmed-commit")[0]

    @decorater_log
    def enable_device_setting(self, device_name, service_type, order_type):
        self.common_util_log.logging(
            device_name, self.log_level_debug,
            "order_type=%s" % (order_type,), __name__)
        if self._check_service_type(device_name, service_type) is False:
            return False
        if self._send_control_signal(device_name, "commit")[0] is False:
            return False
        try:
            is_ok = self._send_control_signal(device_name, "unlock")[0]
        except Exception, ex_message:
            self.common_util_log.logging(
                device_name, self.log_level_debug,
                "ERROR %s\n%s" % (ex_message, traceback.format_exc()),
                __name__)
            is_ok = False
        if not is_ok:
            self.common_util_log.logging(
                device_name, self.log_level_warn,
                self.Logmessage["NetConf_Fault"] % ("unlock",), __name__)
        return True

    @decorater_log
    def disconnect_device(self, device_name, service_type, order_type):
        self.common_util_log.logging(
            device_name, self.log_level_debug,
            "order_type=%s" % (order_type,), __name__)
        self._check_service_type(device_name, service_type)
        try:
            is_ok = self.net_protocol.disconnect_device()
        except Exception, ex_message:
            self.common_util_log.logging(
                device_name, self.log_level_debug,
                "ERROR %s\n%s" % (ex_message, traceback.format_exc()),
                __name__)
            is_ok = False
        if not is_ok:
            self.common_util_log.logging(
                device_name, self.log_level_warn,
                self.Logmessage["NetConf_Fault"] % ("disconnect",), __name__)
        return True

    @decorater_log
    def get_device_setting(self,
                           device_name,
                           service_type,
                           order_type):
        self.common_util_log.logging(
            device_name, self.log_level_debug,
            "order_type=%s" % (order_type,), __name__)
        if self._check_service_type(device_name, service_type) is False:
            return False, None
        is_db_result = (self.common_util_db.read_configureddata_info
                        (device_name, service_type)[0])
        if is_db_result is False:
            return False, None
        send_message = self.get_config_message.get(service_type)
        if send_message is None:
            self.common_util_log.logging(
                device_name, self.log_level_warn,
                self.Logmessage["Signal_Editing"], __name__)
            return False, None
        is_send_result, return_message = \
            self._send_control_signal(device_name,
                                      "get-config",
                                      send_message)
        if is_send_result is False:
            return False, None
        else:
            return True, return_message

    @decorater_log
    def execute_comparing(self, device_name,
                          service_type, order_type, device_signal):
        self.common_util_log.logging(
            device_name, self.log_level_debug,
            "order_type=%s" % (order_type,), __name__)
        if self._check_service_type(device_name, service_type) is False:
            return False
        is_db_result, device_info = \
            self.common_util_db.read_configureddata_info(
                device_name, service_type)
        if is_db_result is False:
            return False
        return self._comparsion_process_sw_db(
            device_name, service_type, device_signal, device_info)

    @decorater_log
    def _check_service_type(self, device_name, service_type):

        for item in self.list_enable_service:
            if service_type == item:
                return True

        self.common_util_log.logging(
            device_name, self.log_level_warn,
            self.Logmessage["Control_Classification"], __name__)
        return False

    @decorater_log
    def _send_control_signal(self,
                             device_name,
                             message_type,
                             send_message=None,
                             service_type=None,
                             operation=None):
        self.common_util_log.logging(
            device_name, self.log_level_debug,
            ("send_message message_type:%s ,service_type:%s ,operation:%s ." +
             "send_message = %s") % (message_type, service_type, operation,
                                     send_message), __name__)
        is_result, message = \
            self.net_protocol.send_control_signal(message_type, send_message)
        if isinstance(message, str) and \
                self.re_rpc_error.search(message) is not None:
            is_result = False
        self.common_util_log.logging(
            device_name, self.log_level_debug,
            "receive_message is_result:%s ,message:%s" %
            (is_result, message), __name__)
        return is_result, message

    @decorater_log
    def _gen_message(self,
                     device_name,
                     service_type,
                     device_info,
                     ec_message=None,
                     operation=None):
        is_message_gen_result = False
        send_message = None
        if device_info is not None:
            parse_json = json.loads(device_info)
        else:
            parse_json = {}
        if ec_message is not None:
            ec_json = json.loads(ec_message)
        else:
            service_type = None

        top_tag_mes = self._send_message_top_tag

        if service_type == self.name_spine:
            is_message_gen_result, send_message = self._gen_message_child(
                parse_json,
                ec_json,
                operation,
                self._gen_spine_fix_message,
                self._gen_spine_variable_message,
                top_tag_mes)
        elif service_type == self.name_leaf:
            is_message_gen_result, send_message = self._gen_message_child(
                parse_json,
                ec_json,
                operation,
                self._gen_leaf_fix_message,
                self._gen_leaf_variable_message,
                top_tag_mes)
        elif service_type == self.name_l2_slice:
            is_message_gen_result, send_message = self._gen_message_child(
                parse_json,
                ec_json,
                operation,
                self._gen_l2_slice_fix_message,
                self._gen_l2_slice_variable_message,
                top_tag_mes)
        elif service_type == self.name_l3_slice:
            is_message_gen_result, send_message = self._gen_message_child(
                parse_json,
                ec_json,
                operation,
                self._gen_l3_slice_fix_message,
                self._gen_l3_slice_variable_message,
                top_tag_mes)
        elif service_type == self.name_celag:
            is_message_gen_result, send_message = self._gen_message_child(
                parse_json,
                ec_json,
                operation,
                self._gen_ce_lag_fix_message,
                self._gen_ce_lag_variable_message,
                top_tag_mes)
        elif service_type == self.name_internal_lag:
            is_message_gen_result, send_message = self._gen_message_child(
                parse_json,
                ec_json,
                operation,
                self._gen_internal_fix_lag_message,
                self._gen_internal_lag_variable_message,
                top_tag_mes)
        else:
            pass
        if is_message_gen_result is False:
            self.common_util_log.logging(
                device_name, self.log_level_warn,
                self.Logmessage["Signal_Editing"], __name__)
            self.common_util_log.logging(
                device_name, self.log_level_warn,
                self.Logmessage["Interworking"], __name__)

        return is_message_gen_result, send_message

    @staticmethod
    @decorater_log
    def _gen_message_child(device_info,
                           ec_message,
                           operation,
                           method_fix_message_gen,
                           method_variable_message_gen,
                           top_tag="config"):
        return_val = True
        xml_obj = etree.Element(top_tag)
        return_val = return_val and method_fix_message_gen(xml_obj, operation)
        return_val = return_val and method_variable_message_gen(
            xml_obj, device_info, ec_message, operation)
        return_string = etree.tostring(xml_obj)
        return return_val, return_string

    @staticmethod
    @decorater_log
    def _set_xml_tag(parent, tag,
                     attr_key=None, attr_value=None, text=None):
        sub_element = etree.SubElement(parent, tag)
        if attr_key is not None and attr_value is not None:
            sub_element.set(attr_key, attr_value)
        if text is None:
            sub_element.text = ""
        else:
            sub_element.text = str(text)
        return sub_element

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

    @decorater_log
    def _set_xml_tag_variable(self, parent, tag, text, *tags):
        target_node = None
        tmp = self._find_xml_node(parent, *tags)
        if tmp is not None:
            target_node = tmp.find(tag)
            if target_node is not None:
                target_node.text = text

        return target_node

    @decorater_log
    def _set_ope_delete_tag(self, node, tag, operation, text=None):
        if operation == "delete":
            return self._set_xml_tag(node, tag, "operation", "delete", text)
        else:
            return self._set_xml_tag(node, tag, None, None, text)

    @staticmethod
    @decorater_log
    def _conversion_cidr2mask(cidr_val):
        try:
            int_cidr = int(cidr_val)
        except (ValueError, TypeError):
            return None
        if int_cidr < 0 or int_cidr > 32:
            return None
        return socket.inet_ntoa(

    @decorater_log
    def _validation(self, device_name, service_type, device_info):
        is_validation_check = False
        parse_json = json.loads(device_info)
        if service_type == self.name_spine:
            is_validation_check = self._validation_spine(parse_json)
        elif service_type == self.name_leaf:
            is_validation_check = self._validation_leaf(parse_json)
        elif service_type == self.name_l2_slice:
            is_validation_check = self._validation_l2_slice(parse_json)
        elif service_type == self.name_l3_slice:
            is_validation_check = self._validation_l3_slice(parse_json)
        elif service_type == self.name_celag:
            is_validation_check = self._validation_ce_lag(parse_json)
        elif service_type == self.name_internal_lag:
            is_validation_check = self._validation_internal_lag(parse_json)
        else:
            pass
        if is_validation_check is False:
            self.common_util_log.logging(
                device_name,
                self.log_level_warn, self.
                Logmessage[
                    "Validation"],
                __name__)
        return is_validation_check

    @decorater_log
    def _comparsion_process_sw_db(self, device_name,
                                  service_type, receive_message, db_info):
        parse_db_info = None
        parse_netconf = None
        if db_info is not None:
            parse_db_info = json.loads(db_info)
        if receive_message is not None:
            parse_netconf = self._parse_receive_info(receive_message)
        is_check_result = False
        try:
            if parse_db_info is None or parse_netconf is None:
                is_check_result = (
                    service_type in
                    (self.name_l2_slice, self.name_l3_slice) and
                    parse_db_info is None and parse_netconf is None)
            elif service_type == self.name_l2_slice:
                is_check_result = self._comparsion_sw_db_l2_slice(
                    parse_netconf, parse_db_info)
            elif service_type == self.name_l3_slice:
                is_check_result = self._comparsion_sw_db_l3_slice(
                    parse_netconf, parse_db_info)
        except Exception:
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "ERROR traceback \n%s" % (traceback.format_exc(),),
                __name__)
        if is_check_result is False:
            self.common_util_log.logging(
                device_name,
                self.log_level_warn,
                self.Logmessage["info_compare"],
                __name__)
        return is_check_result

    @decorater_log
    def _comparsion_pair(self, netconf_val, db_val):
        is_ok = False
        if netconf_val is None and db_val is None:
            is_ok = True
        elif netconf_val is None:
            is_ok = False
        else:
            is_ok = bool("%s" % (netconf_val.text,) == "%s" % (db_val,))
        self.common_util_log.logging(
            "comparsion_pair_result",
            self.log_level_debug,
            "%s : %s = %s" % (
                (netconf_val.tag if netconf_val is not None else None),
                (netconf_val.text if netconf_val is not None else None),
                db_val), __name__)
        return is_ok



    @decorater_log
    def _gen_spine_fix_message(self, xml_obj, operation):
        self.common_util_log.logging(
            " ",
            self.log_level_error,
            self.Logmessage["Call_NG_Method"] %
            ("_gen_spine_fix_message"),
            __name__)
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "params : xml_obj = %s , operation = %s" % (xml_obj, operation),
            __name__)
        return False

    @decorater_log
    def _gen_leaf_fix_message(self, xml_obj, operation):
        self.common_util_log.logging(
            " ",
            self.log_level_error,
            self.Logmessage["Call_NG_Method"] %
            ("_gen_leaf_fix_message"),
            __name__)
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "params : xml_obj = %s , operation = %s" % (xml_obj, operation),
            __name__)
        return False

    @decorater_log
    def _gen_l2_slice_fix_message(self, xml_obj, operation):
        self.common_util_log.logging(
            " ",
            self.log_level_error,
            self.Logmessage["Call_NG_Method"] %
            ("_gen_l2_slice_fix_message"),
            __name__)
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "params : xml_obj = %s , operation = %s" % (xml_obj, operation),
            __name__)
        return False

    @decorater_log
    def _gen_l3_slice_fix_message(self, xml_obj, operation):
        self.common_util_log.logging(
            " ",
            self.log_level_error,
            self.Logmessage["Call_NG_Method"] %
            ("_gen_l3_slice_fix_message"),
            __name__)
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "params : xml_obj = %s , operation = %s" % (xml_obj, operation),
            __name__)
        return False

    @decorater_log
    def _gen_ce_lag_fix_message(self, xml_obj, operation):
        self.common_util_log.logging(
            " ",
            self.log_level_error,
            self.Logmessage["Call_NG_Method"] %
            ("_gen_ce_lag_fix_message"),
            __name__)
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "params : xml_obj = %s , operation = %s" % (xml_obj, operation),
            __name__)
        return False

    @decorater_log
    def _gen_internal_fix_lag_message(self, xml_obj, operation):
        self.common_util_log.logging(
            " ",
            self.log_level_error,
            self.Logmessage["Call_NG_Method"] %
            ("_gen_internal_fix_lag_message"),
            __name__)
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "params : xml_obj = %s , operation = %s" % (xml_obj, operation),
            __name__)
        return False


    @decorater_log
    def _gen_spine_variable_message(self,
                                    xml_obj,
                                    device_info,
                                    ec_message,
                                    operation):
        self.common_util_log.logging(
            " ",
            self.log_level_error,
            self.Logmessage["Call_NG_Method"] %
            ("_gen_spine_variable_message"),
            __name__)
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "params : xml_obj=%s ,device_info=%s ,ec_message=%s operation=%s" %
            (xml_obj, device_info, ec_message, operation),
            __name__)
        return False

    @decorater_log
    def _gen_leaf_variable_message(self,
                                   xml_obj,
                                   device_info,
                                   ec_message,
                                   operation):
        self.common_util_log.logging(
            " ",
            self.log_level_error,
            self.Logmessage["Call_NG_Method"] %
            ("_gen_leaf_variable_message"),
            __name__)
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "params : xml_obj=%s ,device_info=%s ,ec_message=%s operation=%s" %
            (xml_obj, device_info, ec_message, operation),
            __name__)
        return False

    @decorater_log
    def _gen_l2_slice_variable_message(self,
                                       xml_obj,
                                       device_info,
                                       ec_message,
                                       operation):
        self.common_util_log.logging(
            " ",
            self.log_level_error,
            self.Logmessage["Call_NG_Method"] %
            ("_gen_l2_slice_variable_message"),
            __name__)
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "params : xml_obj=%s ,device_info=%s ,ec_message=%s operation=%s" %
            (xml_obj, device_info, ec_message, operation),
            __name__)
        return False

    @decorater_log
    def _gen_l3_slice_variable_message(self,
                                       xml_obj,
                                       device_info,
                                       ec_message,
                                       operation):
        self.common_util_log.logging(
            " ",
            self.log_level_error,
            self.Logmessage["Call_NG_Method"] %
            ("_gen_l3_slice_variable_message"),
            __name__)
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "params : xml_obj=%s ,device_info=%s ,ec_message=%s operation=%s" %
            (xml_obj, device_info, ec_message, operation),
            __name__)
        return False

    @decorater_log
    def _gen_ce_lag_variable_message(self,
                                     xml_obj,
                                     device_info,
                                     ec_message,
                                     operation):
        self.common_util_log.logging(
            " ",
            self.log_level_error,
            self.Logmessage["Call_NG_Method"] %
            ("_gen_ce_lag_variable_message"),
            __name__)
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "params : xml_obj=%s ,device_info=%s ,ec_message=%s operation=%s" %
            (xml_obj, device_info, ec_message, operation),
            __name__)
        return False

    @decorater_log
    def _gen_internal_lag_variable_message(self,
                                           xml_obj,
                                           device_info,
                                           ec_message,
                                           operation):
        self.common_util_log.logging(
            " ",
            self.log_level_error,
            self.Logmessage["Call_NG_Method"] %
            ("_gen_internal_lag_variable_message"),
            __name__)
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "params : xml_obj=%s ,device_info=%s ,ec_message=%s operation=%s" %
            (xml_obj, device_info, ec_message, operation),
            __name__)
        return False


    @decorater_log
    def _validation_spine(self, device_info):
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "%s validation is ok : device_info = %s" %
            (self.name_spine, device_info), __name__)
        return True

    @decorater_log
    def _validation_leaf(self, device_info):
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "%s validation is ok : device_info = %s" %
            (self.name_leaf, device_info), __name__)
        return True

    @decorater_log
    def _validation_l2_slice(self, device_info):
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "%s validation is ok : device_info = %s" %
            (self.name_l2_slice, device_info), __name__)
        return True

    @decorater_log
    def _validation_l3_slice(self, device_info):
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "%s validation is ok : device_info = %s" %
            (self.name_l3_slice, device_info), __name__)
        return True

    @decorater_log
    def _validation_ce_lag(self, device_info):
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "%s validation is ok : device_info = %s" %
            (self.name_celag, device_info), __name__)
        return True

    @decorater_log
    def _validation_internal_lag(self, device_info):
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "%s validation is ok : device_info = %s" %
            (self.name_internal_lag, device_info), __name__)
        return True


    @decorater_log
    def _parse_receive_info(self, receive_message):
        try:
            xml_obj = etree.fromstring(receive_message)
        except Exception, ex_message:
            xml_obj = None
            self.common_util_log.logging(
                "receive_device", self.log_level_warn,
                self.Logmessage["XML_PARSE"], __name__)
            self.common_util_log.logging(
                "receive_device",
                self.log_level_debug,
                ("xml_error_message = %s (receive_message = %s)" %
                 (ex_message, receive_message)),
                __name__)
        self.common_util_log.logging(
            "receive_device", self.log_level_debug,
            "parse_xml_obj = %s " % (xml_obj,), __name__)
        return xml_obj

    @decorater_log
    def _comparsion_sw_db_l2_slice(self, message, db_info):
        self.common_util_log.logging(
            " ",
            self.log_level_error,
            self.Logmessage["Call_NG_Method"] %
            ("_comparsion_sw_db_l2_slice"),
            __name__)
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "params : message = %s ,db_info = %s" % (message, db_info),
            __name__)
        return False

    @decorater_log
    def _comparsion_sw_db_l3_slice(self, message, db_info):
        self.common_util_log.logging(
            " ",
            self.log_level_error,
            self.Logmessage["Call_NG_Method"] %
            ("_comparsion_sw_db_l3_slice"),
            __name__)
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "params : message = %s ,db_info = %s" % (message, db_info),
            __name__)
        return False
