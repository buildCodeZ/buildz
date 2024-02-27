
from . import buffer
from . import base
from . import pos
from . import exp
class Manager:
    def fcs(self, fc, *args, **maps):
        return fc(*self.cs(*args), **maps)
    def add_fc(self, fc, *args, **maps):
        obj = self.fcs(fc, *args, **maps)
        self.add(obj)
        return self
    def cs(self, *args):
        return [self.c(k) for k in args]
    def c(self, s):
        if self.bts:
            s = s.encode(self.code)
        return s
    def add(self,obj):
        #obj.init()
        obj.regist(self)
        self.prevs.append(obj.prev)
        self.deals.append(obj.deal)
        return self
    def do(self, fcs, *argv, **maps):
        for fc in fcs:
            if fc(*argv, **maps):
                return True
        return False
    def regist(self):
        id = self.index
        self.index+=1
        return "id_"+str(id)
    def __init__(self):
        self.index = 0
        self.deals = []
        self.prevs = []
    def load(self, reader):
        buff = buffer.Buffer(reader)
        _pos = pos.PosCal()
        queue = []
        self.pos = _pos
        self.buffer = buff
        self.queue = queue
        while self.do(self.prevs, buff, queue, _pos):
            pass
        stack = []
        while self.do(self.deals, queue, stack):
            pass
        if len(stack)==0:
            raise Exception("ERROR not data")
        for _item in stack:
            if not _item.check(is_val=1):
                raise exp.FormatExp("format error found", _item.pos)
        if len(stack)==1:
            return stack[0].val
        else:
            return [it.val for it in stack]

pass
