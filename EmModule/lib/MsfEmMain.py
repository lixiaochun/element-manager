# -*- coding: utf-8 -*-

import signal
import time
import os
import logging
import traceback
import GlobalModule
import EmCommonLog
from EmConfigManagement import EmConfigManagement
from EmDBControl import EmDBControl
from EmOrderflowControl import EmOrderflowControl
from EmSysCommonUtilityDB import EmSysCommonUtilityDB
from EmNetconfServer import EmNetconfSSHServer, EmStatus, STOP


def receive_signal(signum, frame):
                                % (signum, frame))
    GlobalModule.NETCONFSSH.stop()


def msf_em_start():
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    signal.signal(signal.SIGUSR1, signal.SIG_IGN)
    signal.signal(signal.SIGUSR2, signal.SIG_IGN)

    err_mes_conf = "Failed to get Config : %s"

    GlobalModule.EM_CONFIG = EmConfigManagement()

    isout, log_file_name = (
        GlobalModule.EM_CONFIG.read_sys_common_conf("Em_log_file_path"))
    log_file_name = (
        os.environ.get("EM_LIB_PATH") + log_file_name)
    if isout is False:
        raise IOError(err_mes_conf % ("Em_log_file_path",))
    isout, conf_log_level = (
        GlobalModule.EM_CONFIG.read_sys_common_conf("Em_log_level"))
    if isout is False:
        raise IOError(err_mes_conf % ("Em_log_level",))

    log_lev = logging.DEBUG
    if conf_log_level == "DEBUG":
        log_lev = logging.DEBUG
    elif conf_log_level == "INFO":
        log_lev = logging.INFO
    elif conf_log_level == "WARN":
        log_lev = logging.WARN
    elif conf_log_level == "ERROR":
        log_lev = logging.ERROR
    else:
        raise ValueError("Em_log_level is invalid")

    logging.basicConfig(
        filename=log_file_name,
        filemode="a",
        level=log_lev,
        format="%(asctime)s %(levelname)s %(thread)d " +
        "%(module)s %(funcName)s %(lineno)d %(message)s"
    )
    GlobalModule.EM_LOGGER = logging.getLogger(__name__)

    EmCommonLog.init_decorator_log()

    result1, tmp_val = \
        GlobalModule.EM_CONFIG.read_sys_common_conf("Timer_signal_rcv_wait")
    if not result1:
        raise IOError(err_mes_conf % ("Timer_signal_rcv_wait",))
    if tmp_val is None or tmp_val <= 0:
        raise ValueError("invalid config value : %s = %s" %
                         ("Timer_signal_rcv_wait", tmp_val))
    global SIGNAL_SLEEP_SECOND
    SIGNAL_SLEEP_SECOND = tmp_val / 1000.0

    result1, username = GlobalModule.EM_CONFIG.read_if_process_conf("Account")
    if result1 is False:
        raise IOError(err_mes_conf % ("Account",))
    result2, password = GlobalModule.EM_CONFIG.read_if_process_conf("Password")
    if result2 is False:
        raise IOError(err_mes_conf % ("Password",))
    result3, port = GlobalModule.EM_CONFIG.read_if_process_conf("Port_number")
    if result3 is False:
        raise IOError(err_mes_conf % ("Port_number",))

    GlobalModule.NETCONFSSH = EmNetconfSSHServer(username, password, port)

    GlobalModule.DB_CONTROL = EmDBControl()

    GlobalModule.EMSYSCOMUTILDB = EmSysCommonUtilityDB()

    GlobalModule.EM_ORDER_CONTROL = EmOrderflowControl()

    GlobalModule.NETCONFSSH.start()

    signal.signal(signal.SIGUSR1, receive_signal)

if __name__ == "__main__":
    SIGNAL_SLEEP_SECOND = 1.0
    try:
        msf_em_start()
    except Exception, ex_message:
        STREAM_LOG_NAME = "msf_stream_logger"
        HANDLER = logging.StreamHandler()
        if GlobalModule.EM_LOGGER is not None:
            STREAM_LOGGER = GlobalModule.EM_LOGGER.getChild(STREAM_LOG_NAME)
        else:
            STREAM_LOGGER = logging.getLogger(STREAM_LOG_NAME)
        STREAM_LOGGER.setLevel(logging.DEBUG)
        FORMATTER = logging.Formatter(
            "%(asctime)s %(thread)d %(module)s %(message)s")
        HANDLER.setFormatter(FORMATTER)
        STREAM_LOGGER.addHandler(HANDLER)
        STREAM_LOGGER.debug("ERROR %s\n%s" %
                            (ex_message, traceback.format_exc()))
    else:
        while True:
            if EmStatus.get_em_status() == STOP:
                break
            time.sleep(SIGNAL_SLEEP_SECOND)
