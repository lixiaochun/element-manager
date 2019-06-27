#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmCgwshServiceManagementMerge.py

'''
Individual scenario for registering new Cgwsh service
'''
import json
from lxml import etree
import GlobalModule
from EmCommonLog import decorater_log
from EmCgwshServiceFlavor import EmCgwshServiceFlavor
from EmCgwshServiceBase import EmCgwshServiceBase


class EmCgwshServiceManagementMerge(EmCgwshServiceFlavor, EmCgwshServiceBase):
    '''
    Class for registering new Cgwsh service
    '''

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''
        super(EmCgwshServiceManagementMerge, self).__init__()
        super(EmCgwshServiceFlavor, self).__init__()

        self.service = GlobalModule.SERVICE_CGWSH_SERVICE_MANAGEMENT
        self.order_type = GlobalModule.ORDER_MERGE

        self._xml_ns = "{%s}" % GlobalModule.EM_NAME_SPACES[self.service]
        self._scenario_name = "CgwshServiceManagementMerge"

        self.device_type_1 = "nvrInfo"
        self.device_type_2 = "asrInfo"

    @decorater_log
    def _creating_json(self, device_message):
        '''
        EC Message(XML) devided into each device is converted to JSON.
        Argument:
            device_message: message in each device
        Return value:
            device_json_message: JSON message
        '''
        device_json_message = {}
        xml_elm = etree.fromstring(device_message)

        GlobalModule.EM_LOGGER.debug(
            "device_message = %s", etree.tostring(xml_elm, pretty_print=True))

        dev_type = xml_elm.tag.replace(self._xml_ns, "")
        GlobalModule.EM_LOGGER.debug("device_tag = %s", xml_elm.tag)
        GlobalModule.EM_LOGGER.debug("device_type = %s", dev_type)
        if dev_type == self.device_type_2:
            device_json_message = self._get_asr_info(xml_elm)
        else:
            device_json_message = self._get_nvr_info(xml_elm)

        GlobalModule.EM_LOGGER.debug(
            "device__json_message = %s", device_json_message)

        return json.dumps(device_json_message)
