
from buildz.base import Base
from buildz import xf, fz, dz
from .struct import *
from buildz import log as logz
'''
    只是一个接口，说明实现该接口需要实现的方法
    实际的api调用在apis文件夹中
'''
class Api(Base):
    def init(self, log=None):
        self.log = log or logz.simple()
        self.log = self.log("api")
        pass
    def send(self, send:Send)->tuple[Message, Usage]:
        send = send.out()
        self.log.debug(f"send: {send}")
        rst, usg = self.send_dict(send)
        self.log.debug(f"recv: {rst}")
        return Recv.from_conf(rst), Usage.from_conf(usg)
    def send_dict(self, send:dict)->tuple[dict, dict]:
        return None, None
    def embed(self, msg:str, model:str)->list[float]:
        return None
