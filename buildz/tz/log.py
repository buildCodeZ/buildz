#


from .. import xf
from .. import ioc
from ..base import Base
from ..ioc import wrap
from ..tools import *
import time, sys
class Log(Base):
    def init(self, shows = None):
        if shows is None:
            shows = ["info", "debug", "warn", "error"]
        self.shows=shows
    def log(self, level, *args):
        raise Exception("unimpl")
    def info(self, *args):
        if "info" not in self.shows:
            return
        self.log("INFO", *args)
    def warn(self, *args):
        if "warn" not in self.shows:
            return
        self.log("WARN", *args)
    def debug(self, *args):
        if "debug" not in self.shows:
            return
        self.log("DEBUG", *args)
    def error(self, *args):
        if "error" not in self.shows:
            return
        self.log("ERROR", *args)

pass
class FpLog(Log):
    def init(self, fp = None,shows =None):
        super().init(shows)
        self.fp = fp
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

pass
