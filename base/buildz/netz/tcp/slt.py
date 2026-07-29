from buildz.base import Base
import socket, select, traceback, threading, time, os
from buildz import log as logz, pyz, xf, fz
from buildz import args as argx
from .base import *
from .blkskt import BlockSocket
class Selector(Base):
    def init(self, wait_sec = 1.0, log=None):
        self.log = (log or logz.simple())("selector")
        self.datas = {}
        self.wait_sec = wait_sec
    def add(self, skt, fc, call=False):
        skt = BlockSocket.unwrap(skt)
        ind = id(skt)
        if call:
            fc = fc(skt, ind)
        self.datas[ind] = (skt, fc)
        return ind
    def remove(self, ind):
        del self.datas[ind]
    def call(self):
        skts = [k[0] for k in self.datas.values() if not k[0]._closed]
        #self.log.debug(f"[TESTZ] skts: {skts}")
        (rlist,wlist,elist)=select.select(skts,[],[],self.wait_sec)
        for skt in rlist:
            ind = id(skt)
            if ind in self.datas:
                self.datas[ind][1]()

pass
