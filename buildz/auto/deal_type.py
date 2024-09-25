
from .. import xf
from .. import ioc
from ..base import Base
from ..ioc import wrap
class DealType(Base):
    def init(self, deals = {}):
        self.deals = deals
    def call(self, data):
        if type(data)==str:
            data = xf.loadf(data)
        _type = xf.g(data, type = None)
        return self.deals[_type](data)

pass

@wrap.obj(id = "def.deal.type")
@wrap.obj_args("ioc, confs")
class DefDeal(Base):
    def init(self, mg):
        self.mg = mg
    def call(self, maps, fp):
        conf = xf.get(maps, "def.deal", None)
        factory_id = xf.g(conf, factory="buildz.auto.deal.fill")
        factory = self.mg.get(factory_id)
        data = xf.g(conf, types={})
        rst = {}
        for _type, calls in data.items():
            rst[_type] = factory(calls)
        obj = DealType(rst)
        maps['deal_obj'] = obj
        return True

pass
