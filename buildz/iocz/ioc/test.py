
from buildz.iocz.ioc import *
from buildz.iocz.ioc_deal import obj, deal
from buildz import xf, pyz, Base
class Test(Base):
    def init(self, id=0):
        self.id = id

pass
conf_obj = xf.loads(r"""
type=obj
source=buildz.iocz.ioc.test.Test
args=[
    {
        type=obj
        source = buildz.iocz.ioc.test.Test
        maps={id=123}
    }
]
""")
conf_init = xf.loads(r"""
type=deal
source=buildz.iocz.ioc_deal.obj.ObjectDeal
deals: obj
call=1
""")
def test():
    mg = Manager('.', 'type')
    mg.set_deal("deal", deal.DealDeal())
    print(mg)
    unit = mg.create()
    print(unit)
    #deal_obj = obj.ObjectDeal()
    #mg.set_deal('obj', deal_obj)
    unit.set_conf("test",conf_obj)
    unit.set_conf("deal_obj",conf_init)
    unit.add_build("deal_obj")
    encape, tag, find = mg.get_encape("test")
    print(f"encape: {encape}")
    it = encape()
    print(f"obj: {id(it), id(it.id),it.id.id}")
    it = encape()
    print(f"obj: {id(it), id(it.id),it.id.id}")

pyz.lc(locals(), test)