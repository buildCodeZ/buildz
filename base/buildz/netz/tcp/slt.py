from buildz.base import Base
import socket, select, traceback, threading, time, os
from buildz import log as logz, pyz, xf, fz
from buildz import args as argx
from .base import *
from .blkskt import BlockSocket
CLOSED="closed"
TIMEOUT="timeout"
READABLE = "readable"
class Selector(Base):
    def init(self, wait_sec = 1.0, log=None):
        self.log = (log or logz.simple())("selector")
        self.datas = {}
        self.wait_sec = wait_sec
        self.curr = None
    def add(self, skt, fc, call=False, timeout=0):
        skt = BlockSocket.unwrap(skt)
        ind = id(skt)
        if call:
            fc = fc(skt, ind)
        self.datas[ind] = [skt, fc, timeout, 0.0]
        return ind
    def remove(self, ind):
        del self.datas[ind]
    def call(self):
        try:
            self.deal()
        except Exception as exp:
            self.log.error(f"deal exp: {exp}")
            raise exp
    def deal(self):
        if self.curr is None:
            self.curr = time.time()
        curr = time.time()
        diff = curr-self.curr
        self.curr = curr
        rms = []
        skts = []
        for k, dt in self.datas.items():
            skt, fc, tm, skt_tm = dt
            skt = dt[0]
            if skt._closed:
                rms.append(k)
                fc(CLOSED)
            elif tm and diff>0:
                skt_tm+=diff
                if skt_tm>=tm:
                    fc(TIMEOUT)
                    skt_tm=0
                dt[3]=skt_tm
            else:
                skts.append(skt)
        for ind in rms:
            self.remove(ind)
        #self.log.debug(f"[TESTZ] skts: {skts}")
        (rlist,wlist,elist)=select.select(skts,[],[],self.wait_sec)
        if len(rlist)>0:
            self.log.debug(f"single deal: {len(rlist)}")
        for skt in rlist:
            ind = id(skt)
            if ind in self.datas:
                self.datas[ind][1](READABLE)

pass
