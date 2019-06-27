#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmLeafDelete.py
'''
Individual scenario for reducing Leaf.
'''
from EmDeviceDelete import EmDeviceDelete
import GlobalModule
from EmCommonLog import decorater_log


class EmLeafDelete(EmDeviceDelete):
    '''
    Class for reducing Leaf.
    '''

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''
        super(EmLeafDelete, self).__init__()
        
        self.scenario_name = "LeafDelete"

        self.service = GlobalModule.SERVICE_LEAF

        self._xml_ns = "{%s}" % GlobalModule.EM_NAME_SPACES[self.service]
        
        self.device_type = "device"
