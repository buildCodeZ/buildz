#coding=utf-8
import sys,re
from .base import Base
class Fetch:
    """
    命令行参数读取
    ft = Fetch("id,name,kind".split(","), {"a":"age"})
        or
    ft = Fetch(*xf.loads("[[id,name,kind],{a:age}]"))

    ft("001 zero life -a12".split(" ")) = {'id': '001', 'name': 'zero', 'kind': 'life', 'age': '12'}

    但更简单的方法是:
    xf.args("{id:'001', name: zero, kind: life, age: 12}".split(" ")) = {'id': '001', 'name': 'zero', 'kind': 'life', 'age': 12}
    python buildz.xf {id:'001', name: zero, kind: life, age: 12}
    就是对引号不太适用
    """
    def __init__(self, args = [], maps ={}, marks = set()):
        args = [maps[k] if k in maps else k for k in args]
        self.args = args
        self.maps = maps
        self.marks = marks
    def last(self, key):
        while key in self.maps:
            key = self.maps[key]
            if type(key) in (list, tuple):
                key = key[0]
        return key
    def des(self):
        cmd = " ".join([self.last(k) for k in self.args])
        adds = []
        marks = set()
        lasts = {}
        for key, val in self.maps.items():
            for k in [key, val]:
                if k in marks:
                    continue
                marks.add(k)
                last = self.last(k)
                param = f" <{last}>"
                if k in self.marks:
                    param = f"(set {last} as true)"
                if len(k)==1:
                    tags = [f"-{k}{param}"]
                else:
                    tags = [f"--{k}{param}"]
                    if k not in self.marks:
                        tags.append(f"--{k}=<{last}>")
                if last not in lasts:
                    lasts[last] = []
                lasts[last]+=tags
        for last, tags in lasts.items():
            tags = " | ".join(tags)
            tags = f"[{tags}]"
            adds.append(tags)
            #s = f"  {last}: {' '.join(tags)}"
        adds = [cmd]+adds
        rs = " ".join(adds)
        return rs
    def check(self, args, ks):
        rst = []
        for k in ks:
            if k not in args:
                rst.append(k)
        return rst
    def __call__(self, argv = None):
        args, maps = fetch(argv, self.marks)
        return self.fetch(args, maps)
    def fetch(self, args, maps):
        rst = {}
        for i in range(len(args)):
            if i >= len(self.args):
                break
            key = self.args[i]
            rst[key] = args[i]
        for key in maps:
            rst[key] = maps[key]
        keys = list(rst.keys())
        while len(keys)>0:
            key = keys.pop(0)
            if key in self.maps:
                rkeys = self.maps[key]
                if type(rkeys) not in (list, tuple):
                    rkeys = [rkeys]
                for rkey in rkeys:
                    assert rkey!=key, f'error rkey==key: {key}'
                    val = rst[key]
                    if rkey not in rst:
                        rst[rkey] = val
                    else:
                        tmp = rst[rkey]
                        if type(tmp)!=list:
                            tmp = [tmp]
                            rst[rkey] = tmp
                        tmp.append(val)
                    keys.append(rkey)
                    keys = list(set(keys))
                del rst[key]
        return rst

pass
class FetchX(Fetch):
    def __init__(self, *a, **b):
        super().__init__(a,b)

pass

def build_pt(pt, fc):
    st = "^"
    ed = "$"
    if pt[0]!=st:
        pt = st+pt
    if pt[-1]!=ed:
        pt = pt+ed
    def wfc(val):
        if re.match(pt, val) is None:
            return None, 0
        val = fc(val)
        return val, 1
    return wfc

pass
class ValDeals(Base):
    def init(self):
        self.deals = []
    def add(self, fc):
        self.deals.append(fc)
    def call(self, val):
        if type(val)!=str:
            return val
        for deal in self.deals:
            rst, done = deal(val)
            if done:
                return rst
        return val

pass
to_val = ValDeals()
to_val.add(build_pt("[\+\-]?\d+", int))
to_val.add(build_pt("[\+\-]?\d*\.\d+", float))
to_val.add(build_pt("[\+\-]?\d*(?:\.\d+)?e[\+\-]?\d+", float))
to_val.add(build_pt("null", lambda x:None))
to_val.add(build_pt("true", lambda x:True))
to_val.add(build_pt("false", lambda x:False))

def fetch(argv = None, marks = set()):
    r"""
    format: a b c -a 123 -b456 --c=789 +d  -x"??? ???" y z
    return: [a,b,c,y,z], {a:123,b:456,c:789,d:1,x:'??? ???'}
    """
    if argv is None:
        argv = sys.argv[1:]
    marks = set(marks)
    lists, maps = [],{}
    argv = [str(k).strip() for k in argv]
    argv = [k for k in argv if k!=""]
    i = 0
    def add_maps(maps, k, v):
        v = to_val(v)
        if k not in maps:
            maps[k] = []
        maps[k].append(v)
    while i<len(argv):
        v = argv[i]
        i+=1
        if v[0]!='-':
            v = to_val(v)
            lists.append(v)
            continue
        if v[1]=='-':
            v = v[2:]
            index = v.find("=")
            if index>=0:
                k = v[:index]
                v = v[index+1:]
            else:
                k = v
                v = None
            if k in marks:
                v = 1
            if v is None:
                assert i<len(argv), f"param '{k}' required value (-{k} val)"
                v = argv[i]
                i+=1
            add_maps(maps, k, v)
        else:
            ks = v[1:].strip()
            for k in ks:
                if k in marks:
                    v = 1
                else:
                    assert i<len(argv), f"param '{k}' required value (--{k} val | --{k}=val)"
                    v = argv[i]
                    i+=1
                add_maps(maps, k, v)
    for k in maps:
        v = maps[k]
        if len(v)==1:
            maps[k] = v[0]
    return lists, maps

pass
