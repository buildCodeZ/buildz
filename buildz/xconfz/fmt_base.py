#coding=utf-8
from buildz.xconfz.base import *
"""
返回Node
"""
class BaseFormat:
    def init(self):
        return self
    def deal(self, data, fc, **params):
        return None
    def __call__(self, data, fc, **params):
        return self.deal(data, fc, **params)

pass


class FormatNode:
    def str(self):
        if self.is_leaf():
            return "<Leaf={val}>".format(val = self.value)
        else:
            cs = [str(c) for c in self.childs]
            return "<Node:{val}>".format(val = ", ".join(cs))
    def __str__(self):
        return self.str()
    def __repr__(self):
        return str(self)
    def __init__(self):
        self.init()
    def init(self):
        self.to_top = 0
        self.max_depth = 0
        self.childs = []
        self.value = None
        self.up = None
        return self
    def update_top(self, up):
        self.to_top =up.to_top+1
        if self.is_leaf():
            return
        for _node in self.childs:
            _node.update_top(self)
    def update(self, node):
        up = self
        while up is not None:
            depth = node.max_depth +1
            if depth>up.max_depth:
                up.max_depth = depth
                node, up = up, up.up
            else:
                break
    def add(self, node):
        node.update_top(self)
        self.update(node)
        self.childs.append(node)
        node.up = self
        return self
    def val(self, value):
        self.value = value
        return self
    def is_leaf(self):
        return len(self.childs)==0

pass

class SymbolFormatNode(FormatNode):
    def str(self):
        return "<symbol {key}>".format(key = self.value)
    pass

pass
class KVFormatNode(FormatNode):
    def str(self):
        return "<key-value>"
    pass

pass
class SptFormatNode(FormatNode):
    def str(self):
        return "<split>"

pass

class SpcFormatNode(FormatNode):
    def __init__(self, add_depth = 0, add_top = 0):
        super(SpcFormatNode, self).__init__()
        self._depth = add_depth
        self._top = add_top
    def depth(self):
        return max(0, self._depth+self.up.max_depth)
    def top(self):
        return max(0, self._top+self.up.to_top)
    def str(self):
        return "<space>{i},{j}".format(i=self.up.max_depth, j = self.up.to_top)

pass

class SymbolFormat(BaseFormat):
    def deal(self, node, fc, **params):
        if not isinstance(node, SymbolFormatNode):
            return None
        return node.value

pass
class KeyFormat(BaseFormat):
    def __init__(self, key, node_type):
        self.key = key
        self.node_type = node_type
    def deal(self, node, fc, **params):
        if not isinstance(node, self.node_type):
            return None
        return self.key

pass

class SpcFormat(BaseFormat):
    def __init__(self, spc=" ", enter = "\n", size = 4, format = False, simple = 1, simple_size = 1):
        self.format = format
        self.simple = simple
        self.size = size
        self.enter = enter
        self.simple_size = simple_size
        self.spc = spc*size
        self._spc = spc*simple_size
        pass
    def deal(self, node, fc, **params):
        if not isinstance(node, SpcFormatNode):
            return None
        if not self.format:
            return self._spc
        max_depth = node.depth()
        if max_depth<=self.simple:
            return self._spc
        return self.enter+(self.spc*node.top())


pass


class NodeFormat(BaseFormat):
    def deal(self, node, fc, **params):
        if node.is_leaf():
            return None
        rst = None
        for _node in node.childs:
            _rst = fc(_node, **params)
            if _rst is None:
                raise Exception("Unregist deal node:"+str(_node))
            if rst is None:
                rst = _rst
            else:
                rst += _rst
        return rst

pass