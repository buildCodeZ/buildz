'''
多线程版middleserver
slect写起来太复杂了，先在多线程搞一版

'''

import socket, select, traceback, threading, time, os
from buildz.base import Base
from buildz import log as logz, pyz, xf, fz, dz
from buildz import args as argx
from .base import *
#from .slt import Selector
import threading as th
from .blkskt import BlockSocket
class SERVER:
    ADDR='addr'
    MID='mid'
pass
class MidServer(Base):
    def init(self, addr, listen_num=50, log=None, deal_fc = None):
        log = (log or logz.simple())("midServer")
        self.deal_fc = deal_fc
        self.log = log
        self.addr = fetch_addr(addr)
        self.server = new_skt(self.addr)
        self.log.debug(f"ms try server bind: {self.addr}")
        self.server.bind(self.addr)
        self.log.debug(f"ms done server bind: {self.addr}")
        self.server.listen(listen_num)
        self.dealers = {}
        self.running=1
        # id -> mid_skt
        self.servers = {}
        # id -> (mid_skt, mid_skt)
        self.pairs = {}
        self.pairs_id = 0
    def th_server(self):
        while True:
            self.server.accept()
    def deal(self, opt):
        '''
            服务端监听新连接
        '''
        if opt!=Selector.READABLE:
            return
        skt, addr = self.server.accept()
        try:
            if self.deal_fc:
                skt = self.deal_fc(skt)
            skt = BlockSocket.wrap(skt, 0)
            skt.enable_v2bs()
            self.slt.add(skt, self.wrap_deal_cli(skt), True)
            self.log.debug(f"accept: {addr}, {skt}")
        except Exception as exp:
            self.log.error(f"exp in accept {addr}, {skt}: {exp}")
            self.log.error(f"exp detail: {pyz.s_exp()}")
    def wrap_deal_cli(self, skt):
        '''
            新连接处理逻辑：读取客户端数据，创建中间件处理对应功能
        '''
        def wrap(_skt, ind):
            def fc(opt):
                self.log.debug(f"cli deal: skt: {skt}, ind: {ind}, opt: {opt}")
                if opt == Selector.TIMEOUT:
                    return
                if opt == Selector.CLOSED:
                    _id = id(skt)
                    if _id in self.dealers:
                        self.dealers[_id].close()
                        del self.dealers[_id]
                    return
                data = skt.recv()
                addr, listen = dz.g(data, addr = 0, listen=0)
                self.slt.remove(ind)
                skt.send({"success":True})
                self.log.debug(f"new dealer: {skt}, {addr}, {listen}")
                dealer = MidDealer(self.slt, skt, addr, listen, log=self.log)
                _id = id(skt)
                self.dealers[_id] = dealer
                #self.dealers.append(dealer)
            return fc
        return wrap
    def call(self):
        self.running=1
        while self.running and self.slt.num()>0:
            self.slt()
        self.close()
    def close(self):
        for dealer in self.dealers.values():
            self.log.debug(f"dealer close: {dealer}")
            dealer.close()
        #self.dealers = []
        self.dealers = {}
        if self.server:
            self.log.debug(f"midsrv server close: {self.server}")
            self.slt.remove(self.server_id)
            self.server.close()
            self.log.debug(f"midsrv done server close: {self.server}")
            self.server = None
pass

class MidClient(Base):
    def init(self, addr, log=None, deal_fc = None):
        self.deal_fc = deal_fc
        self.log = (log or logz.simple())("midClient")
        self.addr = fetch_addr(addr)
        self.slt = Selector(log=self.log)
    '''
        remote_type:
            addr: ip/sock_path
            mid: mid_server_id
    '''
    def connect(self, local_addr, remote_addr, listen=False, remote_type=SERVER.ADDR):
        local_addr = fetch_addr(local_addr)
        remote_addr = fetch_addr(remote_addr) if remote_type==SERVER.ADDR else remote_addr
        mid_cli = new_skt(self.addr)
        self.log.debug(f"[TEST.MIDCLIENT] before connect to {self.addr}")
        mid_cli.connect(self.addr)
        self.log.debug(f"[TEST.MIDCLIENT] done connect to {self.addr}")
        if self.deal_fc:
            mid_cli = self.deal_fc(mid_cli)
        self.mid_cli = BlockSocket.wrap(mid_cli, 0)
        self.mid_cli.enable_v2bs()
        data = dz.m(listen=not listen, addr = remote_addr, remote_type = remote_type)
        self.log.debug(f"[TEST.MIDCLIENT] mid_cli send: {data}")
        self.mid_cli.send(data)
        self.log.debug(f"[TEST.MIDCLIENT] mid_cli done send")
        rst = self.mid_cli.recv()
        self.log.debug(f"[TEST.MIDCLIENT] mid_cli recv: {rst}")
        assert rst.get("success")
        self.mid_dealer = MidDealer(self.slt, self.mid_cli, local_addr, listen, log=self.log)
    def call(self):
        self.running=True
        while self.running and self.slt.num()>0:
            self.slt()
        self.close()
    def close(self):
        self.mid_dealer.close()
        if self.mid_cli:
            self.mid_cli.close()
            self.mid_cli = None

