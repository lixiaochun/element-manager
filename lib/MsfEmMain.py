#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2017 Nippon Telegraph and Telephone Corporation
# Filename: MsfEmMain.py
'''
main function module.
'''

import signal
import time
import os
import logging
import traceback
import re
import argparse
import threading
import commands
import sys
import functools
from datetime import datetime, timedelta
from copy import deepcopy


import EmSetPATH

import GlobalModule
from EmCommonLog import decorater_log
from EmConfigManagement import EmConfigManagement
from EmDBControl import EmDBControl
from EmOrderflowControl import EmOrderflowControl
from EmSysCommonUtilityDB import EmSysCommonUtilityDB
from EmNetconfServer import EmNetconfSSHServer
from EmRestServer import EmRestServer
import EmCommonLog
import EmLoggingTool

_request_lock = threading.Lock()

args = None


def get_counter_send():

    _request_lock.acquire()

    is_ok, unit_time = (
        GlobalModule.EM_CONFIG.read_sys_common_conf("Rest_request_average"))

    diffdate = datetime.now() - timedelta(seconds=unit_time)

    counter = 0
    for timeval in GlobalModule.EM_REST_SEND:
        counter += 1
        if timeval <= diffdate:
            break
    _request_lock.release()
    return counter


def _deco_count_request(func):
    '''
    Request counter decorator.
    '''
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        _request_counter()
        return func(*args, **kwargs)
    return wrapper


@decorater_log
def _request_counter(request_date=datetime.now()):
    '''
    Update the request history list.
    '''
    _request_lock.acquire()
    is_ok, unit_time = (
        GlobalModule.EM_CONFIG.read_sys_common_conf("Rest_request_average"))
    if not is_ok:
        GlobalModule.EM_LOGGER.error('310009 REST Count Error')
        _request_lock.release()
        return False
    before_time = request_date + timedelta(seconds=(-1 * unit_time))
    GlobalModule.EM_REST_SEND.append(request_date)
    GlobalModule.EM_REST_SEND = [tmp for tmp
                                 in deepcopy(GlobalModule.EM_REST_SEND)
                                 if tmp >= before_time]
    _request_lock.release()
    return True


def receive_signal(signum, frame):
    '''
    The method to be called at the MAIN thread when receiving signal.
    Explanation about parameter:
        signum: signal number  
        frame: frame object 
    Explanation about the return value:
        None
    '''
    GlobalModule.EM_LOGGER.info('Receive signal (signum = %s ,frame = %s)'
                                % (signum, frame))

    if signum == signal.SIGUSR1:
        param = GlobalModule.COM_STOP_NORMAL
    else:
        param = GlobalModule.COM_STOP_CHGOVER

    GlobalModule.NETCONFSSH.stop(param)


@_deco_count_request
def send_request_by_curl(send_url, json_message=None, method="PUT"):
    '''
    Send request by Curl.
    '''

    curl_comm_base = ('curl -sS --connect-timeout 5 -m 60 ' +
                      '-w \'resultCode:%{http_code}\' ' +
                      '-H "Accept: application/json" -H "Content-type: application/json" ')
    method_opt = "-X %s " % (method,)
    body_opt = '-g -d \"%s\" ' % (json_message,)
    str_command = curl_comm_base + method_opt + body_opt + send_url + ' 2>&1 '
    GlobalModule.EM_LOGGER.debug("exec curl command : %s", (str_command,))
    command_result = commands.getoutput(str_command)
    GlobalModule.EM_LOGGER.debug("exec curl result : %s", (command_result,))
    status_code_mathc = re.search("resultCode:([0-9]{3})", command_result)
    if status_code_mathc:
        status_code = int(status_code_mathc.groups()[0])
    else:
        status_code = 500
    return status_code


def notice_systen_switch_complete_to_ec():
    '''
    Send a system switching notification to EC.
    '''
    GlobalModule.EM_LOGGER.debug("Start notice EC")
    chgover_json_message = {
        "controller":
        {
            "controller_type": "em",
            "event": "end system switching"
        }
    }
    ec_uri = gen_ec_rest_api_uri('/v1/internal/ec_ctrl/statusnotify')
    status_code = send_request_by_curl(ec_uri, chgover_json_message, "PUT")
    if status_code != 200:
        GlobalModule.EM_LOGGER.debug(
            "Fault notice systen switch complete to ec " +
            "(StatusCode=%s)" % (status_code,))
        return False
    else:
        GlobalModule.EM_LOGGER.debug(
            "Success notice systen switch complete to ec")
        return True


