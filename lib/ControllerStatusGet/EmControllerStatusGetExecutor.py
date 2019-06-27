#! /usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmControllerStatusGetExecutor.py


import GlobalModule
import requests
import json

from EmCommonLog import decorater_log, decorater_log_in_out



ctl_type_act = "em"
ctl_type_sby = "em_sby"
sys_type_os = "operating_system"
sys_type_ctl = "ctl_process"


class EmControllerStatusGetExecutor(object):
    '''
    Periordic notification of controller status is executed.
    '''

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''
        self.conf_thresholds = {
            ctl_type_act: ConfActThreshold(),
            ctl_type_sby: ConfSbyThreshold(),
        }
        self.url_format = "http://{address}:{port}/{api_url}"
        self.address = self._get_conf("Ec_rest_server_address")
        self.port = self._get_conf("Ec_port_number")
        self.api_url = "v1/internal/ec_ctrl/serverstatusnotify"

    @decorater_log_in_out
    def execute(self):
        '''
        Contoller status is confirmed and notified.
        '''
        try:
            GlobalModule.EM_LOGGER.info(
                "101013 Start Periodic execution " +
                "for Em Controller status get.")
            status_data = self.controller_status_get()
            notify_list = self.compare_value(status_data)
            if notify_list:
                self.contoroller_notify(notify_list)
        except Exception:
            GlobalModule.EM_LOGGER.warning(
                "201012 Failed to Periodic execution " +
                "for Em Controller status get.")
            raise
        else:
            GlobalModule.EM_LOGGER.info(
                "101014 Complete toPeriodic execution " +
                "for Em Controller status get.")

    @decorater_log_in_out
    def controller_status_get(self):
        '''
        Controller status is acquired.
        '''
        sby_info = bool(
            self._get_conf("Em_standby_server_address"))
        param_controller = ctl_type_act
        if sby_info:
            param_controller = "+".join((param_controller, ctl_type_sby))

        param_get_info = "+".join(("os-cpu",
                                   "os-mem",
                                   "os-disk",
                                   "ctr-cpu",
                                   "ctr-mem", ))
        from EmControllerStatusGet import EmControllerStatusGet
        status_get = EmControllerStatusGet()
        status_data = status_get.get_status(get_info=param_get_info,
                                            controller=param_controller)
        GlobalModule.EM_LOGGER.debug("status:%s", status_data)
        return status_data

    @decorater_log_in_out
    def compare_value(self, status_data={}):
        '''
        Controller status is compared.
        Argument:
            status_data : acquired controller status
        Return value:
            information list of necessary notification : list of CheckStatusBase instance
        '''
        notify_list = []
        for status_info in status_data.get("informations", ()):

            ctl_type = status_info.get("controller_type")
            conf_thr = self.conf_thresholds[ctl_type]

            tmp = self._check_status(status_info,
                                     conf_thr,
                                     CheckStatusOS,
                                     ctl_type)
            notify_list.extend(tmp)
            if ctl_type == ctl_type_act:
                tmp = self._check_status(status_info,
                                         conf_thr,
                                         CheckStatusController,
                                         ctl_type)
                notify_list.extend(tmp)
        return notify_list

    @decorater_log_in_out
    def contoroller_notify(self, notify_list=[]):
        '''
        Request is sent to API of specified address.
        Argument:
            notify_list : notification information list (list)
        '''
        if self.address and self.port:
            for notify_obj in notify_list:
                self.send_notify_request(notify_obj)
        else:
            GlobalModule.EM_LOGGER.debug("not notify : No API address")

    @decorater_log_in_out
    def send_notify_request(self, notify_info):
        '''
        Request is sent to API of specified address.
        Argument:
            notify_info : CheckStatusBase object
        '''
        request_body = self._set_request_body(notify_info)
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

    @decorater_log_in_out
    def _set_request_body(self, notify_info):
        '''
        Body in request is generated.
        Argument:
            notify_info : CheckStatusBase object
        Return value:
            body part ; dict
        '''

        body_json = {}
        controller = {}
        controller["controller_type"] = notify_info.controller_type
        controller["system_type"] = notify_info.system_type
        failure_info = {}
        if notify_info.is_alert_cpu:
            failure_info["cpu"] = {
                "use_rate": float(notify_info.info_cpu["use_rate"]),
            }

        if notify_info.is_alert_memory:
            memory_info = {}
            memory_info["used"] = notify_info.info_memory["used"]
            if notify_info.info_memory.get("free"):
                memory_info["free"] = notify_info.info_memory["free"]
            failure_info["memory"] = memory_info
        if notify_info.is_alert_disk:
            devices = []
            for mnt, item in notify_info.dict_alert_disk.items():
                tmp = {
                    "file_system": item["file_system"],
                    "mounted_on": mnt,
                    "size": item["size"],
                    "used": item["used"],
                }
                devices.append(tmp)
            failure_info["disk"] = {"devices": devices}
        controller["failure_info"] = failure_info
        body_json["controller"] = controller
        return body_json

    @decorater_log
    def _check_status(self, status_info, conf_thr, check_class, ctl_type):
        '''
        Controller status is checked by class which specified the controller status.
        Argument:
            status_info : acquired controller status (dict)
            conf_thr : threshold definition (ConfThreshold object)
            check_class : check class (CheckStatusBase object)
            ctl_type : controller type (str)
        Return value:
            It is returned by CheckStatusBase object format in list, if notification is needed. 
        '''
        return_val = []
        check_obj = check_class(status_info, conf_thr)
        check_obj.controller_type = ctl_type
        if check_obj.is_alert:
            return_val.append(check_obj)
        return return_val

    @decorater_log
    def _get_conf(self, conf_name):
        '''
        Config definition is acquired from system common definition.
        Argument:
            conf_name : config key (str)
        Return value:
            config value (if config is not acquired, None is set.)
        '''
        is_ok, return_val = (
            GlobalModule.EM_CONFIG.read_sys_common_conf(conf_name))
        if not is_ok:
            return_val = None
        return return_val


