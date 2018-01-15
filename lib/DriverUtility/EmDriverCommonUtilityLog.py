#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2017 Nippon Telegraph and Telephone Corporation
# Filename: EmDriverCommonUtilityLog.py
'''
Common utility for the driver (Log)
'''
import logging
import inspect
import GlobalModule
from EmCommonLog import decorater_log
import EmLoggingTool


class EmDriverCommonUtilityLog(object):
    '''
    Log output class for the individual section on the driver
    '''

    __LogLevel = {"DEBUG": logging.DEBUG,
                  "INFO": logging.INFO,
                  "WARN": logging.WARN,
                  "ERROR": logging.ERROR}

    @decorater_log
    def __init__(self, device_name=None):
        '''
        Constructor
        '''

        self.log_dev_name = device_name

        self.__driver_logger = logging.getLogger(__name__)
        self.__is_log_out = True

        if len(self.__driver_logger.handlers) == 0:
            self.__driver_logger.propagate = False

            if len(GlobalModule.EM_LOGGER.handlers) != 1:
                raise ValueError("not rotate handler")
            time_rotate_handle = GlobalModule.EM_LOGGER.handlers[0]

            handler = time_rotate_handle.getFileHandler()
            formatter = EmLoggingTool.Formatter(
                "[%(asctime)s] [%(levelname)s] [tid=%(thread)d] %(message)s")
            handler.setFormatter(formatter)
            self.__driver_logger.addHandler(handler)

    @decorater_log
    def logging(self,
                device_name=None,
                log_level=None,
                log_message=None,
                log_module=" "):
        '''
        Log output (Individual section on the driver)
        Explanation about parameter:
            device_name: Device name
            log_level: Log level (DEBUG,INFO,WARN,ERROR)
            log_message: Log message
            log_module: Module name (Make sure to input "_name_" as the argument.)
        Explanation about the return value:
            Log output result : Boolean
        '''
        if self.__is_log_out is False:
            return False

        if not self.log_dev_name and device_name:
            self.log_dev_name = device_name

        if not device_name:
            device_name = self.log_dev_name

        frame = inspect.currentframe(2)
        log_line_no = str(frame.f_lineno)
        log_func_name = frame.f_code.co_name

        out_message = (
            "(%(module)s::%(funcName)s:%(lineno)s):{%(device)s}:%(message)s" %
            {"module": log_module,
             "funcName": log_func_name,
             "lineno": log_line_no,
             "device": device_name,
             "message": log_message,
             }
        )

        if log_level == "DEBUG":
            self.__driver_logger.debug(out_message)
        elif log_level == "INFO":
            self.__driver_logger.info(out_message)
        elif log_level == "WARN":
            self.__driver_logger.warning(out_message)
        elif log_level == "ERROR":
            self.__driver_logger.error(out_message)
        else:
            return False

        return True
