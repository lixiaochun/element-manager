# -*- coding: utf-8 -*-

import logging
import functools
import os
import GlobalModule

__EM_START_STOP_LOGGER = None


def decorater_log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        def output_decorate_log(conditon, func):
            f_name = func.__name__
            f_module = os.path.basename(
                func.func_code.co_filename)
            f_line_no = func.func_code.co_firstlineno
            log_str = "%s %s %s %s" %\
                (f_module, f_name, f_line_no, conditon)
            __EM_START_STOP_LOGGER.debug(log_str)

        output_decorate_log("START", func)
        return_val = func(*args, **kwargs)
        output_decorate_log("END", func)
        return return_val
    return wrapper


def init_decorator_log():
    global __EM_START_STOP_LOGGER

    __EM_START_STOP_LOGGER = logging.getLogger(__name__)
    __EM_START_STOP_LOGGER.propagate = False

    isout, log_file_name = GlobalModule.EM_CONFIG.\
        read_sys_common_conf("Em_log_file_path")
    if isout is False:
        return False

    lib_path = os.environ.get("EM_LIB_PATH")
    handler = logging.FileHandler(lib_path + log_file_name)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(thread)d %(message)s")
    handler.setFormatter(formatter)
    __EM_START_STOP_LOGGER.addHandler(handler)

    return True
