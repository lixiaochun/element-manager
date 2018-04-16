#! /usr/bin/env python
# _*_ coding: utf-8 _*_
# Copyright(c) 2018 Nippon Telegraph and Telephone Corporation
# Filename: EmNetconfServer.py
'''
Netconf Server function
'''
import io
import Queue
import time
import threading
import traceback
import select
import paramiko as ssh
from netconf import server
from netconf import util
from netconf import qmap
from netconf import NSMAP
import netconf.error as ncerror
from lxml import etree
import GlobalModule
from EmCommonLog import decorater_log
from EmSysCommonUtilityDB import EmSysCommonUtilityDB


class EmNetconfSessionDate(object):
    '''
    Instance information management class for each session.
    '''
    lock = threading.Lock()
    session_date = {}

    @classmethod
    @decorater_log
    def set_session_date(cls, session_id, session):
        '''
        Processing the settings of session instance corresponding to session ID
        '''
        with cls.lock:
            cls.session_date[session_id] = session
        GlobalModule.EM_LOGGER.debug(
            "Active session-id:%s", cls.session_date.keys())

    @classmethod
    @decorater_log
    def get_session_date(cls, session_id):
        '''
        Processing the acquisition of session instance
        corresponding to session ID
        '''
        with cls.lock:
            session = cls.session_date.get(session_id)
        return session

    @classmethod
    @decorater_log
    def del_session_date(cls, session_id):
        '''
        Processing the deletion of session instance corresponding to session ID
        '''
        try:
            with cls.lock:
                del cls.session_date[session_id]
        except KeyError:
            GlobalModule.EM_LOGGER.debug("Active Session-id None")


class NetconfMethods(server.NetconfMethods):
    '''
    NetconfMethod processing
    '''
    @decorater_log
    def __init__(self):
        '''
        Constructor
        '''
        self.__rpc_error_message = """
<rpc-error>
<error-type>application</error-type>
<error-severity>error</error-severity>
<error-message xml:lang="en">internal server error</error-message>
</rpc-error>
"""

    @decorater_log
    def nc_append_capabilities(self, capabilities):
        '''
        Launched from NetconfSSHServer class.
        Edit Capablitiy to be set into Hello.
        Explanation about parameter:
            capabilities: Transmit Capability list
        Explanation about return value:
            None
        '''
        GlobalModule.EM_LOGGER.debug("nc_append_capabilities start")

        base1_0 = etree.Element("capability")
        base1_0.text = "urn:ietf:params:xml:ns:netconf:base:1.0"
        capabilities.append(base1_0)

        GlobalModule.EM_LOGGER.debug(
            "base1_0: %s", etree.tostring(base1_0))

        for base in capabilities.xpath('/capabilities/capability'):
            if base.text == "urn:ietf:params:netconf:base:1.0" \
                    or base.text == "urn:ietf:params:netconf:base:1.1":
                base.getparent().remove(base)

        result, capability_list = GlobalModule.EM_CONFIG.read_if_process_conf(
            'Capability')

        if result is not True:
            GlobalModule.EM_LOGGER.debug(
                "read_if_process_conf [Capability] read Error")

            return

        cap = capabilities.find("capability")

        for value in capability_list:
            xml = etree.fromstring('<capability></capability>')
            xml.text = value
            cap.append(xml)

        GlobalModule.EM_LOGGER.debug(
            "capabilities: %s", etree.tostring(capabilities))
        GlobalModule.EM_LOGGER.debug("nc_append_capabilities end")

    @decorater_log
    def rpc_get_config(self, session, rpc, source_elm, filter_or_none):
        '''
        Launched from NetconfSSHServer class and send Netconf
        message to order flow control.Explanation about parameter:
            session:
            rpc:Netconf message parser result
            source_elm::source parameter of Netconf message
            filter_or_none:filter parameter of Netconf message
        Explanation about return value:
            None
        '''
        GlobalModule.EM_LOGGER.debug("rpc_get_config start")

        (ret, status) = GlobalModule.EMSYSCOMUTILDB.read_system_status(
            EmSysCommonUtilityDB.GET_DATA_TYPE_MEMORY)
        if status != EmSysCommonUtilityDB.STATE_START:
            return False, etree.fromstring(self.__rpc_error_message)

        transaction_result = \
            GlobalModule.EM_ORDER_CONTROL.get_transaction_presence()

        if transaction_result is not True:

            return False, etree.fromstring(self.__rpc_error_message)

        str_rpc = etree.tostring(rpc)

        GlobalModule.EM_LOGGER.debug("get-config message: %s", str_rpc)

        file_rpc = io.BytesIO(str_rpc)

        GlobalModule.EM_ORDER_CONTROL.execute(file_rpc, session)

        GlobalModule.EM_LOGGER.debug("rpc_get_config end")

        return True, None

    @decorater_log
    def rpc_edit_config(self, session, rpc, *unused_params):
        '''
        Launched from NetconfSSHServer class and send Netconf message
        to order flow control.Explanation about parameter:
            session:
            rpc:Netconf message parser result
            target_elm::Parameter for tag and below of Netconf message
            config_elm:Parameter for config tag and below of Netconf message
        Explanation about return value:
            None
        '''
        GlobalModule.EM_LOGGER.debug("rpc_edit_config start")

        (ret, status) = GlobalModule.EMSYSCOMUTILDB.read_system_status(
            EmSysCommonUtilityDB.GET_DATA_TYPE_MEMORY)
        if status != EmSysCommonUtilityDB.STATE_START:
            return False, etree.fromstring(self.__rpc_error_message)

        transaction_result = \
            GlobalModule.EM_ORDER_CONTROL.get_transaction_presence()

        if transaction_result is not True:

            return False, etree.fromstring(self.__rpc_error_message)

        str_rpc = etree.tostring(rpc)

        GlobalModule.EM_LOGGER.debug("edit-config message: %s", str_rpc)

        file_rpc = io.BytesIO(str_rpc)

        GlobalModule.EM_ORDER_CONTROL.execute(file_rpc, session)

        GlobalModule.EM_LOGGER.debug("rpc_edit_config end")

        return True, None


