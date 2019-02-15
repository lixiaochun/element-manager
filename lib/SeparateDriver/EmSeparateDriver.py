# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2018 Nippon Telegraph and Telephone Corporation
# Filename: EmSeparateDriver.py
'''
Individual section on deriver (base class)
'''
import json
import os
import re
import imp
import traceback
from codecs import BOM_UTF8
from lxml import etree
import ipaddress
import GlobalModule
import copy
from EmCommonLog import decorater_log
from EmCommonLog import decorater_log_in_out
from EmNetconfProtocol import EmNetconfProtocol
from EmDriverCommonUtilityDB import EmDriverCommonUtilityDB
from EmDriverCommonUtilityLog import EmDriverCommonUtilityLog


class EmSeparateDriver(object):
    '''
    Individual section on deriver (base class)
    '''

    Logmessage = {"XML_PARSE": "XML Parser Error",
                  "Control_Classification": "Control Classification Error",
                  "Signal_Editing": "Signal Editing Error",
                  "info_compare": "Information Compare Error",
                  "Interworking": "Interworking Error",
                  "Validation": "Validation Error",
                  "Call_NG_Method": "Call EmSeparateDriver IF: %s NG",
                  "NetConf_Fault": "Could not %s Device ERROR",
                  "Recover": "Rebuild recover message Error  %s",
                  "RecoverUtilSelect": "Recover Service Utility Select NG %s"}

    log_level_debug = "DEBUG"
    log_level_warn = "WARN"
    log_level_info = "INFO"
    log_level_error = "ERROR"

    re_rpc_error = re.compile("<rpc-error>")

    _send_message_top_tag = "config"

    _update_ok = 1
    _update_validation_ng = 2
    _update_error = 3

    _if_type_lag = "lag-if"
    _if_type_phy = "physical-if"

    _node_type_leaf = "Leaf"
    _node_type_b_leaf = "B-Leaf"
    _node_type_spine = "Spine"

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''
        self.name_spine = GlobalModule.SERVICE_SPINE
        self.name_leaf = GlobalModule.SERVICE_LEAF
        self.name_l2_slice = GlobalModule.SERVICE_L2_SLICE
        self.name_l3_slice = GlobalModule.SERVICE_L3_SLICE
        self.name_celag = GlobalModule.SERVICE_CE_LAG
        self.name_internal_link = GlobalModule.SERVICE_INTERNAL_LINK
        self.name_b_leaf = GlobalModule.SERVICE_B_LEAF
        self.name_breakout = GlobalModule.SERVICE_BREAKOUT
        self.name_cluster_link = GlobalModule.SERVICE_CLUSTER_LINK
        self.name_recover_node = GlobalModule.SERVICE_RECOVER_NODE
        self.name_recover_service = GlobalModule.SERVICE_RECOVER_SERVICE
        self.name_acl_filter = GlobalModule.SERVICE_ACL_FILTER

        self._MERGE = GlobalModule.ORDER_MERGE
        self._DELETE = GlobalModule.ORDER_DELETE
        self._REPLACE = GlobalModule.ORDER_REPLACE

        self._ATRI_OPE = "operation"

        self._gen_message_methods = {
            self.name_spine: (self._gen_spine_fix_message,
                              self._gen_spine_variable_message),
            self.name_leaf: (self._gen_leaf_fix_message,
                             self._gen_leaf_variable_message),
            self.name_b_leaf: (self._gen_leaf_fix_message,
                               self._gen_leaf_variable_message),
            self.name_l2_slice: (self._gen_l2_slice_fix_message,
                                 self._gen_l2_slice_variable_message),
            self.name_l3_slice: (self._gen_l3_slice_fix_message,
                                 self._gen_l3_slice_variable_message),
            self.name_celag: (self._gen_ce_lag_fix_message,
                              self._gen_ce_lag_variable_message),
            self.name_internal_link:
                (self._gen_internal_link_fix_message,
                 self._gen_internal_link_variable_message),
            self.name_breakout: (self._gen_breakout_fix_message,
                                 self._gen_breakout_variable_message),
            self.name_cluster_link: (self._gen_cluster_link_fix_message,
                                     self._gen_cluster_link_variable_message),
            self.name_acl_filter: (self._gen_acl_filter_fix_message,
                                   self._gen_acl_filter_variable_message),
        }

        self._validation_methods = {
            self.name_spine: self._validation_spine,
            self.name_leaf: self._validation_leaf,
            self.name_b_leaf: self._validation_b_leaf,
            self.name_l2_slice: self._validation_l2_slice,
            self.name_l3_slice: self._validation_l3_slice,
            self.name_celag: self._validation_ce_lag,
            self.name_internal_link: self._validation_internal_link,
            self.name_breakout: self._validation_breakout,
            self.name_cluster_link: self._validation_cluster_link,
            self.name_acl_filter: self._validation_acl_filter,
        }

        self.net_protocol = EmNetconfProtocol()
        self.common_util_db = EmDriverCommonUtilityDB()
        self.common_util_log = EmDriverCommonUtilityLog()
        self.list_enable_service = []
        self.get_config_message = {}

        self.lib_path = GlobalModule.EM_LIB_PATH

        self.internal_link_vlan_config = self._get_internal_link_vlan_config()

    @decorater_log_in_out
    def connect_device(self, device_name,
                       device_info, service_type, order_type):
        '''
        Driver individual section connection control.
            Launch from the common section on driver,
            conduct device connection control to protocol processing section.
        Parameter:
            device_name : Device name
            device_info : Device information
            service_type : Service type
            order_type : Order type
        Return value :
            Protocol processing section response : int (1:Normal, 2:Capability abnormal, 3:No response)
        '''
        self.common_util_log.logging(
            device_name, self.log_level_debug,
            "order_type=%s" % (order_type,), __name__)
        if self._check_service_type(device_name, service_type) is False:
            return 3
        return self.net_protocol.connect_device(device_info)

    @decorater_log_in_out
    def update_device_setting(self, device_name,
                              service_type, order_type, ec_message=None):
        '''
        Driver individual section edit control.
            Launch from the common section on driver,
        Parameter:
            device_name : Device name
            service_type : Service type
            order_type : Order type
            ec_message : EC message
        Return value :
            Processing finish status : int (1:Successfully updated
                                2:Validation check NG
                                3:Updating unsuccessful)
        '''
        self.common_util_log.logging(
            device_name, self.log_level_debug,
            "order_type=%s" % (order_type,), __name__)
        if not self._check_service_type(device_name, service_type) or \
                not self._send_control_signal(device_name, "discard-changes")[0] or \
                not self._send_control_signal(device_name, "lock")[0]:
            return self._update_error

        if service_type == self.name_recover_node or\
                service_type == self.name_recover_service:
            result = self._update_device_setting_recover(
                device_name, service_type, order_type, ec_message)
        else:
            result = self._update_device_setting_other(
                device_name, service_type, order_type, ec_message)
        return result

    @decorater_log
    def _update_device_setting_recover(self, device_name, service_type,
                                       order_type, ec_message=None):
        '''
        Selection of Utility for Recovery
            Generate instance of the applicable utility for recovery
        Parameter:
            device_name : Device name
            service_type : Service type
            order_type : Order type
         Return value :
            Processing finish status : int (1:Successfully updated
                                2:Validation check NG
                                3:Updating unsuccessful)
        '''
        recover_util_cls_dict = self._get_recover_list(service_type)

        if service_type == self.name_recover_node:
            for _, value in sorted(recover_util_cls_dict.items()):
                target_recover_util_class_ins = self._select_recover_util(
                    value[1])
                tmp_ec = copy.copy(ec_message)
                tmp_ec_json = json.loads(tmp_ec)

                if not target_recover_util_class_ins:
                    result = self._update_error
                    break
                elif tmp_ec_json["device"]["node-type"].lower() == value[0]:
                    result = self._update_device_setting_recover_node(
                        device_name, order_type, value[0],
                        target_recover_util_class_ins, ec_message=ec_message)
        else:
            result = self._update_device_setting_recover_service(
                device_name, order_type,
                ec_message=ec_message)

        return result

    @decorater_log
    def _get_recover_list(self, service_type):
        '''
        Obtain list of service applicable for service restoration based on service definition config.
        Parameter：
            None
        Return Value：
            Service LIst : dict
                {Restoration Order:(Service type, Applicable utility class name),.....}
        '''
        recover_node_list, recover_service_list = \
            GlobalModule.EM_CONFIG.read_service_conf_recover()

        if service_type == self.name_recover_node:
            recover_util_cls_dict = recover_node_list
        else:
            recover_util_cls_dict = recover_service_list

        return recover_util_cls_dict

    @decorater_log
    def _select_recover_util(self, recover_util_cls_name):
        '''
        Create utility instance for restoration
            Create instance of the applicable utility for restoration
        Parameter：
            recover_util_cls_name：Name of utility class for restoration
        Return value :
            Instance of utlitiy class for restoration
        '''

        try:
            filepath, filename, data =\
                imp.find_module(recover_util_cls_name,
                                [os.path.join(
                                    self.lib_path,
                                    'SeparateDriver/RecoverUtility')])
            target_recover_util_module =\
                imp.load_module(
                    recover_util_cls_name, filepath, filename, data)
            target_recover_util_class_ins =\
                getattr(target_recover_util_module, recover_util_cls_name)()

            return target_recover_util_class_ins

        except (AttributeError, ImportError, IOError) as e:
            self.common_util_log.logging(
                "", self.log_level_error,
                self.Logmessage["RecoverUtilSelect"] % (
                    recover_util_cls_name,),
                __name__)
            return None

    @decorater_log
    def _update_device_setting_recover_node(self,
                                            device_name,
                                            order_type,
                                            recover_service_type,
                                            recover_service_util_ins,
                                            ec_message=None):
        '''
        Edit control of individual section on driver
            Conduct processing of service for restoration expansion
            Get launched from driver common section,
            and send device control signal to protocol processing section
        Parameter:
            device_name : Device name
            order_type : Order type
            recover_service_type : Service to be restored(leaf,b-leaf,etc)
            recover_service_util_ins : Utility class instance to be restored
            ec_message : EC message
        Return value :
            Processing finish status : int (1:Successfully updated
                                2:Validation check NG
                                3:Updating unsuccessful)
        '''
        service_type = self.name_recover_node

        is_db_result, device_info = \
            self.common_util_db.read_configureddata_info(
                device_name, service_type)
        if not is_db_result:
            return self._update_error

        create_result, _, recover_ec_message = \
            recover_service_util_ins.create_recover_message(
                ec_message, device_info, service_type)

        if not create_result or recover_ec_message is None:
            self.common_util_log.logging(device_name, self.log_level_warn,
                                         self.Logmessage["Recover"] %
                                         (recover_service_type.upper(),),
                                         __name__)
            return self._update_error

        result = self._edit_config_for_recover(
            device_name, recover_service_type,
            None, recover_ec_message)
        if result != self._update_ok:
            self.common_util_log.logging(device_name, self.log_level_debug,
                                         "edit-config error result=%s" %
                                         result, __name__)
            return result

        if not self._send_control_signal(device_name,
                                         "validate",
                                         service_type)[0]:
            self.common_util_log.logging(device_name, self.log_level_debug,
                                         "validate error result=%s" %
                                         result, __name__)
            return self._update_error
        return self._update_ok

    @decorater_log
    def _update_device_setting_recover_service(self,
                                               device_name,
                                               order_type,
                                               ec_message=None):
        '''
        Driver individual section edit control.
            Implement processing of "recover service".
            Launch from the common section on driver,
            transmit device control signal to protocol processing section.
        Parameter:
            device_name : Device name
            order_type : Order type
            ec_message : EC message
        Return value :
            Processing finish status : int (1:Successfully updated
                                2:Validation check NG
                                3:Updating unsuccessful)
        '''
        service_type = self.name_recover_service

        is_db_result, device_info = \
            self.common_util_db.read_configureddata_info(
                device_name, service_type)
        if not is_db_result:
            return self._update_error

        recover_util_cls_dict = self._get_recover_list(service_type)

        result = self._update_ok

        for _, value in sorted(recover_util_cls_dict.items()):
            target_recover_util_class_ins = self._select_recover_util(
                value[1])
            if not target_recover_util_class_ins:
                result = self._update_error
                break

            create_result, recover_db_info_list, recover_ec_message_list = \
                target_recover_util_class_ins.create_recover_message(
                    ec_message, device_info, service_type)
            if not create_result:
                self.common_util_log.logging(
                    device_name, self.log_level_warn,
                    self.Logmessage["Recover"] %
                    (value[0].upper(),), __name__)
                result = self._update_error
                break

            if isinstance(recover_ec_message_list, list):
                idx = 0
                for idx in range(len(recover_ec_message_list)):
                    recover_db_info = recover_db_info_list[idx]
                    recover_ec_message = recover_ec_message_list[idx]
                    result = self._edit_config_for_recover(
                        device_name, value[0],
                        recover_db_info, recover_ec_message)
                    if result != self._update_ok:
                        self.common_util_log.logging(
                            device_name, self.log_level_debug,
                            "edit-config error [%s] result=%s" %
                            (value[0].upper(), result,), __name__)
                        break
                if result != self._update_ok:
                    break
            elif recover_ec_message_list is not None:
                result = self._edit_config_for_recover(
                    device_name, value[0], recover_db_info_list,
                    recover_ec_message_list)

                if result != self._update_ok:
                    self.common_util_log.logging(
                        device_name, self.log_level_debug,
                        "edit-config error [%s] result=%s" %
                        (value[0].upper(), result,), __name__)
                    break
        if result == self._update_ok:
            if not self._send_control_signal(device_name,
                                             "validate",
                                             service_type)[0]:
                return self._update_error

        return result

    @decorater_log
    def _update_device_setting_other(self, device_name,
                                     service_type, order_type,
                                     ec_message=None):
        '''
        Driver individual section edit control.
            Perform processing of services other than "recover node" and "recover service"
            Launch from the common section on driver,
            transmit device control signal to protocol processing section.
        Parameter:
            device_name : Device name
            service_type : Service type
            order_type : Order type
            ec_message : EC message
        Return value :
            Processing finish status : int (1:Successfully updated
                                2:Validation check NG
                                3:Updating unsuccessful)
        '''

        is_db_result, device_info = \
            self.common_util_db.read_configureddata_info(
                device_name, service_type)
        if not is_db_result:
            return self._update_error
        is_message_result, send_message = self._gen_message(
            device_name, service_type, device_info, ec_message, order_type)
        if not is_message_result:
            return self._update_error
        if not self._validation(device_name, service_type, ec_message):
            return self._update_validation_ng
        if (self._send_control_signal(device_name,
                                      "edit-config",
                                      send_message,
                                      service_type,
                                      order_type)[0] is False or
                self._send_control_signal(device_name,
                                          "validate")[0] is False):
            return self._update_error
        else:
            return self._update_ok

    @decorater_log_in_out
    def delete_device_setting(self, device_name,
                              service_type, order_type, ec_message=None):
        '''
        Driver individual section deletion control.
            Launch from the common section on driver,
            conduct device deletion control to protocol processing section.
        Parameter:
            device_name : Device name
            service_type : Service type
            order_type : Order type
            diff_info : Information on difference
        Return value :
            Processing finish status : int (1:Successfully deleted
                                2:Validation check NG
                                3:Deletion unsuccessful)
        '''
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
            device_name, service_type, device_info, ec_message, order_type)
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

    @decorater_log_in_out
    def reserve_device_setting(self, device_name, service_type, order_type):
        '''
        Driver individual section tentative setting control.
            Launch from the common section on driver,
            conduct device tentative setting control to protocol processing section.
        Parameter:
            device_name : Device name
            service_type : Service type
            order_type : Order type
        Return value :
            Processing finish status : Boolean (True:Normal, False:Abnormal)
        '''
        self.common_util_log.logging(
            device_name, self.log_level_debug,
            "order_type=%s" % (order_type,), __name__)
        if self._check_service_type(device_name, service_type) is False:
            return False
        return self._send_control_signal(device_name, "confirmed-commit")[0]

    @decorater_log_in_out
    def enable_device_setting(self, device_name, service_type, order_type):
        '''
        Driver individual section established control.
            Launch from the common section on driver,
            conduct device established control to protocol processing section.
        Parameter:
            device_name : Device name
            service_type : Service type
            order_type : Order type
        Return value :
            Processing finish status : Boolean (True:Normal, False:Abnormal)
        '''
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

    @decorater_log_in_out
    def disconnect_device(self, device_name, service_type, order_type):
        '''
        Driver individual section disconnection control.
            Launch from the common section on driver,
            conduct device disconnection control to protocol processing section.
        Parameter:
            device_name : Device name
            service_type : Service type
            order_type : Order type
        Return value :
            Processing finish status : Should always return "True"
        '''
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

    @decorater_log_in_out
    def get_device_setting(self,
                           device_name,
                           service_type,
                           order_type):
        '''
        Driver individual section acquisition control.
            Launch from the common section on driver,
            conduct device acquisition control to protocol processing section.
        Parameter:
            device_name : Device name
            service_type : Service type
            order_type : Order type
        Return value :
            Processing finish status : Boolean (True:Normal, False:Abnormal)
            Device response signal : Str
        '''
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

    @decorater_log_in_out
    def execute_comparing(self, device_name,
                          service_type, order_type, device_signal):
        '''
        Driver individual section matching control.
            Launch from the common section on driver,
            conduct device matching control to protocol processing section.
        Parameter:
            device_name : Device name
            service_type : Service type
            order_type : Order type
            device_signal : Device signal (Use the device signal obtained by acquisition control as the argument.)
        Return value :
            Processing finish status : Boolean (True:Normaal,  False:Abnormal)
        '''
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
        '''
        Service type analysis
            Called out when starting external IF, check whether service type is suitable.
        Parameter:

            device_name : service_type
            service_type : Service type
        Return value
            Service analysis result : Boolena (Should say "True" no problems with service type)
        '''

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
        '''
        Send message to protocol processing section.
        Parameter:
            device_name ; Device name
            message_type ; Message type
            send_message : Send message
            service_type : Service type
            operation : Operation
        Return value.
            Processed result ; Boolean result of send_control_signal)
            Message ; str Result of send_control_signal)
        '''
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
        '''
        Create message to be sent for Netconf
            Called out before executing get-config and edit-config.
        Parameter:
            device_name : Device name
            service_type : Service type
            device_info : Device information
            ec_message : EC message
            operation : Operation attribute (Set "delete" if the function is "delete function".)
        Return value:
            Creation result ; Boolean
        '''

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

        if service_type in self._gen_message_methods:
            is_message_gen_result, send_message = self._gen_message_child(
                parse_json,
                ec_json,
                operation,
                self._gen_message_methods[service_type][0],
                self._gen_message_methods[service_type][1],
                top_tag_mes)
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
                           top_tag=None):
        '''
        Method to create each message.
            Called out when service type is judged and message writing is created for each message.
        Parameter:
            device_info : DB information
            ec_message : EC message
            operation : Order type(only whether Delete or not)
            method_fix_message_gen : Method to create fixed message
            method_variable_message_gen : Method to create variable message
        Return value.
            Message creation result: Boolean
            Created message: str
        '''
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
        '''
        Can be created by designating XML object, putting name on tag. Designate attribute if there are any.
        If tag is carrying information which contains some settings, conduct setting as required.
            Should be called out when creating XML, like messages.
        Parameter:
            parent : Parent node object
            tag : Tag name
            attr_key : Attribute's key (No need to set if "None")
            attr_value : Attribute's value (No need to set if "None")
            text : Value in the tag (Should be blank and nothing exists in the tag in case of "None".)
        Return value
            Child node : Node object
        '''
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
        '''
        Designate XML object, search the tag.
            Called out when creating node under corresponding parent node in variable section.
        Parameter:
            parent : Parent node object
            *tag : Designate tag name one by one. (tag1,tag2,tag3...)
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

    @decorater_log
    def _set_xml_tag_variable(self, parent, tag, text, *tags):
        '''
        Designate XML object, search the tag.
        Input texts as designated.
            Called out when text is inserted in variable section.
        Parameter:
            parent : Parent node object
            text
            *tag : Designate tag name one by one.
        Return value
            Child node : Node object
        '''
        target_node = None
        tmp = self._find_xml_node(parent, *tags)
        if tmp is not None:
            target_node = tmp.find(tag)
            if target_node is not None:
                target_node.text = text

        return target_node

    @decorater_log
    def _set_ope_delete_tag(self, node, tag, operation, text=None):
        '''
        Create tag for deletion control. (Give an attribute of operation="delete" when operation is delete.)
        (No attributes should be added if nothing.)
        Parameter:
            node: xml object
            tag : Tag name
            operation : Control signal
            text : Text for tag
        Return value
            Created tag : xml object
        '''
        if operation == "delete":
            return self._set_xml_tag(node, tag, "operation", "delete", text)
        else:
            return self._set_xml_tag(node, tag, None, None, text)

    @decorater_log
    def _xml_setdefault_node(self, parent, tag):
        '''
        Search node by Tag name, return the node if the node exists. Create new node for the Tag name to return, if nothing.
        '''
        tmp_node = self._find_xml_node(parent, tag)
        if tmp_node is None:
            tmp_node = self._set_xml_tag(parent, tag)
        return tmp_node

    @decorater_log
    def _get_attr_from_operation(self, operation=None):
        '''
        Obtain attribute and value based on the operation type.
        '''
        attr = None
        attr_val = None
        if operation == self._DELETE:
            attr = self._ATRI_OPE
            attr_val = self._DELETE
        return attr, attr_val

    @staticmethod
    @decorater_log
    def _conversion_cidr2mask(cidr_val, ip_ver=4):
        '''
        Convert the CIDR texts.
            Called out when packing data linked with prefix judged by value from DB into message.
        Parameter:
            cudr_val : CUDR texts (the spot which says "YY" in the "XXX.XXX.XXX.XXX/YY" (0-32))
        Return value:
            Converted IP address  ; str  (XXX.XXX.XXX.XXX)
        '''
        if ip_ver == 4:
            tmp_addr = u"0.0.0.0/%d" % (cidr_val,)
        else:
            tmp_addr = u"0::/%d" % (cidr_val,)

        return str(ipaddress.ip_network(tmp_addr).netmask)

    @decorater_log
    def _validation(self, device_name, service_type, device_info):
        '''
        Validation check
            Called out when creating message
        Parameter:
            device_name : Device name
            service_type : Service type
            message : Check message
        '''

        is_vld_check = False
        parse_json = json.loads(device_info)
        if service_type in self._validation_methods:
            is_vld_check = self._validation_methods[service_type](parse_json)
        if is_vld_check is False:
            self.common_util_log.logging(
                device_name,
                self.log_level_warn,
                self.Logmessage["Validation"],
                __name__)
        return is_vld_check

    @decorater_log
    def _comparsion_process_sw_db(self, device_name,
                                  service_type, receive_message, db_info):
        '''
        SW-DB comparison processing(Information matching check)
            Get called out after obtaining db data
        Parameter:
            device_name : Device name
            service_type : Service type
            receive_message : Check message
            db_info : Device information(Information from DB)
        '''
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
        '''
        Compare two items which have been obtained asthe argument
        Argument:
            netconf_val:Object to be compared (node tag)
            db_val: Object to be compared
        Return value
            Comparison result : true,false
        '''
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
        '''
        Fixed value to create message (spine) for Netconf.
            Called out when creating message for Spine.
        Parameter:
            xml_obj : xml object
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean (Write properly using override method.)
        '''
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
        '''
        Fixed value to create message (Leaf) for Netconf.
            Called out when creating message for Leaf.
        Parameter:
            xml_obj : xml object
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean (Write properly using override method.)
        '''
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
        '''
        Fixed value to create message (L2Slice) for Netconf.
            Called out when creating message for L2Slice.
        Parameter:
            xml_obj : xml object
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean (Write properly using override method.)
        '''
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
        '''
        Fixed value to create message (L3Slice) for Netconf.
            Called out when creating message for L3Slice.
        Parameter:
            xml_obj : xml object
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean (Write properly using override method.)
        '''
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
        '''
        Fixed value to create message (CeLag) for Netconf.
            Called out when creating message for CeLag.
        Parameter:
            xml_obj : xml object
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean (Write properly using override method.)
        '''
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
    def _gen_internal_link_fix_message(self, xml_obj, operation):
        '''
        Fixed value to create message (InternalLink) for Netconf.
            Called out when creating message for InternalLink.
        Parameter:
            xml_obj : xml object
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean (Write properly using override method.)
        '''
        self.common_util_log.logging(
            " ",
            self.log_level_error,
            self.Logmessage["Call_NG_Method"] %
            ("_gen_internal_link_fix_message"),
            __name__)
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "params : xml_obj = %s , operation = %s" % (xml_obj, operation),
            __name__)
        return False

    @decorater_log
    def _gen_breakout_fix_message(self, xml_obj, operation):
        '''
        Fixed value to create message (breakout) for Netconf.
            Called out when creating message for breakout.
        Parameter:
            xml_obj : xml object
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean (Write properly using override method.)
        '''
        self.common_util_log.logging(
            " ",
            self.log_level_error,
            self.Logmessage["Call_NG_Method"] %
            ("_gen_breakout_fix_message"),
            __name__)
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "params : xml_obj = %s , operation = %s" % (xml_obj, operation),
            __name__)
        return False

    @decorater_log
    def _gen_cluster_link_fix_message(self, xml_obj, operation):
        '''
        Fixed value to create message (cluster-link) for Netconf.
            Called out when creating message for cluster-link.
        Parameter:
            xml_obj : xml object
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean (Write properly using override method.)
        '''
        self.common_util_log.logging(
            " ",
            self.log_level_error,
            self.Logmessage["Call_NG_Method"] %
            ("_gen_cluster_link_fix_message"),
            __name__)
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "params : xml_obj = %s , operation = %s" % (xml_obj, operation),
            __name__)
        return False

    @decorater_log
    def _gen_acl_filter_fix_message(self, xml_obj, operation):
        '''
        Fixed value to create message (acl-filter) for Netconf.
            Called out when creating message for acl-filter.
        Parameter:
            xml_obj : xml object
            operation : Designate "delete" when deleting
        Return value
            Creation result : Boolean (Write properly using override method)
        '''
        self.common_util_log.logging(
            " ",
            self.log_level_error,
            self.Logmessage["Call_NG_Method"] %
            ("_gen_acl_filter_fix_message"),
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
        '''
        Variable value to create message (Spine) for Netconf.
            Called out when creating message for Spine. (After fixed message has been created.)
        Parameter:
            xml_obj : xml object
            device_info : Device information
            ec_message : EC message
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean (Write properly using override method)
        '''
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
        '''
        Variable value to create message (Leaf) for Netconf.
            Called out when creating message for Leaf. (After fixed message has been created.)
        Parameter:
            xml_obj : xml object
            device_info : Device information
            ec_message : EC message
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean (Write properly using override method)
        '''
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
        '''
        Variable value to create message (L2Slice) for Netconf.
            Called out when creating message for L2Slice. (After fixed message has been created.)
        Parameter:
            xml_obj : xml object
            device_info : Device information
            ec_message : EC message
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean (Write properly using override method)
        '''
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
        '''
        Variable value to create message (L3Slice) for Netconf.
            Called out when creating message for L3Slice. (After fixed message has been created.)
        Parameter:
            xml_obj : xml object
            device_info : Device information
            ec_message : EC message
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean (Write properly using override method)
        '''
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
        '''
        Variable value to create message (CeLag) for Netconf.
            Called out when creating message for CeLag. (After fixed message has been created.)
        Parameter:
            xml_obj : xml object
            device_info : Device information
            ec_message : EC message
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean (Write properly using override method)
        '''
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
    def _gen_internal_link_variable_message(self,
                                            xml_obj,
                                            device_info,
                                            ec_message,
                                            operation):
        '''
        Variable value to create message (InternalLink) for Netconf.
            Called out when creating message for InternalLink. (After fixed message has been created.)
        Parameter:
            xml_obj : xml object
            device_info : Device information
            ec_message : EC message
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean (Write properly using override method)
        '''
        self.common_util_log.logging(
            " ",
            self.log_level_error,
            self.Logmessage["Call_NG_Method"] %
            ("_gen_internal_link_variable_message"),
            __name__)
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "params : xml_obj=%s ,device_info=%s ,ec_message=%s operation=%s" %
            (xml_obj, device_info, ec_message, operation),
            __name__)
        return False

    @decorater_log
    def _gen_breakout_variable_message(self,
                                       xml_obj,
                                       device_info,
                                       ec_message,
                                       operation):
        '''
        Variable value to create message (breakout) for Netconf.
            Called out when creating message for breakout. (After fixed message has been created.)
        Parameter:
            xml_obj : xml object
            device_info : Device information
            ec_message : EC message
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean (Write properly using override method)
        '''
        self.common_util_log.logging(
            " ",
            self.log_level_error,
            self.Logmessage["Call_NG_Method"] %
            ("_gen_breakout_variable_message"),
            __name__)
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "params : xml_obj=%s ,device_info=%s ,ec_message=%s operation=%s" %
            (xml_obj, device_info, ec_message, operation),
            __name__)
        return False

    @decorater_log
    def _gen_cluster_link_variable_message(self,
                                           xml_obj,
                                           device_info,
                                           ec_message,
                                           operation):
        '''
        Variable value to create message (cluster-link) for Netconf.
            Called out when creating message for cluster-link. (After fixed message has been created.)
        Parameter:
            xml_obj : xml object
            device_info : Device information
            ec_message : EC message
            operation : Designate "delete" when deleting.
        Return value.
            Creation result : Boolean (Write properly using override method)
        '''
        self.common_util_log.logging(
            " ",
            self.log_level_error,
            self.Logmessage["Call_NG_Method"] %
            ("_gen_cluster_link_variable_message"),
            __name__)
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "params : xml_obj=%s ,device_info=%s ,ec_message=%s operation=%s" %
            (xml_obj, device_info, ec_message, operation),
            __name__)
        return False

    @decorater_log
    def _gen_acl_filter_variable_message(self,
                                         xml_obj,
                                         device_info,
                                         ec_message,
                                         operation):
        '''
        Variable value to create message (acl-filter) for Netconf.
           Called out when creating message for acl-filter(After fixed message has been created)
        Parameter:
            xml_obj : xml object
            device_info : Device information
            ec_message : EC message
            operation : Designate "delete" when deleting
        Return value
            Creation result : Boolean (Write properly using override method)
        '''
        self.common_util_log.logging(
            " ",
            self.log_level_error,
            self.Logmessage["Call_NG_Method"] %
            ("_gen_acl_filter_message"),
            __name__)
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "params : xml_obj=%s ,device_info=%s ,ec_message=%s operation=%s" %
            (xml_obj, device_info, ec_message, operation),
            __name__)
        return False

    @decorater_log
    def _validation_spine(self, device_info):
        '''
        Validation check(Spine)
            Called out when doing Validation check for Spine.
        Parameter:
            device_info : Device information
        Return value :
            Checked result : Boolean (Should always be "True" unless override occurs.)
        '''
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "%s validation is ok : device_info = %s" %
            (self.name_spine, device_info), __name__)
        return True

    @decorater_log
    def _validation_leaf(self, device_info):
        '''
        Validation check(Leaf)
            Called out when doing Validation check for Leaf.
        Parameter:
            device_info : Device information
        Return value :
            Checked result : Boolean (Should always be "True" unless override occurs.)
        '''
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "%s validation is ok : device_info = %s" %
            (self.name_leaf, device_info), __name__)
        return True

    @decorater_log
    def _validation_b_leaf(self, device_info):
        '''
        Validation check(B-Leaf)
            Called out when doing Validation check for B-Leaf.
        Parameter:
            device_info : Device information
        Return value :
            Checked result : Boolean (Should always be "True" unless override occurs.)
        '''
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "%s validation is ok : device_info = %s" %
            (self.name_b_leaf, device_info), __name__)
        return True

    @decorater_log
    def _validation_l2_slice(self, device_info):
        '''
        Validation check(L2Slice)
            Called out when doing Validation check for L2Slice.
        Parameter:
            device_info : Device information
        Return value :
            Checked result : Boolean (Should always be "True" unless override occurs.)
        '''
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "%s validation is ok : device_info = %s" %
            (self.name_l2_slice, device_info), __name__)
        return True

    @decorater_log
    def _validation_l3_slice(self, device_info):
        '''
        Validation check(L3Slice)
            Called out when doing Validation check for L3Slice.
        Parameter:
            device_info : Device information
        Return value :
            Checked result : Boolean (Should always be "True" unless override occurs.)
        '''
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "%s validation is ok : device_info = %s" %
            (self.name_l3_slice, device_info), __name__)
        return True

    @decorater_log
    def _validation_ce_lag(self, device_info):
        '''
        Validation check(CeLag)
            Called out when doing Validation check for CeLag.
        Parameter:
            device_info : Device information
        Return value :
            Checked result : Boolean (Should always be "True" unless override occurs.)
        '''
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "%s validation is ok : device_info = %s" %
            (self.name_celag, device_info), __name__)
        return True

    @decorater_log
    def _validation_internal_link(self, device_info):
        '''
        Validation check(InternalLink)
            Called out when doing Validation check for InternalLink.
        Parameter:
            device_info : Device information
        Return value :
            Checked result : Boolean (Should always be "True" unless override occurs.)
        '''
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "%s validation is ok : device_info = %s" %
            (self.name_internal_link, device_info), __name__)
        return True

    @decorater_log
    def _validation_breakout(self, device_info):
        '''
        Validation check(breakout)
            Called out when doing Validation check for breakout.
        Parameter:
            device_info : Device information
        Return value :
            Checked result : Boolean (Should always be "True" unless override occurs.)
        '''
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "%s validation is ok : device_info = %s" %
            (self.name_breakout, device_info), __name__)
        return True

    @decorater_log
    def _validation_cluster_link(self, device_info):
        '''
        Validation check(cluster-link)
            Called out when doing Validation check for cluster-link.
        Parameter:
            device_info : Device information
        Return value :
            Checked result : Boolean (Should always be "True" unless override occurs.)
        '''
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "%s validation is ok : device_info = %s" %
            (self.name_cluster_link, device_info), __name__)
        return True

    @decorater_log
    def _validation_acl_filter(self, device_info):
        '''
        Validation check( acl_filter )
            Called out when checking validation of acl_filer
        Parameter:
            device_info : Device informaiton
        Return value :
            Check result : Boolean (Should always be "True" unless override occurs.)
        '''
        self.common_util_log.logging(
            " ", self.log_level_debug,
            "%s validation is ok : device_info = %s" %
            (self.name_acl_filter, device_info), __name__)
        return True

    @decorater_log
    def _parse_receive_info(self, receive_message):
        '''
        Response message analysis(xml)
            Called out before SW-DB comparison processing
        Parameter:
            receive_message : Response message
        Return value :
            Analysis result : XML object
        '''
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
        '''
        SW-DB comparison processing (check for information matching) (L2Slice).
            Called out when checking information matching of L2Slice.
        Parameter:
            message : Response message
            db_info : DB information
        Return value :
            Matching result : Boolean (Should always be "True" unless override occurs.)
        '''
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
        raise ValueError("this service disabled")

    @decorater_log
    def _comparsion_sw_db_l3_slice(self, message, db_info):
        '''
        SW-DB comparison processing (check for information matching) (L3Slice).
            Called out when checking information matching of L3Slice.
        Parameter:
            message : Response message
            db_info : DB information
        Return value :
            Matching result : Boolean (Should always be "True" unless override occurs.)
        '''
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
        raise ValueError("this service disabled")

    @decorater_log
    def _edit_config_for_recover(self, device_name, service_type,
                                 recover_db_info, recover_ec_message):
        '''
        Perform validation (Non device access) and edit-config in recovery.
        Parameter:
            ec_message : Recovery expansion/"recover service" EC message
            db_info : DB information
        Return value :
            Result : Success：_update_ok  Failure：_update_error
        '''
        is_message_result, send_message = self._gen_message(
            device_name, service_type, recover_db_info, recover_ec_message,
            self._MERGE)
        if not is_message_result:
            return self._update_error
        if not self._validation(device_name, service_type,
                                recover_ec_message):
            return self._update_validation_ng
        if not self._send_control_signal(device_name,
                                         "edit-config",
                                         send_message,
                                         service_type)[0]:
            return self._update_error
        return self._update_ok

    def _get_internal_link_vlan_config(self):
        '''
        Read config from conf_internal_link_vlan.conf
        '''
        splitter_conf = '='
        config_path = os.path.join(GlobalModule.EM_CONF_PATH,
                                   'conf_internal_link_vlan.conf')
        try:
            with open(config_path, 'r') as open_file:
                conf_list = open_file.readlines()
        except IOError:
            raise

        os_list = []
        for value in conf_list:
            if not(value.startswith('#')) and splitter_conf in value:
                tmp_line = value.strip()
                tmp_line = tmp_line.replace(BOM_UTF8, '')
                os_name = tmp_line.split(splitter_conf)[1]
                os_list.append(os_name)

        self.common_util_log.logging(None,
                                     self.log_level_debug,
                                     "vlan_IL_list={0}".format(os_list),
                                     __name__)
        return os_list
