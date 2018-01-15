#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2017 Nippon Telegraph and Telephone Corporation
# Filename: em_monitor.py
'''
EM Monitoring Module for RA
'''
import sys
import os
import time

from ncclient import manager
from ncclient import transport
from ncclient import operations

USERNAME = None
PASSWORD = None
SSH_TIMEOUT = 0

IPV4 = None
PORT = 0

ERROR_CODE = 1
SUCCESS_CODE = 0

'''
Function for server connection
It connects to EM server, transmits/receives Hello and make it a success if the monitoring session is established.
Every time it encounters exception, it ends the program with End Code 1.
If the process completes successfully, it ends the program with End Code 0.
'''


class EmMonitorManager(manager.Manager):
    '''
    Manager class that inheritted close to override.
    '''

    def __init__(self, session, device_handler, timeout=30, *args, **kwargs):
        super(EmMonitorManager, self).__init__(
            session, device_handler, timeout=30, *args, **kwargs)


class EmMonitorSSHSession(transport.SSHSession):
    '''
    SSHSession class that inheritted close to override.
    '''

    def __init__(self, device_handler):
        super(EmMonitorSSHSession, self).__init__(device_handler)

    def close(self):
        if self._transport.is_active():
            try:
                count = 0
                while self._channel is None or not self._channel.closed:
                    time.sleep(0.001)
                    if count > 1000 or self._channel is None:
                        break
                    count += 1
            except Exception as e:
                cmd="logger -i self._channel = "+str(self._channel)
                os.system(cmd)
                cmd1="logger -i exception messages = "+str(e)
                os.system(cmd1)
            self._transport.close()
        self._channel = None
        self._connected = False


def connect_ssh(*args, **kwds):
    """
    Initialize a :class:`Manager` over the SSH transport.
    For documentation of arguments see :meth:
        `ncclient.transport.SSHSession.connect`.

    The underlying :class:`ncclient.transport.SSHSession` is created with
        :data:`CAPABILITIES`. It is first instructed to
        :meth:`~ncclient.transport.SSHSession.load_known_hosts` and then
        all the provided arguments are passed directly to its implement
        ation of :meth:`~ncclient.transport.SSHSession.connect`.

    To invoke advanced vendor related operation add device_params =
        {'name':'<vendor_alias>'} in connection paramerers. For the time,
        'junos' and 'nexus' are supported for Juniper and Cisco Nexus
        respectively.
    """
    # Extract device parameter dict, if it was passed into this function.
    # Need to remove it from kwds, since the session.connect() doesn't like
    # extra stuff in there.
    if "device_params" in kwds:
        device_params = kwds["device_params"]
        del kwds["device_params"]
    else:
        device_params = None
    device_handler = manager.make_device_handler(device_params)
    device_handler.add_additional_ssh_connect_params(kwds)
    session = EmMonitorSSHSession(device_handler)
    if "hostkey_verify" not in kwds or kwds["hostkey_verify"]:
        session.load_known_hosts()

    try:
        session.connect(*args, **kwds)
    except Exception as ex:
        if session.transport:
            session.close()
            print ex
        raise
    return EmMonitorManager(session, device_handler, **kwds)


def connect(*args, **kwds):
    '''
    Function for Connection
    '''
    if "host" in kwds:
        host = kwds["host"]
        device_params = kwds.get('device_params', {})
        if host == 'localhost' and device_params.get('name') == 'junos' \
                and device_params.get('local'):
            return manager.connect_ioproc(*args, **kwds)
        else:
            return connect_ssh(*args, **kwds)

if __name__ == "__main__":
    IPV4=sys.argv[2]
    PORT=int(sys.argv[3])
    USERNAME=sys.argv[4]
    SSH_TIMEOUT=int(sys.argv[1])
    if sys.argv[5:]:
        PASSWORD=sys.argv[5]
    else:
        PASSWORD=""

    try:
        CONNECTION = connect(host=IPV4, port=PORT, username=USERNAME,
                             password=PASSWORD, timeout=SSH_TIMEOUT,
                             hostkey_verify=False,
                             device_params={'name': 'alu'})

    except (transport.SSHUnknownHostError, transport.SessionError,
            transport.SSHError, transport.AuthenticationError,
            transport.TransportError):
        os.system('logger -i "EM Monitoring Module@Abnormal Termination because of Connection Failure."')
        sys.exit(ERROR_CODE)

    try:
        CONNECTION.close_session()

    except (transport.SessionCloseError, transport.SessionError,
            operations.MissingCapabilityError, operations.OperationError):
        os.system('logger -i "EM Monitoring Module@Abnormal Termination because of close-session Failure."')
        sys.exit(ERROR_CODE)

    sys.exit(SUCCESS_CODE)
