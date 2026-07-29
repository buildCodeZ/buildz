
import json, time, os
from buildz.base import Base
from buildz.html import base as xml
from buildz import xf,dz,fz, log as logz, path as pathz
pth = pathz.Path(os.path.dirname(__file__))

'''
    根据名称查物品属性（可以指定方面来查询）
    查询物品周围的物品，
    查询可以看到物品的生物
    查询物品可以看到的物品
'''
class DatasBase(Base):
    def add(self, data):
        pass
    def find(self, data):
        pass
    def remove(self, data):
        pass
    def replace(self, src, target):
        pass
    def query(self, data):
        pass

pass
class Datas(Base):
    '''
        可以根据向量相似度匹配
        向量相似度用其他工具，这里主要做适配，可以根据关键字匹配？

    '''
    def init(self):
        self.datas = []
    def add(self, data):
        
