#
from buildz.ioc import build
from buildz import xf
import os
join = os.path.join
class Test:
    def __init__(self, *args, **maps):
        print(f"Test init args: {args}, maps: {maps}")
        self.args = args
        self.maps = maps
    def run(self):
        print(f"get obj:{self}")
        print("get_obj.obj:", self.obj)

pass
fps = xf.loads("[data1.js, data2.js, data3.js]")[:2]

fps = [join('test_conf', fp) for fp in fps]
def show():
    print("run show")

pass
def test():
    confs = build()
    for fp in fps:
        confs.add_fp(fp)
    #obj =  confs.get("data1.test")
    confs.get("data1.run")
    obj = confs.get("data1.test.obj")
    print(f"obj: {obj}")

pass

if __name__=="__main__":
    test()

pass