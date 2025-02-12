
from . import proxy,mhttp
import socket, threading
log = mhttp.log
import ssl
import traceback
class CapsDealer(proxy.ProxyDealer):
    """
        http和https抓包，要自己实现MsgRecord类处理抓包数据，否则默认只是打印抓包的url和头部数据等信息
        buildz.netz.mhttp.record.MsgRecord的实现可参考buildz.netz.mhttp.record.MsgLog
    """
    def init(self, skt, context, srv_context, channel_read_size=1024000, record=None):
        super().init(skt, channel_read_size, record=record)
        self.context = context
        self.srv_context = srv_context
    def deal_channel(self, skt_cli, skt_srv):
        #self.wskt.closefile()
        #wskt.closefile()
        skt_cli = mhttp.WSocket.Bind(self.context.wrap_socket(skt_cli.skt, server_side=True))
        #context = ssl._create_unverified_context(ssl.PROTOCOL_TLS_CLIENT)
        skt_srv = mhttp.WSocket.Bind(self.srv_context.wrap_socket(skt_srv.skt, server_side=False))
        self.record.set_ssl(True)
        try:
            while True:
                if not skt_cli.readable():
                    continue
                line, headers, data_size = mhttp.http_recv(skt_cli)
                if line is None:
                    continue
                self.default_deal(skt_cli, line, headers, data_size, skt_srv)
        except Exception as exp:
            log.debug(f"channel exp: {exp}")
            log.warn(f"traceback: {traceback.format_exc()}")
        finally:
            self.record.set_ssl(False)


class CapsProxy(proxy.Proxy):
    """
        http和https抓包，要自己实现MsgRecord类处理抓包数据，否则默认只是打印抓包的url和头部数据等信息
        buildz.netz.mhttp.record.MsgRecord的实现可参考buildz.netz.mhttp.record.MsgLog
    """
    def init(self, addr, fp_sign, fp_prv, password = None,listen=5, record=None,cafile=None, capath=None, cadata=None,check_hostname=True):
        super().init(addr, listen, record)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(fp_sign, fp_prv, password=password)
        if cafile is not None or capath is not None or cadata is not None:
            # 导入根证书，需要单个根证书文件cafile或者根证书文件夹capath或者根证书数据cadata
            # cadata是证书数据，不清楚能不能多个证书字节码拼在一起
            srv_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            srv_context.load_verify_locations(cafile=cafile, capath=capath, cadata=cadata)
            srv_context.check_hostname = check_hostname
        else:
            # 不会校验服务端https证书是否有效，可能有风险？
            srv_context = ssl._create_unverified_context(ssl.PROTOCOL_TLS_CLIENT)
        self.context = context
        self.srv_context = srv_context
    def call(self):
        self.running=True
        skt = socket.socket()
        skt.bind(self.addr)
        skt.listen(self.listen)
        self.skt = skt
        while self.running:
            skt,addr = self.skt.accept()
            deal = CapsDealer(skt, self.context, self.srv_context, record=self.record.clone())
            th = threading.Thread(target=deal,daemon=True)
            th.start()
            self.ths.append(th)
