
from buildz.base import Base
from buildz import log as logz, dz, xf
from typing import List, Dict, Any, Optional
class Usage(Base):
    '''
        单次api调用的开销，包括：
        send: 发送的token数
        recv: 返回的token数
        total: 总token数
        用来分析或计算开销
    '''
    def init(self, send=0, recv=0, total=0):
        self.send=send
        self.recv =recv
        self.total = total or (send+recv)
    @staticmethod
    def from_conf(conf):
        send, recv, total = dz.g(conf, send=0, recv=0, total=0)
        return Usage(send, recv, total)
    def out(self):
        return dz.maps(send=self.send, recv=self.recv, total=self.total)
    def str(self):
        return str(self.out())
