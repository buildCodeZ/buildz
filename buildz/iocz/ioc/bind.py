#
from buildz import Base

class Bind(Base):
    def init(self):
        self.mg = None
        self.binds = []
    def add_bind(self, fc):
        self.binds.append(fc)
    def bind(self, mg):
        self.mg = mg
        _ = [fc(mg) for fc in self.binds]

pass