# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2018 Nippon Telegraph and Telephone Corporation
# Filename: EmCommonLog.py

'''
Common log decorator module.
'''
import logging
import functools
import os
import GlobalModule
import EmLoggingTool

__EM_START_STOP_LOGGER = None


def decorater_log(func):
    '''
    Method start/finish DEBUG log output decorator.
        *@decorater_log is required as the decorator method when using.
    '''
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        '''
        Decorator wrapper.
        '''
        def output_decorate_log(conditon, func):
            '''
            Method start/finish DEBUG log output.
            '''
            f_name = func.__name__
            f_module = os.path.basename(
                func.func_code.co_filename)
            f_line_no = func.func_code.co_firstlineno
            log_str = (
                "(%(module)s::%(funcName)s:%(lineno)s): %(message)s" %
                {"module": f_module,
                 "funcName": f_name,
                 "lineno": f_line_no,
                 "message": conditon,
                 }
            )
            __EM_START_STOP_LOGGER.debug(log_str)

        output_decorate_log("START", func)
        try:
            return_val = func(*args, **kwargs)
        except Exception as exc_info:
            output_decorate_log("ERROR(%s):%s" %
                                (type(exc_info).__name__, exc_info.message),
                                func)
            raise
        output_decorate_log("END", func)
        return return_val
    return wrapper


def init_decorator_log():
    '''
    Method start/finish DEBUG log output decorator initialize.
        *Execute after EM_LOGGER creation using main function.
    '''
    global __EM_START_STOP_LOGGER

    __EM_START_STOP_LOGGER = logging.getLogger(__name__)
    __EM_START_STOP_LOGGER.propagate = False


    if len(GlobalModule.EM_LOGGER.handlers) != 1:
        raise ValueError("not rotate handler")
    time_rotate_handle = GlobalModule.EM_LOGGER.handlers[0]

    handler = time_rotate_handle.getFileHandler()
    formatter = EmLoggingTool.Formatter(
        "[%(asctime)s] [%(levelname)s] [tid=%(thread)d] %(message)s")
    handler.setFormatter(formatter)
    __EM_START_STOP_LOGGER.addHandler(handler)

    return True
