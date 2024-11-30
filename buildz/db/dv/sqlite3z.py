
import sqlite3
import sys
from .basez import SimpleDv, fetch
from .structz import CMD
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
    def __init__(self, fp):
        self.con = None
        self.cursor = None
        self.init(fp)
    def init(self, fp):
        self.fp = fp

pass
def build(argv, conf):
    dv = Db(argv[0])
    return dv
def buildbk(argv, conf):
    return CMD(make(argv, conf))

pass
