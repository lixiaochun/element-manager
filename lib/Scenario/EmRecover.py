#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmRecover.py
'''
Base scenario for recover
'''

import json
from lxml import etree
from EmMergeScenario import EmMergeScenario
import GlobalModule
from EmCommonLog import decorater_log


class EmRecover(EmMergeScenario):

    '''
    Base scenario class for recover
    '''


    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmRecover, self).__init__()

        self.device_type = "device"

    @decorater_log
    def _process_scenario(self,
                          device_message=None,
                          transaction_id=None,
                          order_type=None,
                          condition=None,
                          device_name=None,
                          force=False):
        '''
        Executes scenario processing for each device.
        Explanation about parameter :
            device_message: Message for each device (byte)
            transaction_id: Transaction ID (uuid)
            order_type: Order type(int)
            condition: Thread control information (condition object)
            device_name: Device name (str)
            force: Forced deletion flag (boolean)
        Explanation about return value :
            None 
        '''

        order_type = GlobalModule.ORDER_MERGE
        super(EmRecover, self)._process_scenario(
            device_message=device_message,
            transaction_id=transaction_id,
            order_type=order_type,
            condition=condition,
            device_name=device_name,
            force=force)

    @decorater_log
    def _start_common_driver(self,
                             device_name=None,
                             order_type=None,
                             transaction_id=None,
                             json_message=None):
        '''
        Starts driver's common part.
        Explanation about parameter :
            device_name: Device name (str)
            order_type:  Order type (str)
            transaction_id:Transaction ID (uuid)
            json_message: EC esage with json type (str)
        Explanation about return value :
            None
        '''
        com_driver = self.com_driver_list[device_name]
        is_comdriver_result = com_driver.start("", json_message)

        self._check_start_common_driver(device_name,
                                        order_type,
                                        transaction_id,
                                        is_comdriver_result)

    @decorater_log
    def _connect_device(self,
                        device_name=None,
                        order_type=None,
                        transaction_id=None,
                        json_message=None):
        '''
        Executes the connection with device.
        Explanation about parameter :
            device_name: Device name (str)
            order_type:  Order type (str)
            transaction_id:Transaction ID (uuid)
            json_message: EC esage with json type (str)
        Explanation about return value :
            None
        '''
        com_driver = self.com_driver_list[device_name]
        is_ok = com_driver.connect_device("",
                                          self.service,
                                          order_type,
                                          json_message)
        if is_ok == GlobalModule.COM_CONNECT_OK:
            GlobalModule.EM_LOGGER.debug("connect_device OK")
        else:
            if is_ok == GlobalModule.COM_CONNECT_NG:
                GlobalModule.EM_LOGGER.debug("connect_device connect NG")
            else:
                GlobalModule.EM_LOGGER.debug("connect_device no response NG")
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:12" +
                "(Processing failure (Stored information None))",
                self.error_code02, self._scenario_name, device_name)
            self._find_subnormal(transaction_id, order_type, device_name,
                                 GlobalModule.TRA_STAT_PROC_ERR_INF,
                                 False, False)
            raise Exception("connect_device NG")

    @decorater_log
    def _get_dev_regist_info(self, device_name):
        '''
        Gets device information to be registered.
        Explanation about parameter :
            device_name: Device name (str)
        Explanation about return value :
            device information to be registered corresponding to device name : dict

        '''
        GlobalModule.EM_LOGGER.debug("Start Getting Registered info")
        read_method = GlobalModule.EMSYSCOMUTILDB.read_device_registered_info
        result_info, table_info = read_method(device_name)
        if (not result_info or not table_info):
            if not result_info:
                GlobalModule.EM_LOGGER.debug("read_device_registered_info NG")
            else:
                GlobalModule.EM_LOGGER.debug(
                    " read_device_registered_info data not found NG")
            GlobalModule.EM_LOGGER.warning(
                "%s Scenario:%s Device:%s NG:13" +
                "(Processing failure (temporary))",
                self.error_code02, self._scenario_name, device_name)
            GlobalModule.EM_LOGGER.info(
                "%s Scenario:%s Device:%s end",
                self.error_code03, self._scenario_name, device_name)
            raise Exception("Failed to get device regist info.")
        table_info_dict = table_info[0]
        GlobalModule.EM_LOGGER.debug("End Getting Registered info / %s",
                                     table_info_dict)
        return table_info_dict

    @decorater_log
    def _creating_json(self, device_message):
        '''
        Merge  EC message(XML) devided for each device and device registration information from DB
        and Convert them to JSON. 
        Explanation about parameter :
            device_message: message for each device
            table_info_dict: device registration information from DB
        Explanation about return value :
            device_json_message: JSON mesage
        '''
        device_json_message = \
            {
                "device":
                {
                    "name": None,
                    "node-type": None,
                    "equipment":
                    {
                        "platform": None,
                        "os": None,
                        "firmware": None,
                        "loginid": None,
                        "password": None
                    },
                    "management-interface":
                    {
                        "address": None,
                        "prefix": 0
                    },
                    "physical-ifs_value": 0,
                    "physical-ifs": [],
                    "lag-ifs_value": 0,
                    "lag-ifs": []
                }
            }

        xml_elm = etree.fromstring(device_message)

        GlobalModule.EM_LOGGER.debug(
            "device_message = %s", etree.tostring(xml_elm, pretty_print=True))

        device_name = self._find_xml_node(xml_elm, self._xml_ns + "name").text
        table_info_dict = self._get_dev_regist_info(device_name)

        self._gen_json_name(
            device_json_message, xml_elm, self._xml_ns)

        self._gen_json_node_type(
            device_json_message, xml_elm, self._xml_ns)

        self._gen_json_equipment(
            device_json_message, xml_elm, self._xml_ns)

        self._gen_json_management(
            device_json_message, xml_elm, self._xml_ns,
            table_info_dict)

        self._gen_json_if_convert_table(
            device_json_message, xml_elm, self._xml_ns, "physical-ifs")

        self._gen_json_if_convert_table(
            device_json_message, xml_elm, self._xml_ns, "lag-ifs")

        GlobalModule.EM_LOGGER.debug(
            "device__json_message = %s", device_json_message)

        return json.dumps(device_json_message)

    @decorater_log
    def _gen_json_name(self, json, xml, xml_ns):
        '''
            Obtain name information from xml message to be analyzed and
            set it for EC message storage dictionary object.
            Explanation about paramete：
                json：Dictionary object for EC message storage
                xml：Xml message to be analyzed
                xml_ns：Name space
        '''

        name_elm = self._find_xml_node(xml, xml_ns + "name")
        json["device"]["name"] = name_elm.text

    @decorater_log
    def _gen_json_node_type(self, json, xml, xml_ns):
        '''
            Obtain device type information from xml message to be analyzed and
            set it for EC message storage dictionary object.
            Explanation about paramete：
                json：Dictionary object for EC message storage
                xml：Xml message to be analyzed
                xml_ns：Name space
        '''

        name_elm = self._find_xml_node(xml, xml_ns + "node-type")
        json["device"]["node-type"] = name_elm.text

    @decorater_log
    def _gen_json_equipment(self, json, xml, xml_ns):
        '''
            Obtain device connection information from xml message to be analyzed and
            set it for EC message storage dictionary object.
            Explanation about paramete：
                json：Dictionary object for EC message storage
                xml：Xml message to be analyzed
                xml_ns：Name space
        '''

        equ_elm = self._find_xml_node(xml, xml_ns + "equipment")
        equ_json = json["device"]["equipment"]
        equ_json["platform"] = \
            equ_elm.find(xml_ns + "platform").text
        equ_json["os"] = \
            equ_elm.find(xml_ns + "os").text
        equ_json["firmware"] = \
            equ_elm.find(xml_ns + "firmware").text
        equ_json["loginid"] = \
            equ_elm.find(xml_ns + "loginid").text
        equ_json["password"] = \
            equ_elm.find(xml_ns + "password").text

    @decorater_log
    def _gen_json_management(self, json, xml, xml_ns, db_info):
        '''
            Obtain management IF information from xml message to be analyzed and
            set it for EC message storage dictionary object.
            Explanation about paramete：
                json：Dictionary object for EC message storage
                xml：Xml message to be analyzed
                xml_ns：Name space
                db_info：DB information
        '''
        man_json = json["device"]["management-interface"]
        man_json["address"] = db_info.get("mgmt_if_address")
        man_json["prefix"] = db_info.get("mgmt_if_prefix")

    @decorater_log
    def _gen_json_if_convert_table(self,
                                   json,
                                   xml,
                                   xml_ns,
                                   convert_table_name):
        '''
            Obtain Conversion table (PhyicalIF/LAGIF) from xml message to be analyzed and
            set it for EC message storage dictionary object.
            Explanation about paramete：
                json：Dictionary object for EC message storage
                xml：Xml message to be analyzed
                xml_ns：Name space
                convert_table_name：Conversion table name
        '''
        if_convert_elm = self._find_xml_node(xml,
                                             xml_ns + convert_table_name)

        if if_convert_elm is not None:
            if_convert_tag = xml_ns + convert_table_name
            for if_convert in xml.findall(".//" + if_convert_tag):
                name = if_convert.find(xml_ns + "name").text
                old_name = if_convert.find(xml_ns + "old-name").text
                json["device"][convert_table_name].append(
                    {"name": name,
                     "old-name": old_name})
        json["device"][convert_table_name + "_value"] = \
            len(json["device"][convert_table_name])
