
__doc__="""
记忆管理工具
不包括ai调用逻辑
包括记忆存储，关系存储，查找
后续增加向量后，再封装一层VecManager，内部调用Manager
或者封装记忆存储和关系存储，依然用该Manager，看后续需求
"""
from .base import *
class Manager(Base):
    def init(self, mems, rls):
        self.mems = mems
        self.rls = rls
    def mem_add(self, obj):
        return self.mems.add(obj)
    def mem_replace(self, src, tgt):
        return self.mems.replace(src, tgt)
    def mem_remove(self, obj):
        return self.mems.remove(obj)
    pass
