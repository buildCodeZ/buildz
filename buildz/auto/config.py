#
from .. import xf
from .. import ioc
from ..base import Base
from ..ioc import wrap
import os
@wrap.obj(id="buildz.auto.config.load")
class Config(Base):
    def call(self, maps, fp):
        configs = xf.g(maps, configs=[])
        if type(configs)!=list:
            configs = [configs]
        for cfp in configs:
            if not os.path.isfile(cfp):
                self.log.error(f"config file not exist: {cfp}")
                return False
            dt = xf.loadf(cfp)
            xf.fill(dt, maps, replace=0)
        return True

pass
#wrap.add_datas("[(env, env.buildz.auto.deal), buildz.auto.deal, auto.deal]")
@wrap.obj_args("[env, buildz.auto.deal, auto.deal]")
@wrap.obj(id="autoz.deal")
class DfDeal(Base):
    def init(self, id):
        self.id = id
    def call(self, data):
        print(f"[ERROR] implement obj with id '{self.id}' by yourself")

pass



