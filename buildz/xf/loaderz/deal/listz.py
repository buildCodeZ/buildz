from .. import base
from .. import item
from .. import exp
from . import lr
class ListDeal(lr.LRDeal):
    """
        分隔符，有分隔符后将缓存的数据当作字符串
    """
    def init(self, left, right):
        super().init(left, right, 'list')
    def build(self, arr):
        rst = []
        for _item in arr:
            if not _item.is_val:
                raise Exception("error in list:"+_item)
            rst.append(_item.val)
        return item.Item(rst, type='list', is_val = 1)

pass