
'''
单元测试注解
'''
from ..base import Base,fcBase
from .. import logz
import traceback
class UnitTest(Base):
    def init(self, log=None):
        self.tests = []
        self.log = logz.make(log)
    def case(self, key):
        key = str(key)
        def f(fc):
            self.tests.append([key, fc])
        return f
    def call(self, key = None, args=[], maps={}):
        if key is None:
            key = ''
        rst = []
        self.log.info(f"start unit test on key: {key}")
        for _key, fc in self.tests:
            if _key.find(key)==0:
                self.log.info("    unit test case: ", _key)
                try:
                    fc(*args, **maps)
                except exp:
                    import traceback
                    self.log.error("    unit test exp: ", exp)
                    self.log.error(traceback.format_exc())
                self.log.info("    done unit test case: ", _key)

pass
def build(*a,**b):
    return UnitTest(*a,**b)