#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
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
from EmControllerStatusGetManager import EmControllerStatusGetManager
import EmCommonLog
import EmLoggingTool
import PluginLoader
from ControllerLogNotify import ControllerLogNotify

_request_lock = threading.Lock()

args = None


@decorater_log
def run_start_plugins():
    GlobalModule.EM_LOGGER.info('101016 Start Loading Plugin for Start')
    plugin_dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "EmStartPlugin")
    try:
        plugins = PluginLoader.load_plugins(plugin_dir_path, "EmPlugin")
    except Exception:
        GlobalModule.EM_LOGGER.error('301017 Error Loading Plugin for Start')
        raise
    GlobalModule.EM_LOGGER.debug('load plugins = %s', plugins)
    try:
        for plugin in plugins:
            plugin.run()
    except Exception as ex:
        GlobalModule.EM_LOGGER.error('301018 Error Execute Plugin for Start')
        GlobalModule.EM_LOGGER.debug('Plugin Run Error = %s', ex)
        raise
    GlobalModule.EM_LOGGER.debug('plugins all load and run')
    return True


def get_counter_send():
    '''
    Gets number of requests to send
    Explanation about the return value:
        counter : number of requests to send
    '''

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
    Request counter decoder
    '''
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        _request_counter()
        return func(*args, **kwargs)
    return wrapper


@decorater_log
def _request_counter(request_date=datetime.now()):
    '''
    Update history-list of sent requests.
    Explanation about parameter:
        request_date: Time of request
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


    GlobalModule.EM_STATUS_MANAGER.stop()
    GlobalModule.NETCONFSSH.stop(param)

    if signum == signal.SIGUSR2:
        notify_em_changeover("start")


def notify_em_changeover(kind):
    '''
    Start switching-over process to EC and  notifies the completion.
    '''
    err_mes_conf = "Failed to get Config : %s"
    is_ok, retry_num = (
        GlobalModule.EM_CONFIG.read_sys_common_conf("Ec_rest_retry_num"))
    if not is_ok:
        raise IOError(err_mes_conf % ("Ec_rest_retry_num",))
    is_ok, retry_interval = (
        GlobalModule.EM_CONFIG.read_sys_common_conf("Ec_rest_retry_interval"))
    if not is_ok:
        raise IOError(err_mes_conf % ("Ec_rest_retry_interval",))

    if kind == "start":
        chgover_json_message = {
            "controller":
            {
                "controller_type": "em",
                "event": "start system switching"
            }
        }
    elif kind == "end":
        chgover_json_message = {
            "controller":
            {
                "controller_type": "em",
                "event": "end system switching"
            }
        }
    ret = False
    for num in range(int(retry_num) + 1):
        ret = notice_system_switch_to_ec(chgover_json_message)
        if ret:
            break
        else:
            time.sleep(int(retry_interval))
    if ret:
        GlobalModule.EM_LOGGER.info(
            '101010 Complete to system switch notification: \"%s\"' % kind)
    else:
        GlobalModule.EM_LOGGER.warn(
            '201011 Failed to system switch notification: \"%s\"' % kind)


