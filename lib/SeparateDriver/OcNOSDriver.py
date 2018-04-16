# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2018 Nippon Telegraph and Telephone Corporation
# Filename: OcNOSDriver.py
'''
Individual section on driver (Ocnos's driver)
'''
import json
import re
import traceback
from EmSeparateDriver import EmSeparateDriver
from EmCommonLog import decorater_log
from EmCLIProtocol import EmCLIProtocol
import GlobalModule


class OcNOSDriver(EmSeparateDriver):
    '''
    Ocnos driver class (taken over from individual section class on driver)
    '''

    _PORT_MODE_ACCESS = "access"
    _PORT_MODE_TRUNK = "trunk"

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        self.as_super = super(OcNOSDriver, self)
        self.as_super.__init__()
        self._port_number = 22

        self.net_protocol = EmCLIProtocol()
        self.net_protocol.error_recv_message = ["%"]
        self._comm_ok_non_enable_mode = ">"
        self._comm_ok_enable_mode = "#"
        self.list_enable_service = [self.name_spine,
                                    self.name_leaf,
                                    self.name_l2_slice,
                                    self.name_celag,
                                    self.name_internal_link, ]
        self.list_no_edit_service = [self.name_spine,
                                     self.name_leaf,
                                     self.name_celag,
                                     self.name_internal_link, ]

    @decorater_log
    def connect_device(self,
                       device_name,
                       device_info,
                       service_type,
                       order_type):
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
            Protocol processing section response :
                int (1:Normal, 2:Capability abnormal, 3:No response)
        '''
        if service_type in self.list_no_edit_service:
            return GlobalModule.COM_CONNECT_OK
        else:
            tmp_device_info = None
            if device_info is not None:
                tmp_json = json.loads(device_info)
                if tmp_json.get("device_info") is not None:
                    tmp_json["device_info"]["port_number"] = self._port_number
                tmp_device_info = json.dumps(tmp_json)
            return self.as_super.connect_device(device_name,
                                                tmp_device_info,
                                                service_type,
                                                order_type)

    @decorater_log
    def update_device_setting(self,
                              device_name,
                              service_type,
                              order_type,
                              ec_message=None):
        '''
        Driver individual section edit control.
            Launch from the common section on driver,
            transmit device control signal to protocol processing section.
        Parameter:
            device_name : Device name
            service_type : Service type
            order_type : Order type
        Return value :
            Processing finish status : int (1:Successfully updated
                                2:Validation check NG
                                3:Updating unsuccessful)
        '''
        self.common_util_log.logging(
            device_name, self.log_level_debug,
            "service=%s,order_type=%s" % (service_type, order_type,), __name__)
        if (not self._check_service_type(device_name, service_type) or
                order_type == self._REPLACE):
            return self._update_error
        if service_type in self.list_no_edit_service:
            return self._update_ok

        is_db_result, device_info = \
            self.common_util_db.read_configureddata_info(
                device_name, service_type)
        if not is_db_result:
            return self._update_error

        send_command = self._gen_l2_slice_command_list(
            device_name, device_info, ec_message, order_type)
        if not send_command:
            return self._update_error

        is_result = self._send_control_signal(device_name,
                                              "edit-config",
                                              send_command,
                                              service_type,
                                              order_type)[0]
        return_val = self._update_ok if is_result else self._update_error
        return return_val

    @decorater_log
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
        Return value :
            Processing finish status : int (1:Successfully deleted
                                2:バValidation check NG
                                3:Deletion unsuccessful)
        '''
        self.common_util_log.logging(
            device_name, self.log_level_debug,
            "service=%s,order_type=%s" % (service_type, order_type,), __name__)
        if (not self._check_service_type(device_name, service_type) or
                order_type == self._REPLACE):
            return self._update_error
        else:
            return self._update_ok

    @decorater_log
    def disconnect_device(self, device_name, service_type, order_type):
        '''
        Driver individual section disconnection control.
            Launch from the common section on driver,
            conduct device disconnection control
            to protocol processing section.
        Parameter:
            device_name : Device name
            service_type : Service type
            order_type : Order type
        Return value :
            Processing finish status : Should always return "True"
        '''
        if service_type in self.list_no_edit_service:
            return True
        else:
            return self.as_super.disconnect_device(device_name,
                                                   service_type,
                                                   order_type)

    @decorater_log
    def _gen_l2_slice_command_list(self,
                                   device_name,
                                   device_info,
                                   ec_message=None,
                                   operation=None):

        try:
            ec_json = json.loads(ec_message)

            device_mes = ec_json.get("device-leaf", {})
            slice_name = device_mes["slice_name"]

            cp_info = self._get_l2_cps_from_ec(device_mes,
                                               device_info,
                                               slice_name)
            vlans_info = self._get_vlans_list(cp_info,
                                              device_info,
                                              slice_name=slice_name,
                                              operation=operation)
            vni_list = self._get_vni_list(cp_info,
                                          device_info,
                                          slice_name=slice_name,
                                          operation=operation)
            if_list = self._get_cos_if_list(cp_info,
                                            device_info,
                                            slice_name=slice_name,
                                            operation=operation)
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

        comm_vlan_db = self._set_command_vlan_database(vlans_info,
                                                       operation=operation)
        comm_interface = self._set_command_interface(if_list,
                                                     operation=operation)
        comm_mac_vrf = self._set_command_mac_vrf(vni_list,
                                                 operation=operation)
        comm_vni_vlan = self._set_command_vni_vlan_mapping(cp_info,
                                                           operation=operation)
        ocnos_command_list = self._set_command_initial()
        if operation == self._DELETE:
            ocnos_command_list.extend(comm_vni_vlan)
            ocnos_command_list.extend(comm_mac_vrf)
            ocnos_command_list.extend(comm_interface)
            ocnos_command_list.extend(comm_vlan_db)
        else:
            ocnos_command_list.extend(comm_vlan_db)
            ocnos_command_list.extend(comm_interface)
            ocnos_command_list.extend(comm_mac_vrf)
            ocnos_command_list.extend(comm_vni_vlan)
        ocnos_command_list.extend(self._set_command_finaly())
        self.common_util_log.logging(
            None,
            self.log_level_debug,
            self._logging_send_command_str(ocnos_command_list),
            __name__)
        return ocnos_command_list

    @decorater_log
    def _set_command_initial(self):
        '''
        Create command list after OcNOS connection.
           Set Terminal length
           Switch to privileged mode
           Switch to configuration mode
        '''
        tmp_comm_list = []
        comm = ("terminal length 0", self._comm_ok_non_enable_mode)
        tmp_comm_list.append(comm)
        comm = ("enable", self._comm_ok_enable_mode)
        tmp_comm_list.append(comm)
        comm = ("conf t", self._comm_ok_enable_mode)
        tmp_comm_list.append(comm)
        self.common_util_log.logging(
            None,
            self.log_level_debug,
            "initial command : \n%s" % (tmp_comm_list,),
            __name__)
        return tmp_comm_list

    @decorater_log
    def _set_command_finaly(self):
        '''
        Create command list after executing config command.
            Cancel configuration mode
            Copy the currently used config to startup-config
            Cancel privileged mode
        '''
        tmp_comm_list = []
        comm = ("end", self._comm_ok_enable_mode)
        tmp_comm_list.append(comm)
        comm = ("copy running-config startup-config",
                self._comm_ok_enable_mode)
        tmp_comm_list.append(comm)
        comm = ("exit", self._comm_ok_non_enable_mode)
        tmp_comm_list.append(comm)
        self.common_util_log.logging(
            None,
            self.log_level_debug,
            "finally command : \n%s" % (tmp_comm_list,),
            __name__)
        return tmp_comm_list

    @decorater_log
    def _set_command_vlan_database(self, vlans_info, operation=None):
        '''
        Create command list for vlan database.
        '''
        tmp_comm_list = []
        if vlans_info:
            comm = ("vlan database", self._comm_ok_enable_mode)
            tmp_comm_list.append(comm)
            for vlan in vlans_info.keys():
                if operation == self._DELETE:
                    comm_txt = "no vlan %s bridge 1"
                else:
                    comm_txt = "vlan %s bridge 1 state enable"
                comm = (comm_txt % (vlan), self._comm_ok_enable_mode)
                tmp_comm_list.append(comm)
            comm = ("exit", self._comm_ok_enable_mode)
            tmp_comm_list.append(comm)
        self.common_util_log.logging(
            None,
            self.log_level_debug,
            "vlan database command : \n%s" % (tmp_comm_list,),
            __name__)
        return tmp_comm_list

    @decorater_log
    def _set_command_interface(self, if_list=(), operation=None):
        '''
        Create command list for interface.
        '''
        tmp_comm_list = []
        for if_info in if_list:
            if if_info.get("IF-TYPE") == self._if_type_phy:
                comm = ("interface %s" % (if_info["IF-NAME"],),
                        self._comm_ok_enable_mode)
                tmp_comm_list.append(comm)
                if operation == self._DELETE:
                    comm_txt = "no switchport"
                else:
                    comm_txt = "switchport"
                comm = (comm_txt, self._comm_ok_enable_mode)
                tmp_comm_list.append(comm)
                comm = ("exit", self._comm_ok_enable_mode)
                tmp_comm_list.append(comm)
        self.common_util_log.logging(
            None,
            self.log_level_debug,
            "interface command : \n%s" % (tmp_comm_list,),
            __name__)
        return tmp_comm_list

    @decorater_log
    def _set_command_mac_vrf(self, vni_list=(), operation=None):
        '''
        Create command list for MAC-VRF settings (nvo vxlan id).
        '''
        tmp_comm_list = []
        for vni in vni_list:
            if operation == self._DELETE:
                comm_txt = "no nvo vxlan id %s"
            else:
                comm_txt = \
                    "nvo vxlan id %s ingress-replication inner-vid-disabled"
            comm = (comm_txt % (vni,), self._comm_ok_enable_mode)
            tmp_comm_list.append(comm)
            if operation != self._DELETE:
                comm = (
                    "vxlan host-reachability-protocol evpn-bgp L2_VPN_EVPN",
                    self._comm_ok_enable_mode)
                tmp_comm_list.append(comm)
                comm = ("exit", self._comm_ok_enable_mode)
                tmp_comm_list.append(comm)
        self.common_util_log.logging(
            None,
            self.log_level_debug,
            "nvo vxlan id command : \n%s" % (tmp_comm_list,),
            __name__)
        return tmp_comm_list

    @decorater_log
    def _set_command_vni_vlan_mapping(self, cp_info={}, operation=None):
        '''
        Create command list with linkage to VNI,VLAN.
        '''
        tmp_comm_list = []
        for cp_data in cp_info.values():
            if_name = cp_data["IF-NAME"]
            port_mode = cp_data["IF-PORT-MODE"]
            for vlan in cp_data.get("VLAN", {}).values():
                vlan_id = vlan.get("CE-IF-VLAN-ID")
                vni = vlan.get("VNI")
                if port_mode == self._PORT_MODE_ACCESS:
                    tmp_list = self._set_commmand_vni_vlan_mapping_params(
                        if_name, vni, operation=operation)
                if cp_data["IF-PORT-MODE"] == self._PORT_MODE_ACCESS:
                    tmp_list = self._set_commmand_vni_vlan_mapping_params(
                        if_name, vni, operation=operation)
                    tmp_comm_list.extend(tmp_list)
                    break
                else:
                    tmp_list = self._set_commmand_vni_vlan_mapping_params(
                        if_name, vni, vlan_id=vlan_id, operation=operation)
                    tmp_comm_list.extend(tmp_list)
        self.common_util_log.logging(
            None,
            self.log_level_debug,
            "nvo vxlan id command : \n%s" % (tmp_comm_list,),
            __name__)
        return tmp_comm_list

    def _set_commmand_vni_vlan_mapping_params(self,
                                              if_name,
                                              vni,
                                              vlan_id=None,
                                              operation=None):
        '''
        Create command with linkage to VNI,VLAN for each VLANIF.
        '''
        tmp_comm_list = []
        if vlan_id is not None:
            comm_txt = \
                "nvo vxlan access-if port-vlan %s %s" % (if_name, vlan_id)
        else:
            comm_txt = "nvo vxlan access-if port %s" % (if_name,)
        pass
        if operation == self._DELETE:
            comm_txt = "no " + comm_txt
        comm = (comm_txt, self._comm_ok_enable_mode)
        tmp_comm_list.append(comm)
        if operation != self._DELETE:
            comm = ("map vnid %s" % (vni,), self._comm_ok_enable_mode)
            tmp_comm_list.append(comm)
            comm = ("no shutdown", self._comm_ok_enable_mode)
            tmp_comm_list.append(comm)
            comm = ("exit", self._comm_ok_enable_mode)
            tmp_comm_list.append(comm)
        self.common_util_log.logging(
            None,
            self.log_level_debug,
            "nvo vxlan access-port command : \n%s" % (tmp_comm_list,),
            __name__)
        return tmp_comm_list

    @decorater_log
    def _get_l2_cps_from_ec(self,
                            device_mes,
                            db_info,
                            slice_name=None,
                            operation=None):
        '''
        Parameter from EC. (obtain cp data from cp)
        '''
        cp_dicts = {}
        for tmp_cp in device_mes.get("cp", ()):
            tmp, vlan_id = self._get_cp_interface_info_from_ec(
                cp_dicts, tmp_cp)
            if_name = tmp["IF-NAME"]
            if not tmp.get("IF-PORT-MODE"):
                if tmp_cp.get("port-mode"):
                    tmp_port = tmp_cp["port-mode"]
                else:
                    db_cp = self._get_vlan_if_from_db(db_info,
                                                      if_name,
                                                      slice_name,
                                                      vlan_id,
                                                      "cp")
                    tmp_port = db_cp["vlan"]["port_mode"]
                tmp["IF-PORT-MODE"] = tmp_port
            tmp["VLAN"][vlan_id] = self._get_l2_vlan_if_info_from_ec(
                tmp_cp, db_info, slice_name)

        return cp_dicts

    @decorater_log
    def _get_cp_interface_info_from_ec(self, cp_dicts, cp_info):
        '''
        Collect IF information relating to slice from EC message
        (independent unit CPs). (common for L2, L3)
        '''
        if_name = cp_info.get("name")
        vlan_id = cp_info.get("vlan-id")
        if not if_name or vlan_id is None:
            raise ValueError("CP is not enough information")
        if if_name not in cp_dicts:
            tmp = {
                "IF-TYPE": (self._if_type_lag
                            if re.search("^po[0-9]{1,}", if_name)
                            else self._if_type_phy),
                "IF-NAME": if_name,
                "IF-IS-VLAN":  bool(vlan_id),
                "OPERATION": None,
                "VLAN":  {},
            }
            cp_dicts[if_name] = tmp
        else:
            tmp = cp_dicts[if_name]
        return tmp, vlan_id

    @decorater_log
    def _get_l2_vlan_if_info_from_ec(self,
                                     ec_cp,
                                     db_info,
                                     slice_name=None):
        '''
        Set the section relating to VLAN_IF of CP.
        '''
        if_name = ec_cp["name"]
        vlan_id = ec_cp["vlan-id"]
        operation = ec_cp.get("operation")
        if operation == self._DELETE:
            db_cp = self._get_vlan_if_from_db(db_info,
                                              if_name,
                                              slice_name,
                                              vlan_id,
                                              "cp")
            vni = db_cp["vni"]
        else:
            vni = ec_cp["vni"]
        return {
            "OPERATION": ec_cp.get("operation"),
            "CE-IF-VLAN-ID": ec_cp.get("vlan-id"),
            "VNI": vni,
        }

    @staticmethod
    @decorater_log
    def _compound_list_val_dict(dict_1, dict_2):
        '''
        Combine two dictionaries carrying list as the value.
        '''
        tmp = dict_1.keys()
        tmp.extend(dict_2.keys())
        tmp = list(set(tmp))
        ret_dict = {}
        for key in tmp:
            tmp_val = []
            if key in dict_1:
                tmp_val.extend(dict_1[key])
            if key in dict_2:
                tmp_val.extend(dict_2[key])
            tmp_val = list(set(tmp_val))
            ret_dict[key] = tmp_val
        return ret_dict

    @decorater_log
    def _get_vlans_list(self,
                        cp_dict,
                        db_info,
                        slice_name=None,
                        operation=None):
        '''
        Create list for vlans.
        (Compare CP on DB and CP on operation instruction simultaneously.)
        (Make judgment on the necessity of IF deletion and
        possibility for slice to remain inside device.)
        '''
        cos_if_list = {}
        db_cp = {}
        if db_info:
            device_db_data = json.loads(db_info)
            slice_name_list = []
            for tmp_db in device_db_data.get("cp", {}):
                if tmp_db.get("slice_name") in slice_name_list:
                    continue
                slice_name_list.append(tmp_db.get("slice_name"))
            for slice_name in slice_name_list:
                tmp_cp = self._get_db_cp_ifs(device_db_data, slice_name)
                db_cp = self._compound_list_val_dict(db_cp, tmp_cp)
        db_vlan = self._get_db_vlan_counts(db_cp)
        ec_vlan = self._get_ec_vlan_counts(cp_dict.copy())
        if operation == self._DELETE:
            for vlan_id, vlan in ec_vlan.items():
                if vlan["count"] == db_vlan.get(vlan_id, 0):
                    cos_if_list[vlan_id] = ec_vlan.get("VNI")
        else:
            for vlan_id in ec_vlan.keys():
                if vlan_id not in db_vlan:
                    cos_if_list[vlan_id] = ec_vlan[vlan_id].get("VNI")
        return cos_if_list

    @decorater_log
    def _get_cos_if_list(self,
                         cp_dict,
                         db_info,
                         slice_name=None,
                         operation=None):
        '''
        Create list for class-or-service.
        (Compare CP on DB and CP on operation instruction simultaneously.)
        (Make judgment on the necessity of IF deletion
        and possibility for slice to remain inside device.)
        '''
        cos_if_list = []
        db_cp = {}
        if db_info:
            device_db_data = json.loads(db_info)
            slice_name_list = []
            for tmp_db in device_db_data.get("cp", {}):
                if tmp_db.get("slice_name") in slice_name_list:
                    continue
                slice_name_list.append(tmp_db.get("slice_name"))
            for slice_name in slice_name_list:
                tmp_cp = self._get_db_cp_ifs(device_db_data, slice_name)
                db_cp = self._compound_list_val_dict(db_cp, tmp_cp)
        tmp_cp_dict = cp_dict.copy()
        if operation == self._DELETE:
            for if_name, cp_data in tmp_cp_dict.items():
                if len(cp_data["VLAN"]) == len(db_cp.get(if_name, ())):
                    tmp = {"IF-NAME": if_name,
                           "IF-TYPE": cp_data.get("IF-TYPE"),
                           "IF-PORT-MODE": cp_data.get("IF-PORT-MODE")}
                    cos_if_list.append(tmp)
                    cp_dict[if_name]["OPERATION"] = self._DELETE
        else:
            for if_name, cp_data in tmp_cp_dict.items():
                if if_name not in db_cp:
                    tmp = {"IF-NAME": if_name,
                           "IF-TYPE": cp_data.get("IF-TYPE"),
                           "IF-PORT-MODE":
                           tmp_cp_dict[if_name].get("IF-PORT-MODE")}
                    cos_if_list.append(tmp)
        return cos_if_list

    @staticmethod
    @decorater_log
    def _get_db_vlan_counts(db_cp_info):
        db_vlan = {}
        for db_if in db_cp_info.values():
            for vlan in db_if:
                if vlan in db_vlan:
                    db_vlan[vlan] += 1
                else:
                    db_vlan[vlan] = 1
        return db_vlan

    @decorater_log
    def _get_ec_vlan_counts(self, ec_cp_info):
        ec_vlan = {}
        for ec_if in ec_cp_info.values():
            for vlan_id, vlan in ec_if.get("VLAN", {}).items():
                if vlan_id in ec_vlan:
                    ec_vlan[vlan_id]["count"] += 1
                else:
                    ec_vlan[vlan_id] = {"count": 1, "VNI": vlan.get("VNI")}
        return ec_vlan

    @decorater_log
    def _get_vni_list(self,
                      cp_dict,
                      db_info,
                      slice_name=None,
                      operation=None):
        '''
        Create list for vni.
        '''
        vni_list = []
        db_vni = self._get_db_vni_counts(db_info, slice_name)
        ec_vni = self._get_ec_vni_counts(cp_dict.copy())
        if operation == self._DELETE:
            for vni in ec_vni.keys():
                if ec_vni[vni] == db_vni.get(vni, 0):
                    vni_list.append(vni)
        else:
            for vni in ec_vni.keys():
                if vni not in db_vni:
                    vni_list.append(vni)
        return vni_list

    @decorater_log
    def _get_db_vni_counts(self, db_info, slice_name):
        db_vni = {}
        if db_info is not None:
            tmp_json = json.loads(db_info)
            db_cp = tmp_json.get("cp", ())
            for tmp_cp in db_cp:
                if tmp_cp.get("slice_name") != slice_name:
                    continue
                vni = tmp_cp.get("vni")
                if vni in db_vni:
                    db_vni[vni] += 1
                else:
                    db_vni[vni] = 1
        return db_vni

    @decorater_log
    def _get_ec_vni_counts(self, ec_cp_info):
        ec_vni = {}
        for ec_if in ec_cp_info.values():
            for vlan in ec_if.get("VLAN", {}).values():
                vni = vlan.get("VNI")
                if vni in ec_vni:
                    ec_vni[vni] += 1
                else:
                    ec_vni[vni] = 1
        return ec_vni

    @staticmethod
    @decorater_log
    def _get_vlan_if_from_db(db_info,
                             if_name,
                             slice_name,
                             vlan_id,
                             db_name):
        '''
        Obtain VLAN_IF from DB. (cp, vrf, bgp, vrrp)
        '''
        retrun_vlan_if = None
        if db_info is not None:
            tmp_json = json.loads(db_info)
            for vlan_if in tmp_json.get(db_name, ()):
                db_if_name = vlan_if.get("if_name")
                db_slice_name = vlan_if.get("slice_name")
                db_vlan_id = vlan_if.get("vlan", {}).get("vlan_id")
                if (if_name == db_if_name and
                        slice_name == db_slice_name and
                        vlan_id == db_vlan_id):
                    retrun_vlan_if = vlan_if
                    break
        return retrun_vlan_if

    @decorater_log
    def _get_db_cp_ifs(self, db_info, slice_name):
        '''
        Obtain the combination of IF name and vlan from DB.
        '''
        db_cp = db_info.get("cp", ())
        if_dict = {}
        for tmp_cp in db_cp:
            if tmp_cp.get("slice_name") != slice_name:
                continue
            if_name = tmp_cp.get("if_name")
            vlan_id = tmp_cp["vlan"]["vlan_id"]
            if if_name in if_dict:
                if_dict[if_name].append(vlan_id)
            else:
                if_dict[if_name] = [vlan_id]
        return if_dict

    @staticmethod
    @decorater_log
    def _logging_send_command_str(ocnos_command_list=[]):
        '''
        Indicate OcNOS transmit command as letter strings.
        '''
        com_str = "send message for ocnos device:\n"
        for item in ocnos_command_list:
            com_str += "%s\n" % (item[0],)
        return com_str
