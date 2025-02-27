#

from buildz import iocz

from buildz import xf, pyz, Base

class Test(Base):
    def str(self):
        return f'Test<{id(self)}>(id={self.id})'
    def init(self, id=0):
        super().init()
        self.id = id
    def call(self):
        print("Test.show:", self)

pass
confs = r"""
confs.pri: {
    deal_obj:{
        type=deal
        src=buildz_bak.iocz.conf_deal.obj.ObjectDeal
        deals: [obj,object]
        call=1
    }
    deal_val:{
        type=deal
        src=buildz_bak.iocz.conf_deal.val.ValDeal
        deals: [val,value]
        call=1
    }
    deal_ref: {
        type:deal
        src:buildz_bak.iocz.conf_deal.ref.RefDeal
        deals: ref
        call=1
    }
    deal_ioc: {
        type:deal
        src:buildz_bak.iocz.conf_deal.ioc.IOCDeal
        deals: ioc
        call=1
    }
}
builds: [deal_obj,deal_val,deal_ref,deal_ioc]
"""
confs1 = r'''
ns: xxx
envs: {
    a=0
    b=1
}
confs.ns: [
    [[obj, test1], <buildz>.iocz.conf.test.Test, [],{id=[ioc]}]
    {
        id=test
        type=obj
        source=<buildz>.iocz.conf.test.Test
        single=1
        args=[
            [ref, test1]
        ]
    }
]
'''.replace("<buildz>", "buildz")
def get_env_sys(self, id, sid=None):
    sysdt = os.getenv(id)
    return sysdt
def test():
    mg = iocz.build()
    print(mg)
    #unit = mg.add_conf(confs)
    unit = mg.add_conf(confs1)
    with mg.push_vars({"test": 123}):
        it, find = unit.get("test")
        print(f"it: {it, id(it)}, find: {find}")
    it, find = unit.get("test")
    print(f"it: {it, id(it)}, find: {find}")
    it, find = mg.get("test", "xxx")
    print(f"it: {it, id(it)}, find: {find}")
    print(f"env: {unit.get_env('b')}")
    print(type(it))
    it = Test(123)
    print(type(it))
    print(it)
    exit()

pyz.lc(locals(), test)