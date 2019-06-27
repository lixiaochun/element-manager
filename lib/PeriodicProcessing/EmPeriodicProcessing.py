#! /usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmPeriodicProcessing.py

import threading
import datetime
import traceback
import GlobalModule
from EmPeriodicProcessingTimeKeep import EmPeriodicProcessingTimeKeep
from EmCommonLog import decorater_log, decorater_log_in_out


class EmPeriodicProcessing(object):
    '''
    Class for periodic process management
    '''
    @decorater_log
    def __init__(self,
                 exec_class=None,
                 roop_interval=0,
                 stop_timeout=200):
        '''
        Costructor
        '''

        self.is_roop = True
        self.roop_thread = None
        self.roop_interval = roop_interval
        self.stop_timeout = stop_timeout
        self.exec_module = exec_class() if exec_class else None
        self.time_keeper = EmPeriodicProcessingTimeKeep(self.roop_interval)

    @decorater_log_in_out
    def boot(self):
        '''
        Periodic process is started
        '''
        if self.roop_interval > 0:
            self.roop_thread = threading.Thread(target=self.roop_process)
            self.roop_thread.daemon = True
            self.roop_thread.start()
        else:
            GlobalModule.EM_LOGGER.debug("Do not perform periodic processing")

    @decorater_log_in_out
    def stop(self):
        '''
        Periodic process is terminated.
        '''
        if self.roop_interval > 0:

            self.is_roop = False
            self.roop_thread.join(self.stop_timeout)

    @decorater_log_in_out
    def roop_process(self):
        '''
        Loop process
        '''
        GlobalModule.EM_LOGGER.debug("Start periodic processing")
        while self.is_roop:
            now_time = datetime.datetime.now()
            self.execute()
            self.time_keeper.timekeep(now_time)
        GlobalModule.EM_LOGGER.debug("Stop periodic processing")

    @decorater_log_in_out
    def execute(self):
        '''
        Periodic execution
        '''
        try:
            self.exec_module.execute()
        except Exception as exc_info:
            GlobalModule.EM_LOGGER.debug("ERROR periodic processing")
            GlobalModule.EM_LOGGER.debug("ERROR INFO:%s", exc_info)
            GlobalModule.EM_LOGGER.debug(traceback.format_exc())
