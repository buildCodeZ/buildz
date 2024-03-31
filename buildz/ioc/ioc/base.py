#coding=utf-8
from buildz import xf, pyz
from buildz.xf import g as xg
import json
class Base:
    def update_maps(self, maps, src):
        xf.deep_update(maps, src)
    def __init__(self, *args, **maps):
        self.init(*args, **maps)
    def init(self, *args, **maps):
        pass
    def __call__(self, *args, **maps):
        return self.deal(*args, **maps)
    def deal(self, *args, **maps):
        return None

pass
class EncapeData(Base):
    """
        包含data id对应的配置，配置文件id，配置文件对象
        [object.test, call, ]
    """
    def __init__(self, data, conf, local = False, type = None, src = None):
        self.data = data
        self.sid = conf.id
        self.src = src
        self.conf = conf
        self.confs = conf.confs
        self.local = local
        if type is None:
            type = conf.confs.get_data_type(data, 0, conf.default_type())
        self.type = type

pass
