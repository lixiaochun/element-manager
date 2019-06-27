#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: OfcPluginMSF.py
'''
Plugin class for analyzing MSF normal service (for base/private class)
'''

import copy
from lxml import etree
import re

import GlobalModule
from EmCommonLog import decorater_log, decorater_log_in_out


plugin_weight = 1


@decorater_log_in_out
def check_used_plugin(ec_message=None, rpc_name=None):
    '''
    Analysis plugin of availability check
    Argument:
        ec_message : EC message (byte)
        rpc_name : RPC name (str)
    Return value:
        availability(True:available) : boolean
    '''
    return True


@decorater_log_in_out
def get_plugin_ins(*args, **kwargs):
    '''
    Instance of analysis plugin class is acquired.
    Argument:
        variable argument
    Return value:
        plugin interface
    '''
    return OfcPluginMSF(*args, **kwargs)


class _OfcPluginMSF(object):
    '''
    Plugin class for analyzing MSF normal service (for base/private class)
    '''

    ev_start = "start"
    ev_end = "end"
    tag_config = "config"
    tag_filter = "filter"
    attr_operation = "operation"
    ope_merge = "merge"
    ope_delete = "delete"
    ope_replace = "replace"
    ope_get = "get"

    def __init__(self, rpc_name=None):
        self.rpc_name = rpc_name

    @decorater_log_in_out
    def analysis_scenario_from_recv_message(self, ec_message):
        '''
        Scenario information in Received Netconf is acquired.
        Argument:
            ec_message:EC message byte
        Return value:
            service type:str
            order type:order_kind
            number of :str
            device type:str
        '''

        service_kind = None
        device_type = None
        device_num = None

        context = copy.deepcopy(ec_message)
        context = etree.iterparse(context, events=(self.ev_start, self.ev_end))

        for event, element in context:
            if (event == self.ev_start and
                    (element.tag == self.rpc_name + self.tag_config or
                     element.tag == self.rpc_name + self.tag_filter)):
                config_ptn = element.tag

                service_kind, device_type, sys_ns = \
                    self._analysis_service(element)

                device_num = self._count_device(element, sys_ns + device_type)

                order_kind = self._analysis_netconf_operation(
                    context, service_kind, config_ptn, self.rpc_name, sys_ns)
                break

        GlobalModule.EM_LOGGER.debug(
            'analysis result Service:%s Order:%s Device_Num:%s Device_type:%s',
            service_kind, order_kind, device_num, device_type)

        return service_kind, order_kind, device_num, device_type

    @decorater_log
    def _analysis_service(self, element):
        '''
        Service type in received Netconf is analyzed.
        Argument:
            element:config part
        Return value:
            service type:str
            device type:str
            service name space:str
        '''
        svs_dev_type = self._get_device_type(element)

        for service in GlobalModule.EM_SERVICE_LIST:
            sys_ns = "{%s}" % (GlobalModule.EM_NAME_SPACES[service],)
            if element[0].tag == sys_ns + service:
                return service, svs_dev_type, sys_ns

        GlobalModule.EM_LOGGER.debug('Service Kind ERROR')
        raise ValueError('Failed to acquire service')

    @staticmethod
    @decorater_log
    def _get_device_type(element):
        '''
        Device type in received Netconf is analyzed.
        Argument:
            element:config part
        Return value:
            device type:str
        '''

        dev_type = ""
        pattern_with_ope = "<(.*device.*) operation=.*>"
        pattern = "<(.*device.*)>"
        xml_str = etree.tostring(element)
        match_obj = re.search(pattern_with_ope, xml_str)
        if not match_obj:
            match_obj = re.search(pattern, xml_str)
        if match_obj:
            dev_type = match_obj.groups()[0]
            GlobalModule.EM_LOGGER.debug('device type:%s' % (dev_type,))
        else:
            GlobalModule.EM_LOGGER.debug(
                'Error! device type getting fault')
            raise ValueError('Failed to acquire device type')
        return dev_type

    @staticmethod
    @decorater_log
    def _count_device(element, device_type):
        '''
        Number of devices in received Netconf is calculated.
        Argument:
            element:config part
            device_type:device type
        Return value:
            number of devices:int
        '''
        device_list = element[0].findall(device_type)

        if len(device_list) > 0:
            device_num = len(device_list)
        else:
            GlobalModule.EM_LOGGER.debug('device count is fault')
            raise ValueError('Failed to counting device')
        return device_num

    @decorater_log
    def _analysis_netconf_operation(self,
                                    context,
                                    service_kind,
                                    config_ptn,
                                    rpc_name,
                                    svc_ns):
        '''
        Operation type in received Netconf is analyzed.
        Argument:
            context:config part
            service_kind:service type
            config_ptn:config pattern
            rpc_name:RPC name space
            svc_ns:service name space
        Return value:
            order type:str
        '''
        rpc_conf = rpc_name + self.tag_config

        for event, element in context:
            if (event == self.ev_start and
                    element.items() == [(self.attr_operation,
                                         self.ope_replace)]):
                order_kind = self.ope_replace
                break
            if (event == self.ev_start and
                    element.items() == [(self.attr_operation,
                                         self.ope_delete)]):
                order_kind = self.ope_delete
                break
            if event == self.ev_end and element.tag == svc_ns + service_kind:
                order_kind = (
                    self.ope_merge if config_ptn == rpc_conf else self.ope_get)
                break
        return order_kind


class OfcPluginMSF(_OfcPluginMSF):
    '''
    plugin class for analyzing MSF normal service.
    (for generating instance)
    '''
