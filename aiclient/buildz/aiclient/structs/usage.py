
from buildz.base import Base
from buildz import log as logz, dz, xf
from typing import List, Dict, Any, Optional
class Usage(Base):
    def init(self, send=0, recv=0, total=0):
        self.send=send
        self.recv =recv
        self.total = total or (send+recv)
    @staticmethod
    def from_conf(self, conf):
        send, recv, total = dz.g(conf, send=0, recv=0, total=0)
        return Usage(send, recv, total)
    def out(self):
        return dz.maps(send=self.send, recv=self.recv, total=self.total)
