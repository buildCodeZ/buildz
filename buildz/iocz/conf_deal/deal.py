
from .base import *
from ..ioc_deal import deal
class DealDeal(deal.DealDeal):
    def init(self):
        super().init()
        conf = BaseConf()
        conf.index(1, 'source', need=1)
        conf.index(2, 'call')
        conf.index(3, 'tag')
        conf.key('source', 'src'.split(","), need=1)
        self.update = conf

pass