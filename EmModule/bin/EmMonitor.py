# -*- coding: utf-8 -*-
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



class EmMonitorManager(manager.Manager):

    def __init__(self, session, device_handler, timeout=30, *args, **kwargs):
        super(EmMonitorManager, self).__init__(
            session, device_handler, timeout=30, *args, **kwargs)


class EmMonitorSSHSession(transport.SSHSession):

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
    if "host" in kwds:
        host = kwds["host"]
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

    except (transport.SSHUnknownHostError, transport.SessionError,
            transport.SSHError, transport.AuthenticationError,
            transport.TransportError):
        sys.exit(ERROR_CODE)

    try:
        CONNECTION.close_session()

    except (transport.SessionCloseError, transport.SessionError,
            operations.MissingCapabilityError, operations.OperationError):
        sys.exit(ERROR_CODE)

    sys.exit(SUCCESS_CODE)
