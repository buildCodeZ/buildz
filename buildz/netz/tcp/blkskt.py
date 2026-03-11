
from .block import Block
from ..._dz.lists import Lists
# from threading import get_ident as gid
class BlockSocket:
    def __init__(self, skt):
        self.skt = skt
        self.lists = Lists('send', 'recv')
        for k in "add,adds,enable,disable".split(","):
            setattr(self, k, getattr(self.lists, k))
        self.blk = Block()
    def send(self, bts):
        bts = self.lists.send(bts)
        dt=self.blk.wrap(bts)
        #print(f"[{gid()}][BlockSocket] before lists.send")
        #print(f"[{gid()}][BlockSocket] send: {len(dt)}")
        self.skt.send(dt)
    def recv(self, size=1024):
        bts, ch = self.blk.get()
        while len(bts)==0:
            #print(f"[{gid()}][BlockSocket] loop init") 
            bts = self.skt.recv(size)
            #print(f"[{gid()}][BlockSocket] loop recv: {len(bts)}") 
            bts, ch = self.blk.get(bts)
            #print(f"[{gid()}][BlockSocket] loop get: {len(bts), ch}") 
            if len(bts)>0 or ch==0:
                break
        #print(f"[{gid()}][BlockSocket] recv: {len(bts)}")
        bts = self.lists.recv(bts)
        #print(f"[{gid()}][BlockSocket] after lists.recv: {len(bts)}")
        return bts
