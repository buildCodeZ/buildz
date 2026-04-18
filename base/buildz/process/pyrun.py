#

from ..base import Base
from .. import xf, dz, pyz, args as argx
class Runner(Base):
    """
        作为子进程实例运行用的
        python -m buildz.process.pyrun confpath
    """
    def run(self, fc, args, stdin, stdout, stderr):
        import sys
        self.argv = sys.argv
        self.stdin = sys.stdin
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        sys.argv = args
        sys.stdin = stdin
        sys.stdout = stdout
        sys.stderr = stderr
        if type(fc)==str:
            fc = pyz.load(fc)
        if callable(fc):
            fc()
    def call(self):
        conf = self.fetch()
        confpath = conf.get("confpath")
        conf = xf.loadf(confpath)
        
        pass
    def init(self):
        args = xf.loads(r"""
        [confpath]
        {
            cf: confpath
        }
        ()
        """)
        self.fetch = argx.Fetch(*args)

def test():
    import sys
    fp = sys.argv[1]
    lst = FcFpsListener()
    runner = Runner(fp, lst)
    lst.run()

pass
pyz.lc(locals(), test)