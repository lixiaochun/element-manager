#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: NcsPluginCreateResponseMSF.py
import os
from lxml import etree
import GlobalModule
from EmCommonLog import decorater_log, decorater_log_in_out

plugin_name = os.path.basename(__file__)

rpc_error_message = """
<rpc-error>
<error-type>application</error-type>
<error-tag>operation-failed</error-tag>
<error-severity>error</error-severity>
<error-message xml:lang="en">dummy</error-message>
<error-info>
    <operator-mediation>false</operator-mediation>
</error-info>
</rpc-error>
"""

mediation_parme = {
    GlobalModule.TRA_STAT_PROC_END: True,
    GlobalModule.TRA_STAT_ROLL_BACK_END: False,
    GlobalModule.TRA_STAT_ROLL_BACK_ERR: True,
    GlobalModule.TRA_STAT_PROC_ERR_CHECK: False,
    GlobalModule.TRA_STAT_PROC_ERR_ORDER: False,
    GlobalModule.TRA_STAT_PROC_ERR_MATCH: False,
    GlobalModule.TRA_STAT_PROC_ERR_INF: False,
    GlobalModule.TRA_STAT_PROC_ERR_TEMP: False,
    GlobalModule.TRA_STAT_PROC_ERR_OTH: True,
    GlobalModule.TRA_STAT_PROC_ERR_GET_BEF_CONF: False,
    GlobalModule.TRA_STAT_PROC_ERR_SET_DEV: True,
    GlobalModule.TRA_STAT_PROC_ERR_GET_AFT_CONF: True,
    GlobalModule.TRA_STAT_PROC_ERR_STOP_RETRY: False,
    GlobalModule.TRA_STAT_PROC_ERR_STOP_NO_RETRY: True,
}


@decorater_log_in_out
def create_resp_message(order_resp, response_info):
    '''
    It is started from EmNetconfServer and generates Netconf (rpc-reply) according to the argument.
    Argument:
        order_resp:Response contents to EC main module
        response_info:response information(EmNetconfResponse object)
    Return value:
        rpc_message:response message to EC main module
    '''
    rpc_message = None
    if order_resp == GlobalModule.ORDER_RES_OK:
        rpc_message = _message_ok()
        GlobalModule.EM_LOGGER.info("102005 Sending rpc-reply")
    else:
        rpc_message = _message_error(order_resp, response_info)
        GlobalModule.EM_LOGGER.info(
            "102006 Sending rpc-error: %s", etree.tostring(rpc_message))
    return rpc_message


@decorater_log
def _message_ok():
    '''
    Normal response is returned.
    Argument:
        None
    Return value:
        rpc_message:response message to EC main module
    '''
    return etree.Element('ok')


@decorater_log
def _message_error(order_resp, response_info):
    '''
    Failure response is returned.
    Argument:
        None
    Return value:
        rpc_message:response message to EC main module
    '''
    error_rpc = etree.fromstring(rpc_error_message) 
    if order_resp == GlobalModule.ORDER_RES_PROC_ERR_ORDER:
        _message_error_err_order(error_rpc)
    elif order_resp == GlobalModule.ORDER_RES_PROC_ERR_INF:
        _message_error_err_inf(error_rpc, response_info)
    elif order_resp == GlobalModule.ORDER_RES_PROC_ERR_TEMP:
        _message_error_err_temp(error_rpc)
    elif order_resp == GlobalModule.ORDER_RES_PROC_ERR_GET_BEF_CONF:
        _message_error_err_get_bef_conf(error_rpc, response_info)
    elif order_resp == GlobalModule.ORDER_RES_PROC_ERR_SET_DEV:
        _message_error_err_set_dev(error_rpc, response_info)
    elif order_resp == GlobalModule.ORDER_RES_PROC_ERR_GET_AFT_CONF:
        _message_error_err_get_aft_conf(error_rpc, response_info)
    else:
        _message_error_err_other(error_rpc)
    return error_rpc


@decorater_log
def _message_error_err_order(rpc):
    '''
    NG response(request parameter is invalid) is returned.
    Argument:
        rpc:rpc-error message (etree.Element object)
    Return value:
        None(rpc is over-written.) 
    '''

    err_txt = "bad request"
    rpc.find(".//error-message").text = err_txt
    _set_error_info(rpc, set_mediation=False)


@decorater_log
def _message_error_err_inf(rpc, response_info):
    '''
    NG response(there is no inrfomation) is returned.
    Argument:
        rpc:rpc-error message(etree.Element object)
        response_info:response information(EmNetconfResponse object)
    Return value:
        None(rpc is over-written.) 
    '''
    err_txt = _text_error_message_for_ecah_device(response_info)
    rpc.find(".//error-message").text = err_txt
    _set_error_info(rpc, response_info=response_info)


@decorater_log
def _message_error_err_temp(rpc):
    '''
    NG response(temporary) is returned.
    Argument:
        rpc:rpc-error message(etree.Element object)
    Return value:
        None(rpc is over-written.) 
    '''
    err_txt = "service unavailable"
    rpc.find(".//error-message").text = err_txt
    _set_error_info(rpc, set_mediation=False)


@decorater_log
def _message_error_err_other(rpc):
    '''
    NG response(other reasons) is returned.
    Argument:
        rpc:rpc-error message(etree.Element object)
    Return value:
        None(rpc is over-written.) 
    '''
    err_txt = "internal server error"
    rpc.find(".//error-message").text = err_txt
    _set_error_info(rpc, set_mediation=True)


