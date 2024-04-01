#coding=utf-8
"""
一些简单工具代码
"""

"""
a = [rp("<", ">")(script, "id", k[0], "val", k[1]) for k in a]

"""
class rp:
    def __init__(self, l="<", r=">"):
        self.l = l
        self.r = r
    def __call__(self, s, *params):
        for i in range(0, len(params), 2):
            s = s.replace(self.l+params[i*2]+self.r, params[i*2+1])
        return s

pass


import os
def listdirs(fp, maxdepth = -1, include_dir = False, abs = True):
    if abs:
        fp = os.path.abspath(fp)
    if not os.path.exists(fp):
        print("error path:", fp)
        return []
    if os.path.isfile(fp):
        return [fp]
    fs = os.listdir(fp)
    fs = [os.path.join(fp, k) for k in fs]
    rst = []
    for f in fs:
        rst += listdirs(f, maxdepth-1, include_dir, abs)
    return rst

pass

