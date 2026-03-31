
from buildz.base import Base
from .util import *
class Linear(Base):
    def init(self, din, dout, bias=True):
        self.din=din
        self.dout=dout
        self.bias=bias
    def fetch(self, shape):
        if type(shape)==int:
            shape = [shape]
        shape = list(shape)
        if len(shape)<2:
            shape = [1]+shape
        # print(f"shape:{shape}")
        din = shape[-1]
        batch = mul(shape[:-1])
        return batch, din
    def cache(self, shape, unit=1):
        batch, din = self.fetch(shape)
        return (batch*self.din+self.din*self.dout)*unit
    def cal(self, shape):
        batch, din = self.fetch(shape)
        return 2*batch*self.din*self.dout
    def backcal(self, shape):
        return 2*self.cal(shape)
    def size(self, unit=1):
        n = self.din*self.dout+self.bias*self.dout
        return n*unit
    def out(self, shape):
        batch, din = self.fetch(shape)
        return [batch, self.dout]