class CheckStatusBase(object):

    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''
        self.controller_type = None
        self.system_type = None

        self.info_cpu = {}
        self.chk_cpu = None
        self.info_memory = {}
        self.chk_memory = None

        self.info_disk = {}
        self.chk_disk = {}
        self.threshold_cpu = None
        self.threshold_memory = None
        self.threshold_disk = {}

        self.is_alert_cpu = False
        self.is_alert_memory = False
        self.is_alert_disk = False
        self.dict_alert_disk = {}
        self.is_alert = False

    @decorater_log_in_out
    def check_status(self):
        '''
        Status is checked.
        '''

        GlobalModule.EM_LOGGER.debug(
            "Get Data = CPU:%s ,MEMORY:%s ,Disk:%s",
            self.chk_cpu, self.chk_memory, self.chk_disk)
        GlobalModule.EM_LOGGER.debug(
            "Threshold = CPU:%s ,MEMORY:%s ,Disk:%s",
            self.threshold_cpu, self.threshold_memory, self.threshold_disk)
        self.is_alert_cpu = self._compare_data(self.chk_cpu,
                                               self.threshold_cpu)
        self.is_alert_memory = self._compare_data(self.chk_memory,
                                                  self.threshold_memory)
        for mnt, threshold_val in self.threshold_disk.items():
            if (self.chk_disk.get(mnt) and
                    self._compare_data(self.chk_disk[mnt]["used"],
                                       threshold_val)):
                self.is_alert_disk = True
                self.dict_alert_disk[mnt] = self.chk_disk[mnt]
        self.is_alert = (self.is_alert_cpu or
                         self.is_alert_memory or
                         self.is_alert_disk)
        GlobalModule.EM_LOGGER.debug("alert is %s", self.is_alert)
        GlobalModule.EM_LOGGER.debug(
            "alert detail: CPU:%s ,MEMORY:%s ,DISK:%s",
            self.is_alert_cpu,
            self.is_alert_memory,
            self.dict_alert_disk.keys()
        )

    @decorater_log
    def _compare_data(self, status_val=None, thr_val=None):
        '''
        Data is compared.
        Argument:
            status_val : status value
            thr_val : thread value
        Return value:
            result : status_val > thr_val => True else False
        '''
        return status_val > thr_val


