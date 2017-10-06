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

START = 1
READY_TO_START = 2
STOP = 3
READY_TO_STOP = 4


class EmNetconfSessionDate(object):
    lock = threading.Lock()
    session_date = {}

    @classmethod
    @decorater_log
    def set_session_date(cls, session_id, session):
        with cls.lock:
            cls.session_date[session_id] = session
        GlobalModule.EM_LOGGER.debug(
            "Active session-id:%s", cls.session_date.keys())

    @classmethod
    @decorater_log
    def get_session_date(cls, session_id):
        with cls.lock:
            session = cls.session_date.get(session_id)
        return session

    @classmethod
    @decorater_log
    def del_session_date(cls, session_id):
        try:
            with cls.lock:
                del cls.session_date[session_id]
        except KeyError:
            GlobalModule.EM_LOGGER.debug("Active Session-id None")


class EmStatus(object):

    lock = threading.Lock()
    em_status = STOP

    @classmethod
    def get_em_status(cls):
        with cls.lock:
            status = cls.em_status
        return status

    @classmethod
    @decorater_log
    def set_em_status(cls, status):
        with cls.lock:
            cls.em_status = status


class NetconfMethods(server.NetconfMethods):
    @decorater_log
    def __init__(self):

    @decorater_log
    def nc_append_capabilities(self, capabilities):
        GlobalModule.EM_LOGGER.debug("nc_append_capabilities start")

        base1_0 = etree.Element("capability")
        base1_0.text = "urn:ietf:params:xml:ns:netconf:base:1.0"
        capabilities.append(base1_0)

        GlobalModule.EM_LOGGER.debug(
            "base1_0: %s", etree.tostring(base1_0))

            if base.text == "urn:ietf:params:netconf:base:1.0" \
                    or base.text == "urn:ietf:params:netconf:base:1.1":
                base.getparent().remove(base)

        result, capability_list = GlobalModule.EM_CONFIG.read_if_process_conf(

        if result is not True:
            GlobalModule.EM_LOGGER.debug(
                "read_if_process_conf [Capability] read Error")

            return

        cap = capabilities.find("capability")

        for value in capability_list:
            xml.text = value
            cap.append(xml)

        GlobalModule.EM_LOGGER.debug(
            "capabilities: %s", etree.tostring(capabilities))
        GlobalModule.EM_LOGGER.debug("nc_append_capabilities end")

    @decorater_log
    def rpc_get_config(self, session, rpc, source_elm, filter_or_none):
        GlobalModule.EM_LOGGER.debug("rpc_get_config start")

        if EmStatus.get_em_status() != START:
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
        GlobalModule.EM_LOGGER.debug("rpc_edit_config start")

        if EmStatus.get_em_status() != START:
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
    def _accept_chan_thread(self):
        try:
            while True:
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
            self.server.remove_socket(self)


class EmNetconfServerSession(server.NetconfServerSession):
    @decorater_log
    def __init__(self, pktstream, methods, session_id, debug):
        super(EmNetconfServerSession, self).__init__(
            pktstream, methods, session_id, debug)

    @decorater_log
    def _handle_message(self, msg):
        if not self.session_open:
            return

        try:
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
    NetconfSSHServer起動＆分離応答クラス
        コンストラクタ
<rpc-error>
<error-type>application</error-type>
<error-severity>error</error-severity>
<error-message xml:lang="en">dummy</error-message>
</rpc-error>
        オーダフローコントロールから起動され、必要情報をQueueに設定。
        Netconfサーバへ引き渡す。
        パラメータの説明:
            order_result:オーダ結果
            ec_message: ECメッセージ
            session_id: セッションID
        戻り値の説明:
            True:正常
            False:異常
        mainから起動され、EM状態を「起動中」へ更新する。
        パラメータの説明：
            なし
        戻り値の説明:
            なし
        mainから起動され、オーダフローコントロールの
        トランザクション完了を待ち合わせた後停止処理を行う。
        パラメータの説明:
            なし
        戻り値の説明:
            なし
        mainからの停止指示を待ち合わせ、
        EM状態を「停止準備中」へ更新する。
        停止指示受信後、トランザクション終了を待ち合わせ、
        EM状態を「停止中」へ更新する。
        パラメータの説明：
            なし
        戻り値の説明:
            なし
        オーダフローコントロールからの応答結果を基に、
        ECメインモジュールへのNetconf(rpc-reply)の送信を行う。
        パラメータの説明：
            order_resp:オーダ制御結果
            ec_message:受信要求信号
            session_id:ECメインモジュールとの接続中セッションID
        戻り値の説明:
        自クラスから起動され、引数に応じたNetconf(rpc-reply)を生成する。
        パラメータの説明：
            order_resp:ECメインモジュールへの応答内容
        戻り値の説明:
            error_rpc:ECメインモジュールへのレスポンスメッセージ
        オーダフローコントロールからの応答を待ち合わせ
        ECメインモジュールへの応答メソッドを起動する
        パラメータの説明：
            なし
        戻り値の説明:
            なし
