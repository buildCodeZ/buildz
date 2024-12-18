
import sqlite3
import sys,os
from .basez import SimpleDv, fetch
from .structz import CMD
from buildz import xf,fz
class Db(SimpleDv):
    # func to impl:
    def to_list(self, rst):
        rows = self.cursor.description
        keys = [k[0].lower() for k in rows]
        result = []
        result.append(keys)
        if rst is None or len(rst)==0:
            return result
        result += rst
        return result
    def new_con(self):
        return sqlite3.connect(self.fp)
    def new_cursor(self):
        return self.con.cursor()
    def __init__(self, fp, as_map=False, *argv, **maps):
        #def __init__(self, fp):
        self.con = None
        self.cursor = None
        self.as_map = as_map
        self.init(fp)
    def init(self, fp):
        fz.makefdir(fp)
        self.fp = fp
    def sql_tables(self, table = None):
        """
            if not note, use name instead
            require:
                table_name, table_note
        """
        query_table = ""
        if table is not None:
            query_table =  f" and name = '{table}'"
        return f"select name as table_name, '' as table_note from sqlite_master where type='table' {query_table};"
    def sql_indexes(self, table=None):
        """
            require:
                table_name, index_name, is_unique, index_type, index_note
        """
        query_table = ""
        if table is not None:
            query_table =  f" and tbl_name = '{table}'"
        return f"select tbl_name as table_name, name as index_name, -1 as is_unique, '?' as index_type, '' as index_note from sqlite_master where type='index' {query_table};"
    def columns(self, table, as_map=None):
        """
            require:
                table_name, column_name, column_type, column_default, nullable, column_offset, column_note
        """
        rst = self.query(f"PRAGMA table_info({table})", as_map=0)
        dts = rst[1:]
        keys = "table_name, column_name, column_type, column_default, nullable, column_offset, column_note".split(", ")
        rst = [keys]
        for dt in dts:
            cid, name, _type, notnull, dflt_value, pk = dt
            tmp = [table, name, _type, dflt_value, notnull, cid, '']
            rst.append(tmp)
        rst = self.out_list_sqlite3(rst, as_map)
        return rst
    def index_keys(self, index, as_map=None):
        """
            require:
                index_name, column_name, index_offset, column_note
        """
        rst = self.query(f"PRAGMA index_info({index})", as_map=0)
        dts = rst[1:]
        keys = "index_name, column_name, index_offset, column_note".split(", ")
        rst = [keys]
        for dt in dts:
            seqno, cid, name = dt
            tmp = [index, name, seqno, '']
            rst.append(tmp)
        return self.out_list_sqlite3(rst, as_map)
    def out_list_sqlite3(self, query_result, as_map=None):
        if as_map is None:
            as_map = self.as_map
        rst = query_result
        if as_map and len(rst)>0:
            if len(rst)==1:
                return []
            keys = rst[0]
            rst = rst[1:]
            rst = [{k:v for k,v in zip(keys, dt)} for dt in rst]
        return rst

pass
def build(argv, conf):
    root = xf.g(conf, root=None)
    fp = argv[0]
    if root is not None:
        fp = os.path.join(root, fp)
    as_map = xf.g(conf, as_map=False)
    dv = Db(fp, as_map)
    return dv
def buildbk(argv, conf):
    return CMD(make(argv, conf))

pass
