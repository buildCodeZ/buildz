#


from .. import xf
from .. import ioc
from ..base import Base
from ..ioc import wrap
from ..tools import *
import time, sys
@wrap.obj(id="log")
class Log(Base):
    def init(self):
        self.fp = None
    def log(self, level, *args):
        args = [str(k) for k in args]
        msg = " ".join(args)
        date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        msg = f"[{level}] {date} {msg}\n"
        sys.stdout.write(msg)
        if self.fp is not None:
            fp = time.strftime(self.fp)
            fz.makefdir(fp)
            fz.write(msg.encode("utf-8"), fp, 'ab')
    def info(self, *args):
        self.log("INFO", *args)
    def warn(self, *args):
        self.log("WARN", *args)
    def debug(self, *args):
        self.log("DEBUG", *args)
    def error(self, *args):
        self.log("ERROR", *args)
    def call(self, maps, fp):
        fp = xf.g(maps, log = None)
        self.fp = fp
        return True

pass
