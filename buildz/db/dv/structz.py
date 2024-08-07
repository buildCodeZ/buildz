#import pymysql
import sys
class ItDv:
    def begin(self):
        pass
    def close(self):
        pass
    def is_open(self):
        return False
    def commit(self):
        pass
    def refresh(self):
        pass
    def check_query(self, s):
        return False
    def query(self, sql, vals=()):
        # return list, first row is key
        return []
    def execute(self, sql, vals=()):
        return None
    def sql_tables(self):
        return ""

pass

class CMD:
    def begin(self):
        return self.dv.begin()
    def close(self):
        return self.dv.close()
    def __init__(self, dv, simple_format = True):
        self.s_rst = ""
        self.dv = dv
        self.simple_format = simple_format
    def __enter__(self, *argv, **maps):
        self.dv.begin()
        return self
    def __exit__(self, *argv, **maps):
        self.dv.close()
    def exec(self, fc, sql, vals = ()):
        need_close = False
        if not self.dv.is_open():
            self.dv.begin()
            need_close = True
        rst = fc(sql, vals)
        if need_close:
            self.dv.close()
        return rst
    def query(self, sql, vals = ()):
        return self.exec(self.dv.query, sql, vals)
    def execute(self, sql, vals = ()):
        return self.exec(self.dv.execute, sql, vals)
    def s_print(self, *args):
        args = [str(k) for k in args]
        s = " ".join(args)
        s = s+"\n"
        self.s_rst += s
    def s_flush(self):
        out = self.s_rst
        self.s_rst = ""
        return out
    def rp(self, s):
        return s
        rps = ["\n\\n","\r\\r","\t\\t"]
        for rp in rps:
            s = s.replace(rp[0], rp[1:])
        return s
    def sz(self, s):
        try:
            s = s.encode("gbk")
        except Exception as exp:
            print("SZ exp:", exp)
        return min(100, len(s))
    def jstr(self, obj):
        import datetime
        import decimal
        if type(obj) == datetime.datetime:
            obj = str(obj) 
        if type(obj) == decimal.Decimal:
            obj = str(obj) 
        if type(obj) == bytes:
            obj = list(obj)[0]
        import json
        rs = json.dumps(obj, ensure_ascii=0)
        return rs
    def tr_sz(self, s, sz):
        try:
            s = s.encode("gbk")
            s = s+(b" "*(sz-len(s)))
            s = s.decode("gbk")
        except Exception as exp:
            print("TR_SZ exp:", exp)
        return s
    def format(self, arr):
        arr = [[self.rp(k) for k in obj] for obj in arr]
        if self.simple_format and len(arr)>0:
            sz = [[self.sz(k) for k in obj] for obj in arr]
            l = len(arr[0])
            szs = [max([obj[i] for obj in sz]) for i in range(l)]
            arr = [[self.tr_sz(obj[i], szs[i]) for i in range(l)] for obj in arr]
        arr = [" | ".join(k) for k in arr]
        arr = ["[[ "+k+" ]]" for k in arr]
        return "\n".join(arr)
    def single(self, s):
        s=s.strip()
        if s == "commits":
            self.dv.commit()
        elif s == "reset":
            self.dv.close()
            self.dv.begin()
        elif s == "refresh":
            self.dv.refresh()
        elif s == "table":
            s = self.dv.sql_tables()
            self.s_print(self.single(s))
        elif s == "exit":
            raise Exception("exit")
        elif s.split(" ")[0] == "source":
            # source filepath [encoding]
            arr = s.split(" ")
            fp =arr[1].strip()
            cd = "utf-8"
            if len(arr)>2:
                cd = arr[2].strip().lower()
            with open(fp, 'rb') as f:
                s = f.read().decode(cd)
            arr = s.split(";")
            for sql in arr:
                if sql.strip() == "":
                    continue
                _sql = sql+";"
                self.s_print("sql:", _sql)
                tmp = self.execute(_sql)
                self.s_print(tmp)
            self.s_print("done source", fp)
        elif s.split(" ")[0] == "export":
            # export filepath encoding sql;
            self.s_print("export:", s)
            arr = s.split(" ")
            fp =arr[1].strip()
            cd = arr[2].strip().lower()
            s = " ".join(arr[3:])
            self.s_print("sql:", s)
            rst = self.query(s)
            result = []
            if len(rst)>0:
                keys = rst[0]
                rst = rst[1:]
                result.append(['"'+v.lower()+'"' for v in keys])
                for i, obj in zip(range(len(rst)), rst):
                    v = ['"'+str(k)+'"' for k in obj]
                    result.append(v)
            result = [", ".join(k) for k in result]
            rs = "\n".join(result)
            with open(fp, "wb") as f:
                f.write(rs.encode(cd))
            self.s_print("done write \"{s}\" to {fp}".format(s = s, fp = fp))
        elif s == "":
            return ""
        else:
            self.s_print("SQL:", s)
            try:
                if self.dv.check_query(s):
                    rst = self.query(s)
                    result = []
                    if len(rst)>0:
                        keys = rst[0]
                        rst = rst[1:]
                        result.append(["KEY"]+keys)
                        for i, obj in zip(range(len(rst)), rst):
                            v = [self.jstr(k) for k in obj]
                            result.append([str(i)]+v)
                    self.s_print(self.format(result))
                else:
                    rst = self.execute(s)
                    self.s_print(rst)
            except Exception as exp:
                import traceback
                traceback.print_exc()
                self.s_print("Error sql line:", exp)
            self.s_print("")
        return self.s_flush()
    def run(self):
        self.begin()
        try:
            while True:
                rst = []
                while True:
                    s = input(":").strip()
                    if s in "cls, clear".split(","):
                        import os
                        os.system(s)
                        continue
                    rst.append(s)
                    if s.find(";")>=0:
                        break
                s = " ".join(rst)
                s = s.split(";")[0].strip()
                if s == "exit":
                    break
                rst = self.single(s)
                print(rst)
                print("")
        finally:
            self.close()

pass
