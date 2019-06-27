#! /usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmControllerStatusGetManager.py

import GlobalModule
from EmControllerStatusGetExecutor import EmControllerStatusGetExecutor
from EmControllerStatusGetTimeKeep import EmControllerStatusGetTimeKeep
from EmPeriodicProcessing import EmPeriodicProcessing
from EmCommonLog import decorater_log


class EmControllerStatusGetManager(EmPeriodicProcessing):
    '''
    Periodic notification management for controller status
    '''
    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''
        roop_interval = self._get_conf("Em_statusget_notify_interval", 60000)
        roop_interval = float(roop_interval) / 1000
        stop_timeout = self._get_conf(
            "Timer_periodic_execution_thread_stop_watch", 200)
        stop_timeout = float(stop_timeout) / 1000
        super(EmControllerStatusGetManager, self).__init__(
            exec_class=EmControllerStatusGetExecutor,
            roop_interval=roop_interval,
            stop_timeout=stop_timeout)
        self.time_keeper = EmControllerStatusGetTimeKeep(self.roop_interval)

    @decorater_log
    def _get_conf(self, key=None, default_val=None):
        '''
        Necessary config is acquired from config management part.
        Argument:
            key ; key (str)
            default_val ; default value
        Return value;
            config  definition to be acquired : depending on config definition type
        '''
        is_ok, value = GlobalModule.EM_CONFIG.read_sys_common_conf(key)
        if not is_ok or value is None:
            value = default_val
        return value
