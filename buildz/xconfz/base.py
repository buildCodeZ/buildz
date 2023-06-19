#coding=utf-8

class FormatExp(Exception):
    def __init__(self, err, data, s = ""):
        if len(s)==0:
            errs = "Error: {err}, line: {line}, index: {index}".format(err = err, line = data[0], index = data[1])
        else:
            errs = "Error: {err}, line: {line}, index: {index}, content: [{s}]".format(err = err, line = data[0], index = data[1], s = s)
        super(FormatExp, self).__init__(errs)

pass

class Item:
    def __str__(self):
        return "<item val={val}, type = {type}, pos = {pos}>".format(val = str(self.val), type = str(self.type), pos = str(self.pos))
    def __repr__(self):
        return str(self)
    def __init__(self, val, pos, remain=None, type = None):
        self.val= val
        self.pos= pos
        self.remain= remain
        self.type = type

pass

"""
1,使用框架
2，字符串+index
"""
class Buffer:
    def pos_remain(self):
        return 0,0
    def pos_curr(self):
        return 0,0
    def pos(self):
        return 0,0
    def curr(self, size = 1):
        return ""
    def remain_size(self):
        return 0
    def remain(self):
        return ""
    def full(self, size = 1):
        return self.remain()+self.curr(size)
    def deal_remain(self):
        pass
    def deal2curr(self, size=1):
        pass
    def add_remain(self,size=1):
        return False

pass

def is_key(val):
    return isinstance(val, Key)

pass

class Key:
    @staticmethod
    def is_inst(val):
        return isinstance(val, Key)
    def __init__(self, c):
        self.c = c
    def __str__(self):
        return "[key "+str(self.c)+"]"
    def __eq__(self, obj):
        return self(obj)
    def __repr__(self):
        return str(self)
    def equal(self, obj):
        return self(obj)
    def __call__(self, obj):
        if type(obj)!= Key:
            return False
        return obj.c == self.c

pass
class KeyVal:
    def __repr__(self):
        return str(self)
    def __str__(self):
        return "[keyval {key}:{val}]".format(key = str(self.key), val = str(self.val))
    @staticmethod
    def is_inst(val):
        return isinstance(val, KeyVal)
    def __init__(self, key, val):
        self.key = key
        self.val= val

pass
class Reg:
    def __init__(self):
        self.index = 0
        self.sets = set()
        self.keys = {}
    def __call__(self, key):
        if key in self.keys:
            return self.keys[key]
        #if key in self.keys:
        #    raise Exception("reg key already regist:"+str(key))
        self.keys[key] = Key(key)
        return self.keys[key]

pass

class BaseDeal:
    def check_curr(self, buff,  s):
        return buff.curr(len(s))==s
    def init(self, reg):
        pass
    def prev(self, buff, queue):
        return False
    def deal(self, queue, stack):
        return False

pass

class BaseOutput:
    def deal(self, data, fc):
        return ""

pass

