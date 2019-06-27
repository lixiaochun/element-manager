#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmCgwshCustomerUniRouteDelete.py

'''
Individual scenario for deleting individual UNI static route
'''
import json
from lxml import etree
import GlobalModule
from EmCommonLog import decorater_log
from EmCgwshServiceFlavor import EmCgwshServiceFlavor
from EmCgwshServiceBase import EmCgwshServiceBase


class EmCgwshCustomerUniRouteDelete(EmCgwshServiceFlavor, EmCgwshServiceBase):
    '''
    Class for deleting individual UNI static route in  Cgwsh service
    '''

    @decorater_log
    def __init__(self):
        '''
        Costructor
        '''
        super(EmCgwshCustomerUniRouteDelete, self).__init__()
        super(EmCgwshServiceFlavor, self).__init__()

        self.service = GlobalModule.SERVICE_CGWSH_CUSTOMER_UNI_ROUTE
        self.order_type = GlobalModule.ORDER_DELETE

        self._xml_ns = "{%s}" % GlobalModule.EM_NAME_SPACES[self.service]

        self._scenario_name = "CgwshCustomerUniRouteDelete"

    @decorater_log
    def _creating_json(self, device_message):
        '''
        EC Message(XML) devided into each device is converted to JSON.
        Argument:
            device_message: message for each device
        Return value:
            device_json_message: JSON message
        '''
        xml_elm = etree.fromstring(device_message)

        GlobalModule.EM_LOGGER.debug(
            "device_message = %s", etree.tostring(xml_elm, pretty_print=True))

        device_json_message = self._get_nvr_static_info(xml_elm)

        GlobalModule.EM_LOGGER.debug(
            "device__json_message = %s", device_json_message)

        return json.dumps(device_json_message)
