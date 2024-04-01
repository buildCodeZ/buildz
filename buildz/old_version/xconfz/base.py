#coding=utf-8

from ..base import Map
'''
格式化报错
'''
class FormatExp(Exception):
    def __init__(self, err, data, s = ""):
        if len(s)==0:
            errs = "Error: {err}, line: {line}, index: {index}".format(err = err, line = data[0], index = data[1])
        else:
            errs = "Error: {err}, line: {line}, index: {index}, content: [{s}]".format(err = err, line = data[0], index = data[1], s = s)
        super(FormatExp, self).__init__(errs)

pass

'''
数据封装类
val是数据（字符）值
pos是字符在文件里的位置(第几行第几列)
remain和type？
'''
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
文本缓存类
位置都是（行，列）
方法名写的有点乱
remain是未处理数据，curr是当前数据，未处理数据在当前数据之前
一种弱约束，remain里的应该当作数据，curr里用来判断是否是符号，不是则加到remain里
"""
class Buffer:
    def pos_remain(self):
        '''
        前置指针在字符串的位置
        '''
        return 0,0
    def pos_curr(self):
        '''
        当前指针在字符串的位置
        '''
        return 0,0
    def pos(self):
        '''
        不记得这是啥
        '''
        return 0,0
    def curr(self, size = 1):
        '''
        返回当前指针开始，长度为size的字符串
        '''
        return ""
    def remain_size(self):
        '''
        前置指针到当前指针的数据量
        '''
        return 0
    def remain(self):
        '''
        返回前置数据
        '''
        return ""
    def full(self, size = 1):
        '''
        前置+当前数据
        '''
        return self.remain()+self.curr(size)
    def deal_remain(self):
        '''
        调用说明前置数据已经处理，前置指针移到当前指针位置
        '''
        pass
    def deal2curr(self, size=1):
        '''
        读取size字节数据，都当作已经处理（包括前置里的数据，当前指针后移size字节，前置指针移到当前指针位置）
        '''
        pass
    def add_remain(self,size=1):
        '''
        当前指针往后移，提取出来的数据放到前置中，如果剩余数据数量不到size，返回false
        '''
        return False

pass

'''
'''
def is_key(val):
    return isinstance(val, Key)

pass

'''
封装符号类
c是符号值
params是配置的其他参数，用来deal里做特殊判断或处理
'''
class Key:
    @staticmethod
    def is_inst(val):
        return isinstance(val, Key)
    def __init__(self, c, params=None):
        self.c = c
        if params is None:
            params = {}
        self.params = Map(params)
        self._params = self.params()
    @property
    def p(self):
        return self.params
    def get(self, key):
        if key not in self._params:
            return None
        return self.params[key]
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

'''
符号-数值类
'''
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

'''
符号注册，
同一个符号可以多次注册，但后面的注册返回的是最早注册生成的对象
'''
class Reg:
    def __init__(self):
        self.index = 0
        self.sets = set()
        self.keys = {}
    def exist(self, s):
        bts = type(s)==bytes
        for key in self.keys:
            val = key
            if bts:
                val = val.encode("utf-8")
            if s.find(val)>=0:
                return True
        return False
    def __call__(self, key, **params):
        if key in self.keys:
            return self.keys[key]
        #if key in self.keys:
        #    raise Exception("reg key already regist:"+str(key))
        self.keys[key] = Key(key, params)
        return self.keys[key]

pass

'''
字符串处理，分成两个阶段
一阶段prev，生成数值和符号封装对象放到列表里
二阶段deal，从列表里拿符号和数值，生成实际数据
'''
class BaseDeal:
    def check_curr(self, buff,  s):
        '''
        判断缓存当前指针字符串是否和字符串s相同
        '''
        return buff.curr(len(s))==s
    def init(self, reg):
        '''
        初始化，deal放到实际调用的场景时调用，reg用来注册符号
        '''
        pass
    def make(self, data, fc, format = False, simple = True):
        '''
        本来打算数据生成字符串用的，实际没用到
        '''
        return None
    def prev(self, buff, queue):
        '''
        处理缓存buff里的数据，放到列表queue里
        返回false说明没做处理，换下一个deal处理
        '''
        return False
    def deal(self, queue, stack):
        '''
        处理列表queue里的数据，放到堆栈stack里
        返回false说明没做处理，换下一个deal处理
        '''
        return False

pass
