
from .base import *
from ..ioc_deal import ref
class RefDeal(ref.RefDeal):
    def init(self):
        super().init()
        conf = BaseConf()
        conf.index(1, 'ref', need=1)
        conf.index(2, 'default')
        conf.key('ref', 'key,data'.split(","), need=1)
        self.update = conf

pass