class EmNetconfSSHServerSocket(server.NetconfSSHServerSocket):
    '''
    An SSH socket connection from a client
    '''
    @decorater_log
    def __init__(self,
                 server_ctl,
                 server_methods,
                 server,
                 newsocket,
                 addr,
                 debug):
        self.server_methods = server_methods
        self.server = server
        self.client_socket = newsocket
        self.client_addr = addr
        self.debug = debug
        self.server_ctl = server_ctl

        try:
            if self.debug:
                GlobalModule.EM_LOGGER.debug(
                    "%s: Opening SSH connection", str(self))

            self.ssh = ssh.Transport(self.client_socket)
            self.ssh.add_server_key(self.server.host_key)
            self.ssh.start_server(server=self.server_ctl)
        except ssh.AuthenticationException as error:
            self.client_socket.close()
            self.client_socket = None
            GlobalModule.EM_LOGGER.error(
                "302001 Authentication failed:  %s", str(error))
            raise

        self.thread = threading.Thread(None,
                                       self._accept_chan_thread,
                                       name="NetconfSSHAcceptThread")
        self.thread.daemon = True
        self.thread.start()

    @decorater_log
    def _timeout_accept(self):
        '''
        catch running _accept_chan_thread's timeout
        '''
        GlobalModule.EM_LOGGER.debug('_accept_chan_thread is timeout')
        self.timeout_flag = True

    @decorater_log
    def _accept_chan_thread(self):
        try:
            timeout_time = 60.0
            GlobalModule.EM_LOGGER.debug(
                "timeout value is %s", (timeout_time,))
            self.timeout_flag = False
            timer = threading.Timer(timeout_time, self._timeout_accept)
            timer.start()
            while True:
                if self.timeout_flag:
                    raise Exception("accept thread is timeout")
                if self.debug:
                    GlobalModule.EM_LOGGER.debug(
                        "%s: Accepting channel connections", str(self))

                channel = self.ssh.accept(timeout=1)
                if channel is None:
                    if not self.ssh.is_active():
                        GlobalModule.EM_LOGGER.debug(
                            "%s: Got channel as None: exiting", str(self))
                        return
                    GlobalModule.EM_LOGGER.warn(
                        "202011 %s: Got channel as None on active.", str(self))
                    continue

                sid = self.server.allocate_session_id()
                if self.debug:
                    GlobalModule.EM_LOGGER.debug(
                        "%s: Creating session-id %s", str(self), str(sid))
                session = EmNetconfServerSession(
                    channel, self.server_methods, sid, self.debug)
                if self.debug:
                    GlobalModule.EM_LOGGER.debug(
                        "%s: Client session-id %s created: %s",
                        str(self),
                        str(sid),
                        str(session))
                EmNetconfSessionDate.set_session_date(sid, session)
                GlobalModule.EM_LOGGER.info(
                    "102003 Creating Connection %s", str(self))
        except Exception as error:
            if self.debug:
                GlobalModule.EM_LOGGER.error(
                    "302002 %s: Unexpected exception: %s: %s",
                    str(self),
                    str(error),
                    traceback.format_exc())
            else:
                GlobalModule.EM_LOGGER.error(
                    "%s: Unexpected exception: %s closing",
                    str(self),
                    str(error))
            self.client_socket.close()
            self.client_socket = None
        finally:
            timer.cancel()
            self.timeout_flag = False
            self.server.remove_socket(self)


