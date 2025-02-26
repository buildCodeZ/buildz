#

from buildz.iocz.conf.mg import ConfManager

from buildz.iocz.ioc import *
from buildz.iocz.ioc_deal import obj, deal
from buildz import xf, pyz, Base

class Test(Base):
    def init(self, id=0):
        self.id = id

pass
confs = r"""
confs.pri: {
    deal_obj:{
        type=deal
        source=buildz.iocz.ioc_deal.obj.ObjectDeal
        deals: obj
        call=1
    }
}
confs: [
    {
        id=test
        type=obj
        source=buildz.iocz.ioc.test.Test
        args=[
            {
                type=obj
                source = buildz.iocz.ioc.test.Test
                maps={id=123}
            }
        ]
    }
]
builds: [deal_obj]
"""
def test():
    mg = ConfManager()
    mg.set_deal("deal", deal.DealDeal())
    print(mg)
    unit = mg.add_conf(confs)
    encape, tag, find = mg.get_encape("test")
    print(f"encape: {encape}")
    it = encape()
    print(f"obj: {id(it), id(it.id),it.id.id}")
    it = encape()
    print(f"obj: {id(it), id(it.id),it.id.id}")

pyz.lc(locals(), test)