
from buildz.base import Base
from .util import *
class Reshape(Base):
    def init(self, shape, cal_batch=False):
        self.shape = shape
        self.cal_batch = cal_batch
        self.shape_size = 0
        if cal_batch:
            self.shape_size = mul(shape)
    def cache(self, shape, unit=1):
        return 0
    def cal(self, shape):
        return 0
    def backcal(self, shape):
        return 0
    def size(self, unit=1):
        return 0
    def out(self, shape):
        if self.cal_batch:
            isize = mul(shape)
            n = isize//self.shape_size
            shape = [n]+list(self.shape)
        else:
            shape = self.shape
        return shape