class EmNetconfServerSession(server.NetconfServerSession):
    '''
    Netconf Server-side Session Protocol
    '''
    @decorater_log
    def __init__(self, pktstream, methods, session_id, debug):
        super(EmNetconfServerSession, self).__init__(
            pktstream, methods, session_id, debug)

    @decorater_log
    def _handle_message(self, msg):
        '''
        'Handle a message, lock is already held
        '''
        if not self.session_open:
            return

        try:
            tree = etree.parse(io.BytesIO(msg.encode('utf-8')))
            if not tree:
                raise ncerror.SessionError(msg, "Invalid XML from client.")
        except etree.XMLSyntaxError:
            GlobalModule.EM_LOGGER.warning(
                "202010 Closing session due to malformed message")
            raise ncerror.SessionError(msg, "Invalid XML from client.")

        rpcs = tree.xpath("/nc:rpc", namespaces=NSMAP)
        if not rpcs:
            raise ncerror.SessionError(msg, "No rpc found")

        for rpc in rpcs:
            try:
                msg_id = rpc.get('message-id')
                if self.debug:
                    GlobalModule.EM_LOGGER.debug(
                        "%s: Received rpc message-id: %s", str(self), msg_id)
            except (TypeError, ValueError):
                raise ncerror.SessionError(
                    msg, "No valid message-id attribute found")

            try:
                rpc_method = rpc.getchildren()
                if len(rpc_method) != 1:
                    if self.debug:
                        GlobalModule.EM_LOGGER.debug(
                            "%s: Bad Msg: msg-id: %s", str(self), msg_id)
                    raise ncerror.RPCSvrErrBadMsg(rpc)
                rpc_method = rpc_method[0]

                rpcname = rpc_method.tag.replace(qmap('nc'), "")
                params = rpc_method.getchildren()
                paramslen = len(params)

                if rpcname == "close-session":
                    if self.debug:
                        GlobalModule.EM_LOGGER.debug(
                            "%s: Received close-session msg-id: %s",
                            str(self),
                            msg_id)
                    GlobalModule.EM_LOGGER.info(
                        "102007 Connection Closed: %s", str(self))
                    EmNetconfSessionDate.del_session_date(self.session_id)
                    self.send_rpc_reply(etree.Element("ok"), rpc)
                    self.close()
                    return
                elif rpcname == "kill-session":
                    if self.debug:
                        GlobalModule.EM_LOGGER.debug(
                            "%s: Received kill-session msg-id: %s",
                            str(self), msg_id)
                    self.send_rpc_reply(etree.Element("ok"), rpc)
                    self.close()
                    return
                elif rpcname == "get":

                    if paramslen > 1:
                        raise ncerror.RPCSvrErrBadMsg(rpc)
                    if params and not util.filter_tag_match(params[0],
                                                            "nc:filter"):
                        raise ncerror.RPCSvrUnknownElement(rpc, params[0])
                    if not params:
                        params = [None]
                elif rpcname == "get-config":

                    GlobalModule.EM_LOGGER.info("102004 Receiving get-config")

                    if paramslen > 2:
                        raise ncerror.RPCSvrErrBadMsg(rpc)
                    source_param = rpc_method.find(
                        "nc:source", namespaces=NSMAP)
                    if source_param is None:
                        raise ncerror.RPCSvrMissingElement(
                            rpc, util.elm("nc:source"))
                    filter_param = None
                    if paramslen == 2:
                        filter_param = rpc_method.find(
                            "nc:filter", namespaces=NSMAP)
                        if filter_param is None:
                            unknown_elm = params[0] if params[
                                0] != source_param else params[1]
                            raise ncerror.RPCSvrUnknownElement(
                                rpc, unknown_elm)
                    params = [source_param, filter_param]

                elif rpcname == "edit-config":
                    GlobalModule.EM_LOGGER.info("102008 Receiving edit-config")

                    if paramslen > 2:
                        raise ncerror.RPCSvrErrBadMsg(rpc)

                    target_param = rpc_method.find(
                        "nc:target", namespaces=NSMAP)
                    if target_param is None:
                        raise ncerror.RPCSvrMissingElement(
                            rpc, util.elm("nc:target"))

                    config_param = None
                    if paramslen == 2:
                        config_param = rpc_method.find(
                            "nc:config", namespaces=NSMAP)
                        if config_param is None:
                            unknown_elm = params[0] if params[
                                0] != config_param else params[1]
                            raise ncerror.RPCSvrUnknownElement(
                                rpc, unknown_elm)
                    params = [target_param, config_param]

                try:
                    rpcname = rpcname.rpartition("}")[-1]
                    method_name = "rpc_" + rpcname.replace('-', '_')
                    method = getattr(
                        self.methods, method_name, self._rpc_not_implemented)
                    result, reply = method(self.session_id, rpc, *params)

                    if result is not True:
                        self.send_rpc_reply(reply, rpc)

                except NotImplementedError:
                    raise ncerror.RPCSvrErrNotImpl(rpc)
            except ncerror.RPCSvrErrBadMsg as msgerr:
                if self.new_framing:
                    self.send_message(msgerr.get_reply_msg())
                else:
                    GlobalModule.EM_LOGGER.warning(
                        "Closing 1.0 session due to malformed message")
                    raise ncerror.SessionError(msg, "Malformed message")
            except ncerror.RPCServerError as error:
                self.send_message(error.get_reply_msg())
            except Exception as exception:
                error = ncerror.RPCSvrException(rpc, exception)
                self.send_message(error.get_reply_msg())


