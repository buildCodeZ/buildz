#coding=utf-8
from buildz import xf, argx, pyz, ioc

class Deal:
    def deal(self):
        args, maps = argx.fetch()
        if len(args)<2:
            print("need params 1 to be filepath")
            return
        fp = args[1]
        obj = xf.loads(xf.fread(fp))
        s = xf.dumps(obj, format=1, deep=1)
        print(s)
    pass

pass
