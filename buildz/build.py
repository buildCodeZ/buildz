#coding=utf-8
#main
def get(obj, key, default = None):
    if key in obj:
        return obj[key]
    return default

pass
def load(md, fc = None):
    arr = md.split(".")[1:]
    md = __import__(md)
    for k in arr:
        md = getattr(md, k)
    if fc is not None:
        fc = getattr(md, fc)
    else:
        fc = md
    return fc

pass
class EpFc:
    def __init__(self, fc, n = 1):
        self.fc = fc
        self.n = n
    def __call__(self, *argv):
        argv = argv[:self.n]
        return self.fc(*argv)

pass
import builtins
def build_list(*argv):
    return list(argv)

pass

def build_dict(**maps):
    return dict(maps)

pass
builtins._list = build_list
builtins._dict = build_dict
g_default_import = "buildz"+".base"
def read_confz(filepath):
    from buildz import confz
    s = confz.fread(filepath)
    obj = confz.read(s)
    return obj

pass
def read_json(filepath):
    from buildz import confz
    import json
    s = confz.fread(filepath)
    obj = json.loads(s)
    return obj

pass
    
class Builder:
    def __init__(self, default_single = "0", default_import = g_default_import, ref_this = None, format = "confz"):
        self.ref_this = ref_this
        self.default_import = default_import
        self.default_single = default_single
        self.format = format
        self.maps = {}
        self.objs = {}
        types = {}
        types['str'] = EpFc(str)
        types['int'] = EpFc(int)
        types['float'] = EpFc(float)
        self.types = types
        self.types['ref'] = EpFc(self.run)
        self.types['this'] = EpFc(self.get_this, 2)
        self.types['call'] = EpFc(self.run, 2)
        self.types['fc'] = EpFc(self.run, 1)
        self.types['run'] = EpFc(self.run, 1)
        self.loadtypes = {}
        self.loadtypes['json'] = read_json
        self.loadtypes['confz'] = read_confz
    def add_file(self, filepath, format = None, update = False):
        if format is None:
            format = self.format
        obj = self.loadtypes[format](filepath)
        self.add(obj, update)
    def add(self, data, update = False):
        if type(data) == dict:
            data = [data]
        for obj in data:
            key = get(obj, "key")
            if key in self.maps and not update:
                raise Exception("duple define key: ["+key+"]")
            self.maps[key] = obj
            if update and key in self.objs:
                del self.objs[key]
    def get_this(self, key, obj):
        return getattr(obj, key)
    def deal_args(self, args, obj = None):
        if type(args)!= list:
            args = [args]
        rst = []
        for _obj in args:
            if type(_obj) not in [list, tuple]:
                _obj = [_obj, "str"]
            val = self.types[_obj[1]](_obj[0], obj)
            rst.append(val)
        return rst
    def deal_maps(self, maps, obj = None):
        rst = {}
        for _obj in maps:
            if len(_obj)==2:
                _obj.append("str")
            _key = _obj[0]
            if type(_key) == list:
                _key = self.run(_key)
            val = self.types[_obj[2]](_obj[1], obj)
            rst[_key] = val
        return rst
    def deal_sets(self, sets, obj):
        for param in sets:
            if len(param)==2:
                param.append("str")
            _key = param[0]
            val = self.types[param[2]](param[1], obj)
            setattr(obj, _key, val)
    def deal_fcs(self, calls, obj):
        for call in calls:
            if type(call)!= list:
                call = [call, "call"]
            self.types[call[1]](call[0], obj)
    def get(self, key, src = None, force_new = False):
        return self.run(key, src, force_new)
    def set(self, key, val):
        self.maps[key] = {"single":"1"}
        self.objs[key] = val
    def run(self, key, src = None, force_new = False):
        if self.ref_this is not None and key == self.ref_this:
            return self
        if key not in self.maps:
            raise Exception("Error not such fc:"+key)
        data = self.maps[key]
        ref = get(data, "ref")
        if src is None and ref is not None:
            src = self.run(ref)
        if src is not None:
            force_new = True
        single = bool(int(get(data, "single", self.default_single)))
        single &= not force_new
        if single and key in self.objs:
            return self.objs[key]
        val = get(data, "val", None)
        if val is not None:
            args = [val]
        else:
            args = get(data, "args", [])
        args = self.deal_args(args, src)
        maps = get(data, "maps", [])
        maps = self.deal_maps(maps, src)
        fc = get(data, "call", None)
        var = get(data, "var", None)
        mark_var = False
        if fc is None:
            if var is not None:
                mark_var = True
                fc = var
        obj = None
        _data = get(data, "data", None)
        if fc is not None or src is not None:
            fcs = []
            if fc is not None:
                fcs = fc.split(".")
            if src is not None:
                fc = src
            else:
                _import = get(data, "import", self.default_import)
                md = load(_import)
                fc = md
            for nfc in fcs:
                fc = getattr(fc, nfc)
            if mark_var:
                return fc
            if _data is None:
                obj = fc(*args, **maps)
            else:
                obj = fc(_data)
            if single:
                self.objs[key] = obj
            sets = get(data, "sets", [])
            self.deal_sets(sets, obj)
        calls = get(data, "calls", [])
        self.deal_fcs(calls, obj)
        if obj is None:
            if _data is not None:
                return _data
            elif val is not None:
                return val
            elif args is not None:
                return args
            elif maps is not None:
                return maps
        return obj

pass
class Test:
    def __init__(self, a, b):
        print("a:", a)
        self.a = a
        self.b = b
    def test(self, obj):
        print("TEST:", obj)
    def __call__(self):
        print(self.a)
        print(self.b)

pass

import sys
import os
def main(paths, default_import = g_default_import, ref_this = "this"):
    builder = Builder(1, default_import = default_import, ref_this = ref_this)
    for path in paths:
        if os.path.isfile(path):
            builder.add_file(path)
        elif os.path.isdir(path):
            files = os.listdir(path)
            files = [os.path.join(path, file) for file in files]
            [builder.add_file(file) for file in files]
        else:
            print("what is this? :", path)
    builder.run("main")

pass
import os
import re
class Pattern:
    def __init__(self, pt):
        self.pt = pt
    def __call__(self, s):
        if self.pt is None:
            return True
        return re.findall(self.pt, s)>0

pass


def listdir(path, max_depth = -1, pattern = None, nopattern = None, march = None):
    if max_depth == 0:
        return []
    files = os.listdir(path)
    pt = Pattern(pattern)
    files = [os.path.join(path, file) for file in files]
    rst = []
    for file in files:
        if os.path.isdir(file):
            rst += listdir(file, max_depth-1, pattern)
        else:
            if pt(os.path.basename(file)):
                rst.append(file)
    return rst

pass

    
def test():
    builder = Builder(1)
    argv = sys.argv[1:]
    main(argv)

pass

if __name__=="__main__":
    test()

pass

