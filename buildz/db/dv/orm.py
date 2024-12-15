#coding=utf-8

from buildz import Base
from buildz.db import tls
class TableObject(Base):
    def init(self, keys, table=None, translates=None, primary_keys=None, auto_translate=True, dv = None):
        if table_name is None:
            table = tls.lower(self.__class__.__name__)
        self.table = table
        if translates is None:
            translates = {}
        for key in keys:
            if key not in translates:
                k_py, k_sql = key,key
                if auto_translate:
                    k_py,k_sql = tls.upper(key), tls.lower(key)
                translates[k_py] = k_sql
        self.translates = translates
        self.keys = keys
        if primary_keys is None:
            primary_keys = []
        self.primary_keys = primary_keys
        self.dv = dv
    def save(self, obj, dv=None):
        if dv is None:
            dv = self.dv
        assert dv is not None
        if type(obj)!=dict:
            tmp = {}
            for k in self.translates:
                if hasattr(obj, k):
                    tmp[k] = getattr(obj, k)
            obj = tmp
        obj = {self.translates[k]:v for k,v in obj.items()}
        return dv.insert_or_update(obj, self.table, self.primary_keys)

