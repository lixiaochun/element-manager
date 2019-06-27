#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmSpineDelete.py
'''
Individual scenario for Spine reduction.
'''
from EmDeviceDelete import EmDeviceDelete
import GlobalModule
from EmCommonLog import decorater_log


class EmSpineDelete(EmDeviceDelete):
    '''
    Class for Spine reduction.
    '''

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmSpineDelete, self).__init__()

        self.scenario_name = "SpineDelete"

        self.service = GlobalModule.SERVICE_SPINE

        self._xml_ns = "{%s}" % GlobalModule.EM_NAME_SPACES[self.service]

        self.device_type = "device"
