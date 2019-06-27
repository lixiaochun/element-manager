#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmNetconfResponse.py
from EmCommonLog import decorater_log_in_out


class EmNetconfResponse(object):
    """
    Netconf response information class
    """

    @decorater_log_in_out
    def __init__(self, order_result=None, session_id=None, ec_message=None):
        self.device_scenario_results_list = []
        self.order_result = order_result

        self.session_id = session_id
        self.ec_message = ec_message

    @decorater_log_in_out
    def store_device_scenario_results(self, device_name, transaction_result):
        ins_dev_res = EmDeviceScenarioResult(device_name, transaction_result)
        self.device_scenario_results_list.append(ins_dev_res)


class EmDeviceScenarioResult(object):
    """
    Class for scenario reslut in each device
    """

    @decorater_log_in_out
    def __init__(self, device_name, order_result=None):
        self.device_name = device_name
        self.order_result = order_result
