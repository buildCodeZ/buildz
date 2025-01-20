
def arr_pos(arr):
    if len(arr)==0:
        return (0,0)
    return (arr[0].pos[0], arr[-1].pos[-1])
class BaseDeal:
    def arr_pos(self, arr):
        return arr_pos(arr)
    def has_prev(self):
        return 1
    def has_deal(self):
        return 1
    def labels(self):
        return []
    def types(self):
        return []
    def prepare(self, msg):
        pass
    def regist(self, mgs):
        if self._id is None:
            self._id = mgs.regist()
        self.prepare(mgs)
    def id(self):
        return self._id
    def __str__(self):
        return "BaseDeal"
    def __repr__(self):
        return str(self)
    def __init__(self, *argv, **maps):
        self._id = None
        self.init(*argv, **maps)
    def init(self, *argv, **maps):
        pass
    def deal(self, buffer, rst, mg):
        pass
    def build(self):
        pass

pass