class CheckStatusOS(CheckStatusBase):
    '''
    Status of OS is checked.
    '''

    @decorater_log
    def __init__(self, status_info, conf_thr):
        '''
        Constructor
        Argument:
            status_info : acquired status information(one element in information) (dict)
            conf_thr : threshold definition (ConfThreshold class)
        '''
        super(CheckStatusOS, self).__init__()

 
        self.system_type = sys_type_os

        os_info = status_info["os"]

        self.info_cpu = os_info["cpu"]
        self.chk_cpu = self.info_cpu["use_rate"]

        self.info_memory = os_info["memory"]
        self.chk_memory = self.info_memory["used"]
        self.info_disk = os_info["disk"]
        self.chk_disk = self._get_mnt_dict(self.info_disk["devices"])


        self.threshold_cpu = conf_thr.os_cpu
        self.threshold_memory = conf_thr.os_memory

        self.threshold_disk = conf_thr.os_disk

        self.check_status()

    @decorater_log
    def _get_mnt_dict(self, disk_data):
        '''
        Disk information is converted to dictionary whose key is mount point.
        Argument:
            disk_data : disk information element in os/disk/devices (list)
        Return value:
            disk information for each mount point
        '''
        mnt_dict = {}
        for disk in disk_data:
            key = disk["mounted_on"]
            mnt_dict[key] = disk
        return mnt_dict


class CheckStatusController(CheckStatusBase):
    '''
    Status of controller is checked.
    '''

    @decorater_log
    def __init__(self, status_info, conf_thr):
        '''
        Constructor
        Argument:
            status_info : acquired status infomation( one element in information) (dict)
            conf_thr : threshold definition (ConfThreshold class)
        '''
        super(CheckStatusController, self).__init__()

        self.system_type = sys_type_ctl

        ctl_info = status_info["controller"]

        tmp_cpu = {
            "use_rate": ctl_info["cpu"],
        }
        self.info_cpu = tmp_cpu
        self.chk_cpu = ctl_info["cpu"]
        tmp_memory = {
            "used": ctl_info["memory"],
            "free": None,
        }
        self.info_memory = tmp_memory
        self.chk_memory = ctl_info["memory"]

        self.threshold_cpu = conf_thr.ctl_cpu
        self.threshold_memory = conf_thr.ctl_memory

        self.check_status()


class ConfThreshold(object):
    '''
    Threshold for status monitoring is defined.
    '''

    @decorater_log
    def __init__(self, ctl_type=None, conf_method=None):
        '''
        Constructor
        Argument:
            ctl_type : controller type (str)
            conf_method : method for acquiring config (method in config management part)
        '''
        self.ctl_type = ctl_type
        self.conf_method = conf_method
        self.os_cpu = None
        self.os_memory = None
        self.os_disk = None
        self.ctl_cpu = None
        self.ctl_memory = None

    @decorater_log
    def load_config(self):
        '''
        Necessary config is acquired from ACT threshold definition.
        Argument:
            None
        Return value:
            None
        '''
        self.os_cpu = self._get_conf("Em_os_cpu_use_rate_threshold",
                                     self.conf_method)
        self.os_memory = self._get_conf("Em_os_memory_usage_threshold",
                                        self.conf_method)
        self.os_disk = self._get_conf("Em_os_disk_usage_threshold_mountpoint",
                                      self.conf_method)
        self.ctl_cpu = self._get_conf(
            "Em_controller_cpu_use_rate_threshold",
            self.conf_method)
        self.ctl_memory = self._get_conf(
            "Em_controller_memory_usage_threshold",
            self.conf_method)

    @decorater_log
    def _get_conf(self, key=None, conf=None):
        '''
        Necessary Config is acquired from config managemet part.
        Argument:
            key ; key (str)
            conf ; config definition (read method in config management part)
        Return value:
            acquired config definition : depending on config definition type
        '''
        normal_key = ("Em_os_cpu_use_rate_threshold",
                      "Em_os_memory_usage_threshold",
                      "Em_controller_cpu_use_rate_threshold",
                      "Em_controller_memory_usage_threshold")

        thr_conf = conf()
        if key in normal_key:
            return_val = int(thr_conf[key]) if thr_conf.get(key) else None
        else:
            return_val = {}
            for conf_key, conf_val in thr_conf.items():
                if conf_key not in normal_key:
                    return_val[conf_key] = int(conf_val)
        return return_val


class ConfActThreshold(ConfThreshold):
    '''
    Threshold for ACT is defined.
    '''

    @decorater_log
    def __init__(self):
        super(ConfActThreshold, self).__init__()
        self.ctl_type = ctl_type_act
        self.conf_method = GlobalModule.EM_CONFIG.read_act_threshold_conf
        self.load_config()


class ConfSbyThreshold(ConfThreshold):
    '''
    Threshold for SBY is defined.
    '''

    @decorater_log
    def __init__(self):
        super(ConfSbyThreshold, self).__init__()
        self.ctl_type = ctl_type_sby
        self.conf_method = GlobalModule.EM_CONFIG.read_standby_threshold_conf
        self.load_config()
