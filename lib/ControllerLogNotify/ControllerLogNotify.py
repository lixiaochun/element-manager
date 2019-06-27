#! /usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: ControllerLogNotify.py

import logging
import threading
import GlobalModule
import requests
import json

from EmCommonLog import decorater_log, decorater_log_in_out


class ControllerLogNotify(object):
    '''
    Controller log notification class
    '''

    LogName = {
        GlobalModule.TRACE_LOG_LEVEL: "TRACE",
        logging.DEBUG: "DEBUG",
        logging.INFO: "INFO",
        logging.WARN: "WARNING",
        logging.ERROR: "ERROR",
    }

    def __init__(self):
        '''
        Constructor
        '''
        self.address = self._get_conf("Ec_rest_server_address")
        self.port = self._get_conf("Ec_port_number")
        self.controller_type = "em"
        self.api_url = "v1/internal/ec_ctrl/logstatusnotify"
        self.url_format = "http://{address}:{port}/{api_url}"

    @decorater_log_in_out
    def notify_logs(self, msg, log_level):
        '''
        Log is notified.
        Argument:
            msg : log data (str)
            log_level : log level (int)
        '''
        if self.address and self.port:
            thread = threading.Thread(target=self.send_notify_request,
                                      args=(msg, log_level))
            thread.daemon = True
            thread.start()
        else:
            GlobalModule.EM_LOGGER.debug("not notify : No EC address")

    @decorater_log_in_out
    def send_notify_request(self, msg, log_level):
        '''
        Request is sent to API for specified address.
        Argument:
            msg : log data (str)
            log_level : log level (int)
        '''
        request_body = self._set_request_body(msg, log_level)
        request_body = json.dumps(request_body)
        url = self.url_format.format(address=self.address,
                                     port=self.port,
                                     api_url=self.api_url)
        header = {'Content-Type': 'application/json'}
        GlobalModule.EM_LOGGER.debug("Send PUT Request:" +
                                     "URL=%s ,Body=%s ,Header=%s",
                                     url, request_body, header)
        req = requests.put(url, data=request_body, headers=header)
        GlobalModule.EM_LOGGER.debug("request status:%s", req.status_code)

    @decorater_log
    def _set_request_body(self, msg, log_level):
        '''
        Body in request is generated.
        Argument:
            msg : log data (str)
            log_level : log level (int)
        Return value:
            body part ; dict
        '''
        body_json = {}
        controller_info = {}
        controller_info["controller_type"] = self.controller_type
        controller_info["log_level"] = self.LogName[log_level]
        controller_info["message"] = [msg]
        body_json["controller"] = controller_info
        return body_json

    def _get_conf(self, conf_name):
        '''
        Config definition is acquired from system common definition.
        Argument:
            conf_name : config key (str)
        Return value:
            config key value (if acquiring config fails, None is set.)
        '''
        is_ok, return_val = (
            GlobalModule.EM_CONFIG.read_sys_common_conf(conf_name))
        if not is_ok:
            return_val = None
        return return_val
