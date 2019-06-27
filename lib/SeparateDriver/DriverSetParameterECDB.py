#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: DriverSetParameterECDB.py

'''
Module for driver configuration 
'''
import json
from EmCommonLog import decorater_log


class DriverSetParameterECDB(object):
    '''
    Parameter class for driver configuration
    '''

    @decorater_log
    def __init__(self,
                 device_name=None,
                 ec_message=None,
                 db_info=None,
                 order_type=None):
        '''
        Constructor
        '''
        self.device_name = device_name
        self.ec_message = json.loads(ec_message)
        self.db_info = db_info
