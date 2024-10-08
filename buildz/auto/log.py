#


from .. import xf
from .. import ioc
from ..base import Base
from ..ioc import wrap
from ..tools import *
import time, sys
from ..tz.log import FpLog
@wrap.obj(id="log")
class AutoLog(FpLog):
    def call(self, maps, fp):
        fp = xf.g(maps, log = None)
        self.fp = fp
        shows = xf.get(maps, "log.shows")
        if shows is None:
            shows = ["info", "warn", "error"]
        self.shows = shows
        return True

pass
