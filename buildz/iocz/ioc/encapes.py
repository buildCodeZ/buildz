#
from .tdata import TData
from .datas import Datas
from .dataset import Dataset
class Encpaes(Datas):
    def init(self, confs, deals, id=None, ns=None, dts=None):
        super().init(id, ns, dts)
    def tget(self, key, src=None,id=None, gfind=True):
class Encapeset(Dataset):
    '''
        生成对象前的中间层
    '''
    def init(self, ids, confs, deals):
        super().init(ids)
        self.confs = confs
        self.deals = deals
    def pub_get(self, key, ns=None, id=None):
        obj, find = super().get(key, ns, id)

    def ns_get(self, key, ns=None, deal_ns=None):
        map = dz.get_set(self.ns, ns, dict())
        if key not in map:
            return None, 0
        return map[key], 1

    