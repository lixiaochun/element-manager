# -*- coding: utf-8 -*-
from oslo_db.sqlalchemy.engines import create_engine
from uuid import UUID

import GlobalModule
from EmCommonLog import decorater_log


class EmDBControl(object):

    __delete_flg = "DELETE"

    @decorater_log
    def __init__(self):
        port_number = None
        user_name = None
        password = None
        db_table = None
        is_conf, address = (
        if is_conf:
            is_conf, port_number = (
        if is_conf:
            is_conf, user_name = (
        if is_conf:
            is_conf, password = (
        if is_conf:
            is_conf, db_table = (

        if not is_conf:
            GlobalModule.EM_LOGGER.debug(
                (address, port_number, user_name, password, db_table))
            raise IOError


        try:
            self.engine = create_engine(self.url)
        except Exception, ex_message:
            GlobalModule.EM_LOGGER.error(
            GlobalModule.EM_LOGGER.debug(
            raise


    @decorater_log
    def __connect_db(self):
        conn = self.engine.connect()

        return conn

    @staticmethod
    @decorater_log
    def __close_db(conn):
        if conn and not conn.closed:
            conn.close()

    @staticmethod
    @decorater_log
    def __close_result(result):
        if result and not result.closed:
            result.close()

    @staticmethod
    @decorater_log
    def __check_parameter(param, parms_class, not_null=False, b_size=None):
        is_ok = True
        if param is None:
            is_ok = False if not_null else True
            if not is_ok:
                GlobalModule.EM_LOGGER.debug(
                    % (param, not_null))
            return is_ok
        if b_size and parms_class is str and len(param) > b_size:
            is_ok = is_ok and False
        is_ok = is_ok and True if isinstance(param, parms_class) else False
        if not is_ok:
            GlobalModule.EM_LOGGER.debug(
                % (param, isinstance(param, parms_class)))
        return is_ok

    @staticmethod
    @decorater_log
    def __gen_upsert_sql(table_name, where_query_str, *table_cols):
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

        query_str = []
        query_str.append("UPDATE")
        query_str.append("    %s" % (table_name,))
        query_str.append("SET")
        query_str.extend(update_list)
        query_str.extend(where_query_str)

        return insert_query, update_query

    @staticmethod
    @decorater_log
    def __gen_delete_sql(table_name, where_query_str):
        query_str = []
        query_str.append("DELETE")
        query_str.append("    FROM")
        query_str.append("        %s" % (table_name,))
        query_str.extend(where_query_str)

    @staticmethod
    @decorater_log
    def __gen_select_sql(table_name, where_query_str):
        query_str = []
        query_str.append("SELECT")
        query_str.append("    *")
        query_str.append("    FROM")
        query_str.append("        %s" % (table_name,))
        query_str.extend(where_query_str)

    @decorater_log
    def __output_select_result(self, result):
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
        conn = None
        try:
            conn = self.__connect_db()
            result = conn.execute(sql, where_tuple)
            out_data = self.__output_select_result(result)
            is_ok = True
            GlobalModule.EM_LOGGER.error(
            GlobalModule.EM_LOGGER.debug(
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
        is_auto_commit = False
        result = None
        return_val = False
        try:
            if conn is None:
                is_auto_commit = True
                conn = self.__connect_db()
            if db_control == self.__delete_flg:
                GlobalModule.EM_LOGGER.debug(
                result = conn.execute(delete_query, where_param)
                return_val = True
            else:
                GlobalModule.EM_LOGGER.debug(
                result = conn.execute(select_query, where_param)
                row = result.fetchone()
                self.__close_result(result)
                if row:
                    update_param = upsert_param + where_param
                    GlobalModule.EM_LOGGER.debug(
                    result = conn.execute(update_query, update_param)
                else:
                    GlobalModule.EM_LOGGER.debug(

                    result = conn.execute(insert_query, upsert_param)
                return_val = True
            if is_auto_commit:
                GlobalModule.EM_LOGGER.error(
                GlobalModule.EM_LOGGER.debug(
                return_val = False
            else:
                raise
        finally:
            self.__close_result(result)
            if is_auto_commit:
                self.__close_db(conn)
        return return_val


    @decorater_log
    def read_transactionid_list(self):
        table_name = "TransactionMgmtInfo"

        q_str = self.__gen_select_sql(table_name, [])

        is_ok, tr_tuple = self.__execute_read_sql((), q_str)
        ret_list = []
        if is_ok:
            for item in tr_tuple:
                ret_list.append(item["transaction_id"])
        return is_ok, ret_list

    @decorater_log
    def initialize_order_mgmt_info(self):
        delete_trans_mgmt = self.__gen_delete_sql("transactionmgmtinfo", [])
        delete_device_mgmt = self.__gen_delete_sql("devicestatusmgmtinfo", [])

        conn = None
        db_trans = None
        try:
            conn = self.__connect_db()
            db_trans = conn.begin()
            conn.execute(delete_trans_mgmt)
            conn.execute(delete_device_mgmt)
            db_trans.commit()
            is_ok = True
            if db_trans:
                db_trans.rollback()
            GlobalModule.EM_LOGGER.error(
            GlobalModule.EM_LOGGER.debug(
            is_ok = False
        finally:
            self.__close_db(conn)
        return is_ok

    @decorater_log
    def delete_device_status_mgmt_info_linked_tr_id(self,
                                                    transaction_id,
                                                    conn=None):
        table_name = "DeviceStatusMgmtInfo"

        if not self.__check_parameter(transaction_id, UUID, not_null=True):
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

    @decorater_log
    def write_transaction_mgmt_info(self,
                                    db_control,
                                    transaction_id,
                                    transaction_status=None,
                                    service_type=None,
                                    order_type=None,
                                    order_text=None,
                                    conn=None):
        table_name = "TransactionMgmtInfo"

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

    @decorater_log
    def read_transaction_mgmt_info(self, transaction_id):
        table_name = "TransactionMgmtInfo"

        if not self.__check_parameter(transaction_id, UUID, not_null=True):
            return False, None

        where_query_str = ["WHERE transaction_id = %s"]
        q_str = self.__gen_select_sql(table_name, where_query_str)

        return self.__execute_read_sql((transaction_id,), q_str)

    @decorater_log
    def write_device_status_mgmt_info(self,
                                      db_control,
                                      device_name,
                                      transaction_id,
                                      transaction_status=None,
                                      conn=None):
        table_name = "DeviceStatusMgmtInfo"

        is_ok = self.__check_parameter(device_name, str, not_null=True)
        is_ok = is_ok and self.__check_parameter(
            transaction_id, UUID, not_null=True)
        if db_control != self.__delete_flg:
            is_ok = (
                is_ok and
                self.__check_parameter(transaction_status, int, not_null=True)
            )

        if not is_ok:
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

    @decorater_log
    def read_device_status_mgmt_info(self, transaction_id):
        table_name = "DeviceStatusMgmtInfo"

        if not self.__check_parameter(transaction_id, UUID, not_null=True):
            return False, None

        where_query_str = ["WHERE transaction_id = %s"]
        q_str = self.__gen_select_sql(table_name, where_query_str)

        return self.__execute_read_sql((transaction_id,), q_str)

    @decorater_log
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
                                 msdp_peer_address=None,
                                 msdp_local_address=None,
                                 as_number=None,
                                 pim_other_rp_address=None,
                                 pim_self_rp_address=None,
                                 pim_rp_address=None,
                                 vpn_type=None,
                                 conn=None):
        table_name = "DeviceRegistrationInfo"

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
                                                     str, not_null=True)
            is_ok = is_ok and self.__check_parameter(loopback_if_address,
                                                     str, not_null=True)
            is_ok = is_ok and self.__check_parameter(loopback_if_prefix,
                                                     str, not_null=True)
            is_ok = is_ok and self.__check_parameter(snmp_server_address,
                                                     str, not_null=True)
            is_ok = is_ok and self.__check_parameter(
                snmp_community, str, not_null=True)
            is_ok = (
                is_ok and
                self.__check_parameter(ntp_server_address, str, not_null=True)
            )
            is_ok = is_ok and self.__check_parameter(msdp_peer_address, str)
            is_ok = is_ok and self.__check_parameter(msdp_local_address, str)
            is_ok = is_ok and self.__check_parameter(as_number, int)
            is_ok = is_ok and self.__check_parameter(pim_other_rp_address, str)
            is_ok = is_ok and self.__check_parameter(pim_self_rp_address, str)
            is_ok = is_ok and self.__check_parameter(pim_rp_address, str)
            is_ok = is_ok and self.__check_parameter(vpn_type, int)

        if not is_ok:
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
        tmp_list.append(msdp_peer_address)
        tmp_list.append(msdp_local_address)
        tmp_list.append(as_number)
        tmp_list.append(pim_other_rp_address)
        tmp_list.append(pim_self_rp_address)
        tmp_list.append(pim_rp_address)
        tmp_list.append(vpn_type)
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
                                  "msdp_peer_address",
                                  "msdp_local_address",
                                  "as_number",
                                  "pim_other_rp_address",
                                  "pim_self_rp_address",
                                  "pim_rp_address",
                                  "vpn_type"))

        return self.__exec_write_sql(select_query,
                                     insert_query,
                                     update_query,
                                     delete_query,
                                     upsert_param,
                                     where_param,
                                     db_control,
                                     conn)

    @decorater_log
    def read_device_regist_info(self, device_name):
        table_name = "DeviceRegistrationInfo"

        if not self.__check_parameter(device_name, str, not_null=True):
            return False, None

        where_query_str = ["WHERE device_name = %s"]
        q_str = self.__gen_select_sql(table_name, where_query_str)

        return self.__execute_read_sql((device_name,), q_str)

    @decorater_log
    def write_cp_info(self,
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
                      conn=None):
        table_name = "CpInfo"

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

        if not is_ok:
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
                                  "metric"))

        return self.__exec_write_sql(select_query,
                                     insert_query,
                                     update_query,
                                     delete_query,
                                     upsert_param,
                                     where_param,
                                     db_control,
                                     conn)

    @decorater_log
    def read_cp_info(self, device_name):
        table_name = "CpInfo"

        if not self.__check_parameter(device_name, str, not_null=True):
            return False, None

        where_query_str = ["WHERE device_name = %s"]
        q_str = self.__gen_select_sql(table_name, where_query_str)

        return self.__execute_read_sql((device_name,), q_str)

    @decorater_log
    def write_lagif_info(self,
                         db_control,
                         device_name,
                         lag_if_name,
                         lag_type=None,
                         minimum_links=None,
                         link_speed=None,
                         internal_link_ip_address=None,
                         internal_link_ip_prefix=None,
                         conn=None):
        table_name = "LagIfInfo"

        is_not_null = True
        if db_control == self.__delete_flg and lag_if_name is None:
            is_not_null = False

        is_ok = self.__check_parameter(device_name, str, not_null=True)
        is_ok = is_ok and self.__check_parameter(lag_if_name,
                                                 str, not_null=is_not_null)
        if db_control != self.__delete_flg:
            is_ok = is_ok and self.__check_parameter(
                lag_type, int, not_null=True)
            is_ok = (is_ok and
                     self.__check_parameter(minimum_links, int, not_null=True))
            is_ok = is_ok and self.__check_parameter(link_speed, str)
            is_ok = is_ok and self.__check_parameter(
                internal_link_ip_address, str)
            is_ok = is_ok and self.__check_parameter(
                internal_link_ip_prefix, str)

        if not is_ok:
            return False

        tmp_list = []
        tmp_list.append(device_name)
        if is_not_null:
            tmp_list.append(lag_if_name)
        where_param = tuple(tmp_list)

        tmp_list.append(lag_type)
        tmp_list.append(minimum_links)
        tmp_list.append(link_speed)
        tmp_list.append(internal_link_ip_address)
        tmp_list.append(internal_link_ip_prefix)
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
                                  "minimum_links",
                                  "link_speed",
                                  "internal_link_ip_address",
                                  "internal_link_ip_prefix"))

        return self.__exec_write_sql(select_query,
                                     insert_query,
                                     update_query,
                                     delete_query,
                                     upsert_param,
                                     where_param,
                                     db_control,
                                     conn)

    @decorater_log
    def read_lagif_info(self, device_name):
        table_name = "LagIfInfo"

        if not self.__check_parameter(device_name, str, not_null=True):
            return False, None

        where_query_str = ["WHERE device_name = %s"]
        q_str = self.__gen_select_sql(table_name, where_query_str)

        return self.__execute_read_sql((device_name,), q_str)

    @decorater_log
    def write_lagmemberif_info(self,
                               db_control,
                               lag_if_name,
                               if_name,
                               device_name,
                               conn=None):
        table_name = "LagMemberIfInfo"

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

    @decorater_log
    def read_lagmemberif_info(self, device_name):
        table_name = "LagMemberIfInfo"

        if not self.__check_parameter(device_name, str, not_null=True):
            return False, None

        where_query_str = ["WHERE device_name = %s"]
        q_str = self.__gen_select_sql(table_name, where_query_str)

        return self.__execute_read_sql((device_name,), q_str)

    @decorater_log
    def write_l3vpn_leaf_bgp_basic_info(self,
                                        db_control,
                                        device_name,
                                        neighbor_ipv4,
                                        bgp_community_value,
                                        bgp_community_wildcard,
                                        conn=None):
        table_name = "L3VpnLeafBgpBasicInfo"

        is_not_null = True
        if db_control == self.__delete_flg and neighbor_ipv4 is None:
            is_not_null = False

        is_ok = self.__check_parameter(device_name, str, not_null=True)
        is_ok = is_ok and self.__check_parameter(neighbor_ipv4,
                                                 str, not_null=is_not_null)
        if db_control != self.__delete_flg:
            is_ok = is_ok and self.__check_parameter(
                bgp_community_value, str, not_null=True)
            is_ok = is_ok and self.__check_parameter(
                bgp_community_wildcard, str, not_null=True)

        if not is_ok:
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

    @decorater_log
    def read_l3vpn_leaf_bgp_basic_info(self, device_name):
        table_name = "L3VpnLeafBgpBasicInfo"

        if not self.__check_parameter(device_name, str, not_null=True):
            return False, None

        where_query_str = ["WHERE device_name = %s"]
        q_str = self.__gen_select_sql(table_name, where_query_str)

        return self.__execute_read_sql((device_name,), q_str)

    @decorater_log
    def write_vrf_detail_info(self,
                              db_control,
                              device_name,
                              if_name,
                              vlan_id,
                              slice_name,
                              vrf_name=None,
                              rt=None,
                              rd=None,
                              router_id=None,
                              conn=None):
        table_name = "VrfDetailInfo"

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
            is_ok = is_ok and self.__check_parameter(rt, str, not_null=True)
            is_ok = is_ok and self.__check_parameter(rd, str, not_null=True)
            is_ok = is_ok and self.__check_parameter(
                router_id, str, not_null=True)

        if not is_ok:
            return False

        tmp_list = []
        tmp_list.append(device_name)
        if is_not_null:
            tmp_list.append(if_name)
            tmp_list.append(vlan_id)
        tmp_list.append(slice_name)
        where_param = tuple(tmp_list)

        tmp_list.append(vrf_name)
        tmp_list.append(rt)
        tmp_list.append(rd)
        tmp_list.append(router_id)
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
                                  "rt",
                                  "rd",
                                  "router_id"))

        return self.__exec_write_sql(select_query,
                                     insert_query,
                                     update_query,
                                     delete_query,
                                     upsert_param,
                                     where_param,
                                     db_control,
                                     conn)

    @decorater_log
    def read_vrf_detail_info(self, device_name):
        table_name = "VrfDetailInfo"

        if not self.__check_parameter(device_name, str, not_null=True):
            return False, None

        where_query_str = ["WHERE device_name = %s"]
        q_str = self.__gen_select_sql(table_name, where_query_str)

        return self.__execute_read_sql((device_name,), q_str)

    @decorater_log
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
        table_name = "VrrpDetailInfo"

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

    @decorater_log
    def read_vrrp_detail_info(self, device_name):
        table_name = "VrrpDetailInfo"

        if not self.__check_parameter(device_name, str, not_null=True):
            return False, None

        where_query_str = ["WHERE device_name = %s"]
        q_str = self.__gen_select_sql(table_name, where_query_str)

        return self.__execute_read_sql((device_name,), q_str)

    @decorater_log
    def write_vrrp_trackif_info(self,
                                db_control,
                                vrrp_group_id,
                                track_if_name,
                                conn=None):
        table_name = "VrrpTrackIfInfo"

        is_not_null = True
        if db_control == self.__delete_flg and track_if_name is None:
            is_not_null = False

        is_ok = self.__check_parameter(vrrp_group_id, int, not_null=True)
        is_ok = is_ok and self.__check_parameter(track_if_name,
                                                 str,
                                                 not_null=is_not_null)

        if not is_ok:
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

    @decorater_log
    def read_vrrp_trackif_info(self, device_name):

        if not self.__check_parameter(device_name, str, not_null=True):
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

        return self.__execute_read_sql((device_name,), q_str)

    @decorater_log
    def write_bgp_detail_info(self,
                              db_control,
                              device_name,
                              if_name,
                              vlan_id,
                              slice_name,
                              remote_as_number=None,
                              local_ipv4_address=None,
                              remote_ipv4_address=None,
                              local_ipv6_address=None,
                              remote_ipv6_address=None,
                              conn=None):
        table_name = "BgpDetailInfo"

        is_ok = self.__check_parameter(device_name, str, not_null=True)
        is_ok = is_ok and self.__check_parameter(if_name, str, not_null=True)
        is_ok = is_ok and self.__check_parameter(vlan_id, int, not_null=True)
        is_ok = is_ok and self.__check_parameter(
            slice_name, str, not_null=True)
        if db_control != self.__delete_flg:
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
            return False

        tmp_list = []
        tmp_list.append(device_name)
        tmp_list.append(if_name)
        tmp_list.append(vlan_id)
        tmp_list.append(slice_name)
        where_param = tuple(tmp_list)

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

    @decorater_log
    def read_bgp_detail_info(self, device_name):
        table_name = "BgpDetailInfo"

        if not self.__check_parameter(device_name, str, not_null=True):
            return False, None

        where_query_str = ["WHERE device_name = %s"]
        q_str = self.__gen_select_sql(table_name, where_query_str)

        return self.__execute_read_sql((device_name,), q_str)

    @decorater_log
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
        table_name = "StaticRouteDetailInfo"

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

    @decorater_log
    def read_static_route_detail_info(self, device_name):
        table_name = "StaticRouteDetailInfo"

        if not self.__check_parameter(device_name, str, not_null=True):
            return False, None

        where_query_str = ["WHERE device_name = %s"]
        q_str = self.__gen_select_sql(table_name, where_query_str)

        return self.__execute_read_sql((device_name,), q_str)

    @decorater_log
    def write_simultaneous_table(self, functions, params):

        func_dict = {
            self.write_lagmemberif_info.__name__: self.write_lagmemberif_info,
            self.write_l3vpn_leaf_bgp_basic_info.__name__:
                self.write_l3vpn_leaf_bgp_basic_info,
            self.write_cp_info.__name__: self.write_cp_info,
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
                self.delete_device_status_mgmt_info_linked_tr_id
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
            if db_trans:
                db_trans.rollback()
            GlobalModule.EM_LOGGER.error(
            GlobalModule.EM_LOGGER.debug(
            is_insert = False
        finally:
            self.__close_db(con)
        return is_insert
