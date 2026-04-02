
from buildz.base import Base
from .util import *
class MultiAttrn(Base):
    def init(self, din, dout, num_heads, bias=True):
        self.din=din
        self.dout=dout
        self.num_heads=num_heads
        self.dout_per_head = dout//num_heads
        self.bias=bias
    def fetch(self, shape):
        if type(shape)==int:
            shape = [shape]
        shape = list(shape)
        while len(shape)<3:
            shape = [1]+shape
        din = shape[2]
        seq_n = shape[1]
        batch = shape[0]
        return batch, seq_n, din
    def cache(self, shape, unit=1):
        batch, seq_n, din = self.fetch(shape)
        n_input = 3*batch*seq_n*din
        n_w = 2*batch*self.num_heads*seq_n*seq_n
        n = n_input+n_w
        return n*unit
    def cal(self, shape):
        batch, seq_n, din = self.fetch(shape)
        n = 6*batch*seq_n*din*self.dout+2*batch*self.num_heads*seq_n*seq_n*self.dout_per_head+2*batch*seq_n*self.dout*self.dout
        return n
    def backcal(self, shape):
        return 2*self.cal(shape)
    def size(self, unit=1):
        kqv = 3*(self.din*self.dout+self.dout*self.bias)
        out = self.dout*self.dout+self.dout*self.bias
        n = kqv+out
        return n*unit
    def out(self, shape):
        batch, seq_n, din = self.fetch(shape)
        return [batch, seq_n, self.dout]

pass