class EmNetconfServer(server.NetconfSSHServer):
    '''
    A netconf server
    '''
    @decorater_log
    def __init__(self,
                 server_ctl=None,
                 server_methods=None,
                 port=830,
                 host_key=None,
                 debug=False):
        super(EmNetconfServer, self).__init__(server_ctl,
                                              server_methods,
                                              port,
                                              host_key,
                                              debug)

    @decorater_log
    def _accept_socket_thread(self, proto_sock):
        """Call from within a thread to accept connections."""

        while True:
            if self.debug:
                GlobalModule.EM_LOGGER.debug(
                    "%s: Accepting connections", str(self))

            rfds, unused, unused = select.select(
                [proto_sock, self.close_rsocket], [], [])
            if self.close_rsocket in rfds:
                if self.debug:
                    GlobalModule.EM_LOGGER.debug(
                        "%s: Got close notification closing down server",
                        str(self))

                sockets = list(self.sockets)
                for sock in sockets:
                    if sock in self.sockets:
                        sock._shutdown()

                return

            if proto_sock in rfds:
                client, addr = proto_sock.accept()
                if self.debug:
                    GlobalModule.EM_LOGGER.debug(
                        "%s: Client accepted: %s: %s",
                        str(self), str(client), str(addr))
                try:
                    with self.lock:
                        sock = EmNetconfSSHServerSocket(self.server_ctl,
                                                        self.server_methods,
                                                        self,
                                                        client,
                                                        addr,
                                                        self.debug)
                        self.sockets.append(sock)
                except ssh.AuthenticationException:
                    pass


