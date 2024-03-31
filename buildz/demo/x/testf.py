#coding=utf-8
try:
    from buildz import build
except:
    import sys
    import os
    sys.path.append(os.path.abspath("./../.."))
    from buildz import build
from buildz import xconfz
from buildz import confz

import os
import json
def test(fp = "test.confz"):
    
    obj = xconfz.loads(confz.fread(fp))

    s = confz.dumps(obj, format=True)#, simple =1, as_json = False, t_single = False)
    robj = xconfz.loads(s)
    #robj = json.loads(s)
    return s, obj, json.dumps(robj)

pass

def main():
    nd, obj, robj = test()
    print("obj:")
    print(obj)
    print("nd:")
    print(nd)
    print("robj:")
    print(robj)

pass

if __name__=="__main__":
    main()

pass
"""

python3
import testf
nd, obj = testf.test()

"""
