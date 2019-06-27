#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: CumulusDriver.py
from __builtin__ import True

'''
Cumulus Driver Module
'''
import json
import traceback
import ipaddress
import copy
import re

from CLIDriver import CLIDriverBase
from CumulusCLIProtocol import CumulusCLIProtocol
from EmCommonLog import decorater_log
from EmCommonLog import decorater_log_in_out
import GlobalModule


class CumulusDriver(CLIDriverBase):
    '''
    Cumulus Driver Class
    '''

    _DEFAULT_INTERNAL_LINK_COST = 100

    _DELETE_CLAG_ID_FLAG = -1

    _Q_IN_Q_DEVICE_UNIT = "selectable_by_node"
    _Q_IN_Q_VLANIF_UNIT = "selectable_by_vlan_if"

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''
        error_mes_list = ["ERROR:"]
        self.as_super = super(CumulusDriver, self)
        self.as_super.__init__()
        self.net_protocol = CumulusCLIProtocol(
            error_recv_message=error_mes_list,
            connected_recv_message=CumulusCLIProtocol._CUMULU_USER_RECV_MES)

        self.list_enable_service = [self.name_spine,
                                    self.name_leaf,
                                    self.name_l2_slice,
                                    self.name_celag,
                                    self.name_internal_link,
                                    self.name_recover_node,
                                    self.name_recover_service,
                                    self.name_acl_filter,
                                    self.name_if_condition,
                                    ]

        self._recv_message = CumulusCLIProtocol._CUMULU_USER_RECV_MES
        self._password = None
        self.driver_public_method["compare_to_latest_device_configuration"] = (
            self.compare_to_latest_device_configuration)
        self.get_config_default = [("net show configuration commands",
                                    self._recv_message)]

    @decorater_log_in_out
    def connect_device(self,
                       device_name,
                       device_info,
                       service_type,
                       order_type):
        '''
       Connection Control of Individual Section on Driver
            Launch from driver common section,
            execute device connecion control to protocol processing section
        Parameter:
            device_name : Device name
            device_info : Device information
            service_type : Service type
            order_type : Order type
        Return value :
            Response of protocol processing section : int (1:Normal, 3:No response)
        '''
        if service_type == self.name_l2_slice:
            self.net_protocol.is_operation_policy_d = True
        ret_val = self.as_super.connect_device(device_name,
                                               device_info,
                                               service_type,
                                               order_type)
        parse_json = json.loads(device_info)
        self._password = parse_json["device_info"]["password"]
        return ret_val

    @decorater_log_in_out
    def disconnect_device(self,
                          device_name,
                          service_type=None,
                          order_type=None,
                          get_config_flag=True):
        '''
        Driver individual disconnection control
            Initiate from driver common part and request protcol processing  part
            to disconnect with device.
        Argument:
            device_name : device name
            service_type : service type
            order_type : order type
            get_config_flag: Flag to obtain device config(except for in config Audit）
        Return value:
            process termination status: Return always True. 
        '''

        is_get_ok = self._write_device_setting(device_name, get_config_flag)

        is_disconnect_device_ok = self.as_super.disconnect_device(device_name,
                                                                  service_type,
                                                                  order_type,
                                                                  get_config_flag)

        ret_val = is_get_ok and is_disconnect_device_ok

        return ret_val

    @decorater_log_in_out
    def get_device_setting(self,
                           device_name,
                           service_type=None,
                           order_type=None,
                           ec_message=None):
        '''
        Driver individual obtaining control
            Initiate from driver common part and request protcol processing  part
            to obtain device.
        Argument:
            device_name : device name
            service_type : service type
            order_type : order type
            ec_message : EC message
        Return value:
            process termination status : Boolean (True:normal, False:fail)
            signal for device response : Str
        '''
        is_result, conf_str = (
            self.as_super.get_device_setting(device_name,
                                             service_type,
                                             order_type,
                                             ec_message))
        if is_result:
            conf_str = self._shaping_get_config(conf_str)
        return is_result, conf_str


    @decorater_log
    def _shaping_get_config(self, conf_str):
        '''
        Form get-config result.
        (only add/del between  net del all and net commit are extracted)
        Argument:
            conf_str : obtained device setting  str
        Return value:
            formed device setting ; str
        '''
        re_conf = re.compile("^net (commit|add|del).*")
        no_br = conf_str.splitlines()
        str_br = conf_str.splitlines(True)
        start = no_br.index("net del all") if "net del all" in no_br else 0
        end = (
            no_br.index("net commit") if "net commit" in no_br else len(no_br))
        tmp = [line for line in str_br[start:end + 1] if re_conf.search(line)]
        return "".join(tmp)

    @decorater_log
    def _set_sudo_command(self, send_command, recv_command):
        comm_list = []
        sudo_send_comm = "sudo -k {0}".format(send_command)
        comm_list.append((sudo_send_comm, "\[sudo\] password for cumulus:"))
        comm_list.append((self._password, recv_command))
        return comm_list

    @decorater_log
    def _set_sudo_echo_command(self, send_command, recv_command):
        tmp = 'sh -c "{0}"'.format(send_command)
        return self._set_sudo_command(tmp, recv_command)

    @decorater_log
    def _gen_spine_variable_message(self,
                                    device_info,
                                    ec_message,
                                    operation):
        '''
        Variable value to create message for CLI(Spine)
            Called out when creating message for Spine
        Parameter:
            device_info : Device information
            ec_message : EC message
            operation : Designate "delete" when deleting
        Return value
            Creation command list : list [ command (str) , recv_message(str) ]
            Execute raise when error occurs
        '''

        return self._gen_node_add_variable_message(self._node_type_spine,
                                                   device_info,
                                                   ec_message,
                                                   operation)

    @decorater_log
    def _gen_leaf_variable_message(self,
                                   device_info,
                                   ec_message,
                                   operation):
        '''
        Variable value to create message CLI (Leaf)
            Called out when creating message for Leaf.
        Parameter:
            device_info : Device information (DB)
            ec_message : EC message
            operation : Designate "delete" when deleting
        Return value
            Creation command list : list [ command (str) , recv_message(str) ]
            Execute raise when error occurs
        '''

        return self._gen_node_add_variable_message(self._node_type_leaf,
                                                   device_info,
                                                   ec_message,
                                                   operation)

    @decorater_log
    def _gen_internal_link_variable_message(self,
                                            device_info,
                                            ec_message,
                                            operation):
        '''
        Variable value to create message for CLI (InternalLink)
            Called out when creating message for InternalLink.
        Parameter:
            device_info : Device information
            ec_message : EC message
            operation : Designate "delete" when deleting
        Return value
            Creation command list : list [ command (str) , recv_message(str) ]
            Execute raise when error occurs
        '''

        try:
            device_mes = ec_message.get("device", {})

            device_name = device_mes.get("name")

            ospf_area = device_info.get("device", {}).get(
                "ospf", {}).get("area_id")

            if_info = {}
            if device_mes.get("internal-physical"):
                if_info["physical"] = self._get_internal_if_list(
                    device_mes["internal-physical"], device_info, operation)
            if device_mes.get("internal-lag"):
                if_info["lag"] = self._get_internal_if_list(
                    device_mes["internal-lag"], device_info, operation)

            nw_addr_info = self._get_setting_network_addr(if_info,
                                                          device_info,
                                                          operation)

        except Exception as ex:
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "ERROR : message = %s / Exception: %s" % (ec_message, ex),
                __name__)
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "Traceback:%s" % (traceback.format_exc(),),
                __name__)
            return None

        self.common_util_log.logging(
            device_name,
            self.log_level_debug,
            "if_info:{0} , nw_info:{1}".format(if_info, nw_addr_info),
            __name__)
        self.common_util_log.logging(
            device_name,
            self.log_level_debug,
            "ec_message:{0} , db_info:{1}".format(ec_message, device_info),
            __name__)

        comm_internal_link = self._set_command_internal_if(
            if_info, ospf_area, operation=operation, nw_addr_info=nw_addr_info)

        command_list = []
        command_list.extend(comm_internal_link)

        self.common_util_log.logging(
            None,
            self.log_level_debug,
            self._logging_send_command_str(command_list),
            __name__)

        return command_list

    @decorater_log
    def _gen_if_condition_variable_message(self,
                                           device_info,
                                           ec_message,
                                           operation):
        '''
        Variable value to create message for CLI(IfCondtion)
            Called out when creating message for IfCondtion.
        Parameter:
            device_info : Device information
            ec_message : EC message
            operation : Designate "delete" when deleting
        Return value
            Creation command list : list [ command (str) , recv_message(str) ]
            Execute raise when error occurs
        '''

        try:
            device_mes = ec_message.get("device", {})

            device_name = device_mes.get("name")

            if_info = self._get_if_condition_list(
                device_mes, device_info, operation)

        except Exception as ex:
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "ERROR : message = %s / Exception: %s" % (ec_message, ex),
                __name__)
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "Traceback:%s" % (traceback.format_exc(),),
                __name__)
            return None

        comm_if_condition = self._set_command_if_condition(
            if_info, operation=operation)

        command_list = []
        command_list.extend(comm_if_condition)

        self.common_util_log.logging(
            None,
            self.log_level_debug,
            self._logging_send_command_str(command_list),
            __name__)

        return command_list

    @decorater_log
    def _gen_ce_lag_variable_message(self,
                                     device_info,
                                     ec_message,
                                     operation):
        '''
        Variable value to create message for CLI (CE-LAG)
            Called out when creating message for CE-LAG
        Parameter:
            device_info : Device information
            ec_message : EC message
            operation : Designate "delete" when deleting
        Return value
            Creation command list : list [ command (str) , recv_message(str) ]
            Execute raise when error occurs
        '''

        try:
            device_mes = ec_message.get("device", {})

            device_name = device_mes.get("name")

            if_info = self._get_lag_if_list(
                device_mes.get("ce-lag-interface"), device_info, operation)

        except Exception as ex:
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "ERROR : message = %s / Exception: %s" % (ec_message, ex),
                __name__)
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "Traceback:%s" % (traceback.format_exc(),),
                __name__)
            return None

        comm_lag = self._set_command_lag(if_info, operation=operation)

        command_list = []
        command_list.extend(comm_lag)

        self.common_util_log.logging(
            None,
            self.log_level_debug,
            self._logging_send_command_str(command_list),
            __name__)

        return command_list

    @decorater_log
    def _gen_l2_slice_variable_message(self,
                                       device_info,
                                       ec_message,
                                       operation):
        '''
        Variable value to create message for CLI (L2Slice)
            Called out when creating message for L2Slice
        Parameter:
            device_info : Device information
            ec_message : EC message
            operation : Designate "delete" when deleting
        Return value
            Creation command list : list [ command (str) , recv_message(str) ]
            Execute raise when error occurs
        '''

        if operation == self._REPLACE:
            return self._gen_l2_slice_replace_message(device_info,
                                                      ec_message,
                                                      operation)
        elif operation == self._DELETE:
            return self._gen_l2_slice_delete_message(device_info,
                                                     ec_message,
                                                     operation)
        else:
            return self._gen_l2_slice_merge_message(device_info,
                                                    ec_message,
                                                    operation)

    @decorater_log
    def _gen_l2_slice_merge_message(self,
                                    device_info,
                                    ec_message,
                                    operation):
        '''
       Message creation for CLI (L2Slice) - merge
            Called out when creating message for L2Slice(merge)
        Parameter:
            device_info : Device information
            ec_message : EC message
            operation : Designate "delete" when deleting
        Return value
            Creation command list : list [ command (str) , recv_message(str) ]
            Execute raise when error occurs
        '''
        try:
            device_mes = ec_message.get("device-leaf", {})

            device_name = device_mes.get("name")

            merge_info = self._gen_l2_slice_merge_message_for_cmd(
                device_mes, device_info)

        except Exception as ex:
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "ERROR : message = %s / Exception: %s" % (ec_message, ex),
                __name__)
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "Traceback:%s" % (traceback.format_exc(),),
                __name__)
            return None

        self.common_util_log.logging(
            device_name,
            self.log_level_debug,
            "merge_info:{0}".format(merge_info),
            __name__)
        self.common_util_log.logging(
            device_name,
            self.log_level_debug,
            "ec_message:{0} , db_info:{1}".format(ec_message, device_info),
            __name__)


        command_list = []

        comm_qos = self._set_command_l2slice_merge_qos(
            device_mes, device_info, merge_info)
        if comm_qos:
            command_list.extend(comm_qos)

        comm_ifs = self._set_command_l2slice_merge_ifs(
            device_mes, device_info, merge_info)
        if comm_ifs:
            command_list.extend(comm_ifs)

        comm_base = self._set_command_l2slice_merge_base(
            device_mes, device_info, merge_info)
        if comm_base:
            command_list.extend(comm_base)

        comm_irb = self._set_command_l2slice_merge_irb(
            device_mes, device_info, merge_info)
        if comm_irb:
            command_list.extend(comm_irb)

        comm_multi = self._set_command_l2slice_merge_multi(
            device_mes, device_info, merge_info)
        if comm_multi:
            command_list.extend(comm_multi)

        comm_policy = self._set_command_l2slice_merge_policyd(
            device_mes, device_info, merge_info)
        if comm_policy:
            command_list.extend(comm_policy)

        self.common_util_log.logging(
            None,
            self.log_level_debug,
            self._logging_send_command_str(command_list),
            __name__)

        return command_list

    @decorater_log
    def _gen_l2_slice_delete_message(self,
                                     device_info,
                                     ec_message,
                                     operation):
        '''
         Message creation for CLI - delete
            L2Slice(merge)Called out when creating message for
        Parameter:
            device_info : Device information
            ec_message : EC message
            operation : Designate "delete" when deleting
        Return value
            Creation command list : list [ command (str) , recv_message(str) ]
            Execute raise when error occurs
        '''
        try:
            device_mes = ec_message.get("device-leaf", {})

            device_name = device_mes.get("name")

            delete_info = self._gen_l2_slice_delete_message_for_cmd(
                device_mes, device_info)

        except Exception as ex:
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "ERROR : message = %s / Exception: %s" % (ec_message, ex),
                __name__)
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "Traceback:%s" % (traceback.format_exc(),),
                __name__)
            return None

        self.common_util_log.logging(
            device_name,
            self.log_level_debug,
            "delete_info:{0}".format(delete_info),
            __name__)
        self.common_util_log.logging(
            device_name,
            self.log_level_debug,
            "ec_message:{0} , db_info:{1}".format(ec_message, device_info),
            __name__)


        command_list = []

        comm_base = self._set_command_l2slice_delete_base(
            device_mes, device_info, delete_info)
        if comm_base:
            command_list.extend(comm_base)

        comm_ifs = self._set_command_l2slice_delete_ifs(
            device_mes, device_info, delete_info)
        if comm_ifs:
            command_list.extend(comm_ifs)

        comm_qos = self._set_command_l2slice_delete_qos(
            device_mes, device_info, delete_info)
        if comm_qos:
            command_list.extend(comm_qos)

        comm_irb = self._set_command_l2slice_delete_irb(
            device_mes, device_info, delete_info)
        if comm_irb:
            command_list.extend(comm_irb)

        comm_multi = self._set_command_l2slice_delete_multi(
            device_mes, device_info, delete_info)
        if comm_multi:
            command_list.extend(comm_multi)

        comm_policy = self._set_command_l2slice_delete_policyd(
            device_mes, device_info, delete_info)
        if comm_policy:
            command_list.extend(comm_policy)

        self.common_util_log.logging(
            None,
            self.log_level_debug,
            self._logging_send_command_str(command_list),
            __name__)

        return command_list

    @decorater_log
    def _gen_l2_slice_replace_message(self,
                                      device_info,
                                      ec_message,
                                      operation):
        '''
        Create message for CLI(L2Slice) - replace
            Called out when creating message for L2Slice(merge)
        Parameter:
            device_info : Device information
            ec_message : EC message
            operation : Designate "delete" when deleting
        Return value
            Creation command list : list [ command (str) , recv_message(str) ]
            Execute raise when error occurs
        '''
        try:
            device_mes = ec_message.get("device-leaf", {})

            device_name = device_mes.get("name")

            replace_info = self._gen_l2_slice_replace_message_for_cmd(
                device_mes, device_info)

        except Exception as ex:
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "ERROR : message = %s / Exception: %s" % (ec_message, ex),
                __name__)
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "Traceback:%s" % (traceback.format_exc(),),
                __name__)
            return None

        self.common_util_log.logging(
            device_name,
            self.log_level_debug,
            "replace_info:{0}".format(replace_info),
            __name__)
        self.common_util_log.logging(
            device_name,
            self.log_level_debug,
            "ec_message:{0} , db_info:{1}".format(ec_message, device_info),
            __name__)


        command_list = []

        comm_qos = self._set_command_l2slice_replace_qos(
            device_mes, device_info, replace_info)
        if comm_qos:
            command_list.extend(comm_qos)

        comm_policy = self._set_command_l2slice_replace_policyd(
            device_mes, device_info, replace_info)
        if comm_policy:
            command_list.extend(comm_policy)

        self.common_util_log.logging(
            None,
            self.log_level_debug,
            self._logging_send_command_str(command_list),
            __name__)

        return command_list

    @decorater_log
    def _gen_acl_filter_variable_message(self,
                                         device_info,
                                         ec_message,
                                         operation):
        '''
        Variable value to create message for CLI (acl-filter)
        Set routing-options for device
        Parameter:
            device_info : Device information
            ec_message : EC message
            operation : Designate "delete" when deleting
        Return value
            Creation command list : list [ command (str) , recv_message(str) ]
            Execute raise when error occurs
        '''
        try:
            device_mes = ec_message.get("device", {})
            device_name = device_mes.get("name")
            if operation == self._DELETE:
                acl_list = self._get_del_acl_from_ec(device_mes, device_info)
            else:
                acl_list = self._get_add_acl_from_ec(device_mes, device_info)
        except Exception as ex:
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "ERROR : message = %s / Exception: %s" % (ec_message, ex),
                __name__)
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "Traceback:%s" % (traceback.format_exc(),),
                __name__)
            return None

        self.common_util_log.logging(
            device_name,
            self.log_level_debug,
            "acl_list:{0}".format(acl_list),
            __name__)
        self.common_util_log.logging(
            device_name,
            self.log_level_debug,
            "ec_message:{0} , db_info:{1}".format(ec_message, device_info),
            __name__)

        command_list = self._set_acl_filter(acl_list, operation)

        self.common_util_log.logging(
            None,
            self.log_level_debug,
            self._logging_send_command_str(command_list),
            __name__)

        return command_list


    @decorater_log
    def _get_add_acl_from_ec(self, device_mes, db_info):
        '''
        Obtain information of EC message relating to ACL
        '''
        acl_list = []
        for filter_data in device_mes.get("filter", ()):
            acl_data = self._get_add_acl_from_ec_filter(filter_data, db_info)
            acl_list.extend(acl_data)
        return acl_list

    @decorater_log
    def _get_add_acl_from_ec_filter(self, filter_mes, db_info):
        '''
        Obtain information of EC message relating to ACL
        '''
        acl_list = []
        for term_data in filter_mes.get("term", ()):
            if (
                term_data.get("name") is None or
                term_data.get("priority") is None
            ):
                raise ValueError("acl not enough information")

            if term_data["priority"] > 900:
                raise ValueError("priority is less than 900")

            acl_data = {
                "IF-TYPE": (self._if_type_lag if "bond" in term_data["name"]
                            else self._if_type_phy),
                "IF-NAME": term_data["name"],
                "PRIORITY": term_data["priority"],
                "PROTOCOL": term_data.get("protocol"),
                "SOURCE-PORT": term_data.get("source-port"),
                "DESTINATION-PORT": term_data.get("destination-port"),
                "IS-ACL-MAC": False,
                "IS-ACL-IPV4": False,
                "IS-ACL-IPV6": False,
                "IS-ACL-IF-EXISTS-IPV4": False,
                "IS-ACL-IF-EXISTS-IPV6": False,
            }
            acl_data.update(
                self._get_acl_addr_data_from_ec(
                    term_data.get("source-mac-address"), "SOURCE-MAC")
            )
            acl_data.update(
                self._get_acl_addr_data_from_ec(
                    term_data.get("destination-mac-address"),
                    "DESTINATION-MAC")
            )
            acl_data.update(
                self._get_acl_addr_data_from_ec(
                    term_data.get("source-ip-address"), "SOURCE-IP")
            )
            acl_data.update(
                self._get_acl_addr_data_from_ec(
                    term_data.get("destination-ip-address"), "DESTINATION-IP")
            )

            if self._check_set_port_without_ip(acl_data):
                acl_data["IS-ACL-IPV4"] = True

            for db_acl_info in db_info.get("acl-info", ()):
                if db_acl_info.get("if_name") == term_data.get("name"):
                    for db_acl_detail_info in db_acl_info.get("term"):
                        db_source = db_acl_detail_info.get(
                            "source_ip_address")
                        db_dest = db_acl_detail_info.get(
                            "destination_ip_address")
                        db_source_mac = db_acl_detail_info.get(
                            "source_mac_address")
                        db_dest_mac = db_acl_detail_info.get(
                            "destination_mac_address")
                        db_source_port = db_acl_detail_info.get(
                            "source_port")
                        db_dest_port = db_acl_detail_info.get(
                            "destination_port")
                        db_protocol = db_acl_detail_info.get(
                            "protocol")
                        ip_version = 0
                        mac_exist = False
                        if db_source_mac or db_dest_mac:
                            mac_exist = True
                        if db_source:
                            ip_version = ipaddress.ip_address(
                                unicode(db_source.rpartition("/")[0])).version
                        if db_dest:
                            ip_version = ipaddress.ip_address(
                                unicode(db_dest.rpartition("/")[0])).version
                        if ip_version == 6:
                            acl_data["IS-ACL-IF-EXISTS-IPV6"] = True
                        if ip_version == 4 or (ip_version != 6 and
                                               (db_source_port or db_dest_port
                                                or (db_protocol
                                                    and not mac_exist))):
                            acl_data["IS-ACL-IF-EXISTS-IPV4"] = True

            acl_data["IS-IF-EXISTS"] = (
                term_data["name"] in db_info.get("cp_if_name_list", []))

            acl_list.append(acl_data)

        return acl_list

    @decorater_log
    def _get_acl_addr_data_from_ec(self, addr_data=None, tag_name=None):
        if not addr_data:
            return {}
        addr_obj = {}
        return_obj = {}
        if addr_data.get("ip_version"):
            addr_obj["IP_VERSION"] = addr_data["ip_version"]
            if addr_data["ip_version"] == 4:
                return_obj["IS-ACL-IPV4"] = True
            else:
                return_obj["IS-ACL-IPV6"] = True
        else:
            return_obj["IS-ACL-MAC"] = True
        addr_obj["ADDRESS"] = addr_data["address"]
        addr_obj["PREFIX"] = addr_data["prefix"]
        return_obj["{0}-ADDR".format(tag_name)] = addr_obj
        return return_obj

    @decorater_log
    def _check_set_port_without_ip(self, acl_data):
        '''
       Check if LF filter is necessary without IP
        '''
        is_set_port = (acl_data.get("SOURCE-PORT") is not None or
                       acl_data.get("DESTINATION-PORT") is not None)
        is_set_ip_addr = (acl_data["IS-ACL-IPV4"] or
                          acl_data["IS-ACL-IPV6"])
        return (is_set_port and not is_set_ip_addr)

    @decorater_log
    def _get_del_acl_from_ec(self, device_mes, db_info):
        '''
        Obtain information of EC message relating to ACL
        '''
        acl_list = []

        for filter_data in device_mes.get("filter", ()):
            for term_data in filter_data.get("term", ()):
                if_name = term_data.get("name")
                term_name = term_data.get("term-name")
                if (
                    if_name is None or term_name is None
                ):
                    raise ValueError("acl not enough information")

                db_term_data = self._get_acl_term_from_db(
                    if_name, term_name, db_info)

                acl_data = {
                    "IF-NAME": if_name,
                    "PRIORITY": db_term_data["PRIORITY"],
                    "IS-ACL-MAC": False,
                    "IS-ACL-IPV4": False,
                    "IS-ACL-IPV6": False,
                }
                acl_data.update(db_term_data)
                if self._check_set_port_without_ip(acl_data):
                    acl_data["IS-ACL-IPV4"] = True

                acl_list.append(acl_data)

        return acl_list

    def _get_acl_term_from_db(self, if_name, term_name, db_info):
        return_obj = {}
        for db_filter in db_info["acl-info"]:
            break_flug = False
            if db_filter.get("if-name") == if_name:
                for term in db_filter.get("term"):
                    if term.get("term-name") == term_name:
                        return_obj["PRIORITY"] = term.get("priority")
                        return_obj["SOURCE-PORT"] = term.get("source-port")
                        return_obj["DESTINATION-PORT"] = term.get(
                            "destination-port")
                        return_obj.update(
                            self._get_acl_addr_data_from_db(
                                term, "source-mac-address")
                        )
                        return_obj.update(
                            self._get_acl_addr_data_from_db(
                                term, "destination-mac-address")
                        )
                        return_obj.update(
                            self._get_acl_addr_data_from_db(
                                term, "source-ip-address")
                        )
                        return_obj.update(
                            self._get_acl_addr_data_from_db(
                                term, "destination-ip-address")
                        )
                        break_flug = True
                        break
            if break_flug:
                break

        return return_obj

    @decorater_log
    def _get_acl_addr_data_from_db(self, term_data=None, addr_name=None):
        if not term_data.get(addr_name):
            return {}
        return_obj = {}
        if "mac" in addr_name:
            return_obj["IS-ACL-MAC"] = True
        else:
            addr = unicode(term_data[addr_name].rpartition("/")[0])
            ip_addr = ipaddress.ip_address(addr)
            if ip_addr.version == 4:
                return_obj["IS-ACL-IPV4"] = True
            else:
                return_obj["IS-ACL-IPV6"] = True
        return return_obj


    @decorater_log
    def _set_acl_filter(self, acl_list=[], operation=None):
        comm_list = []
        for acl_data in acl_list:
            if_name = acl_data.get("IF-NAME")
            if_type = acl_data.get("IF-TYPE")
            ipv4_filter_name = None
            ipv6_filter_name = None
            if acl_data["IS-ACL-IPV4"]:
                ipv4_filter_name = self._gen_acl_filter_name(if_name,
                                                             ip_version=4)
                tmp_comm = self._set_acl_ip_filter(acl_data,
                                                   ipv4_filter_name,
                                                   4,
                                                   operation)
                comm_list.append((tmp_comm, self._recv_message))
            if acl_data["IS-ACL-IPV6"]:
                ipv6_filter_name = self._gen_acl_filter_name(if_name,
                                                             ip_version=6)
                tmp_comm = self._set_acl_ip_filter(acl_data,
                                                   ipv6_filter_name,
                                                   6,
                                                   operation)
                comm_list.append((tmp_comm, self._recv_message))
            if acl_data["IS-ACL-MAC"]:
                mac_filter_name = self._gen_acl_filter_name(if_name,
                                                            is_mac=True)
                tmp_comm = self._set_acl_mac_filter(acl_data,
                                                    mac_filter_name,
                                                    operation)
                comm_list.append((tmp_comm, self._recv_message))

            if_comm = "bond" if if_type == self._if_type_lag else "interface"
            if acl_data.get("IS-IF-EXISTS"):
                tmp = "net add {0} {1} acl ipv{3} {2} inbound"
                if not acl_data.get("IS-ACL-IF-EXISTS-IPV4") and \
                        operation != self._DELETE:
                    if ipv4_filter_name:
                        tmp_comm = tmp.format(
                            if_comm, if_name, ipv4_filter_name, 4)
                        comm_list.append((tmp_comm, self._recv_message))
                if not acl_data.get("IS-ACL-IF-EXISTS-IPV6") and \
                        operation != self._DELETE:
                    if ipv6_filter_name:
                        tmp_comm = tmp.format(
                            if_comm, if_name, ipv6_filter_name, 6)
                        comm_list.append((tmp_comm, self._recv_message))
        return comm_list

    @decorater_log
    def _gen_acl_filter_name(self, if_name, ip_version=None, is_mac=False):
        tmp_name = None
        if ip_version:
            tmp_name = "ce_ingress_{0}_l3_ipv{1}".format(if_name, ip_version)
        if is_mac:
            tmp_name = "ce_ingress_{0}_l2".format(if_name)
        return tmp_name

    @decorater_log
    def _set_acl_ip_filter(self,
                           acl_data,
                           filter_name,
                           ip_version=4,
                           operation=None):
        operation_comm = "del" if operation == self._DELETE else "add"
        tmp_comm = "net {0} acl ipv{1} {2} priority {3}".format(
            operation_comm, ip_version, filter_name, acl_data["PRIORITY"])
        if operation == self._DELETE:
            return tmp_comm
        is_no_prl = (acl_data.get("PROTOCOL") is None and
                     acl_data.get("SOURCE-PORT") is None and
                     acl_data.get("DESTINATION-PORT") is None)
        if is_no_prl:
            tmp_comm += self._set_filter_drop_no_protocol_no_port(acl_data,
                                                                  ip_version)
        else:
            tmp_comm += self._set_filter_drop_protocol_ip_port(acl_data,
                                                               ip_version)
        return tmp_comm

    @decorater_log
    def _set_filter_drop_protocol_ip_port(self, acl_data, ip_version=4):
        '''
        Create drop or later of net add acl ～
        drop <tcp|udp> source-ip　～
        '''
        tmp_comm = " drop"
        tmp_comm += " {0}".format(acl_data["PROTOCOL"]
                                  if acl_data["PROTOCOL"] else "")
        tmp_comm += self._get_command_text_acl_addr_port(acl_data,
                                                         "SOURCE-IP-ADDR",
                                                         "source-ip",
                                                         ip_version)

        tmp_comm += self._get_command_text_acl_port(acl_data,
                                                    "SOURCE-PORT",
                                                    "source-port")
        tmp_comm += self._get_command_text_acl_addr_port(acl_data,
                                                         "DESTINATION-IP-ADDR",
                                                         "dest-ip",
                                                         ip_version)
        tmp_comm += self._get_command_text_acl_port(acl_data,
                                                    "DESTINATION-PORT",
                                                    "dest-port")
        return tmp_comm

    @decorater_log
    def _set_filter_drop_no_protocol_no_port(self, acl_data, ip_version=4):
        '''
        Create drop or later of net add acl ～
        drop source-ip　～
        '''
        tmp_comm = " drop"
        tmp_comm += self._get_command_text_acl_addr_port(acl_data,
                                                         "SOURCE-IP-ADDR",
                                                         "source-ip",
                                                         ip_version)
        tmp_comm += self._get_command_text_acl_addr_port(acl_data,
                                                         "DESTINATION-IP-ADDR",
                                                         "dest-ip",
                                                         ip_version)
        return tmp_comm

    @decorater_log
    def _get_command_text_acl_addr_port(self,
                                        acl_data,
                                        target=None,
                                        set_command=None,
                                        ip_version=None):
        if (not ip_version and acl_data.get(target)):
            parameter = (
                acl_data[target]["ADDRESS"] if acl_data[target].get("ADDRESS")
                else acl_data[target]
            )
        elif (acl_data.get(target) and
                acl_data[target]["IP_VERSION"] == ip_version):
            tmp = "{0}/{1}".format(acl_data[target]["ADDRESS"],
                                   acl_data[target]["PREFIX"])
            parameter = str(ipaddress.ip_interface(unicode(tmp)).network)
        else:
            parameter = "any"
        return " {0} {1}".format(set_command, parameter)

    @decorater_log
    def _get_command_text_acl_port(self,
                                   acl_data,
                                   target=None,
                                   set_command=None,
                                   ip_version=None):

        if acl_data.get(target):
            parameter = acl_data[target]
        else:
            parameter = "any"
        return " {0} {1}".format(set_command, parameter)

    @decorater_log
    def _set_acl_mac_filter(self, acl_data, filter_name, operation=None):
        operation_comm = "del" if operation == self._DELETE else "add"
        tmp_comm = "net {0} acl mac {1} priority {2}".format(
            operation_comm, filter_name, acl_data["PRIORITY"])
        if operation == self._DELETE:
            return tmp_comm
        tmp_comm += " drop"
        tmp_comm += self._get_command_text_acl_addr_port(acl_data,
                                                         "SOURCE-MAC-ADDR",
                                                         "source-mac")
        tmp_comm += self._get_command_text_acl_addr_port(
            acl_data,
            "DESTINATION-MAC-ADDR",
            "dest-mac")
        tmp_comm += " protocol any"
        return tmp_comm


    @decorater_log
    def _gen_node_add_variable_message(self,
                                       node_type,
                                       device_info,
                                       ec_message,
                                       operation):
        '''
        Variable value to create message for CLI (Leaf, Spine)
            Called out when creating message for Leaf, Spine
        Parameter:
            node_type : Device type
            device_info : Device information (DB)
            ec_message : EC message
            operation : Designate "delete" when deleting
        Return value
            Creation command list : list [ command (str) , recv_message(str) ]
            Execute raise when error occurs
        '''

        try:
            device_mes = ec_message.get("device", {})

            device_name = device_mes.get("name")

            ospf_area = device_mes.get("ospf", {}).get("area-id")

            if_info = {}
            if device_mes.get("internal-physical"):
                if_info["physical"] = self._get_internal_if_list(
                    device_mes["internal-physical"], device_info, operation)
            if device_mes.get("internal-lag"):
                if_info["lag"] = self._get_internal_if_list(
                    device_mes["internal-lag"], device_info, operation)

            nw_addr_info = self._get_setting_network_addr(if_info,
                                                          device_info,
                                                          operation)

        except Exception as ex:
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "ERROR : message = %s / Exception: %s" % (ec_message, ex),
                __name__)
            self.common_util_log.logging(
                device_name,
                self.log_level_debug,
                "Traceback:%s" % (traceback.format_exc(),),
                __name__)
            return None

        self.common_util_log.logging(
            device_name,
            self.log_level_debug,
            "if_info:{0} , nw_info:{1}".format(if_info, nw_addr_info),
            __name__)
        self.common_util_log.logging(
            device_name,
            self.log_level_debug,
            "ec_message:{0} , db_info:{1}".format(ec_message, device_info),
            __name__)

        comm_base = self._set_command_node_base(device_mes, operation)
        if node_type == self._node_type_leaf:
            comm_bgp = self._set_command_bgp(device_mes, operation)
        comm_ospf = self._set_command_ospf(
            device_mes, ospf_area, operation=operation)
        comm_internal_link = self._set_command_internal_if(
            if_info, ospf_area, operation=operation, nw_addr_info=nw_addr_info)

        command_list = []
        command_list.extend(comm_base)
        if node_type == self._node_type_leaf:
            command_list.extend(comm_bgp)
        command_list.extend(comm_ospf)
        command_list.extend(comm_internal_link)

        self.common_util_log.logging(
            None,
            self.log_level_debug,
            self._logging_send_command_str(command_list),
            __name__)

        return command_list

    @decorater_log
    def _get_internal_if_list(self, ec_info, db_info, operation=None):
        '''
        Obtain internal link IF information
            Organise EC message and DB information to make command creation easier
        Parameter:
            ec_info : EC message(Internal link IF information)
            db_info : DB information
            operation : Operation type (Mandatory in case other than MERGE)
        Return value
            IF infomration list (list)
            Execute raise when error occurs
        '''

        if_info = []
        if operation == self._DELETE:
            for internal_if_info in ec_info:
                tmp_if = {}
                tmp_if["name"] = internal_if_info.get("name")
                for db_info_if in db_info.get("internal-link"):
                    if tmp_if["name"] == db_info_if.get("if_name"):
                        tmp_if["vlan_id"] = db_info_if.get("vlan_id")
                        tmp_if["address"] = "{0}/{1}".format(
                            db_info_if.get("ip_address"),
                            db_info_if.get("ip_prefix")
                        )
                        tmp_if["cost"] = db_info_if.get("cost")
                        break
                if internal_if_info.get("internal-interface", {}):
                    tmp_if["internal-interface"] = internal_if_info.get(
                        "internal-interface")
                if_info.append(tmp_if)
        elif operation == self._REPLACE:
            for internal_if_info in ec_info:
                tmp_if = {}
                tmp_if["name"] = internal_if_info.get("name")
                for db_info_if in db_info.get("internal-link"):
                    if tmp_if["name"] == db_info_if.get("if_name"):
                        if internal_if_info.get("cost"):
                            tmp_if["vlan_id"] = db_info_if.get("vlan_id")
                            tmp_if["cost"] = internal_if_info.get("cost")
                        if internal_if_info.get("minimum-links"):
                            tmp_if["minimum-links"] = internal_if_info.get(
                                "minimum-links")
                        break
                if internal_if_info.get("internal-interface", {}):
                    tmp_if["internal-interface"] = internal_if_info.get(
                        "internal-interface")
                if_info.append(tmp_if)
        else:
            for internal_if_info in ec_info:
                if (not internal_if_info.get("opposite-node-name")):
                    raise ValueError("fault opposite-node vpn:device = %s" %
                                     (internal_if_info.get(
                                         "opposite-node-name")))
                else:
                    tmp_if = {}
                    if internal_if_info.get("opposite-node-name") != "Recover":
                        opposite_os = \
                            self.common_util_db.read_device_os(
                                internal_if_info.get("opposite-node-name"))
                        vlan_flag = False
                        if opposite_os in self.internal_link_vlan_config:
                            vlan_flag = True
                        tmp_if["name"] = internal_if_info.get("name")
                        if vlan_flag:
                            tmp_if["vlan_id"] = internal_if_info.get("vlan-id")
                        else:
                            tmp_if["vlan_id"] = None
                    else:
                        tmp_if["name"] = internal_if_info.get("name")
                        tmp_if["vlan_id"] = internal_if_info.get("vlan-id")

                    tmp_if["address"] = internal_if_info.get(
                        "address") + '/' + str(internal_if_info.get("prefix"))

                    if internal_if_info.get("cost"):
                        tmp_if["cost"] = internal_if_info.get("cost")
                    else:
                        tmp_if["cost"] = self._DEFAULT_INTERNAL_LINK_COST

                    if internal_if_info.get("internal-interface", {}):
                        tmp_if["internal-interface"] = internal_if_info.get(
                            "internal-interface")
                        tmp_if["minimum-links"] = internal_if_info.get(
                            "minimum-links")

                    if_info.append(tmp_if)

        return if_info

    @decorater_log
    def _get_if_condition_list(self, ec_info, db_info, operation=None):
        '''
        Obtain information on IF  open/close.
        Arrange  EC message and DB information ino order that command can be created easily.
        Parameter:
            ec_info : EC message
            db_info : DB information
            operation : operation type
        Return value
            IF information list (list)
            Execute raise when error occurs
        '''
        if_info = {}
        phy_ifs = ec_info.get("interface-physical")
        lag_ifs = ec_info.get("internal-lag")

        if phy_ifs:
            if_info_phy = []
            for phy_if in phy_ifs:
                tmp_if = {}
                tmp_if["name"] = phy_if.get("name")
                for db_info_if in db_info.get("physical-interface"):
                    if tmp_if["name"] == db_info_if.get("if_name"):
                        tmp_if["condition"] = phy_if.get(
                            "condition")
                if_info_phy.append(tmp_if)
            if_info["physical"] = if_info_phy
        if lag_ifs:
            if_info_lag = []
            for lag_if in lag_ifs:
                tmp_if = {}
                tmp_if["name"] = lag_if.get("name")
                for db_info_if in db_info.get("lag"):
                    if tmp_if["name"] == db_info_if.get("if_name"):
                        tmp_if["condition"] = lag_if.get(
                            "condition")
                if_info_lag.append(tmp_if)
            if_info["lag"] = if_info_lag
        self.common_util_log.logging(
            None,
            self.log_level_debug,
            "if_info : \n%s" % (if_info,),
            __name__)

        return if_info

    @decorater_log
    def _get_setting_network_addr(self, if_info, db_info, operation=None):
        ret_val = []
        if operation == self._REPLACE:
            return ret_val
        db_nw_addrs = self._get_network_dict_from_ecdb(db_info, is_db=True)
        ec_nw_addrs = self._get_network_dict_from_ecdb(if_info)
        if operation == self._DELETE:
            for nw_addr, if_count in ec_nw_addrs.items():
                if db_nw_addrs.get(nw_addr) == if_count:
                    ret_val.append(nw_addr)
        else:
            ret_val.extend(list(ec_nw_addrs.keys()))
        return ret_val

    @decorater_log
    def _get_network_dict_from_ecdb(self, data_info, is_db=False):
        ret_val = {}
        if is_db:
            tmp_if_list = data_info.get("internal-link", ())
        else:

            tmp_if_list = copy.deepcopy(data_info.get("physical", []))

            tmp_if_list.extend(copy.deepcopy(data_info.get("lag", [])))

        for if_item in tmp_if_list:
            tmp_addr = (
                "{0}/{1}".format(if_item["ip_address"], if_item["ip_prefix"])
                if is_db else if_item.get("address")
            )
            if_mod = ipaddress.ip_interface(unicode(tmp_addr))
            nw_addr = str(if_mod.network)
            ret_val[nw_addr] = (
                ret_val[nw_addr] + 1 if nw_addr in ret_val else 1)
        return ret_val

    @decorater_log
    def _set_command_internal_if(self,
                                 if_info,
                                 ospf_area,
                                 operation=None,
                                 nw_addr_info=[]):
        '''
        Create command list for internal link IF configuraiton
        Parameter:
            if_info : Internal link IF information
            ospf_area : OSPF area ID(Unnecessary in case of REPLACE; Necessary in case of addition/deletion)
            operation : Operation type (Mandatory in case other than MERGE)
            nw_addr_info : Netwrk address list information
        Return value
            command list (list)
        '''
        tmp_comm_list = []

        for internal_if in if_info.get("physical", ()):
            tmp_comm_list.extend(
                self._set_command_unit_inner_if(self._if_type_phy,
                                                internal_if,
                                                operation)
            )
        for internal_if in if_info.get("lag", ()):
            tmp_comm_list.extend(
                self._set_command_unit_inner_if(self._if_type_lag,
                                                internal_if,
                                                operation)
            )
        if operation != self._REPLACE:
            tmp_comm_list.extend(
                self._set_command_ospf_nw_addr(nw_addr_info,
                                               ospf_area,
                                               operation)
            )
        self.common_util_log.logging(
            None,
            self.log_level_debug,
            "internal link command : \n%s" % (tmp_comm_list,),
            __name__)
        return tmp_comm_list

    @decorater_log
    def _set_command_unit_inner_if(self,
                                   if_type,
                                   internal_if,
                                   operation=None):
        tmp_comm_list = []
        vlan_id = internal_if.get("vlan_id")
        if (vlan_id is None and if_type == self._if_type_lag):
            if_name = internal_if["name"]
        elif (vlan_id is not None and if_type == self._if_type_phy):
            if_name = "{0}.{1}".format(internal_if["name"], vlan_id)
        else:
            if if_type == self._if_type_phy:
                tmp = "Physical IF with no vlan is not allowed."
            else:
                tmp = "Lag IF with vlan is not allowed."
            raise ValueError(tmp)
        comm_net_if = "bond" if if_type == self._if_type_lag else "interface"
        comm_net_ope = "del" if operation == self._DELETE else "add"
        comm_net_top = "net {0} {1} {2}".format(comm_net_ope,
                                                comm_net_if,
                                                if_name)
        cost_cmd = "{0} ospf cost {1}".format(comm_net_top,
                                              internal_if.get("cost"))
        p2p_cmd = "{0} ospf network point-to-point".format(comm_net_top)
        if operation == self._DELETE:
            tmp_comm_list.append((cost_cmd, self._recv_message))
            tmp_comm_list.append((p2p_cmd, self._recv_message))
            if if_type == self._if_type_lag:
                tmp_comm_list.append((comm_net_top, self._recv_message))
                for physical_if in internal_if["internal-interface"]:
                    comm = "net del interface {0}".format(
                        physical_if.get("name"))
                    tmp_comm_list.append((comm, self._recv_message))
            else:
                comm = "net del interface {0}".format(internal_if["name"])
                tmp_comm_list.append((comm, self._recv_message))
        elif operation == self._REPLACE:
            if internal_if.get("minimum-links"):
                for physical_if in internal_if["internal-interface"]:
                    if physical_if["operation"] == "delete":
                        comm = "net del bond {0} bond slaves {1}".format(
                            internal_if.get("name"), physical_if.get("name"))
                        tmp_comm_list.append((comm, self._recv_message))
                        comm = "net del interface {0}".format(
                            physical_if.get("name"))
                        tmp_comm_list.append((comm, self._recv_message))
                    else:
                        comm =\
                            "{0} bond slaves {1}".format(comm_net_top,
                                                         physical_if["name"])
                        tmp_comm_list.append((comm, self._recv_message))
            if internal_if.get("cost"):
                tmp_comm_list.append((cost_cmd, self._recv_message))
        else:
            if if_type == self._if_type_lag:
                for physical_if in internal_if["internal-interface"]:
                    comm = "{0} bond slaves {1}".format(comm_net_top,
                                                        physical_if["name"])
                    tmp_comm_list.append((comm, self._recv_message))
                tmp_mtu_if = if_name
            else:
                tmp_comm_list.append((comm_net_top, self._recv_message))
                tmp_mtu_if = "{0},{1}".format(internal_if["name"], if_name)
            comm = "net {0} {1} {2} mtu {3}".format(comm_net_ope,
                                                    comm_net_if,
                                                    tmp_mtu_if,
                                                    4096)
            tmp_comm_list.append((comm, self._recv_message))
            comm = "{0} ip address {1}".format(comm_net_top,
                                               internal_if["address"])
            tmp_comm_list.append((comm, self._recv_message))
            if if_type == self._if_type_lag:
                comm = "{0} bond min-links {1}"
                comm = comm.format(comm_net_top, internal_if["minimum-links"])
                tmp_comm_list.append((comm, self._recv_message))
            comm = "{0} acl ipv4 {1} outbound".format(comm_net_top,
                                                      "msf_egress_l3_ipv4")
            tmp_comm_list.append((comm, self._recv_message))
            tmp_comm_list.append((cost_cmd, self._recv_message))
            tmp_comm_list.append((p2p_cmd, self._recv_message))
        return tmp_comm_list

    @decorater_log
    def _set_command_ospf_nw_addr(self, nw_addr_info, ospf_area, operation):
        ope_comm = "del" if operation == self._DELETE else "add"
        tmp_cmd = "net {0} ospf network {1} area 0.0.0.{2}"
        tmp_comm_list = []
        for nw_addr in nw_addr_info:
            area_cmd = tmp_cmd.format(ope_comm,
                                      nw_addr,
                                      ospf_area)
            tmp_comm_list.append((area_cmd, self._recv_message))
        return tmp_comm_list

    @decorater_log
    def _set_command_if_condition(self,
                                  if_info,
                                  operation=None):
        '''
        Create command list for IF open/close  configuraiton
        Parameter:
            if_info : Internal link IF information
            operation : Operation type (Mandatory in case other than MERGE)
        Return value
            command list (list)
        '''
        tmp_comm_list = []

        for if_condition in if_info.get("physical", ()):
            tmp_comm_list.extend(
                self._set_command_unit_if_condition(self._if_type_phy,
                                                    if_condition,
                                                    operation)
            )
        for if_condition in if_info.get("lag", ()):
            tmp_comm_list.extend(
                self._set_command_unit_if_condition(self._if_type_lag,
                                                    if_condition,
                                                    operation)
            )

        self.common_util_log.logging(
            None,
            self.log_level_debug,
            "internal link command : \n%s" % (tmp_comm_list,),
            __name__)

        return tmp_comm_list

    @decorater_log
    def _set_command_unit_if_condition(self,
                                       if_type,
                                       if_condition,
                                       operation=None):
        tmp_comm_list = []

        if_name = if_condition.get("name")
        condition = if_condition.get("condition")

        comm_net_if = "bond" if if_type == self._if_type_lag else "interface"
        comm_net_ope = "add" if condition == "disable" else "del"
        comm = "net {0} {1} {2} link down".format(comm_net_ope,
                                                  comm_net_if,
                                                  if_name)

        tmp_comm_list.append((comm, self._recv_message))

        return tmp_comm_list

    @decorater_log
    def _set_command_node_base(self, device_mes, operation=None):
        '''
        Create command list for device expansion setting (base)
        Parameter:
            device_mes : Device information (EC message)
            operation : Operation type (Mandatory in case other than MERGE)
        Return value
            command list (list)
        '''
        tmp_comm_list = []

        if operation == self._DELETE:
            pass
        elif operation == self._REPLACE:
            pass
        else:
            lo_ip_address = device_mes.get(
                "loopback-interface", {}).get("address")
            lo_ip_address_cidr = lo_ip_address + "/" + \
                str(device_mes.get("loopback-interface", {}).get("prefix"))

            comm = "net add hostname " + device_mes.get("name")
            tmp_comm_list.append((comm, self._recv_message))
            comm = "net add loopback lo ip address " + lo_ip_address_cidr
            tmp_comm_list.append((comm, self._recv_message))

        self.common_util_log.logging(
            None,
            self.log_level_debug,
            "internal link command : \n%s" % (tmp_comm_list,),
            __name__)
        return tmp_comm_list

    @decorater_log
    def _set_command_bgp(self, device_mes, operation=None):
        '''
        Create command list for device expansion setting (BGP)
        Parameter:
            device_mes : Device information (EC message)
        Set system-id,admin-key of LAG
        Return value
            command list (list)
        '''
        tmp_comm_list = []

        if operation == self._DELETE:
            pass
        elif operation == self._REPLACE:
            pass
        else:
            lo_ip_address = device_mes.get(
                "loopback-interface", {}).get("address")
            as_number = device_mes.get(
                "l2-vpn", {}).get("as", {}).get("as-number")
            bgp_neighbors_list = device_mes.get(
                "l2-vpn", {}).get("bgp", {}).get("neighbor", {})

            comm = "net add bgp autonomous-system " + str(as_number)
            tmp_comm_list.append((comm, self._recv_message))
            comm = "net add bgp router-id " + lo_ip_address
            tmp_comm_list.append((comm, self._recv_message))
            comm = "net add bgp timers 30 90"
            tmp_comm_list.append((comm, self._recv_message))

            for neighbor in bgp_neighbors_list:
                comm = "net add bgp neighbor " + \
                    neighbor.get("address") + " remote-as " + str(as_number)
                tmp_comm_list.append((comm, self._recv_message))
                comm = "net add bgp neighbor " + \
                    neighbor.get("address") + " update-source " + lo_ip_address
                tmp_comm_list.append((comm, self._recv_message))
                comm = "net add bgp l2vpn evpn  neighbor " + \
                    neighbor.get("address") + " activate"
                tmp_comm_list.append((comm, self._recv_message))

            comm = "net add bgp l2vpn evpn  advertise-all-vni"
            tmp_comm_list.append((comm, self._recv_message))

        self.common_util_log.logging(
            None,
            self.log_level_debug,
            "internal link command : \n%s" % (tmp_comm_list,),
            __name__)
        return tmp_comm_list

    @decorater_log
    def _set_command_q_in_q(self, device_mes, operation=None):
        '''
        Create command list of configuration for device addition(Q-in-Q).
        Argument:
            device_mes : devce message information (EC message)
            operation : opeation type( it is mandatry except for in  case of MERGE)
        Return value:
            command list (list)
        '''
        q_in_q_comm_list = []
        q_in_q = device_mes.get("device", {}).get(
            "equipment", {}).get("q-in-q")
        if q_in_q == self._Q_IN_Q_DEVICE_UNIT:
            comm = "net add bridge bridge vlan-protocol 802.1ad"
            q_in_q_comm_list.append((comm, self._recv_message))
        self.common_util_log.logging(
            None,
            self.log_level_debug,
            "Q-in-Q command : \n%s" % (q_in_q_comm_list,),
            __name__)
        return q_in_q_comm_list

    @decorater_log
    def _set_command_ospf(self, device_mes, ospf_area, operation=None):
        '''
        Create command list for device expansion setting (OSPF)
        Parameter:
            device_mes : Device information (EC message)
            ospf_area : OSPF area ID(Mandatory at the time of addition)
            operation : Operation type (Mandatory in case other than MERGE)
        Return value
            command list (list)
        '''
        tmp_comm_list = []

        if operation == self._DELETE:
            pass
        elif operation == self._REPLACE:
            pass
        else:
            lo_ip_address = device_mes.get(
                "loopback-interface", {}).get("address")
            lo_ip_address_cidr = lo_ip_address + "/" + \
                str(device_mes.get("loopback-interface", {}).get("prefix"))

            comm = "net add ospf router-id " + lo_ip_address
            tmp_comm_list.append((comm, self._recv_message))
            comm = "net add ospf timers throttle spf 200 200 200"
            tmp_comm_list.append((comm, self._recv_message))
            comm = "net add ospf passive-interface lo"
            tmp_comm_list.append((comm, self._recv_message))
            comm = "net add ospf network " + \
                lo_ip_address_cidr + " area 0.0.0." + str(ospf_area)
            tmp_comm_list.append((comm, self._recv_message))

        self.common_util_log.logging(
            None,
            self.log_level_debug,
            "internal link command : \n%s" % (tmp_comm_list,),
            __name__)
        return tmp_comm_list


    @decorater_log
    def _get_lag_if_list(self, ec_info, db_info, operation=None):
        '''
        LAGIF information acquisition
           Organise EC message and DB information, and make command creation easier.
        Parameter:
            ec_info : EC message(LAG IF information)
            db_info : DB information
            operation : Operation type
        Return value
            LAG IF infomration list (list)
            Execute raise when error occurs
        Create vni to protocols/evpn
        '''
        lag_list = []

        for lag_if_info in ec_info:
            tmp_lag = {}
            tmp_lag["name"] = lag_if_info.get("name")
            tmp_lag["lag_member"] = lag_if_info.get("leaf-interface", {})
            lag_list.append(tmp_lag)

        return lag_list

    @decorater_log
    def _set_command_lag(self, lag_list, operation=None):
        '''
        Create command list for LAG IF configuraiton
        Parameter:
            lag_list : LAG IF infomration list
            operation : Operation type
        Return value
            command list (list)
        '''
        tmp_comm_list = []

        if operation == self._DELETE:
            for lag_info in lag_list:
                comm = "net del bond " + lag_info.get("name")
                tmp_comm_list.append((comm, self._recv_message))
                for member_info in lag_info.get("lag_member"):
                    comm = "net del interface " + member_info.get("name")
                    tmp_comm_list.append((comm, self._recv_message))
        elif operation == self._REPLACE:
            for lag_info in lag_list:
                for member_info in lag_info.get("lag_member"):
                    if member_info.get("operation") == "delete":
                        comm = "net del bond " + \
                            lag_info.get("name") + " bond slaves " + \
                            member_info.get("name")
                        tmp_comm_list.append((comm, self._recv_message))
                        comm = "net del interface " + member_info.get("name")
                        tmp_comm_list.append((comm, self._recv_message))
                    else:
                        comm = "net add bond " + \
                            lag_info.get("name") + " bond slaves " + \
                            member_info.get("name")
                        tmp_comm_list.append((comm, self._recv_message))
        else:
            for lag_info in lag_list:
                for member_info in lag_info.get("lag_member"):
                    comm = "net add bond " + \
                        lag_info.get("name") + " bond slaves " + \
                        member_info.get("name")
                    tmp_comm_list.append((comm, self._recv_message))

        self.common_util_log.logging(
            None,
            self.log_level_debug,
            "internal link command : \n%s" % (tmp_comm_list,),
            __name__)
        return tmp_comm_list


    @decorater_log
    def _gen_l2_slice_merge_message_for_cmd(self, ec_info, db_info):
        '''
        Information creation for L2 Slice EVPN control command creation
            Organise EC message and DB information to make command creation easier
        Parameter:
            ec_info : EC message(Internal link IF information)
            db_info : DB information
        Return value
            Information list for L2 slice creation (dict)
                multi-homing        Object of Multihoming setting information (str)
                irb-slice           Whether slide is corresponding to IRB or not (boolean)
                first-cp-on-if      Whether it is the first CP for IF or not (dict)
                first-cp-on-vlan    Whether it is the first CP for VLAN or not (dict)
                first-cp-on-slice   Whether it is the first CP for slide or not (boolean)
                first-clag-on-if    Whether it is the first clag for IF or not (dict)
                if-type            IF type of each IF (dict)
            Execute raise when error occurs
        '''

        tmp_flug = \
            {
                "multi-homing": None,
                "irb-slice": False,
                "first-cp-on-if": {},
                "first-cp-on-vlan": {},
                "first-cp-on-vni": {},
                "first-cp-on-vni-vlan": {},
                "first-cp-on-slice": False,
                "first-clag-on-if": {},
                "if-type": {},
                "if-speed": {},
            }

        if ec_info.get("multi-homing"):
            tmp_flug["multi-homing"] = "ec"
        elif db_info.get("multi_homing"):
            tmp_flug["multi-homing"] = "db"

        clag_on_ifs_in_ec_mes = {}
        cps_on_ifs_in_ec_mes = {}
        cps_on_vlans_in_ec_mes = {}
        cps_on_vni_in_ec_mes = {}
        cps_on_slice_in_ec_mes = 0
        cps_on_vnivlan_in_ec_mes = {}
        for cp in ec_info.get("cp", {}):
            if_name = cp.get("name")
            vlan_id = cp.get("vlan-id")
            clag_id = cp.get("clag-id")
            vni = str(cp.get("vni"))

            cps_on_slice_in_ec_mes += 1

            cps_on_ifs_in_ec_mes[if_name] = \
                self._flag_count_up(cps_on_ifs_in_ec_mes.get(if_name))

            cps_on_vlans_in_ec_mes[vlan_id] = \
                self._flag_count_up(cps_on_vlans_in_ec_mes.get(vlan_id))

            cps_on_vni_in_ec_mes[vni] = \
                self._flag_count_up(cps_on_vni_in_ec_mes.get(vni))

            if not cps_on_vnivlan_in_ec_mes.get(vni):
                cps_on_vnivlan_in_ec_mes[vni] = {}
            if not cps_on_vnivlan_in_ec_mes[vni].get(vlan_id):
                cps_on_vnivlan_in_ec_mes[vni][vlan_id] = 1
            else:
                cps_on_vnivlan_in_ec_mes[vni][vlan_id] += 1

            if clag_id:
                clag_on_ifs_in_ec_mes[if_name] = \
                    self._flag_count_up(clag_on_ifs_in_ec_mes.get(if_name))

            if cp.get("irb"):
                tmp_flug["irb-slice"] = True

            if not tmp_flug["if-type"].get(if_name):
                tmp_flug["if-type"][if_name] = "physical"
                for lag_if in db_info.get("lag", {}):
                    if if_name == lag_if.get("if_name"):
                        tmp_flug["if-type"][if_name] = "lag"
                        break

            if not tmp_flug["if-speed"].get(if_name):
                if tmp_flug["if-type"][if_name] == "physical":
                    if cp.get("speed"):
                        tmp_flug["if-speed"][if_name] = int(cp.get(
                            "speed").strip("g"))
                else:
                    for lag_if in db_info.get("lag", {}):
                        if if_name == lag_if.get("if_name"):
                            tmp_flug["if-speed"][if_name] = \
                                int(lag_if.get("link_speed").strip("g")) * \
                                int(lag_if.get("links"))
                            break

        clag_on_ifs_in_db_info = {}
        cps_on_ifs_in_db_info = {}
        cps_on_vlans_in_db_info = {}
        cps_on_vni_in_db_info = {}
        cps_on_slice_in_db_info = 0
        cps_on_vnivlan_in_db_info = {}
        for cp in db_info.get("cp", ()):
            if_name = cp.get("if_name")
            vlan_id = cp.get("vlan").get("vlan_id")
            clag_id = cp.get("clag-id")
            vni = str(cp.get("vni"))

            if cp.get("slice_name") == ec_info.get("slice_name"):
                cps_on_slice_in_db_info += 1

            cps_on_ifs_in_db_info[if_name] = \
                self._flag_count_up(cps_on_ifs_in_db_info.get(if_name))

            cps_on_vlans_in_db_info[vlan_id] = \
                self._flag_count_up(cps_on_vlans_in_db_info.get(vlan_id))

            cps_on_vni_in_db_info[vni] = \
                self._flag_count_up(cps_on_vni_in_db_info.get(vni))

            if not cps_on_vnivlan_in_db_info.get(vni):
                cps_on_vnivlan_in_db_info[vni] = {}
            if not cps_on_vnivlan_in_db_info[vni].get(vlan_id):
                cps_on_vnivlan_in_db_info[vni][vlan_id] = 1
            else:
                cps_on_vnivlan_in_db_info[vni][vlan_id] += 1

            if clag_id:
                clag_on_ifs_in_db_info[if_name] = \
                    self._flag_count_up(clag_on_ifs_in_db_info.get(if_name))

        if cps_on_slice_in_db_info == 0:
            tmp_flug["first-cp-on-slice"] = True

        tmp_flug["first-vrf-on-slice"] = False
        if ec_info.get("vrf"):
            vrf_name = ec_info["vrf"].get("vrf-name")
            db_vrf = db_info.get("vrf_detail", ())
            if not [tmp for tmp in db_vrf if tmp.get("vrf_name") == vrf_name]:
                tmp_flug["first-vrf-on-slice"] = True

        tmp_flug["first-multi-homing"] = not bool(db_info.get("multi_homing"))
        if ec_info.get("multi-homing", {}).get("recover"):
            tmp_flug["first-multi-homing"] = True

        if ec_info.get("vrf"):
            l3_vni = ec_info["vrf"].get("l3-vni", {})
            if l3_vni.get("vni-id") is None or l3_vni.get("vlan-id") is None:
                tmp = "l3-vni is insufficient: vni-id={0}, vlan-id={1}"
                raise ValueError(
                    tmp.format(l3_vni.get("vni-id"), l3_vni.get("vlan-id")))

        for ifs_name in cps_on_ifs_in_ec_mes.keys():
            if cps_on_ifs_in_db_info.get(ifs_name):
                tmp_flug["first-cp-on-if"][ifs_name] = False
            else:
                tmp_flug["first-cp-on-if"][ifs_name] = True

        for vlan in cps_on_vlans_in_ec_mes.keys():
            if cps_on_vlans_in_db_info.get(vlan):
                tmp_flug["first-cp-on-vlan"][vlan] = False
            else:
                tmp_flug["first-cp-on-vlan"][vlan] = True

        for vni in cps_on_vni_in_ec_mes.keys():
            if cps_on_vni_in_db_info.get(vni):
                tmp_flug["first-cp-on-vni"][vni] = False
            else:
                tmp_flug["first-cp-on-vni"][vni] = True

        for vni in cps_on_vnivlan_in_ec_mes.keys():
            tmp_flug["first-cp-on-vni-vlan"][vni] = {}

            if cps_on_vnivlan_in_db_info.get(vni):
                for vlan in cps_on_vnivlan_in_ec_mes.get(vni, {}).keys():
                    if cps_on_vnivlan_in_db_info.get(vni).get(vlan):
                        tmp_flug["first-cp-on-vni-vlan"][vni][vlan] = False
                    else:
                        tmp_flug["first-cp-on-vni-vlan"][vni][vlan] = True
            else:
                for vlan in cps_on_vnivlan_in_ec_mes.get(vni, {}).keys():
                    tmp_flug["first-cp-on-vni-vlan"][vni][vlan] = True

        if clag_on_ifs_in_ec_mes:
            for ifs_name in clag_on_ifs_in_ec_mes.keys():
                if clag_on_ifs_in_db_info.get(ifs_name):
                    tmp_flug["first-clag-on-if"][ifs_name] = False
                else:
                    tmp_flug["first-clag-on-if"][ifs_name] = True

        return tmp_flug

    @decorater_log
    def _set_command_l2slice_merge_qos(self, ec_info, db_info, merge_info):
        '''
        L2 slice EVPN control command creation -  merge, qos
            Create command list for L2 slice EVPN control (merge, qos)
        Parameter:
            ec_info : EC message(Internal link IF information)
            db_info : DB information
            merge_info : Information for command creation
        Return value
            command list (list)
            Execute raise when error occurs
        '''

        tmp_comm_list = []
        ifs_flag = {}

        for cp in ec_info.get("cp", {}):
            if_name = cp.get("name")

            if cp.get("port-mode") is None:
                continue

            if merge_info["first-cp-on-if"].get(if_name) and \
                    (ifs_flag.get(if_name) is None):
                port_mode = cp.get("port-mode")
                qos_val = self._get_cp_qos_info_from_ec(cp, db_info)
                remark_m = str(qos_val["REMARK-MENU"]["IPV4"]) \
                    if qos_val.get("REMARK-MENU", {}).get("IPV4") \
                    is not None else None

                if remark_m:
                    comm = "net add acl mac ce_ingress_" + if_name + \
                        "_l2 priority 1000 set-class " + \
                        remark_m + " protocol any"
                else:
                    if port_mode == "trunk":
                        comm = "net add acl mac ce_ingress_" + if_name + \
                            "_l2 priority 1000 accept protocol any"
                    else:
                        raise ValueError(
                            "This qos_menu is not allowed in this port-mode.")

                ifs_flag[if_name] = True
                tmp_comm_list.append((comm, self._recv_message))

        self.common_util_log.logging(
            None,
            self.log_level_debug,
            "internal link command : \n%s" % (tmp_comm_list,),
            __name__)

        return tmp_comm_list

    @decorater_log
    def _set_command_l2slice_merge_ifs(self, ec_info, db_info, merge_info):
        '''
       L2 slice EVPN control command creation - merge, IF basic information
            Create command list for L2 slice EVPN control (merge, IF basic information)
        Parameter:
            ec_info : EC message(Internal link IF information)
            db_info : DB information
            merge_info : Information for command creation
        Return value
            command list (list)
            Execute raise when error occurs
        '''

        tmp_comm_list = []
        clag_flag = {}
        ifs_flag = {}

        for cp in ec_info.get("cp", {}):
            if_name = cp.get("name")
            vlan_id = cp.get("vlan-id")
            port_mode = cp.get("port-mode")

            if cp.get("port-mode") is None:
                if merge_info["if-type"].get(if_name) == "lag" and \
                        (clag_flag.get(if_name) is None):
                    comm = "net add bond " + if_name + \
                        " clag id " + str(cp.get("clag-id"))
                    tmp_comm_list.append((comm, self._recv_message))
                    clag_flag[if_name] = True
                    continue
                elif clag_flag.get(if_name):
                    continue
                else:
                    raise ValueError(
                        "This operation is not allowed in this IF type.")

            if merge_info["if-type"].get(if_name) == "lag":
                if merge_info["first-clag-on-if"].get(if_name) and \
                        (clag_flag.get(if_name) is None):
                    comm = "net add bond " + if_name + \
                        " clag id " + str(cp.get("clag-id"))
                    tmp_comm_list.append((comm, self._recv_message))

                    clag_flag[if_name] = True

                if port_mode == "access":
                    comm = "net add bond " + if_name + \
                        " bridge access " + str(vlan_id)
                    tmp_comm_list.append((comm, self._recv_message))
                else:
                    comm = "net add bond " + if_name + \
                        " bridge vid " + str(vlan_id)
                    tmp_comm_list.append((comm, self._recv_message))

                if merge_info["first-cp-on-if"].get(if_name) and \
                        (ifs_flag.get(if_name) is None):
                    comm = "net add bond " + if_name + \
                        " acl mac ce_ingress_" + if_name + "_l2 inbound"
                    tmp_comm_list.append((comm, self._recv_message))

                    ifs_flag[if_name] = True
            else:
                if cp.get("clag-id"):
                    raise ValueError(
                        "This operation is not allowed in this IF type.")

                if merge_info["first-cp-on-if"].get(if_name) and \
                        (ifs_flag.get(if_name) is None):
                    link_speed = str(int(cp.get("speed").strip("g")) * 1000)
                    comm = "net add interface " + if_name + \
                        " link speed " + link_speed
                    tmp_comm_list.append((comm, self._recv_message))

                if port_mode == "access":
                    comm = "net add interface " + if_name + \
                        " bridge access " + str(vlan_id)
                    tmp_comm_list.append((comm, self._recv_message))
                else:
                    comm = "net add interface " + if_name + \
                        " bridge vid " + str(vlan_id)
                    tmp_comm_list.append((comm, self._recv_message))

                if merge_info["first-cp-on-if"].get(if_name) and \
                        (ifs_flag.get(if_name) is None):
                    comm = "net add interface " + if_name + \
                        " acl mac ce_ingress_" + if_name + "_l2 inbound"
                    tmp_comm_list.append((comm, self._recv_message))

                    ifs_flag[if_name] = True

        self.common_util_log.logging(
            None,
            self.log_level_debug,
            "internal link command : \n%s" % (tmp_comm_list,),
            __name__)

        return tmp_comm_list

    @decorater_log
    def _set_command_l2slice_merge_base(self, ec_info, db_info, merge_info):
        '''
        L2 slide EVPN control command creation -  merge, basic configuration
           Create command list for L2 slide EVPN control (merge, basic configuraiton)
        Parameter:
            ec_info : EC message(Internal link IF information)
        Set from of term to set firewall for VLAN traffic acquisition
            merge_info : Information for command creation
        Return value
            command list (list)
            Execute raise when error occurs
        '''

        tmp_comm_list = []
        ifs_flag = {}
        vlan_flag = {}
        vni_vlan_flag = {}
        vni_flag = {}

        for cp in ec_info.get("cp", {}):
            if_name = cp.get("name")
            vlan_id = cp.get("vlan-id")
            vni = str(cp.get("vni"))

            if cp.get("port-mode") is None:
                continue

            is_first_cp_on_vni = (
                merge_info["first-cp-on-vni"].get(vni) and
                vni_flag.get(vni) is None
            )

            if merge_info["first-cp-on-if"].get(if_name) and \
                    (ifs_flag.get(if_name) is None):
                comm = "net add bridge bridge ports " + if_name
                tmp_comm_list.append((comm, self._recv_message))

                ifs_flag[if_name] = True

            if merge_info["first-cp-on-vlan"].get(vlan_id) and \
                    (vlan_flag.get(vlan_id) is None):
                comm = "net add bridge bridge vids " + str(vlan_id)
                tmp_comm_list.append((comm, self._recv_message))

                vlan_flag[vlan_id] = True

            if is_first_cp_on_vni:
                comm = "net add vxlan vni" + vni + " vxlan id " + vni
                tmp_comm_list.append((comm, self._recv_message))

            if merge_info["first-cp-on-vni-vlan"].get(vni, {}).get(vlan_id) and \
                    (vni_vlan_flag.get(vni, {}).get(vlan_id) is None):
                comm = "net add vxlan vni" + vni + \
                    " bridge access " + str(vlan_id)
                tmp_comm_list.append((comm, self._recv_message))

                if not vni_vlan_flag.get(vni):
                    vni_vlan_flag[vni] = {}
                vni_vlan_flag[vni][vlan_id] = True

            if is_first_cp_on_vni:
                comm = "net add vxlan vni" + vni + " vxlan local-tunnelip " + \
                    db_info.get("device", {}).get("loopback_if_address")
                tmp_comm_list.append((comm, self._recv_message))
                comm = "net add vxlan vni" + vni + " bridge learning off"
                tmp_comm_list.append((comm, self._recv_message))
                comm = "net del vxlan vni" + vni + " stp bpduguard"
                tmp_comm_list.append((comm, self._recv_message))
                comm = "net del vxlan vni" + vni + " stp portbpdufilter"
                tmp_comm_list.append((comm, self._recv_message))

            if is_first_cp_on_vni:
                vni_flag[vni] = True

        self.common_util_log.logging(
            None,
            self.log_level_debug,
            "internal link command : \n%s" % (tmp_comm_list,),
            __name__)

        return tmp_comm_list

    @decorater_log
    def _set_command_l2slice_merge_irb(self, ec_info, db_info, merge_info):
        '''
        L2 slide EVPN control command creation -  merge, IRB
            Create command liast for L2 slide EVPN control (merge, IRB)
        Parameter:
            ec_info : EC message(Internal link IF information)
            db_info : DB information
            merge_info : Information for command creation
        Return value
            command list (list)
            Execute raise when error occurs
        '''

        tmp_comm_list = []
        vlan_flag = {}
        vlan_on_vrf_flag = {}

        if merge_info["irb-slice"]:

            vrf_name = ec_info.get("vrf", {}).get("vrf-name")
            if vrf_name:
                for vrf in db_info.get("vrf_detail", {}):
                    if vrf.get("slice_name") == ec_info.get("slice_name"):
                        vrf_name = vrf.get("vrf_name")

            if merge_info.get("first-vrf-on-slice"):
                comm = "net add bgp vrf " + vrf_name + " autonomous-system " + \
                    str(db_info.get("device", {}).get("as_number"))
                tmp_comm_list.append((comm, self._recv_message))
                comm = "net add bgp vrf " + vrf_name + \
                    " l2vpn evpn advertise ipv4 unicast"
                tmp_comm_list.append((comm, self._recv_message))
                comm = "net add bgp vrf " + \
                    vrf_name + " redistribute connected"
                tmp_comm_list.append((comm, self._recv_message))
                comm = "net add vrf " + vrf_name + " vni " + \
                    str(ec_info.get("vrf", {}).get("l3-vni", {}).get("vni-id"))
                tmp_comm_list.append((comm, self._recv_message))
                comm = "net add vrf " + vrf_name + " vrf-table auto"
                tmp_comm_list.append((comm, self._recv_message))

                comm = "net add vlan " + \
                    str(ec_info.get("vrf", {}).get(
                        "l3-vni", {}).get("vlan-id")) + " vrf " + vrf_name
                tmp_comm_list.append((comm, self._recv_message))
                comm = "net add vlan " + \
                    str(ec_info.get("vrf", {}).get("l3-vni", {}).get("vlan-id")) + \
                    " vlan-id " + \
                    str(ec_info.get(
                        "vrf", {}).get("l3-vni", {}).get("vlan-id"))
                tmp_comm_list.append((comm, self._recv_message))
                comm = "net add vlan " + \
                    str(ec_info.get("vrf", {}).get("l3-vni", {}).get(
                        "vlan-id")) + " vlan-raw-device bridge"
                tmp_comm_list.append((comm, self._recv_message))

                anycast_id = None
                if merge_info.get("multi-homing") == "ec":
                    tmp = ec_info.get("multi-homing", {}).get("anycast", {})
                    anycast_id = tmp.get("id")
                elif merge_info.get("multi-homing") == "db":
                    anycast_id = (
                        db_info.get("multi_homing", {}).get("anycast_id"))

                if anycast_id:
                    sys_mac = self._gen_sysmac_from_anycast_id(int(anycast_id))
                    tmp = ec_info.get("vrf", {}).get("l3-vni", {})
                    vrf_vlan = tmp.get("vlan-id")
                    comm = "net add vlan {0} hwaddress {1}".format(vrf_vlan,
                                                                   sys_mac)
                    tmp_comm_list.append((comm, self._recv_message))

                comm = "net add vxlan vni" + \
                    str(ec_info.get("vrf", {}).get("l3-vni", {}).get(
                        "vni-id")) + " vxlan id " + \
                    str(ec_info.get("vrf", {}).get("l3-vni", {}).get(
                        "vni-id"))
                tmp_comm_list.append((comm, self._recv_message))
                comm = "net add vxlan vni" + \
                    str(ec_info.get("vrf", {}).get("l3-vni", {}).get(
                        "vni-id")) + " bridge access " + \
                    str(ec_info.get("vrf", {}).get("l3-vni", {}).get(
                        "vlan-id"))
                tmp_comm_list.append((comm, self._recv_message))
                comm = "net add vxlan vni" + \
                    str(ec_info.get("vrf", {}).get("l3-vni", {}).get(
                        "vni-id")) + " vxlan local-tunnelip " + \
                    db_info.get("device", {}).get("loopback_if_address")
                tmp_comm_list.append((comm, self._recv_message))
                comm = "net add vxlan vni" + \
                    str(ec_info.get("vrf", {}).get("l3-vni", {}).get(
                        "vni-id")) + \
                    " bridge learning off"
                tmp_comm_list.append((comm, self._recv_message))
                comm = "net del vxlan vni" + \
                    str(ec_info.get("vrf", {}).get("l3-vni", {}).get(
                        "vni-id")) + " stp bpduguard"
                tmp_comm_list.append((comm, self._recv_message))
                comm = "net del vxlan vni" + \
                    str(ec_info.get("vrf", {}).get("l3-vni", {}).get(
                        "vni-id")) + " stp portbpdufilter"
                tmp_comm_list.append((comm, self._recv_message))

            for cp in ec_info.get("cp", {}):
                vlan_id = cp.get("vlan-id")
                irb_info = cp.get("irb", {})

                if cp.get("port-mode") is None:
                    continue

                is_first_cp_on_vlan = (
                    merge_info["first-cp-on-vlan"].get(vlan_id) and
                    vlan_flag.get(vlan_id) is None
                )
                is_first_vrf_on_vlan = (
                    merge_info.get("first-vrf-on-slice") and
                    vlan_on_vrf_flag.get(vlan_id) is None
                )

                if is_first_cp_on_vlan:
                    comm = "net add vlan " + str(vlan_id) + " ip address " + \
                        irb_info.get("physical-ip-address", {}).get("address") + "/" + \
                        str(irb_info.get("physical-ip-address",
                                         {}).get("prefix"))
                    tmp_comm_list.append((comm, self._recv_message))

                    comm = "net add vlan " + str(vlan_id) + " ip address-virtual " + \
                        irb_info.get("virtual-mac-address") + " " + \
                        irb_info.get("virtual-gateway", {}).get("address") + "/" + \
                        str(irb_info.get("virtual-gateway", {}).get("prefix"))
                    tmp_comm_list.append((comm, self._recv_message))

                    comm = "net add vlan " + str(vlan_id) + \
                        " vlan-id " + str(vlan_id)
                    tmp_comm_list.append((comm, self._recv_message))

                    comm = "net add vlan " + str(vlan_id) + \
                        " vlan-raw-device bridge"
                    tmp_comm_list.append((comm, self._recv_message))

                if is_first_cp_on_vlan or is_first_vrf_on_vlan:
                    comm = "net add vlan " + str(vlan_id) + " vrf " + vrf_name
                    tmp_comm_list.append((comm, self._recv_message))

                if is_first_cp_on_vlan:
                    vlan_flag[vlan_id] = True
                if is_first_vrf_on_vlan:
                    vlan_on_vrf_flag[vlan_id] = True

        self.common_util_log.logging(
            None,
            self.log_level_debug,
            "internal link command : \n%s" % (tmp_comm_list,),
            __name__)

        return tmp_comm_list

    @decorater_log
    def _set_command_l2slice_merge_multi(self, ec_info, db_info, merge_info):
        '''
        L2 slide EVPN control command creation -  merge, multihoming
            Create command list for L2 slide EVPN control (merge, multihoming)
        Parameter:
            ec_info : EC message(Internal link IF information)
            db_info : DB information
            merge_info : Information for command creation
        Return value
            command list (list)
            Execute raise when error occurs
        '''

        tmp_comm_list = []

        if (merge_info["multi-homing"] == "ec" and
                merge_info["first-multi-homing"]):

            comm = "net add loopback lo clag vxlan-anycast-ip " + \
                ec_info.get("multi-homing", {}).get("anycast",
                                                    {}).get("address")
            tmp_comm_list.append((comm, self._recv_message))
            comm = "net add bond peerlink bond slaves swp47"
            tmp_comm_list.append((comm, self._recv_message))
            comm = "net add bond peerlink bond slaves swp48"
            tmp_comm_list.append((comm, self._recv_message))
            comm = "net add bridge bridge ports peerlink"
            tmp_comm_list.append((comm, self._recv_message))
            comm = "net add interface peerlink.4094 clag backup-ip " + \
                ec_info.get("multi-homing", {}).get(
                    "clag", {}).get("backup", {}).get("address")
            tmp_comm_list.append((comm, self._recv_message))
            comm = "net add interface peerlink.4094 clag peer-ip " + \
                ec_info.get("multi-homing", {}).get(
                    "clag", {}).get("peer", {}).get("address")
            tmp_comm_list.append((comm, self._recv_message))
            anycast_id = int(
                ec_info.get("multi-homing", {}).get("anycast", {}).get("id"))
            sys_mac = self._gen_sysmac_from_anycast_id(anycast_id)
            comm = ("net add interface peerlink.4094 " +
                    "clag sys-mac {0}".format(sys_mac))
            tmp_comm_list.append((comm, self._recv_message))
            comm = "net add interface peerlink.4094 ip address " + \
                ec_info.get("multi-homing", {}).get("interface", {}).get("address") + \
                "/" + str(ec_info.get("multi-homing", {}
                                      ).get("interface", {}).get("prefix"))
            tmp_comm_list.append((comm, self._recv_message))
            comm = "net add ospf network " + \
                ec_info.get("multi-homing", {}).get("anycast", {}).get("address") + \
                "/32 area 0.0.0." + \
                str(db_info.get("device", {}).get("cluster_ospf_area"))
            tmp_comm_list.append((comm, self._recv_message))

        self.common_util_log.logging(
            None,
            self.log_level_debug,
            "internal link command : \n%s" % (tmp_comm_list,),
            __name__)

        return tmp_comm_list

    @decorater_log
    def _set_command_l2slice_merge_policyd(self, ec_info, db_info, merge_info):
        '''
        L2 slide EVPN control command creation -  merge, policyd
            Create command list for L2 slide EVPN control (merge, policyd)
        Parameter:
            ec_info : EC message(Internal link IF information)
            db_info : DB information
            merge_info : Information for command creation
        Return value
            command list (list)
            Execute raise when error occurs
        '''

        tmp_comm_list = []
        ifs_flag = {}

        for cp in ec_info.get("cp", {}):
            if_name = cp.get("name")

            if cp.get("port-mode") is None:
                continue

            if merge_info["first-cp-on-if"].get(if_name) and \
                    (ifs_flag.get(if_name) is None):

                ifs_flag[if_name] = True

                if_speed = merge_info["if-speed"].get(cp.get("name"))
                ingress = cp.get("qos", {}).get("inflow-shaping-rate")
                egress = cp.get("qos", {}).get("outflow-shaping-rate")

                if ingress:
                    tmp_comm_list.extend(self._get_policyd_cmd(
                        self._MERGE, "ingress", ingress, if_speed, if_name))

                if egress:
                    tmp_comm_list.extend(self._get_policyd_cmd(
                        self._MERGE, "egress", egress, if_speed, if_name))

        self.common_util_log.logging(
            None,
            self.log_level_debug,
            "internal link command : \n%s" % (tmp_comm_list,),
            __name__)

        return tmp_comm_list


    @decorater_log
    def _gen_l2_slice_delete_message_for_cmd(self, ec_info, db_info):
        '''
        Create information for L2 slide EVPN control command deletion
            Organise EC message and DB information to make command creation easier
        Parameter:
            ec_info : EC message(Internal link IF information)
            db_info : DB information
        Return value
            Information list for L2 slice creation (dict)
                multi-homing       Object of Multihoming setting information (str)
                irb-slice          Whether slide is corresponding to IRB or not (boolean)
                last-cp-on-if      Whether it is a lst CP for IF or not (dict)
                last-cp-on-vlan    Whether it is a lst CP for VLAN or not (dict)
                last-cp-on-slice   Whether it is a lst CP for slide or not (boolean)
                last-cp-on-device  Whether it is the last CP for device or not (boolean)
                last-clag-on-if    Whether it is the last clag for IF or not (dict)
                if-type            IF type of each IF (dict)
                port-mode          port-mode type of each IF (dict)
                clag-id            clag-id which is linked with each IF (dicr)
            Execute raise when error occurs
        '''

        tmp_flug = \
            {
                "multi-homing": None,
                "irb-slice": False,
                "last-cp-on-if": {},
                "last-cp-on-vlan": {},
                "last-cp-on-slice": False,
                "last-cp-on-device": False,
                "last-cp-on-vni": {},
                "last-cp-on-vni-vlan": {},
                "last-clag-on-if": {},
                "if-type": {},
                "port-mode": {},
                "clag-id": {},
                "cp_db": {},
                "irb-vrf": {}
            }

        slice_name = ec_info.get("slice_name")

        if db_info.get("multi_homing"):
            tmp_flug["multi-homing"] = "db"

        cps_on_ifs_in_ec_mes = {}
        cps_on_vlans_in_ec_mes = {}
        cps_on_slice_in_ec_mes = 0
        cps_on_vni_in_ec_mes = {}
        cps_on_vnivlan_in_ec_mes = {}
        for cp in ec_info.get("cp", {}):
            if_name = cp.get("name")
            vlan_id = cp.get("vlan-id")
            clag_id = cp.get("clag-id")
            vni = None
            for db_cp in db_info.get("cp", ()):
                if (db_cp.get("if_name") == if_name and
                    db_cp.get("vlan", {}).get("vlan_id") == vlan_id and
                        db_cp.get("slice_name") == slice_name):
                    vni = db_cp.get("vni")
                    break

            if not tmp_flug["if-type"].get(if_name):
                tmp_flug["if-type"][if_name] = "physical"
                for lag_if in db_info.get("lag", {}):
                    if if_name == lag_if.get("if_name"):
                        tmp_flug["if-type"][if_name] = "lag"
                        break

            if str(clag_id) == str(self._DELETE_CLAG_ID_FLAG):
                if cps_on_ifs_in_ec_mes.get(if_name) is None:
                    cps_on_ifs_in_ec_mes[if_name] = 0
                if cps_on_vlans_in_ec_mes.get(vlan_id) is None:
                    cps_on_vlans_in_ec_mes[vlan_id] = 0
                continue

            cps_on_slice_in_ec_mes += 1

            cps_on_ifs_in_ec_mes[if_name] = \
                self._flag_count_up(cps_on_ifs_in_ec_mes.get(if_name))

            cps_on_vlans_in_ec_mes[vlan_id] = \
                self._flag_count_up(cps_on_vlans_in_ec_mes.get(vlan_id))

            cps_on_vni_in_ec_mes[vni] = \
                self._flag_count_up(cps_on_vni_in_ec_mes.get(vni))

            if not cps_on_vnivlan_in_ec_mes.get(vni):
                cps_on_vnivlan_in_ec_mes[vni] = {}
            if not cps_on_vnivlan_in_ec_mes[vni].get(vlan_id):
                cps_on_vnivlan_in_ec_mes[vni][vlan_id] = 1
            else:
                cps_on_vnivlan_in_ec_mes[vni][vlan_id] += 1

        remain_clag_on_ifs_in_db_info = {}
        cps_on_ifs_in_db_info = {}
        clags_on_ifs_in_db_info = {}
        cps_on_vlans_in_db_info = {}
        cps_on_slice_in_db_info = 0
        cps_on_device_in_db_info = 0
        cps_on_vni_in_db_info = {}
        cps_on_vnivlan_in_db_info = {}
        for cp in db_info.get("cp", {}):
            if_name = cp.get("if_name")
            vlan_id = cp.get("vlan").get("vlan_id")
            vni = cp.get("vni")
            clag_id = cp.get("clag-id")
            irb_info = cp.get("irb_ipv4_address")

            if not tmp_flug["port-mode"].get(if_name):
                tmp_flug["port-mode"][if_name] = cp.get(
                    "vlan").get("port_mode")

            if (not tmp_flug["clag-id"].get(if_name)) and clag_id and \
                    (clag_id != self._DELETE_CLAG_ID_FLAG):
                tmp_flug["clag-id"][if_name] = clag_id

            cps_on_device_in_db_info += 1

            if cp.get("slice_name") == ec_info.get("slice_name"):
                cps_on_slice_in_db_info += 1

                if not tmp_flug["cp_db"].get(if_name):
                    tmp_flug["cp_db"][if_name] = {}
                tmp_flug["cp_db"][if_name][vlan_id] = {}
                tmp_flug["cp_db"][if_name][vlan_id]["vni"] = cp.get("vni")
                tmp_flug["cp_db"][if_name][vlan_id]["ingress"] = cp.get(
                    "qos", {}).get("inflow_shaping_rate")
                tmp_flug["cp_db"][if_name][vlan_id]["egress"] = cp.get(
                    "qos", {}).get("outflow_shaping_rate")

                if irb_info:
                    tmp_flug["irb-slice"] = True

                    if not tmp_flug["irb-vrf"]:
                        for vrf_info in db_info.get("vrf_detail", {}):
                            if vrf_info.get("if_name") == if_name and \
                                vrf_info.get("vlan_id") == vlan_id and \
                                    vrf_info.get("slice_name") == \
                                    cp.get("slice_name"):
                                tmp_flug["irb-vrf"]["vrf_name"] = vrf_info.get(
                                    "vrf_name")
                                tmp_flug["irb-vrf"]["l3_vni_vni_id"] = \
                                    vrf_info.get(
                                    "l3_vni", {}).get("vni")
                                tmp_flug["irb-vrf"]["l3_vni_vlan_id"] = \
                                    vrf_info.get(
                                    "l3_vni", {}).get("vlan_id")
                                break

            cps_on_ifs_in_db_info[if_name] = \
                self._flag_count_up(cps_on_ifs_in_db_info.get(if_name))

            cps_on_vlans_in_db_info[vlan_id] = \
                self._flag_count_up(cps_on_vlans_in_db_info.get(vlan_id))

            if clag_id:
                clags_on_ifs_in_db_info[if_name] = \
                    self._flag_count_up(clags_on_ifs_in_db_info.get(if_name))

            cps_on_vni_in_db_info[vni] = \
                self._flag_count_up(cps_on_vni_in_db_info.get(vni))

            if not cps_on_vnivlan_in_db_info.get(vni):
                cps_on_vnivlan_in_db_info[vni] = {}
            if not cps_on_vnivlan_in_db_info.get(vni).get(vlan_id):
                cps_on_vnivlan_in_db_info[vni][vlan_id] = 1
            else:
                cps_on_vnivlan_in_db_info[vni][vlan_id] += 1

            not_found_flug = True
            for ec_cp in ec_info.get("cp", {}):
                if (ec_cp.get("name") == if_name) and \
                    (ec_cp.get("vlan-id") == vlan_id) and \
                        cp.get("slice_name") == ec_info.get("slice_name"):
                    not_found_flug = False
                    break

            if not_found_flug and clag_id:
                remain_clag_on_ifs_in_db_info[if_name] = \
                    self._flag_count_up(
                        remain_clag_on_ifs_in_db_info.get(if_name))

        if cps_on_slice_in_db_info == cps_on_slice_in_ec_mes:
            tmp_flug["last-cp-on-slice"] = True
            if cps_on_slice_in_ec_mes == cps_on_device_in_db_info:
                tmp_flug["last-cp-on-device"] = True

        for ifs_name in cps_on_ifs_in_ec_mes.keys():
            if cps_on_ifs_in_db_info.get(ifs_name) == \
                    cps_on_ifs_in_ec_mes.get(ifs_name):
                tmp_flug["last-cp-on-if"][ifs_name] = True
            else:
                tmp_flug["last-cp-on-if"][ifs_name] = False

        for vlan in cps_on_vlans_in_ec_mes.keys():
            if cps_on_vlans_in_db_info.get(vlan) == \
                    cps_on_vlans_in_ec_mes.get(vlan):
                tmp_flug["last-cp-on-vlan"][vlan] = True
            else:
                tmp_flug["last-cp-on-vlan"][vlan] = False

        for vni in cps_on_vni_in_ec_mes.keys():
            if cps_on_vni_in_db_info.get(vni) == \
                    cps_on_vni_in_ec_mes.get(vni):
                tmp_flug["last-cp-on-vni"][vni] = True
            else:
                tmp_flug["last-cp-on-vni"][vni] = False

        for vni in cps_on_vnivlan_in_ec_mes.keys():
            tmp_flug["last-cp-on-vni-vlan"][vni] = {}

            for vlan in cps_on_vnivlan_in_ec_mes.get(vni, {}).keys():
                if cps_on_vnivlan_in_db_info.get(vni, {}).get(vlan) == \
                        cps_on_vnivlan_in_ec_mes.get(vni).get(vlan):
                    tmp_flug["last-cp-on-vni-vlan"][vni][vlan] = True
                else:
                    tmp_flug["last-cp-on-vni-vlan"][vni][vlan] = False

        for ifs_name in cps_on_ifs_in_db_info.keys():
            if remain_clag_on_ifs_in_db_info.get(ifs_name):
                tmp_flug["last-clag-on-if"][ifs_name] = False
            elif clags_on_ifs_in_db_info.get(ifs_name) is None:
                continue
            else:
                tmp_flug["last-clag-on-if"][ifs_name] = True

        return tmp_flug

    @decorater_log
    def _set_command_l2slice_delete_qos(self, ec_info, db_info, delete_info):
        '''
        Creation of Parameter from EC(Obtain cp data from cp)
            L2 slice EVPN control command creatin - delete, qos
        Parameter:
            ec_info : EC message(Internal link IF information)
            db_info : DB information
            delete_info : Information for command creation
        Return value
            command list (list)
            Execute raise when error occurs
        '''

        tmp_comm_list = []
        ifs_flag = {}

        for cp in ec_info.get("cp", {}):
            if_name = cp.get("name")

            if cp.get("clag-id") == self._DELETE_CLAG_ID_FLAG:
                continue

            if delete_info["last-cp-on-if"].get(if_name) and \
                    (ifs_flag.get(if_name) is None):
                comm = "net del acl mac ce_ingress_" + \
                    if_name + "_l2 priority 1000"

                ifs_flag[if_name] = True
                tmp_comm_list.append((comm, self._recv_message))

        self.common_util_log.logging(
            None,
            self.log_level_debug,
            "internal link command : \n%s" % (tmp_comm_list,),
            __name__)

        return tmp_comm_list

    @decorater_log
    def _set_command_l2slice_delete_ifs(self, ec_info, db_info, delete_info):
        '''
        L2 slide EVPN control command creation -  delete, IF basic information
            Create command list for L2 slide EVPN control  (delete, IF basic information)
        Parameter:
            ec_info : EC message(Internal link IF information)
            db_info : DB information
            delete_info : Information for command creation
        Return value
            command list (list)
            Execute raise when error occurs
        '''

        tmp_comm_list = []
        clag_flag = {}
        ifs_flag = {}

        for cp in ec_info.get("cp", {}):
            if_name = cp.get("name")
            vlan_id = str(cp.get("vlan-id"))

            if delete_info["if-type"].get(if_name) == "lag":
                if delete_info["last-clag-on-if"].get(if_name) and \
                        (clag_flag.get(if_name) is None):
                    comm = "net del bond " + if_name + \
                        " clag id " + str(delete_info["clag-id"].get(if_name))
                    tmp_comm_list.append((comm, self._recv_message))

                    clag_flag[if_name] = True

                if cp.get("clag-id") == self._DELETE_CLAG_ID_FLAG:
                    continue

                if delete_info["port-mode"].get(if_name) == "access":
                    comm = "net del bond " + if_name + \
                        " bridge access " + vlan_id
                    tmp_comm_list.append((comm, self._recv_message))
                else:
                    comm = "net del bond " + if_name + \
                        " bridge vid " + vlan_id
                    tmp_comm_list.append((comm, self._recv_message))

                if delete_info["last-cp-on-if"].get(if_name) and \
                        (ifs_flag.get(if_name) is None):
                    comm = "net del bond " + if_name + \
                        " acl mac ce_ingress_" + if_name + "_l2 inbound"
                    tmp_comm_list.append((comm, self._recv_message))

                    ifs_flag[if_name] = True
            else:
                if cp.get("clag-id"):
                    raise ValueError(
                        "This operation is not allowed in this IF type.")

                if delete_info["last-cp-on-if"].get(if_name) and \
                        (ifs_flag.get(if_name) is None):
                    comm = "net del interface " + if_name
                    tmp_comm_list.append((comm, self._recv_message))

                    ifs_flag[if_name] = True

        self.common_util_log.logging(
            None,
            self.log_level_debug,
            "internal link command : \n%s" % (tmp_comm_list,),
            __name__)

        return tmp_comm_list

    @decorater_log
    def _set_command_l2slice_delete_base(self, ec_info, db_info, delete_info):
        '''
        L2 slide EVPN control command creation -  delete, basic configuration
           Create command list for L2 slide EVPN control (delete, basic configuration)
        Parameter:
            ec_info : EC message(Internal link IF information)
            db_info : DB information
            delete_info : Information for command creation
        Return value
            command list (list)
            Execute raise when error occurs
        '''

        tmp_comm_list = []
        last_vlan_list = []
        last_if_list = []
        last_vni_list = []
        last_vni_vlan_flag = {}

        for cp in ec_info.get("cp", {}):
            if_name = cp.get("name")
            vlan_id = cp.get("vlan-id")
            vni = delete_info["cp_db"].get(if_name).get(vlan_id).get("vni")

            if cp.get("clag-id") == self._DELETE_CLAG_ID_FLAG:
                continue

            is_last_vlan_cp = (
                delete_info["last-cp-on-vlan"].get(vlan_id) and
                vlan_id not in last_vlan_list
            )
            is_last_vni = (
                delete_info["last-cp-on-vni"].get(vni) and
                vni not in last_vni_list
            )
            is_last_if = (
                delete_info["last-cp-on-if"].get(if_name) and
                if_name not in last_if_list
            )
            is_last_vlan_vni = (
                delete_info["last-cp-on-vni-vlan"].get(vni, {}).get(vlan_id)
                and not last_vni_vlan_flag.get(vni, {}).get(vlan_id)
            )

            if is_last_vlan_cp:
                comm = "net del bridge bridge vids {0}".format(vlan_id)
                tmp_comm_list.append((comm, self._recv_message))

            if is_last_if:
                comm = "net del bridge bridge ports {0}".format(if_name)
                tmp_comm_list.append((comm, self._recv_message))

            if is_last_vni:
                comm = "net del vxlan vni{0}".format(vni)
                tmp_comm_list.append((comm, self._recv_message))
            elif (is_last_vlan_vni and not
                  delete_info["last-cp-on-vni"].get(vni)):
                comm = ("net del vxlan " +
                        "vni{0} bridge access {1}".format(vni, vlan_id))
                tmp_comm_list.append((comm, self._recv_message))
                if not last_vni_vlan_flag.get(vni):
                    last_vni_vlan_flag[vni] = {}
                last_vni_vlan_flag[vni][vlan_id] = True

            if is_last_vlan_cp:
                last_vlan_list.append(vlan_id)
            if is_last_if:
                last_if_list.append(if_name)
            if is_last_vni:
                last_vni_list.append(vni)

        self.common_util_log.logging(
            None,
            self.log_level_debug,
            "internal link command : \n%s" % (tmp_comm_list,),
            __name__)

        return tmp_comm_list

    @decorater_log
    def _set_command_l2slice_delete_irb(self, ec_info, db_info, delete_info):
        '''
        L2 slide EVPN control command creation -  delete, IRB
            Create command list for L2 slide EVPN control (delete, IRB)
        Parameter:
            ec_info : EC message(Internal link IF information)
            db_info : DB information
            delete_info : Information for command creation
        Return value
            command list (list)
            Execute raise when error occurs
        '''

        tmp_comm_list = []
        vlan_flag = {}

        if delete_info["irb-slice"]:

            vrf_name = delete_info["irb-vrf"].get("vrf_name")

            for cp in ec_info.get("cp", {}):
                vlan_id = cp.get("vlan-id")

                if cp.get("clag-id") == self._DELETE_CLAG_ID_FLAG:
                    continue

                if delete_info["last-cp-on-vlan"].get(vlan_id) and \
                        (vlan_flag.get(vlan_id) is None):
                    comm = "net del vlan " + str(vlan_id)
                    tmp_comm_list.append((comm, self._recv_message))

                    vlan_flag[vlan_id] = True

            if delete_info.get("last-cp-on-slice"):
                comm = "net del bgp vrf " + vrf_name + " autonomous-system " + \
                    str(db_info.get("device", {}).get("as_number"))
                tmp_comm_list.append((comm, self._recv_message))
                comm = "net del vrf " + vrf_name + " vni " + \
                    str(delete_info["irb-vrf"].get("l3_vni_vni_id"))
                tmp_comm_list.append((comm, self._recv_message))
                comm = "net del vrf " + vrf_name
                tmp_comm_list.append((comm, self._recv_message))

                comm = "net del vlan " + \
                    str(delete_info["irb-vrf"].get("l3_vni_vlan_id"))
                tmp_comm_list.append((comm, self._recv_message))
                comm = "net del vxlan vni" + \
                    str(delete_info["irb-vrf"].get("l3_vni_vni_id"))
                tmp_comm_list.append((comm, self._recv_message))

        self.common_util_log.logging(
            None,
            self.log_level_debug,
            "internal link command : \n%s" % (tmp_comm_list,),
            __name__)

        return tmp_comm_list

    @decorater_log
    def _set_command_l2slice_delete_multi(self, ec_info, db_info, delete_info):
        '''
        L2 slide EVPN control command creation -  delete, multihoming
            Create command list for L2 slide EVPN control (delete, multihoming)
        Parameter:
            ec_info : EC message(Internal link IF information)
            db_info : DB information
            delete_info : Information for command creation
        Return value
            command list (list)
            Execute raise when error occurs
        '''

        tmp_comm_list = []

        if delete_info["multi-homing"] == "db" and \
                delete_info["last-cp-on-device"]:

            comm = "net del bond peerlink"
            tmp_comm_list.append((comm, self._recv_message))
            comm = "net del interface swp47"
            tmp_comm_list.append((comm, self._recv_message))
            comm = "net del interface swp48"
            tmp_comm_list.append((comm, self._recv_message))
            comm = "net del loopback lo clag vxlan-anycast-ip " + \
                db_info.get("multi_homing", {}).get("anycast_address")
            tmp_comm_list.append((comm, self._recv_message))
            comm = "net del ospf network " + \
                db_info.get("multi_homing", {}).get("anycast_address") + \
                "/32 area 0.0.0." + \
                str(db_info.get("device", {}).get("cluster_ospf_area"))
            tmp_comm_list.append((comm, self._recv_message))

        self.common_util_log.logging(
            None,
            self.log_level_debug,
            "internal link command : \n%s" % (tmp_comm_list,),
            __name__)

        return tmp_comm_list

    @decorater_log
    def _set_command_l2slice_delete_policyd(self,
                                            ec_info,
                                            db_info,
                                            delete_info):
        '''
        L2 slide EVPN control command creation -  merge, policyd
            Create command list for L2 slide EVPN control (merge, policyd)
        Parameter:
            ec_info : EC message(Internal link IF information)
            db_info : DB information
            delete_info : Information for command creation
        Return value
            command list (list)
            Execute raise when error occurs
        '''

        tmp_comm_list = []
        ifs_flag = {}

        for cp in ec_info.get("cp", ()):
            if_name = cp.get("name")

            if cp.get("clag-id") == self._DELETE_CLAG_ID_FLAG:
                continue

            if delete_info["last-cp-on-if"].get(if_name) and \
                    (ifs_flag.get(if_name) is None):
                ifs_flag[if_name] = True
                ingress = delete_info["cp_db"].get(cp.get("name"), {}).get(
                    cp.get("vlan-id"), {}).get("ingress")
                egress = delete_info["cp_db"].get(cp.get("name"), {}).get(
                    cp.get("vlan-id"), {}).get("egress")

                comm_fmt = "rm -f /etc/cumulus/acl/policy.d/10_{0}_{1}.rules"
                if ingress:
                    comm = comm_fmt.format("ingress", if_name)
                    tmp_comm_list.extend(
                        self._set_sudo_command(comm, self._recv_message)
                    )
                if egress:
                    comm = comm_fmt.format("egress", if_name)
                    tmp_comm_list.extend(
                        self._set_sudo_command(comm, self._recv_message)
                    )

        self.common_util_log.logging(
            None,
            self.log_level_debug,
            "policy.d command : \n%s" % (tmp_comm_list,),
            __name__)

        return tmp_comm_list


    @decorater_log
    def _gen_l2_slice_replace_message_for_cmd(self, ec_info, db_info):
        '''
        Information creation for L2 slide EVPN control command change
            Organise EC message and DB information to make command creation easier
        Parameter:
            ec_info : EC message(Internal link IF information)
            db_info : DB information
        Return value
            Information list for L2 slice change (dict)
                flow-rate          Input/output limit value (dict)
                remark-menu        Value of remark menu (str)
                if-type            IF type of each IF (dict)
                port-mode          port-mode type of each IF (dict)
                if-speed           Information of each CP (dict
        Execute raise when error occurs
        '''

        tmp_flug = \
            {
                "flow-rate": {},
                "remark-menu": None,
                "if-type": {},
                "port-mode": {},
                "if-speed": {},
            }

        for cp in ec_info.get("cp", {}):
            if_name = cp.get("name")

            if (tmp_flug["flow-rate"].get(if_name) is None) and \
                ((cp.get("qos", {}).get("inflow-shaping-rate") is not None) or
                 (cp.get("qos", {}).get("outflow-shaping-rate") is not None)):
                tmp_flug["flow-rate"][if_name] = {}
                tmp_flug["flow-rate"][if_name]["inflow-shaping-rate"] = cp.get(
                    "qos", {}).get("inflow-shaping-rate")
                tmp_flug["flow-rate"][if_name]["outflow-shaping-rate"] = \
                    cp.get("qos", {}).get("outflow-shaping-rate")

            if tmp_flug["remark-menu"] is None:
                tmp_flug["remark-menu"] = cp.get("qos", {}).get("remark-menu")

            if not tmp_flug["if-type"].get(if_name):
                tmp_flug["if-type"][if_name] = "physical"
                for lag_if in db_info.get("lag", {}):
                    if if_name == lag_if.get("if_name"):
                        tmp_flug["if-type"][if_name] = "lag"
                        break

        for cp in db_info.get("cp", {}):
            if_name = cp.get("if_name")

            if not tmp_flug["port-mode"].get(if_name):
                tmp_flug["port-mode"][if_name] = cp.get(
                    "vlan").get("port_mode")

            if not tmp_flug["if-speed"].get(if_name):
                if tmp_flug["if-type"].get(if_name) == "physical":
                    tmp_flug["if-speed"][if_name] = cp.get(
                        "speed").strip("g")
                else:
                    for lag_if in db_info.get("lag", {}):
                        if if_name == lag_if.get("if_name"):
                            tmp_flug["if-speed"][if_name] = \
                                int(lag_if.get("link_speed").strip("g")) * \
                                int(lag_if.get("links"))
                            break

        return tmp_flug

    @decorater_log
    def _set_command_l2slice_replace_qos(self, ec_info, db_info, replace_info):
        '''
        L2 slide EVPN control command creation -  replace, qos
            Create command list for L2 slide EVPN control  (replace, qos)
        Parameter:
            ec_info : EC message(Internal link IF information)
            db_info : DB information
            replace_info : Information for command creation
        Return value
            command list (list)
            Execute raise when error occurs
        '''

        tmp_comm_list = []
        ifs_flag = {}

        if replace_info.get("remark-menu") is None:
            return tmp_comm_list

        for cp in ec_info.get("cp", {}):
            if_name = cp.get("name")

            if ifs_flag.get(if_name) is None:
                port_mode = replace_info.get("port-mode", {}).get(if_name)
                cp_qos = \
                    {
                        "qos": {}
                    }
                cp_qos["qos"]["remark-menu"] = replace_info.get(
                    "remark-menu")
                qos_val = self._get_cp_qos_info_from_ec(cp_qos, db_info)
                remark_m = str(qos_val["REMARK-MENU"]["IPV4"]) \
                    if qos_val.get("REMARK-MENU", {}).get("IPV4") \
                    is not None else None

                if remark_m:
                    comm = "net add acl mac ce_ingress_" + if_name + \
                        "_l2 priority 1000 set-class " + \
                        remark_m + " protocol any"
                else:
                    if port_mode == "trunk":
                        comm = "net add acl mac ce_ingress_" + if_name + \
                            "_l2 priority 1000 accept protocol any"
                    else:
                        raise ValueError(
                            "This qos_menu is not allowed in this port-mode.")

                ifs_flag[if_name] = True
                tmp_comm_list.append((comm, self._recv_message))

        self.common_util_log.logging(
            None,
            self.log_level_debug,
            "internal link command : \n%s" % (tmp_comm_list,),
            __name__)

        return tmp_comm_list

    @decorater_log
    def _set_command_l2slice_replace_policyd(self,
                                             ec_info,
                                             db_info,
                                             replace_info):
        '''
        L2 slide EVPN control command creation -  replace, policyd
           Create command list for L2 slide EVPN control (replace, policyd)
        Parameter:
        Create list for class-or-service
            db_info : DB information
            replace_info : Information for command creation
        Return value
            command list (list)
            Execute raise when error occurs
        '''

        tmp_comm_list = []
        ifs_flag = {}

        for cp in ec_info.get("cp", {}):
            if_name = cp.get("name")

            if ifs_flag.get(if_name) is None:

                if replace_info["flow-rate"].get(if_name) is None:
                    continue

                ifs_flag[if_name] = True

                if_speed = replace_info["if-speed"].get(if_name)
                ingress = replace_info["flow-rate"][if_name].get(
                    "inflow-shaping-rate")
                egress = replace_info["flow-rate"][if_name].get(
                    "outflow-shaping-rate")

                if ingress:
                    tmp_comm_list.extend(self._get_policyd_cmd(
                        self._REPLACE, "ingress", ingress, if_speed, if_name))

                if egress:
                    tmp_comm_list.extend(self._get_policyd_cmd(
                        self._REPLACE, "egress", egress, if_speed, if_name))

        self.common_util_log.logging(
            None,
            self.log_level_debug,
            "internal link command : \n%s" % (tmp_comm_list,),
            __name__)

        return tmp_comm_list


    @decorater_log
    def _flag_count_up(self, judge_flag):
        '''
        Add qos information from EC to the CP information to be set.
        Argument:
            Flag for judgment of judge_flag: int
        Return value:
            Count value (int)
        '''

        if judge_flag is None:
            return 1
        else:
            return judge_flag + 1

    @decorater_log
    def _get_policyd_cmd(self,
                         operation,
                         direction,
                         flow_rate,
                         if_speed,
                         if_name):
        '''
        Add qos information from EC to the CP information to be set.
        Argument:
            operation: str operation type
            direction: str Flow amount limit direction (ingress or egress)
            flow_rate: float Flow amount limit ratio (0～100)
            if_speed:  str IF speed
            if_name:   str IF name
        Return value:
            command list (list)
            Execute raise when error occurs
        '''
        if direction != "ingress" and direction != "egress":
            raise ValueError("This flow direction is not allowed.")

        tmp_comm_list = []

        flow_val = int(round(float(flow_rate) * float(if_speed) *
                             1024.0 * 1024.0 / 100.0))
        tmp_file_fmt = "/etc/cumulus/acl/policy.d/10_{0}_{1}.rules"
        tmp_file = tmp_file_fmt.format(direction, if_name)

        if direction == "ingress":
            tmp_top_policy = "-t mangle -A FORWARD -i"
        else:
            tmp_top_policy = "-A FORWARD -o"

        if operation != self._REPLACE:
            comm = "touch {0}".format(tmp_file)
            tmp_comm_list.extend(
                self._set_sudo_command(comm, self._recv_message)
            )
        echo_data = ""
        comm = "echo '{0}' > {1}".format(echo_data, tmp_file)
        tmp_comm_list.extend(
            self._set_sudo_echo_command(comm, self._recv_message)
        )
        echo_data = "[iptables]"
        comm = "echo '{0}' >> {1}".format(echo_data, tmp_file)
        tmp_comm_list.extend(
            self._set_sudo_echo_command(comm, self._recv_message)
        )
        tmp = ("{0} {1} -j POLICE " +
               "--set-mode KB --set-rate {2} --set-burst 2000")
        echo_data = tmp.format(tmp_top_policy, if_name, flow_val)
        comm = "echo '{0}' >> {1}".format(echo_data, tmp_file)
        tmp_comm_list.extend(
            self._set_sudo_echo_command(comm, self._recv_message)
        )

        return tmp_comm_list

    @decorater_log
    def _get_cp_qos_info_from_ec(self, cp_info_ec, db_info):
        '''
        Add qos information from EC to the CP information to be set.
        Argument:
            cp_info_ec: CP information inserted from dict EC
            db_info: dict DB information
        Return value:
            cp_info_em : qos information to be inserted to dict device
        '''
        cp_info_em = {}

        conf_qos_remark, conf_qos_egress = GlobalModule.EM_CONFIG.get_qos_conf(
            db_info["device"].get("platform_name"),
            db_info["device"].get("os_name"),
            db_info["device"].get("firm_version"))

        tmp_remark_menu = cp_info_ec["qos"].get("remark-menu")
        for tmp_conf_key in conf_qos_remark.keys():
            if tmp_remark_menu == tmp_conf_key:
                tmp_remark_menu = conf_qos_remark[tmp_conf_key]
                break

        cp_info_em["REMARK-MENU"] = tmp_remark_menu

        return cp_info_em

    @decorater_log
    def _gen_sysmac_from_anycast_id(self, anycast_id):
        tmp_hex = "{:04X}".format(anycast_id)
        sys_mac = "44:38:39:FF:{0}:{1}".format(tmp_hex[:2], tmp_hex[2:])
        return sys_mac