class EmNetconfSSHServer(object):
    '''
    NetconfSSHServer launch & separated response class.
    '''
    @decorater_log
    def __init__(self, username=None, password=None, port=830, system_status=None, host_key=None):
        '''
        Constructor
        '''
        self.nc_server = None
        self.que_events = Queue.Queue(10)
        self.stop_event = threading.Event()
        self.started = True
        self.__rpc_error_message = """
<rpc-error>
<error-type>application</error-type>
<error-severity>error</error-severity>
<error-message xml:lang="en">dummy</error-message>
</rpc-error>
"""
        if system_status is None:
            GlobalModule.EMSYSCOMUTILDB.write_system_status(
                "UPDATE",
                EmSysCommonUtilityDB.STATE_STOP,
                EmSysCommonUtilityDB.GET_DATA_TYPE_BOTH)
            GlobalModule.EM_LOGGER.info(
                "102009 EM Status Transition[%s -> %s]",
                "UNKNOWN", "STOP")
            raise IOError("system_status is not specified")

        self.stop_state = GlobalModule.COM_STOP_NORMAL

        (ret, lo_status) = GlobalModule.EMSYSCOMUTILDB.read_system_status(
            EmSysCommonUtilityDB.GET_DATA_TYPE_MEMORY)

        if lo_status != EmSysCommonUtilityDB.STATE_STOP:
            raise RuntimeError(
                "Starting request detected, but Em state is not Stop state.")

        if system_status != EmSysCommonUtilityDB.STATE_CHANGE_OVER:
            GlobalModule.EMSYSCOMUTILDB.write_system_status(
                "UPDATE",
                EmSysCommonUtilityDB.STATE_READY_TO_START,
                EmSysCommonUtilityDB.GET_DATA_TYPE_BOTH)
            GlobalModule.EM_LOGGER.info(
                "102009 EM Status Transition[%s -> %s]",
                "STOP", "READY_TO_START")
        else:
            GlobalModule.EMSYSCOMUTILDB.write_system_status(
                "UPDATE",
                EmSysCommonUtilityDB.STATE_CHANGE_OVER,
                EmSysCommonUtilityDB.GET_DATA_TYPE_MEMORY)
            GlobalModule.EM_LOGGER.info(
                "102009 EM Status Transition[%s -> %s]",
                "STOP", "CHG_OVER")

        if username is None:
            GlobalModule.EMSYSCOMUTILDB.write_system_status(
                "UPDATE",
                EmSysCommonUtilityDB.STATE_STOP,
                EmSysCommonUtilityDB.GET_DATA_TYPE_BOTH)
            GlobalModule.EM_LOGGER.info(
                "102009 EM Status Transition[%s -> %s]",
                "READY_TO_START", "STOP")
            raise IOError("username is not specified")
        if password is None:
            GlobalModule.EMSYSCOMUTILDB.write_system_status(
                "UPDATE",
                EmSysCommonUtilityDB.STATE_STOP,
                EmSysCommonUtilityDB.GET_DATA_TYPE_BOTH)
            GlobalModule.EM_LOGGER.info(
                "102009 EM Status Transition[%s -> %s]",
                "READY_TO_START", "STOP")
            raise IOError("password is not specified")

        result, conf_log_level = GlobalModule.EM_CONFIG.\
            read_sys_common_conf("Em_log_level")
        if result is not True:
            GlobalModule.EMSYSCOMUTILDB.write_system_status(
                "UPDATE",
                EmSysCommonUtilityDB.STATE_STOP,
                EmSysCommonUtilityDB.GET_DATA_TYPE_BOTH)
            GlobalModule.EM_LOGGER.info(
                "102009 EM Status Transition[%s -> %s]",
                "READY_TO_START", "STOP")
            raise IOError

        debug_flg = bool(conf_log_level == "DEBUG")

        server_ctl = server.SSHUserPassController(
            username=username,
            password=password)

        try:
            self.nc_server = EmNetconfServer(
                server_ctl=server_ctl,
                server_methods=NetconfMethods(),
                port=port,
                host_key=host_key,
                debug=debug_flg)
        except Exception as exception:
            GlobalModule.EM_LOGGER.debug(
                "Connect Error:%s", str(type(exception)))
            GlobalModule.EMSYSCOMUTILDB.write_system_status(
                "UPDATE",
                EmSysCommonUtilityDB.STATE_STOP,
                EmSysCommonUtilityDB.GET_DATA_TYPE_BOTH)
            GlobalModule.EM_LOGGER.info(
                "102009 EM Status Transition[%s -> %s]",
                "READY_TO_START", "STOP")

            raise exception

        self.stop_mon_thread = threading.Thread(target=self._stop_monitoring)
        self.stop_mon_thread.daemon = True
        self.stop_mon_thread.start()

        self.wait_order_thread = threading.Thread(target=self._wait_order_resp)
        self.wait_order_thread.daemon = True
        self.wait_order_thread.start()

    @decorater_log
    def send_response(self, order_result, ec_message, session_id):
        '''
        Launched from order flow control sets necessary information
        in the Queue, hand over to Netconf server.
        Explanation about parameter:
            order_result:Order result
            ec_message: EC message
            session_id: Session ID
        Explanation about return value:
            True:Normal
            False:Abnormal
        '''
        try:
            self.que_events.put(
                (order_result, ec_message, session_id), block=False)
        except Queue.Full:
            return False

        return True

    @decorater_log
    def start(self):
        '''
        Launched from main, updates the EM status to "Running".
        Explanation about parameter:
            None
        Explanation about return value:
            None
        '''
        GlobalModule.EMSYSCOMUTILDB.write_system_status(
            "UPDATE",
            EmSysCommonUtilityDB.STATE_START,
            EmSysCommonUtilityDB.GET_DATA_TYPE_BOTH)
        GlobalModule.EM_LOGGER.info("102009 EM Status Transition[%s -> %s]",
                                    "READY_TO_START", "START")

    @decorater_log
    def stop(self, stop_state):
        '''
        Launched from main, waits until transactions
        in order flow control have been finished.
        Then, conducts processing to stop.

        Explanation about parameter:
            stop_state: Stop state
        Explanation about return value:
            None
        '''
        self.stop_state = stop_state
        self.stop_event.set()

    @decorater_log
    def _stop_monitoring(self):
        '''
        Wait for the instruction to stop from main,
        updates EM status to "Getting ready to stop".
        After receiving the instruction to stop,
        wait until transactions will finish
        and updates EM status to "Stopping".
        Explanation about parameter：
            None
        Explanation about return value:
            None
        '''
        result, transaction_stop_watch = GlobalModule.EM_CONFIG.\
            read_sys_common_conf("Timer_transaction_stop_watch")

        if result is not True:
            stop_watch_timer = 0.2
            GlobalModule.EM_LOGGER.debug(
                "Timer_transaction_stop_watch default Setting: %s",
                stop_watch_timer)
        else:
            stop_watch_timer = float(transaction_stop_watch) / 1000
            GlobalModule.EM_LOGGER.debug(
                "Timer_transaction_stop_watch: %s",
                stop_watch_timer)

        while True:
            if self.stop_event.is_set() is True:
                (ret, status) = GlobalModule.EMSYSCOMUTILDB.read_system_status(
                    EmSysCommonUtilityDB.GET_DATA_TYPE_MEMORY)
                if status != EmSysCommonUtilityDB.STATE_START:
                    self.stop_event.clear()
                    GlobalModule.EM_LOGGER.debug(
                        "Stop request detected, " +
                        "but Em state is not Start state.")
                else:
                    if self.stop_state == GlobalModule.COM_STOP_NORMAL:
                        GlobalModule.EMSYSCOMUTILDB.write_system_status(
                            "UPDATE",
                            EmSysCommonUtilityDB.STATE_READY_TO_STOP,
                            EmSysCommonUtilityDB.GET_DATA_TYPE_BOTH)
                        GlobalModule.EM_LOGGER.info(
                            "102009 EM Status Transition[%s -> %s]",
                            "START", "READY_TO_STOP")

                    elif self.stop_state == GlobalModule.COM_STOP_CHGOVER:
                        GlobalModule.EMSYSCOMUTILDB.write_system_status(
                            "UPDATE",
                            EmSysCommonUtilityDB.STATE_CHANGE_OVER,
                            EmSysCommonUtilityDB.GET_DATA_TYPE_BOTH)
                        GlobalModule.EM_LOGGER.info(
                            "102009 EM Status Transition[%s -> %s]",
                            "START", "CHANGE_OVER")
                    break
            time.sleep(stop_watch_timer)
        while True:
            transaction_result = \
                GlobalModule.EM_ORDER_CONTROL.get_transaction_presence()

            if transaction_result is True:
                break

            time.sleep(stop_watch_timer)

        GlobalModule.EM_ORDER_CONTROL.stop()

        self.started = False

        self.nc_server.close()
        self.nc_server.join()

        if self.stop_state == GlobalModule.COM_STOP_NORMAL:

            GlobalModule.EMSYSCOMUTILDB.write_system_status(
                "UPDATE",
                EmSysCommonUtilityDB.STATE_STOP,
                EmSysCommonUtilityDB.GET_DATA_TYPE_BOTH)
            GlobalModule.EM_LOGGER.info(
                "102009 EM Status Transition[%s -> %s]",
                "READY_TO_STOP", "STOP")

        elif self.stop_state == GlobalModule.COM_STOP_CHGOVER:

            GlobalModule.EMSYSCOMUTILDB.write_system_status(
                "UPDATE",
                EmSysCommonUtilityDB.STATE_STOP,
                EmSysCommonUtilityDB.GET_DATA_TYPE_MEMORY)
            GlobalModule.EM_LOGGER.info(
                "102009 EM Status Transition[%s -> %s]",
                "READY_TO_STOP", "STOP")

    @decorater_log
    def _send_netconf_resp(self, order_resp, ec_message, session_id):
        '''
        Transmits Netconf(rpc-reply) to EC main module based
        on the response from order flow control.
        Explanation about parameter：
            order_resp:Order control result
            ec_message:Receive request signal
            session_id:Session ID during connection to EC mail module
        Explanation about return value:
        '''
        session_date = EmNetconfSessionDate.get_session_date(session_id)

        if session_date is None:
            GlobalModule.EM_LOGGER.debug(
                "Target session is not existed.Could not send response.")
            return

        rpc_reply = self._create_resp_message(order_resp)

        rpc_str = ec_message.read()

        GlobalModule.EM_LOGGER.debug("rpc_reply: %s", rpc_str)

        session_date.send_rpc_reply(rpc_reply, etree.fromstring(rpc_str))

    @decorater_log
    def _create_resp_message(self, order_resp):
        '''
        Launched from self class, creates Netconf(rpc-reply)
        according to the argument.Explanation about parameter：
            order_resp:Response to EC main module
        Explanation about return value:
            error_rpc:Response message to EC main module
        '''

        if order_resp == GlobalModule.ORDER_RES_OK:
            GlobalModule.EM_LOGGER.info("102005 Sending rpc-reply")
            return etree.Element('ok')

        error_rpc = etree.fromstring(self.__rpc_error_message)

        if order_resp == GlobalModule.ORDER_RES_ROLL_BACK_END:
            error_rpc.find(".//error-message").text = "not modified"

        elif order_resp == GlobalModule.ORDER_RES_PROC_ERR_CHECK:
            error_rpc.find(".//error-message").text = "unprocessable entity"

        elif order_resp == GlobalModule.ORDER_RES_PROC_ERR_ORDER:
            error_rpc.find(".//error-message").text = "bad request"

        elif order_resp == GlobalModule.ORDER_RES_PROC_ERR_MATCH:
            error_rpc.find(".//error-message").text = "conflict"

        elif order_resp == GlobalModule.ORDER_RES_PROC_ERR_INF:
            error_rpc.find(".//error-message").text = "not found"

        elif order_resp == GlobalModule.ORDER_RES_PROC_ERR_TEMP:
            error_rpc.find(".//error-message").text = "service unavailable"

        else:
            error_rpc.find(".//error-message").text = "internal server error"

        error_rpc_str = etree.tostring(error_rpc)

        GlobalModule.EM_LOGGER.info(
            "102006 Sending rpc-error: %s", error_rpc_str)

        return error_rpc

    @decorater_log
    def _wait_order_resp(self):
        """
        Wait for orderflow control response.
        Start method making response for EC.
        Explanation about parameter：
            None
        Explanation about return value:
            None
        """
        while self.started:
            try:
                order_resp, ec_message, session_id = self.que_events.get()

                self._send_netconf_resp(order_resp, ec_message, session_id)

                self.que_events.task_done()

            except Exception as exception:
                GlobalModule.EM_LOGGER.debug(
                    "Message Send Error:%s", str(type(exception)))

                self.que_events.task_done()
