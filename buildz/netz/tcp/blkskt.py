
from .block import Block

class BlockSocket:
    def __init__(self, skt):
        self.skt = skt
        self.blk = Block()
    def send(self, bts):
        dt=self.blk.wrap(bts)
        #print(f"[BlockSocket] send: {len(dt)}")
        self.skt.send(dt)
    def recv(self, size=1024):
        bts, ch = self.blk.get()
        if len(bts)>0:
            return bts
        while True:
            #print(f"[BlockSocket] loop init") 
            bts = self.skt.recv(size)
            #print(f"[BlockSocket] loop recv: {len(bts)}") 
            bts, ch = self.blk.get(bts)
            #print(f"[BlockSocket] loop get: {len(bts), ch}") 
            if len(bts)>0 or ch==0:
                break
        #print(f"[BlockSocket] recv: {len(bts)}")
        return bts
