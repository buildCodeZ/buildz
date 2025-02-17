import socket,threading
from . import mhttp
from . import record as _record
from buildz import Base
import traceback
log = mhttp.log
class ProxyDealer(Base):
    """
        http和https代理
    """
    def init(self, skt, channel_read_size=1024000, record=None, protocol = "HTTP/1.1"):
        self.wskt = mhttp.WSocket.Bind(skt)
        self.channel_read_size = channel_read_size
        self.deals = {}
        self.deals[None] = self.default_deal
        self.deals['CONNECT'] = self.connect_deal
        self.skts = {}
        self.protocol = protocol
        if record is None:
            record = _record.MsgLog(log)
        self.record = record
    def simple_chunked(self, skt_read, skt_send):
        while True:
            n, dt = mhttp.chunked_data(skt_read)
            self.record.add_chunk(dt)
            bts = mhttp.chunked_encode(dt)
            skt_send.send(bts)
            if n==0:
                break
    def default_deal(self, skt_cli, line, headers, data_size, skt=None):
        self.record.request(line, headers, data_size)
        http_type, url, protocol = line
        skt,fc_done = mhttp.http_send_head(http_type, url, headers, data_size,protocol, skt, self.skts)
        if data_size>0:
            data = skt_cli.read(data_size)
            skt.send(data)
            self.record.add(data)
        if mhttp.check_chunked(headers):
            self.simple_chunked(skt_cli, skt)
        self.record.finish()
        line, headers, data_size=mhttp.http_recv(skt)
        self.record.response(line, headers, data_size)
        protocol, code, rsp_text = line
        bts = mhttp.http_encode_rsp(code, rsp_text, headers, data_size, protocol)
        skt_cli.send(bts)
        if data_size>0:
            data = skt.read(data_size)
            skt_cli.send(data)
            self.record.add(data)
        if mhttp.check_chunked(headers):
            self.simple_chunked(skt, skt_cli)
        self.record.finish()
        fc_done()
    def close(self):
        self.wskt.close()
        for addr,skt in self.skts.items():
            try:
                skt.close()
            except:
                pass
    def connect_deal(self, skt_cli, line, headers, data_size, skt=None):
        self.record.request(line, headers, data_size)
        if data_size>0:
            dt = skt_cli.read(data_size)
            self.record.add(dt)
        self.record.finish()
        http_type, url, protocol = line
        addr = url.split(":")
        if len(addr)==1:
            addr.append(80)
        addr[1] = int(addr[1])
        addr = tuple(addr)
        code, txt = 200, "OK"
        need_close = skt is None
        if skt is None:
            try:
                skt = mhttp.WSocket.Connect(addr)
            except:
                code,txt=404,"Not Found"
        self.record.response([self.protocol,code, txt],{},0).finish()
        bts = mhttp.http_encode_rsp(code, txt, protocol = self.protocol)
        skt_cli.send(bts)
        if code==200:
            try:
                self.deal_channel(skt_cli, skt)
            finally:
                if need_close:
                    skt.close()
    def deal_channel(self, skt_cli, skt_srv):
        return self.direct_channel(skt_cli, skt_srv)
    def direct_channel(self, skt_cli, skt_srv):
        try:
            while True:
                while skt_cli.readable():
                    bts = skt_cli.recv(self.channel_read_size)
                    if len(bts)==0:
                        return
                    skt_srv.send(bts)
                while skt_srv.readable():
                    bts = skt_srv.recv(self.channel_read_size)
                    if len(bts)==0:
                        return
                    skt_cli.send(bts)
        except Exception as exp:
            log.debug(f"channel exp: {exp}")
            log.warn(f"traceback: {traceback.format_exc()}")
    def deal(self):
        try:
            if not self.wskt.readable():
                return True
            line, headers, data_size = mhttp.http_recv(self.wskt.rfile)
            if line is None:
                return True
            log.debug(f"[DEAL] START")
            log.debug(f"proxy recv: {line, headers, data_size}")
        except Exception as exp:
            log.warn(f"http_recv exp: {exp}")
            log.warn(f"traceback: {traceback.format_exc()}")
            return False
        http_type, url, protocol = line
        if http_type not in self.deals:
            http_type = None
        fc = self.deals[http_type]
        fc(self.wskt, line, headers, data_size)
        log.debug(f"[DEAL] END")
        return True
    def call(self):
        log.debug(f"[TESTZ] new deal")
        try:
            while True:
                if not self.deal():
                    break
        finally:
            self.wskt.close()
            #self.monitor.close()

pass

class Proxy(Base):
    def init(self, addr, listen=5, record=None):
        self.addr = addr
        self.listen = listen
        self.ths = []
        self.running=False
        if record is None:
            record = _record.MsgLog(log)
        self.record = record
    def close(self):
        self.skt.close()
    def call(self):
        self.running=True
        skt = socket.socket()
        skt.bind(self.addr)
        skt.listen(self.listen)
        self.skt = skt
        while self.running:
            skt,addr = self.skt.accept()
            deal = ProxyDealer(skt,record=self.record.clone())
            th = threading.Thread(target=deal,daemon=True)
            th.start()
            self.ths.append(th)
