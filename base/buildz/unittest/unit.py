
from buildz.base import Base
from buildz import log as logz, pyz
class Unit(Base):
    def init(self, log=None):
        self.log = log or logz.simple()
        self.log = self.log("unittest")
        self.tests = []
    def add_fc(self, fc, *args, **maps):
        name = str(fc)
        return self.add(name, fc, *args, **maps)
    def add(self, name, fc, *args, **maps):
        self.tests.append([name, fc, args, maps])
    def all(self):
        passes, errors = 0,0
        total = len(self.tests)
        err_names = []
        for name, fc, args, maps in self.tests:
            rst = self.single(name, fc, *args, **maps)
            if rst is not None:
                errors+=1
                err_names.append([name, rst])
                self.log.error(f"not pass test {name}")
            else:
                passes+=1
                self.log.info(f"pass test {name}")
        self.log.info(f"total passes {passes} / {total}")
        self.log.info(f"total faileds: {errors}")
        if errors>0:
            self.log.info(f"Faileds Tests:")
            for name,err in err_names:
                self.log.info(f"    Test: {name}")
                self.log.info(f"    Error: {err}")
        return passes, errors
    def single(self, name, fc, *args, **maps):
        try:
            out = fc(*args, **maps)
            return out
        except Exception as exp:
            self.log.error(f"exp in test {name}: {exp}")
            self.log.error(f"traceback: {pyz.s_exp()}")
            return exp
    def call(self, fc=None, *args, **maps):
        if fc is None:
            return self.all()
        if type(fc)==str:
            finds = [k for k in self.tests if k[0]==fc]
            if len(finds)==0:
                return False
            name = fc
            fc, args, maps = finds[0]
        else:
            name = str(fc)
        return self.single(name, fc, *args, **maps)
