
from buildz.base import Base
from .util import *
class Nets(Base):
    def init(self, *nets):
        self.nets = nets
    def call(self, fc, shape, *a, **b):
        rst = 0
        for net in self.nets:
            rst+= getattr(net, fc)(shape, *a, **b)
            shape = net.out(shape)
        return rst
    def cache(self, shape, unit=1):
        return self.call("cache", shape, unit)
    def cal(self, shape):
        return self.call("cal", shape)
    def backcal(self, shape):
        return self.call("backcal", shape)
    def size(self, unit=1):
        sizes = [net.size(unit) for net in self.nets]
        return sum(sizes)
        return self.call("size", shape, unit)
    def out(self, shape):
        for net in self.nets:
            shape = net.out(shape)
        return shape
