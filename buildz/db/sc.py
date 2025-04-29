#coding=utf-8
from . import runz
from .. import Base, xf


from ..sc.lst import FcFpsListener
from buildz.db import runz
class DbRunner(Base):
    def init(self, conf_fp, listener):
        self.fp = conf_fp
        self.lstn = listener
        self.lstn.set_update(self.update)
        self.lstn.set_deal_exp(self.deal_exp)
        self.reset()
    def reset(self, last_update=False):
        self.lstn.clean()
        self.lstn.add(self.fp,last_update)
        conf = xf.loadf(self.fp)
        src = xf.g(conf, src=None)
        self.lstn.add(src,last_update)
        sec = xf.g(conf, sec=0.1)
        self.lstn.set_wait(sec)
    def update(self, fps):
        self.reset(True)
        runz.test(self.fp)
    def deal_exp(self, exp, fmt_exc):
        print(f"exp: {exp}")
        print(f"traceback: \n{fmt_exc}")

pass
#runz.main()
def run():
    import sys
    fp = runz.FP
    if len(sys.argv)>1:
        fp = sys.argv[1]
    lst = FcFpsListener()
    runner = DbRunner(fp, lst)
    lst.run()

pass



