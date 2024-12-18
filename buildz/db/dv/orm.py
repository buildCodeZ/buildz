#coding=utf-8

from buildz import Base
from buildz.db import tls
from buildz import xf
def dict2list(data):
    rst = []
    for k,v in data.items():
        if type(v) not in (list, tuple):
            v = [v]
        tmp = [k]+list(v)
        rst.append(tmp)
    return rst
def deal_item(item, conf):
    key = item[0]
    if key in "sql_before,sql_after,sql_delete_before,sql_delete_after".split(","):
        conf[key].append(item[1])
    else:
        conf[key] = item[1]
def deal_key(it, conf):
    data_keys = xf.g(conf, data_keys=[])
    tmp = {}
    for i in range(min(len(it), len(data_keys))):
        tmp[data_keys[i]] = it[i]
    sql_key = tmp['sql_key']
    sql_def = tmp['sql_def']
    py_key = xf.g(tmp, py_key=None)
    if py_key is not None:
        xf.g(conf, py2sqls={})[py_key] = sql_key
    xf.g(conf, keys=[]).append(sql_key)
    xf.g(conf, vars=[]).append(sql_key+" "+sql_def)
def makes(datas, data_keys = "sql_key,sql_def,py_key".split(",")):
    if type(datas)==dict:
        rst = [make(v, k) for k,v in datas.items()]
    else:
        rst = [make(it) for it in datas]
    return rst
def make(data, table=None, data_keys = "sql_key,sql_def,py_key".split(",")):
    """
        从配置中生成建表语句，删表语句和orm对象
        输入:
            data: dict or list
                dict: {
                    (其他配置)
                    (其他配置)
                    表字段: [sql字段定义, 转py后字段名]
                    表字段: sql字段定义
                }
                list: [
                    ((其他配置))
                    ((其他配置))
                    [表字段, sql字段定义, 转py后字段名]
                    [表字段, sql字段定义]
                ]
                其他配置:
                    格式: key, val
                    key:
                        table: 表名
                        query_keys: 默认null，orm做插入/更新时，判断数据是插入还是更新的查询方式
                        auto_translate: 默认true，如果没有配置“转py后字段名”，是否自动转(a_b=>aB)
                        sql_before: 新增一条建表前sql语句
                        sql_after: 新增一条建表后sql语句
                        sql_delete_before: 新增一条删表前sql语句
                        sql_delete_after: 新增一条删表后sql语句
                        data_keys: 默认[sql_key, sql_def, py_key]，非配置项怎么解析，不建议改
            table: 表名
        输出:
            [[sql_create, sql_delete], orm_obj]
    """
    if xf.is_args(data):
        confs = data.lists
        confs =[[it] for it in confs]
        data = dict2list(data.maps)
        data = confs+data
    elif type(data) == dict:
        data = dict2list(data)
    conf = {}
    xf.s(conf, sql_before = [], sql_after = [], sql_delete_before=[], sql_delete_after=[],auto_translate=True,table=table,keys=[],py2sqls={},query_keys=None, data_keys = data_keys, vars=[])
    for it in data:
        if len(it)==1 and type(it[0]) in (list, tuple):
            deal_item(it[0], conf)
        else:
            deal_key(it, conf)
    table = xf.g(conf, table=table)
    vars =  xf.g(conf, vars = [])
    vars = ",".join(vars)
    assert table is not None
    sql = f"create table if not exists {table}({vars})"
    sql_del = f"drop table if exists {table}"
    sqls = xf.g(conf, sql_before=[], sql_after=[], sql_delete_before=[], sql_delete_after=[])
    #sqls = [";".join(k) for k in sqls]
    sqls_crt = sqls[0]+[sql]+sqls[1]
    sqls_del = sqls[2]+[sql_del]+sqls[3]
    sqls = [sqls_crt, sqls_del]
    sqls = [(";\n".join(k)+";").replace(";;",";") for k in sqls]
    obj = TableObject(*xf.g(conf, keys=[], table=table, py2sqls = None, query_keys=None,auto_translate=True), sql_create = sqls[0], sql_delete = sqls[1])
    return sqls, obj

pass

class TableObject(Base):
    """
        字段映射
        keys: 表字段
        table: 表名
        py2sqls: 自定义映射
        query_keys: 唯一索引（判断数据重复）
        auto_translate:
            对于没有在py2sqls自定义映射的表字段，是否自动转换(py|autoTran<=>auto_tran|sql)
    """
    def init(self, keys, table=None, py2sqls=None, query_keys=None, auto_translate=True, dv = None, sql_create=None, sql_delete=None):
        if table is None:
            table = tls.lower(self.__class__.__name__)
        self.table = table
        if py2sqls is None:
            py2sqls = {}
        if type(py2sqls) in (list, tuple):
            py2sqls = {k[0]:k[1] for k in py2sqls}
        sql2pys = {}
        for k_py, k_sql in py2sqls.items():
            sql2pys[k_sql] = k_py
        for key in keys:
            if key not in sql2pys:
                k_py, k_sql = key,key
                if auto_translate:
                    k_py,k_sql = tls.upper(key), tls.lower(key)
                py2sqls[k_py] = k_sql
                sql2pys[k_sql] = k_py
        self.py2sqls = py2sqls
        self.sql2pys = sql2pys
        self.keys = keys
        if query_keys is None:
            query_keys = []
        self.query_keys = query_keys
        self.dv = dv
        self.py2sql=self.toSql
        self.sql2py = self.toPy
        self.sql_create = sql_create
        self.sql_delete = sql_delete
    def create(self, dv=None):
        assert self.sql_create is not None
        dv = self.rdv(dv)
        dv.executes(self.sql_create)
    def delete(self, dv=None):
        assert self.sql_delete is not None
        self.rdv(dv).execute(self.sql_delete)
    def bind(self, dv):
        self.dv = dv
    def toSql(self, obj):
        if type(obj)!=dict:
            tmp = {}
            for k in self.py2sqls:
                if hasattr(obj, k):
                    tmp[k] = getattr(obj, k)
            obj = tmp
        obj = {self.py2sqls[k]:v for k,v in obj.items()}
        return obj
    def toPy(self, obj):
        if type(obj)!=dict:
            tmp = {}
            for k in self.sql2pys:
                if hasattr(obj, k):
                    tmp[k] = getattr(obj, k)
            obj = tmp
        obj = {self.sql2pys[k]:v for k,v in obj.items()}
        return obj
    def rdv(self, dv):
        if dv is None:
            dv = self.dv
        assert dv is not None
        return dv
    def query(self, sql, dv=None, sql2py=True):
        dv=self.rdv(dv)
        rst = dv.query(sql)
        if sql2py:
            rst = [self.sql2py(it) for it in rst]
        return rst
    def queryAll(self, dv=None, sql2py=True):
        sql = f"select * from {self.table};"
        return self.query(sql, dv, sql2py)
    def save(self, obj, dv=None, py2sql = True, commit=False):
        dv = self.rdv(dv)
        if type(obj) not in [list, tuple]:
            obj = [obj]
        if py2sql:
            obj = [self.toSql(k) for k in obj]
        _ = [dv.insert_or_update(k, self.table, self.query_keys) for k in obj]
        if commit:
            dv.execute("commit;")
        return _

