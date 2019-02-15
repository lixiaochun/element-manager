#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2018 Nippon Telegraph and Telephone Corporation
# Filename: EmSysCommonUtilityDB.py
'''
Utility (DB) module common for the system.
'''
import threading
from lxml import etree
import GlobalModule
from EmCommonLog import decorater_log
from EmCommonLog import decorater_log_in_out


class EmSysCommonUtilityDB(object):
    '''
    Utility (DB) class common over the system.
    '''
    STATE_STOP = 0
    STATE_READY_TO_START = 10
    STATE_CHANGE_OVER = 50
    STATE_READY_TO_STOP = 90
    STATE_START = 100

    GET_DATA_TYPE_DB = 1
    GET_DATA_TYPE_MEMORY = 2
    GET_DATA_TYPE_BOTH = 3

    table_TransactionMgmtInfo = "TransactionMgmtInfo"
    table_DeviceStatusMgmtInfo = "DeviceStatusMgmtInfo"
    table_DeviceRegistrationInfo = "DeviceRegistrationInfo"
    table_VlanIfInfo = "VlanIfInfo"
    table_LagIfInfo = "LagIfInfo"
    table_LagMemberIfInfo = "LagMemberIfInfo"
    table_L3VpnLeafBgpBasicInfo = "L3VpnLeafBgpBasicInfo"
    table_VrfDetailInfo = "VrfDetailInfo"
    table_VrrpDetailInfo = "VrrpDetailInfo"
    table_VrrpTrackIfInfo = "VrrpTrackIfInfo"
    table_BgpDetailInfo = "BgpDetailInfo"
    table_StaticRouteDetailInfo = "StaticRouteDetailInfo"
    table_PhysicalIfInfo = "PhysicalIfInfo"
    table_ClusterLinkIfInfo = "ClusterLinkIfInfo"
    table_BreakoutIfInfo = "BreakoutIfInfo"
    table_InnerLinkIfInfo = "InnerLinkIfInfo"
    table_EmSystemStatusInfo = "EmSystemStatusInfo"
    table_ACLInfo = "ACLInfo"
    table_ACLDetailInfo = "ACLDetailInfo"
    table_DummyVlanIfInfo = "DummyVlanIfInfo"
    table_MultiHomingInfo = "MultiHomingInfo"

    class __service(object):
        spine = GlobalModule.SERVICE_SPINE
        leaf = GlobalModule.SERVICE_LEAF
        l2_slice = GlobalModule.SERVICE_L2_SLICE
        l3_slice = GlobalModule.SERVICE_L3_SLICE
        ce_lag = GlobalModule.SERVICE_CE_LAG
        internal_link = GlobalModule.SERVICE_INTERNAL_LINK
        b_leaf = GlobalModule.SERVICE_B_LEAF
        cluster_link = GlobalModule.SERVICE_CLUSTER_LINK
        breakout = GlobalModule.SERVICE_BREAKOUT
        recover = GlobalModule.SERVICE_RECOVER_SERVICE
        acl_filter = GlobalModule.SERVICE_ACL_FILTER

    class __orders(object):
        delete = GlobalModule.ORDER_DELETE
        get = GlobalModule.ORDER_GET
        merge = GlobalModule.ORDER_MERGE
        replace = GlobalModule.ORDER_REPLACE

    __db_delete = "DELETE"

    @decorater_log
    def __init__(self):
        '''
        Initialization
        Explanation about parameter:
            None
        Return value:
            None
        '''
        self._namespace = GlobalModule.EM_NAME_SPACES

        self._order_replace = GlobalModule.ORDER_REPLACE

        self._if_type_phy = "physical-if"
        self._if_type_lag = "lag-if"

    @staticmethod
    @decorater_log_in_out
    def read_transactionid_list():
        '''
        Method which gets launched from order flow control
        and instructs the DB control to read the transaction management table.
        Explanation about parameter:
            None
        Return value:
            Execution result : boolean(True or False)
            Transaction ID list : tuple
        '''
        result, data = GlobalModule.DB_CONTROL.read_transactionid_list()
        if result:
            if len(data) == 0:
                data = None
            return True, data
        else:
            GlobalModule.EM_LOGGER.warning(
                '209001 Database Get Information Error')
            return False, None

    @staticmethod
    @decorater_log_in_out
    def read_transaction_info(transaction_id):
        '''
        Method which gets launched from order flow control
        and instructs the DB control to read the transaction management table.
        Explanation about parameter:
            transaction_id:Transaction ID
        Return value:
            Execution result : boolean(True or False)
            Information about the table
            which has been read out by DB control: tuple
        '''
        result, data = GlobalModule.DB_CONTROL.read_transaction_mgmt_info(
            transaction_id)
        if result:
            if len(data) == 0:
                data = None
            return True, data
        else:
            GlobalModule.EM_LOGGER.warning(
                '209001 Database Get Information Error')
            return False, None

    @staticmethod
    @decorater_log_in_out
    def initialize_order_mgmt_info():
        '''
        Method which gets launched by initialization processing and
        instructs DB control to initialize the order management information.
        Explanation about parameter:
            None
        Return value:
            Execution result : boolean(True or False)
        '''
        result = GlobalModule.DB_CONTROL.initialize_order_mgmt_info()
        if result:
            return True
        else:
            GlobalModule.EM_LOGGER.warning(
                '209002 Database Edit Information Error')
            return False

    @decorater_log_in_out
    def write_transaction_status(self,
                                 db_contolorer,
                                 transaction_id,
                                 transaction_status=None,
                                 service_type=None,
                                 order_type=None,
                                 order_text=None):
        '''
        Method which gets launched from order flow control
        and instructs the DB control to write into
        the transaction management information table.
        Explanation about parameter:
            db_contolorer,DB control
            transaction_id:Transaction ID
            transaction_status:Transaction status
            service_type:Service type
            order_type:Order type
            order_text:Order text
        Return value:
            Execution result : boolean(True or False)
        '''
        order_key = order_type if order_type is not None else self.__orders.get

        scenario_conf = \
            GlobalModule.EM_CONFIG.read_service_type_scenario_conf()
        GlobalModule.EM_LOGGER.debug('Get Scenario Dict:%s ', scenario_conf)

        tmp_scenario = scenario_conf.get(
            (service_type, order_key), (None, None, None, None))
        tmp_service_type = tmp_scenario[2]
        tmp_order_type = tmp_scenario[3]
        GlobalModule.EM_LOGGER.debug(
            'Transaction Service : %s => %s ,Transaction Order : %s => %s',
            service_type, tmp_service_type, order_key, tmp_order_type)

        result = (
            GlobalModule.DB_CONTROL.
            write_transaction_mgmt_info(db_contolorer,
                                        transaction_id,
                                        transaction_status,
                                        tmp_service_type,
                                        tmp_order_type,
                                        order_text)
        )
        if result:
            GlobalModule.EM_LOGGER.debug(
                'Transaction ID:%s Transaction Status:%s',
                transaction_id, transaction_status)
        else:
            GlobalModule.EM_LOGGER.warning(
                '209002 Database Edit Information Error')
        return result

    @staticmethod
    @decorater_log_in_out
    def read_transaction_device_status_list(transaction_id):
        '''
        Method which gets launched from order flow control
        and instructs DB control to read device status management
        information table by Transaction ID.
        Explanation about parameter:
            transaction_id : Transaction ID
        Return value:
            Execution result : boolean(True or False)
            Device status list : tuple
        '''
        result, data = GlobalModule.DB_CONTROL.read_device_status_mgmt_info(
            transaction_id)
        if result:
            if len(data) == 0:
                data = None
            return True, data
        else:
            GlobalModule.EM_LOGGER.warning(
                '209001 Database Get Information Error')
            return False, None

    @staticmethod
    @decorater_log_in_out
    def write_transaction_device_status_list(db_contolorer,
                                             device_name,
                                             transaction_id,
                                             transaction_status=None):
        '''
        Method which gets launched from individual processing for each scenario
        and instructs DB control to write into the device status
        management information table.
        Explanation about parameter:
            db_contolorer:DB control
            device_name:Device name
            transaction_id:Transaction ID
            transaction_status:Transaction status
        Return value:
            Execution result : boolean(True or False)
        '''
        result = GlobalModule.\
            DB_CONTROL.write_device_status_mgmt_info(db_contolorer,
                                                     device_name,
                                                     transaction_id,
                                                     transaction_status)
        if result:
            GlobalModule.EM_LOGGER.debug('Device Name:%s Device Status:%s',
                                         device_name,
                                         transaction_status)
            return True
        else:
            GlobalModule.EM_LOGGER.warning(
                '209002 Database Edit Information Error')
            return False

    @decorater_log_in_out
    def write_em_info(self,
                      db_controlorer,
                      device_name,
                      service_type,
                      ec_message,
                      is_write_force=False):
        '''
        Method which gets launched from common section on driver
        and instructs DB control to read the tables
        that responded to the order type.
        Explanation about parameter:
            device_name:Device name
            service_type:Service type
            order_type:Order type
            ec_message:EC message
        Return value:
            Execution result : boolean
        '''
        add_param = []
        if service_type == self.__service.spine:
            set_db_info_function = self.__set_db_function_info_spine
        elif service_type in (self.__service.leaf, self.__service.b_leaf):
            set_db_info_function = self.__set_db_function_info_leaf
            add_param.append(service_type)
        elif service_type == self.__service.l2_slice:
            set_db_info_function = self.__set_db_function_info_l2_slice
            add_param.append(is_write_force)
        elif service_type == self.__service.l3_slice:
            set_db_info_function = self.__set_db_function_info_l3_slice
            add_param.append(is_write_force)
        elif service_type == self.__service.ce_lag:
            set_db_info_function = self.__set_db_function_info_ce_lag
        elif service_type == self.__service.internal_link:
            set_db_info_function = self.__set_db_function_info_internal_link
        elif service_type == self.__service.cluster_link:
            set_db_info_function = self.__set_db_function_info_cluster_link
        elif service_type == self.__service.breakout:
            set_db_info_function = self.__set_db_function_info_breakout
        elif service_type == self.__service.recover:
            set_db_info_function = self.__set_db_function_info_recover
        elif service_type == self.__service.acl_filter:
            set_db_info_function = self.__set_db_function_info_acl_filter
        else:
            GlobalModule.EM_LOGGER.warning(
                '209002 Database Edit Information Error')
            return False

        try:
            xml_obj = etree.fromstring(ec_message)
            param_set_db = [xml_obj, db_controlorer, device_name]
            param_set_db.extend(add_param)
            funcs, params = set_db_info_function(*param_set_db)

        except Exception, ex_mes:
            GlobalModule.EM_LOGGER.warning(
                '209002 Database Edit Information Error')
            GlobalModule.EM_LOGGER.debug("error_mes = %s" % (ex_mes,))
            return False

        GlobalModule.EM_LOGGER.debug(
            'funcs = %s , params = %s' % (funcs, params))

        is_ok = GlobalModule.DB_CONTROL.write_simultaneous_table(funcs, params)
        if not is_ok:
            GlobalModule.EM_LOGGER.warning(
                '209002 Database Edit Information Error')
        return is_ok

    @staticmethod
    @decorater_log_in_out
    def read_separate_driver_info(device_name):
        '''
        Method which gets launched from common section on driver
        and instructs DB control to read device registration information table.
        Explanation about parameter:
            device_name:Device name
        Return value:
            Execution result : boolean(True or False)
            Information about table read out by DB control.
            (Platform name, OS, Firmware version) : tuple
        '''
        result, data0 = GlobalModule.DB_CONTROL.read_device_regist_info(
            device_name)
        if result:
            if len(data0) == 0:
                return True, None

            platform_name = data0[0]['platform_name']
            os = data0[0]['os']
            firm_version = data0[0]['firm_version']
            data = (platform_name, os, firm_version)
            return True, data
        else:
            GlobalModule.EM_LOGGER.warning(
                '209001 Database Get Information Error')
            return False, None

    @staticmethod
    @decorater_log_in_out
    def read_device_registered_info(device_name):
        '''
        Method which gets launched from common section on driver
        and instructs DB control to read device registration information table.
        Explanation about parameter:
        device_name:Device name
        Return value:
            Execution result : boolean(True or False)
            Information about table read out by DB control : tuple
        '''
        result, data = GlobalModule.DB_CONTROL.read_device_regist_info(
            device_name)
        if result:
            if len(data) == 0:
                data = None
            return True, data
        else:
            GlobalModule.EM_LOGGER.warning(
                '209001 Database Get Information Error')
            return False, None

    @staticmethod
    @decorater_log_in_out
    def write_device_status_list(transaction_id):
        '''
        Method which gets launched from order flow control
       and instructs DB control to request device
       registration information table to delete.
        Explanation about parameter:
            transaction_id:Transaction ID
        Return value:
            Execution result : boolean(True or False)
        '''
        result = (GlobalModule.DB_CONTROL.
                  delete_device_status_mgmt_info_linked_tr_id(transaction_id))
        if not result:
            GlobalModule.EM_LOGGER.warning(
                '209002 Database Edit Information Error')
        return result

    @decorater_log_in_out
    def read_em_info(self, device_name, service_type):
        '''
        Method which gets launched from common section on driver
        and instructs DB control to read the tables corresponding
        to the Service type and Order type.
        Explanation about parameter:
            device_name:Device name
            service_type:Service type
        Return value:
            Execution result : boolean(True or False)
            Information about table read out by DB control : tuple
        '''
        if service_type == self.__service.l3_slice:

            result1, data1 = GlobalModule.DB_CONTROL.read_vrf_detail_info(
                device_name)
            result2, data2 = GlobalModule.DB_CONTROL.read_vlanif_info(
                device_name)
            result3, data3 = GlobalModule\
                .DB_CONTROL.read_static_route_detail_info(device_name)
            result4, data4 = GlobalModule\
                .DB_CONTROL.read_bgp_detail_info(device_name)
            result5, data5 = GlobalModule.DB_CONTROL.read_vrrp_detail_info(
                device_name)
            result6, data6 = GlobalModule.DB_CONTROL.read_vrrp_trackif_info(
                device_name)

            if (result1 and result2 and result3 and
                    result4 and result5 and result6):

                data = (data1, data2, data3, data4, data5, data6)
                data_all =\
                    data1 or data2 or data3 or data4 or data5 or data6
                if len(data_all) == 0:
                    data = None
                return True, data
            else:
                GlobalModule.EM_LOGGER.warning(
                    '209001 Database Get Information Error')
                return False, None

        elif service_type == self.__service.l2_slice:

            result1, data1 = GlobalModule.DB_CONTROL.read_vlanif_info(
                device_name)
            result2, data2 = GlobalModule.DB_CONTROL.read_physical_if_info(
                device_name)
            result3, data3 = GlobalModule.DB_CONTROL.read_dummy_vlan_if_info(
                device_name)
            result4, data4 = GlobalModule.DB_CONTROL.read_vrf_detail_info(
                device_name)
            result5, data5 = GlobalModule.DB_CONTROL.read_multi_homing_info(
                device_name)
            result6, data6 = GlobalModule.DB_CONTROL.read_acl_info(
                device_name)

            if (result1 and result2 and result3 and
                    result4 and result5 and result6):

                data = (data1, data2, data3, data4, data5, data6)
                data_all =\
                    data1 or data2 or data3 or data4 or data5 or data6
                if len(data_all) == 0:
                    data = None
                return True, data
            else:
                GlobalModule.EM_LOGGER.warning(
                    '209001 Database Get Information Error')
                return False, None

        elif service_type == self.__service.spine:

            result1, data1 = GlobalModule.DB_CONTROL.read_device_regist_info(
                device_name)
            result2, data2 = GlobalModule.DB_CONTROL.read_lagif_info(
                device_name)
            result3, data3 = GlobalModule.DB_CONTROL.read_lagmemberif_info(
                device_name)
            result4, data4 = GlobalModule.DB_CONTROL.read_inner_link_if_info(
                device_name)
            result5, data5 = GlobalModule.DB_CONTROL.read_physical_if_info(
                device_name)
            result6, data6 = GlobalModule.DB_CONTROL.read_breakout_if_info(
                device_name)

            if (result1 and result2 and result3 and
                    result4 and result5 and result6):

                data = (data1, data2, data3, data4, data5, data6)
                data_all =\
                    data1 or data2 or data3 or data4 or data5 or data6
                if len(data_all) == 0:
                    data = None
                return True, data
            else:
                GlobalModule.EM_LOGGER.warning(
                    '209001 Database Get Information Error')
                return False, None

        elif service_type in (self.__service.leaf, self.__service.b_leaf):

            result1, data1 = GlobalModule.DB_CONTROL\
                .read_device_regist_info(device_name)
            result2, data2 = GlobalModule.DB_CONTROL.read_lagif_info(
                device_name)
            result3, data3 = GlobalModule.DB_CONTROL.read_lagmemberif_info(
                device_name)
            result4, data4 = GlobalModule.DB_CONTROL.read_inner_link_if_info(
                device_name)
            result5, data5 = GlobalModule.DB_CONTROL.read_physical_if_info(
                device_name)
            result6, data6 = GlobalModule.DB_CONTROL.read_breakout_if_info(
                device_name)
            result7, data7 = GlobalModule.DB_CONTROL\
                .read_leaf_bgp_basic_info(device_name)

            if (result1 and result2 and result3 and
                    result4 and result5 and result6 and result7):

                data = (data1, data2, data3, data4, data5, data6, data7)
                data_all =\
                    data1 or data2 or data3 or data4 or data5 or data6 or data7
                if len(data_all) == 0:
                    data = None
                return True, data
            else:
                GlobalModule.EM_LOGGER.warning(
                    '209001 Database Get Information Error')
                return False, None

        elif service_type == self.__service.ce_lag:

            result1, data1 = GlobalModule.DB_CONTROL.read_lagif_info(
                device_name)
            result2, data2 = GlobalModule.DB_CONTROL.read_lagmemberif_info(
                device_name)
            result3, data3 = GlobalModule.DB_CONTROL.read_physical_if_info(
                device_name)

            if result1 and result2 and result3:

                data = (data1, data2, data3)
                data_all = data1 or data2 or data3
                if len(data_all) == 0:
                    data = None
                return True, data
            else:
                GlobalModule.EM_LOGGER.warning(
                    '209001 Database Get Information Error')
                return False, None

        elif service_type == self.__service.internal_link:

            result1, data1 = GlobalModule.DB_CONTROL.read_lagif_info(
                device_name)
            result2, data2 = GlobalModule.DB_CONTROL.read_lagmemberif_info(
                device_name)
            result3, data3 = GlobalModule.DB_CONTROL.read_physical_if_info(
                device_name)
            result4, data4 = GlobalModule.DB_CONTROL.read_inner_link_if_info(
                device_name)
            result5, data5 = GlobalModule.DB_CONTROL.read_breakout_if_info(
                device_name)

            if result1 and result2 and result3 and result4 and result5:

                data = (data1, data2, data3, data4, data5)
                data_all = data1 or data2 or data3 or data4 or data5
                if len(data_all) == 0:
                    data = None
                return True, data
            else:
                GlobalModule.EM_LOGGER.warning(
                    '209001 Database Get Information Error')
                return False, None

        elif service_type == self.__service.breakout:

            result, data = GlobalModule.DB_CONTROL.read_vlanif_info(
                device_name)

            if result:
                if len(data) == 0:
                    data = None
                return True, data
            else:
                GlobalModule.EM_LOGGER.warning(
                    '209001 Database Get Information Error')
                return False, None

        elif service_type == self.__service.cluster_link:

            result1, data1 = GlobalModule.DB_CONTROL.read_cluster_link_if_info(
                device_name)
            result2, data2 = GlobalModule.DB_CONTROL.read_physical_if_info(
                device_name)

            if (result1 and result2):

                data = (data1, data2)
                data_all = data1 or data2
                if len(data_all) == 0:
                    data = None
                return True, data
            else:
                GlobalModule.EM_LOGGER.warning(
                    '209001 Database Get Information Error')
                return False, None

        elif service_type == self.__service.acl_filter:

            result1, data1 = GlobalModule.DB_CONTROL.read_acl_info(
                device_name)
            result2, data2 = GlobalModule.DB_CONTROL.read_acl_detail_info(
                device_name)

            if (result1 and result2):

                data = (data1, data2)
                data_all = data1 or data2
                if len(data_all) == 0:
                    data = None
                return True, data
            else:
                GlobalModule.EM_LOGGER.warning(
                    '209001 Database Get Information Error')
                return False, None

        else:
            GlobalModule.EM_LOGGER.debug('Service Type Error')
            return False, None

    @staticmethod
    def read_system_status(data_type=GET_DATA_TYPE_MEMORY):
        '''
        Method which gets launched from Netconf server and others,
        instructs DB control to read system status information table.
        Explanation about parameter:
            data_type:original source
        Return value:
            Execution result : boolean(True or False)
            System status
        '''
        ret_status = 0

        if data_type == EmSysCommonUtilityDB.GET_DATA_TYPE_DB:
            result, data = GlobalModule.DB_CONTROL.read_system_status_info()
            if result is True:
                if len(data) == 0:
                    ret_status = 0
                else:
                    dic = data[0]
                    ret_status = dic["service_status"]
                    GlobalModule.EM_LOGGER.debug('ret_status:%s', ret_status)
            else:
                GlobalModule.EM_LOGGER.warning(
                    '209001 Database Get Information Error')
                return False, None

        if data_type == EmSysCommonUtilityDB.GET_DATA_TYPE_MEMORY:
            ret_status = EmStatus.get_em_status()

        return True, ret_status

    @decorater_log_in_out
    def write_system_status(self,
                            db_contolorer,
                            service_status,
                            data_type):
        '''
        Method which gets launched from Netconf server and others,
        instructs DB control and memory to
        write into the system status information table.
        Explanation about parameter:
            db_contolorer,DB control
            system_status:System status
            data_type:Data type（1:DB, 2:Memory, 3:Both)
        Return value:
            Execution result : boolean(True or False)
        '''
        result = True
        if data_type == EmSysCommonUtilityDB.GET_DATA_TYPE_DB or \
                data_type == EmSysCommonUtilityDB.GET_DATA_TYPE_BOTH:

            result = (
                GlobalModule.DB_CONTROL.
                write_system_status_info(db_contolorer,
                                         service_status)
            )

            if result:
                GlobalModule.EM_LOGGER.debug(
                    'Service Status:%s', service_status)
            else:
                GlobalModule.EM_LOGGER.error(
                    '209002 Database Edit Information Error')
                return False

        if data_type == EmSysCommonUtilityDB.GET_DATA_TYPE_MEMORY or \
                data_type == EmSysCommonUtilityDB.GET_DATA_TYPE_BOTH:

            EmStatus.set_em_status(service_status)

        return result

    @decorater_log
    def __set_db_function_info_spine(self, ec_mes, db_control, device_name):
        '''
        Analyze the EC message, create method list and
        method parameter to be executed by DB control.
        Explanation about parameter:
            ec_mes:EC message
            db_control:EC message
            device_name:EC message
        Return value:
            Method list   : list
            Parameter list : list
         '''
        func_list = []
        param_list = []

        service = self.__service.spine

        tmp_func, tmp_param = (
            self.__get_func_device_regist_info(ec_mes, db_control, service))
        func_list.extend(tmp_func)
        param_list.extend(tmp_param)
        if db_control == self.__db_delete:
            tmp_func, tmp_param = self.__get_func_all_del_lag(ec_mes, service)
        else:
            tmp_func, tmp_param = (
                self.__get_func_lagif_info(
                    ec_mes, db_control, self.__service.internal_link, service))
        func_list.extend(tmp_func)
        param_list.extend(tmp_param)

        tmp_func, tmp_param = (
            self.__get_func_inner_link_info(ec_mes, db_control, service))
        func_list.extend(tmp_func)
        param_list.extend(tmp_param)
        tmp_func, tmp_param = (
            self.__get_func_breakoutif_info(ec_mes, db_control, service))
        func_list.extend(tmp_func)
        param_list.extend(tmp_param)

        if db_control == self.__db_delete:
            func_list.reverse()
            param_list.reverse()

        return func_list, param_list

    @decorater_log
    def __set_db_function_info_leaf(self, ec_mes,
                                    db_control,
                                    device_name,
                                    service):
        '''
        Analyze the EC message, create method list and
        method parameter to be executed by DB control. (Leaf)
        Explanation about parameter:
            ec_mes:EC message
            db_control:EC message
            device_name:EC message
            service_type:Device type
        Return value:
            Method list   : list
            Parameter list : list
         '''
        func_list = []
        param_list = []

        name_s = "{%s}" % (self._namespace.get(service),)
        if service == self.__service.b_leaf and \
                db_control == self.__db_delete:
            if ec_mes.find(name_s + "ospf"):
                db_control = "UPDATE"

        tmp_func, tmp_param = (
            self.__get_func_device_regist_info(ec_mes, db_control, service))
        func_list.extend(tmp_func)
        param_list.extend(tmp_param)

        if db_control == self.__db_delete:
            tmp_func, tmp_param = self.__get_func_all_del_lag(ec_mes, service)
        else:
            tmp_func, tmp_param = (
                self.__get_func_lagif_info(
                    ec_mes, db_control, self.__service.internal_link, service))
        func_list.extend(tmp_func)
        param_list.extend(tmp_param)

        tmp_func, tmp_param = (
            self.__get_func_leaf_bgp_basic_info(ec_mes,
                                                db_control,
                                                service))
        func_list.extend(tmp_func)
        param_list.extend(tmp_param)

        tmp_func, tmp_param = (
            self.__get_func_inner_link_info(ec_mes, db_control, service))
        func_list.extend(tmp_func)
        param_list.extend(tmp_param)

        tmp_func, tmp_param = (
            self.__get_func_breakoutif_info(ec_mes, db_control, service))
        func_list.extend(tmp_func)
        param_list.extend(tmp_param)

        if db_control == self.__db_delete:
            func_list.reverse()
            param_list.reverse()

        return func_list, param_list

    @decorater_log
    def __set_db_function_info_l2_slice(self,
                                        ec_mes,
                                        db_control,
                                        device_name,
                                        is_write_force=False):
        '''
        Analyze the EC message, create method list and
        method parameter to be executed by DB control. (L2Slice)
        Explanation about parameter:
            ec_mes:EC message
            db_control:EC message
            device_name:EC message
        Return value:
            Method list   : list
            Parameter list : list
         '''
        func_list = []
        param_list = []

        service = self.__service.l2_slice

        is_replace = self.__get_judge_replace(ec_mes, service, "cp")

        if db_control == self.__db_delete:
            tmp_func, tmp_param = (
                self.__get_func_l2_del(ec_mes,  service, is_write_force))
        elif is_replace:
            tmp_func, tmp_param = (
                self.__get_func_l2_replace(ec_mes, db_control, service))
        else:
            tmp_func, tmp_param = (
                self.__get_func_vlanif_info(ec_mes, db_control, service))
        func_list.extend(tmp_func)
        param_list.extend(tmp_param)

        if db_control == self.__db_delete:
            func_list.reverse()
            param_list.reverse()

        return func_list, param_list

    @decorater_log
    def __set_db_function_info_l3_slice(self,
                                        ec_mes,
                                        db_control,
                                        device_name,
                                        is_write_force=False):
        '''
        Analyze the EC message, create method list and
        method parameter to be executed by DB control. (L3Slice)
        Explanation about parameter:
            ec_mes:EC message
            db_control:EC message
            device_name:EC message
        Return value:
            Method list   : list
            Parameter list : list
         '''
        func_list = []
        param_list = []

        service = self.__service.l3_slice

        is_replace = self.__get_judge_replace(ec_mes, service, "cp")

        if db_control == self.__db_delete:
            tmp_func, tmp_param = (
                self.__get_func_l3_del(ec_mes, service, is_write_force))
        elif is_replace:
            tmp_func, tmp_param = (
                self.__get_func_l3_replace(ec_mes, db_control, service))
        else:
            tmp_func, tmp_param = (
                self.__get_func_vlanif_info(ec_mes, db_control, service))
        func_list.extend(tmp_func)
        param_list.extend(tmp_param)

        if db_control == self.__db_delete:
            func_list.reverse()
            param_list.reverse()

        return func_list, param_list

    @decorater_log
    def __set_db_function_info_ce_lag(self,
                                      ec_mes,
                                      db_control,
                                      device_name):
        '''
        Analyze the EC message, create method list and
        method parameter to be executed by DB control. (CE_Lag)
        Explanation about parameter:
            ec_mes:EC message
            db_control:EC message
            device_name:EC message
        Return value:
            Method list   : list
            Parameter list : list
         '''
        func_list = []
        param_list = []

        service = self.__service.ce_lag

        tmp_func, tmp_param = (
            self.__get_func_lagif_info(ec_mes, db_control, service, service))
        func_list.extend(tmp_func)
        param_list.extend(tmp_param)

        if db_control == self.__db_delete:
            func_list.reverse()
            param_list.reverse()

        return func_list, param_list

    @decorater_log
    def __set_db_function_info_internal_link(self,
                                             ec_mes,
                                             db_control,
                                             device_name):
        '''
        Analyze the EC message, create method list and
        method parameter to be executed by DB control. (Internal_Link)
        Explanation about parameter:
            ec_mes:EC message
            db_control:EC message
            device_name:EC message
        Return value:
            Method list   : list
            Parameter list : list
         '''
        func_list = []
        param_list = []

        service = self.__service.internal_link
        db_vpn_type = {"l2": 2,
                       "l3": 3}

        leaf_device_type = 2

        is_replace = self.__get_judge_replace(
            ec_mes, service, "internal-interface")
        if is_replace:
            tmp_func, tmp_param = (
                self.__get_func_internal_link_replace(
                    ec_mes, db_control, service))
            func_list.extend(tmp_func)
            param_list.extend(tmp_param)
        else:
            tmp_func, tmp_param = (
                self.__get_func_lagif_info(ec_mes, db_control,
                                           service, service))
            func_list.extend(tmp_func)
            param_list.extend(tmp_param)

            ok, dev_regist = (
                GlobalModule.DB_CONTROL.read_device_regist_info(device_name))
            if not (ok and len(dev_regist) > 0):
                raise ValueError(
                    "failed get to dev_regist_info at %s" % (device_name,))
            if (db_control != self.__db_delete and
                    dev_regist[0].get("device_type") == leaf_device_type):
                name_s = "{%s}" % (self._namespace.get(service),)
                tmp_reg = dev_regist[0].copy()
                if ec_mes.find(name_s + "vpn-type") is not None:
                    vpn_type = ec_mes.find(name_s + "vpn-type").text.lower()
                    tmp_reg["vpn_type"] = db_vpn_type[vpn_type]
                    tmp_reg["db_control"] = "UPDATE"
                    func_list.append(
                        GlobalModule.DB_CONTROL.write_device_regist_info)
                    param_list.append(tmp_reg)

            tmp_func, tmp_param = (
                self.__get_func_inner_link_info(ec_mes, db_control, service))
            func_list.extend(tmp_func)
            param_list.extend(tmp_param)

            tmp_func, tmp_param = (
                self.__get_func_breakoutif_info(ec_mes, db_control, service))
            func_list.extend(tmp_func)
            param_list.extend(tmp_param)

        if db_control == self.__db_delete:
            func_list.reverse()
            param_list.reverse()

        return func_list, param_list

    @decorater_log
    def __set_db_function_info_cluster_link(self,
                                            ec_mes,
                                            db_control,
                                            device_name):
        '''
        Analyze the EC message, create method list and
        method parameter to be executed by DB control. (Cluster_Link)
        Explanation about parameter:
            ec_mes:EC message
            db_control:EC message
            device_name:EC message
        Return value:
            Method list   : list
            Parameter list : list
         '''
        func_list = []
        param_list = []

        service = self.__service.cluster_link

        tmp_func, tmp_param = (
            self.__get_func_cluster_linkif_info(ec_mes, db_control, service))
        func_list.extend(tmp_func)
        param_list.extend(tmp_param)

        if db_control == self.__db_delete:
            func_list.reverse()
            param_list.reverse()

        return func_list, param_list

    @decorater_log
    def __set_db_function_info_breakout(self,
                                        ec_mes,
                                        db_control,
                                        device_name):
        '''
        Analyze the EC message, create method list and
        method parameter to be executed by DB control. (BreakoutIF)
        Explanation about parameter:
            ec_mes:EC message
            db_control:EC message
            device_name:EC message
        Return value:
            Method list   : list
            Parameter list : list
         '''
        func_list = []
        param_list = []

        service = self.__service.breakout

        tmp_func, tmp_param = (
            self.__get_func_breakoutif_info(ec_mes, db_control, service))
        func_list.extend(tmp_func)
        param_list.extend(tmp_param)

        if db_control == self.__db_delete:
            func_list.reverse()
            param_list.reverse()

        return func_list, param_list

    @decorater_log
    def __set_db_function_info_recover(self,
                                       ec_mes,
                                       db_control,
                                       device_name):
        '''
        Analyze the EC message, create method list and
        method parameter to be executed by DB control. (Recover)
        Explanation about parameter:
            ec_mes:EC message
            db_control:EC message
            device_name:EC message
        Return value:
            Method list   : list
            Parameter list : list
         '''
        func_list = []
        param_list = []

        service = self.__service.recover

        tmp_func, tmp_param = (
            self.__get_func_recover_info(ec_mes, db_control, service))
        func_list.extend(tmp_func)
        param_list.extend(tmp_param)

        return func_list, param_list

    @decorater_log
    def __set_db_function_info_acl_filter(self,
                                          ec_mes,
                                          db_control,
                                          device_name):
        '''
        Analyze the EC message, create method list and
        method parameter to be executed by DB control.
        (ACL configuration)
        Explanation about parameter:
            ec_mes:EC message
            db_control:EC message
            device_name:EC message
        Return value:
            Method list   : list
            Parameter list : list
         '''
        func_list = []
        param_list = []

        service = self.__service.acl_filter

        tmp_func, tmp_param, acl_detail_param = (
            self.__get_func_acl_info(ec_mes, db_control, service))
        func_list.extend(tmp_func)
        param_list.extend(tmp_param)
        if db_control == self.__db_delete:
            acl_del_func_list = []
            acl_del_param_list = []
            device_name = tmp_param[0]["device_name"]
            GlobalModule.EM_LOGGER.debug(device_name)
            if not self._check_acl_detail_all_del(device_name,
                                                  acl_detail_param):
                acl_del_param_list.extend(acl_detail_param)
                for i in acl_del_param_list:
                    acl_del_func_list.append(
                        GlobalModule.DB_CONTROL.write_acl_detail_info)
                return acl_del_func_list, acl_del_param_list
            func_list.reverse()
            param_list.reverse()
        return func_list, param_list

    @decorater_log
    def __get_param(self, node, tag, val_class):
        '''
        Search the tag in node object,
        convert its text into val_class and return.
        Explanation about parameter:
            node:Node object
            tag:Tag name
            val_class:After conversion type
        Return value:
           Parameter for function  : val_class's object or None
         '''
        return_val = None
        if node is not None:
            node_tag = node.find(tag)
            if node_tag is not None:
                return_val = self.__parse(node_tag.text, val_class)
        return return_val

    @staticmethod
    @decorater_log
    def __parse(value, val_class):
        '''
        Convert the value in EC message to val_class format.
        Explanation about parameter:
            value:Value to input
            val_class:After conversion type
        Return value:
            Converted value  : val_class's object or None
         '''
        return_val = None
        if value is not None:
            try:
                return_val = val_class(value)
            except ValueError:
                raise
        return return_val

    @decorater_log
    def __get_judge_replace(self, ec_mes, service, search_tag):
        '''
        Analyze EC message, make judgment
        on whether operation="replace" has been set.
        Explanation about parameter:
            ec_mes:EC message
            service:Service type (str)
            search_tag:Tag name (str) to be searched
        Return value:
            True or False
         '''
        name_s = "{%s}" % (self._namespace.get(service),)

        for node in ec_mes.findall(name_s + search_tag):
            if node.get("operation") == "replace":
                return True
        return False

    @decorater_log
    def __get_func_device_regist_info(self, dev_node, db_control, dev_type):
        '''
        Create parameter for write_device_regist_info based on device node.
        Explanation about parameter:
            dev_node : Device node (xml object)
            db_control : DB control (str)
            dev_type : Device type (str)
        Return value:
            Method list   : list
            Parameter list : list
         '''
        name_s = "{%s}" % (self._namespace.get(dev_type),)

        regist_param = dict.fromkeys(["db_control",
                                      "device_name",
                                      "device_type",
                                      "platform_name",
                                      "os",
                                      "firm_version",
                                      "username",
                                      "password",
                                      "mgmt_if_address",
                                      "mgmt_if_prefix",
                                      "loopback_if_address",
                                      "loopback_if_prefix",
                                      "snmp_server_address",
                                      "snmp_community",
                                      "ntp_server_address",
                                      "as_number",
                                      "pim_other_rp_address",
                                      "pim_self_rp_address",
                                      "pim_rp_address",
                                      "vpn_type",
                                      "virtual_link_id",
                                      "ospf_range_area_address",
                                      "ospf_range_area_prefix",
                                      "cluster_ospf_area",
                                      "rr_loopback_address",
                                      "rr_loopback_prefix",
                                      "irb_type"])
        db_dev_type = {self.__service.spine: 1,
                       self.__service.leaf: 2,
                       self.__service.b_leaf: 2}

        func_list = []
        param_list = []

        regist_param["db_control"] = db_control

        regist_param["device_type"] = db_dev_type.get(dev_type)

        device_name = self.__get_param(dev_node, name_s + "name", str)
        regist_param["device_name"] = device_name

        is_ok, db_device_regist = \
            GlobalModule.DB_CONTROL.read_device_regist_info(device_name)
        if not is_ok:
            err_mes = ('DB Fault read_device_regist_info(device_name = %s)' %
                       (device_name,))
            GlobalModule.EM_LOGGER.debug(err_mes)
            raise ValueError("DB Control ERROR")

        ospf_node = dev_node.find(name_s + "ospf")

        db_exist = False
        for device_regist in db_device_regist:
            if device_regist["device_name"] == device_name:
                tmp_device_regist = device_regist
                db_exist = True
                break

        if not db_exist:
            GlobalModule.EM_LOGGER.debug(
                'Not exist %s in DB. Start registration of the device.',
                (device_name,))
        elif db_exist and (ospf_node is None):
            GlobalModule.EM_LOGGER.debug(
                'Exist %s in DB. Start deleting registration of the device.',
                (device_name,))
        elif db_exist and (ospf_node is not None):
            GlobalModule.EM_LOGGER.debug(
                'Exist %s in DB. Start updating registration of the device.',
                (device_name,))
            regist_param.update(tmp_device_regist)

        node_1 = dev_node.find(name_s + "equipment")
        if node_1 is not None:
            regist_param["platform_name"] = (
                self.__get_param(node_1, name_s + "platform", str))
            regist_param["os"] = (
                self.__get_param(node_1, name_s + "os", str))
            regist_param["firm_version"] = (
                self.__get_param(node_1, name_s + "firmware", str))
            regist_param["username"] = (
                self.__get_param(node_1, name_s + "loginid", str))
            regist_param["password"] = (
                self.__get_param(node_1, name_s + "password", str))

        node_1 = dev_node.find(name_s + "management-interface")
        if node_1 is not None:
            regist_param["mgmt_if_address"] = (
                self.__get_param(node_1, name_s + "address", str))
            regist_param["mgmt_if_prefix"] = (
                self.__get_param(node_1, name_s + "prefix", int))

        node_1 = dev_node.find(name_s + "loopback-interface")
        if node_1 is not None:
            regist_param["loopback_if_address"] = (
                self.__get_param(node_1, name_s + "address", str))
            regist_param["loopback_if_prefix"] = (
                self.__get_param(node_1, name_s + "prefix", int))

        node_1 = dev_node.find(name_s + "snmp")
        if node_1 is not None:
            regist_param["snmp_server_address"] = (
                self.__get_param(node_1, name_s + "server-address", str))
            regist_param["snmp_community"] = (
                self.__get_param(node_1, name_s + "community", str))

        node_1 = dev_node.find(name_s + "ntp")
        if node_1 is not None:
            regist_param["ntp_server_address"] = (
                self.__get_param(node_1, name_s + "server-address", str))

        if dev_node.find(name_s + "l3-vpn") is not None:
            node_1 = dev_node.find(name_s + "l3-vpn").find(name_s + "as")
            regist_param["as_number"] = (
                self.__get_param(node_1, name_s + "as-number", int))
            regist_param["vpn_type"] = 3

        if dev_node.find(name_s + "l2-vpn") is not None:
            node_1 = dev_node.find(name_s + "l2-vpn").find(name_s + "as")
            regist_param["as_number"] = (
                self.__get_param(node_1, name_s + "as-number", int))
            regist_param["vpn_type"] = 2

        node_1 = dev_node.find(name_s + "ospf")
        if node_1 is not None:
            regist_param["cluster_ospf_area"] = (
                self.__get_param(node_1, name_s + "area-id", str))

            virtual_link = node_1.find(name_s + "virtual-link")
            ospf_range = node_1.find(name_s + "range")
            if virtual_link is not None:
                if (virtual_link.get("operation") == "replace") or \
                        (virtual_link.get("operation") == "delete"):
                    regist_param["virtual_link_id"] = None
                else:
                    regist_param["virtual_link_id"] = self.__get_param(
                        virtual_link, name_s + "router-id", str)
            if ospf_range is not None:
                if ospf_range.get("operation") == "delete":
                    regist_param["ospf_range_area_address"] = None
                    regist_param["ospf_range_area_prefix"] = None
                else:
                    regist_param["ospf_range_area_address"] = self.__get_param(
                        ospf_range, name_s + "address", str)
                    regist_param["ospf_range_area_prefix"] = self.__get_param(
                        ospf_range, name_s + "prefix", int)

        func_list.append(GlobalModule.DB_CONTROL.write_device_regist_info)
        param_list.append(regist_param)
        return func_list, param_list

    @decorater_log
    def __get_func_lagif_info(self, dev_node, db_control, lag_type, service):
        '''
        Create parameters for write_lagif_info, write_lagmemberif_info
        and write_physical_if_info based on device node.
        Explanation about parameter:
            dev_node : Device node (xml object)
            db_control : DB control (str)
            lag_type : LAG type (str)
            service : Service type (str)
        Return value:
            Method list   : list
            Parameter list : list
         '''
        name_s = "{%s}" % (self._namespace.get(service),)

        db_lag_type = {self.__service.ce_lag: 2,
                       self.__service.internal_link: 1}
        lag_if_node_tag = {self.__service.ce_lag: "ce-lag-interface",
                           self.__service.internal_link: "internal-interface"}
        lag_mem_node_tag = {self.__service.ce_lag: "leaf-interface",
                            self.__service.internal_link: "internal-interface"}

        func_list = []
        param_list = []

        device_name = self.__get_param(dev_node, name_s + "name", str)

        if_counts = {}
        if db_control == self.__db_delete:
            is_ok, db_lag_mem = \
                GlobalModule.DB_CONTROL.read_lagmemberif_info(device_name)
            if not is_ok:
                err_mes = ('DB Fault read_lagmem(device_name = %s)' %
                           (device_name,))
                GlobalModule.EM_LOGGER.debug(err_mes)
                raise ValueError("DB Control ERROR")
            for lag_mem in db_lag_mem:
                if lag_mem["lag_if_name"] in if_counts:
                    if_counts[lag_mem["lag_if_name"]] += 1
                else:
                    if_counts[lag_mem["lag_if_name"]] = 1

        lag_if_nodes = dev_node.findall(name_s +
                                        lag_if_node_tag.get(
                                            lag_type, "none-interface"))

        for lag_if_node in lag_if_nodes:
            if_type = lag_if_node.find(name_s + "type")

            if (if_type is not None and if_type.text == "lag-if") or\
                    lag_type == self.__service.ce_lag:

                lagif_param = dict.fromkeys(["db_control",
                                             "device_name",
                                             "lag_if_name",
                                             "lag_type",
                                             "lag_if_id",
                                             "minimum_links",
                                             "link_speed"])
                lagif_param["db_control"] = db_control
                lagif_param["device_name"] = device_name
                lag_if_name = self.__get_param(
                    lag_if_node, name_s + "name", str)
                lagif_param["lag_if_name"] = lag_if_name
                lagif_param["lag_type"] = db_lag_type.get(lag_type)
                lagif_param["lag_if_id"] = (
                    self.__get_param(lag_if_node, name_s + "lag-id", int))
                lagif_param["minimum_links"] = (
                    self.__get_param(lag_if_node, name_s + "minimum-links",
                                     int))
                lagif_param["link_speed"] = (
                    self.__get_param(lag_if_node, name_s + "link-speed", str))

                if_nodes = lag_if_node.findall(name_s +
                                               lag_mem_node_tag.get(
                                                   lag_type, "none-interface"))

                if db_control != self.__db_delete and len(if_nodes) == 0:
                    err_mes = (
                        'Fault Interface node do not find(lag_name = %s)'
                        % (lag_if_name,))
                    GlobalModule.EM_LOGGER.debug(err_mes)
                    raise ValueError("Interface node do not find")

                if (db_control != self.__db_delete or
                        if_nodes[0].text is None or
                        len(if_nodes) == if_counts.get(lag_if_name)):
                    func_list.append(
                        GlobalModule.DB_CONTROL.write_lagif_info)
                    param_list.append(lagif_param)

                for if_node in if_nodes:
                    self.__set_physicalif_param(func_list,
                                                param_list,
                                                name_s,
                                                db_control,
                                                device_name,
                                                node=if_node)
                    self.__set_lagmemberif_param(func_list,
                                                 param_list,
                                                 name_s,
                                                 db_control,
                                                 device_name,
                                                 node=if_node,
                                                 lag_if_name=lag_if_name)
            else:
                self.__set_physicalif_param(func_list,
                                            param_list,
                                            name_s,
                                            db_control,
                                            device_name,
                                            node=lag_if_node)

        return func_list, param_list

    @decorater_log
    def __set_lagmemberif_param(self,
                                func_list,
                                param_list,
                                name_s,
                                db_control,
                                device_name,
                                node=None,
                                lag_if_name=None):
        '''
        Create parameter for write_lagmemberif_info.
        Explanation about parameter:
            func_list : Method list (list)
            param_list : Parameter list (list)
            name_s : Name space (str)
            db_control : DB control (str)
            device_name : Device name (str)
            node : Node (xml object)
            lag_if_name : LAG IF name(str)
        '''

        lagmemberif_param = dict.fromkeys(["db_control",
                                           "lag_if_name",
                                           "if_name",
                                           "device_name"])

        lagmemberif_param["db_control"] = db_control

        lagmemberif_param["device_name"] = device_name
        lagmemberif_param["lag_if_name"] = lag_if_name
        if node is not None:
            lagmemberif_param["if_name"] = (
                self.__get_param(node, name_s + "name", str))
        func_list.append(GlobalModule.DB_CONTROL.write_lagmemberif_info)
        param_list.append(lagmemberif_param)

    @decorater_log
    def __get_func_leaf_bgp_basic_info(self,
                                       dev_node,
                                       db_control,
                                       service):
        '''
        Create parameter for write_leaf_bgp_basic_info based on device node.
        Explanation about parameter:
            dev_node : Device node (xml object)
            db_control : DB control (str)
            service : Service type (str)
        Return value:
            Method list   : list
            Parameter list : list
        '''
        name_s = "{%s}" % (self._namespace.get(service),)

        func_list = []
        param_list = []

        device_name = self.__get_param(dev_node, name_s + "name", str)

        if (dev_node.find(name_s + "equipment") is not None) or \
                db_control == self.__db_delete:

            res_vpn_type = False

            if (dev_node.find(name_s + "l3-vpn") is not None):
                node_1 = dev_node.find(name_s + "l3-vpn").find(name_s + "bgp")
                res_vpn_type = True
            elif (dev_node.find(name_s + "l2-vpn") is not None):
                node_1 = dev_node.find(name_s + "l2-vpn").find(name_s + "bgp")
                res_vpn_type = True

            if res_vpn_type:
                community = self.__get_param(node_1, name_s + "community", str)
                wildcard = self.__get_param(
                    node_1, name_s + "community-wildcard", str)
                neighbor_nodes = node_1.findall(name_s + "neighbor")
                for neighbor_node in neighbor_nodes:
                    self.__set_leaf_bgp_param(func_list,
                                              param_list,
                                              name_s,
                                              db_control,
                                              device_name,
                                              community=community,
                                              wildcard=wildcard,
                                              node=neighbor_node)
            else:
                self.__set_leaf_bgp_param(func_list,
                                          param_list,
                                          name_s,
                                          db_control,
                                          device_name)

        return func_list, param_list

    @decorater_log
    def __set_leaf_bgp_param(self,
                             func_list,
                             param_list,
                             name_s,
                             db_control,
                             device_name,
                             community=None,
                             wildcard=None,
                             node=None):
        '''
        Create parameter for write_leaf_bgp_basic_info.
        Explanation about parameter:
            func_list : Method list (list)
            param_list : Parameter list (list)
            name_s : Name space (str)
            db_control : DB control (str)
            device_name : Device name (str)
            community : BGP's community value (str)
            wildcard : Expression which includes the community value,
                       both priority on BGP and not. (str)
            node : Node (xml object)
        '''
        vpn_param = dict.fromkeys(["db_control",
                                   "device_name",
                                   "neighbor_ipv4",
                                   "bgp_community_value",
                                   "bgp_community_wildcard"])

        vpn_param["db_control"] = db_control
        vpn_param["device_name"] = device_name
        if node is not None and db_control != self.__db_delete:
            vpn_param["neighbor_ipv4"] = (
                self.__get_param(node, name_s + "address", str))
            vpn_param["bgp_community_value"] = community
            vpn_param["bgp_community_wildcard"] = wildcard

        func_list.append(
            GlobalModule.DB_CONTROL.write_leaf_bgp_basic_info)
        param_list.append(vpn_param)

    @decorater_log
    def __get_func_vlanif_info(self,
                               dev_node,
                               db_control,
                               slice_type):
        '''
        Create parameter for write_vlanif_info based on device node.
        Explanation about parameter:
            dev_node : Device node (xml object)
            db_control : DB control (str)
            slice_type : Slice type (str)
        Return value:
            Method list   : list
            Parameter list : list
        '''
        name_s = "{%s}" % (self._namespace.get(slice_type),)

        db_slice_type = {self.__service.l2_slice: 2,
                         self.__service.l3_slice: 3}

        db_port_mode = {"access": 1, "trunk": 2}

        func_list = []
        param_list = []
        vrf_param = None

        device_name = self.__get_param(dev_node, name_s + "name", str)

        slice_name = self.__get_param(dev_node, name_s + "slice_name", str)
        if self.__service.l3_slice or (
                dev_node.find(name_s + "vrf") is not None):
            tmp_node = dev_node.find(name_s + "vrf")
            vrf_name = self.__get_param(tmp_node, name_s + "vrf-name", str)
            vrf_rt = self.__get_param(tmp_node, name_s + "rt", str)
            vrf_rd = self.__get_param(tmp_node, name_s + "rd", str)
            vrf_route_id = (
                self.__get_param(tmp_node, name_s + "router-id", str))
        tmp_func_list = []
        tmp_param_list = []

        for cp_node in dev_node.findall(name_s + "cp"):
            if cp_node.find(name_s + "port-mode") is None and \
                    (slice_type == self.__service.l2_slice):
                ok, db_vlan_info = GlobalModule.DB_CONTROL.read_vlanif_info(
                    device_name)
                if not ok:
                    err_mes = ('DB Fault read_vlanif_info(device_name = %s)' %
                               (device_name,))
                    GlobalModule.EM_LOGGER.debug(err_mes)
                    raise ValueError("DB Control ERROR")
                if_name = self.__get_param(cp_node, name_s + "name", str)
                vlan_id = self.__get_param(cp_node, name_s + "vlan-id", int)
                cp_param = self.__get_key_recode(db_vlan_info,
                                                 device_name=device_name,
                                                 if_name=if_name,
                                                 vlan_id=vlan_id,
                                                 slice_name=slice_name)

                self._change_multi(
                    cp_node, name_s, slice_name, device_name, cp_param)
                cp_param["db_control"] = ("UPDATE")
                cp_param["esi"] = self.__get_param(
                    cp_node, name_s + "esi", str)
                cp_param["system_id"] = self.__get_param(
                    cp_node, name_s + "system-id", str)
                cp_param["clag_id"] = self.__get_param(
                    cp_node, name_s + "clag-id", int)
                func_list.append(
                    GlobalModule.DB_CONTROL.write_vlanif_info)
                param_list.append(cp_param)
                continue

            cp_param = dict.fromkeys(["db_control",
                                      "device_name",
                                      "if_name",
                                      "vlan_id",
                                      "slice_name",
                                      "slice_type",
                                      "port_mode",
                                      "vni",
                                      "multicast_group",
                                      "ipv4_address",
                                      "ipv4_prefix",
                                      "ipv6_address",
                                      "ipv6_prefix",
                                      "bgp_flag",
                                      "ospf_flag",
                                      "static_flag",
                                      "direct_flag",
                                      "vrrp_flag",
                                      "mtu_size",
                                      "metric",
                                      "esi",
                                      "system_id",
                                      "inflow_shaping_rate",
                                      "outflow_shaping_rate",
                                      "remark_menu",
                                      "egress_queue_menu",
                                      "clag_id",
                                      "speed",
                                      "irb_ipv4_address",
                                      "irb_ipv4_prefix",
                                      "virtual_mac_address",
                                      "virtual_gateway_address",
                                      "virtual_gateway_prefix"])
            cp_param["db_control"] = db_control
            cp_param["device_name"] = device_name
            cp_param["slice_name"] = slice_name
            cp_param["slice_type"] = db_slice_type.get(slice_type)
            cp_param["if_name"] = (
                self.__get_param(cp_node, name_s + "name", str))
            cp_param["vlan_id"] = (
                self.__get_param(cp_node, name_s + "vlan-id", int))

            qos_info = cp_node.find(name_s + "qos")
            if qos_info is not None:

                self.__set_qos_param(qos_info,
                                     name_s,
                                     db_control,
                                     cp_param)

            is_ok, lag_data = GlobalModule.DB_CONTROL.read_lagif_info(
                device_name)
            if not is_ok:
                err_mes = ('DB Fault read_lagif_info(device_name = %s)' %
                           (device_name,))
                GlobalModule.EM_LOGGER.debug(err_mes)
                raise ValueError("DB Control ERROR")

            is_if_name = False
            for data in lag_data:
                if (data["device_name"] == device_name and
                        data["lag_if_name"] == cp_param["if_name"]):
                    is_if_name = True
                    break

            if not is_if_name:
                self.__set_physicalif_param(tmp_func_list,
                                            tmp_param_list,
                                            name_s,
                                            db_control,
                                            device_name,
                                            node=cp_node)
            if slice_type == self.__service.l2_slice:
                tmp = self.__get_param(cp_node, name_s + "port-mode", str)
                port_mode_data = (
                    db_port_mode.get(tmp.lower()) if tmp else None)
                vni_data = self.__get_param(cp_node, name_s + "vni", int)
                clag_id = self.__get_param(cp_node, name_s + "clag-id", int)
                if dev_node.find(name_s + "vrf") is not None:
                    if_name = cp_param["if_name"]
                    vlan_id = cp_param["vlan_id"]
                    db_control_merge = "INSERT"
                    vrf_param = self.__set_l2_vrf_param(
                        name_s,
                        db_control_merge,
                        device_name,
                        slice_name,
                        if_name,
                        vlan_id,
                        dev_node)
                cp_param["port_mode"] = port_mode_data
                cp_param["vni"] = vni_data
                cp_param["esi"] = self.__get_param(
                    cp_node, name_s + "esi", str)
                cp_param["system_id"] = self.__get_param(
                    cp_node, name_s + "system-id", str)
                cp_param["clag_id"] = clag_id
                cp_param["speed"] = self.__get_param(
                    cp_node, name_s + "speed", str)
                irb_info = cp_node.find(name_s + "irb")
                if irb_info is not None:
                    self.__set_irb_param(irb_info,
                                         name_s,
                                         db_control,
                                         cp_param)

                tmp_func_list.append(
                    GlobalModule.DB_CONTROL.write_vlanif_info)
                tmp_param_list.append(cp_param)
                if vrf_param is not None:
                    tmp_func_list.append(
                        GlobalModule.DB_CONTROL.write_vrf_detail_info)
                    tmp_param_list.append(vrf_param)

            if slice_type == self.__service.l3_slice:
                vrf_param = dict.fromkeys(["db_control",
                                           "device_name",
                                           "if_name",
                                           "vlan_id",
                                           "slice_name",
                                           "vrf_name",
                                           "rt",
                                           "rd",
                                           "router_id"])
                vrf_param["db_control"] = db_control
                vrf_param["device_name"] = device_name
                vrf_param["slice_name"] = slice_name
                vrf_param["if_name"] = cp_param["if_name"]
                vrf_param["vlan_id"] = cp_param["vlan_id"]
                vrf_param["vrf_name"] = vrf_name
                vrf_param["rt"] = vrf_rt
                vrf_param["rd"] = vrf_rd
                vrf_param["router_id"] = vrf_route_id
                tmp_func_list.append(
                    GlobalModule.DB_CONTROL.write_vrf_detail_info)
                tmp_param_list.append(vrf_param)

                tmp_node = cp_node.find(name_s + "ce-interface")
                cp_param["ipv4_address"] = (
                    self.__get_param(tmp_node, name_s + "address", str))
                cp_param["ipv4_prefix"] = (
                    self.__get_param(tmp_node, name_s + "prefix", int))
                cp_param["ipv6_address"] = (
                    self.__get_param(tmp_node, name_s + "address6", str))
                cp_param["ipv6_prefix"] = (
                    self.__get_param(tmp_node, name_s + "prefix6", int))
                cp_param["mtu_size"] = self.__get_param(
                    tmp_node, name_s + "mtu", int)

                cp_param["ospf_flag"] = False
                if cp_node.find(name_s + "ospf") is not None:
                    cp_param["ospf_flag"] = True
                    cp_param["metric"] = (
                        self.__get_param(cp_node.find(name_s + "ospf"),
                                         name_s + "metric", int))

                cp_param["vrrp_flag"] = False
                if cp_node.find(name_s + "vrrp")is not None:
                    cp_param["vrrp_flag"] = True
                    self.__set_vrrp_param(tmp_func_list,
                                          tmp_param_list,
                                          cp_node.find(name_s + "vrrp"),
                                          name_s,
                                          db_control,
                                          device_name,
                                          slice_name,
                                          cp_param["if_name"],
                                          cp_param["vlan_id"])

                cp_param["bgp_flag"] = False
                if cp_node.find(name_s + "bgp") is not None:
                    cp_param["bgp_flag"] = True
                    self.__set_bgp_param(tmp_func_list,
                                         tmp_param_list,
                                         cp_node.find(name_s + "bgp"),
                                         name_s,
                                         db_control,
                                         device_name,
                                         slice_name,
                                         cp_param["if_name"],
                                         cp_param["vlan_id"])

                cp_param["static_flag"] = False
                if cp_node.find(name_s + "static") is not None:
                    cp_param["static_flag"] = True
                    self.__set_static_param(tmp_func_list,
                                            tmp_param_list,
                                            cp_node.find(name_s + "static"),
                                            name_s,
                                            db_control,
                                            device_name,
                                            slice_name,
                                            cp_param["if_name"],
                                            cp_param["vlan_id"])

                cp_param["direct_flag"] = (not cp_param["ospf_flag"] and
                                           not cp_param["vrrp_flag"] and
                                           not cp_param["bgp_flag"] and
                                           not cp_param["static_flag"])

                tmp_func_list.append(
                    GlobalModule.DB_CONTROL.write_vlanif_info)
                tmp_param_list.append(cp_param)
                func_list.extend(tmp_func_list)
                func_list.reverse()
                param_list.extend(tmp_param_list)
                param_list.reverse()
        if slice_type == self.__service.l2_slice:
            key_ope = "operation"
            val_del = "delete"
            dummy_info = dev_node.find(name_s + "dummy_vlan")
            if dummy_info is not None:
                for dummy_cp_node in dev_node.findall(name_s + "dummy_vlan"):
                    if not dummy_cp_node.get(key_ope) == val_del:
                        self.__set_dummy_param(tmp_func_list,
                                               tmp_param_list,
                                               dev_node,
                                               dummy_cp_node,
                                               name_s,
                                               db_control,
                                               device_name,
                                               slice_name)

            multi_homing = dev_node.find(name_s + "multi-homing")
            if multi_homing is not None:
                tmp_node = multi_homing.find(name_s + "multi-homing")
                tmp_anycast = multi_homing.find(name_s + "anycast")
                anycast_address = self.__get_param(
                    tmp_anycast, name_s + "address", str)
                tmp_interface = multi_homing.find(name_s + "interface")
                interface_address = self.__get_param(
                    tmp_interface, name_s + "address", str)
                interface_prefix = self.__get_param(
                    tmp_interface, name_s + "prefix", int)
                tmp_clag = multi_homing.find(name_s + "clag")
                tmp_clag_backup = tmp_clag.find(name_s + "backup")
                clag_backup_address = self.__get_param(
                    tmp_clag_backup, name_s + "address", str)
                tmp_clag_peer = tmp_clag.find(name_s + "peer")
                clag_peer_address = (
                    self.__get_param(tmp_clag_peer, name_s + "address", str))

                multi_homing_param = dict.fromkeys(["db_control",
                                                    "device_name",
                                                    "anycast_id",
                                                    "anycast_address",
                                                    "clag_if_address",
                                                    "clag_if_prefix",
                                                    "backup_address",
                                                    "peer_address"])

                multi_homing_param["db_control"] = db_control
                multi_homing_param["device_name"] = device_name
                anycast_id = GlobalModule.EMSYSCOMUTILDB.get_anycast_id(
                    anycast_address)
                multi_homing_param["anycast_id"] = anycast_id
                multi_homing_param["anycast_address"] = anycast_address
                multi_homing_param["clag_if_address"] = interface_address
                multi_homing_param["clag_if_prefix"] = interface_prefix
                multi_homing_param["backup_address"] = clag_backup_address
                multi_homing_param["peer_address"] = clag_peer_address
                tmp_func_list.append(
                    GlobalModule.DB_CONTROL.write_multi_homing_info)
                tmp_param_list.append(multi_homing_param)
        func_list.extend(tmp_func_list)
        param_list.extend(tmp_param_list)
        return func_list, param_list

    @decorater_log
    def __get_func_breakoutif_info(self, dev_node, db_control, service):
        '''
        Create parameter for write_breakout_if_info based on device node.
        Explanation about parameter:
            dev_node : Device node (xml object)
            db_control : DB control (str)
            service : Service type (str)
        Return value:
            Method list   : list
            Parameter list : list
         '''
        name_s = "{%s}" % (self._namespace.get(service),)

        device_name = self.__get_param(dev_node, name_s + "name", str)

        func_list = []
        param_list = []

        for if_node in dev_node.findall(name_s + "breakout-interface"):
            self.__set_breakoutif_param(func_list,
                                        param_list,
                                        name_s,
                                        db_control,
                                        device_name,
                                        node=if_node)
        return func_list, param_list

    @decorater_log
    def __set_breakoutif_param(self,
                               func_list,
                               param_list,
                               name_s,
                               db_control,
                               device_name,
                               node=None):
        '''
        Create parameter for write_breakout_if_info.
        Explanation about parameter:
            func_list : Method list (list)
            param_list : Parameter list (list)
            name_s : Name space (str)
            db_control : DB control (str)
            device_name : Device name (str)
            node : Node (xml object)
        '''
        breakoutif_param = dict.fromkeys(["db_control",
                                          "device_name",
                                          "base_interface",
                                          "speed",
                                          "breakout_num"])

        breakoutif_param["db_control"] = db_control

        breakoutif_param["device_name"] = device_name
        if node is not None:
            breakoutif_param["base_interface"] = (
                self.__get_param(node, name_s + "base-interface", str))
            breakoutif_param["speed"] = (
                self.__get_param(node, name_s + "speed", str))
            breakoutif_param["breakout_num"] = (
                self.__get_param(node, name_s + "breakout-num", int))

        func_list.append(GlobalModule.DB_CONTROL.write_breakout_if_info)
        param_list.append(breakoutif_param)

    @decorater_log
    def __get_func_inner_link_info(self, dev_node, db_control, service):
        '''
        Create parameter for write_inner_link_info based on device node.
        Explanation about parameter:
            dev_node : Device node (xml object)
            db_control : DB control (str)
            service : Service type (str)
        Return value:
            Method list   : list
            Parameter list : list
         '''
        name_s = "{%s}" % (self._namespace.get(service),)

        device_name = self.__get_param(dev_node, name_s + "name", str)

        os_name = None
        node_1 = dev_node.find(name_s + "equipment")
        if node_1 is not None:
            os_name = (
                self.__get_param(node_1, name_s + "os", str))

        func_list = []
        param_list = []

        db_if_type = {"physical-if": 1,
                      "breakout-if": 1,
                      "lag-if": 2}

        for if_node in dev_node.findall(name_s + "internal-interface"):
            if_type = self.__get_param(if_node, name_s + "type", str)

            self.__set_inner_linkif_param(func_list,
                                          param_list,
                                          name_s,
                                          db_control,
                                          device_name,
                                          if_type=db_if_type[if_type],
                                          node=if_node,
                                          os_name=os_name)
        return func_list, param_list

    @decorater_log
    def __set_inner_linkif_param(self,
                                 func_list,
                                 param_list,
                                 name_s,
                                 db_control,
                                 device_name,
                                 if_type=None,
                                 node=None,
                                 os_name=None):
        '''
        Create parameter for write_inner_link_if_info.
        Explanation about parameter:
            func_list : Method list (list)
            param_list : Parameter list (list)
            name_s : Name space (str)
            db_control : DB control (str)
            device_name : Device name (str)
            if_type : IF type (int)
            node : Node (xml object)
        '''
        inner_linkif_param = dict.fromkeys(["db_control",
                                            "device_name",
                                            "if_name",
                                            "if_type",
                                            "vlan_id",
                                            "link_speed",
                                            "internal_link_ip_address",
                                            "internal_link_ip_prefix",
                                            "cost"])
        inner_linkif_param["db_control"] = db_control

        inner_linkif_param["device_name"] = device_name
        if node is not None:
            inner_linkif_param["if_name"] = (
                self.__get_param(node, name_s + "name", str))
            inner_linkif_param["if_type"] = if_type
            inner_linkif_param["vlan_id"] = (
                self.__get_param(node, name_s + "vlan-id", int))
            inner_linkif_param["link_speed"] = (
                self.__get_param(node, name_s + "link-speed", str))
            inner_linkif_param["internal_link_ip_address"] = (
                self.__get_param(node, name_s + "address", str))
            inner_linkif_param["internal_link_ip_prefix"] = (
                self.__get_param(node, name_s + "prefix", int))
            inner_linkif_param["cost"] = (
                self.__get_param(node, name_s + "cost", int))

            if db_control != self.__db_delete:
                oppo_name = self.__get_param(
                    node, name_s + "opposite-node-name", str)
                ok, dev_regist_opp = (
                    GlobalModule.DB_CONTROL.read_device_regist_info(oppo_name))
                if not (ok and len(dev_regist_opp) > 0):
                    raise ValueError(
                        "failed get to dev_regist_info at %s" %
                        (dev_regist_opp[0]['device_name'],))
                if not os_name:
                    ok1, dev_regist = (GlobalModule.DB_CONTROL.
                                       read_device_regist_info(device_name))
                    if not (ok1 and len(dev_regist) > 0):
                        raise ValueError(
                            "failed get to dev_regist_info at %s"
                            % (device_name,))
                    os_name = dev_regist[0]['os']

                need_vlan_os = (
                    GlobalModule.EM_CONFIG.
                    read_conf_internal_link_vlan_os_tuple())
                if not (dev_regist_opp[0]['os'] in
                        need_vlan_os or
                        os_name in need_vlan_os):
                    inner_linkif_param["vlan_id"] = None

        func_list.append(GlobalModule.DB_CONTROL.write_inner_link_if_info)
        param_list.append(inner_linkif_param)

    @decorater_log
    def __get_func_cluster_linkif_info(self, dev_node, db_control, service):
        '''
        Create parameter for write_cluster_link_if_info based on device node.
        Explanation about parameter:
            dev_node : Device node (xml object)
            db_control : DB control (str)
            service : Service type (str)
        Return value:
            Method list   : list
            Parameter list : list
         '''
        name_s = "{%s}" % (self._namespace.get(service),)

        func_list = []
        param_list = []

        db_if_type = {"physical-if": 1,
                      "breakout-if": 1,
                      "lag-if": 2}

        db_condition = {"enable": 1,
                        "disable": 0}

        device_name = self.__get_param(dev_node, name_s + "name", str)

        for if_node in dev_node.findall(name_s + "cluster-link"):
            cluster_param = dict.fromkeys(["db_control",
                                           "device_name",
                                           "if_name",
                                           "if_type",
                                           "cluster_link_ip_address",
                                           "cluster_link_ip_prefix",
                                           "igp_cost"])
            cluster_param["db_control"] = db_control
            cluster_param["device_name"] = device_name
            if_name = self.__get_param(if_node, name_s + "name", str)
            cluster_param["if_name"] = if_name
            if_type = self.__get_param(if_node, name_s + "if_type", str)
            if if_type:
                cluster_param["if_type"] = db_if_type[if_type]
            cluster_param["cluster_link_ip_address"] = (
                self.__get_param(if_node, name_s + "address", str))
            cluster_param["cluster_link_ip_prefix"] = (
                self.__get_param(if_node, name_s + "prefix", int))
            cluster_param["igp_cost"] = (
                self.__get_param(if_node.find(name_s + "ospf"),
                                 name_s + "metric",
                                 int))
            func_list.append(
                GlobalModule.DB_CONTROL.write_cluster_link_if_info)
            param_list.append(cluster_param)

            if db_control == self.__db_delete:
                is_ok, db_clusters = \
                    GlobalModule.DB_CONTROL.read_cluster_link_if_info(
                        device_name)
                if not is_ok:
                    err_mes = (
                        'DB Fault read_cluster_link_if_info(device_name = %s)'
                        % (device_name,))
                    GlobalModule.EM_LOGGER.debug(err_mes)
                    raise ValueError("DB Control ERROR")

                for db_cluster in db_clusters:
                    if db_cluster["if_name"] == if_name:
                        db_if_type = db_cluster["if_type"]
                        if db_if_type == 1:
                            self.__set_physicalif_param(func_list,
                                                        param_list,
                                                        name_s,
                                                        db_control,
                                                        device_name,
                                                        node=if_node)
                        else:
                            is_ok, db_lag_mems = \
                                GlobalModule.DB_CONTROL.read_lagmemberif_info(
                                    device_name)
                            if not is_ok:
                                err_mes = (
                                    'DB Fault read_lagmem(device_name = %s)'
                                    % (device_name,))
                                GlobalModule.EM_LOGGER.debug(err_mes)
                                raise ValueError("DB Control ERROR")
                            for db_lag_mem in db_lag_mems:
                                if db_lag_mem["lag_if_name"] == if_name:
                                    name = db_lag_mem["if_name"]
                                    self.__set_physicalif_param(func_list,
                                                                param_list,
                                                                name_s,
                                                                "UPDATE",
                                                                device_name,
                                                                if_name=name)
            else:
                for node in if_node.findall(name_s +
                                            "cluster-lagmem-interface"):
                    condition = self.__get_param(node,
                                                 name_s + "condition",
                                                 str)
                    self.__set_physicalif_param(func_list,
                                                param_list,
                                                name_s,
                                                db_control,
                                                device_name,
                                                condition=db_condition[
                                                    condition],
                                                node=node)

        return func_list, param_list

    @decorater_log
    def __get_func_acl_info(self, dev_node, db_control, service):
        '''
        Creates parameters of write_acl_info based on device node
        Explanation about parameter:
            dev_node : device node (xml object)
            db_control : DB control (str)
            service : service type (str)
        Return value:
            Method list   : list
            Parameter list : list
         '''
        name_s = "{%s}" % (self._namespace.get(service),)
        func_list = []
        param_list = []
        acl_detail_list = []

        device_name = self.__get_param(dev_node, name_s + "name", str)

        for acl_filter in dev_node.findall(name_s + "filter"):
            acl_id = (self.__get_param(
                acl_filter, name_s + "filter_id", int))
            acl_filter_param = dict.fromkeys(["db_control",
                                              "device_name",
                                              "acl_id",
                                              "if_name",
                                              "vlan_id"])
            acl_filter_param["db_control"] = db_control
            acl_filter_param["device_name"] = device_name
            acl_filter_param["acl_id"] = acl_id
            term_para = acl_filter.find(name_s + "term")
            acl_filter_param["if_name"] = (
                self.__get_param(term_para,
                                 name_s + "name",
                                 str))
            acl_filter_param["vlan_id"] = (
                self.__get_param(term_para,
                                 name_s + "vlan-id",
                                 int))
            func_list.append(
                GlobalModule.DB_CONTROL.write_acl_info)
            param_list.append(acl_filter_param)
            for term in acl_filter.findall(name_s + "term"):
                self.__set_acl_detail_param(func_list,
                                            param_list,
                                            acl_detail_list,
                                            name_s,
                                            db_control,
                                            term,
                                            device_name,
                                            acl_id)

        return func_list, param_list, acl_detail_list

    @decorater_log
    def __set_acl_detail_param(self, func_list, param_list, acl_detail_list,
                               name_s, db_control, acl_term=None,
                               device_name=None, acl_id=None):
        '''
        Creates parameter of write_acl_detail_info based on device node
        Explanation about parameter:
            func_list : Method list (list)
            param_list : Parameter list (list)
            acl_detail_list : ACL list (list)
            name_s : Name space (str)
            db_control : DB control (str)
            acl_term : ACL term name (str)
            device_name : Device name (str)
            acl_id : ACL Configuration ID
        Return value:
            Method list   : list
            Parameter list : list
         '''
        if acl_term is not None:
            acl_term_param = dict.fromkeys(["db_control",
                                            "device_name",
                                            "acl_id",
                                            "term_name",
                                            "action",
                                            "direction",
                                            "source_mac_address",
                                            "destination_mac_address",
                                            "source_ip_address",
                                            "destination_ip_address",
                                            "source_port",
                                            "destination_port",
                                            "protocol",
                                            "acl_priority"])
            acl_term_param["db_control"] = db_control
            acl_term_param["device_name"] = device_name
            acl_term_param["acl_id"] = acl_id
            acl_term_param["term_name"] = (self.__get_param(
                acl_term, name_s + "term_name", str))
            acl_term_param["action"] = (self.__get_param(
                acl_term, name_s + "action", str))
            acl_term_param["direction"] = (self.__get_param(
                acl_term, name_s + "direction", str))
            acl_term_param["source_mac_address"] = (self.__get_param(
                acl_term, name_s + "source-mac-address", str))
            acl_term_param["destination_mac_address"] = (
                self.__get_param(acl_term, name_s
                                 + "destination-mac-address", str))
            acl_term_param["source_ip_address"] = (self.__get_param(
                acl_term, name_s + "source-ip-address", str))
            acl_term_param["destination_ip_address"] = (self.__get_param(
                acl_term, name_s + "destination-ip-address", str))
            acl_term_param["source_port"] = (self.__get_param(
                acl_term, name_s + "source-port", int))
            acl_term_param["destination_port"] = (self.__get_param(
                acl_term, name_s + "destination-port", int))
            acl_term_param["protocol"] = (self.__get_param(
                acl_term, name_s + "protocol", str))
            acl_term_param["acl_priority"] = (self.__get_param(
                acl_term, name_s + "priority", int))
            func_list.append(
                GlobalModule.DB_CONTROL.write_acl_detail_info)
            param_list.append(acl_term_param)
            acl_detail_list.append(acl_term_param)

    @decorater_log
    def __get_func_l2_del(self,
                          dev_node,
                          slice_type,
                          is_write_force=False):
        '''
        Create parameter for L2 slice deletion based on device node.
        Explanation about parameter:
            dev_node : Device node (xml object)
            slice_type : Slice type (str)
        Return value:
            Method list   : list
            Parameter list : list
        '''
        name_s = "{%s}" % (self._namespace.get(slice_type),)

        db_slice_type = {self.__service.l2_slice: 2}

        db_port_mode = {"access": 1, "trunk": 2}

        db_control = self.__db_delete

        func_list = []
        param_list = []

        key_ope = "operation"
        val_del = "delete"

        device_name = self.__get_param(dev_node, name_s + "name", str)

        slice_name = self.__get_param(dev_node, name_s + "slice_name", str)

        ok, db_vlan_info = GlobalModule.DB_CONTROL.read_vlanif_info(
            device_name)
        if not ok:
            err_mes = ('DB Fault read_vlanif_info(device_name = %s)' %
                       (device_name,))
            GlobalModule.EM_LOGGER.debug(err_mes)
            raise ValueError("DB Control ERROR")

        if is_write_force and (db_vlan_info is None or
                               len(db_vlan_info) <= 0):
            err_mes = ('db vlan_count = 0 (device_name = %s , vlan = %s)' %
                       (device_name, db_vlan_info))
            GlobalModule.EM_LOGGER.debug(err_mes)
            raise ValueError("VLAN COUNT ZERO ERROR")
        cp_del_count = 0
        vlan_count = 0
        for cp_node in dev_node.findall(name_s + "cp"):
            is_cp_del = False
            if_name = self.__get_param(cp_node, name_s + "name", str)
            vlan_id = self.__get_param(cp_node, name_s + "vlan-id", int)
            if cp_node.get(key_ope) == val_del:
                is_cp_del = True
                db_control_merge = "INSERT"
                cp_del_count = cp_del_count + 1
                cp_param = self.__get_key_recode(db_vlan_info,
                                                 device_name=device_name,
                                                 if_name=if_name,
                                                 vlan_id=vlan_id,
                                                 slice_name=slice_name)
                cp_param["db_control"] = (db_control)
                if cp_param is None:
                    GlobalModule.EM_LOGGER.debug(
                        'DB Fault not found recode (device_name =' +
                        '%s ,if_name = %s ,vlan_id = %s ,slice_name = %s)' %
                        (device_name, if_name, vlan_id, slice_name)
                    )
                    raise ValueError("DB UNKNOWN VLAN DELETE OPERATION ERROR")
                else:
                    func_list.append(
                        GlobalModule.DB_CONTROL.write_vlanif_info)
                    param_list.append(cp_param)
                if dev_node.find(name_s + "vrf") is not None:
                    ok, db_vrf_detail_info = (
                        GlobalModule.DB_CONTROL.read_vrf_detail_info(
                            device_name))
                    if not ok:
                        err_mes = (
                            'DB Fault read_vrf_detail_info(device_name = %s)' %
                            (device_name,))
                        GlobalModule.EM_LOGGER.debug(err_mes)
                        raise ValueError("DB Control ERROR")
                    vrf_param = self.__get_key_recode(db_vrf_detail_info,
                                                      device_name=device_name,
                                                      if_name=if_name,
                                                      vlan_id=vlan_id,
                                                      slice_name=slice_name)
                    if vrf_param is None:
                        GlobalModule.EM_LOGGER.debug(
                            'DB Fault not found VRF recode (device_name =' +
                            '%s ,if_name = %s ,vlan_id = %s ,slice_name = %s)'
                            % (device_name, if_name, vlan_id, slice_name)
                        )
                    else:
                        vrf_param["db_control"] = (db_control)
                        func_list.append(
                            GlobalModule.DB_CONTROL.write_vrf_detail_info)
                        param_list.append(vrf_param)

            elif cp_node.find(name_s + "port-mode") is None and \
                    cp_node.find(name_s + "esi") is not None and \
                    cp_node.find(name_s + "system-id")is not None and \
                    cp_node.find(name_s + "esi").get(key_ope) == val_del and \
                    cp_node.find(name_s + "system-id").get(key_ope) == val_del:
                esi_node = cp_node.find(name_s + "esi")
                system_id_node = cp_node.find(name_s + "system-id")
                if esi_node.get(key_ope) == val_del and (
                    system_id_node.get(key_ope) == val_del) and(
                        not is_cp_del):
                    cp_param = self.__get_key_recode(db_vlan_info,
                                                     device_name=device_name,
                                                     if_name=if_name,
                                                     vlan_id=vlan_id,
                                                     slice_name=slice_name)
                    if esi_node.get(key_ope) == val_del:
                        cp_param["esi"] = None
                    if system_id_node.get(key_ope) == val_del:
                        cp_param["system_id"] = None
                    cp_param["clag_id"] = None
                    cp_param["db_control"] = ("UPDATE")
                    func_list.append(
                        GlobalModule.DB_CONTROL.write_vlanif_info)
                    param_list.append(cp_param)
            elif not (cp_node.get(key_ope) == val_del) and(
                    cp_node.find(name_s + "vni") is None) and (
                    cp_node.find(name_s + "port-mode") is None and
                    cp_node.find(name_s + "esi") is not None and
                    cp_node.find(name_s + "system-id") is not None and
                    not (cp_node.find(name_s + "esi").get(key_ope) == val_del)
                    and not (cp_node.find(name_s + "system-id").get(
                        key_ope) == val_del)):
                cp_param = self.__get_key_recode(db_vlan_info,
                                                 device_name=device_name,
                                                 if_name=if_name,
                                                 vlan_id=vlan_id,
                                                 slice_name=slice_name)

                self._change_multi(
                    cp_node, name_s, slice_name, device_name, cp_param)
                cp_param["db_control"] = ("UPDATE")
                cp_param["esi"] = self.__get_param(
                    cp_node, name_s + "esi", str)
                cp_param["system_id"] = self.__get_param(
                    cp_node, name_s + "system-id", str)
                cp_param["clag_id"] = self.__get_param(
                    cp_node, name_s + "clag-id", int)
                func_list.append(
                    GlobalModule.DB_CONTROL.write_vlanif_info)
                param_list.append(cp_param)

            elif cp_node.find(name_s + "port-mode") is not None:
                slice_name = self.__get_param(
                    dev_node, name_s + "slice_name", str)
                tmp_func_list = []
                tmp_param_list = []
                vrf_param = {}
                db_control_merge = "INSERT"
                cp_param = dict.fromkeys(["db_control",
                                          "device_name",
                                          "if_name",
                                          "vlan_id",
                                          "slice_name",
                                          "slice_type",
                                          "port_mode",
                                          "vni",
                                          "multicast_group",
                                          "ipv4_address",
                                          "ipv4_prefix",
                                          "ipv6_address",
                                          "ipv6_prefix",
                                          "bgp_flag",
                                          "ospf_flag",
                                          "static_flag",
                                          "direct_flag",
                                          "vrrp_flag",
                                          "mtu_size",
                                          "metric",
                                          "esi",
                                          "system_id",
                                          "inflow_shaping_rate",
                                          "outflow_shaping_rate",
                                          "remark_menu",
                                          "egress_queue_menu",
                                          "clag_id",
                                          "speed",
                                          "irb_ipv4_address",
                                          "irb_ipv4_prefix",
                                          "virtual_mac_address",
                                          "virtual_gateway_address",
                                          "virtual_gateway_prefix"])
                cp_param["db_control"] = db_control_merge
                cp_param["device_name"] = device_name
                cp_param["slice_name"] = slice_name
                cp_param["slice_type"] = db_slice_type.get(slice_type)
                cp_param["if_name"] = (
                    self.__get_param(cp_node, name_s + "name", str))
                cp_param["vlan_id"] = (
                    self.__get_param(cp_node, name_s + "vlan-id", int))

                qos_info = cp_node.find(name_s + "qos")
                if qos_info is not None:

                    self.__set_qos_param(qos_info,
                                         name_s,
                                         db_control_merge,
                                         cp_param)

                is_ok, lag_data = GlobalModule.DB_CONTROL.read_lagif_info(
                    device_name)
                if not is_ok:
                    err_mes = (
                        'DB Fault read_lagif_info(device_name = %s)' %
                        (device_name,))
                    GlobalModule.EM_LOGGER.debug(err_mes)
                    raise ValueError("DB Control ERROR")

                is_if_name = False
                for data in lag_data:
                    if (data["device_name"] == device_name and
                            data["lag_if_name"] == cp_param["if_name"]):
                        is_if_name = True
                        break

                if not is_if_name:
                    self.__set_physicalif_param(tmp_func_list,
                                                tmp_param_list,
                                                name_s,
                                                db_control_merge,
                                                device_name,
                                                node=cp_node)
                tmp = self.__get_param(
                    cp_node, name_s + "port-mode", str)
                port_mode_data = (
                    db_port_mode.get(tmp.lower()) if tmp else None)
                vni_data = self.__get_param(
                    cp_node, name_s + "vni", int)
                clag_id = self.__get_param(
                    cp_node, name_s + "clag-id", int)
                speed = self.__get_param(
                    cp_node, name_s + "speed", str)

                if dev_node.find(name_s + "vrf"):
                    if_name = cp_param["if_name"]
                    vlan_id = cp_param["vlan_id"]
                    vrf_param = self.__set_l2_vrf_param(
                        name_s,
                        db_control_merge,
                        device_name,
                        slice_name,
                        if_name,
                        vlan_id,
                        dev_node)
                cp_param["port_mode"] = port_mode_data
                cp_param["vni"] = vni_data
                cp_param["esi"] = self.__get_param(
                    cp_node, name_s + "esi", str)
                cp_param["system_id"] = self.__get_param(
                    cp_node, name_s + "system-id", str)
                cp_param["clag_id"] = clag_id
                cp_param["speed"] = self.__get_param(
                    cp_node, name_s + "speed", str)
                irb_info = cp_node.find(name_s + "irb")
                if irb_info is not None:
                    self.__set_irb_param(irb_info,
                                         name_s,
                                         db_control_merge,
                                         cp_param)
                if vrf_param is not None:
                    tmp_func_list.append(
                        GlobalModule.DB_CONTROL.write_vrf_detail_info)
                    tmp_param_list.append(vrf_param)
                tmp_func_list.append(
                    GlobalModule.DB_CONTROL.write_vlanif_info)
                tmp_param_list.append(cp_param)

                multi_homing = dev_node.find(name_s + "multi-homing")
                if multi_homing is not None:
                    tmp_anycast = multi_homing.find(name_s + "anycast")
                    anycast_address = self.__get_param(
                        tmp_anycast, name_s + "address", str)
                    tmp_interface = multi_homing.find(name_s + "interface")
                    interface_address = self.__get_param(
                        tmp_interface, name_s + "address", str)
                    interface_prefix = self.__get_param(
                        tmp_interface, name_s + "prefix", int)
                    tmp_clag = multi_homing.find(name_s + "clag")
                    tmp_clag_backup = tmp_clag.find(name_s + "backup")
                    clag_backup_address = self.__get_param(
                        tmp_clag_backup, name_s + "address", str)
                    tmp_clag_peer = tmp_clag.find(name_s + "peer")
                    clag_peer_address = (
                        self.__get_param(
                            tmp_clag_peer, name_s + "address", str))

                    multi_homing_param = dict.fromkeys(["db_control",
                                                        "device_name",
                                                        "anycast_id",
                                                        "anycast_address",
                                                        "clag_if_address",
                                                        "clag_if_prefix",
                                                        "backup_address",
                                                        "peer_address"])

                    multi_homing_param["db_control"] = db_control_merge
                    multi_homing_param["device_name"] = device_name
                    anycast_id = (
                        GlobalModule.EMSYSCOMUTILDB.get_anycast_id(
                            anycast_address))
                    multi_homing_param["anycast_id"] = anycast_id
                    multi_homing_param["anycast_address"] = anycast_address
                    multi_homing_param["clag_if_address"] = (
                        interface_address)
                    multi_homing_param["clag_if_prefix"] = interface_prefix
                    multi_homing_param["backup_address"] = (
                        clag_backup_address)
                    multi_homing_param["peer_address"] = clag_peer_address
                    tmp_func_list.append(
                        GlobalModule.DB_CONTROL.write_multi_homing_info)
                    tmp_param_list.append(multi_homing_param)
                func_list.extend(tmp_func_list)
                param_list.extend(tmp_param_list)

        for dummy_node in dev_node.findall(name_s + "dummy_vlan"):
            vlan_id = self.__get_param(dummy_node, name_s + "vlan-id", int)
            if dummy_node.get(key_ope) == val_del:
                ok, db_dummy_vlan_info = (
                    GlobalModule.DB_CONTROL.read_dummy_vlan_if_info(
                        device_name))
                if not ok:
                    err_mes = (
                        'DB Fault read_dummy_vlan_if_info(device_name = %s)' %
                        (device_name,))
                    GlobalModule.EM_LOGGER.debug(err_mes)
                    raise ValueError("DB Control ERROR")
                dummy_param = self.__get_key_recode(db_dummy_vlan_info,
                                                    device_name=device_name,
                                                    vlan_id=vlan_id,
                                                    slice_name=slice_name)
                dummy_param["db_control"] = (db_control)

                func_list.append(
                    GlobalModule.DB_CONTROL.write_dummy_vlan_if_info)
                param_list.append(dummy_param)
            else:
                dummy_info = dev_node.find(name_s + "dummy_vlan")
                if dummy_info is not None:
                    db_control_merge = "INSERT"
                    self.__set_dummy_param(func_list,
                                           param_list,
                                           dev_node,
                                           dummy_node,
                                           name_s,
                                           db_control_merge,
                                           device_name,
                                           slice_name)

        for row in db_vlan_info:
            vlan_count += 1

        if cp_del_count == vlan_count and not cp_del_count == 0:
            ok, db_multi_homing_info = (
                GlobalModule.DB_CONTROL.read_multi_homing_info(device_name))
            if not ok:
                err_mes = ('DB Fault read_multi_homing_info(device_name = %s)'
                           % (device_name,))
                GlobalModule.EM_LOGGER.debug(err_mes)
                raise ValueError("DB Control ERROR")
            multi_homing_param = self.__get_key_recode(db_multi_homing_info,
                                                       device_name=device_name)
            if multi_homing_param is not None and len(multi_homing_param) > 0:
                multi_homing_param["db_control"] = (db_control)
                multi_homing_param["device_name"] = device_name

                func_list.append(
                    GlobalModule.DB_CONTROL.write_multi_homing_info)
                param_list.append(multi_homing_param)
        return func_list, param_list

    @decorater_log
    def _change_multi(self,
                      cp_node,
                      name_s,
                      slice_name,
                      device_name,
                      cp_param):
        is_ok, vlan_data = \
            GlobalModule.DB_CONTROL.read_vlanif_info(
                device_name)
        if is_ok:
            for data in vlan_data:
                if data["device_name"] == device_name and \
                        data["slice_name"] == slice_name and \
                        data["if_name"] == cp_param["if_name"] and \
                        data["vlan_id"] == cp_param["vlan_id"]:
                    cp_param = data
                    port_mode_data = data["port_mode"]
                    vni_data = data["vni"]

        cp_param["port_mode"] = port_mode_data
        cp_param["vni"] = vni_data

    @decorater_log
    def __get_func_internal_link_replace(self, dev_node, db_control, service):
        '''
        Creates parameter for internal linnk IF update based on device node
        Explanation about parameter:
            dev_node : device node (xml object)
            db_control : DB control (str)
            service:Service name
        Return value:
            Method list   : list
            Parameter list : list
        '''
        name_s = "{%s}" % (self._namespace.get(service),)

        func_list = []
        param_list = []

        db_if_type = {"physical-if": 1,
                      "breakout-if": 1,
                      "lag-if": 2}

        device_name = self.__get_param(dev_node, name_s + "name", str)
        ok, db_internal_link_info =\
            GlobalModule.DB_CONTROL.read_inner_link_if_info(device_name)
        if not ok:
            GlobalModule.EM_LOGGER.debug(
                'DB Fault read_inner_link_if_info(device_name = %s)'
                % (device_name,))
            raise ValueError("DB Control (VLANIFINFO) ERROR")
        for in_node in dev_node.findall(name_s + "internal-interface"):
            if_name = self.__get_param(in_node, name_s + "name", str)
            if_type = self.__get_param(in_node, name_s + "type", str)
            cost = self.__get_param(in_node, name_s + "cost", int)
            cp_param = self.__get_key_recode(db_internal_link_info,
                                             device_name=device_name,
                                             if_name=if_name)

            if cp_param is None:
                GlobalModule.EM_LOGGER.debug(
                    'DB Fault not found recode (device_name =' +
                    '%s ,if_name = %s)' %
                    (device_name, if_name)
                )
                raise ValueError
            cp_param["db_control"] = db_control
            cp_param["if_type"] = db_if_type[if_type]
            cp_param["cost"] = cost
            func_list.append(GlobalModule.DB_CONTROL.write_inner_link_if_info)
            param_list.append(cp_param)

        return func_list, param_list

    @decorater_log
    def __get_func_l3_del(self,
                          dev_node,
                          slice_type,
                          is_write_force=False):
        '''
        Create parameter for L3 slice deletion based on device node.
        Explanation about parameter:
            dev_node : Device node (xml object)
            slice_type : Slice type (str)
        Return value:
            Method list   : list
            Parameter list : list
        '''
        name_s = "{%s}" % (self._namespace.get(slice_type),)

        db_control = self.__db_delete

        key_ope = "operation"
        val_del = "delete"

        func_list = []
        param_list = []

        device_name = self.__get_param(dev_node, name_s + "name", str)

        slice_name = self.__get_param(dev_node, name_s + "slice_name", str)

        ok, db_vlan_info =\
            GlobalModule.DB_CONTROL.read_vlanif_info(device_name)
        if not ok:
            GlobalModule.EM_LOGGER.debug(
                'DB Fault read_vlanif_info(device_name = %s)' % (device_name,))
            raise ValueError("DB Control (VLANIFINFO) ERROR")
        ok, db_vrrp = GlobalModule.DB_CONTROL.read_vrrp_detail_info(
            device_name)
        if not ok:
            GlobalModule.EM_LOGGER.debug(
                'DB Fault read_vrrp_detail_info(device_name = %s)' %
                (device_name,))
            raise ValueError("DB Control (VRRP_DETAIL) ERROR")
        ok, db_static = \
            GlobalModule.DB_CONTROL.read_static_route_detail_info(device_name)
        if not ok:
            GlobalModule.EM_LOGGER.debug(
                'DB Fault read_static_route_detail_info(device_name = %s)' %
                (device_name,))
            raise ValueError("DB Control (STATIC_DETAIL) ERROR")

        if is_write_force and (db_vlan_info is None or len(db_vlan_info) <= 0):
            err_mes = ('db vlan_count = 0 (device_name = %s , vlan = %s)' %
                       (device_name, db_vlan_info))
            GlobalModule.EM_LOGGER.debug(err_mes)
            raise ValueError("VLAN COUNT ZERO ERROR")

        cp_del_count = vlan_count = 0
        for row in db_vlan_info:
            vlan_count += 1 if row.get("slice_name") == slice_name else 0

        static_db_counts = {}
        for row in db_static:
            if row.get("slice_name") != slice_name:
                continue
            tmp_key = (row.get("if_name"), row.get("vlan_id"))
            if tmp_key in static_db_counts:
                static_db_counts[tmp_key] += 1
            else:
                static_db_counts[tmp_key] = 1

        for cp_node in dev_node.findall(name_s + "cp"):
            tmp_func_list = []
            tmp_param_list = []
            is_cp_del = False
            if_name = self.__get_param(cp_node, name_s + "name", str)
            vlan_id = self.__get_param(cp_node, name_s + "vlan-id", int)
            if cp_node.get(key_ope) == val_del:
                is_cp_del = True
                cp_del_count += 1
            cp_param = self.__get_key_recode(db_vlan_info,
                                             device_name=device_name,
                                             if_name=if_name,
                                             vlan_id=vlan_id,
                                             slice_name=slice_name)
            if cp_param is None:
                GlobalModule.EM_LOGGER.debug(
                    'DB Fault not found recode (device_name =' +
                    '%s ,if_name = %s ,vlan_id = %s ,slice_name = %s)' %
                    (device_name, if_name, vlan_id, slice_name)
                )
                raise ValueError
            cp_param["db_control"] = (self.__db_delete
                                      if is_cp_del else "UPDATE")
            if is_cp_del or cp_node.find(name_s + "ospf") is not None:
                cp_param["ospf_flag"] = False
                cp_param["metric"] = None
            if is_cp_del or cp_node.find(name_s + "bgp") is not None:
                cp_param["bgp_flag"] = False
                self.__set_bgp_param(tmp_func_list,
                                     tmp_param_list,
                                     cp_node.find(name_s + "bgp"),
                                     name_s,
                                     db_control,
                                     device_name,
                                     slice_name,
                                     if_name,
                                     vlan_id)
            if is_cp_del or cp_node.find(name_s + "static") is not None:
                if is_cp_del:
                    cp_param["static_flag"] = False
                    sr_param = dict.fromkeys(["db_control",
                                              "device_name",
                                              "if_name",
                                              "vlan_id",
                                              "slice_name",
                                              "address_type",
                                              "address",
                                              "prefix",
                                              "nexthop"])
                    sr_param["db_control"] = db_control
                    sr_param["device_name"] = device_name
                    sr_param["slice_name"] = slice_name
                    sr_param["if_name"] = if_name
                    sr_param["vlan_id"] = vlan_id
                    tmp_func_list.append(
                        GlobalModule.DB_CONTROL.write_static_route_detail_info)
                    tmp_param_list.append(sr_param)
                else:
                    route_nodes = cp_node.find(name_s + "static")
                    tmp_count = 0
                    for route_node in route_nodes:
                        if route_node.get("operation") == "delete":
                            tmp_count += 1
                    if static_db_counts.get((if_name, vlan_id)) == tmp_count:
                        cp_param["static_flag"] = False

                    self.__set_static_param(tmp_func_list,
                                            tmp_param_list,
                                            route_nodes,
                                            name_s,
                                            db_control,
                                            device_name,
                                            slice_name,
                                            if_name,
                                            vlan_id)

            if is_cp_del or cp_node.find(name_s + "vrrp") is not None:
                cp_param["vrrp_flag"] = False
                self.__set_vrrp_param(tmp_func_list,
                                      tmp_param_list,
                                      cp_node.find(name_s + "vrrp"),
                                      name_s,
                                      db_control,
                                      device_name,
                                      slice_name,
                                      if_name,
                                      vlan_id)
                vrrp_row = self.__get_key_recode(db_vrrp,
                                                 device_name=device_name,
                                                 if_name=if_name,
                                                 vlan_id=vlan_id,
                                                 slice_name=slice_name)
                if vrrp_row is not None:
                    tr_param = dict.fromkeys(["db_control",
                                              "vrrp_group_id",
                                              "track_if_name"])
                    tr_param["db_control"] = db_control
                    tr_param["vrrp_group_id"] = vrrp_row.get("vrrp_group_id")
                    if tr_param not in tmp_param_list:
                        tmp_func_list.append(
                            GlobalModule.DB_CONTROL.write_vrrp_trackif_info)
                        tmp_param_list.append(tr_param)

            if is_cp_del:
                vrf_param = dict.fromkeys(["db_control",
                                           "device_name",
                                           "if_name",
                                           "vlan_id",
                                           "slice_name",
                                           "vrf_name",
                                           "rt",
                                           "rd",
                                           "router_id"])
                vrf_param["db_control"] = db_control
                vrf_param["device_name"] = device_name
                vrf_param["slice_name"] = slice_name
                vrf_param["if_name"] = if_name
                vrf_param["vlan_id"] = vlan_id
                tmp_func_list.append(
                    GlobalModule.DB_CONTROL.write_vrf_detail_info)
                tmp_param_list.append(vrf_param)

            cp_param["direct_flag"] = (not cp_param["ospf_flag"] and
                                       not cp_param["vrrp_flag"] and
                                       not cp_param["bgp_flag"] and
                                       not cp_param["static_flag"])
            self.__set_physicalif_param(tmp_func_list,
                                        tmp_param_list,
                                        name_s,
                                        db_control,
                                        device_name,
                                        node=cp_node)

            func_list.append(
                GlobalModule.DB_CONTROL.write_vlanif_info)
            param_list.append(cp_param)
            func_list.extend(tmp_func_list)
            param_list.extend(tmp_param_list)

        return func_list, param_list

    @decorater_log
    def __get_func_l3_replace(self,
                              dev_node,
                              db_control,
                              slice_type):
        '''
        Create parameter for updating L3 slice based on device node.
        Explanation about parameter:
            dev_node : Device node (xml object)
            db_control : DB control (str)
            slice_type : Slice type (str)
        Return value:
            Method list   : list
            Parameter list : list
        '''
        name_s = "{%s}" % (self._namespace.get(slice_type),)

        func_list = []
        param_list = []

        device_name = self.__get_param(dev_node, name_s + "name", str)

        slice_name = self.__get_param(dev_node, name_s + "slice_name", str)

        ok, db_vlan_info =\
            GlobalModule.DB_CONTROL.read_vlanif_info(device_name)
        if not ok:
            GlobalModule.EM_LOGGER.debug(
                'DB Fault read_vlanif_info(device_name = %s)' % (device_name,))
            raise ValueError("DB Control (VLANIFINFO) ERROR")
        ok, db_static = \
            GlobalModule.DB_CONTROL.read_static_route_detail_info(device_name)
        if not ok:
            GlobalModule.EM_LOGGER.debug(
                'DB Fault read_static_route_detail_info(device_name = %s)' %
                (device_name,))
            raise ValueError("DB Control (STATIC_DETAIL) ERROR")

        static_db_counts = {}
        for row in db_static:
            if row.get("slice_name") != slice_name:
                continue
            tmp_key = (row.get("if_name"), row.get("vlan_id"))
            if tmp_key in static_db_counts:
                static_db_counts[tmp_key] += 1
            else:
                static_db_counts[tmp_key] = 1

        for cp_node in dev_node.findall(name_s + "cp"):
            tmp_func_list = []
            tmp_param_list = []
            if_name = self.__get_param(cp_node, name_s + "name", str)
            vlan_id = self.__get_param(cp_node, name_s + "vlan-id", int)
            cp_param = self.__get_key_recode(db_vlan_info,
                                             device_name=device_name,
                                             if_name=if_name,
                                             vlan_id=vlan_id,
                                             slice_name=slice_name)
            if cp_param is None:
                GlobalModule.EM_LOGGER.debug(
                    'DB Fault not found recode (device_name =' +
                    '%s ,if_name = %s ,vlan_id = %s ,slice_name = %s)' %
                    (device_name, if_name, vlan_id, slice_name)
                )
                raise ValueError
            cp_param["db_control"] = db_control
            if cp_node.find(name_s + "static") is not None:
                route_nodes = cp_node.find(name_s + "static")
                tmp_count = 0
                for route_node in route_nodes:
                    if route_node.get("operation") == "delete":
                        tmp_count += 1
                if static_db_counts.get((if_name, vlan_id)) == tmp_count:
                    cp_param["static_flag"] = False

                self.__set_static_param(tmp_func_list,
                                        tmp_param_list,
                                        route_nodes,
                                        name_s,
                                        db_control,
                                        device_name,
                                        slice_name,
                                        if_name,
                                        vlan_id)

            qos_info = cp_node.find(name_s + "qos")
            if qos_info is not None:

                self.__set_qos_param(qos_info,
                                     name_s,
                                     db_control,
                                     cp_param)

            func_list.append(GlobalModule.DB_CONTROL.write_vlanif_info)
            param_list.append(cp_param)
            func_list.extend(tmp_func_list)
            param_list.extend(tmp_param_list)

        return func_list, param_list

    @decorater_log
    def __get_func_l2_replace(self,
                              dev_node,
                              db_control,
                              slice_type):
        '''
        Create parameter for updating L2 slice based on device node.
        Explanation about parameter:
            dev_node : Device node (xml object)
            db_control : DB control (str)
            slice_type : Slice type (str)
        Return value:
            Method list   : list
            Parameter list : list
        '''
        name_s = "{%s}" % (self._namespace.get(slice_type),)

        func_list = []
        param_list = []

        device_name = self.__get_param(dev_node, name_s + "name", str)

        slice_name = self.__get_param(dev_node, name_s + "slice_name", str)

        ok, db_vlan_info =\
            GlobalModule.DB_CONTROL.read_vlanif_info(device_name)
        if not ok:
            GlobalModule.EM_LOGGER.debug(
                'DB Fault read_vlanif_info(device_name = %s)' % (device_name,))
            raise ValueError("DB Control (VLANIFINFO) ERROR")

        for cp_node in dev_node.findall(name_s + "cp"):
            if_name = self.__get_param(cp_node, name_s + "name", str)
            vlan_id = self.__get_param(cp_node, name_s + "vlan-id", int)
            cp_param = self.__get_key_recode(db_vlan_info,
                                             device_name=device_name,
                                             if_name=if_name,
                                             vlan_id=vlan_id,
                                             slice_name=slice_name)
            if cp_param is None:
                GlobalModule.EM_LOGGER.debug(
                    'DB Fault not found recode (device_name =' +
                    '%s ,if_name = %s ,vlan_id = %s ,slice_name = %s)' %
                    (device_name, if_name, vlan_id, slice_name)
                )
                raise ValueError
            cp_param["db_control"] = db_control

            qos_info = cp_node.find(name_s + "qos")
            if qos_info is not None:

                self.__set_qos_param(qos_info,
                                     name_s,
                                     db_control,
                                     cp_param)

            func_list.append(GlobalModule.DB_CONTROL.write_vlanif_info)
            param_list.append(cp_param)

        return func_list, param_list

    @decorater_log
    def __set_bgp_param(self,
                        func_list,
                        param_list,
                        bgp_node,
                        name_s,
                        db_control,
                        device_name,
                        slice_name,
                        if_name,
                        vlan_id):
        tmp_node = bgp_node
        bgp_param = dict.fromkeys(["db_control",
                                   "device_name",
                                   "if_name",
                                   "vlan_id",
                                   "slice_name",
                                   "master",
                                   "remote_as_number",
                                   "local_ipv4_address",
                                   "remote_ipv4_address",
                                   "local_ipv6_address",
                                   "remote_ipv6_address"])
        bgp_param["db_control"] = db_control
        bgp_param["device_name"] = device_name
        bgp_param["slice_name"] = slice_name
        bgp_param["if_name"] = if_name
        bgp_param["vlan_id"] = vlan_id
        if db_control != self.__db_delete and bgp_node is not None:
            if tmp_node.find(name_s + "master") is not None:
                bgp_param["master"] = True
            else:
                bgp_param["master"] = False
            bgp_param["remote_as_number"] = (
                self.__get_param(tmp_node,
                                 name_s + "remote-as-number",
                                 int))
            bgp_param["local_ipv4_address"] = (
                self.__get_param(tmp_node,
                                 name_s + "local-address",
                                 str))
            bgp_param["remote_ipv4_address"] = (
                self.__get_param(tmp_node,
                                 name_s + "remote-address",
                                 str))
            bgp_param["local_ipv6_address"] = (
                self.__get_param(tmp_node,
                                 name_s + "local-address6",
                                 str))
            bgp_param["remote_ipv6_address"] = (
                self.__get_param(tmp_node,
                                 name_s + "remote-address6",
                                 str))
        func_list.append(
            GlobalModule.DB_CONTROL.write_bgp_detail_info)
        param_list.append(bgp_param)

    @decorater_log
    def __set_static_param(self,
                           func_list,
                           param_list,
                           static_node,
                           name_s,
                           db_control,
                           device_name,
                           slice_name,
                           if_name,
                           vlan_id):
        tmp_node = static_node
        route_nodes = []
        route_nodes.extend(
            tmp_node.findall(name_s + "route")
            if tmp_node.find(name_s + "route") is not None else []
        )
        route_nodes.extend(
            tmp_node.findall(name_s + "route6")
            if tmp_node.find(name_s + "route6") is not None else []
        )
        for route_node in route_nodes:
            if (db_control == self.__db_delete and
                    route_node.get("operation") != "delete"):
                continue
            if (db_control == "UPDATE" and
                    route_node.get("operation") == "delete"):
                db_control = self.__db_delete

            sr_param = dict.fromkeys(["db_control",
                                      "device_name",
                                      "if_name",
                                      "vlan_id",
                                      "slice_name",
                                      "address_type",
                                      "address",
                                      "prefix",
                                      "nexthop"])
            sr_param["db_control"] = db_control
            sr_param["device_name"] = device_name
            sr_param["slice_name"] = slice_name
            sr_param["if_name"] = if_name
            sr_param["vlan_id"] = vlan_id
            if route_node.tag == (name_s + "route6"):
                sr_param["address_type"] = 6
            else:
                sr_param["address_type"] = 4
            sr_param["address"] = self.__get_param(route_node,
                                                   name_s + "address",
                                                   str)
            sr_param["prefix"] = self.__get_param(route_node,
                                                  name_s + "prefix",
                                                  int)
            sr_param["nexthop"] = self.__get_param(route_node,
                                                   name_s + "next-hop",
                                                   str)
            func_list.append(
                GlobalModule.DB_CONTROL.write_static_route_detail_info)
            param_list.append(sr_param)

    @decorater_log
    def __set_vrrp_param(self,
                         func_list,
                         param_list,
                         vrrp_node,
                         name_s,
                         db_control,
                         device_name,
                         slice_name,
                         if_name,
                         vlan_id):
        tmp_node = vrrp_node
        vrrp_param = dict.fromkeys(["db_control",
                                    "device_name",
                                    "if_name",
                                    "vlan_id",
                                    "slice_name",
                                    "vrrp_group_id",
                                    "virtual_ipv4_address",
                                    "virtual_ipv6_address",
                                    "priority"])
        vrrp_param["db_control"] = db_control
        vrrp_param["device_name"] = device_name
        vrrp_param["slice_name"] = slice_name
        vrrp_param["if_name"] = if_name
        vrrp_param["vlan_id"] = vlan_id
        if db_control != self.__db_delete and vrrp_node is not None:
            vrrp_group_id = (
                self.__get_param(tmp_node, name_s + "group-id", int))
            vrrp_param["vrrp_group_id"] = vrrp_group_id
            vrrp_param["virtual_ipv4_address"] = (
                self.__get_param(tmp_node,
                                 name_s + "virtual-address",
                                 str))
            vrrp_param["virtual_ipv6_address"] = (
                self.__get_param(tmp_node,
                                 name_s + "virtual-address6",
                                 str))
            vrrp_param["priority"] = (
                self.__get_param(tmp_node, name_s + "priority", int))
        func_list.append(
            GlobalModule.DB_CONTROL.write_vrrp_detail_info)
        param_list.append(vrrp_param)
        if (db_control != self.__db_delete and vrrp_node is not None and
                tmp_node.find(name_s + "track") is not None):
            for track in (tmp_node.find(name_s + "track")
                          .findall(name_s + "interface")):
                tr_param = dict.fromkeys(["db_control",
                                          "vrrp_group_id",
                                          "track_if_name"])
                tr_param["db_control"] = db_control
                tr_param["vrrp_group_id"] = vrrp_group_id
                tr_param["track_if_name"] = (
                    self.__get_param(track, name_s + "name", str))
                if tr_param not in param_list:
                    func_list.append(
                        GlobalModule.DB_CONTROL.write_vrrp_trackif_info)
                    param_list.append(tr_param)

    @decorater_log
    def __set_physicalif_param(self,
                               func_list,
                               param_list,
                               name_s,
                               db_control,
                               device_name,
                               condition=1,
                               node=None,
                               if_name=None):
        '''
        Create parameter for write_physical_if_info.
        Explanation about parameter:
            func_list : Method list (list)
            param_list : Parameter list (list)
            name_s : Name space (str)
            db_control : DB control (str)
            device_name : Device name (str)
            condition : Port status (int)
            node : Node (xml object)
            db_physical : Physical IF information table data (dict)
        '''
        tmp_node = node
        physical_param = dict.fromkeys(["db_control",
                                        "device_name",
                                        "if_name",
                                        "condition"])

        if if_name is not None:
            physical_param["if_name"] = if_name
        else:
            if node is not None:
                physical_param["if_name"] = (
                    self.__get_param(tmp_node, name_s + "name", str))

        physical_param["db_control"] = db_control
        physical_param["device_name"] = device_name
        physical_param["condition"] = condition

        func_list.append(GlobalModule.DB_CONTROL.write_physical_if_info)
        param_list.append(physical_param)

    @staticmethod
    @decorater_log
    def __get_key_recode(db_rows, **keyvalues):
        return_row = None
        for row in db_rows:
            tmp_row = row.copy()
            tmp_row.update(keyvalues)
            if row == tmp_row:
                return_row = tmp_row
                break
        return return_row

    @decorater_log
    def __get_func_all_del_lag(self, dev_node, service):
        '''
        Delete all IF records linked to device name.
        （LAG interface information table,
          LAG member interface information table,
          Physical interface information table,
          Internal Link interface information table,
          BreakoutIF information table）
        Explanation about parameter:
            dev_node : Device node(xml object)
            service : Service type(str)
        '''

        name_s = "{%s}" % (self._namespace.get(service),)
        func_list = []
        param_list = []
        device_name = self.__get_param(dev_node, name_s + "name", str)

        lagif_param = dict.fromkeys(["db_control",
                                     "device_name",
                                     "lag_if_name",
                                     "lag_type",
                                     "minimum_links",
                                     "link_speed"])
        lagif_param["db_control"] = self.__db_delete
        lagif_param["device_name"] = device_name
        func_list.append(GlobalModule.DB_CONTROL.write_lagif_info)
        param_list.append(lagif_param)

        self.__set_physicalif_param(func_list,
                                    param_list,
                                    name_s,
                                    self.__db_delete,
                                    device_name)

        self.__set_lagmemberif_param(func_list,
                                     param_list,
                                     name_s,
                                     self.__db_delete,
                                     device_name)

        self.__set_inner_linkif_param(func_list,
                                      param_list,
                                      name_s,
                                      self.__db_delete,
                                      device_name)

        self.__set_breakoutif_param(func_list,
                                    param_list,
                                    name_s,
                                    self.__db_delete,
                                    device_name)

        return func_list, param_list

    @decorater_log
    def __set_qos_param(self,
                        qos_info,
                        name_s,
                        db_control,
                        cp_param):
        '''
        Edit QoS information to insert or update
        the VLAN interface information table.
        Explanation about parameter:
            qos_info : QoS information object of EC message (dict)
            name_s : XML Name Space
            db_control : DB Control information (str)
            cp_param : Rewrite variable (dict)
        '''

        inflow_shaping_rate = qos_info.find(
            name_s + "inflow-shaping-rate")
        if inflow_shaping_rate is not None:
            if inflow_shaping_rate.get("operation") == "replace" and \
                    inflow_shaping_rate.text is None:
                cp_param["inflow_shaping_rate"] = None
            else:
                cp_param["inflow_shaping_rate"] = float(
                    inflow_shaping_rate.text)

        outflow_shaping_rate = qos_info.find(
            name_s + "outflow-shaping-rate")
        if outflow_shaping_rate is not None:
            if outflow_shaping_rate.get("operation") == "replace" and \
                    outflow_shaping_rate.text is None:
                cp_param["outflow_shaping_rate"] = None
            else:
                cp_param["outflow_shaping_rate"] = float(
                    outflow_shaping_rate.text)

        remark_menu = qos_info.find(name_s + "remark-menu")
        if remark_menu is not None:
            cp_param["remark_menu"] = remark_menu.text

        egress_menu = qos_info.find(name_s + "egress-menu")
        if egress_menu is not None:
            cp_param["egress_queue_menu"] = egress_menu.text

    @decorater_log
    def __set_l2_vrf_param(self,
                           name_s,
                           db_control,
                           device_name,
                           slice_name,
                           if_name,
                           vlan_id,
                           dev_node):
        '''
        Edit VRF information to be inserted to VRF information table.
        Explanation about parameter:
            vrf_info : QoS information object of EC message (dict)
            name_s : Name space
            db_control : DB control information (str)
            cp_param : Rewrite variable (dict)
        '''

        tmp_node = dev_node.find(name_s + "vrf")
        vrf_name = self.__get_param(
            tmp_node, name_s + "vrf-name", str)
        vrf_rt = self.__get_param(
            tmp_node, name_s + "rt", str)
        vrf_rd = self.__get_param(
            tmp_node, name_s + "rd", str)
        vrf_route_id = (
            self.__get_param(
                tmp_node, name_s + "router-id", str))
        vrf_id = self.__get_param(
            tmp_node, name_s + "vrf-id", int)

        if vrf_rd is None and vrf_rt is not None:
            result, data_tpl = GlobalModule.DB_CONTROL.read_dummy_vlan_if_info(
                device_name)
            if result:
                for data in data_tpl:
                    if data.get("slice_name") == slice_name and \
                            data.get("vlan_id") == vlan_id:
                        vrf_rd = data.get("rd")
                        break

        if tmp_node.find(name_s + "loopback") is not None:
            tmp_loopback = tmp_node.find(
                name_s + "loopback")
            vrf_loopback_address = (
                self.__get_param(tmp_loopback, name_s +
                                 "address", str))
            vrf_loopback_prefix = (
                self.__get_param(
                    tmp_loopback, name_s + "prefix", int))
        if tmp_node.find(name_s + "l3-vni") is not None:
            tmp_l3_vni = tmp_node.find(name_s + "l3-vni")
            vni_id = (
                self.__get_param(
                    tmp_l3_vni, name_s + "vni-id", int))
            l3_vlan_id = (
                self.__get_param(
                    tmp_l3_vni, name_s + "vlan-id", int))
        vrf_param = dict.fromkeys([
            "db_control",
            "device_name",
            "if_name",
            "vlan_id",
            "slice_name",
            "vrf_name",
            "vrf_id",
            "rt",
            "rd",
            "router_id",
            "l3_vni",
            "l3_vlan_id",
            "vrf_loopback_interface_address",
            "vrf_loopback_interface_prefix",
        ])
        vrf_param["db_control"] = db_control
        vrf_param["device_name"] = device_name
        vrf_param["slice_name"] = slice_name
        vrf_param["if_name"] = if_name
        vrf_param["vlan_id"] = vlan_id
        if not db_control == "DELETE":
            vrf_param["vrf_name"] = vrf_name
            vrf_param["rt"] = vrf_rt
            vrf_param["rd"] = vrf_rd
            vrf_param["router_id"] = vrf_route_id
            vrf_param["vrf_id"] = vrf_id
            if tmp_node.find(name_s + "l3-vni") is not None:
                vrf_param["l3_vni"] = vni_id
                vrf_param["l3_vlan_id"] = l3_vlan_id
            if tmp_node.find(name_s + "loopback") is not None:
                vrf_param["vrf_loopback_interface_address"] = (
                    vrf_loopback_address)
                vrf_param[
                    "vrf_loopback_interface_prefix"] = (
                        vrf_loopback_prefix)
        return vrf_param

    @decorater_log
    def __get_func_recover_info(self, dev_node, db_control, service):
        '''
        Generate parameters that update the IF name and
        model information (OS / Farm) and login information.
        Usage method:
            write_device_regist_info
            recover_if_info
        Explanation about parameter:
            dev_node : device node (xml object)
            db_control : DB Control (str)
            service : service type (str)
        Return value:
            Method list   : list
            Parameter list : list
         '''
        name_s = "{%s}" % (self._namespace.get(service),)

        device_name = self.__get_param(dev_node, name_s + "name", str)

        phys_convert = []
        for phys_list in dev_node.findall(name_s + "physical-ifs"):
            new_name = self.__get_param(phys_list, name_s + "name", str)
            old_name = self.__get_param(phys_list, name_s + "old-name", str)
            convert = {"name": new_name, "old-name": old_name}
            phys_convert.append(convert)
        lag_convert = []
        for lag_list in dev_node.findall(name_s + "lag-ifs"):
            new_name = self.__get_param(lag_list, name_s + "name", str)
            old_name = self.__get_param(lag_list, name_s + "old-name", str)
            convert = {"name": new_name, "old-name": old_name}
            lag_convert.append(convert)

        func_list = []
        param_list = []

        self.__set_recover_device_param(func_list,
                                        param_list,
                                        name_s,
                                        db_control,
                                        device_name,
                                        dev_node)

        self.__set_recover_lag_param(func_list,
                                     param_list,
                                     db_control,
                                     device_name,
                                     phys_convert,
                                     lag_convert)

        self.__set_recover_physical_param(func_list,
                                          param_list,
                                          db_control,
                                          device_name,
                                          phys_convert,
                                          lag_convert)

        self.__set_recover_breakout_param(func_list,
                                          param_list,
                                          db_control,
                                          device_name,
                                          phys_convert,
                                          lag_convert)

        self.__set_recover_cluster_param(func_list,
                                         param_list,
                                         db_control,
                                         device_name,
                                         phys_convert,
                                         lag_convert)

        self.__set_recover_inner_link_param(func_list,
                                            param_list,
                                            db_control,
                                            device_name,
                                            phys_convert,
                                            lag_convert)

        self.__set_recover_vlan_param(func_list,
                                      param_list,
                                      db_control,
                                      device_name,
                                      phys_convert,
                                      lag_convert)

        self.__set_recover_track_param(func_list,
                                       param_list,
                                       db_control,
                                       device_name,
                                       phys_convert,
                                       lag_convert)

        self.__set_recover_vlan_qos_param(func_list,
                                          param_list,
                                          db_control,
                                          device_name,
                                          phys_convert,
                                          lag_convert,
                                          dev_node,
                                          name_s)

        self.__set_recover_acl_param(func_list,
                                     param_list,
                                     db_control,
                                     device_name,
                                     phys_convert,
                                     lag_convert)

        return func_list, param_list

    @decorater_log
    def __set_recover_device_param(self,
                                   func_list,
                                   param_list,
                                   name_s,
                                   db_control,
                                   device_name,
                                   dev_node
                                   ):
        '''
        Create parameter for reover write_device_regist_info.
        Explanation about parameter:
            func_list : Method list (list)
            param_list : Parameter list (list)
            name_s : Name space (str)
            db_control : DB control (str)
            device_name : Device name (str)
            dev_node : EC Message（deviceXML）
        '''
        is_ok, db_devices = \
            GlobalModule.DB_CONTROL.read_device_regist_info(device_name)
        if not is_ok:
            err_mes = ('DB Fault read_device_regist_info(device_name = %s)' %
                       (device_name,))
            GlobalModule.EM_LOGGER.debug(err_mes)
            raise ValueError("DB Control ERROR")

        eq_node = dev_node.findall(name_s + "equipment")[0]
        platform = self.__get_param(eq_node, name_s + "platform", str)
        os = self.__get_param(eq_node, name_s + "os", str)
        firmware = self.__get_param(eq_node, name_s + "firmware", str)
        loginid = self.__get_param(eq_node, name_s + "loginid", str)
        password = self.__get_param(eq_node, name_s + "password", str)

        param = db_devices[0]
        param["db_control"] = db_control
        param["device_name"] = device_name
        param["platform_name"] = platform
        param["os"] = os
        param["firm_version"] = firmware
        param["username"] = loginid
        param["password"] = password

        func_list.append(GlobalModule.DB_CONTROL.write_device_regist_info)
        param_list.append(param)

    @decorater_log
    def __set_recover_lag_param(self,
                                func_list,
                                param_list,
                                db_control,
                                device_name,
                                phys_convert,
                                lag_convert):
        '''
        Create parameter for recover_if_info（LAG）.
        Explanation about parameter:
            func_list : Method list (list)
            param_list : Parameter list (list)
            db_control : DB control (str)
            device_name : Device name (str)
            phys_convert : Table for converting physical IF
            lag_convert : Table for converting LAG IF
        '''
        for lag in lag_convert:
            if lag.get("old-name") == lag.get("name"):
                continue
            param = dict.fromkeys(["db_control",
                                   "table_name",
                                   "if_name_column",
                                   "if_name_new",
                                   "device_name",
                                   "lag_if_name"])
            param["db_control"] = db_control
            param["table_name"] = self.table_LagIfInfo
            param["if_name_column"] = "lag_if_name"
            param["if_name_new"] = lag.get("name")
            param["device_name"] = device_name
            param["lag_if_name"] = lag.get("old-name")

            func_list.append(GlobalModule.DB_CONTROL.recover_if_info)
            param_list.append(param)

    @decorater_log
    def __set_recover_physical_param(self,
                                     func_list,
                                     param_list,
                                     db_control,
                                     device_name,
                                     phys_convert,
                                     lag_convert):
        '''
        Create parameter for recover_if_info（Physical）.
        Explanation about parameter:
            func_list : Method list (list)
            param_list : Parameter list (list)
            device_name : Device name (str)
            device_name : Device name (str)
            phys_convert : Table for converting physical IF
            lag_convert : Table for converting LAG IF
        '''
        is_ok, db_physicals = \
            GlobalModule.DB_CONTROL.read_physical_if_info(device_name)
        if not is_ok:
            err_mes = ('DB Fault read_physical_if_info(device_name = %s)' %
                       (device_name,))
            GlobalModule.EM_LOGGER.debug(err_mes)
            raise ValueError("DB Control ERROR")

        for db_physical in db_physicals:
            old_name = db_physical.get("if_name")
            new_name = self._convert_ifname(
                old_name, phys_convert, lag_convert, self._if_type_phy)
            if old_name == new_name:
                continue
            param = dict.fromkeys(["db_control",
                                   "table_name",
                                   "if_name_column",
                                   "if_name_new",
                                   "device_name"])
            param["db_control"] = db_control
            param["table_name"] = self.table_PhysicalIfInfo
            param["if_name_column"] = "if_name"
            param["if_name_new"] = new_name
            param["device_name"] = device_name
            param["if_name"] = old_name

            func_list.append(GlobalModule.DB_CONTROL.recover_if_info)
            param_list.append(param)

    @decorater_log
    def __set_recover_breakout_param(self,
                                     func_list,
                                     param_list,
                                     db_control,
                                     device_name,
                                     phys_convert,
                                     lag_convert):
        '''
        Create parameter for recover_if_info（Breakout）.
        Explanation about parameter:
            func_list : Method list (list)
            param_list : Parameter list (list)
            db_control : DB control (str)
            device_name : Device name (str)
            phys_convert : Table for converting physical IF
            lag_convert : Table for converting LAG IF
        '''
        is_ok, db_breakouts = \
            GlobalModule.DB_CONTROL.read_breakout_if_info(device_name)
        if not is_ok:
            err_mes = ('DB Fault read_breakout_if_info(device_name = %s)' %
                       (device_name,))
            GlobalModule.EM_LOGGER.debug(err_mes)
            raise ValueError("DB Control ERROR")

        for db_breakout in db_breakouts:
            old_name = db_breakout.get("base_interface")
            new_name = self._convert_ifname(
                old_name, phys_convert, lag_convert, self._if_type_phy)
            if old_name == new_name:
                continue
            param = dict.fromkeys(["db_control",
                                   "table_name",
                                   "if_name_column",
                                   "if_name_new",
                                   "device_name",
                                   "base_interface"])
            param["db_control"] = db_control
            param["table_name"] = self.table_BreakoutIfInfo
            param["if_name_column"] = "base_interface"
            param["if_name_new"] = new_name
            param["device_name"] = device_name
            param["base_interface"] = old_name

            func_list.append(GlobalModule.DB_CONTROL.recover_if_info)
            param_list.append(param)

    @decorater_log
    def __set_recover_cluster_param(self,
                                    func_list,
                                    param_list,
                                    db_control,
                                    device_name,
                                    phys_convert,
                                    lag_convert):
        '''
        Create parameter for recover_if_info（Inter-Cluster Link）.
        Explanation about parameter:
            func_list : Method list (list)
            param_list : Parameter list (list)
            db_control : DB control (str)
            device_name : Device name (str)
            phys_convert : Table for converting physical IF
            lag_convert : Table for converting LAG IF
        '''
        is_ok, db_clusters = \
            GlobalModule.DB_CONTROL.read_cluster_link_if_info(device_name)
        if not is_ok:
            err_mes = ('DB Fault read_cluster_link_if_info(device_name = %s)' %
                       (device_name,))
            GlobalModule.EM_LOGGER.debug(err_mes)
            raise ValueError("DB Control ERROR")

        for db_cluster in db_clusters:
            old_name = db_cluster.get("if_name")
            new_name = self._convert_ifname(
                old_name, phys_convert, lag_convert, "all")
            if old_name == new_name:
                continue
            param = dict.fromkeys(["db_control",
                                   "table_name",
                                   "if_name_column",
                                   "if_name_new",
                                   "device_name",
                                   "if_name"])
            param["db_control"] = db_control
            param["table_name"] = self.table_ClusterLinkIfInfo
            param["if_name_column"] = "if_name"
            param["if_name_new"] = new_name
            param["device_name"] = device_name
            param["if_name"] = old_name

            func_list.append(GlobalModule.DB_CONTROL.recover_if_info)
            param_list.append(param)

    @decorater_log
    def __set_recover_inner_link_param(self,
                                       func_list,
                                       param_list,
                                       db_control,
                                       device_name,
                                       phys_convert,
                                       lag_convert):
        '''
        Create parameter for recover_if_info（Inner Link）.
        Explanation about parameter:
            func_list : Method list (list)
            param_list : Parameter list (list)
            db_control : DB control (str)
            device_name : Device name (str)
            phys_convert : Table for converting physical IF
            lag_convert : Table for converting LAG IF
        '''
        is_ok, db_inner_ifs = \
            GlobalModule.DB_CONTROL.read_inner_link_if_info(device_name)
        if not is_ok:
            err_mes = ('DB Fault read_inner_link_if_info(device_name = %s)' %
                       (device_name,))
            GlobalModule.EM_LOGGER.debug(err_mes)
            raise ValueError("DB Control ERROR")

        for db_inner_if in db_inner_ifs:
            old_name = db_inner_if.get("if_name")
            new_name = self._convert_ifname(
                old_name, phys_convert, lag_convert, "all")
            if old_name == new_name:
                continue
            param = dict.fromkeys(["db_control",
                                   "table_name",
                                   "if_name_column",
                                   "if_name_new",
                                   "device_name",
                                   "if_name"])

            param["db_control"] = db_control
            param["table_name"] = self.table_InnerLinkIfInfo
            param["if_name_column"] = "if_name"
            param["if_name_new"] = new_name
            param["device_name"] = device_name
            param["if_name"] = old_name

            func_list.append(GlobalModule.DB_CONTROL.recover_if_info)
            param_list.append(param)

    @decorater_log
    def __set_recover_vlan_param(self,
                                 func_list,
                                 param_list,
                                 db_control,
                                 device_name,
                                 phys_convert,
                                 lag_convert):
        '''
        Create parameter for recover_if_info（VLAN）.
        Explanation about parameter:
            func_list : Method list (list)
            param_list : Parameter list (list)
            db_control : DB control (str)
            device_name : Device name (str)
            phys_convert : Table for converting physical IF
            lag_convert : Table for converting LAG IF
        '''
        is_ok, db_vlans = \
            GlobalModule.DB_CONTROL.read_vlanif_info(device_name)
        if not is_ok:
            err_mes = ('DB Fault read_vlanif_info(device_name = %s)' %
                       (device_name,))
            GlobalModule.EM_LOGGER.debug(err_mes)
            raise ValueError("DB Control ERROR")

        for db_vlan in db_vlans:
            old_name = db_vlan.get("if_name")
            new_name = self._convert_ifname(
                old_name, phys_convert, lag_convert, "all")
            if old_name == new_name:
                continue
            param = dict.fromkeys(["db_control",
                                   "table_name",
                                   "if_name_column",
                                   "if_name_new",
                                   "device_name",
                                   "if_name",
                                   "vlan_id",
                                   "slice_name"])
            param["db_control"] = db_control
            param["table_name"] = self.table_VlanIfInfo
            param["if_name_column"] = "if_name"
            param["if_name_new"] = new_name
            param["device_name"] = device_name
            param["if_name"] = old_name
            param["vlan_id"] = db_vlan.get("vlan_id")
            param["slice_name"] = db_vlan.get("slice_name")

            func_list.append(GlobalModule.DB_CONTROL.recover_if_info)
            param_list.append(param)

    @decorater_log
    def __set_recover_track_param(self,
                                  func_list,
                                  param_list,
                                  db_control,
                                  device_name,
                                  phys_convert,
                                  lag_convert):
        '''
        Create parameter for recover_if_info（VRRP track interface）.
        Explanation about parameter:
            func_list : Method list (list)
            param_list : Parameter list (list)
            db_control : DB control (str)
            device_name : Device name (str)
            phys_convert : Table for converting physical IF
            lag_convert : Table for converting LAG IF
        '''
        is_ok, db_tracks = \
            GlobalModule.DB_CONTROL.read_vrrp_trackif_info(device_name)
        if not is_ok:
            err_mes = ('DB Fault read_vrrp_trackif_info(device_name = %s)' %
                       (device_name,))
            GlobalModule.EM_LOGGER.debug(err_mes)
            raise ValueError("DB Control ERROR")
        for db_track in db_tracks:
            old_name = db_track.get("track_if_name")
            new_name = self._convert_ifname(
                old_name, phys_convert, lag_convert, "all")
            if old_name == new_name:
                continue
            param = dict.fromkeys(["db_control",
                                   "table_name",
                                   "if_name_column",
                                   "if_name_new",
                                   "vrrp_group_id",
                                   "track_if_name"])
            param["db_control"] = db_control
            param["table_name"] = self.table_VrrpTrackIfInfo
            param["if_name_column"] = "track_if_name"
            param["if_name_new"] = new_name
            param["vrrp_group_id"] = db_track.get("vrrp_group_id")
            param["track_if_name"] = old_name

            func_list.append(GlobalModule.DB_CONTROL.recover_if_info)
            param_list.append(param)

    @decorater_log
    def __set_recover_vlan_qos_param(self,
                                     func_list,
                                     param_list,
                                     db_control,
                                     device_name,
                                     phys_convert,
                                     lag_convert,
                                     dev_node,
                                     name_s):
        '''
        Create parameter for write_vlanif_info.
        Explanation about parameter:
            func_list : Method list (list)
            param_list : Parameter list (list)
            db_control : DB control (str)
            device_name : Device name (str)
            phys_convert : Table for converting physical IF
            lag_convert : Table for converting LAG IF
            dev_node : EC Information（XML）
            name_s : XML Name space.
        '''
        inflow_shaping_rate = {}
        outflow_shaping_rate = {}
        remark_menu = {}
        egress_menu = {}

        qos_node = dev_node.find(name_s + "qos")
        if qos_node is None:
            return
        tmp = qos_node.find(name_s + "inflow-shaping-rate")
        if tmp is not None:
            if tmp.get("operation") == "delete":
                inflow_shaping_rate["operation"] = "delete"
            else:
                inflow_shaping_rate["operation"] = "merge"
                inflow_shaping_rate["value"] = float(tmp.text)

        tmp = qos_node.find(name_s + "outflow-shaping-rate")
        if tmp is not None:
            if tmp.get("operation") == "delete":
                outflow_shaping_rate["operation"] = "delete"
            else:
                outflow_shaping_rate["operation"] = "merge"
                outflow_shaping_rate["value"] = float(tmp.text)

        tmp = qos_node.find(name_s + "remark-menu")
        if tmp is not None:
            if tmp.get("operation") == "delete":
                remark_menu["operation"] = "delete"
            else:
                remark_menu["operation"] = "merge"
                remark_menu["value"] = tmp.text

        tmp = qos_node.find(name_s + "egress-menu")
        if tmp is not None:
            if tmp.get("operation") == "delete":
                egress_menu["operation"] = "delete"
            else:
                egress_menu["operation"] = "merge"
                egress_menu["value"] = tmp.text

        ok, db_vlan_infos = \
            GlobalModule.DB_CONTROL.read_vlanif_info(device_name)
        if not ok:
            GlobalModule.EM_LOGGER.debug(
                'DB Fault read_vlanif_info(device_name = %s)' % (device_name,))
            raise ValueError("DB Control (VLANIFINFO) ERROR")

        for db_vlan in db_vlan_infos:
            param = db_vlan
            param["db_control"] = db_control
            param["device_name"] = device_name

            param["if_name"] = self._convert_ifname(
                db_vlan.get("if_name"), phys_convert, lag_convert, "all")

            if inflow_shaping_rate.get("operation") == "delete":
                param["inflow_shaping_rate"] = None
            elif inflow_shaping_rate.get("operation") == "merge":
                param["inflow_shaping_rate"] = inflow_shaping_rate.get("value")

            if outflow_shaping_rate.get("operation") == "delete":
                param["outflow_shaping_rate"] = None
            elif outflow_shaping_rate.get("operation") == "merge":
                param["outflow_shaping_rate"] = outflow_shaping_rate.get(
                    "value")

            if remark_menu.get("operation") == "delete":
                param["remark_menu"] = None
            elif remark_menu.get("operation") == "merge":
                param["remark_menu"] = remark_menu.get("value")

            if egress_menu.get("operation") == "delete":
                param["egress_queue_menu"] = None
            elif egress_menu.get("operation") == "merge":
                param["egress_queue_menu"] = egress_menu.get("value")

            func_list.append(GlobalModule.DB_CONTROL.write_vlanif_info)
            param_list.append(param)

        return func_list, param_list

    @decorater_log
    def __set_recover_acl_param(self,
                                func_list,
                                param_list,
                                db_control,
                                device_name,
                                phys_convert,
                                lag_convert):
        '''
        Creates parameter for recover_if_info（ACL)
        Explanation about parameter:
            func_list : Method list (list)
            param_list : Parameter list (list)
            db_control : DB control (str)
            device_name : Device name (str)
            phys_convert : Physical IF conversion table
            lag_convert : LAGIF conversion table
        '''
        is_ok, db_acls = \
            GlobalModule.DB_CONTROL.read_acl_info(device_name)
        if not is_ok:
            err_mes = ('DB Fault read_acl_info(device_name = %s)' %
                       (device_name,))
            GlobalModule.EM_LOGGER.debug(err_mes)
            raise ValueError("DB Control ERROR")

        for db_acl in db_acls:
            old_name = db_acl.get("if_name")
            new_name = self._convert_ifname(
                old_name, phys_convert, lag_convert, "all")
            if old_name == new_name:
                continue
            param = dict.fromkeys(["db_control",
                                   "table_name",
                                   "if_name_column",
                                   "if_name_new",
                                   "device_name",
                                   "acl_id"])
            param["db_control"] = db_control
            param["table_name"] = self.table_ACLInfo
            param["if_name_column"] = "if_name"
            param["if_name_new"] = new_name
            param["device_name"] = device_name
            param["acl_id"] = db_acl.get("acl_id")

            func_list.append(GlobalModule.DB_CONTROL.recover_if_info)
            param_list.append(param)

    @decorater_log
    def _convert_ifname(self, old_ifname,
                        phys_convert,
                        lag_convert,
                        if_type="all"):
        '''
        In accordance with the interface name conversion table,
        the interface name before the restoration is converted
        into the interface name after restoration.
        Explanation about parameter:
            old_ifname : Interface name before the restoration
            phys_convert : Table for converting physical IF
            lag_convert : Table for converting LAG IF
            if_type : Interface type
        Return Value :
            Interface name after restoration
        Excepton :
            ValueError : Fault Convert
        '''
        converted_if_name = None
        if if_type == self._if_type_phy or if_type == "all":
            for if_info in phys_convert:
                if if_info.get("old-name") == old_ifname:
                    converted_if_name = if_info.get("name")
                    break
        if converted_if_name is None and \
                (if_type == self._if_type_lag or if_type == "all"):
            for if_info in lag_convert:
                if if_info.get("old-name") == old_ifname:
                    converted_if_name = if_info.get("name")
                    break
        if converted_if_name is None:
            GlobalModule.EM_LOGGER.debug(
                'if convert error. error_ifname = %s' % (old_ifname))
            raise ValueError(old_ifname + " " + if_type)
        GlobalModule.EM_LOGGER.debug(
            'if convert success. old_ifname = %s , new_ifname = %s' %
            (old_ifname, converted_if_name))
        return converted_if_name

    @decorater_log
    def __set_dummy_param(self,
                          tmp_func_list,
                          tmp_param_list,
                          dev_node,
                          dummy_cp_node,
                          name_s,
                          db_control,
                          device_name,
                          slice_name):
        '''
        Instert into the dummy VLAN interface information table.
        Explanation about parameter:
            tmp_func_list : Method list (list)
            tmp_param_list : Parameter list (list)
            dev_node : device node (xml object)
            dummy_cp_node : Dummy cp information
            name_s : Name space
            db_control : DB control information
            device_name : Device name
            slice_name : Slice name
        '''
        tmp_node = dev_node.find(name_s + "vrf")
        vrf_name = self.__get_param(
            tmp_node, name_s + "vrf-name", str)
        vrf_rt = self.__get_param(
            tmp_node, name_s + "rt", str)
        vrf_rd = self.__get_param(
            tmp_node, name_s + "rd", str)
        vrf_route_id = (
            self.__get_param(
                tmp_node, name_s + "router-id", str))
        vrf_id = self.__get_param(
            tmp_node, name_s + "vrf-id", int)
        if tmp_node.find(name_s + "loopback") is not None:
            tmp_loopback = tmp_node.find(
                name_s + "loopback")
            vrf_loopback_address = (
                self.__get_param(tmp_loopback, name_s +
                                 "address", str))
            vrf_loopback_prefix = (
                self.__get_param(
                    tmp_loopback, name_s + "prefix", int))
        else:
            vrf_loopback_address = None
            vrf_loopback_prefix = None

        if vrf_rt is None or vrf_rd is None or vrf_route_id is None or \
                vrf_loopback_address is None or vrf_loopback_prefix is None:
            result, data_tpl = GlobalModule.DB_CONTROL.read_vrf_detail_info(
                device_name)
            if result:
                vlan_id = self.__get_param(
                    dummy_cp_node, name_s + "vlan-id", int)
                for data in data_tpl:
                    if data.get("slice_name") == slice_name and \
                            data.get("vlan_id") == vlan_id:
                        if vrf_rt is None:
                            vrf_rt = data.get("rt")
                        if vrf_rd is None:
                            vrf_rd = data.get("rd")
                        if vrf_route_id is None:
                            vrf_route_id = data.get("router_id")
                        if vrf_loopback_address is None:
                            vrf_loopback_address = data.get(
                                "vrf_loopback_interface_address")
                        if vrf_loopback_prefix is None:
                            vrf_loopback_prefix = data.get(
                                "vrf_loopback_interface_prefix")
                        break

        dummy_cp_param = dict.fromkeys([
            "db_control",
            "device_name",
            "vlan_id",
            "slice_name",
            "vni",
            "irb_ipv4_address",
            "irb_ipv4_prefix",
            "vrf_name",
            "vrf_id",
            "rt",
            "rd",
            "router_id",
            "vrf_loopback_interface_address",
            "vrf_loopback_interface_prefix"])
        dummy_cp_param["db_control"] = db_control
        dummy_cp_param["device_name"] = device_name
        dummy_cp_param["slice_name"] = slice_name
        dummy_cp_param["vlan_id"] = (self.__get_param(
            dummy_cp_node, name_s + "vlan-id", int))
        dummy_cp_param["vni"] = (self.__get_param(
            dummy_cp_node, name_s + "vni", int))

        dummy_cp_param["vrf_name"] = vrf_name
        dummy_cp_param["vrf_id"] = vrf_id
        dummy_cp_param["rt"] = vrf_rt
        dummy_cp_param["rd"] = vrf_rd
        dummy_cp_param["router_id"] = vrf_route_id
        dummy_cp_param["vrf_loopback_interface_address"] = (
            vrf_loopback_address)
        dummy_cp_param["vrf_loopback_interface_prefix"] = (
            vrf_loopback_prefix)

        irb_info = dummy_cp_node.find(name_s + "irb")
        if irb_info is not None:
            self.__set_dummy_irb_param(irb_info,
                                       name_s,
                                       db_control,
                                       dummy_cp_param)
        tmp_func_list.append(
            GlobalModule.DB_CONTROL.write_dummy_vlan_if_info)
        tmp_param_list.append(dummy_cp_param)

    @decorater_log
    def __set_dummy_irb_param(self,
                              irb_info,
                              name_s,
                              db_control,
                              param):
        '''
        Edits IRB information to be inserted into the dummy VLAN interface information table.
        Explanation about parameter:
            irb_info : IRB information object of EC message (dict)
            name_s : Name space
            db_control : DB control information (str)
            cp_param : Rewrite varaible (dict)
        '''
        tmp = irb_info.find(name_s + "physical-ip-address")
        param["irb_ipv4_address"] = self.__get_param(
            tmp, name_s + "address", str)
        param["irb_ipv4_prefix"] = self.__get_param(
            tmp, name_s + "prefix", int)

    @decorater_log
    def __set_irb_param(self,
                        irb_info,
                        name_s,
                        db_control,
                        param):
        '''
        Edits IRB information to be inserted into the VLAN interface information table.
        Explanation about parameter:
            irb_info : IRB information object of EC message (dict)
            name_s : Name space
            db_control : DB control information (str)
            cp_param : Rewrite variable (dict)
        '''

        tmp = irb_info.find(name_s + "physical-ip-address")
        param["irb_ipv4_address"] = self.__get_param(
            tmp, name_s + "address", str)
        param["irb_ipv4_prefix"] = self.__get_param(
            tmp, name_s + "prefix", int)
        param["virtual_mac_address"] = self.__get_param(
            irb_info, name_s + "virtual-mac-address", str)
        tmp_virtual = irb_info.find(name_s + "virtual-gateway")
        param["virtual_gateway_address"] = self.__get_param(
            tmp_virtual, name_s + "address", str)
        param["virtual_gateway_prefix"] = self.__get_param(
            tmp_virtual, name_s + "prefix", int)

    @staticmethod
    @decorater_log
    def get_anycast_id(anycast_ip_address):
        get_anycast_id = -1
        is_ok, multi_homings = GlobalModule.DB_CONTROL.read_multi_homing_all_info()
        if not is_ok:
            err_mes = (
                'DB Fault read_multi_homing_all_info')
            GlobalModule.EM_LOGGER.debug(err_mes)
            raise ValueError("DB Control ERROR")
        anycast_id_list = [0]
        for mh_row in multi_homings:
            if mh_row["anycast_address"] == anycast_ip_address:
                get_anycast_id = mh_row["anycast_id"]
                break
            else:
                anycast_id_list.append(mh_row["anycast_id"])
        if get_anycast_id < 0:
            get_anycast_id = max(anycast_id_list) + 1
        return get_anycast_id

    @decorater_log_in_out
    def _get_acl_del_if(self, device_name, acl_id):
        is_ok, db_acl_del = \
            self._read_acl_deleteif_info(device_name, acl_id)
        if not is_ok:
            err_mes = ('DB Fault read_acl_deleteif_info(device_name = %s,' %
                       (device_name,) + ' acl_id = %s)' % (acl_id,))
            GlobalModule.EM_LOGGER.debug(err_mes)
            raise ValueError("DB Control ERROR")
        else:
            if_name = db_acl_del["if_name"]
        return if_name

    @decorater_log_in_out
    def _read_acl_deleteif_info(self, device_name, acl_id):
        '''
        Method which returns the information of ACL configuration information table
        Parameter:
            device_name: Device name
        Return value:
            Execution result : boolean(True or False)
            Refer to ACL configuration information table : tuple
        '''
        if_name = {}
        if not self.__check_parameter(device_name, str, not_null=True):
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False, None
        is_ok, acl_list = GlobalModule.DB_CONTROL.read_acl_all_info()
        if not is_ok:
            err_mes = (
                'DB Fault read_acl_all_info')
            GlobalModule.EM_LOGGER.debug(err_mes)
            raise ValueError("DB Control ERROR")
        else:
            for acl in acl_list:
                if acl["device_name"] == device_name and acl["acl_id"] == acl_id:
                    if_name["if_name"] = acl["if_name"]
                    return True, if_name

    @decorater_log
    def _check_acl_detail_all_del(self, device_name, acl_detail_params):
        '''
        Check which is intended for deleting the entire data within ACL information table
        when only the registered information to be deleted exists in ACL details information table after the table has been searched.
        Parameter:
            device_name: Device name
            acl_detail_params : ACL detail information
        Return value:
            Execution result : boolean(True or False)
        '''
        acl_id = acl_detail_params[0].get("acl_id")
        is_ok, data1 = GlobalModule.DB_CONTROL.read_acl_detail_info(
            device_name)
        if not is_ok:
            err_mes = ('DB Fault read_acl_detail_info')
            GlobalModule.EM_LOGGER.debug(err_mes)
            raise ValueError("DB Control ERROR")

        acl_detail_count = 0
        is_all_acl_detail_del = False
        for db_data in data1:
            if db_data["acl_id"] == acl_id:
                acl_detail_count = acl_detail_count + 1
        if acl_detail_count == len(acl_detail_params):
            is_all_acl_detail_del = True
        return is_all_acl_detail_del

    @staticmethod
    @decorater_log
    def __check_parameter(param, parms_class, not_null=False, b_size=None):
        '''
        Confirm the type of argument to be handed over as SQL
        Parameter:
            param : Argument to be checked
            parms_class : Type of DB side
            not_null : NOT NULL restriction (Default is False)
            b_size : Length of item (byte size)
        Return value:
            Execution result : boolean
        '''
        is_ok = True
        if param is None:
            is_ok = False if not_null else True
            if not is_ok:
                GlobalModule.EM_LOGGER.debug(
                    'Fault Parameter = %s (not_null is %s)'
                    % (param, not_null))
            return is_ok
        if b_size and parms_class is str and len(param) > b_size:
            is_ok = is_ok and False
        tmp = True
        if parms_class is str:
            tmp = isinstance(param, str) or isinstance(param, unicode)
        else:
            tmp = isinstance(param, parms_class)
        is_ok = is_ok and True if tmp else False
        if not is_ok:
            GlobalModule.EM_LOGGER.debug(
                'Fault Parameter = %s (class is %s)'
                % (param, isinstance(param, parms_class)))
        return is_ok


class EmStatus(object):
    '''
    EM status management class
    '''

    lock = threading.Lock()
    em_status = EmSysCommonUtilityDB.STATE_STOP

    @classmethod
    def get_em_status(cls):
        '''
        Launched from EmNetconfSSHServer class and returns current status.
        Explanation about parameter:
            None
        Explanation about return value:
            em_status:EMSystem status
        '''
        with cls.lock:
            status = cls.em_status
        return status

    @classmethod
    @decorater_log
    def set_em_status(cls, status):
        '''
        Launched from EmNetconfSSHServer class and updates current status.
        Explanation about parameter:
            status: Update status
        Explanation about return value:
            None
        '''
        with cls.lock:
            cls.em_status = status
