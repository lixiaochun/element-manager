#! /usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2017 Nippon Telegraph and Telephone Corporation
# Filename: EmRestSeparateScenario.py
'''
Individual processing base for each scenario. 
'''
import re
from flask import jsonify
import traceback
from EmCommonLog import decorater_log
import GlobalModule


class EmRestScenario(object):
    '''
    Individual section for each scenario. (base class)
    '''
    _error_text = "ERROR_CODE=%s:%s"

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''
        self.scenario_name = None
        self.error_code_top = None
        self._error_code_list = []

    @decorater_log
    def execute(self, *args, **kwargs):
        '''
        Launched from REST server and executes individual section of each scenario. 
        Explanation about parameter:
            URI:  Request object corresponding to URI delivered from EC.
        Explanation about return value:
            True:Normal, False:Abnormal
        '''
        try:
            url_parameter = self._get_url_param(
                request=kwargs.get("request"))
            GlobalModule.EM_LOGGER.debug(
                "Request Parameter = %s" % (url_parameter,))

            response = self._scenario_main(*args, **kwargs)
            GlobalModule.EM_LOGGER.debug("Scenario Execute OK")
        except Exception as ex:
            GlobalModule.EM_LOGGER.debug(
                "Scenario Execute Error:%s" % (ex.message,))
            GlobalModule.EM_LOGGER.debug(
                "Trace Back:%s" % (traceback.format_exc(),))
            response = self._error_response(ex)
        return response

    @decorater_log
    def _get_url_param(self, **kwargs):
        pass

    @decorater_log
    def _scenario_main(self, url_parameter, *args, **kwargs):
        pass

    @decorater_log
    def _get_url_parameter(self,
                           request,
                           param_name,
                           param_type,
                           is_none_ok=False):
        '''
        Obtain URL parameter, conduct parameter check. 
        '''
        error_code = "%s0101" % (self.error_code_top,)
        if request.args.get(param_name) == None and is_none_ok == False:
            raise ValueError(self._error_text % (
                error_code, "%s don't be empty" % (param_name,)))
        elif request.args.get(param_name) == None and is_none_ok == True:
            return None
        param = request.args.get(param_name)
        try:
            trans_param = param_type(param)
        except ValueError:
            raise ValueError(self._error_text % (
                error_code, "%s is not %s Type" % (param_name, param_type)))
        return trans_param

    @decorater_log
    def _analysis_error(self, error_message):
        '''
        Analyze error message.
        '''
        error_code = None
        match_obj = re.search("ERROR_CODE=([0-9]{6})", error_message)
        if match_obj:
            error_code = match_obj.groups()[0]
        return error_code

    @decorater_log
    def _error_response(self, ex_obj):
        '''
        Create response for exceptional cases. 
        '''
        error_code = self._analysis_error(ex_obj.message)
        if error_code not in self._error_code_list:
            error_code = "%s%s" % (self.error_code_top, "0399")
        status_code = self._error_code_list.get(error_code, 500)
        response = jsonify({"error_code": error_code})
        response.headers["Content-Type"] = "application/json"
        response.status_code = status_code
        return response
