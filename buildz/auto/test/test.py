#coding=utf-8
from buildz.tools import *
from buildz.ioc import wrap
@wrap.obj(id="request")
@wrap.obj_args("ref, log", "ref, cache.modify")
class Req(Base):
    def init(self, log, upd):
        self.upd = upd
        self.log = log
    def call(self, data, fc=None):
        data = self.upd(data)
        self.log.debug(f"test data: {data}")
        if fc is not None:
            return fc(data)
        return True

pass
from buildz.auto import Run
import sys
def test():
    rst = Run()("data/test")
    print(f"rst: {rst}")

pass
pyz.lc(locals(), test)
