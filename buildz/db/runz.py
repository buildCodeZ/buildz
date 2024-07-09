
import sys
import os
import time
from buildz import xf
FP = "run.conf"
def find(arr, k, base = 0):
    for i in range(base, len(arr)):
        if arr[i]==k:
            return i
    return -1

pass
def test(fp):
    obj = xf.loads(xf.fread(fp))
    dv = obj['dv']
    if __name__ == "__main__":
        if dv == 'mysql':
            from dv.mysqlz import build
        elif dv == 'oracle':
            from dv.oraclez import build
        elif dv == 'clickhouse':
            from dv.clickhousez import build
    else:
        if dv == 'mysql':
            from .dv.mysqlz import build
        elif dv == 'oracle':
            from .dv.oraclez import build
        elif dv == 'clickhouse':
            from .dv.clickhousez import build
    db_url = obj['db']
    db_url = obj[db_url]
    user = obj['user']
    pwd = obj['pwd']
    src = obj['src']
    out = obj['out']
    sqls = xf.fread(src)
    sqls = sqls.replace("\r\n", "\n").rstrip().split("\n")
    sqls_strip = [k.strip() for k in sqls]
    i = find(sqls_strip, "!!begin")
    bi = i
    if i < 0:
        bi=0
    j = find(sqls_strip, "!!end", bi)
    sqls = sqls[i+1:j]
    sqls = [k for k in sqls if k.lstrip()[:2]!="--"]
    sqls = "\n".join(sqls)
    sqls = sqls.split(";")
    print(f"[TESTZ] sqls:{sqls}")
    cmd = build([db_url, user, pwd], obj)
    cmd.dv.begin()
    print("[TESTZ] A")
    with open(out, 'wb') as f:
        for sql in sqls:
            if sql.strip()=="":
                continue
            if sql.strip() == "exit":
                break
            print("[TESTZ] B")
            rst = cmd.single(sql)
            print("[TESTZ] C")
            f.write(rst.encode("utf-8"))
    cmd.close()

pass
class Runner:
    def __init__(self, fp):
        self.fp = fp
    def init(self):
        self.obj = xf.loads(xf.fread(self.fp))
        self.fps = [self.fp, self.obj['src']]
        self.fps = [os.path.abspath(fp) for fp in self.fps]
        self.curr = [0,0]
    def run(self):
        while True:
            secs = [os.path.getmtime(fp) for fp in self.fps]
            if self.curr != secs:
                print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "done update")
                self.init()
                self.curr = secs
                test(self.fp)
            time.sleep(float(self.obj['sec']))

pass

def run(fp):
    r = Runner(fp)
    r.init()
    r.run()

pass
def main():
    fp = FP
    if len(sys.argv)>1:
        fp = sys.argv[1]
    return run(fp)

pass

if __name__=="__main__":
    main()

pass