@_deco_count_request
def send_request_by_curl(send_url, json_message=None, method="PUT"):
    '''
    Send requests by using Curl.
    Explanation about parameter:
        send_url : destination URL
        json_message : Json body for sending
        method : WebAPI method for sending
    Explanation about the return value:
        status_code : response code
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


def notice_system_switch_to_ec(message=None):
    '''
    Notify  EC that switch-over process has started.
    Explanation about parameter:
        message : message for sending
    Explanation about the return value:
        notification success or fail
    '''
    GlobalModule.EM_LOGGER.debug("Start notice EC")
    ec_uri = gen_ec_rest_api_uri('/v1/internal/ec_ctrl/statusnotify')
    status_code = send_request_by_curl(ec_uri, message, "PUT")
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
    Generate URI for EC REST API.
    Explanation about parameter:
        target_api : API to be generated 
    Explanation about the return value:
        ec_url : URI
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

    service_conf = \
        GlobalModule.EM_CONFIG.read_service_conf_list()

    for key in service_conf.keys():
        service_list.append(key[0])

    for key in scenario_conf.keys():
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

    log_file_name = _read_sys_common_conf(err_mes_conf,
                                          "Em_log_file_path")
    log_file_name = os.path.join(GlobalModule.EM_LIB_PATH, log_file_name)
    info_log_file_name = _read_sys_common_conf(err_mes_conf,
                                               "Em_info_log_file_path")
    info_log_file_name = os.path.join(
        GlobalModule.EM_LIB_PATH, info_log_file_name)

    conf_log_level = _read_sys_common_conf(err_mes_conf,
                                           "Em_log_level")
    conf_log_file_generation_num = _read_sys_common_conf(
        err_mes_conf, "Em_log_file_generation_num")

    conf_notify_info_log = _read_sys_common_conf(err_mes_conf,
                                                 "Em_notify_info_log")
    conf_notify_warn_log = _read_sys_common_conf(err_mes_conf,
                                                 "Em_notify_warn_log")
    conf_notify_error_log = _read_sys_common_conf(err_mes_conf,
                                                  "Em_notify_error_log")

    conf_notify_log_levels = []
    _set_list(conf_notify_log_levels, conf_notify_info_log, logging.INFO)
    _set_list(conf_notify_log_levels, conf_notify_warn_log, logging.WARN)
    _set_list(conf_notify_log_levels, conf_notify_error_log, logging.ERROR)

    GlobalModule.EM_LOG_NOTIFY = ControllerLogNotify.ControllerLogNotify()

    log_lev = logging.DEBUG
    if conf_log_level == "TRACE":
        log_lev = GlobalModule.TRACE_LOG_LEVEL
    elif conf_log_level == "DEBUG":
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
    root_logger.setLevel(GlobalModule.TRACE_LOG_LEVEL)

    GlobalModule.EM_LOGGER = logging.getLogger(__name__)
    GlobalModule.EM_LOGGER.propagate = False
    GlobalModule.EM_LOGGER.setLevel(GlobalModule.TRACE_LOG_LEVEL)
    handler = EmLoggingTool.TimedRotatingFileHandler(
        filename=log_file_name,
        when='midnight',
        gzbackupCount=int(conf_log_file_generation_num),
        notify_log_levels=conf_notify_log_levels,
        gzip=True)
    info_handler = EmLoggingTool.TimedRotatingFileHandler(
        filename=info_log_file_name,
        when='midnight',
        backupCount=int(conf_log_file_generation_num))

    formatter = EmLoggingTool.Formatter(em_log_format)

    _handlerset(handler, formatter, log_lev)
    _handlerset(info_handler, formatter, logging.INFO)

    _roothandlerset(root_logger, handler, formatter)
    _roothandlerset(root_logger, info_handler, formatter)

    EmCommonLog.init_decorator_log()

    GlobalModule.EM_LOGGER.info('101001 EM process start')
    GlobalModule.EM_LOGGER.info('101003 EM initialize start')

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

    GlobalModule.EM_STATUS_MANAGER = EmControllerStatusGetManager()
    GlobalModule.EM_STATUS_MANAGER.boot()

    run_start_plugins()

    GlobalModule.NETCONFSSH.start()
    GlobalModule.EM_LOGGER.info('101004 EM initialize end')

    signal.signal(signal.SIGUSR1, receive_signal)
    signal.signal(signal.SIGUSR2, receive_signal)

    if system_status == EmSysCommonUtilityDB.STATE_CHANGE_OVER:
        check_resource_status(err_mes_conf)
        notify_em_changeover("end")


def check_resource_status(err_mes_conf):
    '''
    Confirm status of resource after swtiched-over has been completed.
    If resource is locked, unlock the resource.    
    Explanation about parameter:
        err_mes_conf: error message string
    Explanation about the return value:
        None
    '''
    _Retry_num = _read_sys_common_conf(err_mes_conf,
                                       "Em_resource_status_check_retry_num")
    _Retry_wait_time = _read_sys_common_conf(
        err_mes_conf, "Em_resource_status_check_retry_timer")

    resource_grp_name = _read_sys_common_conf(err_mes_conf,
                                              "Em_resource_group_name")
    result_check = None
    for i in range(_Retry_num):
        result_check = _execute_shell(err_mes_conf,
                                      conf_key="Em_check_resource_lock",
                                      shell_arg=resource_grp_name,
                                      log_mes="check_resource_lock")
        if result_check[1]:
            _execute_shell(err_mes_conf,
                           conf_key="Em_resource_lock_release",
                           shell_arg=resource_grp_name,
                           log_mes="resource_lock_release")
            time.sleep(_Retry_wait_time)
        else:
            return

    GlobalModule.EM_LOGGER.error(
        "301022 Post processing of EM system change over is failed.")


def _execute_shell(err_mes_conf,
                   conf_key,
                   shell_arg,
                   log_mes):
    '''
    Execute the specified script.
    Explanation about parameter:
        err_mes_conf:error message string
        conf_key: key for config of which  path is acquired.
        shell_arg: argument(to be executed) in script
        log_mes: log message
    Explanation about the return value:
        result of executed script 
    '''
    _sh_path = _read_sys_common_conf(err_mes_conf, conf_key)
    _sh_path = os.path.join(GlobalModule.EM_LIB_PATH, _sh_path)

    shell_result = None
    command_txt = "%s %s" % (_sh_path, shell_arg)
    GlobalModule.EM_LOGGER.debug("exec command:%s" % (command_txt,))
    try:
        shell_result = commands.getstatusoutput(command_txt)
        if shell_result[0] != 0:
            GlobalModule.EM_LOGGER.warn(
                "201020 Failed to execute shell:{0}".format(shell_result[1]))
        GlobalModule.EM_LOGGER.debug("shell result = %s", shell_result)
        GlobalModule.EM_LOGGER.info(
            "101019 Execute script:%s", log_mes)

    except Exception as ex:
        GlobalModule.EM_LOGGER.warn("201021 command error:%s" % (ex.message,))

    return shell_result


def _handlerset(handler, formatter, log_lev):
    '''
    Set handler.
    Explanation about parameter:
        handler: handler
        formatter: log format
        log_lev: log level
    '''
    handler.setFormatter(formatter)
    handler.setLevel(log_lev)
    GlobalModule.EM_LOGGER.addHandler(handler)


def _roothandlerset(root_logger, handler, formatter):
    '''
    Set handler for route logger.
    Explanation about parameter:
        formatter: log format
        log_lev: log level
    '''
    root_logger_handler = handler.getFileHandler()
    root_logger_handler.setFormatter(formatter)
    root_logger.addHandler(root_logger_handler)


def _read_sys_common_conf(err_mes_conf, conf_key):
    '''
    Get the value from conf_sys_common.conf.
    If it cannot be obtained, raise error,
    Explanation about parameter:
        err_mes_conf: error messge string
        conf_key: Key of config
    Explanation about the return value:
        conf_value：value of config
    '''
    isout, conf_value = (
        GlobalModule.EM_CONFIG.read_sys_common_conf(conf_key))
    if not isout:
        raise IOError(err_mes_conf % (conf_key,))
    return conf_value


def _set_list(set_list, is_set, set_value):
    '''
    Add value to list.
    Explanation about parameter:
        set_list: list to be added
        is_set: whether it is to be added or not.(boolean)
        set_value: values to be added in  list.
    Explanation about the return value:
        set_list：added list
    '''
    if is_set:
        set_list.append(set_value)


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
