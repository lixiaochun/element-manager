# -*- coding: utf-8 -*-
import os
import logging
import inspect
import GlobalModule
from EmCommonLog import decorater_log


class EmDriverCommonUtilityLog(object):

    __LogLevel = {"DEBUG": logging.DEBUG,
                  "INFO": logging.INFO,
                  "WARN": logging.WARN,
                  "ERROR": logging.ERROR}

    @decorater_log
    def __init__(self):
        self.__driver_logger = logging.getLogger(__name__)
        self.__is_log_out = True

        if len(self.__driver_logger.handlers) == 0:
            self.__driver_logger.propagate = False
            self.__is_log_out, conf_file_path = \
                GlobalModule.EM_CONFIG.read_sys_common_conf("Em_log_file_path")
            if self.__is_log_out is False:
                return
            lib_path = os.environ.get("EM_LIB_PATH")
            handler = logging.FileHandler(lib_path + conf_file_path)
            formatter = logging.Formatter(
                "%(asctime)s %(levelname)s %(thread)d %(message)s")
            handler.setFormatter(formatter)
            self.__driver_logger.addHandler(handler)

    @decorater_log
    def logging(self,
                device_name,
                log_level,
                log_dessage,
                log_module=" "):
        if self.__is_log_out is False:
            return False

        frame = inspect.currentframe(2)
        log_line_no = str(frame.f_lineno)
        log_func_name = frame.f_code.co_name

        out_message = "%s(%s) %s %s %s" %\
            (log_module, log_line_no, log_func_name,
             device_name, log_dessage)

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
