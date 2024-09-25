from .. import xf,fz
from .. import ioc
from ..base import Base
from . import init
import os
class Run(Base):
    def init(self, fps=None):
        mg = ioc.build()
        if fps is not None:
            mg.add_fps(fps)
        self.mg = mg
    def add_current(self, dp):
        self.mg.get("cache").add_current(dp)
    def call(self, fp):
        self.log = self.mg.get("log")
        if not os.path.isfile(fp):
            dp = os.path.dirname(fp)
            fn = os.path.basename(fp)
            fps = fz.search(dp, fn)
            print(f"search dp:{dp}, fn: {fn}, rst: {fps}")
            if len(fps)!=1:
                self.log.error(f"can't find filepath: {fp}")
                return False
            fp = fps[0]
        maps = xf.loadf(fp)
        dp = os.path.dirname(os.path.abspath(fp))
        self.add_current(dp)
        config = self.mg.get("buildz.auto.config.load")
        if not config(maps, fp):
            return False
        calls = xf.g(maps, calls = [])
        for deal in calls:
            fc = self.mg.get(deal)
            if not fc(maps, fp):
                return False
        return True

pass

