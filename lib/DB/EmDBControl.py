#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmDBControl.py
'''
DB Control module.
'''
from oslo_db.sqlalchemy.engines import create_engine
from uuid import UUID

import GlobalModule
from EmCommonLog import decorater_log
from EmCommonLog import decorater_log_in_out
from EmSysCommonUtilityDB import EmSysCommonUtilityDB


class EmDBControl(object):
    '''
    DB Control class.
    '''
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
    table_DeviceConfigrationinfo = "DeviceConfigrationinfo"
    table_NvrAdminPasswordMgmt = "NvrAdminPasswordMgmt"

    __delete_flg = "DELETE"

    @decorater_log
    def __init__(self):
        '''
        Initialization.
        Explanation about parameter:
            None.
        Return value:
            None.
        '''
        port_number = None
        user_name = None
        password = None
        db_table = None
        is_conf, address = (
            GlobalModule.EM_CONFIG.read_sys_common_conf('DB_server_address'))
        if is_conf:
            is_conf, port_number = (
                GlobalModule.EM_CONFIG.read_sys_common_conf('DB_access_port'))
        if is_conf:
            is_conf, user_name = (
                GlobalModule.EM_CONFIG.read_sys_common_conf('DB_user'))
        if is_conf:
            is_conf, password = (
                GlobalModule.EM_CONFIG.read_sys_common_conf('DB_access_pass'))
        if is_conf:
            is_conf, db_table = (
                GlobalModule.EM_CONFIG.read_sys_common_conf('DB_access_table'))

        if not is_conf:
            GlobalModule.EM_LOGGER.debug(
                'address:%s port:%s user:%s pass:%s table:%s' %
                (address, port_number, user_name, password, db_table))
            raise IOError

        self.url = ('postgresql://%s' % (user_name,) +
                    (':%s' % (password,) if password else '') +
                    '@%s:%s/%s' % (address, port_number, db_table))

        GlobalModule.EM_LOGGER.debug('URL = %s' % (self.url,))
        try:
            self.engine = create_engine(self.url)
        except Exception, ex_message:
            GlobalModule.EM_LOGGER.error(
                '305003 Database Control Error')
            GlobalModule.EM_LOGGER.debug(
                'db_error_message = %s' % (ex_message,))
            raise
        GlobalModule.EM_LOGGER.debug('end')


    @decorater_log
    def __connect_db(self):
        '''
        Connected to each DB
        Explanation about the parameters:
            url : Location of each DB
        Return value:
            conn : Connection object to each DB
        '''
        conn = self.engine.connect()
        GlobalModule.EM_LOGGER.info('105001 Database Control Start')

        return conn

    @staticmethod
    @decorater_log
    def __close_db(conn):
        '''
        Close the connection to each DB.
        Explanation about parameter:
            connect : Connection object to each DB
        Return value:
            None
        '''
        if conn and not conn.closed:
            conn.close()
        GlobalModule.EM_LOGGER.info('105002 Database Control End')

    @staticmethod
    @decorater_log
    def __close_result(result):
        '''
        Close the ResultProxy object.
        Parameter:
            result : ResultProxy object
        Return value:
            None
        '''
        if result and not result.closed:
            result.close()

    @staticmethod
    @decorater_log
    def __check_parameter(param, parms_class, not_null=False, b_size=None):
        '''
        Confirm the type of the argument to be delivered as the SQL.
        Parameter:
            param : Argument targetted for checking
            parms_class : type of DB
            not_null : NOT NULL restriction (default is set to False)
            b_size : Length of the item (byte size)
        Return value:
            Execution results : boolean
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

    @staticmethod
    @decorater_log
    def __gen_upsert_sql(table_name, where_query_str, *table_cols):
        '''
        Create INSERT/UPDATE sentences.
        Parameter:
            table_name : Table name
            where_query_str : List of letter strings which start with where and can work as phrases.
            *table_cols : DB item name (set any numbers you like)
        Return value:
            INSERT sentence : str
            UPDATE sentence : str
        '''
        insert_col_list = []
        values_list = []
        update_list = []
        for col in table_cols:
            if insert_col_list:
                insert_col_list.append(",%s" % col)
            else:
                insert_col_list.append("%s" % col)
            if values_list:
                values_list.append(",%s")
            else:
                values_list.append("%s")
            if update_list:
                update_list.append("     ,%s" % col + "= %s")
            else:
                update_list.append("     %s" % col + "= %s")

        query_str = []
        query_str.append("INSERT INTO")
        query_str.append("    %s" % (table_name,))
        query_str.append("(")
        query_str.extend(insert_col_list)
        query_str.append(")")
        query_str.append("VALUES")
        query_str.append("(")
        query_str.extend(values_list)
        query_str.append(")")
        insert_query = ' '.join(query_str)

        query_str = []
        query_str.append("UPDATE")
        query_str.append("    %s" % (table_name,))
        query_str.append("SET")
        query_str.extend(update_list)
        query_str.extend(where_query_str)
        update_query = ' '.join(query_str)

        return insert_query, update_query

    @staticmethod
    @decorater_log
    def __gen_delete_sql(table_name, where_query_str):
        '''
        Create DELETE sentence.
        Parameter:
            table_name : Table name
            where_query_str : List of letter strings which start with where.
        Return value:
            DELETE sentence : str
        '''
        query_str = []
        query_str.append("DELETE")
        query_str.append("    FROM")
        query_str.append("        %s" % (table_name,))
        query_str.extend(where_query_str)
        return ' '.join(query_str)

    @staticmethod
    @decorater_log
    def __gen_select_sql(table_name, where_query_str):
        '''
        Create SELECT sentence
        Parameter:
            table_name : Table name
            where_query_str : List of letter strings which start with where.
        Return value:
            SELECT sentence: str
        '''
        query_str = []
        query_str.append("SELECT")
        query_str.append("    *")
        query_str.append("    FROM")
        query_str.append("        %s" % (table_name,))
        query_str.extend(where_query_str)
        return ' '.join(query_str)

    @decorater_log
    def __output_select_result(self, result):
        '''
        Convert the SELECT results to the style as below.
        (
             { row1 ; value , row2 : value , row3 : value ...} (first line)
            ,{ row1 ; value , row2 : value , row3 : value ...} (second line)
            ...
        )
        For your information, in case of the "0" line, blank tuple should be returned.
        Parameter:
            result:ResultProxy object
        Return value:
            Acquisition result : tuple
        '''
        keys = result.keys()
        rowlist = []
        while True:
            row = result.fetchone()
            if row is None:
                break
            rowdict = {}
            for key in keys:
                if isinstance(row[key], unicode):
                    rowdict[str(key)] = str(row[key])
                else:
                    rowdict[str(key)] = row[key]
            rowlist.append(rowdict)
        returnval = tuple(rowlist)
        self.__close_result(result)
        return returnval

    @decorater_log
    def __execute_read_sql(self, where_tuple, sql):
        '''
        Issue SELECT sentence in data reading style.
        Parameter:
            where_tuple:WHERE phrase tuple (tuple)
            sql:SQL sentence to be issued (SELECT sentence only) (str)
        Return value:
            Execution result : boolean
            Acquisition result : tuple
        '''
        conn = None
        GlobalModule.EM_LOGGER.debug('EXEC SQL : ' + sql % where_tuple)
        try:
            conn = self.__connect_db()
            result = conn.execute(sql, where_tuple)
            out_data = self.__output_select_result(result)
            is_ok = True
        except Exception, ex_message:  
            GlobalModule.EM_LOGGER.error(
                '305003 Database Control Error')
            GlobalModule.EM_LOGGER.debug(
                'db_error_message = %s' % (ex_message,))
            out_data = None
            is_ok = False
        finally:
            self.__close_db(conn)
        return is_ok, out_data

    @decorater_log
    def __exec_write_sql(self,
                         select_query,
                         insert_query,
                         update_query,
                         delete_query,
                         upsert_param,
                         where_param,
                         db_control=None,
                         conn=None):
        '''
        Conduct DB processing of data reading style (SQL issue).
        Parameter:
            select_query : SELECT sentence (str)
            insert_query : INSERT sentence (str)
            update_query : UPDATE sentence (str)
            delete_query : DELETE sentence (str)
            upsert_param : UPDATE/INSERT parameter (tuple)
            where_param :  WHERE phrase parameter (tuple)
            db_control : DB control (DELETE should be launched in case of DELETE.)
            conn : Connection object
        Return value:
            Execution result : boolean
        '''
        is_auto_commit = False
        result = None
        return_val = False
        try:
            if conn is None:
                is_auto_commit = True
                conn = self.__connect_db()
            if db_control == self.__delete_flg:
                GlobalModule.EM_LOGGER.debug(
                    'EXEC SQL : ' + delete_query % where_param)
                result = conn.execute(delete_query, where_param)
                return_val = True
            else:
                GlobalModule.EM_LOGGER.debug(
                    'EXEC SQL : ' + select_query % where_param)
                result = conn.execute(select_query, where_param)
                row = result.fetchone()
                self.__close_result(result)
                if row:
                    update_param = upsert_param + where_param
                    GlobalModule.EM_LOGGER.debug(
                        'EXEC SQL : ' + update_query % update_param)
                    result = conn.execute(update_query, update_param)
                else:
                    GlobalModule.EM_LOGGER.debug(
                        'EXEC SQL : ' + insert_query % upsert_param)

                    result = conn.execute(insert_query, upsert_param)
                return_val = True
        except Exception, ex_message:
            if is_auto_commit:
                GlobalModule.EM_LOGGER.error(
                    '305003 Database Control Error')
                GlobalModule.EM_LOGGER.debug(
                    'db_error_message = %s' % (ex_message,))
                return_val = False
            else:
                raise
        finally:
            self.__close_result(result)
            if is_auto_commit:
                self.__close_db(conn)
        return return_val


    @decorater_log_in_out
    def read_transactionid_list(self):
        '''
        The method which returns only transaction ID from the transaction management information table.
        Explanation about parameter:
            None
        Return value:
            Execution result : boolean(True or False)
            Transaction ID list : tuple
        '''
        table_name = self.table_TransactionMgmtInfo

        q_str = self.__gen_select_sql(table_name, [])

        is_ok, tr_tuple = self.__execute_read_sql((), q_str)
        ret_list = []
        if is_ok:
            for item in tr_tuple:
                ret_list.append(item["transaction_id"])
        return is_ok, ret_list

    @decorater_log_in_out
    def initialize_order_mgmt_info(self):
        '''
        The method which deletes contents of order management information table
        Parameter explanation:
            None
        Explanation about Return Value:
            Execution result : boolean(True or False)
        '''
        delete_trans_mgmt = self.__gen_delete_sql("transactionmgmtinfo", [])
        delete_device_mgmt = self.__gen_delete_sql("devicestatusmgmtinfo", [])

        conn = None
        db_trans = None
        try:
            conn = self.__connect_db()
            db_trans = conn.begin()
            conn.execute(delete_device_mgmt)
            conn.execute(delete_trans_mgmt)
            db_trans.commit()
            is_ok = True
        except Exception, ex_message:
            if db_trans:
                db_trans.rollback()
            GlobalModule.EM_LOGGER.error(
                '305003 Database Control Error')
            GlobalModule.EM_LOGGER.debug(
                'db_error_message = %s' % (ex_message,))
            is_ok = False
        finally:
            self.__close_db(conn)
        return is_ok

    @decorater_log_in_out
    def delete_device_status_mgmt_info_linked_tr_id(self,
                                                    transaction_id,
                                                    conn=None):
        '''
        The method which deletes the data likned with the transaction_ID in the equipment status management table
        all at once based on the DB control information.
        Explanation about parameter:
            transaction_id:Tansaction ID
        Return value:
            Execution result : boolean(True or False)
        '''
        table_name = self.table_DeviceStatusMgmtInfo

        if not self.__check_parameter(transaction_id, UUID, not_null=True):
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False

        tmp_list = []
        tmp_list.append(transaction_id)
        where_param = tuple(tmp_list)

        where_query_str = []
        where_query_str.append("WHERE transaction_id = %s")

        delete_query = self.__gen_delete_sql(table_name, where_query_str)

        return self.__exec_write_sql(None,
                                     None,
                                     None,
                                     delete_query,
                                     None,
                                     where_param,
                                     self.__delete_flg,
                                     conn)

    @decorater_log_in_out
    def write_transaction_mgmt_info(self,
                                    db_control,
                                    transaction_id,
                                    transaction_status=None,
                                    service_type=None,
                                    order_type=None,
                                    order_text=None,
                                    conn=None):
        '''
        The method which registers/updates/deletes the information in the transaction management information table
        based on the DB control information.
        Explanation about parameter:
            db_control:DB control
            transaction_id:Transaction ID
            transaction_status:Transaction status
            service_type:Service type
            order_type:Order type
            order_text:Order details
        Return value:
            Execution result : boolean(True or False)
        '''
        table_name = self.table_TransactionMgmtInfo

        is_ok = self.__check_parameter(transaction_id, UUID, not_null=True)
        if db_control != self.__delete_flg:
            is_ok = (
                is_ok and
                self.__check_parameter(transaction_status, int, not_null=True)
            )
            is_ok = (is_ok and
                     self.__check_parameter(service_type, int, not_null=True))
            is_ok = (is_ok and
                     self.__check_parameter(order_type, int, not_null=True))
            is_ok = (is_ok and
                     self.__check_parameter(order_text, str, not_null=True))

        if not is_ok:
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False

        tmp_list = []
        tmp_list.append(transaction_id)
        where_param = tuple(tmp_list)

        tmp_list.append(transaction_status)
        tmp_list.append(service_type)
        tmp_list.append(order_type)
        tmp_list.append(order_text)
        upsert_param = tuple(tmp_list)

        where_query_str = ["WHERE transaction_id = %s"]

        delete_query = self.__gen_delete_sql(table_name, where_query_str)

        select_query = self.__gen_select_sql(table_name, where_query_str)

        insert_query, update_query = (
            self.__gen_upsert_sql(table_name, where_query_str,
                                  "transaction_id",
                                  "transaction_status",
                                  "service_type",
                                  "order_type",
                                  "order_text"))

        return self.__exec_write_sql(select_query,
                                     insert_query,
                                     update_query,
                                     delete_query,
                                     upsert_param,
                                     where_param,
                                     db_control,
                                     conn)

    @decorater_log_in_out
    def read_transaction_mgmt_info(self, transaction_id):
        '''
        The method which returns the information on the transaction management information table.
        Explanation about parameter:
            transaction_id: Transaction ID
        Return value:
            Execution result : boolean(True or False)
            Refer to the transaction management information table: tuple
        '''
        table_name = self.table_TransactionMgmtInfo

        if not self.__check_parameter(transaction_id, UUID, not_null=True):
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False, None

        where_query_str = ["WHERE transaction_id = %s"]
        q_str = self.__gen_select_sql(table_name, where_query_str)

        return self.__execute_read_sql((transaction_id,), q_str)

    @decorater_log_in_out
    def write_device_status_mgmt_info(self,
                                      db_control,
                                      device_name,
                                      transaction_id,
                                      transaction_status=None,
                                      conn=None):
        '''
        The method which registers/updates/deletes the information of the equipment status management information table
        based on the DB control information.
        Explanation about parameter:
            db_control:DB control
            device_name:Device name
            transaction_id:Transaction ID
            transaction_status:Transaction status
        Return value:
            Execution result : boolean(True or False)
        '''
        table_name = self.table_DeviceStatusMgmtInfo

        is_ok = self.__check_parameter(device_name, str, not_null=True)
        is_ok = is_ok and self.__check_parameter(
            transaction_id, UUID, not_null=True)
        if db_control != self.__delete_flg:
            is_ok = (
                is_ok and
                self.__check_parameter(transaction_status, int, not_null=True)
            )

        if not is_ok:
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False

        tmp_list = []
        tmp_list.append(device_name)
        tmp_list.append(transaction_id)
        where_param = tuple(tmp_list)

        tmp_list.append(transaction_status)
        upsert_param = tuple(tmp_list)

        where_query_str = []
        where_query_str.append("    WHERE")
        where_query_str.append("          device_name    = %s")
        where_query_str.append("    AND   transaction_id = %s")

        delete_query = self.__gen_delete_sql(table_name, where_query_str)

        select_query = self.__gen_select_sql(table_name, where_query_str)

        insert_query, update_query = (
            self.__gen_upsert_sql(table_name, where_query_str,
                                  "device_name",
                                  "transaction_id",
                                  "transaction_status"))

        return self.__exec_write_sql(select_query,
                                     insert_query,
                                     update_query,
                                     delete_query,
                                     upsert_param,
                                     where_param,
                                     db_control,
                                     conn)

    @decorater_log_in_out
    def read_device_status_mgmt_info(self, transaction_id):
        '''
        The method which returns the information on the equipment status management information table.
        Explanation about parameter:
            transaction_id:Transaction ID
        Return value:
            Execution result : boolean(True or False)
            Refer to the equipment status management information table : tuple
        '''
        table_name = self.table_DeviceStatusMgmtInfo

        if not self.__check_parameter(transaction_id, UUID, not_null=True):
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False, None

        where_query_str = ["WHERE transaction_id = %s"]
        q_str = self.__gen_select_sql(table_name, where_query_str)

        return self.__execute_read_sql((transaction_id,), q_str)

    @decorater_log_in_out
    def write_device_regist_info(self,
                                 db_control,
                                 device_name,
                                 device_type=None,
                                 platform_name=None,
                                 os=None,
                                 firm_version=None,
                                 username=None,
                                 password=None,
                                 mgmt_if_address=None,
                                 mgmt_if_prefix=None,
                                 loopback_if_address=None,
                                 loopback_if_prefix=None,
                                 snmp_server_address=None,
                                 snmp_community=None,
                                 ntp_server_address=None,
                                 as_number=None,
                                 pim_other_rp_address=None,
                                 pim_self_rp_address=None,
                                 pim_rp_address=None,
                                 vpn_type=None,
                                 virtual_link_id=None,
                                 ospf_range_area_address=None,
                                 ospf_range_area_prefix=None,
                                 cluster_ospf_area=None,
                                 rr_loopback_address=None,
                                 rr_loopback_prefix=None,
                                 irb_type=None,
                                 q_in_q_type=None,
                                 conn=None):
        '''
        Registers/updates/deletes the information of the equipment registration information table
        based on the DB control information.
        Explanation about parameter:
            db_control:DB control
            device_name:Equipment name
            device_type:Device type
            platform_name:Platform name
            os:os
            firm_version:Firm version
            username:Log in ID
            password:Password
            mgmt_if_address:Management IF's IPv4 address
            mgmt_if_prefix:Pre-fix of the Management IF's IPv4 address
            loopback_if_address:Loopback IF's IPv4 address
            loopback_if_prefix:Pre-fix of the Loopback IF's IPv4 address
            snmp_server_address:SNMP server's IPv4 address
            snmp_community:SNMP community name
            ntp_server_address:NTP server's IPv4 address
            as_number:Self AS number
            pim_other_rp_address:IPv4 address when other router is RP
            pim_self_rp_address:IPv4 address when yourself is RP
            pim_rp_address:RP's IPv4address
            vpn_type: VPN type
            virtual_link_id:Opposite B-Leaf equipment's router-id
            ospf_range_area_address:OSPF route collective setting address
            ospf_range_area_prefix:Pre-fix of the OSPF route collective setting address
            cluster_ospf_area:OSPF_AREA in case of multi cludter
            rr_loopback_address:Loopback address for RR
            rr_loopback_prefix:Pre-fix of the loopback address for RR
            irb_type:IRB setting type
            q_in_q_type:Q-in-Q type
         Return value:
            Execution result : boolean(True or False)
        '''
        table_name = self.table_DeviceRegistrationInfo

        is_ok = self.__check_parameter(device_name, str, not_null=True)
        if db_control != self.__delete_flg:
            is_ok = is_ok and self.__check_parameter(
                device_type, int, not_null=True)
            is_ok = (is_ok and
                     self.__check_parameter(platform_name, str, not_null=True))
            is_ok = is_ok and self.__check_parameter(os, str, not_null=True)
            is_ok = (is_ok and
                     self.__check_parameter(firm_version, str, not_null=True))
            is_ok = is_ok and self.__check_parameter(
                username, str, not_null=True)
            is_ok = is_ok and self.__check_parameter(
                password, str, not_null=True)
            is_ok = is_ok and self.__check_parameter(mgmt_if_address,
                                                     str, not_null=True)
            is_ok = is_ok and self.__check_parameter(mgmt_if_prefix,
                                                     int, not_null=True)
            is_ok = is_ok and self.__check_parameter(loopback_if_address,
                                                     str, not_null=True)
            is_ok = is_ok and self.__check_parameter(loopback_if_prefix,
                                                     int, not_null=True)
            is_ok = is_ok and self.__check_parameter(snmp_server_address,
                                                     str, not_null=True)
            is_ok = is_ok and self.__check_parameter(
                snmp_community, str, not_null=True)
            is_ok = (
                is_ok and
                self.__check_parameter(ntp_server_address, str, not_null=True)
            )
            is_ok = is_ok and self.__check_parameter(as_number, int)
            is_ok = is_ok and self.__check_parameter(pim_other_rp_address, str)
            is_ok = is_ok and self.__check_parameter(pim_self_rp_address, str)
            is_ok = is_ok and self.__check_parameter(pim_rp_address, str)
            is_ok = is_ok and self.__check_parameter(vpn_type, int)
            is_ok = is_ok and self.__check_parameter(virtual_link_id, str)
            is_ok = is_ok and self.__check_parameter(ospf_range_area_address,
                                                     str)
            is_ok = is_ok and self.__check_parameter(ospf_range_area_prefix,
                                                     int)
            is_ok = is_ok and self.__check_parameter(cluster_ospf_area, str)
            is_ok = is_ok and self.__check_parameter(rr_loopback_address, str)
            is_ok = is_ok and self.__check_parameter(rr_loopback_prefix, int)
            is_ok = is_ok and self.__check_parameter(irb_type, str)
            is_ok = is_ok and self.__check_parameter(q_in_q_type, str)

        if not is_ok:
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False

        tmp_list = []
        tmp_list.append(device_name)
        where_param = tuple(tmp_list)

        tmp_list.append(device_type)
        tmp_list.append(platform_name)
        tmp_list.append(os)
        tmp_list.append(firm_version)
        tmp_list.append(username)
        tmp_list.append(password)
        tmp_list.append(mgmt_if_address)
        tmp_list.append(mgmt_if_prefix)
        tmp_list.append(loopback_if_address)
        tmp_list.append(loopback_if_prefix)
        tmp_list.append(snmp_server_address)
        tmp_list.append(snmp_community)
        tmp_list.append(ntp_server_address)
        tmp_list.append(as_number)
        tmp_list.append(pim_other_rp_address)
        tmp_list.append(pim_self_rp_address)
        tmp_list.append(pim_rp_address)
        tmp_list.append(vpn_type)
        tmp_list.append(virtual_link_id)
        tmp_list.append(ospf_range_area_address)
        tmp_list.append(ospf_range_area_prefix)
        tmp_list.append(cluster_ospf_area)
        tmp_list.append(rr_loopback_address)
        tmp_list.append(rr_loopback_prefix)
        tmp_list.append(irb_type)
        tmp_list.append(q_in_q_type)
        upsert_param = tuple(tmp_list)

        where_query_str = ["WHERE device_name = %s"]

        delete_query = self.__gen_delete_sql(table_name, where_query_str)

        select_query = self.__gen_select_sql(table_name, where_query_str)

        insert_query, update_query = (
            self.__gen_upsert_sql(table_name, where_query_str,
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
                                  "irb_type",
                                  "q_in_q_type"))

        return self.__exec_write_sql(select_query,
                                     insert_query,
                                     update_query,
                                     delete_query,
                                     upsert_param,
                                     where_param,
                                     db_control,
                                     conn)

    @decorater_log_in_out
    def read_device_regist_info(self, device_name):
        '''
        The method which returns the information of the equipment registration information table.
        Explanation about parameter:
            device_name:Equipment name
        Return value:
            Execution result : boolean(True or False)
            Refer to the equipment status management information table : tuple
        '''
        table_name = self.table_DeviceRegistrationInfo

        if not self.__check_parameter(device_name, str, not_null=True):
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False, None

        where_query_str = ["WHERE device_name = %s"]
        q_str = self.__gen_select_sql(table_name, where_query_str)

        return self.__execute_read_sql((device_name,), q_str)

    @decorater_log_in_out
    def write_vlanif_info(self,
                          db_control,
                          device_name,
                          if_name,
                          vlan_id,
                          slice_name,
                          slice_type=None,
                          port_mode=None,
                          vni=None,
                          multicast_group=None,
                          ipv4_address=None,
                          ipv4_prefix=None,
                          ipv6_address=None,
                          ipv6_prefix=None,
                          bgp_flag=None,
                          ospf_flag=None,
                          static_flag=None,
                          direct_flag=None,
                          vrrp_flag=None,
                          mtu_size=None,
                          metric=None,
                          esi=None,
                          system_id=None,
                          inflow_shaping_rate=None,
                          outflow_shaping_rate=None,
                          remark_menu=None,
                          egress_queue_menu=None,
                          clag_id=None,
                          speed=None,
                          irb_ipv4_address=None,
                          irb_ipv4_prefix=None,
                          virtual_mac_address=None,
                          virtual_gateway_address=None,
                          virtual_gateway_prefix=None,
                          q_in_q=None,
                          conn=None):
        '''
        The method which registers/updates/deletes the information of the VLAN interface information table
        based on the DB control information.
        Explanation about parameter:
            db_control:DB control
            device_name:Device name
            if_name:IF name
            vlan_id:VLAN ID
            slice_name:Slice name
            slice_type:Slice type
            port_mode:Port mode
            vni:VNI value
            multicast_group:Multi cast group's IPv4 address
            ipv4_address:IPv4 address for CE
            ipv4_prefix:Pre-fix of the IPv4 address for CE
            ipv6_address:IPv6 address for CE
            ipv6_prefix:Pre-fix of the IPv6 address for CE
            bgp_flag:Flag which uses BGP
            ospf_flag:Flag which uses OSPF
            static_flag:Flag which uses Static
            direct_flag:Flag which uses Direct
            vrrp_flag:Flag which uses VRRP
            mtu_size:MTU size
            metric:metric value
            esi:ESI
            system_id:LACP system-id
            inflow_shaping_rate:QoS inflow traffic limit value
            outflow_shaping_rate:QoS outflow traffic limit value
            remark_menu:QoS remark menu
            egress_queue_menu:QoS eggress queue menu
            CLAG ID:clag_id
            IF Speed (Physical case only):speed
            IPv4 Address for IRB configuration:irb_ipv4_address
            IPv4 Address Prefix for IRB configuration:irb_ipv4_prefix
            Virtual mac address:virtual_mac_address
            Virtual Gateway Address:virtual_gateway_address
            Virtual Gateway Prefix:virtual_gateway_prefix
            q_in_q:Q-in-Q setting
        Return Value:
            Execution Results : boolean(True or False)
        '''
        table_name = self.table_VlanIfInfo

        is_ok = self.__check_parameter(device_name, str, not_null=True)
        is_ok = is_ok and self.__check_parameter(if_name, str, not_null=True)
        is_ok = is_ok and self.__check_parameter(vlan_id, int, not_null=True)
        is_ok = is_ok and self.__check_parameter(
            slice_name, str, not_null=True)
        if db_control != self.__delete_flg:
            is_ok = is_ok and self.__check_parameter(
                slice_type, int, not_null=True)
            is_ok = is_ok and self.__check_parameter(port_mode, int)
            is_ok = is_ok and self.__check_parameter(vni, int)
            is_ok = is_ok and self.__check_parameter(multicast_group, str)
            is_ok = is_ok and self.__check_parameter(
                ipv4_address, str, b_size=15)
            is_ok = is_ok and self.__check_parameter(ipv4_prefix, int)
            is_ok = is_ok and self.__check_parameter(
                ipv6_address, str, b_size=39)
            is_ok = is_ok and self.__check_parameter(ipv6_prefix, int)
            is_ok = is_ok and self.__check_parameter(bgp_flag, bool)
            is_ok = is_ok and self.__check_parameter(ospf_flag, bool)
            is_ok = is_ok and self.__check_parameter(static_flag, bool)
            is_ok = is_ok and self.__check_parameter(direct_flag, bool)
            is_ok = is_ok and self.__check_parameter(vrrp_flag, bool)
            is_ok = is_ok and self.__check_parameter(mtu_size, int)
            is_ok = is_ok and self.__check_parameter(metric, int)
            is_ok = is_ok and self.__check_parameter(esi, str)
            is_ok = is_ok and self.__check_parameter(system_id, str)
            is_ok = is_ok and self.__check_parameter(
                inflow_shaping_rate, float)
            is_ok = is_ok and self.__check_parameter(
                outflow_shaping_rate, float)
            is_ok = is_ok and self.__check_parameter(remark_menu, str)
            is_ok = is_ok and self.__check_parameter(egress_queue_menu, str)
            is_ok = is_ok and self.__check_parameter(clag_id, int)
            is_ok = is_ok and self.__check_parameter(speed, str)
            is_ok = is_ok and self.__check_parameter(irb_ipv4_address, str)
            is_ok = is_ok and self.__check_parameter(irb_ipv4_prefix, int)
            is_ok = is_ok and self.__check_parameter(
                virtual_mac_address, str)
            is_ok = is_ok and self.__check_parameter(
                virtual_gateway_address, str)
            is_ok = is_ok and self.__check_parameter(
                virtual_gateway_prefix, int)
            is_ok = is_ok and self.__check_parameter(q_in_q, bool)

        if not is_ok:
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False

        tmp_list = []
        tmp_list.append(device_name)
        tmp_list.append(if_name)
        tmp_list.append(vlan_id)
        tmp_list.append(slice_name)
        where_param = tuple(tmp_list)

        tmp_list.append(slice_type)
        tmp_list.append(port_mode)
        tmp_list.append(vni)
        tmp_list.append(multicast_group)
        tmp_list.append(ipv4_address)
        tmp_list.append(ipv4_prefix)
        tmp_list.append(ipv6_address)
        tmp_list.append(ipv6_prefix)
        tmp_list.append(bgp_flag)
        tmp_list.append(ospf_flag)
        tmp_list.append(static_flag)
        tmp_list.append(direct_flag)
        tmp_list.append(vrrp_flag)
        tmp_list.append(mtu_size)
        tmp_list.append(metric)
        tmp_list.append(esi)
        tmp_list.append(system_id)
        tmp_list.append(inflow_shaping_rate)
        tmp_list.append(outflow_shaping_rate)
        tmp_list.append(remark_menu)
        tmp_list.append(egress_queue_menu)
        tmp_list.append(clag_id)
        tmp_list.append(speed)
        tmp_list.append(irb_ipv4_address)
        tmp_list.append(irb_ipv4_prefix)
        tmp_list.append(virtual_mac_address)
        tmp_list.append(virtual_gateway_address)
        tmp_list.append(virtual_gateway_prefix)
        tmp_list.append(q_in_q)
        upsert_param = tuple(tmp_list)

        where_query_str = []
        where_query_str.append("    WHERE")
        where_query_str.append("          device_name = %s")
        where_query_str.append("    AND   if_name     = %s")
        where_query_str.append("    AND   vlan_id = %s")
        where_query_str.append("    AND   slice_name = %s")

        delete_query = self.__gen_delete_sql(table_name, where_query_str)

        select_query = self.__gen_select_sql(table_name, where_query_str)

        insert_query, update_query = (
            self.__gen_upsert_sql(table_name, where_query_str,
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
                                  'virtual_mac_address',
                                  "virtual_gateway_address",
                                  "virtual_gateway_prefix",
                                  "q_in_q"))

        return self.__exec_write_sql(select_query,
                                     insert_query,
                                     update_query,
                                     delete_query,
                                     upsert_param,
                                     where_param,
                                     db_control,
                                     conn)

    @decorater_log_in_out
    def read_vlanif_info(self, device_name):
        '''
        The method which returns the in formation of VLAN interface information table.
        Parameter:
            device_name: Device name
        Return value:
            Execution result : boolean(True or False)
            Refer to the VLAN interface information table : tuple
        '''
        table_name = self.table_VlanIfInfo

        if not self.__check_parameter(device_name, str, not_null=True):
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False, None

        where_query_str = ["WHERE device_name = %s"]
        q_str = self.__gen_select_sql(table_name, where_query_str)

        return self.__execute_read_sql((device_name,), q_str)

    @decorater_log_in_out
    def write_lagif_info(self,
                         db_control,
                         device_name,
                         lag_if_name,
                         lag_type=None,
                         lag_if_id=None,
                         minimum_links=None,
                         link_speed=None,
                         condition=None,
                         conn=None):
        '''
        The method which registers/updates/deletes the information of the LAG interface information table
        based on the DB control information.
        Parameter:
            db_control:DB control
            device_name: Device name
            lag_if_name:LAG IF name
            lag_type:LAG type
            lag_if_id:LAGIFID
            minimum_links:LAG member count
            link_speed:Link speed
            condition:port status
         Return value:
            Execution result : boolean(True or False)
        '''
        table_name = self.table_LagIfInfo

        is_not_null = True
        if db_control == self.__delete_flg and lag_if_name is None:
            is_not_null = False

        is_ok = self.__check_parameter(device_name, str, not_null=True)
        is_ok = is_ok and self.__check_parameter(lag_if_name,
                                                 str, not_null=is_not_null)
        if db_control != self.__delete_flg:
            is_ok = is_ok and self.__check_parameter(
                lag_type, int, not_null=True)
            is_ok = is_ok and self.__check_parameter(
                lag_if_id, int, not_null=True)
            is_ok = (is_ok and
                     self.__check_parameter(minimum_links, int, not_null=True))
            is_ok = is_ok and self.__check_parameter(link_speed, str)
            is_ok = (is_ok and self.__check_parameter(
                condition, int, not_null=True))

        if not is_ok:
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False

        tmp_list = []
        tmp_list.append(device_name)
        if is_not_null:
            tmp_list.append(lag_if_name)
        where_param = tuple(tmp_list)

        tmp_list.append(lag_type)
        tmp_list.append(lag_if_id)
        tmp_list.append(minimum_links)
        tmp_list.append(link_speed)
        tmp_list.append(condition)
        upsert_param = tuple(tmp_list)

        where_query_str = []
        where_query_str.append("    WHERE")
        where_query_str.append("          device_name = %s")
        if is_not_null:
            where_query_str.append("    AND   lag_if_name = %s")

        delete_query = self.__gen_delete_sql(table_name, where_query_str)

        select_query = self.__gen_select_sql(table_name, where_query_str)

        insert_query, update_query = (
            self.__gen_upsert_sql(table_name, where_query_str,
                                  "device_name",
                                  "lag_if_name",
                                  "lag_type",
                                  "lag_if_id",
                                  "minimum_links",
                                  "link_speed",
                                  "condition"))

        return self.__exec_write_sql(select_query,
                                     insert_query,
                                     update_query,
                                     delete_query,
                                     upsert_param,
                                     where_param,
                                     db_control,
                                     conn)

    @decorater_log_in_out
    def read_lagif_info(self, device_name):
        '''
        Returns the information of the LAG interface information table.
        Parameter:
            device_name:Device name
        Return value:
            Execution result : boolean(True or False)
            Refer to the LAG interface information table : tuple
        '''
        table_name = self.table_LagIfInfo

        if not self.__check_parameter(device_name, str, not_null=True):
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False, None

        where_query_str = ["WHERE device_name = %s"]
        q_str = self.__gen_select_sql(table_name, where_query_str)

        return self.__execute_read_sql((device_name,), q_str)

    @decorater_log_in_out
    def write_lagmemberif_info(self,
                               db_control,
                               lag_if_name,
                               if_name,
                               device_name,
                               conn=None):
        '''
        The method which registers/updates/deletes the information of the LAG member interface information table
        based on the DB control information.
        Parameter:
            db_control:DB control
            lag_if_name:LAG IF name
            if_name:IF name
            device_name:Device name
        Return value:
            Execution result : boolean
        '''
        table_name = self.table_LagMemberIfInfo

        is_not_null = True
        if (db_control == self.__delete_flg and
                (lag_if_name is None or if_name is None)):
            is_not_null = False

        is_ok = self.__check_parameter(lag_if_name, str, not_null=is_not_null)
        is_ok = is_ok and self.__check_parameter(
            if_name, str, not_null=is_not_null)
        is_ok = is_ok and self.__check_parameter(
            device_name, str, not_null=True)

        if not is_ok:
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False

        tmp_list = []
        if is_not_null or lag_if_name is not None:
            tmp_list.append(lag_if_name)
        if is_not_null or if_name is not None:
            tmp_list.append(if_name)
        tmp_list.append(device_name)
        where_param = tuple(tmp_list)

        upsert_param = tuple(tmp_list)

        where_query_str = []
        where_query_str.append("    WHERE")
        where_query_str.append("          1 = 1")
        if is_not_null or lag_if_name is not None:
            where_query_str.append("    AND   lag_if_name = %s")
        if is_not_null or if_name is not None:
            where_query_str.append("    AND   if_name     = %s")
        where_query_str.append("    AND   device_name = %s")

        delete_query = self.__gen_delete_sql(table_name, where_query_str)

        select_query = self.__gen_select_sql(table_name, where_query_str)

        insert_query, update_query = (
            self.__gen_upsert_sql(table_name, where_query_str,
                                  "lag_if_name",
                                  "if_name",
                                  "device_name"))

        return self.__exec_write_sql(select_query,
                                     insert_query,
                                     update_query,
                                     delete_query,
                                     upsert_param,
                                     where_param,
                                     db_control,
                                     conn)

    @decorater_log_in_out
    def read_lagmemberif_info(self, device_name):
        '''
        The method which returns the information of the LAG member interface information table.
        Parameter:
            device_name:Device name
        Return value:
            Execution result : boolean(True or False)
            Refer to the LAG member interface information table : tuple
        '''
        table_name = self.table_LagMemberIfInfo

        if not self.__check_parameter(device_name, str, not_null=True):
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False, None

        where_query_str = ["WHERE device_name = %s"]
        q_str = self.__gen_select_sql(table_name, where_query_str)

        return self.__execute_read_sql((device_name,), q_str)

    @decorater_log_in_out
    def write_leaf_bgp_basic_info(self,
                                  db_control,
                                  device_name,
                                  neighbor_ipv4,
                                  bgp_community_value,
                                  bgp_community_wildcard,
                                  conn=None):
        '''
        Registers/updates/deletes the information of the BPG basic setting table for Leaf
        based on the DB control information.
        Parameter:
            db_control:DB control
            device_name:Device name
            neighbor_ipv4:Neighbor's IPv4address
            bgp_community_value:BGP community value
            bgp_community_wildcard:BGP priority
        Return value:
            Execution result : boolean(True or False)
        '''
        table_name = self.table_L3VpnLeafBgpBasicInfo

        is_not_null = True
        if db_control == self.__delete_flg and neighbor_ipv4 is None:
            is_not_null = False

        is_ok = self.__check_parameter(device_name, str, not_null=True)
        is_ok = is_ok and self.__check_parameter(neighbor_ipv4,
                                                 str, not_null=is_not_null)
        if db_control != self.__delete_flg:
            is_ok = is_ok and self.__check_parameter(
                bgp_community_value, str)
            is_ok = is_ok and self.__check_parameter(
                bgp_community_wildcard, str)

        if not is_ok:
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False

        tmp_list = []
        tmp_list.append(device_name)
        if is_not_null:
            tmp_list.append(neighbor_ipv4)
        where_param = tuple(tmp_list)

        tmp_list.append(bgp_community_value)
        tmp_list.append(bgp_community_wildcard)
        upsert_param = tuple(tmp_list)

        where_query_str = []
        where_query_str.append("    WHERE")
        where_query_str.append("          device_name      = %s")
        if is_not_null:
            where_query_str.append("    AND   neighbor_ipv4    = %s")

        delete_query = self.__gen_delete_sql(table_name, where_query_str)

        select_query = self.__gen_select_sql(table_name, where_query_str)

        insert_query, update_query = (
            self.__gen_upsert_sql(table_name, where_query_str,
                                  "device_name",
                                  "neighbor_ipv4",
                                  "bgp_community_value",
                                  "bgp_community_wildcard"))

        return self.__exec_write_sql(select_query,
                                     insert_query,
                                     update_query,
                                     delete_query,
                                     upsert_param,
                                     where_param,
                                     db_control,
                                     conn)

    @decorater_log_in_out
    def read_leaf_bgp_basic_info(self, device_name):
        '''
        Returns the information of the BGP basic table for Leaf.
        Parameter:
            device_name:Device name
        Return value:
            Execution result : boolean(True or False)
            Refer to the BGP basic setting table for Leaf : tuple
        '''
        table_name = self.table_L3VpnLeafBgpBasicInfo

        if not self.__check_parameter(device_name, str, not_null=True):
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False, None

        where_query_str = ["WHERE device_name = %s"]
        q_str = self.__gen_select_sql(table_name, where_query_str)

        return self.__execute_read_sql((device_name,), q_str)

    @decorater_log_in_out
    def write_vrf_detail_info(self,
                              db_control,
                              device_name,
                              if_name,
                              vlan_id,
                              slice_name,
                              vrf_name=None,
                              vrf_id=None,
                              rt=None,
                              rd=None,
                              router_id=None,
                              l3_vni=None,
                              l3_vlan_id=None,
                              vrf_loopback_interface_address=None,
                              vrf_loopback_interface_prefix=None,
                              conn=None):
        '''
        The method which registers/updates/deletes the information of the VRF detailed information table
        based on the DB control information.
        Parameter:
            db_control:DB control
            device_name:Device name
            if_name:IF name
            vlan_id:VLAN ID
            slice_name:Slice name
            vrf_name:VRF name
            vrf_id:VRF ID
            rt:RT (Route Target) value
            rd:RD (Route Distinguisher) value
            router_id:Router ID
            l3_vni:VNI Value for L3VNI
            l3_vlan_id:VLANID for L3VNI
            vrf_loopback_interface_address:Loopback IF Address for VRF
            vrf_loopback_interface_prefix:Loopback IF Address Prefix for VRF
        Return Value:
            Execution Result : boolean(True or False)            
        '''
        table_name = self.table_VrfDetailInfo

        is_not_null = True
        if db_control == self.__delete_flg and (if_name is None and
                                                vlan_id is None):
            is_not_null = False

        is_ok = self.__check_parameter(device_name, str, not_null=True)
        is_ok = is_ok and self.__check_parameter(
            if_name, str, not_null=is_not_null)
        is_ok = is_ok and self.__check_parameter(
            vlan_id, int, not_null=is_not_null)
        is_ok = is_ok and self.__check_parameter(
            slice_name, str, not_null=True)
        if db_control != self.__delete_flg:
            is_ok = is_ok and self.__check_parameter(
                vrf_name, str, not_null=True)
            is_ok = is_ok and self.__check_parameter(vrf_id, int)
            is_ok = is_ok and self.__check_parameter(rt, str, not_null=True)
            is_ok = is_ok and self.__check_parameter(rd, str, not_null=True)
            is_ok = is_ok and self.__check_parameter(
                router_id, str, not_null=True)
            is_ok = is_ok and self.__check_parameter(l3_vni, int)
            is_ok = is_ok and self.__check_parameter(l3_vlan_id, int)
            is_ok = is_ok and self.__check_parameter(
                vrf_loopback_interface_address, str)
            is_ok = is_ok and self.__check_parameter(
                vrf_loopback_interface_prefix, int)

        if not is_ok:
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False

        tmp_list = []
        tmp_list.append(device_name)
        if is_not_null:
            tmp_list.append(if_name)
            tmp_list.append(vlan_id)
        tmp_list.append(slice_name)
        where_param = tuple(tmp_list)

        tmp_list.append(vrf_name)
        tmp_list.append(vrf_id)
        tmp_list.append(rt)
        tmp_list.append(rd)
        tmp_list.append(router_id)
        tmp_list.append(l3_vni)
        tmp_list.append(l3_vlan_id)
        tmp_list.append(vrf_loopback_interface_address)
        tmp_list.append(vrf_loopback_interface_prefix)
        upsert_param = tuple(tmp_list)

        where_query_str = []
        where_query_str.append("    WHERE")
        where_query_str.append("          device_name = %s")
        if is_not_null:
            where_query_str.append("    AND   if_name     = %s")
            where_query_str.append("    AND   vlan_id     = %s")
        where_query_str.append("    AND   slice_name  = %s")

        delete_query = self.__gen_delete_sql(table_name, where_query_str)

        select_query = self.__gen_select_sql(table_name, where_query_str)

        insert_query, update_query = (
            self.__gen_upsert_sql(table_name, where_query_str,
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
                                  "vrf_loopback_interface_prefix"))

        return self.__exec_write_sql(select_query,
                                     insert_query,
                                     update_query,
                                     delete_query,
                                     upsert_param,
                                     where_param,
                                     db_control,
                                     conn)

    @decorater_log_in_out
    def read_vrf_detail_info(self, device_name):
        '''
        The method which returns the information of the VRF detailed information table.
        Parameter:
            device_name:Device name
        Return value:
            Execution result : boolean(True or False)
            Refer to the VRF detailed information table : tuple
        '''
        table_name = self.table_VrfDetailInfo

        if not self.__check_parameter(device_name, str, not_null=True):
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False, None

        where_query_str = ["WHERE device_name = %s"]
        q_str = self.__gen_select_sql(table_name, where_query_str)

        return self.__execute_read_sql((device_name,), q_str)

    @decorater_log_in_out
    def write_vrrp_detail_info(self,
                               db_control,
                               device_name,
                               if_name,
                               vlan_id,
                               slice_name,
                               vrrp_group_id=None,
                               virtual_ipv4_address=None,
                               virtual_ipv6_address=None,
                               priority=None,
                               conn=None):
        '''
        The method which registers/updates/deletes the information of the VRRP detailed information table
        based on the DB control information.
        Parameter:
            db_control:DB control
            device_name:Device name
            if_name:IF name
            vlan_id:VLAN ID
            slice_name:slice name
            vrrp_group_id:VRRP group ID
            virtual_ipv4_address:VRRP virtual IPv4address
            virtual_ipv6_address:VRRP virtual IPv6address
            priority:VRRP priority
        Return value:
            Execution result : boolean(True or False)
        '''
        table_name = self.table_VrrpDetailInfo

        is_ok = self.__check_parameter(device_name, str, not_null=True)
        is_ok = is_ok and self.__check_parameter(if_name, str, not_null=True)
        is_ok = is_ok and self.__check_parameter(vlan_id, int, not_null=True)
        is_ok = is_ok and self.__check_parameter(
            slice_name, str, not_null=True)
        if db_control != self.__delete_flg:
            is_ok = is_ok and self.__check_parameter(
                vrrp_group_id, int, not_null=True)
            is_ok = (is_ok and
                     self.__check_parameter(virtual_ipv4_address,
                                            str, b_size=15))
            is_ok = (is_ok and
                     self.__check_parameter(virtual_ipv6_address,
                                            str, b_size=39))
            is_ok = is_ok and self.__check_parameter(
                priority, int, not_null=True)

        if not is_ok:
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False

        tmp_list = []
        tmp_list.append(device_name)
        tmp_list.append(if_name)
        tmp_list.append(vlan_id)
        tmp_list.append(slice_name)
        where_param = tuple(tmp_list)

        tmp_list.append(vrrp_group_id)
        tmp_list.append(virtual_ipv4_address)
        tmp_list.append(virtual_ipv6_address)
        tmp_list.append(priority)
        upsert_param = tuple(tmp_list)

        where_query_str = []
        where_query_str.append("    WHERE")
        where_query_str.append("          device_name = %s")
        where_query_str.append("    AND   if_name     = %s")
        where_query_str.append("    AND   vlan_id     = %s")
        where_query_str.append("    AND   slice_name  = %s")

        delete_query = self.__gen_delete_sql(table_name, where_query_str)

        select_query = self.__gen_select_sql(table_name, where_query_str)

        insert_query, update_query = (
            self.__gen_upsert_sql(table_name, where_query_str,
                                  "device_name",
                                  "if_name",
                                  "vlan_id",
                                  "slice_name",
                                  "vrrp_group_id",
                                  "virtual_ipv4_address",
                                  "virtual_ipv6_address",
                                  "priority"))

        return self.__exec_write_sql(select_query,
                                     insert_query,
                                     update_query,
                                     delete_query,
                                     upsert_param,
                                     where_param,
                                     db_control,
                                     conn)

    @decorater_log_in_out
    def read_vrrp_detail_info(self, device_name):
        '''
        The method which returns the information of the VRRP detailed information table.
        Parameter:
            device_name:Device name
        Return value:
            Execution result : boolean(True or False)
            Refer to the VRRP detailed information table : tuple
        '''
        table_name = self.table_VrrpDetailInfo

        if not self.__check_parameter(device_name, str, not_null=True):
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False, None

        where_query_str = ["WHERE device_name = %s"]
        q_str = self.__gen_select_sql(table_name, where_query_str)

        return self.__execute_read_sql((device_name,), q_str)

    @decorater_log_in_out
    def write_vrrp_trackif_info(self,
                                db_control,
                                vrrp_group_id,
                                track_if_name,
                                conn=None):
        '''
        The method which returns the information of the VRRP track interface information table.
        Parameter:
            db_control:DB control
            vrrp_group_id:VRRP group ID
            track_if_name:Track IF name
        Return value:
            Execution result : boolean(True or False)
        '''
        table_name = self.table_VrrpTrackIfInfo

        is_not_null = True
        if db_control == self.__delete_flg and track_if_name is None:
            is_not_null = False

        is_ok = self.__check_parameter(vrrp_group_id, int, not_null=True)
        is_ok = is_ok and self.__check_parameter(track_if_name,
                                                 str,
                                                 not_null=is_not_null)

        if not is_ok:
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False

        tmp_list = []
        tmp_list.append(vrrp_group_id)
        if is_not_null:
            tmp_list.append(track_if_name)
        where_param = tuple(tmp_list)

        upsert_param = tuple(tmp_list)

        where_query_str = []
        where_query_str.append("    WHERE")
        where_query_str.append("          vrrp_group_id = %s")
        if is_not_null:
            where_query_str.append("    AND   track_if_name = %s")

        delete_query = self.__gen_delete_sql(table_name, where_query_str)

        select_query = self.__gen_select_sql(table_name, where_query_str)

        insert_query, update_query = (
            self.__gen_upsert_sql(table_name, where_query_str,
                                  "vrrp_group_id",
                                  "track_if_name"))

        return self.__exec_write_sql(select_query,
                                     insert_query,
                                     update_query,
                                     delete_query,
                                     upsert_param,
                                     where_param,
                                     db_control,
                                     conn)

    @decorater_log_in_out
    def read_vrrp_trackif_info(self, device_name):
        '''
        The method which returns the information of the VRRP track interface information table.
        Parameter:
            device_name:Device name
        Return value:
            Execution result : boolean(True or False)
            Refer to the VRRP track interface information table : tuple
        '''
        if not self.__check_parameter(device_name, str, not_null=True):
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False, None

        query_str = []
        query_str.append("SELECT DISTINCT")
        query_str.append("     track.vrrp_group_id AS vrrp_group_id")
        query_str.append("    ,track.track_if_name AS track_if_name")
        query_str.append("    FROM")
        query_str.append("        VrrpTrackIfInfo AS track")
        query_str.append("    INNER JOIN VrrpDetailInfo AS vrrp ON")
        query_str.append("        track.vrrp_group_id = vrrp.vrrp_group_id")
        query_str.append("    WHERE")
        query_str.append("        vrrp.device_name = %s")
        q_str = ' '.join(query_str)

        return self.__execute_read_sql((device_name,), q_str)

    @decorater_log_in_out
    def write_bgp_detail_info(self,
                              db_control,
                              device_name,
                              if_name,
                              vlan_id,
                              slice_name,
                              master=None,
                              remote_as_number=None,
                              local_ipv4_address=None,
                              remote_ipv4_address=None,
                              local_ipv6_address=None,
                              remote_ipv6_address=None,
                              conn=None):
        '''
        Method which registers/updates/deletes the information of the BGP Detailed Information Table
        based on the DB control information
        Parameter：
            db_control:DB Control
            device_name: Device Name
            if_name:IFName
            vlan_id:VLAN ID
            slice_name:Slice name
            master:Priority
            remote_as_number:CE's AS number
            local_ipv4_address:IPv4address for CE
            remote_ipv4_address:IPv4address for CE
            local_ipv6_address:IPv6address for CE
            remote_ipv6_address:IPv6address for CE
        Return value:
            Execution result : boolean(True or False)
        '''
        table_name = self.table_BgpDetailInfo

        is_ok = self.__check_parameter(device_name, str, not_null=True)
        is_ok = is_ok and self.__check_parameter(if_name, str, not_null=True)
        is_ok = is_ok and self.__check_parameter(vlan_id, int, not_null=True)
        is_ok = is_ok and self.__check_parameter(
            slice_name, str, not_null=True)
        if db_control != self.__delete_flg:
            is_ok = (
                is_ok and
                self.__check_parameter(master, bool))
            is_ok = (
                is_ok and
                self.__check_parameter(remote_as_number, int, not_null=True))
            is_ok = (
                is_ok and
                self.__check_parameter(local_ipv4_address, str, b_size=15))
            is_ok = (
                is_ok and
                self.__check_parameter(remote_ipv4_address, str, b_size=15))
            is_ok = (
                is_ok and
                self.__check_parameter(local_ipv6_address, str, b_size=39))
            is_ok = (
                is_ok and
                self.__check_parameter(remote_ipv6_address, str, b_size=39))

        if not is_ok:
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False

        tmp_list = []
        tmp_list.append(device_name)
        tmp_list.append(if_name)
        tmp_list.append(vlan_id)
        tmp_list.append(slice_name)
        where_param = tuple(tmp_list)

        tmp_list.append(master)
        tmp_list.append(remote_as_number)
        tmp_list.append(local_ipv4_address)
        tmp_list.append(remote_ipv4_address)
        tmp_list.append(local_ipv6_address)
        tmp_list.append(remote_ipv6_address)
        upsert_param = tuple(tmp_list)

        where_query_str = []
        where_query_str.append("    WHERE")
        where_query_str.append("          device_name = %s")
        where_query_str.append("    AND   if_name     = %s")
        where_query_str.append("    AND   vlan_id     = %s")
        where_query_str.append("    AND   slice_name  = %s")

        delete_query = self.__gen_delete_sql(table_name, where_query_str)

        select_query = self.__gen_select_sql(table_name, where_query_str)

        insert_query, update_query = (
            self.__gen_upsert_sql(table_name, where_query_str,
                                  "device_name",
                                  "if_name",
                                  "vlan_id",
                                  "slice_name",
                                  "master",
                                  "remote_as_number",
                                  "local_ipv4_address",
                                  "remote_ipv4_address",
                                  "local_ipv6_address",
                                  "remote_ipv6_address"))

        return self.__exec_write_sql(select_query,
                                     insert_query,
                                     update_query,
                                     delete_query,
                                     upsert_param,
                                     where_param,
                                     db_control,
                                     conn)

    @decorater_log_in_out
    def read_bgp_detail_info(self, device_name):
        '''
        The method which returns the information of the BGP detailed information table.
        Parameter:
            device_name:Device name
        Return value:
            Execution result : boolean(True or False)
            Refer to the BGP detailed information table : tuple
        '''
        table_name = self.table_BgpDetailInfo

        if not self.__check_parameter(device_name, str, not_null=True):
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False, None

        where_query_str = ["WHERE device_name = %s"]
        q_str = self.__gen_select_sql(table_name, where_query_str)

        return self.__execute_read_sql((device_name,), q_str)

    @decorater_log_in_out
    def write_static_route_detail_info(self,
                                       db_control,
                                       device_name,
                                       if_name,
                                       vlan_id,
                                       slice_name,
                                       address_type,
                                       address,
                                       prefix,
                                       nexthop,
                                       conn=None):
        '''
        Method which registers/updates/deletes the information of Static Route Detailed Information Table based on DB Control Information
        Parameter:
            db_control:DB Control
            device_name: Device Name
            if_name:IFName
            vlan_id:VLAN ID
            slice_name:Slice name
            address_type:IPaddress type
            address:Static route address information
            prefix:Static route pre-fix information
            nexthop:Next hop information
        Return value:
            Execution result : boolean(True or False)
        '''
        table_name = self.table_StaticRouteDetailInfo

        is_not_null = True
        if db_control == self.__delete_flg and (address_type is None and
                                                address is None and
                                                prefix is None and
                                                nexthop is None):
            is_not_null = False

        is_ok = self.__check_parameter(device_name, str, not_null=True)
        is_ok = is_ok and self.__check_parameter(if_name, str, not_null=True)
        is_ok = is_ok and self.__check_parameter(vlan_id, int, not_null=True)
        is_ok = is_ok and self.__check_parameter(
            slice_name, str, not_null=True)
        is_ok = (is_ok and self.__check_parameter(address_type,
                                                  int, not_null=is_not_null))
        is_ok = is_ok and self.__check_parameter(
            address, str, not_null=is_not_null)
        is_ok = is_ok and self.__check_parameter(
            prefix, int, not_null=is_not_null)
        is_ok = is_ok and self.__check_parameter(
            nexthop, str, not_null=is_not_null)

        if not is_ok:
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False

        tmp_list = []
        tmp_list.append(device_name)
        tmp_list.append(if_name)
        tmp_list.append(vlan_id)
        tmp_list.append(slice_name)
        if is_not_null:
            tmp_list.append(address_type)
            tmp_list.append(address)
            tmp_list.append(prefix)
            tmp_list.append(nexthop)
        where_param = tuple(tmp_list)

        upsert_param = tuple(tmp_list)

        where_query_str = []
        where_query_str.append("    WHERE")
        where_query_str.append("          device_name  = %s")
        where_query_str.append("    AND   if_name      = %s")
        where_query_str.append("    AND   vlan_id      = %s")
        where_query_str.append("    AND   slice_name   = %s")
        if is_not_null:
            where_query_str.append("    AND   address_type = %s")
            where_query_str.append("    AND   address      = %s")
            where_query_str.append("    AND   prefix       = %s")
            where_query_str.append("    AND   nexthop      = %s")

        delete_query = self.__gen_delete_sql(table_name, where_query_str)

        select_query = self.__gen_select_sql(table_name, where_query_str)

        insert_query, update_query = (
            self.__gen_upsert_sql(table_name, where_query_str,
                                  "device_name",
                                  "if_name",
                                  "vlan_id",
                                  "slice_name",
                                  "address_type",
                                  "address",
                                  "prefix",
                                  "nexthop"))

        return self.__exec_write_sql(select_query,
                                     insert_query,
                                     update_query,
                                     delete_query,
                                     upsert_param,
                                     where_param,
                                     db_control,
                                     conn)

    @decorater_log_in_out
    def read_static_route_detail_info(self, device_name):
        '''
        The method which returns the information of the static route detailed information table.
        Parameter:
            device_name:Device name
        Return value:
            Execution result : boolean(True or False)
            Redfer to the static route detailed information table : tuple
        '''
        table_name = self.table_StaticRouteDetailInfo

        if not self.__check_parameter(device_name, str, not_null=True):
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False, None

        where_query_str = ["WHERE device_name = %s"]
        q_str = self.__gen_select_sql(table_name, where_query_str)

        return self.__execute_read_sql((device_name,), q_str)

    @decorater_log_in_out
    def write_simultaneous_table(self, functions, params):
        '''
        Establish the DB connection which carries transaction and execute one by one using the parameter
        which has the method featuring data-feeding style.
        Parameter:
            functions:Method list
            params:Parameter list
        Return value:
            Execution result : boolean
        '''
        func_dict = {
            self.write_lagmemberif_info.__name__: self.write_lagmemberif_info,
            self.write_leaf_bgp_basic_info.__name__:
                self.write_leaf_bgp_basic_info,
            self.write_vlanif_info.__name__: self.write_vlanif_info,
            self.write_lagif_info.__name__: self.write_lagif_info,
            self.write_vrf_detail_info.__name__: self.write_vrf_detail_info,
            self.write_vrrp_detail_info.__name__: self.write_vrrp_detail_info,
            self.write_vrrp_trackif_info.__name__:
                self.write_vrrp_trackif_info,
            self.write_bgp_detail_info.__name__: self.write_bgp_detail_info,
            self.write_static_route_detail_info.__name__:
                self.write_static_route_detail_info,
            self.write_transaction_mgmt_info.__name__:
                self.write_transaction_mgmt_info,
            self.write_device_status_mgmt_info.__name__:
                self.write_device_status_mgmt_info,
            self.write_device_regist_info.__name__:
                self.write_device_regist_info,
            self.delete_device_status_mgmt_info_linked_tr_id.__name__:
                self.delete_device_status_mgmt_info_linked_tr_id,
            self.write_physical_if_info.__name__: self.write_physical_if_info,
            self.write_cluster_link_if_info.__name__:
                self.write_cluster_link_if_info,
            self.write_breakout_if_info.__name__: self.write_breakout_if_info,
            self.write_inner_link_if_info.__name__:
                self.write_inner_link_if_info,
            self.write_system_status_info.__name__:
                self.write_system_status_info,
            self.recover_if_info.__name__: self.recover_if_info,
            self.write_acl_detail_info.__name__:
                self.write_acl_detail_info,
            self.write_acl_info.__name__:
                self.write_acl_info,
            self.write_dummy_vlan_if_info.__name__:
                self.write_dummy_vlan_if_info,
            self.write_multi_homing_info.__name__:
                self.write_multi_homing_info,
            self.write_nvr_administrator_password_info.__name__:
                self.write_nvr_administrator_password_info,
            self.write_device_configration_info.__name__:
                self.write_device_configration_info,
        }

        con = None
        db_trans = None
        try:
            con = self.__connect_db()
            db_trans = con.begin()

            for index, func in enumerate(functions):
                param = params[index].copy()
                target_func = func_dict[func.__name__]
                is_upsert_ok = target_func(conn=con, **param)
                if not is_upsert_ok:
                    raise ValueError

            db_trans.commit()
            is_insert = True
        except Exception, ex_message:
            if db_trans:
                db_trans.rollback()
            GlobalModule.EM_LOGGER.error(
                '305003 Database Control Error')
            GlobalModule.EM_LOGGER.debug(
                'db_error_message = %s' % (ex_message,))
            is_insert = False
        finally:
            self.__close_db(con)
        return is_insert

    @decorater_log_in_out
    def write_physical_if_info(self,
                               db_control,
                               device_name,
                               if_name,
                               condition,
                               conn=None):
        '''
        The method which registers/updates/deletes the information of the physical interface information table
        based on the DB control information.
        Parameter:
            db_control:DB control
            device_name:Device name
            if_name:IF name
            condition:Port condition
        Return value:
            Execution result : boolean(True or False)
        '''
        table_name = self.table_PhysicalIfInfo

        is_not_null = True
        if db_control == self.__delete_flg and (if_name is None):
            is_not_null = False

        is_ok = self.__check_parameter(device_name, str, not_null=True)
        is_ok = is_ok and self.__check_parameter(if_name,
                                                 str, not_null=is_not_null)
        if db_control != self.__delete_flg:
            is_ok = is_ok and self.__check_parameter(condition,
                                                     int, not_null=True)

        if not is_ok:
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False

        tmp_list = []
        tmp_list.append(device_name)
        if is_not_null:
            tmp_list.append(if_name)
        where_param = tuple(tmp_list)

        tmp_list.append(condition)
        upsert_param = tuple(tmp_list)

        where_query_str = []
        where_query_str.append("    WHERE")
        where_query_str.append("          device_name  = %s")
        if is_not_null:
            where_query_str.append("    AND   if_name      = %s")

        delete_query = self.__gen_delete_sql(table_name, where_query_str)

        select_query = self.__gen_select_sql(table_name, where_query_str)

        insert_query, update_query = (
            self.__gen_upsert_sql(table_name, where_query_str,
                                  "device_name",
                                  "if_name",
                                  "condition"))

        return self.__exec_write_sql(select_query,
                                     insert_query,
                                     update_query,
                                     delete_query,
                                     upsert_param,
                                     where_param,
                                     db_control,
                                     conn)

    @decorater_log_in_out
    def read_physical_if_info(self, device_name):
        '''
        The method which returns the information of the physical interface information table.
        Parameter:
            device_name:Device name
        Return value:
            Execution result : boolean(True or False)
            Refer to the physical interface information table : tuple
        '''
        table_name = self.table_PhysicalIfInfo

        if not self.__check_parameter(device_name, str, not_null=True):
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False, None

        where_query_str = ["WHERE device_name = %s"]
        q_str = self.__gen_select_sql(table_name, where_query_str)

        return self.__execute_read_sql((device_name,), q_str)

    @decorater_log_in_out
    def write_cluster_link_if_info(self,
                                   db_control,
                                   device_name,
                                   if_name,
                                   if_type=None,
                                   cluster_link_ip_address=None,
                                   cluster_link_ip_prefix=None,
                                   igp_cost=None,
                                   conn=None):
        '''
            The method which registers/updates/deletes the information of the link interface information table among the clusters
            based on the DB control information.
        Parameter:
            db_control:DB control
            device_name:Device name
            if_name:IF name
            if_type:IF type
            cluster_link_ip_address:IF IPv4address for the link among the cluters
            cluster_link_ip_prefix:Pre-fix of IF IPv4address for the link among the cluters
            igp_cost:IGP cost value
        Return value:
            Execution result : boolean(True or False)
        '''
        table_name = self.table_ClusterLinkIfInfo

        is_not_null = True
        if db_control == self.__delete_flg and if_name is None:
            is_not_null = False

        is_ok = self.__check_parameter(device_name, str, not_null=True)
        is_ok = is_ok and self.__check_parameter(if_name,
                                                 str, not_null=is_not_null)
        if db_control != self.__delete_flg:
            is_ok = is_ok and self.__check_parameter(if_type,
                                                     int, not_null=True)
            is_ok = is_ok and self.__check_parameter(cluster_link_ip_address,
                                                     str)
            is_ok = is_ok and self.__check_parameter(cluster_link_ip_prefix,
                                                     int)
            is_ok = is_ok and self.__check_parameter(igp_cost, int)

        if not is_ok:
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False

        tmp_list = []
        tmp_list.append(device_name)
        if is_not_null:
            tmp_list.append(if_name)
        where_param = tuple(tmp_list)

        tmp_list.append(if_type)
        tmp_list.append(cluster_link_ip_address)
        tmp_list.append(cluster_link_ip_prefix)
        tmp_list.append(igp_cost)
        upsert_param = tuple(tmp_list)

        where_query_str = []
        where_query_str.append("    WHERE")
        where_query_str.append("          device_name  = %s")
        if is_not_null:
            where_query_str.append("    AND   if_name      = %s")

        delete_query = self.__gen_delete_sql(table_name, where_query_str)

        select_query = self.__gen_select_sql(table_name, where_query_str)

        insert_query, update_query = (
            self.__gen_upsert_sql(table_name, where_query_str,
                                  "device_name",
                                  "if_name",
                                  "if_type",
                                  "cluster_link_ip_address",
                                  "cluster_link_ip_prefix",
                                  "igp_cost"))

        return self.__exec_write_sql(select_query,
                                     insert_query,
                                     update_query,
                                     delete_query,
                                     upsert_param,
                                     where_param,
                                     db_control,
                                     conn)

    @decorater_log_in_out
    def read_cluster_link_if_info(self, device_name):
        '''
       The method which returns the information of Link interface information table among the clusters.
       Parameter:
            device_name:Device name
        Return value:
            Execution result : boolean(True or False)
            Refer to the Link interface information table among the clusters : tuple
        '''
        table_name = self.table_ClusterLinkIfInfo

        if not self.__check_parameter(device_name, str, not_null=True):
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False, None

        where_query_str = ["WHERE device_name = %s"]
        q_str = self.__gen_select_sql(table_name, where_query_str)

        return self.__execute_read_sql((device_name,), q_str)

    @decorater_log_in_out
    def write_breakout_if_info(self,
                               db_control,
                               device_name,
                               base_interface,
                               speed=None,
                               breakout_num=None,
                               conn=None):
        '''
        The method which registers/updates/deletes the information of the BreakoutIF information table
        based on the DB control information.
        Parameter:
            db_control:DB control
            device_name:Device name
            base_interface:breakout base IF name
            speed:Speed after breakout
            breakout_num:Breakout number
        Return value:
            Execution result : boolean(True or False)
        '''
        table_name = self.table_BreakoutIfInfo

        is_not_null = True
        if db_control == self.__delete_flg and (base_interface is None):
            is_not_null = False

        is_ok = self.__check_parameter(device_name, str, not_null=True)
        is_ok = is_ok and self.__check_parameter(base_interface,
                                                 str, not_null=is_not_null)
        if db_control != self.__delete_flg:
            is_ok = is_ok and self.__check_parameter(speed, str, not_null=True)
            is_ok = is_ok and self.__check_parameter(breakout_num,
                                                     int, not_null=True)

        if not is_ok:
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False

        tmp_list = []
        tmp_list.append(device_name)
        if is_not_null:
            tmp_list.append(base_interface)
        where_param = tuple(tmp_list)

        tmp_list.append(speed)
        tmp_list.append(breakout_num)
        upsert_param = tuple(tmp_list)

        where_query_str = []
        where_query_str.append("    WHERE")
        where_query_str.append("          device_name     = %s")
        if is_not_null:
            where_query_str.append("    AND   base_interface  = %s")

        delete_query = self.__gen_delete_sql(table_name, where_query_str)

        select_query = self.__gen_select_sql(table_name, where_query_str)

        insert_query, update_query = (
            self.__gen_upsert_sql(table_name, where_query_str,
                                  "device_name",
                                  "base_interface",
                                  "speed",
                                  "breakout_num"))

        return self.__exec_write_sql(select_query,
                                     insert_query,
                                     update_query,
                                     delete_query,
                                     upsert_param,
                                     where_param,
                                     db_control,
                                     conn)

    @decorater_log_in_out
    def read_breakout_if_info(self, device_name):
        '''
        The method which returns the information of the Breakout IF information table.
        Parameter:
            device_name:Device name
        Return value:
            Execution result : boolean(True or False)
            Refer to the Breakout IF information table : tuple
        '''
        table_name = self.table_BreakoutIfInfo

        if not self.__check_parameter(device_name, str, not_null=True):
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False, None

        where_query_str = ["WHERE device_name = %s"]
        q_str = self.__gen_select_sql(table_name, where_query_str)

        return self.__execute_read_sql((device_name,), q_str)

    @decorater_log_in_out
    def write_inner_link_if_info(self,
                                 db_control,
                                 device_name,
                                 if_name,
                                 if_type=None,
                                 vlan_id=None,
                                 link_speed=None,
                                 internal_link_ip_address=None,
                                 internal_link_ip_prefix=None,
                                 cost=None,
                                 conn=None):
        '''
        The method which registers/updates/deletes the information of the internal Link interface information table
        based on the DB control information.
        Parameter:
            db_control:DB control
            device_name:Device name
            if_name:IF name
            if_type:IF type
            link_speed:Link speed
            internal_link_ip_address:IF IPv4address for internal Link
            internal_link_ip_prefix:Pre-fix of the IF IPv4address for internal Link
        Return value:
            Execution result : boolean(True or False)            
            cost:cost value
        Return value:
            Execution result : boolean(True or False)
        '''
        table_name = self.table_InnerLinkIfInfo

        is_not_null = True
        if db_control == self.__delete_flg and (if_name is None):
            is_not_null = False

        is_ok = self.__check_parameter(device_name, str, not_null=True)
        is_ok = is_ok and self.__check_parameter(if_name, str,
                                                 not_null=is_not_null)
        if db_control != self.__delete_flg:
            is_ok = is_ok and self.__check_parameter(if_type,
                                                     int, not_null=True)
            is_ok = is_ok and self.__check_parameter(vlan_id, int)
            is_ok = is_ok and self.__check_parameter(link_speed, str)
            is_ok = is_ok and self.__check_parameter(internal_link_ip_address,
                                                     str)
            is_ok = is_ok and self.__check_parameter(internal_link_ip_prefix,
                                                     int)
            is_ok = is_ok and self.__check_parameter(cost, int)

        if not is_ok:
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False

        tmp_list = []
        tmp_list.append(device_name)
        if is_not_null:
            tmp_list.append(if_name)
        where_param = tuple(tmp_list)

        tmp_list.append(if_type)
        tmp_list.append(vlan_id)
        tmp_list.append(link_speed)
        tmp_list.append(internal_link_ip_address)
        tmp_list.append(internal_link_ip_prefix)
        tmp_list.append(cost)
        upsert_param = tuple(tmp_list)

        where_query_str = []
        where_query_str.append("    WHERE")
        where_query_str.append("          device_name  = %s")
        if is_not_null:
            where_query_str.append("    AND   if_name      = %s")

        delete_query = self.__gen_delete_sql(table_name, where_query_str)

        select_query = self.__gen_select_sql(table_name, where_query_str)

        insert_query, update_query = (
            self.__gen_upsert_sql(table_name, where_query_str,
                                  "device_name",
                                  "if_name",
                                  "if_type",
                                  "vlan_id",
                                  "link_speed",
                                  "internal_link_ip_address",
                                  "internal_link_ip_prefix",
                                  "cost"))

        return self.__exec_write_sql(select_query,
                                     insert_query,
                                     update_query,
                                     delete_query,
                                     upsert_param,
                                     where_param,
                                     db_control,
                                     conn)

    @decorater_log_in_out
    def read_inner_link_if_info(self, device_name):
        '''
        The method which returns the information of the internal Link IF information table.
        Parameter:
            device_name:Device name
        Return value:
            Execution result : boolean(True or False)
            Refer to the internal Link IF information table : tuple
        '''
        table_name = self.table_InnerLinkIfInfo

        if not self.__check_parameter(device_name, str, not_null=True):
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False, None

        where_query_str = ["WHERE device_name = %s"]
        q_str = self.__gen_select_sql(table_name, where_query_str)

        return self.__execute_read_sql((device_name,), q_str)

    @decorater_log_in_out
    def write_system_status_info(self,
                                 db_control,
                                 service_status,
                                 conn=None):
        '''
        The method which registers/updates/deletes the information of the system status information table
        based on the DB control information.
        Explanation about parameter:
            db_control:DB control
            system_status:System status
        Return value:
            Execution result : boolean(True or False)
        '''
        table_name = self.table_EmSystemStatusInfo

        is_ok = self.__check_parameter(service_status, int, not_null=True)

        if not is_ok:
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False

        tmp_list = []
        tmp_list.append(EmSysCommonUtilityDB.STATE_STOP)
        tmp_list.append(EmSysCommonUtilityDB.STATE_READY_TO_START)
        tmp_list.append(EmSysCommonUtilityDB.STATE_CHANGE_OVER)
        tmp_list.append(EmSysCommonUtilityDB.STATE_READY_TO_STOP)
        tmp_list.append(EmSysCommonUtilityDB.STATE_START)
        where_param = tuple(tmp_list)

        upd_list = []
        upd_list.append(service_status)
        upsert_param = tuple(upd_list)

        where_query_str = []
        where_query_str.append("    WHERE")
        where_query_str.append("          service_status = %s")
        where_query_str.append("    OR    service_status = %s")
        where_query_str.append("    OR    service_status = %s")
        where_query_str.append("    OR    service_status = %s")
        where_query_str.append("    OR    service_status = %s")

        delete_query = self.__gen_delete_sql(table_name, where_query_str)

        select_query = self.__gen_select_sql(table_name, where_query_str)

        insert_query, update_query = (
            self.__gen_upsert_sql(table_name, where_query_str,
                                  "service_status"))

        return self.__exec_write_sql(select_query,
                                     insert_query,
                                     update_query,
                                     delete_query,
                                     upsert_param,
                                     where_param,
                                     db_control,
                                     conn)

    @decorater_log_in_out
    def read_system_status_info(self):
        '''
        The method which returns the information of the system status information table.
        Explanation about parameter:
        Return value:
            Execution result : boolean(True or False)
            Refer to the system status information table : tuple
        '''
        table_name = self.table_EmSystemStatusInfo

        where_query_str = []
        q_str = self.__gen_select_sql(table_name, where_query_str)

        return self.__execute_read_sql((), q_str)

    @decorater_log_in_out
    def write_acl_info(self,
                       db_control,
                       device_name,
                       acl_id,
                       if_name=None,
                       vlan_id=None,
                       conn=None):
        '''
        The method which registers/udpates/deletes the information of ACL Configuration Information Table based on DB
        Parameter：
            db_control:DB Control
            device_name:Device Name
            acl_id:ACL Configuration ID
            if_name:IF Name
            vlan_id:VLANID
        Return Value:
            Execution Result : boolean(True or False)
        '''
        table_name = self.table_ACLInfo

        is_not_null = True
        if db_control == self.__delete_flg and (acl_id is None):
            is_not_null = False

        is_ok = self.__check_parameter(device_name, str, not_null=True)
        is_ok = is_ok and self.__check_parameter(
            acl_id, int, not_null=is_not_null)

        if db_control != self.__delete_flg:
            is_ok = (is_ok and
                     self.__check_parameter(if_name, str))
            is_ok = (is_ok and
                     self.__check_parameter(vlan_id, int))

        if not is_ok:
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False

        tmp_list = []
        tmp_list.append(device_name)
        if is_not_null:
            tmp_list.append(acl_id)
        where_param = tuple(tmp_list)

        tmp_list.append(if_name)
        tmp_list.append(vlan_id)
        upsert_param = tuple(tmp_list)

        where_query_str = []
        where_query_str.append("    WHERE")
        where_query_str.append("          device_name = %s")
        if is_not_null:
            where_query_str.append("    AND   acl_id     = %s")

        delete_query = self.__gen_delete_sql(table_name, where_query_str)

        select_query = self.__gen_select_sql(table_name, where_query_str)

        insert_query, update_query = (
            self.__gen_upsert_sql(table_name, where_query_str,
                                  "device_name",
                                  "acl_id",
                                  "if_name",
                                  "vlan_id"))

        return self.__exec_write_sql(select_query,
                                     insert_query,
                                     update_query,
                                     delete_query,
                                     upsert_param,
                                     where_param,
                                     db_control,
                                     conn)

    @decorater_log_in_out
    def read_acl_info(self, device_name):
        '''
        The method which returns information of ACL Configuration Information Table
        Parameter:
            device_name:Device Name
        Return Value:
            Execution Result : boolean(True or False)
            Refer to BGP Detailed Information Table : tuple
        '''
        table_name = self.table_ACLInfo

        if not self.__check_parameter(device_name, str, not_null=True):
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False, None

        where_query_str = ["WHERE device_name = %s"]
        q_str = self.__gen_select_sql(table_name, where_query_str)

        return self.__execute_read_sql((device_name,), q_str)

    @decorater_log_in_out
    def read_acl_all_info(self,):
        '''
        The Method which returns information of ACL Configuration Inforamtion Table
        Return Value:
            Execution Result : boolean(True or False)
            Refer to BGP Detailed Information Table : tuple
        '''
        table_name = self.table_ACLInfo

        where_query_str = []
        q_str = self.__gen_select_sql(table_name, where_query_str)

        return self.__execute_read_sql((), q_str)

    @decorater_log_in_out
    def write_acl_detail_info(self,
                              db_control,
                              device_name,
                              acl_id,
                              term_name,
                              action=None,
                              direction=None,
                              source_mac_address=None,
                              destination_mac_address=None,
                              source_ip_address=None,
                              destination_ip_address=None,
                              source_port=None,
                              destination_port=None,
                              protocol=None,
                              acl_priority=None,
                              conn=None):
        '''
        Method which registers/updates/deletes the information of ACL configuration information table based on DB Control Information
        Parameter：
            db_control:DB Control
            device_name:Device Name
            acl_id:ACL Configuration ID
            term_name:IF Name
            action:Action
            direction:Direction
            source_mac_address: Transmission Source MAC Address
            destination_mac_address:Transmission Destination MAC Address
            source_ip_address:Transmission Source IP Address
            destination_ip_address:Transmission Destination IP Address
            source_port:Transmission Source Port
            destination_port:Transmission Destination Port
            protocol:Protocol
            acl_priority:ACLpriority Value
            conn=None):

        Return value:
            Execution result : boolean(True or False)
        '''
        table_name = self.table_ACLDetailInfo

        is_not_null = True
        if db_control == self.__delete_flg and (acl_id is None and
                                                term_name is None):
            is_not_null = False

        is_ok = self.__check_parameter(device_name, str, not_null=True)
        is_ok = is_ok and self.__check_parameter(
            acl_id, int, not_null=is_not_null)
        is_ok = is_ok and self.__check_parameter(
            term_name, str, not_null=is_not_null)

        if db_control != self.__delete_flg:
            is_ok = (
                is_ok and
                self.__check_parameter(action, str, not_null=True))
            is_ok = (
                is_ok and
                self.__check_parameter(direction, str, not_null=True))
            is_ok = (
                is_ok and
                self.__check_parameter(source_mac_address, str))
            is_ok = (
                is_ok and
                self.__check_parameter(destination_mac_address, str))
            is_ok = (
                is_ok and
                self.__check_parameter(source_ip_address, str))
            is_ok = (
                is_ok and
                self.__check_parameter(destination_ip_address, str))
            is_ok = (
                is_ok and
                self.__check_parameter(source_port, int))
            is_ok = (
                is_ok and
                self.__check_parameter(destination_port, int))
            is_ok = (
                is_ok and
                self.__check_parameter(protocol, str))
            is_ok = (
                is_ok and
                self.__check_parameter(acl_priority, int))

        if not is_ok:
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False
        tmp_list = []
        tmp_list.append(device_name)
        if is_not_null:
            tmp_list.append(acl_id)
            tmp_list.append(term_name)

        where_param = tuple(tmp_list)

        tmp_list.append(action)
        tmp_list.append(direction)
        tmp_list.append(source_mac_address)
        tmp_list.append(destination_mac_address)
        tmp_list.append(source_ip_address)
        tmp_list.append(destination_ip_address)
        tmp_list.append(source_port)
        tmp_list.append(destination_port)
        tmp_list.append(protocol)
        tmp_list.append(acl_priority)

        upsert_param = tuple(tmp_list)

        where_query_str = []
        where_query_str.append("    WHERE")
        where_query_str.append("          device_name = %s")
        if is_not_null:
            where_query_str.append("    AND   acl_id     = %s")
            where_query_str.append("    AND   term_name     = %s")

        delete_query = self.__gen_delete_sql(table_name, where_query_str)

        select_query = self.__gen_select_sql(table_name, where_query_str)

        insert_query, update_query = (
            self.__gen_upsert_sql(table_name, where_query_str,
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
                                  "acl_priority"))

        return self.__exec_write_sql(select_query,
                                     insert_query,
                                     update_query,
                                     delete_query,
                                     upsert_param,
                                     where_param,
                                     db_control,
                                     conn)

    @decorater_log_in_out
    def read_acl_detail_info(self, device_name):
        '''
        Method which returns the informatin of ACL configuration details informatioin table
        Parameter:
            device_name: Device Name
        Return Value:
            Execution Result : boolean(True or False)
            Refer to BGP Detailed Information Table : tuple
        '''
        table_name = self.table_ACLDetailInfo

        if not self.__check_parameter(device_name, str, not_null=True):
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False, None

        where_query_str = ["WHERE device_name = %s"]
        q_str = self.__gen_select_sql(table_name, where_query_str)

        return self.__execute_read_sql((device_name,), q_str)

    @decorater_log_in_out
    def read_acl_detail_all_info(self):
        '''
        Method which returns the entire information of ACL configuration details information table
        Return Value:
            Execution Result : boolean(True or False)
            Refer to BGP Detailed Information Table : tuple
        '''
        table_name = self.table_ACLDetailInfo

        where_query_str = []
        q_str = self.__gen_select_sql(table_name, where_query_str)

        return self.__execute_read_sql((), q_str)

    @decorater_log_in_out
    def write_dummy_vlan_if_info(self,
                                 db_control,
                                 device_name,
                                 vlan_id,
                                 slice_name,
                                 vni=None,
                                 irb_ipv4_address=None,
                                 irb_ipv4_prefix=None,
                                 vrf_name=None,
                                 vrf_id=None,
                                 rt=None,
                                 rd=None,
                                 router_id=None,
                                 vrf_loopback_interface_address=None,
                                 vrf_loopback_interface_prefix=None,
                                 conn=None):
        '''
        The method which registers/updates/deletes the information of Vlan interface information based on DB Control information

        Parameter Explanation :
            db_control:DB Control
            device_name: Device Name
            vlan_id:VLAN ID
            slice_name:Slice Name
            vni:VNI Value
            irb_ipv4_address:IPv4 Address for IRB setting
            irb_ipv4_prefix:IPv4 Address Prefix for IRB setting
            vrf_name:VRFName
            vrf_id:VRF-ID
            rt:RT
            rd:RD
            router_id: RouterID
            vrf_loopback_interface_address:Loopback IF Address for VRF
            vrf_loopback_interface_prefix:Loopback IF Address Prefix for VRF
        Return Value:
            Execution Result : boolean(True or False)
        '''
        table_name = self.table_DummyVlanIfInfo

        is_not_null = True
        if db_control == self.__delete_flg and (vlan_id is None and
                                                slice_name is None):
            is_not_null = False

        is_ok = self.__check_parameter(device_name, str, not_null=True)
        is_ok = is_ok and self.__check_parameter(
            vlan_id, int, not_null=is_not_null)
        is_ok = is_ok and self.__check_parameter(
            slice_name, str, not_null=is_not_null)

        if db_control != self.__delete_flg:
            is_ok = is_ok and self.__check_parameter(vni, int)
            is_ok = is_ok and self.__check_parameter(irb_ipv4_address, str)
            is_ok = is_ok and self.__check_parameter(irb_ipv4_prefix, int)
            is_ok = is_ok and self.__check_parameter(vrf_name, str)
            is_ok = is_ok and self.__check_parameter(vrf_id, int)
            is_ok = is_ok and self.__check_parameter(rt, str)
            is_ok = is_ok and self.__check_parameter(rd, str)
            is_ok = is_ok and self.__check_parameter(router_id, str)
            is_ok = is_ok and self.__check_parameter(
                vrf_loopback_interface_address, str)
            is_ok = is_ok and self.__check_parameter(
                vrf_loopback_interface_prefix, int)
        if not is_ok:
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False
        tmp_list = []
        tmp_list.append(device_name)
        if is_not_null:
            tmp_list.append(vlan_id)
            tmp_list.append(slice_name)
        where_param = tuple(tmp_list)

        tmp_list.append(vni)
        tmp_list.append(irb_ipv4_address)
        tmp_list.append(irb_ipv4_prefix)
        tmp_list.append(vrf_name)
        tmp_list.append(vrf_id)
        tmp_list.append(rt)
        tmp_list.append(rd)
        tmp_list.append(router_id)
        tmp_list.append(vrf_loopback_interface_address)
        tmp_list.append(vrf_loopback_interface_prefix)
        upsert_param = tuple(tmp_list)

        where_query_str = []
        where_query_str.append("    WHERE")
        where_query_str.append("          device_name = %s")
        where_query_str.append("    AND   vlan_id = %s")
        where_query_str.append("    AND   slice_name = %s")

        delete_query = self.__gen_delete_sql(table_name, where_query_str)

        select_query = self.__gen_select_sql(table_name, where_query_str)

        insert_query, update_query = (
            self.__gen_upsert_sql(table_name, where_query_str,
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
                                  "vrf_loopback_interface_prefix"))

        return self.__exec_write_sql(select_query,
                                     insert_query,
                                     update_query,
                                     delete_query,
                                     upsert_param,
                                     where_param,
                                     db_control,
                                     conn)

    @decorater_log_in_out
    def read_dummy_vlan_if_info(self, device_name):
        '''
        Method which returns information of Dummy VLAN Interface Information Table
        Parameter:
            device_name: Device Name
        Return Value:
            Execution Result : boolean(True or False)
            Refer to Dummy VLAN Interface Information Table : tuple
        '''
        table_name = self.table_DummyVlanIfInfo

        if not self.__check_parameter(device_name, str, not_null=True):
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False, None

        where_query_str = ["WHERE device_name = %s"]
        q_str = self.__gen_select_sql(table_name, where_query_str)

        return self.__execute_read_sql((device_name,), q_str)

    @decorater_log_in_out
    def write_multi_homing_info(self,
                                db_control,
                                device_name,
                                anycast_id=None,
                                anycast_address=None,
                                clag_if_address=None,
                                clag_if_prefix=None,
                                backup_address=None,
                                peer_address=None,
                                conn=None):
        '''
        Method which registers/updates/deletes the information of Multihoming Configuration Information Table based on DB control information

        Parameter Explanation :
            db_control:DB Control
            device_name: Device Name
            anycast_id:AnycastID
            anycast_address:AnycastIP Address
            clag_if_address:Clag Bridge IF IP Address
            clag_if_prefix:Clag Bridge IF Prefix
            backup_address:Backup IP Address
            peer_address:Peer IP Address
        Return Value:
            Execution Result : boolean(True or False)
        '''
        table_name = self.table_MultiHomingInfo

        is_ok = self.__check_parameter(device_name, str, not_null=True)
        if db_control != self.__delete_flg:
            is_ok = is_ok and self.__check_parameter(
                anycast_id, int, not_null=True)
            is_ok = is_ok and self.__check_parameter(
                anycast_address, str, not_null=True)
            is_ok = is_ok and self.__check_parameter(
                clag_if_address, str, not_null=True)
            is_ok = is_ok and self.__check_parameter(
                clag_if_prefix, int, not_null=True)
            is_ok = is_ok and self.__check_parameter(
                backup_address, str, not_null=True)
            is_ok = is_ok and self.__check_parameter(
                peer_address, str, not_null=True)

        if not is_ok:
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False

        tmp_list = []
        tmp_list.append(device_name)
        where_param = tuple(tmp_list)

        tmp_list.append(anycast_id)
        tmp_list.append(anycast_address)
        tmp_list.append(clag_if_address)
        tmp_list.append(clag_if_prefix)
        tmp_list.append(backup_address)
        tmp_list.append(peer_address)
        upsert_param = tuple(tmp_list)

        where_query_str = []
        where_query_str.append("    WHERE")
        where_query_str.append("          device_name = %s")

        delete_query = self.__gen_delete_sql(table_name, where_query_str)

        select_query = self.__gen_select_sql(table_name, where_query_str)

        insert_query, update_query = (
            self.__gen_upsert_sql(table_name, where_query_str,
                                  "device_name",
                                  "anycast_id",
                                  "anycast_address",
                                  "clag_if_address",
                                  "clag_if_prefix",
                                  "backup_address",
                                  "peer_address"))

        return self.__exec_write_sql(select_query,
                                     insert_query,
                                     update_query,
                                     delete_query,
                                     upsert_param,
                                     where_param,
                                     db_control,
                                     conn)

    @decorater_log_in_out
    def read_multi_homing_info(self, device_name):
        '''
        Method which returns the information of Multihoming Configuration Information Table
        Parameter:
            device_name:Device Name
        Return Value:
            Execution Result : boolean(True or False)
            Refer to Multihoming Configuration Information Table : tuple
        '''
        table_name = self.table_MultiHomingInfo

        if not self.__check_parameter(device_name, str, not_null=True):
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False, None

        where_query_str = ["WHERE device_name = %s"]
        q_str = self.__gen_select_sql(table_name, where_query_str)

        return self.__execute_read_sql((device_name,), q_str)

    @decorater_log_in_out
    def read_multi_homing_all_info(self):
        '''
        Method which returns the information of Multihoming Configuration Information Table
        Return Value:
            Execution Result : boolean(True or False)
            Refer to Multihoming Configuration Information Table : tuple
        '''
        table_name = self.table_MultiHomingInfo

        where_query_str = []
        q_str = self.__gen_select_sql(table_name, where_query_str)

        return self.__execute_read_sql((), q_str)

    @decorater_log_in_out
    def recover_if_info(self,
                        conn,
                        db_control,
                        table_name,
                        if_name_column,
                        if_name_new,
                        **key_dict):
        '''
        Method which updates IFName of each table
        Parameter:
            db_control:DB Control
            table_name:Table Name
            if_name_column:IFName Column Name
            if_name_new:IFName after update
            conn:DB connection
            key_dict:key= Column Name, value= Value of Column
        Return Value:
            Execution Result : boolean(True or False)
        '''
        is_ok = self.__check_parameter(if_name_new,
                                       str, not_null=True)
        if not is_ok:
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            GlobalModule.EM_LOGGER.debug("if_name_new = %s" % if_name_new)
            return False

        tmp_list = []
        where_query_str = []
        for column_name, value in key_dict.items():
            tmp_list.append(value)
            if where_query_str:
                where_query_str.append("    AND   " + column_name + "= %s")
            else:
                where_query_str.append("    WHERE")
                where_query_str.append("          " + column_name + " = %s")
        where_param = tuple(tmp_list)

        upsert_column = if_name_column
        upsert_param = (if_name_new,)

        select_query = self.__gen_select_sql(table_name, where_query_str)

        update_query = \
            self.__gen_upsert_sql(table_name, where_query_str,
                                  upsert_column)[1]

        return self.__exec_write_sql(select_query,
                                     None,
                                     update_query,
                                     None,
                                     upsert_param,
                                     where_param,
                                     db_control,
                                     conn)

    @decorater_log_in_out
    def write_device_configration_info(self,
                                       db_control,
                                       device_name,
                                       working_date=None,
                                       working_time=None,
                                       platform_name=None,
                                       vrf_name=None,
                                       practice_system=None,
                                       log_type=None,
                                       get_timing=None,
                                       config_file=None,
                                       conn=None):
        '''
        Method which registers, updates  and deletes configuration information table
        by DB control information.
        Parameter:
            db_control:DB cntrol
            device_name:device name
            working_date:working date
            working_time:working time
            platform_name:platform name
            vrf_name:VRF name
            practice_system:acting system
            log_type:log type
            get_timing:timing of obtaining
            config_file:configuration file
        Return Value:
           Execution Result : boolean(True or False)

        '''
        table_name = self.table_DeviceConfigrationinfo

        is_ok = self.__check_parameter(device_name, str, not_null=True)
        if db_control != self.__delete_flg:
            is_ok = (is_ok and
                     self.__check_parameter(working_date, str, not_null=True))
            is_ok = (is_ok and
                     self.__check_parameter(working_time, str, not_null=True))
            is_ok = (is_ok and
                     self.__check_parameter(platform_name, str, not_null=True))
            is_ok = (is_ok and
                     self.__check_parameter(vrf_name, str, not_null=False))
            is_ok = (
                is_ok and
                self.__check_parameter(practice_system, str, not_null=False))
            is_ok = (is_ok and
                     self.__check_parameter(log_type, str, not_null=False))
            is_ok = (is_ok and
                     self.__check_parameter(get_timing, int, not_null=False))
            is_ok = (is_ok and
                     self.__check_parameter(config_file, str, not_null=True))

        if not is_ok:
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False

        tmp_list = []
        tmp_list.append(device_name)
        where_param = tuple(tmp_list)

        tmp_list.append(working_date)
        tmp_list.append(working_time)
        tmp_list.append(platform_name)
        tmp_list.append(vrf_name)
        tmp_list.append(practice_system)
        tmp_list.append(log_type)
        tmp_list.append(get_timing)
        tmp_list.append(config_file)
        upsert_param = tuple(tmp_list)

        where_query_str = []
        where_query_str.append("    WHERE")
        where_query_str.append("          device_name = %s")
        if db_control != self.__delete_flg:
            where_query_str.append("    AND   1 = 2")

        delete_query = self.__gen_delete_sql(table_name, where_query_str)

        select_query = self.__gen_select_sql(table_name, where_query_str)

        insert_query, update_query = (
            self.__gen_upsert_sql(table_name,
                                  where_query_str,
                                  "device_name",
                                  "working_date",
                                  "working_time",
                                  "platform_name",
                                  "vrf_name",
                                  "practice_system",
                                  "log_type",
                                  "get_timing",
                                  "config_file"))

        return self.__exec_write_sql(select_query,
                                     insert_query,
                                     update_query,
                                     delete_query,
                                     upsert_param,
                                     where_param,
                                     db_control,
                                     conn)

    @decorater_log_in_out
    def read_device_configration_info(self, device_name):
        '''
        Method which returns information of coniguration information table.
        Parameter:
            device_name: device name
        Return Value:
            Execution Result : boolean(True or False)
            Configuration information table : tuple
        '''
        table_name = self.table_DeviceConfigrationinfo

        if not self.__check_parameter(device_name, str, not_null=True):
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False, None

        where_query_str = ["WHERE device_name = %s"]
        q_str = self.__gen_select_sql(table_name, where_query_str)

        return self.__execute_read_sql((device_name,), q_str)

    @decorater_log_in_out
    def write_nvr_administrator_password_info(self,
                                              db_control,
                                              device_name,
                                              administrator_password=None,
                                              conn=None):
        '''
        Method which registers, updates  and deletes password management table for NVR
        by DB control information.
        Parameter:
            db_control:DB control
            device_name:device name
            administrator_password:Administrator password
        Return Value:
            Execution Result : boolean(True or False)
        '''
        table_name = self.table_NvrAdminPasswordMgmt

        is_ok = self.__check_parameter(device_name, str, not_null=True)
        if db_control != self.__delete_flg:
            is_ok = (is_ok and self.__check_parameter(administrator_password,
                                                      str,
                                                      not_null=True))

        if not is_ok:
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False

        tmp_list = []
        tmp_list.append(device_name)
        where_param = tuple(tmp_list)

        tmp_list.append(administrator_password)
        upsert_param = tuple(tmp_list)

        where_query_str = []
        where_query_str.append("    WHERE")
        where_query_str.append("          device_name = %s")

        delete_query = self.__gen_delete_sql(table_name, where_query_str)

        select_query = self.__gen_select_sql(table_name, where_query_str)

        insert_query, update_query = (
            self.__gen_upsert_sql(table_name,
                                  where_query_str,
                                  "device_name",
                                  "administrator_password"))

        return self.__exec_write_sql(select_query,
                                     insert_query,
                                     update_query,
                                     delete_query,
                                     upsert_param,
                                     where_param,
                                     db_control,
                                     conn)

    @decorater_log_in_out
    def read_nvr_administrator_password_info(self, device_name):
        '''
        Method which returns password  management information table for NVR.
            device_name: device name
        Return Value:
            Execution Result : boolean(True or False)
            password  management information table for NVR : tuple    
        '''
        table_name = self.table_NvrAdminPasswordMgmt

        if not self.__check_parameter(device_name, str, not_null=True):
            GlobalModule.EM_LOGGER.error('305003 Database Control Error')
            return False, None

        where_query_str = ["WHERE device_name = %s"]
        q_str = self.__gen_select_sql(table_name, where_query_str)

        return self.__execute_read_sql((device_name,), q_str)
