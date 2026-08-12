from buildz.base import Base
import socket, select, traceback, threading, time, os
from buildz import log as logz, pyz, xf, fz, pyz
from buildz import args as argx
from .base import *
from .blkskt import BlockSocket
CLOSED="closed"
TIMEOUT="timeout"
READABLE = "readable"
class Selector(Base):
    CLOSED=CLOSED
    TIMEOUT=TIMEOUT
    READABLE=READABLE
    def init(self, wait_sec = 30.0, log=None):
        self.log = (log or logz.simple())("selector")
        self.datas = {}
        self.wait_sec = wait_sec
        self.curr = None
    def num(self):
        return len(self.datas)
    def add(self, skt, fc, call=False, timeout=0):
        '''
            这里timeout是多久没收到数据后触发
        '''
        skt = BlockSocket.unwrap(skt)
        ind = id(skt)
        if call:
            fc = fc(skt, ind)
        self.datas[ind] = [skt, fc, timeout, 0.0]
        return ind
    def remove(self, ind):
        if ind not in self.datas:
            return
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
        self.log.debug(f"slt.deal start: {self.wait_sec}")
        ks = list(self.datas.keys())
        for k in ks:
            dt = self.datas[k]
            skt, fc, tm, skt_tm = dt
            skt = dt[0]
            add = 1
            if skt._closed:
                add=0
                rms.append(k)
                try:
                    fc(CLOSED)
                except Exception as exp:
                    self.log.error(f"fc(CLOSED) error for {skt}: {exp}")
                    self.log.error(pyz.s_exp())
            elif tm and diff>0:
                skt_tm+=diff
                if skt_tm>=tm:
                    try:
                        fc(TIMEOUT)
                    except Exception as exp:
                        self.log.error(f"fc(TIMEOUT) error for {skt}: {exp}")
                        self.log.error(pyz.s_exp())
                        fc(CLOSED)
                        rms.append(k)
                        add=0
                    skt_tm=0
                dt[3]=skt_tm
            if add:
                skts.append(skt)
        for ind in rms:
            self.remove(ind)
        rms = []
        self.log.debug(f"[TESTZ] skts: {skts}")
        (rlist,wlist,elist)=select.select(skts,[],[],self.wait_sec)
        if len(rlist)>0:
            self.log.debug(f"single deal: {rlist}")
        for skt in rlist:
            ind = id(skt)
            if ind in self.datas:
                fc = self.datas[ind][1]
                self.datas[ind][3]=0
                try:
                    fc(READABLE)
                except Exception as exp:
                    self.log.error(f"read exp for {skt}: {pyz.s_exp()}")
                    self.log.error(f"read exp for {skt}: {exp}, do close")
                    rms.append(ind)
                    try:
                        fc(CLOSED)
                    except Exception as exp:
                        self.log.error(f"close exp after read for {skt}: {exp}")
                        self.log.error(pyz.s_exp())
            else:
                self.log.error(f"deal {ind} not in datas")
        for ind in rms:
            self.remove(ind)
        self.log.debug(f"slt.deal done")

pass
