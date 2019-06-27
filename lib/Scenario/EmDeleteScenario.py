#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmDeleteScenario.py
'''
Class which is common for scenario for deletion
'''
from EmMergeScenario import EmMergeScenario
import GlobalModule
from EmCommonLog import decorater_log


class EmDeleteScenario(EmMergeScenario):
    '''
    Class which is common for scenario for deletion
    '''

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmDeleteScenario, self).__init__()

    @decorater_log
    def _setting_device(self,
                        device_name=None,
                        order_type=None,
                        transaction_id=None,
                        json_message=None):
        '''
        Conduct setting device for each device.
        Explanation about parameter:
            device_name: Device name (str)
            order_type: Order type(str)
            transaction_id: Transation ID (uuid)
            json_message: EC message with json type (str)
         Explanation about return value:
            Result: (OK:True,NG:False) : boolean
        '''
        com_driver = self.com_driver_list[device_name]
        is_result = com_driver.delete_device_setting(device_name,
                                                     self.service,
                                                     order_type,
                                                     json_message)
        if is_result == GlobalModule.COM_DELETE_OK:
            GlobalModule.EM_LOGGER.debug("delete_device_setting OK")
        else:
            if is_result == GlobalModule.COM_DELETE_VALICHECK_NG:
                GlobalModule.EM_LOGGER.debug(
                    "delete_device_setting validation check NG")
                GlobalModule.EM_LOGGER.warning(
                    "%s Scenario:%s Device:%s NG:9" +
                    "(processing failure(validation check NG))",
                    self.error_code02, self._scenario_name, device_name)

                self._find_subnormal(transaction_id, order_type, device_name,
                                     GlobalModule.TRA_STAT_PROC_ERR_CHECK,
                                     True, False)
            else:
                GlobalModule.EM_LOGGER.debug("delete_device_setting delete NG")
                GlobalModule.EM_LOGGER.warning(
                    "%s Scenario:%s Device:%s NG:16" +
                    "(processing failure(device setting NG))",
                    self.error_code02, self._scenario_name, device_name)
                self._find_subnormal(transaction_id, order_type, device_name,
                                     GlobalModule.TRA_STAT_PROC_ERR_SET_DEV,
                                     True, False)
            raise Exception("delete_device_setting NG")
