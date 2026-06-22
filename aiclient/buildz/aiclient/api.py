
from buildz.base import Base
from buildz import xf, fz, dz
from .struct import *
class Api(Base):
    def init(self, conf:dict):
        pass
    def send(self, send:Send)->tuple[Message, Usage]:
        send = send.out()
        rst, usg = self.send_dict(send)
        return Recv.from_dict(rst), Usage.from_dict(usg)
    def send_dict(self, send:dict)->tuple[dict, dict]:
        return None, None
