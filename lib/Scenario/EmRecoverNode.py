#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2018 Nippon Telegraph and Telephone Corporation
# Filename: EmRecoverNode.py
'''
Individual scenario of recover node
'''
import EmRecover
import GlobalModule
from EmCommonLog import decorater_log


class EmRecoverNode(EmRecover.EmRecover):
    '''
    Scenario class for recover node
    '''

    @decorater_log
    def __init__(self):
        '''
        Constluctor
        '''

        super(EmRecoverNode, self).__init__()

        self.service = GlobalModule.SERVICE_RECOVER_NODE

        self._xml_ns = "{%s}" % GlobalModule.EM_NAME_SPACES[self.service]

        self.scenario_name = "RecoverNode"

    @decorater_log
    def _write_em_info(self, device_name, service, order_type, device_message):
        '''
        EM information update.
            Do nothing at "recover node".
            Gets launched through individual processing of each scenario, launches the writing of the EM designated information
            on the common utility (DB) across the systems.
        Argument:
            device_name: str equipment name
            service_type: str type of service
            order_type: str type of order
            ec_message: str EC message (xml)
        Return value:
            boolean method results.
                true: Normal
                false: Abnormal
        '''

        return True