@decorater_log
def _message_error_err_get_bef_conf(rpc, response_info):
    '''
    NG response(advanced config could not be acquired.) is returned.
    Argument:
        rpc:rpc-error message (etree.Element object)
        response_info:response information(EmNetconfResponse object)
    Return value:
        None(rpc is over-written.) 
    '''
    err_txt = _text_error_message_for_ecah_device(response_info)
    rpc.find(".//error-message").text = err_txt
    _set_error_info(rpc, response_info=response_info)


@decorater_log
def _message_error_err_set_dev(rpc, response_info):
    '''
    NG response(device setting error) is returned.
    Argument:
        rpc:rpc-error message(etree.Element object)
        response_info:response information(EmNetconfResponse object)
    Return value:
        None(rpc is over-written.) 
    '''
    err_txt = _text_error_message_for_ecah_device(response_info)
    rpc.find(".//error-message").text = err_txt
    _set_error_info(rpc, response_info=response_info)


@decorater_log
def _message_error_err_get_aft_conf(rpc, response_info):
    '''
    NG response(advanced config could not be acquired.) is returned.
    Argument:
        rpc:rpc-error message(etree.Element object)
        response_info:response information(EmNetconfResponse object)
    Return value:
        None(rpc is over-written.) 
    '''
    err_txt = _text_error_message_for_ecah_device(response_info)
    rpc.find(".//error-message").text = err_txt
    _set_error_info(rpc, response_info=response_info)


@decorater_log
def _text_error_message_for_ecah_device(response_info):
    '''
    Error message is generated for each device.
    Argument:
        response_info:response information(EmNetconfResponse object)
    Return value:
        text is set to error-info value (str)
    '''
    err_txt = ""
    delimiter = ""
    for dev_result in response_info.device_scenario_results_list:
        device_name = dev_result.device_name
        order_result = dev_result.order_result
        result_text = _get_txt_from_device_order(device_name, order_result)
        err_txt += "{0}{1}::{2}".format(delimiter, device_name, result_text)
        delimiter = ","
    return err_txt


@decorater_log
def _get_txt_from_device_order(device_name, order_result):
    '''
    Order result and error message are generated for each device.
    Argument:
        device_name : device name (str)
        order_result ：order result of each device (int)
    Return value:
         Error message for each device : str
    '''
    result_text = ""
    if order_result <= GlobalModule.TRA_STAT_ROLL_BACK_END:
        result_text = "Control success to {0}".format(device_name)
    elif order_result == GlobalModule.TRA_STAT_PROC_ERR_INF:
        result_text = ("Connection error to {0}".format(device_name))
    elif order_result == GlobalModule.TRA_STAT_PROC_ERR_GET_BEF_CONF:
        result_text = ("Confirmation error of " +
                       "preliminary setting of {0}".format(device_name))
    elif order_result == GlobalModule.TRA_STAT_PROC_ERR_SET_DEV:
        result_text = ("Setting error to {0}".format(device_name))
    elif order_result == GlobalModule.TRA_STAT_PROC_ERR_GET_AFT_CONF:
        result_text = ("Confirmation error of " +
                       "post setting of {0}".format(device_name))
    elif order_result == GlobalModule.TRA_STAT_PROC_ERR_STOP_RETRY:
        result_text = ("Due to error of other device, " +
                       "interrupted before setting to {0}".format(device_name))
    elif order_result == GlobalModule.TRA_STAT_PROC_ERR_STOP_NO_RETRY:
        result_text = ("Due to error of other device, " +
                       "interrupted after setting to {0}".format(device_name))
    else:
        result_text = "internal server error"
    return result_text


@decorater_log
def _set_error_info(rpc,
                    response_info=None,
                    set_mediation=None):
    '''
    Value is set to rpc-error message tag.
    Argument:
        rpc : rpc-error message(etree.Element object)
        response_info ：response information (EmNetconfResponse)
        set_mediation ：value which network operator sets (boolean)
                        * If it is independent of device type, this value is set.
    Return value:
        rpc_message:response message to EC main module
    '''
    if set_mediation is not None:
        _set_error_info_mediation(rpc, set_mediation)
    else:
        _set_error_info_from_response(rpc, response_info)


@decorater_log
def _set_error_info_from_response(rpc, response_info=None):
    '''
    Transaction result is acquired from response information.
    Value of rpc-error is set to error-message tag.
    Argument:
        rpc : rpc-error message(etree.Element object)
        response_info ：response information(EmNetconfResponse)
    Return value:
        rpc_message:response message to EC main module
    '''
    is_mediation = False
    for trans in response_info.device_scenario_results_list:
        dev_order = trans.order_result
        is_mediation = is_mediation or mediation_parme.get(dev_order, True)
    _set_error_info_mediation(rpc, is_mediation)


@decorater_log
def _set_error_info_mediation(rpc, is_mediation=False):
    '''
    Value of rpc-error is set to error-message tag.
    Argument:
        rpc : rpc-error message(etree.Element object)
        is_mediation ：Flag indicating network operator is needed or not(True:needed) (boolean)
    Return value:
        rpc_message:response message to EC main module
    '''
    set_txt = "true" if is_mediation else "false"
    rpc.find(".//error-info/operator-mediation").text = set_txt
