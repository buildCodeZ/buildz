
from buildz.base import Base
from .util import *
class Reshape(Base):
    def init(self, shape):
        self.shape = shape
    def cache(self, shape, unit=1):
        return 0
    def cal(self, shape):
        return 0
    def backcal(self, shape):
        return 0
    def size(self, unit=1):
        return 0
    def out(self, shape):
        return self.shape
