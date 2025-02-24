
from buildz.iocz.ioc import *
from buildz.iocz.ioc_deal import obj
from buildz import xf, pyz, Base
class Test(Base):
    def init(self, id=0):
        self.id = id

pass
def test():
    conf = xf.loads(r"""
    type=obj
    source=buildz.iocz.ioc.test.Test
    single=0
    args=[
        {
            type=obj
            source = buildz.iocz.ioc.test.Test
            maps={id=123}
        }
    ]
    """)
    mg = Manager('.', 'type')
    print(mg)
    unit = mg.create()
    print(unit)
    deal_obj = obj.ObjectDeal()
    mg.set_deal('obj', deal_obj)
    unit.set_conf("test",conf)
    encape, tag, find = mg.get_encape("test")
    print(f"encape: {encape}")
    it = encape()
    print(f"obj: {id(it), id(it.id),it.id.id}")
    it = encape()
    print(f"obj: {id(it), id(it.id),it.id.id}")

pyz.lc(locals(), test)