#coding=utf-8
from .read import loads
import sys
def fetch(argv = None):
    if argv is None:
        argv = sys.argv[1:]
    argv = [str(k) for k in argv]
    s = " ".join(argv)
    s = s.strip()
    lrs = [["",""]]
    if len(s)==0:
        return None
    if s[0] not in "([{":
        lrs = ["{}", "[]"]
    for l,r in lrs:
        x = l+s+r
        try:
            return loads(x)
        except:
            pass
    raise Exception("unable to fetch params")

pass
# python -m buildz.xf {a:b}
def test():
    rst = fetch()
    print(f"cmd params: {rst}")

pass
