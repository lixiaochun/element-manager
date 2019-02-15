#! /usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2018 Nippon Telegraph and Telephone Corporation
# Filename: EmRestServer.py
'''
Rest Server function.
'''
import os
import imp
import traceback
import threading
import functools
import signal
from datetime import datetime, timedelta
from copy import deepcopy
from flask import Flask, request
import GlobalModule
from EmCommonLog import decorater_log
from EmCommonLog import decorater_log_in_out

application = Flask(__name__)

_request_date_list = []

_request_lock = threading.Lock()


@decorater_log_in_out
def get_counter_recv():
    _request_lock.acquire()

    is_ok, unit_time = (
        GlobalModule.EM_CONFIG.read_sys_common_conf("Rest_request_average"))

    diffdate = datetime.now() - timedelta(seconds=unit_time)

    counter = 0
    for timeval in _request_date_list[:]:
        counter += 1
        if timeval <= diffdate:
            break

    _request_lock.release()
    return counter


def _deco_count_request(func):
    '''
    Request counter recorder.
    '''
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        _request_counter()
        return func(*args, **kwargs)
    return wrapper


@decorater_log
def _request_counter(request_date=datetime.now()):
    '''
    Update request history list.
    '''
    _request_lock.acquire()
    is_ok, unit_time = (
        GlobalModule.EM_CONFIG.read_sys_common_conf("Rest_request_average"))
    if not is_ok:
        GlobalModule.EM_LOGGER.error('310009 REST Count Error')
        _request_lock.release()
        return False
    before_time = request_date + timedelta(seconds=(-1 * unit_time))
    global _request_date_list
    _request_date_list.append(request_date)
    _request_date_list = [
        tmp for tmp in deepcopy(_request_date_list) if tmp >= before_time]
    _request_lock.release()
    return True


@application.route("/v1/internal/em_ctrl/statusget")
@_deco_count_request
def rest_if_statusget():
    '''
    Controller status acquisition.
        Obtain controller status.
    Parameter:
        key : Key
    Return value :
    '''
    return _execute_rest_api("/v1/internal/em_ctrl/statusget",
                             request=request,
                             request_date_list=deepcopy(_request_date_list))


@application.route("/v1/internal/em_ctrl/log")
@_deco_count_request
def rest_if_logget():
    '''
    Controller log acquisition.
        Obtain controller log.
    Parameter:
        key : Key
    Return value :
    '''
    return _execute_rest_api("/v1/internal/em_ctrl/log",
                             request=request)


@decorater_log
def _execute_rest_api(rest_uri, *args, **kwargs):
    '''
    Conduct processing which is common for REST server.
    '''
    GlobalModule.EM_LOGGER.info(
        '110004 Request Received: %s', rest_uri)

    try:
        scenario_name = _select_rest_scenario(rest_uri)
        scenario_ins = _import_scenario_and_get_instance(scenario_name)
        response = _execute_scenario(scenario_ins, *args, **kwargs)
    except Exception as ex:
        raise
    return response


@decorater_log
def _select_rest_scenario(rest_uri):
    '''
    Determin REST scenario to launch.
    '''
    is_result, rest_scnario = (
        GlobalModule.EM_CONFIG.read_scenario_rest_conf(rest_uri))

    if not is_result:
        GlobalModule.EM_LOGGER.debug(
            "REST API cannot get this scenario : %s" % (rest_uri,))
        raise KeyError(
            "ERROR! REST API unknown scenario : %s" % (rest_uri,))
    else:
        scenario_name_em = 'Em' + rest_scnario
        GlobalModule.EM_LOGGER.debug(
            "get scenario result Scenario:%s" % (scenario_name_em,))
        return scenario_name_em


@decorater_log
def _import_scenario_and_get_instance(rest_scenario_name):
    '''
    Read scenario, obtain instance applicable to the class.
    '''
    GlobalModule.EM_LOGGER.debug(
        'startup class name generation:%s', rest_scenario_name)

    lib_path = GlobalModule.EM_LIB_PATH
    GlobalModule.EM_LOGGER.debug('environment path:%s', lib_path)

    filepath, filename, data =\
        imp.find_module(
            rest_scenario_name, [os.path.join(lib_path, 'RestScenario')])
    GlobalModule.EM_LOGGER.debug('search modules')

    scenario_mod = imp.load_module(
        rest_scenario_name, filepath, filename, data)
    GlobalModule.EM_LOGGER.debug('load modules')

    scenario_ins = getattr(scenario_mod, rest_scenario_name)()
    GlobalModule.EM_LOGGER.debug('instantiation')

    return scenario_ins


@decorater_log
def _execute_scenario(scenario_ins, *arg, **kwargs):
    '''
    Execute scenario.
    '''
    GlobalModule.EM_LOGGER.debug('execute scenario : %s' % (scenario_ins,))
    return scenario_ins.execute(*arg, **kwargs)


class EmRestServer(object):
    '''
    REST server class
    '''

    @decorater_log
    def __init__(self, address=None, port=None):
        '''
        Constructor
        '''
        self._rest_address = address
        self._rest_port = port
        self.rest_thread = None

    @decorater_log_in_out
    def start(self):
        '''
        REST server launching method
        '''
        self.rest_thread = threading.Thread(target=self._run_server)
        self.rest_thread.setDaemon(True)
        self.rest_thread.start()
        GlobalModule.EM_LOGGER.info("110001 REST Server Start")
        return True

    @decorater_log
    def _run_server(self):
        '''
        REST server launching method (execute app.run)
        '''
        application.run(host=self._rest_address, port=self._rest_port,
                        threaded=True)
