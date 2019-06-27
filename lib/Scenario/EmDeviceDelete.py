#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmDeviceDelete.py
'''
Scenario for decreasing  MSF device
'''
import traceback
from EmDeleteScenario import EmDeleteScenario
from EmCommonDriver import EmCommonDriver
import GlobalModule
from EmCommonLog import decorater_log


class EmDeviceDelete(EmDeleteScenario):
    '''
    Scenario for decreasing  MSF device
    '''
    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmDeviceDelete, self).__init__()

    @decorater_log
    def _process_scenario(self,
                          device_message=None,
                          transaction_id=None,
                          order_type=None,
                          condition=None,
                          device_name=None,
                          force=False):
        '''
        Scenario in each device is executed.
         Argument:
            device_message:  message for each device (byte)
            transaction_id: trancation ID(uuid)
            order_type: order type  (int)
            condition: thread control information(condition object)
            device_name: device name(str)
            force: flag indicating forced deletion (boolean)
        Return value:
            none
        '''
        self._process_scenario_existing(
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
        Scenario in each device is executed.
        (for decreaseing device(It is not connected with device becase it is the same as current system)
          Argument:
            device_message: message for each device (byte)
            transaction_id: trancation ID (uuid)
            order_type: order type (int)
            condition: thread control information (condition object)
            device_name: device name (str)
            force: flag indicating forced deletion(boolean)
        Return value:
            none
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
