
from buildz.base import Base
from .util import *
class Fc(Base):
    def init(self, *a, **b):
        pass
    def cache(self, shape, unit=1):
        return mul(shape)*unit
    def cal(self, shape):
        return mul(shape)//2
    def backcal(self, shape):
        return 2*self.cal(shape)
    def size(self, unit=1):
        return 0
    def out(self, shape):
        return shape

LeakyReLU = Fc
Dropout = Fc