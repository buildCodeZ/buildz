from buildz import Base, xf, dz
from . import argz
from . import evalx
class Fc(Base):
    def str(self):
        return str(self.fc)
    def init(self, fc=None):
        self.fc = fc
    def call(self, params):
        return self.fc(*params.args, **params.maps), 1
    @staticmethod
    def make(fc):
        if isinstance(fc, Fc):
            return fc
        return Fc(fc)
class RetFc(Fc):
    def call(self, params):
        return (params.args, params.maps), 1
class Call(Fc):
    def str(self):
        return str(self.fcs)
    def init(self, fc, args=None, eval=None):
        if not dz.islist(fc):
            fc = [fc]
        fc = [self.make(k) for k in fc]
        self.fcs = fc
        self.args = args
        self.eval = eval
    def call(self, params):
        if self.eval is not None:
            if not self.eval(params):
                return None,0
        if self.args is not None:
            params = self.args(params)
        try:
            rst = None,0
            for fc in self.fcs:
                val,mark_call = fc(params)
                if mark_call:
                    rst = val, mark_call
            return rst
        except argz.ArgExp as exp:
            if self.args is not None:
                exp = self.args.deal_exp(exp)
            raise exp
    def add(self, fc):
        self.fcs.append(self.make(fc))