def gen_ec_rest_api_uri(target_api="/"):
    '''
    Compose the URI for the REST API of EC.
    '''
    err_mes_conf = "Failed to get Config : %s"
    is_ok, ec_address = (
        GlobalModule.EM_CONFIG.read_sys_common_conf("Ec_rest_server_address"))
    if not is_ok:
        raise IOError(err_mes_conf % ("Ec_rest_server_address",))
    is_ok, ec_port = (
        GlobalModule.EM_CONFIG.read_sys_common_conf("Ec_port_number"))
    if not is_ok:
        raise IOError(err_mes_conf % ("Ec_port_number",))
    ec_url = 'http://%s' % (ec_address,)
    ec_url += ':%s' % (ec_port,) if ec_port is not None else ""
    ec_url += target_api
    GlobalModule.EM_LOGGER.debug("EC REST API URI:%s" % (ec_url,))
    return ec_url


def get_service_order_list():
    '''
    Obtain the service list and order list from the scenario_conf.
    Explanation about the arguement.
        None.
    Explanation about the return value:
        service_list: Service list (tuple)
        order_list: Order list (tuple)
    '''
    GlobalModule.EM_LOGGER.debug("start getting service and order list")

    service_list = []
    order_list = []

    scenario_conf = \
        GlobalModule.EM_CONFIG.read_service_type_scenario_conf()

    for key in scenario_conf.keys():
        if key[0] not in service_list:
            service_list.append(key[0])
        if key[1] not in order_list:
            order_list.append(key[1])

    GlobalModule.EM_LOGGER.debug(
        "get service_list :%s" % (tuple(service_list),))
    GlobalModule.EM_LOGGER.debug(
        "get order_list :%s" % (tuple(order_list),))
    return tuple(service_list), tuple(order_list)


def get_name_spaces(service_list):
    '''
    Obtain the service list and names space list from the Service list and Capability list.
    Explanation about the argument.
        None.
    Explanation about the return value:
        ns_dict: names space list dictionary (dict(service name: names space})
    '''
    GlobalModule.EM_LOGGER.debug("start getting namespace list")

    pattern_template = ".*/%s$"

    ns_dict = {}

    is_ok, if_capabilities = \
        GlobalModule.EM_CONFIG.read_if_process_conf("Capability")
    if not is_ok:
        if_capabilities = []

    for key in service_list:
        GlobalModule.EM_LOGGER.debug(
            'search service %s in capabilities' % (key,))
        pattern = re.compile(pattern_template % (key))
        for capability in if_capabilities:
            if pattern.search(capability):
                if capability in ns_dict.values():
                    GlobalModule.EM_LOGGER.debug(
                        'Duplicate capabilities : %s' % (capability,))
                    pass
                else:
                    ns_dict[key] = capability
                    GlobalModule.EM_LOGGER.debug(
                        'Get %s Capability : %s' % (key, capability))
                break
    GlobalModule.EM_LOGGER.debug("get namespace list : %s" % (ns_dict,))
    return ns_dict


def parse_em_run_args():
    '''
    Launch option parser.
    Explanation about the parameter:
        None
    Explanation about the return value:
        parser; Launch option parser object
    '''
    parser = argparse.ArgumentParser(description="Run EM Module")
    parser.add_argument("-c",
                        "--config-dir",
                        dest="config_dir_path",
                        metavar="EM_CONFIG_DIR_PATH",
                        type=str,
                        nargs="?",
                        help=("directory path " +
                              "where configuration files are stored"),
                        default=os.path.join("..", "conf")
                        )
    parser.add_argument("start_type",
                        metavar="START_TYPE",
                        type=str,
                        nargs="?",
                        help=("Activation type " +
                              "(normal startup or system switchover)"),
                        default=None
                        )
    return parser.parse_args()


