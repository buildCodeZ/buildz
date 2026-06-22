
from .block import Block
from ..._dz.lists import Lists
from threading import get_ident as gid
from ... import dz
def v2bs(obj):
    import json
    rs = json.dumps(obj, ensure_ascii=False)
    return rs.encode("utf-8")
def bs2v(bs):
    import json
    s = bs.decode("utf-8")
    obj = json.loads(s)
    return obj

class BlockSocket:
    def out(self):
        return self.skt, self.blk.out()
    @staticmethod
    def wrap(skt, reset=True):
        #print(f"[BS] wrap skt: {skt}, reset: {reset}")
        if isinstance(skt, BlockSocket):
            #print(f"[BS] is inst")
            if reset:
                skt.reset_lists()
            return skt
        #print(f"[BS] not inst and new")
        return BlockSocket(skt)
    def enable_v2bs(self):
        if not self.mark_v2bs:
            self.adds("v2bs",True,send=dz.val2bs, recv=dz.bs2val) 
            self.mark_v2bs=1
        else:
            self.enable("v2bs")
    def disable_v2bs(self):
        self.disable("v2bs")
    def enable_json(self):
        if not self.mark_js:
            self.adds("json",True,send=v2bs, recv=bs2v) 
            self.mark_js=1
        else:
            self.enable("json")
    def disable_json(self):
        self.disable("json")
    def reset_lists(self):
        self.mark_js = 0
        self.mark_v2bs = 0
        self.lists = Lists(send=-1, recv=1)
        for k in "add,adds,enable,disable".split(","):
            setattr(self, k, getattr(self.lists, k))
    def __init__(self, skt, caches = None):
        self.skt = skt
        self.mark_js = 0
        self.mark_v2bs = 0
        # 数据流入流出前预处理流程
        self.reset_lists()
        self.blk = Block(caches)
    def close(self):
        self.skt.close()
    def send(self, bts):
        #print(f"[{gid()}][BlockSocket][{self}] send: {len(bts)}")
        bts = self.lists.send(bts)
        #print(f"[{gid()}][BlockSocket][{self}] done lists.send: {len(bts)}")
        dt=self.blk.wrap(bts)
        #print(f"[{gid()}][BlockSocket][{self}] before send: {len(dt)}")
        self.skt.send(dt)
        #print(f"[{gid()}][BlockSocket][{self}] done send: {len(dt)}")
    def recv(self, size=1024*1024*10):
        #print(f"[{gid()}][BlockSocket][{self}] before recv")
        bts, ch = self.blk.get()
        while len(bts)==0:
            #print(f"[{gid()}][BlockSocket][{self}] loop init {self.blk.size()}") 
            bts = self.skt.recv(size)
            if len(bts)==0:
                return bts
            #print(f"[{gid()}][BlockSocket][{self}] loop recv: {len(bts)}") 
            bts, ch = self.blk.get(bts)
            #print(f"[{gid()}][BlockSocket][{self}] loop get: {len(bts), ch, self.blk.size()}") 
            if len(bts)>0 or ch==0:
                break
        #print(f"[{gid()}][BlockSocket][{self}] recv: {len(bts)}")
        bts = self.lists.recv(bts)
        #print(f"[{gid()}][BlockSocket][{self}] after lists.recv: {len(bts)}")
        return bts
