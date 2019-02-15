#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2018 Nippon Telegraph and Telephone Corporation
# Filename: EmNetconfClient.py
'''
ncclient
'''
import sys
import os
import traceback
import logging
import datetime
import ConfigParser
from ConfigParser import NoOptionError

from ncclient import manager
from ncclient.manager import Manager
from ncclient.transport import session
from ncclient import transport
from ncclient import operations
from ncclient.devices import default as defaultDeviceHandler
from ncclient.capabilities import Capabilities
import paramiko
from threading import Thread, Lock, Event
try:
    from Queue import Queue
except ImportError:
    from queue import Queue
if sys.version < '3':
    from six import StringIO
else:
    from io import BytesIO as StringIO

import GlobalModule

VENDOR_OPERATIONS = {}


class EmNetconfClientSession(session.Session):

    def __init__(self, capabilities, device_info):
        Thread.__init__(self)
        self.setDaemon(True)
        self._listeners = set()
        self._lock = Lock()
        self.setName('session')
        self._q = Queue()
        self._client_capabilities = capabilities
        self._server_capabilities = None
        self._id = None
        self._connected = False
        self._device_handler = None
        self._device_info = device_info

    def send(self, message):
        """Send the supplied *message* (xml string) to NETCONF server."""
        if not self.connected:
            raise transport.TransportError('Not connected to NETCONF server')
        do_not_use_nc = (
            GlobalModule.EM_CONFIG.
            read_conf_internal_link_vlan_os_tuple())
        if self._device_info.get("os_name") in do_not_use_nc:
            import BeluganosDriver
            message = message.replace("nc:", "")
            message = message.replace(":nc", "")
            for key, value in BeluganosDriver.ncclient_update.iteritems():
                message = message.replace(key, value)

        self._q.put(message)


class EmNetconfClientSSHSession(EmNetconfClientSession, transport.SSHSession):

    "Implements a :rfc:`4742` NETCONF session over SSH."

    def __init__(self, device_handler, device_info):
        capabilities = Capabilities(device_handler.get_capabilities())
        EmNetconfClientSession.__init__(self, capabilities, device_info)
        self._host_keys = paramiko.HostKeys()
        self._transport = None
        self._connected = False
        self._channel = None
        self._channel_id = None
        self._channel_name = None
        self._buffer = StringIO()
        self._device_handler = device_handler
        self._parsing_state10 = 0
        self._parsing_pos10 = 0
        self._parsing_pos11 = 0
        self._parsing_state11 = 0
        self._expchunksize = 0
        self._curchunksize = 0
        self._inendpos = 0
        self._size_num_list = []
        self._message_list = []


def make_device_handler(device_params):
    """
    Create a device handler object that provides device specific parameters and
    functions, which are called in various places throughout our code.

    If no device_params are defined or the "name" in the parameter dict is not
    known then a default handler will be returned.

    """
    if device_params is None:
        device_params = {}

    device_name = device_params.get("name", "default")
    class_name = "%sDeviceHandler" % device_name.capitalize()
    devices_module_name = "ncclient.devices.%s" % device_name
    dev_module_obj = __import__(devices_module_name)
    handler_module_obj = getattr(
        getattr(dev_module_obj, "devices"), device_name)
    class_obj = getattr(handler_module_obj, class_name)
    handler_obj = class_obj(device_params)
    return handler_obj


def connect_ssh(*args, **kwds):
    """
    Initialize a :class:`Manager` over the SSH transport.
    For documentation of arguments see :meth:`ncclient.transport.SSHSession.connect`.

    The underlying :class:`ncclient.transport.SSHSession` is created with
        :data:`CAPABILITIES`. It is first instructed to
        :meth:`~ncclient.transport.SSHSession.load_known_hosts` and then
        all the provided arguments are passed directly to its implementation
        of :meth:`~ncclient.transport.SSHSession.connect`.

    To invoke advanced vendor related operation add device_params =
        {'name':'<vendor_alias>'} in connection paramerers. For the time,
        'junos' and 'nexus' are supported for Juniper and Cisco Nexus respectively.
    """
    if "device_params" in kwds:
        device_params = kwds["device_params"]
        del kwds["device_params"]
    else:
        device_params = None

    device_handler = make_device_handler(device_params)
    device_handler.add_additional_ssh_connect_params(kwds)
    global VENDOR_OPERATIONS
    VENDOR_OPERATIONS.update(device_handler.add_additional_operations())
    session = EmNetconfClientSSHSession(device_handler, kwds["device_info"])
    if "hostkey_verify" not in kwds or kwds["hostkey_verify"]:
        session.load_known_hosts()

    try:
        del kwds["device_info"]
        session.connect(*args, **kwds)
    except Exception as ex:
        if session.transport:
            session.close()
        raise
    return Manager(session, device_handler, **kwds)
