
from buildz import ioc

from buildz import xf, pyz, Base
class Test(Base):
    def init(self, id=0):
        self.id = id

pass
def test():
    conf = xf.loads(r"""
    [
        {
            id=test
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
        }
    ]
    """)
    mg = ioc.build()
    mg.add(conf)
    print(mg)
    it = mg.get("test")
    print(f"obj: {id(it), id(it.id),it.id.id}")
    it = mg.get("test")
    print(f"obj: {id(it), id(it.id),it.id.id}")

pyz.lc(locals(), test)