def msf_em_start():
    '''
    The method called from the MAIN when starting to get launched.
    Explanation about the parameter:
        None
    Explanation about the return value:
        None
    '''
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    signal.signal(signal.SIGUSR1, signal.SIG_IGN)
    signal.signal(signal.SIGUSR2, signal.SIG_IGN)

    GlobalModule.EM_CONF_PATH = args.config_dir_path
    GlobalModule.EM_LIB_PATH = os.path.dirname(os.path.abspath(__file__))

    err_mes_conf = "Failed to get Config : %s"

    GlobalModule.EM_CONFIG = EmConfigManagement(args.config_dir_path)

    isout, log_file_name = (
        GlobalModule.EM_CONFIG.read_sys_common_conf("Em_log_file_path"))
    log_file_name = os.path.join(GlobalModule.EM_LIB_PATH, log_file_name)
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

    em_log_format = ("[%(asctime)s] [%(levelname)s] [tid=%(thread)d] " +
                     "(%(module)s::%(funcName)s:%(lineno)d):%(message)s")

    root_logger = logging.getLogger()
    root_logger.setLevel(log_lev)

    GlobalModule.EM_LOGGER = logging.getLogger(__name__)
    GlobalModule.EM_LOGGER.propagate = False
    GlobalModule.EM_LOGGER.setLevel = log_lev
    handler = EmLoggingTool.TimedRotatingFileHandler(filename=log_file_name,
                                                     when='D',
                                                     interval=1)
    formatter = EmLoggingTool.Formatter(em_log_format)
    handler.setFormatter(formatter)
    GlobalModule.EM_LOGGER.addHandler(handler)

    GlobalModule.EM_LOGGER.info('101001 EM process start')
    GlobalModule.EM_LOGGER.info('101003 EM initialize start')

    root_logger_handler = handler.getFileHandler()
    root_logger_handler.setFormatter(formatter)
    root_logger.addHandler(root_logger_handler)

    EmCommonLog.init_decorator_log()

    GlobalModule.EM_SERVICE_LIST, GlobalModule.EM_ORDER_LIST =\
        get_service_order_list()

    GlobalModule.EM_NAME_SPACES = get_name_spaces(
        GlobalModule.EM_SERVICE_LIST)

    GlobalModule.EM_REST_SEND = []

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

    is_ok, rest_port = GlobalModule.EM_CONFIG.read_if_process_rest_conf(
        "Port_number")
    if not is_ok:
        raise IOError(err_mes_conf % ("Port_number(REST)",))
    is_ok, rest_address = GlobalModule.EM_CONFIG.read_if_process_rest_conf(
        "Rest_server_address")
    if not is_ok:
        raise IOError(err_mes_conf % ("Rest_server_address(REST)",))

    GlobalModule.DB_CONTROL = EmDBControl()

    GlobalModule.EMSYSCOMUTILDB = EmSysCommonUtilityDB()

    (ret, system_status) = GlobalModule.EMSYSCOMUTILDB.read_system_status(
        EmSysCommonUtilityDB.GET_DATA_TYPE_DB)
    GlobalModule.NETCONFSSH = EmNetconfSSHServer(
        username, password, port, system_status)

    GlobalModule.EM_REST_SERVER = EmRestServer(address=rest_address,
                                               port=rest_port)
    GlobalModule.EM_REST_SERVER.start()

    GlobalModule.EM_ORDER_CONTROL = EmOrderflowControl()

    GlobalModule.NETCONFSSH.start()
    GlobalModule.EM_LOGGER.info('101004 EM initialize end')

    signal.signal(signal.SIGUSR1, receive_signal)
    signal.signal(signal.SIGUSR2, receive_signal)

    is_ok, retry_num = (
        GlobalModule.EM_CONFIG.read_sys_common_conf("Ec_rest_retry_num"))
    if not is_ok:
        raise IOError(err_mes_conf % ("Ec_rest_retry_num",))
    is_ok, retry_interval = (
        GlobalModule.EM_CONFIG.read_sys_common_conf("Ec_rest_retry_interval"))
    if not is_ok:
        raise IOError(err_mes_conf % ("Ec_rest_retry_interval",))

    for num in range(int(retry_num) + 1):
        ret = notice_systen_switch_complete_to_ec()
        if ret:
            break
        else:
            time.sleep(int(retry_interval))

if __name__ == "__main__":
    SIGNAL_SLEEP_SECOND = 1.0
    try:
        args = parse_em_run_args()
        system_switch_start = args.start_type
        msf_em_start()
    except Exception, ex_message:
        STREAM_LOG_NAME = "msf_stream_logger"
        HANDLER = logging.StreamHandler()
        if GlobalModule.EM_LOGGER is not None:
            STREAM_LOGGER = GlobalModule.EM_LOGGER.getChild(STREAM_LOG_NAME)
        else:
            STREAM_LOGGER = logging.getLogger(STREAM_LOG_NAME)
        STREAM_LOGGER.setLevel(logging.DEBUG)
        FORMATTER = EmLoggingTool.Formatter(
            "%(asctime)s %(thread)d %(module)s %(message)s")
        HANDLER.setFormatter(FORMATTER)
        STREAM_LOGGER.addHandler(HANDLER)
        STREAM_LOGGER.debug("ERROR %s\n%s" %
                            (ex_message, traceback.format_exc()))
        STREAM_LOGGER.info('101002 EM process stop')
    else:
        while True:
            (ret, status) = GlobalModule.EMSYSCOMUTILDB.read_system_status(
                EmSysCommonUtilityDB.GET_DATA_TYPE_MEMORY)
            if status == EmSysCommonUtilityDB.STATE_STOP:
                GlobalModule.EM_LOGGER.info('101002 EM process stop')
                break
            time.sleep(SIGNAL_SLEEP_SECOND)
