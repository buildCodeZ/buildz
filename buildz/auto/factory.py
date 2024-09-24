#

from .. import xf
from .. import ioc
from ..base import Base
from ..ioc import wrap

class DeepFc(Base):
    def init(self, fcs):
        self.fc = fcs[0]
        if len(fcs)>1:
            self.next = DeepFc(fcs[1:])
        else:
            self.next = None
    def call(self, data):
        return self.fc(data, self.next)

pass
@wrap.obj(id = "buildz.auto.deal.fill")
@wrap.obj_args("ioc, confs")
class Fill(Base):
    def init(self, mg):
        self.mg = mg
    def call(self, orders):
        fcs = [self.mg.get(id) for id in orders]
        return DeepFc(fcs)

pass