class MidServers(Base):
    def init(self):
        self.servers = {}
    def listen(self, sid, dealer):
        self.servers[sid] = dealer
    def close(self, sid):
        if sid in self.servers:
            del self.servers[sid]
    def connect(self, sid, addr):
        if sid not in self.servers:
            return None
        skt_cli, skt_srv = socket.socketpair()
        dealer = self.servers[sid]
        try:
            dealer.deal_server_skt(skt_srv, addr)
        except Exception as exp:
            self.log.error(f"error in connect {sid} by {addr}: {exp}")
            skt_cli.close()
            skt_srv.close()
            self.close(sid)
            return None
        return skt_cli

pass

class MidDealer(Base):
    '''
        接收一个socket，和本身是客户端/服务端的标志，以及本地的另一个地址
        如果是客户端：
            等待数据，数据里会有id和指令（connect, send, close)，进行相应处理
        如果是服务端：
            监听端口等待连接，有连接就往客户端发新建连接请求并新建id
    '''
    def init(self, slt, mid_skt, addr, is_server=False, listen_num=50, max_recv=1024*1024*10, log=None, deal_ping=30, server_type = SERVER.ADDR, mid_srvs = None):
        self.server_type = server_type
        self.log = (log or logz.simple())("midDealer")
        self.log.debug(f"init dealer: mid_skt: {mid_skt}, addr: {addr}, is_server: {is_server}")
        self.max_recv=max_recv
        self.mid_skt = mid_skt
        self.addr = fetch_addr(addr) if server_type == SERVER.ADDR else addr
        self.is_server = is_server
        self.id = 0
        self.listen_num = listen_num
        self.clis = {}
        self.deal_ping=deal_ping
        self.slt = slt
        self.mid_srvs = mid_srvs
        self.mid_id = self.slt.add(self.mid_skt, self.deal_mid, timeout=self.deal_ping)
        if self.is_server and server_type == SERVER.ADDR:
            self.listen()
        else:
            self.mid_srvs.listen(addr, self)
    def listen(self):
        self.server = new_skt(self.addr)
        self.log.debug(f"[TESTZ] middealer try server bind: {self.addr}")
        self.server.bind(self.addr)
        self.log.debug(f"[TESTZ] middealer done server bind: {self.addr}")
        self.server.listen(self.listen_num)
        self.server_id = self.slt.add(self.server, self.deal_server)
    def deal_server(self, opt):
        '''
            本地监听到新连接的处理方法:
                新建本地客户端连接处理，往远端中间件发送新建连接请求，等待响应处理
        '''
        if opt!=Selector.READABLE:
            if opt==Selector.CLOSED:
                # 本地监听被中断，结束
                self.close()
            return
        skt, addr = self.server.accept()
        self.deal_server_skt(skt, addr)
    def deal_server_skt(self, skt, addr):
        self.log.debug(f"accept: {skt}, {addr}")
        _id = self.id
        self.id+=1
        self.clis[_id]=[skt, addr, 0, -1]#slt_id]
        #slt_id = self.slt.add(skt, self.wrap_cli(_id))
        self.log.debug(f"before send connect: {self.mid_skt}, {addr}")
        self.mid_skt.send({"type":"connect", 'id': _id})
        self.log.debug(f"done send connect: {self.mid_skt}, {addr}")
    def wrap_cli(self, _id):
        def fc(opt):
            return self.deal_cli(_id, opt)
        return fc
    def deal_cli(self, _id, opt):
        '''
            本地客户端连接处理逻辑：
                读取数据，发给远端
        '''
        if opt== Selector.CLOSED:
            self.close_cli(_id)
            return
        skt, addr, status, slt_id = self.clis[_id]
        #self.log.debug(f"deal_cli: {_id}")
        if status==0:
            #远程连接还没建好，等待中
            return
        self.log.debug(f"[TESTZ.Client] before recv from {skt.getpeername()} to {skt.getsockname()}")
        dt = skt.recv(self.max_recv)
        self.log.debug(f"[TESTZ.Client] recv from {skt.getpeername()} to {skt.getsockname()}: {dsp(dt)}")
        do_close=0
        if dt == b'':
            obj = dz.mnn(id=_id, type="close")
            do_close=1
        else:
            obj = dz.mnn(id=_id, type="send", data=dt)
        self.log.debug(f"[TESTZ.Client] send from {skt.getpeername()} to {self.mid_skt.skt.getpeername()}: {dsp(obj)}")
        self.mid_skt.send(obj)
        self.log.debug(f"[TESTZ.Client] done send from {skt.getpeername()} to {self.mid_skt.skt.getpeername()}")
        #self.log.debug(f"mid send: ")
        if do_close:
            self.log.debug(f"do cli close: {_id}")
            self.close_cli(_id)
    def close_cli(self, _id):
        if _id not in self.clis:
            return
        skt, addr, status, slt_id = self.clis[_id]
        #if status in (0,1):
        #    skt.close()
        self.log.debug(f"close_cli try close: {skt}")
        skt.close()
        self.log.debug(f"close_cli done close: {skt}")
        del self.clis[_id]
        self.slt.remove(slt_id)
    def close_clis(self):
        ids = list(self.clis.keys())
        for _id in ids:
            self.close_cli(_id)
    def close(self):
        '''
            关闭所有客户端
            关闭中间层连接
            如果监听本地，关闭本地监听
        '''
        self.close_clis()
        if self.mid_skt:
            try:
                mid_addr= self.mid_skt.skt.getsockname()
            except:
                mid_addr = self.mid_skt
            self.log.debug(f"try mid_skt close: {mid_addr}")
            self.mid_skt.close()
            self.log.debug(f"done mid_skt close: {mid_addr}")
            self.mid_skt = None
            self.slt.remove(self.mid_id)
        if self.is_server and self.server:
            try:
                srv_addr = self.server.getsockname()
            except:
                srv_addr = self.server
            self.log.debug(f"middeal try server close: {srv_addr}")
            self.server.close()
            self.log.debug(f"middeal done server close: {srv_addr}")
            self.server = None
            self.slt.remove(self.server_id)
    def deal_mid(self, opt):
        '''
            中间件连接处理逻辑
        '''
        if opt!=Selector.READABLE:
            if opt==Selector.TIMEOUT:
                dt = dz.mnn(type="ping")
                self.mid_skt.send(dt)
            if opt==Selector.CLOSED:
                self.close()
            return
        self.log.debug(f"[TESTZ.MID] before recv from {self.mid_skt.skt.getpeername()} to {self.mid_skt.skt.getsockname()}")
        data = self.mid_skt.recv()
        self.log.debug(f"[TESTZ.MID] recv from {self.mid_skt.skt.getpeername()} to {self.mid_skt.skt.getsockname()}: {dsp(data)}")
        if data==b'':
            self.close()
            return
        self.single_deal(data)
        while self.mid_skt.readable():
            data = self.mid_skt.recv()
            if data==b'':
                self.close()
                return
            self.single_deal(data)
    def single_deal(self, data):
        _type, _id, dt = dz.g(data, type=None, id=None, data=None)
        #self.log.debug(f"deal_mid: type: {_type}, id:{_id}")
        if _type=='connect':
            skt = new_skt(self.addr)
            try:
                self.log.debug(f"[TEST.MID] before connect to {self.addr}")
                skt.connect(self.addr)
                self.log.debug(f"[TEST.MID] done connect to {self.addr}")
                obj = dz.mnn(id=_id, type='connected')
                slt_id = self.slt.add(skt, self.wrap_cli(_id))
                self.clis[_id] = [skt, self.addr, 1, slt_id]
            except Exception as exp:
                self.log.error(f"exp in connect: {exp}")
                obj = dz.mnn(id=_id, type='connected', error= str(exp))
            self.log.debug(f"[TESTZ.MID]: send from {self.mid_skt.skt.getsockname()} to {self.mid_skt.skt.getpeername()}: {dsp(obj)}")
            self.mid_skt.send(obj)
            self.log.debug(f"[TESTZ.MID]: done send from {self.mid_skt.skt.getsockname()} to {self.mid_skt.skt.getpeername()}")
        elif _type=='connected':
            self.log.debug("connected")
            err = data.get("error", None)
            if err:
                self.log.error(f"exp in connected: {err}")
                self.close_cli(_id)
            else:
                tmp = self.clis[_id]
                tmp[2]=1
                skt=tmp[0]
                slt_id = self.slt.add(skt, self.wrap_cli(_id))
                tmp[3] = slt_id
        elif _type == 'send':
            self.log.debug(f"send")
            if _id not in self.clis:
                self.log.warn(f"{_id} not in clis")
                rst = dz.mnn(id=_id, type="close")
                self.mid_skt.send(rst)
                # TODO ?
                pass
            else:
                _skt = self.clis[_id][0]
                self.log.debug(f"[TESTZ.MID]: sen from {_skt.getsockname()} to {_skt.getpeername()}: {dsp(dt)}")
                _skt.send(dt)
                self.log.debug(f"[TESTZ.MID]: done sen from {_skt.getsockname()} to {_skt.getpeername()}")
        elif _type=='close':
            self.close_cli(_id)
        elif _type == 'ping':
            self.mid_skt.send(dz.mnn(type="pong"))
        elif _type == 'pong':
            pass
        else:
            assert 0, f"unknown type {_type}"
