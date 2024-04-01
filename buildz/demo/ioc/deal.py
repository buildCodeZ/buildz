#coding=utf-8
from buildz import xf, argx, pyz, ioc, fz

class Deal:
    def deal(self):
        args, maps = argx.fetch()
        if len(args)<3:
            print("need params 1 to be filepath, params 2 to be data_id")
            return
        dp = args[1]
        fps = fz.search(dp, ".*\.js$")
        confs = ioc.build()
        confs.add_fps(fps)
        id = args[2]
        rst = confs.get(id)
        print(f"get {id}: {rst}")
        return rst

pass
