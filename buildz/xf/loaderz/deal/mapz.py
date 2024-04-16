from .. import base
from .. import item
from .. import exp
from . import lr
class MapDeal(lr.LRDeal):
    """
        分隔符，有分隔符后将缓存的数据当作字符串
    """
    def init(self, left, right):
        super().init(left, right, "map")
    def build(self, arr):
        rst = {}
        if len(arr)%3!=0:
            raise Exception(f"u f in map: {arr}")
        for i in range(0, len(arr), 3):
            k = arr[i]
            v = arr[i+2]
            opt = arr[i+1]
            if opt.type != "kv":
                raise Exception(f"u f opt in map: {opt}")
            rst[k.val] = v.val
        return item.Item(rst, type='map', is_val = 1)

pass