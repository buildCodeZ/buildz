from .. import xf
from .. import ioc
from ..base import Base
from . import init
class Run(Base):
    def init(self, fps=None):
        mg = ioc.build()
        if fps is not None:
            mg.add_fps(fps)
        self.mg = mg
    def call(self, fp):
        maps = xf.loadf(fp)
        calls = xf.g(maps, calls = [])
        for deal in calls:
            fc = self.mg.get(deal)
            if not fc(maps, fp):
                break

pass

