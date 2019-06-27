#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmControllerLogGet.py
'''
Controller log acquisition scenario.
'''
import re
import os
import glob
import socket
import traceback
from datetime import datetime, timedelta
from flask import jsonify
import linecache
import EmSeparateRestScenario
import GlobalModule
from EmCommonLog import decorater_log


class EmControllerLogGet(EmSeparateRestScenario.EmRestScenario):
    '''
    Controller log acquisition class
    '''

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''

        super(EmControllerLogGet, self).__init__()
        self.scenario_name = "EmControllerLogGet"
        self.error_code_top = "02"
        self._error_code_list = {"020101": 400,
                                 "020201": 409,
                                 "020303": 500,
                                 "020304": 500,
                                 "020305": 500,
                                 "020399": 500, }
        self._em_lib_path = GlobalModule.EM_LIB_PATH
        log_format = ("^\[([0-9]{4}/[0-9]{2}/[0-9]{2}) " +
                      "[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3}\]")
        self._log_re = re.compile(log_format)
        self._log_date_format = "%Y/%m/%d"
        self._file_format_re = re.compile("([0-9]{4}-[0-9]{2}-[0-9]{2})")
        self._file_format = "%Y-%m-%d"
        self._log_count = 0
        self._log_data = []

    @decorater_log
    def _get_url_param(self, request):
        '''
        Obtain URL parameter.
        '''
        date_format = "%Y%m%d"
        if not request:
            raise ValueError("Request object is NULL")
        start_date = self._get_url_parameter(request, "start_date", str, True)
        if not start_date:
            start_date = datetime.today().strftime(date_format)
        end_date = self._get_url_parameter(request, "end_date", str, True)
        if not end_date:
            end_date = datetime.today().strftime(date_format)
        limit_number = self._get_url_parameter(request,
                                               "limit_number",
                                               int,
                                               False)

        self.url_parameter = {"start_date": start_date,
                              "end_date": end_date,
                              "limit_number": limit_number, }
        try:
            start_date = datetime.strptime(start_date, date_format)
            end_date = datetime.strptime(end_date, date_format)
        except ValueError as ex:
            raise ValueError(self._error_text % ("020101", ex.message))
        tmp_url_parameter = {"start_date": start_date,
                             "end_date": end_date,
                             "limit_number": limit_number, }
        self.start_date = start_date
        self.end_date = end_date
        self.limit_number = limit_number
        return tmp_url_parameter

    @decorater_log
    def _scenario_main(self, *args, **kwargs):
        '''
        Scenario processing section.
        Obtain log data.
        '''
        GlobalModule.EM_LOGGER.debug(
            "start get log: args=%s ,kwargs=%s" % (args, kwargs))
        start_date = self.start_date
        end_date = self.end_date
        limit_number = self.limit_number
        try:
            log_data, is_over_limit = self._get_log_data(start_date,
                                                         end_date,
                                                         limit_number)
            response = self._gen_response(log_data, is_over_limit)
        except IOError as ex:
            GlobalModule.EM_LOGGER.debug(
                "Trace Back:%s" % (traceback.format_exc(),))
            raise IOError(
                (self._error_text % ("020305", ex.message)))
        except Exception as ex:
            GlobalModule.EM_LOGGER.debug(
                "Trace Back:%s" % (traceback.format_exc(),))
            raise
        return response

    @decorater_log
    def _gen_response(self, log_data, is_over_limit):
        '''
        Create response.
        '''

        tmp_json = self._gen_response_json(
            log_data, self.url_parameter, is_over_limit)
        response = jsonify(tmp_json)
        response.headers["Content-Type"] = "application/json"
        response.status_code = 200
        return response

    @staticmethod
    @decorater_log
    def _gen_response_json(log_data, url_parameter, is_over_limit):
        '''
        Create Json for response.
        '''
        conditions = {}
        conditions.update(url_parameter)

        em_log = {}
        log_count = len(log_data)
        em_log["data_number"] = log_count
        em_log["over_limit_number"] = is_over_limit
        em_log["server_name"] = socket.gethostname()
        GlobalModule.EM_LOGGER.debug(
            "Make Response Json without log_data:%s" % (
                {"conditions": conditions, "em_log": em_log},
            )
        )

        log_data_list = []
        for item in log_data:
            message = {}
            message["message"] = ''.join(item)
            log_data_list.append(message)
        em_log["log_data"] = log_data_list

        res_json = {}
        res_json["conditions"] = conditions
        res_json["em_log"] = em_log
        return res_json

    @decorater_log
    def _get_log_data(self,
                      start_date,
                      end_date,
                      limit_number):
        '''
        Obtain log data.
        Explanation about parameter:
            start_date:Reading target period (start date)
            end_date:Reading target period (end date)
            limit_number:Maximum number of read lines
        Explanation about return value:
            get_log_data:Acquisition log data
            is_over_limit:Exceeding limit flag
        '''
        GlobalModule.EM_LOGGER.debug(
            "Target Date : Start = %s, End = %s" % (start_date, end_date))
        isout, log_file_name = (
            GlobalModule.EM_CONFIG.read_sys_common_conf("Em_info_log_file_path"))
        if not isout:
            raise IOError(
                (self._error_text % ("020305", "Cannot read Config")))
        GlobalModule.EM_LOGGER.debug(self._em_lib_path)
        log_file_name = os.path.join(self._em_lib_path, log_file_name)
        GlobalModule.EM_LOGGER.debug(
            "Target Log File Name = %s" % (log_file_name,))
        get_log_data, is_over_limit = self._get_log_data_from_files(
            log_file_name, start_date, end_date, limit_number)
        return get_log_data, is_over_limit

    @decorater_log
    def _get_log_data_from_files(self,
                                 log_file_name,
                                 start_date,
                                 end_date,
                                 limit_number):
        '''
        Read log files (all files which have been rotated)
        based on file name and obtain log.
        Explanation about parameter:
            log_file_name:Log File Name
            start_date:Reading target period (start date)
            end_date:Reading target period (end date)
            limit_number:Maximum number of read lines
        Explanation about return value:
            get_log_data:Acquisition log data
            is_over_limit:Exceeding limit flag
        '''

        is_over_limit = False

        pa_log_file_name = log_file_name
        get_log_data = []
        log_files_list = glob.glob(log_file_name + "*")
        sorted(log_files_list,
               key=self._sorted_key_file_date,
               reverse=True)
        GlobalModule.EM_LOGGER.debug(
            "Target Log File List = %s" % (log_files_list,))
        if len(log_files_list) == 0:
            GlobalModule.EM_LOGGER.warning(
                "210007 Not Found Required Log Error: %s", log_file_name)

        target_file_dict = {}
        for log_file_name in log_files_list:
            match_obj = self._file_format_re.search(log_file_name)
            if not match_obj:
                continue
            file_date = datetime.strptime(
                match_obj.groups()[0], self._file_format)
            target_file_dict[file_date] = log_file_name

        today = datetime.today()
        today = today.replace(hour=0)
        today = today.replace(minute=0)
        today = today.replace(second=0)
        today = today.replace(microsecond=0)
        target_file_dict[today] = pa_log_file_name
        GlobalModule.EM_LOGGER.debug(
            "target_file_dict = %s" % (target_file_dict,))

        tmp_start_date = start_date
        tmp_end_date = end_date

        target_date_list = []
        tmp_start_date -= timedelta(1)
        tmp_end_date += timedelta(1)
        while True:
            if tmp_start_date < tmp_end_date:
                target_date_list.append(tmp_end_date)
            elif tmp_start_date == tmp_end_date:
                target_date_list.append(tmp_end_date)
                break
            else:
                break
            tmp_end_date -= timedelta(1)
        GlobalModule.EM_LOGGER.debug(
            "target_date_list = %s" % (target_date_list,))

        log_cnt = 0
        for target_date in target_date_list:
            GlobalModule.EM_LOGGER.debug("Check date : %s" % (target_date,))

            if target_date in target_file_dict:
                target_file = target_file_dict[target_date]
                GlobalModule.EM_LOGGER.debug(
                    "target_file : %s" % (target_file,))

                tmp_log_date = self._get_log_data_from_one_log_file(
                    target_file, limit_number, start_date, end_date)

                log_cnt += len(tmp_log_date)
                get_log_data.extend(tmp_log_date)

                if log_cnt >= limit_number:
                    del get_log_data[limit_number:]
                    is_over_limit = True
                    GlobalModule.EM_LOGGER.debug("Over Limit!")
                    break

        get_log_data.sort(reverse=True)
        return get_log_data, is_over_limit

    @decorater_log
    def _sorted_key_file_date(self, f_name1):
        '''
        Method as the key for sorted method.
        (change the file name to the "Order of the date.")
        '''
        match_obj = self._file_format_re.search(f_name1)
        if not match_obj:
            return datetime.max
        else:
            return datetime.strptime(match_obj.groups()[0],
                                     self._file_format)

    @decorater_log
    def _get_log_data_from_one_log_file(self,
                                        file_name,
                                        limit_number,
                                        start_date=None,
                                        end_date=None):
        '''
        Open the files under applicable file names, obtain log.
        Explanation about parameter:
            file_name:Log File Name
            limit_number:Maximum number of read lines
            start_date:Reading target period (start date)
            end_date:Reading target period (end date)
        Explanation about return value:
            Acquisition log data
        '''
        GlobalModule.EM_LOGGER.debug("Get Log Date in %s" % (file_name, ))
        with open(file_name, "r") as log_file:

            line_num = sum(1 for line in log_file)
            linecache.clearcache()
            tmp_log = []
            get_log_data = []
            counter = 0
            while True:
                line = linecache.getline(file_name, int(line_num))
                counter += 1
                match_obj = self._log_re.search(line)

                tmp_log.append(line.rstrip("\n"))
                if match_obj:

                    log_date = datetime.strptime(match_obj.groups()[0],
                                                 self._log_date_format)
                    if start_date is not None and log_date < start_date:
                        break
                    if end_date is None or log_date <= end_date:
                        if len(tmp_log) > 1:
                            tmp_log.reverse()
                            result = '\n'.join(tmp_log)
                            get_log_data.append(result)
                        elif len(tmp_log) != 0:
                            get_log_data.append("".join(tmp_log))

                    tmp_log = []

                    if len(get_log_data) >= limit_number + 1:
                        break

                if line_num > 1:
                    line_num -= 1
                else:
                    break

        GlobalModule.EM_LOGGER.debug(
            "%s Date log num is %s" % (file_name, len(get_log_data)))
        return get_log_data
