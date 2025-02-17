
from . import proxy,mhttp
import socket, threading
log = mhttp.log
from buildz import xf
import ssl
from os.path import join, isfile
import traceback
from buildz import fz

cert_conf = xf.loads(r"""
// 国家
country: CN
// 省份
provice: fujian
// 城镇
local: quanzhou
// 机构
org: testz
// 域名
comman: testz
// 邮箱
email: netz@testz
// 是否是ca
ca: true
//dns: [localhost]
// 签名有效提前时间（签名多少天前就有效）
valid_before: 1
// 签名有效时间（签名后有效多少天）
valid: 3650
dns: []
""")
sign_conf = xf.loads(r"""
// 签名有效提前时间（签名多少天前就有效）
valid_before: 1
// 签名有效时间（签名后有效多少天）
valid: 3650
""")
class CapsDealer(proxy.ProxyDealer):
    """
        http和https抓包，要自己实现MsgRecord类处理抓包数据，否则默认只是打印抓包的url和头部数据等信息
        buildz.netz.mhttp.record.MsgRecord的实现可参考buildz.netz.mhttp.record.MsgLog
    """
    def init(self, skt, ca, srv_context, channel_read_size=1024000, record=None,dp_cache=None):
        if dp_cache is None:
            dp_cache = "./res/certs"
        super().init(skt, channel_read_size, record=record)
        self.ca = ca
        self.srv_context = srv_context
        self.contexts = {}
        self.dp_cache = dp_cache
    def sign(self, hostname):
        dp = join(self.dp_cache, "_"+hostname)
        fz.makedir(dp)
        fp_csr = join(dp, "csr")
        fp_cert = join(dp, "cert")
        fp_prv = join(dp, "prv")
        if isfile(fp_cert):
            return fp_cert, fp_prv, None
        try:
            from buildz.netz import sslz
        except:
            # 不能创建域名证书，则直接用根证书
            return self.ca
        conf = dict(cert_conf)
        conf['comman']=hostname
        conf['dns'] = [hostname]
        sslz.gen_prv(fp_prv)
        sslz.gen_csr(fp_csr, fp_prv, conf, None)
        sslz.sign_csr(fp_cert, fp_csr, self.ca[0], self.ca[1],sign_conf, self.ca[2])
        return fp_cert, fp_prv, None
    def context(self, hostname):
        if hostname not in self.contexts:
            fp_cert, fp_prv, pwd = self.sign(hostname)
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(fp_cert, fp_prv, password=pwd)
            self.contexts[hostname]=context
        return self.contexts[hostname]
    def deal_channel(self, skt_cli, skt_srv):
        #self.wskt.closefile()
        #wskt.closefile()
        hostname = skt_srv.addr[0]
        context = self.context(hostname)
        skt_cli = mhttp.WSocket.Bind(context.wrap_socket(skt_cli.skt, server_side=True))
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
    def init(self, addr, fp_sign, fp_prv, password = None,listen=5, record=None,cafile=None, capath=None, cadata=None,check_hostname=True, dp_cache = None):
        super().init(addr, listen, record)
        # context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        # context.load_cert_chain(fp_sign, fp_prv, password=password)
        self.ca = fp_sign, fp_prv, password
        if cafile is not None or capath is not None or cadata is not None:
            # 导入根证书，需要单个根证书文件cafile或者根证书文件夹capath或者根证书数据cadata
            # cadata是证书数据，不清楚能不能多个证书字节码拼在一起
            srv_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            srv_context.load_verify_locations(cafile=cafile, capath=capath, cadata=cadata)
            srv_context.check_hostname = check_hostname
        else:
            # 不会校验服务端https证书是否有效，可能有风险？
            srv_context = ssl._create_unverified_context(ssl.PROTOCOL_TLS_CLIENT)
        #self.context = context
        self.srv_context = srv_context
        if dp_cache is None:
            dp_cache = "./res/certs"
        self.dp_cache = dp_cache
    def call(self):
        self.running=True
        skt = socket.socket()
        skt.bind(self.addr)
        skt.listen(self.listen)
        self.skt = skt
        while self.running:
            skt,addr = self.skt.accept()
            deal = CapsDealer(skt, self.ca, self.srv_context, record=self.record.clone(), dp_cache = self.dp_cache)
            th = threading.Thread(target=deal,daemon=True)
            th.start()
            self.ths.append(th)
