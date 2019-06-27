#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: OfcPluginCGWSH.py
'''
Plugin for analyzing CGWSH message
'''
import re
from lxml import etree
import copy

import GlobalModule
from EmCommonLog import decorater_log, decorater_log_in_out
from OfcPluginMSF import _OfcPluginMSF


plugin_weight = 50


@decorater_log_in_out
def check_used_plugin(ec_message=None, rpc_name=None):
    '''
    It is checked on whether plugin is available or not
    Argument:
        ec_message : EC message (byte)
        rpc_name : RPC name (str)
    Return value:
        availability (True:yes) : boolean
    '''
    is_used_plugin = False
    context = copy.deepcopy(ec_message)
    context = etree.iterparse(context, events=(OfcPluginCGWSH.ev_start,
                                               OfcPluginCGWSH.ev_end))
    for event, element in context:
        if (event == OfcPluginCGWSH.ev_start and
                (element.tag == rpc_name + OfcPluginCGWSH.tag_config or
                 element.tag == rpc_name + OfcPluginCGWSH.tag_filter)):
            conf_elem = element[0]
            tmp_re = re.search("^({.*})", conf_elem.tag)
            name_space = tmp_re.groups()[0] if tmp_re else None
            if (name_space and
                conf_elem.find(name_space + OfcPluginCGWSH.tag_asr_info) or
                    conf_elem.find(name_space + OfcPluginCGWSH.tag_nvr_info)):
                is_used_plugin = True
            break
    return is_used_plugin


@decorater_log_in_out
def get_plugin_ins(*args, **kwargs):
    '''
    Instance of the plugin class  is acquired.
    Argument:
        variable argument
    Return value:
        plugin instance
    '''
    return OfcPluginCGWSH(*args, **kwargs)


class OfcPluginCGWSH(_OfcPluginMSF):
    '''
    Plugin  class for analyzing CGWSH message
    '''
    top_str_asr = "asr"
    top_str_nvr = "nvr"
    tag_asr_info = top_str_asr + "Info"
    tag_nvr_info = top_str_nvr + "Info"

    @decorater_log_in_out
    def __init__(self, rpc_name=None):
        '''
        Constructor
        Argument:
            rpc_name : str
        Return value:
            None
        '''
        super(OfcPluginCGWSH, self).__init__(rpc_name)

    @decorater_log
    def _get_device_type(self, element):
        '''
        Device type with received Netconf is analyzed.
         Argument:
            element:config part
         Return value:
            device type:str
        '''

        dev_type = None
        xml_str = etree.tostring(element)
        match_obj = self._check_fvw_device_type(xml_str)

        if match_obj:
            dev_type = match_obj.groups()[0]
            GlobalModule.EM_LOGGER.debug('device type:%s' % (dev_type,))
        else:
            GlobalModule.EM_LOGGER.debug(
                'Error! device type getting fault')
            raise ValueError('Failed to acquire device type')
        return dev_type

    @decorater_log
    def _check_fvw_device_type(self, xml_str):
        pattern_fvw_with_ope = "<(%sInfo) operation=.*>"
        pattern_fvw = "<(%sInfo)>"
        match_obj = None
        check_list = (
            pattern_fvw_with_ope % (self.top_str_nvr,),
            pattern_fvw % (self.top_str_nvr,),
            pattern_fvw_with_ope % (self.top_str_asr,),
            pattern_fvw % (self.top_str_asr,),
        )
        for item in check_list:
            if match_obj:
                break
            else:
                match_obj = re.search(item, xml_str)
        return match_obj

    @decorater_log
    def _count_device(self, element, device_type):
        '''
        Number of devices withreceived Netconf is calculated.
        Argument:
            element:config type
            device_type:device type
        Return value:
            number of devices:int
        '''
        device_list = []
        device_list.extend(element[0].findall(device_type))
        tmp_dev_type = None
        if self.tag_asr_info in device_type:
            tmp_dev_type = device_type.replace(self.tag_asr_info,
                                               self.tag_nvr_info)
        elif self.tag_nvr_info in device_type:
            tmp_dev_type = device_type.replace(self.tag_nvr_info,
                                               self.tag_asr_info)
        device_list.extend(element[0].findall(tmp_dev_type))
        if len(device_list) > 0:
            device_num = len(device_list)
        else:
            GlobalModule.EM_LOGGER.debug('device count is fault')
            raise ValueError('Failed to counting device')
        return device_num
