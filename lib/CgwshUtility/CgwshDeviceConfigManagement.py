#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: CgwshDeviceConfigManagement.py
'''
Utility for CGW-SH Device (to manage configuration)
'''
import traceback
import os
from lxml import etree
import GlobalModule
from EmCommonLog import decorater_log


class CgwshDeviceConfigManagement(object):
    '''
    Utility for CGW-SH Device (to manage configuration)
    '''

    @decorater_log
    def __init__(self, conf_file_path):
        self._dev_config = None
        self.conf_file_path = conf_file_path
        self._file_name = os.path.basename(self.conf_file_path)
        self._host_name = None
        self._delete_flag = False
        self._address = None
        self._platform_name = None
        self._os_name = None
        self._firm_version = None
        self._username = None
        self._password = None
        self._administrator_password = None

    @decorater_log
    def get_config(self):
        '''
        Getting device information.
        The information is returned as dict which each information is saved.
        '''
        tmp_dict = {
            "host-name": self._host_name,
            "delete-flag": self._delete_flag,
            "address": self._address,
            "platform-name": self._platform_name,
            "os-name": self._os_name,
            "firm-version": self._firm_version,
            "username": self._username,
            "password": self._password,
        }
        if self._administrator_password:
            tmp_dict["administrator-password"] = self._administrator_password
        return tmp_dict

    @decorater_log
    def load_config(self):
        '''
        Reading the contents from device information file.
        '''
        GlobalModule.EM_LOGGER.info(
            '112003 Load conf start ("%s")' % (self._file_name,))
        try:
            get_config = self._open_xml_file(self.conf_file_path)
            self._dev_config = self._make_conf_dict_from_xml(get_config)
            self._host_name = self._dev_config.get("host-name")
            self._delete_flag = self._dev_config.get("delete-flag")
            self._address = self._dev_config.get("address")
            self._platform_name = self._dev_config.get("platform-name")
            self._os_name = self._dev_config.get("os-name")
            self._firm_version = self._dev_config.get("firm-version")
            self._username = self._dev_config.get("username")
            self._password = self._dev_config.get("password")
            self._administrator_password = \
                self._dev_config.get("administrator-password")
        except Exception as exc_info:
            GlobalModule.EM_LOGGER.error(
                '312004 Load conf Error ("%s")' % (self._file_name,))
            GlobalModule.EM_LOGGER.debug("ERROR:%s" % (exc_info,))
            GlobalModule.EM_LOGGER.debug(
                "Trace Back:%s" % (traceback.format_exc(),))
            return False
        GlobalModule.EM_LOGGER.debug(
            "Load config(%s) = %s" % (self._file_name, self._dev_config))
        return True

    @decorater_log
    def _open_xml_file(self, file_path):
        '''
        Conf is read and returned as XML Element
        paramter:
            file_path : File patf for read-definition file
        returns:
            contents of read file : etree.Element object
        '''
        conf_xml = etree.parse(file_path)
        GlobalModule.EM_LOGGER.info(
            'Load file_data:\n%s' % (etree.tostring(conf_xml),))
        return conf_xml

    @decorater_log
    def _make_conf_dict_from_xml(self, xml_obj):
        '''
        Information from file is saved in the dictionay.
            After device inforamtation definition is read from the file 
            the data is called(XML).
        Argument:
            conf_list : XML object aquired from the file
        Return value:
            definition dictionary : Dict
        '''
        conf_dict = {}  
        tmp_param_list = ("host-name",
                          "address",
                          "platform-name",
                          "os-name",
                          "firm-version",
                          "username",
                          "password",
                          )
        dev_node = xml_obj.find("device")
        if dev_node is None:
            raise ValueError("device node is not found")
        for key in tmp_param_list:
            tmp_node = dev_node.find(key)
            if tmp_node is None:
                raise ValueError("device node is not found")
            conf_dict[key] = tmp_node.text
        tmp_node = dev_node.find("delete-flag")
        if tmp_node is not None:
            conf_dict["delete-flag"] = True
        else:
            conf_dict["delete-flag"] = False
        tmp_node = dev_node.find("administrator-password")
        if tmp_node is not None:
            conf_dict["administrator-password"] = tmp_node.text
        return conf_dict
