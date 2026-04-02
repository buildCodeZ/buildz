
from buildz.base import Base
from .util import *
class Upsample(Base):
    def init(self, dims, size=None, scale_factor=None, mode='nearest'):
        self.dims = dims
        assert size is not None or scale_factor is not None
        self.size= exp(size, dims)
        self.scale_factor=exp(scale_factor, dims)
        self.mode=mode
    def fetch(self, shape):
        if type(shape)==int:
            shape = [shape]
        shape = list(shape)
        while len(shape)<self.dims+2:
            shape = [1]+shape
        batch = shape[0]
        ch = shape[1]
        return batch, ch, shape[2:]
    def cache(self, shape, unit=1):
        if self.mode=='nearest':
            return 0
        n = mul(shape)
        return n*unit
    def cal(self, shape):
        oshape = self.out(shape)
        batch, ch, oszs = self.fetch(oshape)
        n = 4*batch*ch*mul(oszs)
        return n
    def backcal(self, shape):
        return self.cal(batch)
    def size(self, unit=1):
        return 0
    def out(self, shape):
        batch, ch, szs = self.fetch(shape)
        if self.size:
            osz = list(self.size)
        else:
            osz = [int(sz/sf) for sz, sf in zip(self.size, self.scale_factor)]
        return [batch, ch]+osz
