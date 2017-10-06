# -*- coding: utf-8 -*-
from codecs import BOM_UTF8
import os
import GlobalModule


class EmConfigManagement(object):


    __FileName = {
    }


    __capability_key = "Capability"

    __ParseListConfSysCommon = [
    ]
    __ParseListConfScnario = [3]


    def read_if_process_conf(self, target_key):
        return self.__read_conf_dict(self.__conf_dict_if_process,
                                     target_key,
                                     self.__conf_if_process,
                                     False)

    def read_scenario_conf(self, target_scenario_key, target_order):
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
        return self.__read_conf_dict(self.__conf_dict_sys_common,
                                     target_key,
                                     self.__conf_sys_common,
                                     False)


    def __init__(self):

        self.__conf_dict_if_process = self.__load_conf(
            self.__conf_dict_if_process, self.__conf_if_process)
        self.__conf_dict_scenario = self.__load_conf(
            self.__conf_dict_scenario, self.__conf_scenario)
        self.__conf_dict_driver = self.__load_conf(
            self.__conf_dict_driver, self.__conf_driver)
        self.__conf_dict_sys_common = self.__load_conf(
            self.__conf_dict_sys_common, self.__conf_sys_common)

    def __read_conf_dict(self, conf_dict, target_key,
                         target_conf, recursive_flg=True):
        if GlobalModule.EM_LOGGER is not None:
                                        self.__FileName.get(target_conf))
        if target_key in conf_dict:
            return True, conf_dict[target_key]
        else:
            if recursive_flg:
                                            self.__FileName.get(target_conf))
                tmp = conf_dict.copy()
                conf_dict = self.__load_conf(conf_dict, target_conf)
                if tmp == conf_dict:
                    GlobalModule.EM_LOGGER.error(
                        self.__FileName.get(target_conf))
                return self.__read_conf_dict(conf_dict, target_key,
                                             target_conf, False)
            else:
                if GlobalModule.EM_LOGGER is not None:
                    GlobalModule.EM_LOGGER.error(
                        self.__FileName.get(target_conf))
                return False, None

    def __load_conf(self, set_dict, target_conf):
        return_dict = set_dict
        config_path = os.environ.get("EM_CONF_PATH")
        result, tmp_list = self.__open_conf_file(config_path +
                                                 self.__FileName[target_conf])
        if result:
            if target_conf == self.__conf_if_process:
                return_dict = self.__make_conf_dict_if_process(tmp_list)
                return_dict = self.__parse_int_conf_dict(
                    return_dict, self.__ParseListConfIFProcess)
            elif target_conf == self.__conf_scenario:
                return_dict = self.__make_conf_dict_tuple_key(
                    tmp_list, 4, 2, self.__ParseListConfScnario)
            elif target_conf == self.__conf_driver:
                return_dict = self.__make_conf_dict_tuple_key(tmp_list, 5, 3)
            elif target_conf == self.__conf_sys_common:
                return_dict = self.__make_conf_dict(tmp_list)
                return_dict = self.__parse_int_conf_dict(
                    return_dict, self.__ParseListConfSysCommon)
        return return_dict

    @staticmethod
    def __parse_int_conf_dict(conf_dict, target_list):
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
        if slice_count - slice_key == 1:
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
        for value in conf_list:
            tmp_key_value = value.split(self.__SPLITSTR)
            if len(tmp_key_value) == 2:
                conf_dict[tmp_key_value[0]] = tmp_key_value[1]
        return conf_dict

    def __make_conf_dict_if_process(self, conf_list):
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
        try:
        except IOError:
            return False, None
        return_list = []
        for value in conf_list:
                tmp_line = value.strip()
                return_list.append(tmp_line)
        return True, return_list

    @staticmethod
    def __strip_space(target_str):
        return_val = target_str
        if target_str is not None and " " in target_str:
            return_val = target_str.replace(" ", "")
        return return_val
