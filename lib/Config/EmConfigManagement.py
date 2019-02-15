#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2018 Nippon Telegraph and Telephone Corporation
# Filename: EmConfigManagement.py
'''
Configuration Management Module
'''
from codecs import BOM_UTF8
import os
import GlobalModule


class EmConfigManagement(object):
    '''
    Configuration Management Class
    '''

    __conf_if_process = 'ConfIFProcess'
    __conf_scenario = 'ConfScenario'
    __conf_driver = 'ConfDriver'
    __conf_sys_common = 'ConfSysCommon'
    __conf_rest_if_process = 'ConfRestIFProcess'
    __conf_rest_scenario = 'ConfRestScenario'
    __conf_service = 'ConfService'
    __conf_internal_link_vlan = 'ConfInternalLinkVlan'

    __FileName = {
        'ConfIFProcess': "conf_if_process.conf",
        'ConfScenario': "conf_scenario.conf",
        'ConfDriver': "conf_driver.conf",
        'ConfSysCommon': "conf_sys_common.conf",
        'ConfRestIFProcess': "conf_if_process_rest.conf",
        'ConfRestScenario': "conf_scenario_rest.conf",
        'ConfService': "conf_service.conf",
        'ConfInternalLinkVlan': "conf_internal_link_vlan.conf",
    }

    __SPLITSTR = '='

    __capability_key = "Capability"

    __ParseListConfIFProcess = ['Port_number']
    __ParseListConfSysCommon = [
        'DB_access_port',
        'Timer_confirmed-commit',
        'Timer_confirmed-commit_em_offset',
        'Timer_netconf_protocol',
        'Timer_signal_rcv_wait',
        'Timer_thread_stop_watch',
        'Timer_transaction_stop_watch',
        'Timer_transaction_db_watch',
        'Timer_connection_retry',
        'Connection_retry_num',
        'Rest_request_average',
    ]
    __ParseListConfRestProcess = ['Rest_port_number']
    __ParseListConfScnario = [3, 4, 5]

    __ParseListConfService = [2]

    def read_if_process_conf(self, target_key):
        '''
         Acquisition of IF Processing Part Definition
            Gets called from MAIN method at the start-up time
        Argument
            target_key : Type Key
        Return value
            Method Results : True or False
            Type Value : str
        '''
        return self.__read_conf_dict(self.__conf_dict_if_process,
                                     target_key,
                                     self.__conf_if_process,
                                     False)

    def read_scenario_conf(self, target_scenario_key, target_order):
        '''
        Scenario Definition Acquisition
            Gets called from Order Flow Control Class at the time of order request
            (Not return Service/Order Transaction Management No.)
        Argument
            target_scenario_key : Scenario Key
            target_order : Order Type
        Return value
            Method Results : True or False
            Startup IF : str
        '''
        target_key = (self.__strip_space(target_scenario_key),
                      self.__strip_space(target_order))
        result, tmp_value = self.__read_conf_dict(self.__conf_dict_scenario,
                                                  target_key,
                                                  self.__conf_scenario)
        if result:
            return result, tmp_value[0], tmp_value[1]
        else:
            return result, None, None

    def read_driver_conf(self,
                         target_platform,
                         target_os,
                         target_firmversion,
                         get_qos=False):
        '''
        Driver Definition Acquisition
            Gets called from Driver Common Part at the time of controlling start of Driver Common Part
        Argument
            target_platform : Platform Name
            target_os : OS Name
            target_firmversion : Firmware Version
        Return value
            Method Results : True or False
            Individual Driver Name : str
            Individual Driver Class Name : str
            File Address for QoS Configuration : str
        '''
        target_key = (self.__strip_space(target_platform),
                      self.__strip_space(target_os),
                      self.__strip_space(target_firmversion))
        result, tmp_value = self.__read_conf_dict(self.__conf_dict_driver,
                                                  target_key,
                                                  self.__conf_driver)
        if not result:
            tmp_value = (None, None, None)
        if get_qos:
            return result, tmp_value[0], tmp_value[1], tmp_value[2]
        else:
            return result, tmp_value[0], tmp_value[1]

    def read_sys_common_conf(self, target_key):
        '''
        Acquisition of Definition across the System
            Gets called from each initialization method at the time of initializing of DB control or log class from each initialization method
        Argument
            target_key : Type Key
        Return value
            Method Results : True or False
            Type Value : str
        '''
        return self.__read_conf_dict(self.__conf_dict_sys_common,
                                     target_key,
                                     self.__conf_sys_common,
                                     False)

    def read_service_type_scenario_conf(self):
        '''
        Obtains Scenario List from Scenario Configuration
        Return value
            Scenario List : dict
        '''
        return self.__conf_dict_scenario

    def read_if_process_rest_conf(self, target_key):
        '''
        Acquisition of REST IF Processing Part Definition
            Gets called from MAIN method at the start-up time
        Argument
            target_key : Type Key
        Return value
            Method Results : True or False
            Type Value : str
        '''
        return self.__read_conf_dict(self.__conf_dict_rest_if_process,
                                     target_key,
                                     self.__conf_rest_if_process,
                                     False)

    def read_scenario_rest_conf(self, target_key):
        '''
        RESTScenario Definition Acquisition
            Gets called from REST Server Module at the time of execution of RESTAPI request
        Argument
            target_key : Scenario Key(set URL)
        Return value
            Method Results : True or False
            Startup IF : str
        '''
        return self.__read_conf_dict(self.__conf_dict_rest_scenario,
                                     target_key,
                                     self.__conf_rest_scenario)

    def read_service_conf(self, target_service_key):
        '''
        Service Definition Acquisition
            Gets called from Order Flow Control Class at the time of order request
        Argument
            target_key : ServiceKey
        Return value
            Method Results : True or False
            Service Definition : tuple
        '''
        target_key = (self.__strip_space(target_service_key),)
        return self.__read_conf_dict(self.__conf_dict_service,
                                     target_key,
                                     self.__conf_service)

    def read_service_conf_recover(self):
        '''
        Gets Utility Class List for Recovery of the Service to be recovered from Service Definition Configuration
        Return value
            Utility Class List for Recovery Expansion: dict
            Utility Class List for Service Resetting : dict
        '''
        self.recover_node_dict = {}
        self.recover_service_dict = {}
        for key, value in self.__conf_dict_service.items():
            if value[2] == GlobalModule.SERVICE_RECOVER_NODE:
                self.recover_node_dict[value[1]] = key[0], value[0]
            if value[2] == GlobalModule.SERVICE_RECOVER_SERVICE:
                self.recover_service_dict[value[1]] = key[0], value[0]

        return self.recover_node_dict, self.recover_service_dict

    def read_service_conf_list(self):
        '''
        Gets Service List from Service Definition Configuration
        Return Value
            Service List : dict
        '''
        return self.__conf_dict_service

    def read_conf_internal_link_vlan_os_tuple(self):
        '''
        Gets List of OS which requires Internal Link VLAN from Internal Link VLAN Configuration
        Return value
            List of OS which requires Internal Link VLAN : tuple
        '''
        return self.__conf_tuple_internl_link_vlan_os

    def __init__(self, conf_dir_path=None):
        '''
        Constructor
        '''
        self._conf_dir_path = conf_dir_path

        self.__conf_dict_if_process = {}
        self.__conf_dict_scenario = {}
        self.__conf_dict_driver = {}
        self.__conf_dict_sys_common = {}
        self.__conf_dict_rest_if_process = {}
        self.__conf_dict_rest_scenario = {}
        self.__conf_dict_service = {}
        self.__conf_tuple_internl_link_vlan_os = ()

        self.__conf_dict_if_process = self.__load_conf(
            self.__conf_dict_if_process, self.__conf_if_process)
        self.__conf_dict_scenario = self.__load_conf(
            self.__conf_dict_scenario, self.__conf_scenario)
        self.__conf_dict_driver = self.__load_conf(
            self.__conf_dict_driver, self.__conf_driver)
        self.__conf_dict_sys_common = self.__load_conf(
            self.__conf_dict_sys_common, self.__conf_sys_common)
        self.__conf_dict_rest_if_process = self.__load_conf(
            self.__conf_dict_rest_if_process, self.__conf_rest_if_process)
        self.__conf_dict_rest_scenario = self.__load_conf(
            self.__conf_dict_rest_scenario, self.__conf_rest_scenario)
        self.__conf_dict_service = self.__load_conf(
            self.__conf_dict_service, self.__conf_service)
        tmp_dict = {}
        tmp_dict = self.__load_conf(tmp_dict, self.__conf_internal_link_vlan)
        self.__conf_tuple_internl_link_vlan_os = tuple(tmp_dict.values())

    def __read_conf_dict(self, conf_dict, target_key,
                         target_conf, recursive_flg=True):
        '''
        Definition Acquisition
        (Performs reloading of Definition at the time of acquisition failure)
            Gets called from each Definition Acquisition Method which is an external IF
        Argument:
            conf_dict : Definition Dictionary
            target_key : Key to be acquired
            target_conf : Definition Name
            recursive_flg : Reloading Execution Flag (For recursive processing)
        Return value:
            Acquisition Results : Boolean
            Definition Value ; str or int or taple (Changes based on values which has been stored)
        '''
        if GlobalModule.EM_LOGGER is not None:
            GlobalModule.EM_LOGGER.info('101005 Load conf start (%s)' %
                                        self.__FileName.get(target_conf))
        if target_key in conf_dict:
            return True, conf_dict[target_key]
        else:
            if recursive_flg:
                GlobalModule.EM_LOGGER.info('101006 ReLoad conf start (%s)' %
                                            self.__FileName.get(target_conf))
                tmp = conf_dict.copy()
                conf_dict = self.__load_conf(conf_dict, target_conf)
                if tmp == conf_dict:
                    GlobalModule.EM_LOGGER.error(
                        '301008 ReLoad conf Error (%s)' %
                        self.__FileName.get(target_conf))
                return self.__read_conf_dict(conf_dict, target_key,
                                             target_conf, False)
            else:
                if GlobalModule.EM_LOGGER is not None:
                    GlobalModule.EM_LOGGER.error(
                        '301007 Load conf Error (%s)' %
                        self.__FileName.get(target_conf))
                return False, None

    def __load_conf(self, set_dict, target_conf):
        '''
       Reads Conf File to acquire the Target Dictionary
        Returns the Dictionary to be updated if acqusition of Dictionary has failed, and will not be updated.
        Argument:
            set_dict : Dictionary to be updated
            Filepath : Absolute path of the Definition File to be read
        Return value:
            Definition Dictionary which has been updated: dict
        '''
        return_dict = set_dict
        conf_file_path = os.path.join(self._conf_dir_path,
                                      self.__FileName[target_conf])
        result, tmp_list = self.__open_conf_file(conf_file_path)
        if result:
            if target_conf == self.__conf_if_process:
                return_dict = self.__make_conf_dict_if_process(tmp_list)
                return_dict = self.__parse_int_conf_dict(
                    return_dict, self.__ParseListConfIFProcess)
                self.__conf_dict_if_process = return_dict
            elif target_conf == self.__conf_scenario:
                return_dict = self.__make_conf_dict_tuple_key(
                    tmp_list, 6, 2, self.__ParseListConfScnario)
                self.__conf_dict_scenario = return_dict
            elif target_conf == self.__conf_driver:
                return_dict = self.__make_conf_dict_tuple_key(tmp_list, 6, 3)
                self.__conf_dict_driver = return_dict
            elif target_conf == self.__conf_sys_common:
                return_dict = self.__make_conf_dict(tmp_list)
                return_dict = self.__parse_int_conf_dict(
                    return_dict, self.__ParseListConfSysCommon)
                self.__conf_dict_sys_common = return_dict
            elif target_conf == self.__conf_rest_if_process:
                return_dict = self.__make_conf_dict(tmp_list)
                return_dict = self.__parse_int_conf_dict(
                    return_dict, self.__ParseListConfRestProcess)
                self.__conf_dict_rest_if_process = return_dict
            elif target_conf == self.__conf_rest_scenario:
                return_dict = self.__make_conf_dict_tuple_key(
                    tmp_list, 2, 1)
                tmp = {}
                for key in return_dict.copy().keys():
                    tmp[key[0]] = return_dict[key]
                return_dict = tmp
                self.__conf_dict_rest_scenario = return_dict
            elif target_conf == self.__conf_service:
                return_dict = self.__make_conf_dict_tuple_key(
                    tmp_list, 4, 1, self.__ParseListConfService)
                self.__conf_dict_service = return_dict
            elif target_conf == self.__conf_internal_link_vlan:
                return_dict = self.__make_conf_dict(tmp_list)
        return return_dict

    @staticmethod
    def __parse_int_conf_dict(conf_dict, target_list):
        '''
        Fetches Key of conf_dict from target_list,
        and convers all the Values into the style of int
        Argument:
            conf_dict : Definition Dictionary
            target_list : Key Storage List to be converted
        Return value:
            Definition Dictionary which has been updated : dict
        '''
        return_dict = conf_dict.copy()
        for key in target_list:
            if key in conf_dict:
                try:
                    return_dict[key] = int(conf_dict[key])
                except ValueError:
                    pass
        return return_dict

    def __make_conf_dict_tuple_key(self, conf_list, slice_count,
                                   slice_key, parse_list=None):
        '''
        Stores the Definition to be read from file into Definition Dictionary that has tuple as a key
            Gets called after reading Scenario Definition and Driver Definition from file
        Argument:
            conf_list : List of string acquired from file
            slice_count : No. of items of one Scenario (Driver )group
            slice_key : No. of Keys of one Scenario (Driver )group
            parse_list : Index List of items to be convered to numerical type (Set if required)
        Return value:
            Definition Dictionary : Dict
        '''
        conf_dict = {}
        tmp_value_list = []
        tuple_value_flg = True
        if slice_count - slice_key == 1:
            tuple_value_flg = False
        index = 0
        count = 0
        for item in conf_list:
            tmp = item.split(self.__SPLITSTR)[1]
            if parse_list is not None and tmp:
                if count % slice_count in parse_list:
                    tmp = int(tmp)
            tmp_value_list.append(tmp)
            count += 1
        max_index = len(tmp_value_list) - slice_count + 1
        while index < max_index:
            tmp_key = tuple(tmp_value_list[index:index + slice_key])
            if tuple_value_flg:
                tmp_value = tuple(
                    tmp_value_list[index + slice_key:index + slice_count])
            else:
                tmp_value = tmp_value_list[index + slice_key]
            conf_dict[tmp_key] = tmp_value
            index += slice_count
        return conf_dict

    def __make_conf_dict(self, conf_list):
        '''
        Stores the Definition which has been read from file, into Dictionary
            Get called after reading the Common Definition across the system from file
        Argument:
            conf_list : List of string acquired from file
        Return value:
            Definition Dictionary : Dict
        '''
        conf_dict = {}
        for value in conf_list:
            tmp_key_value = value.split(self.__SPLITSTR)
            if len(tmp_key_value) == 2:
                conf_dict[tmp_key_value[0]] = tmp_key_value[1]
        return conf_dict

    def __make_conf_dict_if_process(self, conf_list):
        '''
        Creation of Definition Dictionary for IFProcess
            Gets called after reading IF Processing Part Definition from file
        Argument:
            conf_list : List of string acquired from file
        Return value:
            Definition Dictionary : Dict
        '''
        conf_dict = {}
        capability_list = []
        index = 0
        while index < len(conf_list):
            tmp_key_value = conf_list[index].split(self.__SPLITSTR)
            if len(tmp_key_value) == 2:
                if tmp_key_value[0].find(self.__capability_key) == 0:
                    capability_list.append(tmp_key_value[1])
                else:
                    conf_dict[tmp_key_value[0]] = tmp_key_value[1]
            index += 1
        conf_dict[self.__capability_key] = capability_list
        return conf_dict

    def __open_conf_file(self, file_path):
        '''
        Reads Conf File to return each line as a KeyValue Dictionary
            Gets called at the beginning of each Definition Acquisition Processing
        Argument:
            file_path : File path of the Definition File to be read
        Return value:
            Processing Results : Boolean
            Reading Results (Each line to be listed as string) : List
        '''
        try:
            open_file = open(file_path, 'r')
            conf_list = open_file.readlines()
            open_file.close()
        except IOError:
            return False, None
        return_list = []
        for value in conf_list:
            if not(value.startswith('#')) and self.__SPLITSTR in value:
                tmp_line = value.strip()
                tmp_line = tmp_line.replace(BOM_UTF8, '')
                return_list.append(tmp_line)
        return True, return_list

    @staticmethod
    def __strip_space(target_str):
        return_val = target_str
        if target_str is not None and " " in target_str:
            return_val = target_str.replace(" ", "")
        return return_val

    def get_qos_conf(self, platform_name, driver_os, firmware_ver):
        '''
        Gets Configuration File Address for QoS to read QoS Configuration Information
        Parameter :
            platform_name : Platform Name
            driver_os : Driver OS
            firmware_ver : Firmware Version
        Return value :
            QoS Config  : dict
        '''
        driver_conf = self.read_driver_conf(platform_name,
                                            driver_os,
                                            firmware_ver,
                                            True)

        qos_conf_address = os.path.join(GlobalModule.EM_CONF_PATH,
                                        driver_conf[3])
        return self._load_qos_config(qos_conf_address)

    def _load_qos_config(self, config_path):
        '''
        Reads QoS Configuration Information from QoS Configuration File for Qos
        Parameter :
            file_address : Configuration File Address
        Return value :
            Remark Menu Configuration  : dict conf_qos_remark
            Egress Queue Menu Config  : dict conf_qos_egress
        '''
        splitter_conf = '='
        try:
            with open(config_path, 'r') as open_file:
                conf_list = open_file.readlines()
        except IOError:
            raise

        tmp_list = []
        for value in conf_list:
            if not(value.startswith('#')) and splitter_conf in value:
                tmp_line = value.strip()
                tmp_line = tmp_line.replace(BOM_UTF8, '')
                tmp_list.append(tmp_line)

        conf_qos_remark = {}
        conf_qos_egress = {}
        index = 0
        tmp_value_list = []
        for item in tmp_list:
            tmp_k = item.split(splitter_conf)[0]
            tmp_v = item.split(splitter_conf)[1]
            tmp = (tmp_k, tmp_v)
            tmp_value_list.append(tmp)
        max_index = len(tmp_value_list) - 1
        while index < max_index:
            tmp_key = tmp_value_list[index][1]
            tmp_value_ipv4 = tmp_value_list[index + 1][1]
            tmp_value_ipv6 = tmp_value_list[index + 2][1]
            if tmp_value_list[index][0].startswith("Remark"):
                conf_qos_remark[tmp_key] = {
                    "IPV4": tmp_value_ipv4, "IPV6": tmp_value_ipv6}
            else:
                conf_qos_egress[tmp_key] = {
                    "IPV4": tmp_value_ipv4, "IPV6": tmp_value_ipv6}
            index += 3

        return conf_qos_remark, conf_qos_egress
