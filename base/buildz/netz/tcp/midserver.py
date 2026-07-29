'''
middleserver

服务端:
    ip,port as server

客户端:
    connect and send listen port, 
    local: connect to other port
    server: listen such port

user: connect to listen port

add ssl verify

服务端启动，监听端口

客户端连接服务端，发送模式和端口

模式：
    服务端到客户端：
        服务端新启动监听端口
        有用户连上（新socket），通知客户端新建连接，存到处理队列：
            处理逻辑：转发
    客户端到服务端:
        客户端启动监听端口
        有用户脸上（新socket），通知服务端新建连接，存到处理队列：
            处理逻辑：转发
'''

import socket, select, traceback, threading, time, os
from buildz.base import Base
from buildz import log as logz, pyz, xf, fz, dz
from buildz import args as argx
from .base import *
from .slt import Selector
from .blkskt import BlockSocket
class MidServer(Base):
    def init(self, addr, listen_num=10, log=None, deal_fc = None):
        log = (log or logz.simple())("midServer")
        self.deal_fc = deal_fc
        self.log = log
        self.addr = fetch_addr(addr)
        self.server = new_skt(self.addr)
        self.server.bind(self.addr)
        self.server.listen(listen_num)
        self.slt = Selector(log=self.log)
        self.server_id = self.slt.add(self.server, self.deal)
        self.dealers = []
        self.running=1
    def deal(self):
        skt, addr = self.server.accept()
        if self.deal_fc:
            skt = self.deal_fc(skt)
        skt = BlockSocket.wrap(skt, 0)
        skt.enable_v2bs()
        self.slt.add(skt, self.wrap_deal_cli(skt), True)
    def wrap_deal_cli(self, skt):
        def wrap(_skt, ind):
            def fc():
                data = skt.recv()
                addr, listen = dz.g(data, addr = 0, listen=0)
                self.slt.remove(ind)
                skt.send({"success":True})
                dealer = MidDealer(self.slt, skt, addr, listen, log=self.log)
                self.dealers.append(dealer)
            return fc
        return wrap
    def call(self):
        self.running=1
        while self.running:
            self.slt()
    def close(self):
        for dealer in self.dealers:
            dealer.close()
        self.dealers = []
        if self.server:
            self.slt.remove(self.server_id)
            self.server.close()
            self.server = None
pass

class MidClient(Base):
    def init(self, addr, log=None, deal_fc = None):
        self.deal_fc = deal_fc
        self.log = (log or logz.simple())("midClient")
        self.addr = fetch_addr(addr)
        self.slt = Selector()
    def connect(self, local_addr, remote_addr, listen=False):
        local_addr = fetch_addr(local_addr)
        remote_addr = fetch_addr(remote_addr)
        mid_cli = new_skt(self.addr)
        mid_cli.connect(self.addr)
        if self.deal_fc:
            mid_cli = self.deal_fc(mid_cli)
        self.mid_cli = BlockSocket.wrap(mid_cli, 0)
        self.mid_cli.enable_v2bs()
        data = dz.m(listen=not listen, addr = remote_addr)
        self.mid_cli.send(data)
        rst = self.mid_cli.recv()
        assert rst.get("success")
        self.mid_dealer = MidDealer(self.slt, self.mid_cli, local_addr, listen, log=self.log)
    def call(self):
        self.running=True
        while self.running:
            self.slt()
    def close(self):
        self.mid_dealer.close()
        if self.mid_cli:
            self.mid_cli.close()
            self.mid_cli = None


class MidDealer(Base):
    '''
        接收一个socket，和本身是客户端/服务端的标志，以及本地的另一个地址
        如果是客户端：
            等待数据，数据里会有id和指令（connect, send, close)，进行相应处理
        如果是服务端：
            监听端口等待连接，有连接就往客户端发新建连接请求并新建id
    '''
    def init(self, slt, mid_skt, addr, is_server=False, listen_num=10, max_recv=1024*1024*10, log=None):
        self.log = (log or logz.simple())("midDealer")
        self.max_recv=max_recv
        self.mid_skt = mid_skt
        self.addr = fetch_addr(addr)
        self.is_server = is_server
        self.id = 0
        self.listen_num = listen_num
        self.clis = {}
        self.slt = slt
        self.mid_id = self.slt.add(self.mid_skt, self.deal_mid)
        if self.is_server:
            self.listen()
    def listen(self):
        self.server = new_skt(self.addr)
        self.log.debug(f"[TESTZ] middealer bind: {self.addr}")
        self.server.bind(self.addr)
        self.server.listen(self.listen_num)
        self.server_id = self.slt.add(self.server, self.deal_server)
    def deal_server(self):
        skt, addr = self.server.accept()
        _id = self.id
        self.id+=1
        slt_id = self.slt.add(skt, self.wrap_cli(_id))
        self.clis[_id]=[skt, addr, 0, slt_id]
        self.mid_skt.send({"type":"connect", 'id': _id})
    def wrap_cli(self, _id):
        def fc():
            return self.deal_cli(_id)
        return fc
    def deal_cli(self, _id):
        skt, addr, status, slt_id = self.clis[_id]
        if status!=1:
            return
        dt = skt.recv(self.max_recv)
        do_close=0
        if dt == b'':
            obj = dz.mnn(id=_id, type="close")
            do_close=1
        else:
            obj = dz.mnn(id=_id, type="send", data=dt)
        self.mid_skt.send(obj)
        if do_close:
            self.close_cli(_id)
    def close_cli(self, _id):
        skt, addr, status, slt_id = self.clis[_id]
        if status in (0,1):
            skt.close()
        del self.clis[_id]
        self.slt.remove(slt_id)
    def close(self):
        if self.mid_skt:
            self.mid_skt.close()
            self.mid_skt = None
        if self.is_server and self.server:
            self.server.close()
            self.server = None
    def deal_mid(self):
        data = self.mid_skt.recv()
        if data==b'':
            self.close()
            return
        _type, _id, dt = dz.g(data, type=None, id=None, data=None)
        if _type=='connect':
            skt = new_skt(self.addr)
            try:
                skt.connect(self.addr)
                obj = dz.mnn(id=_id, type='connected')
                slt_id = self.slt.add(skt, self.wrap_cli(_id))
                self.clis[_id] = [skt, self.addr, 1, slt_id]
            except Exception as exp:
                self.log.error(f"exp in connect: {exp}")
                obj = dz.mnn(id=_id, type='connected', error= str(exp))
            self.mid_skt.send(obj)
        elif _type=='connected':
            err = data.get("error", None)
            if err:
                self.log.error(f"exp in connected: {exp}")
                self.close_cli(_id)
            else:
                self.clis[_id][2]=1
        elif _type == 'send':
            if _id not in self.clis:
                pass
            self.clis[_id][0].send(dt)
        elif _type=='close':
            if _id not in self.clis:
                return
            skt = self.clis[_id]
            skt[0].close()
            skt[0]=None
            skt[2]=-1
        else:
            assert 0, f"unknown type {_type}"
