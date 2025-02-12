from ..base import *
basepath = path
path = pathz.Path()
path.set("conf", basepath.local("ioc/conf"), curr=0)

class Creater(Base):
    def init(self):
        self.mg = None
    def bind(self, mg):
        self.mg = mg
    def call(self, *a, **b):
        return None

pass