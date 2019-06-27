#! /usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmPeriodicProcessingTimeKeep.py

import time
import datetime
import math
from EmCommonLog import decorater_log, decorater_log_in_out


class EmPeriodicProcessingTimeKeep(object):
    '''
    Periodic management for execution
    '''

    @decorater_log
    def __init__(self, interval=0):
        '''
        Constructor :
        ：Argument:
            interval: interval(second) (int)
        '''
        self.interval_delta = datetime.timedelta(seconds=interval)

    @decorater_log_in_out
    def timekeep(self, base_time):
        '''
        It is waiting for next operation.
        Argument:：
            base_time: strting time for current cyclic process (datetime)
        '''
        diff_time = self._get_now_time() - base_time

        if diff_time < self.interval_delta:
            diff_sec = self.interval_delta - diff_time
            wait_time = int(math.ceil(diff_sec.total_seconds()))
            time.sleep(wait_time)

    @decorater_log
    def _get_now_time(self):
        return datetime.datetime.now()
