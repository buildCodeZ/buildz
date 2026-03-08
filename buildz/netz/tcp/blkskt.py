
from .block import Block

class BlockSocket:
    def __init__(self, skt):
        self.skt = skt
        self.blk = Block()
    def send(self, bts):
        self.skt.send(self.blk.wrap(bts))
    def recv(self, size=1024):
        while True:
            bts = self.skt.recv(size)
            bts, ch = self.blk.get(bts)
            if len(bts)>0 or ch==0:
                break
        return bts
