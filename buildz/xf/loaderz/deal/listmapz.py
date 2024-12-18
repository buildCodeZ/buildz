from .. import base
from .. import item
from .. import exp
from . import lr
from buildz import Base
class Args(Base):
    def str(self):
        return f"<Args args={self.args}, maps={self.maps}>"
    @property
    def lists(self):
        return self.args
    @lists.setter
    def lists(self, val):
        self.args=val
    @lists.deleter
    def lists(self):
        del self.args
    @property
    def dicts(self):
        return self.maps
    @dicts.setter
    def dicts(self, val):
        self.maps=val
    @dicts.deleter
    def dicts(self):
        del self.maps
    def init(self, args, maps):
        self.args = args
        self.maps = maps

pass
class ListMapDeal(lr.LRDeal):
    """
        分隔符，有分隔符后将缓存的数据当作字符串
    """
    def init(self, left, right, as_map = False, as_args=False):
        super().init(left, right, "listmap")
        self.as_map = as_map
        self.as_args = as_args
    def types(self):
        return ['list']
    def build(self, obj):
        # if self.check_right(obj):
        #     return None
        val = obj.val
        if len(val)==0:
            obj.val = []
            obj.is_val = 1
            return obj
        return self.build_arr(val)
    def build_arr(self, arr):
        rst = {}
        lst = []
        mp = {}
        i = 0
        while i<len(arr):
            obj = arr[i]
            opt = None
            if i+1<len(arr):
                opt = arr[i+1]
            if opt is not None and opt.type == 'kv':
                if i+2>=len(arr):
                    raise Exception(f"u f in listmap: {arr}")
                val = arr[i+2]
                mp[obj.val]=val.val
                i+=3
            else:
                lst.append(obj.val)
                i+=1
        if self.as_args:
            return item.Item(Args(lst, mp), type='args', is_val=1)
        if len(mp)==0:
            if self.as_map:
                if len(lst)==0:
                    return item.Item(mp, type="map", is_val=1)
                else:
                    return item.Item(Args(lst, mp), type='args', is_val=1)
            return item.Item(lst, type="list", is_val=1)
        elif len(lst)==0:
            return item.Item(mp, type="map", is_val=1)
        else:
            return item.Item(Args(lst, mp), type='args', is_val=1)

pass