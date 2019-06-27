#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmDeviceMerge.py
'''
Scenario for adding MSF device 
'''
import traceback
from EmMergeScenario import EmMergeScenario
from EmCommonDriver import EmCommonDriver
import GlobalModule
from EmCommonLog import decorater_log


class EmDeviceMerge(EmMergeScenario):
    '''
    Scenario for adding MSF device 
    '''
    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmDeviceMerge, self).__init__()

    @decorater_log
    def _process_scenario(self,
                          device_message=None,
                          transaction_id=None,
                          order_type=None,
                          condition=None,
                          device_name=None,
                          force=False):
        '''
        Scenario for each device is executed.
        Argument:
            device_message: message for each device (byte)
            transaction_id: transaction ID (uuid)
            order_type: order type (int)
            condition: thread control information (condition object)
            device_name:  device name (str)
            force: flag indicating forced stop (boolean)
        Return value:
            none
        '''
        if ("newly-establish" not in device_message) and \
                ("equipment" in device_message):
            GlobalModule.EM_LOGGER.debug("no newly-establish flag")
            self._process_scenario_existing(
                device_message=device_message,
                transaction_id=transaction_id,
                order_type=order_type,
                condition=condition,
                device_name=device_name,
                force=force)
        else:
            GlobalModule.EM_LOGGER.debug("with newly-establish flag")
            super(EmDeviceMerge, self)._process_scenario(
                device_message=device_message,
                transaction_id=transaction_id,
                order_type=order_type,
                condition=condition,
                device_name=device_name,
                force=force)

    @decorater_log
    def _process_scenario_existing(self,
                                   device_message=None,
                                   transaction_id=None,
                                   order_type=None,
                                   condition=None,
                                   device_name=None,
                                   force=False):
        '''
        Scenario for each device is executed.(scenario for curent system)
        Argument:
            device_message: message for each device(byte)
            transaction_id: transaction ID (uuid)
            order_type: order type (int)
            condition: thread control information (condition object)
            device_name: device name (str)
            force: flag indicating forced stop (boolean)
        Return value:
            None
        '''
        self.com_driver_list[device_name] = EmCommonDriver()

        self._device_state_transition(
            device_name=device_name,
            order_type=order_type,
            transaction_id=transaction_id,
            transition_state=GlobalModule.TRA_STAT_PROC_RUN,
            failure_state=GlobalModule.TRA_STAT_PROC_ERR_TEMP)

        try:
            json_message = self._creating_json(device_message)
        except Exception:
            GlobalModule.EM_LOGGER.debug("receive message parse NG")
            GlobalModule.EM_LOGGER.debug("Traceback:%s",
                                         traceback.format_exc())
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:12" +
                "(processing failure(Stored information None))",
                self.error_code02, self._scenario_name, device_name)
            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_ORDER,
                                 False, False)
            raise
        else:
            GlobalModule.EM_LOGGER.debug("json_message =%s", json_message)

        self._start_common_driver(device_name=device_name,
                                  order_type=order_type,
                                  transaction_id=transaction_id,
                                  json_message=json_message)

        self._device_state_transition_with_timer(
            device_name=device_name,
            order_type=order_type,
            transaction_id=transaction_id,
            transition_state=GlobalModule.TRA_STAT_PROC_END,
            failure_state=GlobalModule.TRA_STAT_PROC_ERR_OTH,
            is_connected=False,
            get_timer_method=self._get_timer_value_for_disconnect,
            condition=condition,
            is_roleback=False)

        self._register_the_setting_in_em(device_name=device_name,
                                         order_type=order_type,
                                         device_message=device_message,
                                         transaction_id=transaction_id)

        GlobalModule.EM_LOGGER.debug("scenario all ok.")
