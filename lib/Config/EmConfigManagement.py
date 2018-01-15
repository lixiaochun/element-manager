#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2017 Nippon Telegraph and Telephone Corporation
# Filename: EmConfigManagement.py
'''
Config management module.
'''
from codecs import BOM_UTF8
import os
import GlobalModule


class EmConfigManagement(object):
    '''
    Config management class.
    '''

    __conf_if_process = 'ConfIFProcess'
    __conf_scenario = 'ConfScenario'
    __conf_driver = 'ConfDriver'
    __conf_sys_common = 'ConfSysCommon'
    __conf_rest_if_process = 'ConfRestIFProcess'
    __conf_rest_scenario = 'ConfRestScenario'

    __FileName = {
        'ConfIFProcess': "conf_if_process.conf",
        'ConfScenario': "conf_scenario.conf",
        'ConfDriver': "conf_driver.conf",
        'ConfSysCommon': "conf_sys_common.conf",
        'ConfRestIFProcess': "conf_if_process_rest.conf",
        'ConfRestScenario': "conf_scenario_rest.conf",
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


    def read_if_process_conf(self, target_key):
        '''
        IF processing section definition acquisition.
            Called out through the MAIN method when getting launched. 
        Argument.
            target_key : Type key
        Return value.
            Method results : True or False
            Type value : str
        '''
        return self.__read_conf_dict(self.__conf_dict_if_process,
                                     target_key,
                                     self.__conf_if_process,
                                     False)

    def read_scenario_conf(self, target_scenario_key, target_order):
        '''
        Scenario definition acquisition.
            Called out based on the order flow control class when order is requested.
            (Service/order transaction management number should not be returned.)
        Argument.
            target_scenario_key : Scenario key
            target_order : Order type
        Return value.
            Method results : True or False
            Launch IF : str
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

    def read_driver_conf(self, target_platform, target_os, target_firmversion):
        '''
        Driver definition acquisition.
            Called out through the common section on driver when controlling the start of the common section on driver.
        Argument.
            target_platform : Platform name
            target_os : OS name
            target_firmversion : firm version
        Return value.
            Method results : True or False
            Individual driver name : str
            Individual driver class name : str
        '''
        target_key = (self.__strip_space(target_platform),
                      self.__strip_space(target_os),
                      self.__strip_space(target_firmversion))
        result, tmp_value = self.__read_conf_dict(self.__conf_dict_driver,
                                                  target_key,
                                                  self.__conf_driver)
        if result:
            return result, tmp_value[0], tmp_value[1]
        else:
            return result, None, None

    def read_sys_common_conf(self, target_key):
        '''
        System common definition acquisition.
            Called out by initialization method when initializing DB control and log class.
        Argument.
            target_key : Type key
        Return value.
            Method results : True or False
            Type value : str
        '''
        return self.__read_conf_dict(self.__conf_dict_sys_common,
                                     target_key,
                                     self.__conf_sys_common,
                                     False)

    def read_service_type_scenario_conf(self):
        '''
        Acquire the scenario list from the scenario cinfig. 
        Return value.
            Scenario list : dict
        '''
        return self.__conf_dict_scenario

    def read_if_process_rest_conf(self, target_key):
        '''
        REST IF processing section definition acquisition.
            Called out through the MAIN method when getting launched. 
        Argument.
            target_key : Type key
        Return value.
            Method results : True or False
            Type value : str
        '''
        return self.__read_conf_dict(self.__conf_dict_rest_if_process,
                                     target_key,
                                     self.__conf_rest_if_process,
                                     False)

    def read_scenario_rest_conf(self, target_key):
        '''
        Acquire the REST scenario definition.
            Called out through the REST server module when executing RESTAPI request.
        Argument.
            target_key : Scenario key (set URL)
        Return value.
            Method results : True or False
            Launch IF : str
        '''
        return self.__read_conf_dict(self.__conf_dict_rest_scenario,
                                     target_key,
                                     self.__conf_rest_scenario)


    def __init__(self, conf_dir_path=None):
        '''
        Constructor.
        '''
        self._conf_dir_path = conf_dir_path

        self.__conf_dict_if_process = {}   
        self.__conf_dict_scenario = {}    
        self.__conf_dict_driver = {}      
        self.__conf_dict_sys_common = {}   
        self.__conf_dict_rest_if_process = {}   
        self.__conf_dict_rest_scenario = {}    

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

    def __read_conf_dict(self, conf_dict, target_key,
                         target_conf, recursive_flg=True):
        '''
        Definition acquisition.
        (The definition should be fed in again when definition acquisition has been failed. 
            Called out through definition acquisition method which is external IF.
        Argument:
            conf_dict : Definition dictionary
            target_key : Key as the target for acquisition
            target_conf : Definition name
            recursive_flg : Flag to execute re-reading (for recursive processing) 
        Return value:
            Acquisition results : Boolean
            Defined value ; str or int or taple (Varies depending on the stored value)
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
        Take in the Conf file and acquire the target dictionary. 
        The dictionary targetted for updating should be returned and updating does not proceed when dictionary acquisition fails. 
        Argument:
            set_dict : The dictionary targetted for updating
            Filepath : Absolute path of the definition file targetted for taking-in.
        Return value:
            Updated definition dictionary : dict
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
                return_dict = self.__make_conf_dict_tuple_key(tmp_list, 5, 3)
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
        return return_dict

    @staticmethod
    def __parse_int_conf_dict(conf_dict, target_list):
        '''
        Take conf_dict keys out of the target_list, convert all their values into int format.
        Argument:
            conf_dict : Definition dictionary
            target_list : Storage list for keys targetted for conversion 
        Return value:
            Updated definition dictionary : dict
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
        Store the definition fed in from the file to the definition dictionary 
        which has tuple as the key.
            Called out after taking the scenario definition and driver definition in from the file.
        Argument:
            conf_list : Letter strings list obtained from the file 
            slice_count : Number of items in the scenario (driver) 1 group
            slice_key : Number of the keys in the scenario (driver) 1 group
            parse_list : Index list of the items to be converted into numeric format. (should be set if necessary.)
        Return value:
            Definition dictionary : Dict
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
            if parse_list is not None:
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
        Store the definition taken from the file to the dictionary.
            Called out after taking the common definition for the system in from the file.
        Argument:
            conf_list : Letter string list obtained from the file. 
        Return value:
            Definition dictionary : Dict
        '''
        conf_dict = {}  
        for value in conf_list:
            tmp_key_value = value.split(self.__SPLITSTR)
            if len(tmp_key_value) == 2:
                conf_dict[tmp_key_value[0]] = tmp_key_value[1]
        return conf_dict

    def __make_conf_dict_if_process(self, conf_list):
        '''
        Create the definition dictionary for the IFProcess.
            Called out after taking the IF processing section definition in from the file.
        Argument:
            conf_list : Letter string list obtained from the file.
        Return value:
            Definition dictionary : Dict
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
        Read the Conf file, return each line as the KeyValue dictionary.
            Called out at the beginning of definition acquisition processing for each.
        Argument:
            file_path : File path for the definition file to be read-in 
        Return value:
            Processing results : Boolean
            Result of reading-in (make it into a list with each line treated as letter strings) : List
        '''
        try:
            open_file = open(file_path, 'r')     
            conf_list = open_file.readlines()    
            open_file.close()                   
        except IOError:
            return False, None
        return_list = []
        for value in conf_list:
            if not(value.startswith('
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
