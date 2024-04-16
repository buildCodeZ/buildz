from .. import base


class PrevNextDeal(base.BaseDeal):
    def labels(self):
        return ['']
    def types(self):
        return [""]
    def build(self, obj):
        obj.is_val = 1
        return obj
    """
        读取下一个字符放缓存里，应放最低优先级
    """
    def deal(self, buffer, arr, mg):
        c = buffer.read_cache(1)
        if len(c)==0:
            return False
        return True

pass