#coding=utf-8
'''
1, remain char:
    {}[]()<>:'"#\n,;
   to write a string contain remain char, user '' or "" or "x3 or 'x3:
    "hello:world, 'zero'"
    'hello:world, "zero"'
    """zero say: "hello, 'world'" """
2, from string to obj:
    read(s)
3, from obj to string:
    output(obj)
4, from filepath to obj:
    loadfile(filepath)
5, simple read filepath to string:
    fread(filepath)


example:
demo.txt:
[
    # single line note
    {
        filepath: "D:\demo\demo.txt"
        key: test.com
        array: [1, 2, 3]
    }
    ###
        multi-line note
        1
        2
        3
    ###
    {
        test: ":test{}??",
        val: <10, int>,
        cost: <10.0, float>,
        check: <true, bool>,
        <10, int>: "test"
    }
    #multi-line string
    """test line
        1
        2
        3
    """
    1
    2
    3
    # type not string
    <4, int>
    <5.0, float>
    <true, bool>
]

code:

obj = confz.loadfile("demo.txt")
obj: [{'filepath': 'D:\\demo\\demo.txt', 'key': 'test.com', 'array': ['1', '2', '3']}, {'test': ':test{}??', 'val': 10, 'cost': 10.0, 'check': True, 10: 'test'}, 'test line\n        1\n        2\n        3\n    ', '1', '2', '3', 4, 5.0, True]

s = confz.output(obj)
print(s):
[
    {
        filepath: "D:\demo\demo.txt"
        key: test.com
        array: [1, 2, 3]
    }
    {test: ":test{}??", val: <10, int>, cost: <10.0, float>, check: <true, bool>, <10, int>: test}
    "test line
        1
        2
        3
    "
    1
    2
    3
    <4, int>
    <5.0, float>
    <true, bool>
]
'''
global G_DEBUG
G_DEBUG = False
def debug(on = True):
    global G_DEBUG
    G_DEBUG = on

pass

coding="utf-8"
def bread(filepath):
    with open(filepath, 'rb') as file:
        s = file.read()
    return s

pass
def decode(s, coding = 'utf-8'):
    coding = coding.lower()
    xcoding = 'utf-8'
    if coding == 'utf-8':
        xcoding = 'gbk'
    try:
        return s.decode(coding)
    except:
        return s.decode(xcoding)

pass
def decode_c(s, coding = 'utf-8'):
    coding = coding.lower()
    xcoding = 'utf-8'
    if coding == 'utf-8':
        xcoding = 'gbk'
    try:
        return s.decode(coding), coding
    except:
        return s.decode(xcoding), xcoding

pass
def fread(filepath, coding = 'utf-8'):
    s = bread(filepath)
    return decode(s, coding)

pass
def fread_c(filepath, coding = 'utf-8'):
    s = bread(filepath)
    return decode_c(s, coding)

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
def sread(s):
    s = s.strip()
    if s == "":
        raise Exception("SR Empty")
    c = s[0]
    if c == '#':
        if s[:3].count(c) < 3:
            j = s.find("\n")
            if j < 0:
                return s, ""
            a = s[:j+1].strip()
            b = s[j+1:]
            return a, b
    if c == '/':
        if s[:2].count(c) == 2:
            j = s.find("\n")
            if j < 0:
                return s, ""
            a = s[:j+1].strip()
            b = s[j+1:]
            return a, b
    if c in "{}[]():<>":
        return c, s[1:]
    if c in ['"', "'", '#']:
        k = s[:3]
        if k.count(c)==3:
            j = s[3:].find(k)
            if j < 0:
                raise Exception("SR q3:"+k)
            k = j
            a = s[:j+3+3].strip()
            b = s[j+3+3:]
            return a, b
        j = s[1:].find(c)
        if j < 0:
            raise Exception("SR qt:"+c)
        a = s[:j+2].strip()
        b = s[j+2:]
        return a, b
    for i in range(len(s)):
        k = s[i]
        if k in "{}[]()<>:'\"#":
            return s[:i].strip(), s[i:]
        if k in '\n,;':
            return s[:i].strip(), s[i+1:]
    return s.strip(), ""

pass
def q3(s):
    if s=="":
        return False
    c = s[0]
    if c not in ["'", '"']:
        return False
    return s[:3].count(c)==3

pass
def qt(s):
    if s=="":
        return False
    return s[0] in ['"', "'"]

pass
def note(s):
    if s=="":
        return True
    if s[:2] == "//":
        return True
    return s[0] == "#"

pass
class Key:
    def __init__(self, c):
        self.c = c
    def __str__(self):
        return "<obj "+self.c+">"
    def __repr__(self):
        return str(self)

pass
g_keys = "{}[]()<>:'\"#\n,;"
g_keys = {k:Key(k) for k in g_keys}

def s2i(s):
    global g_keys
    return [g_keys[k] for k in s]
    return list(s.encode("ascii"))

pass
def c2i(s):
    global g_keys
    return g_keys[s]
    return s.encode("ascii")[0]

pass


def getList(stack):
    rst = []
    while len(stack)>0:
        w = stack.pop(-1)
        if w in s2i("[("):
            rst.reverse()
            return rst
        rst.append(w)
    raise Exception("getList not [")

pass

def getDict(stack):
    rst = {}
    lst = []
    while len(stack)>0:
        w = stack.pop(-1)
        if w == c2i("{"):
            lst.reverse()
            for k in lst:
                rst[k[0]] = k[1]
            return rst
        lst.append(w)
    raise Exception("getDict not {")

pass

def getStr(s):
    s = s.strip()
    if s == "":
        return
    c = s[0]
    if c not in ['"', "'"]:
        return s
    if s[:3].count(c)<3:
        return s[1:-1]
    return s[3:-3]

pass

g_bools = {}
g_bools['true'] = True
g_bools['1'] = True
g_bools['false'] = False
g_bools['0'] = False
g_bools[''] = False

def get_bool(s):
    global g_bools
    s = s.lower()
    if s not in g_bools:
        raise Exception("Error g_bools val: "+s)
    return g_bools[s]

pass
def get_none(s):
    return None

pass
g_types = {}
g_types['int'] = int
g_types['float'] = float
g_types['str'] = str
g_types['bool'] = get_bool
g_types['null'] = get_none


g_rtypes = {}
g_rtypes[int] = 'int'
g_rtypes[float] = 'float'
g_rtypes[str] = 'str'
g_rtypes[bool] = 'bool'
g_rtypes[type(None)] = 'null'
def getVal(stack):
    global g_types
    rst = []
    while len(stack)>0:
        w = stack.pop(-1)
        if w in s2i("<"):
            rst.reverse()
            if len(rst)==1:
                rst.append("str")
            if rst[1] not in g_types:
                raise Exception("Error <type>: "+rst[1])
            return g_types[rst[1]](rst[0].strip())
        rst.append(w)
    raise Exception("getVal not <")

pass
def symbol(w):
    return type(w) == Key
    return type(w)==int

pass
def get(obj, key, default = None):
    if key not in obj:
        return default
    return obj[key]

pass
paths = []
def read(s, path = None):
    global paths
    if path is not None:
        paths.append(path)
    stack = []
    while s != "":
        if G_DEBUG:
            print("stack:", stack)
        w, s = sread(s)
        #print("w:", w)
        w = w.strip()
        if note(w):
            continue
        if w in "])":
            obj = getList(stack)
            stack.append(obj)
        elif w in "[({<:":
            stack.append(c2i(w))
        elif w == ">":
            obj = getVal(stack)
            stack.append(obj)
        elif w == "}":
            obj = getDict(stack)
            stack.append(obj)
        else:
            w = getStr(w)
            stack.append(w)
        if len(stack)>=3:
            k = stack[-2]
            if k == c2i(":"):
                v = stack[-1]
                if not symbol(v):
                    val = stack.pop(-1)
                    stack.pop(-1)
                    key = stack.pop(-1)
                    stack.append([key, val])
    if G_DEBUG:
        print("stack:", stack)
    if path is not None:
        paths.pop(-1)
    return stack.pop(-1)

pass
loads = read
import os
def loadfile(filepath, coding="utf-8"):
    global paths
    if len(paths)>0:
        if filepath[0] not in ["/", "\\\\"] and filepath.find(":")<0:
            filepath = os.path.join(paths[-1], filepath)
    return read(fread(filepath, coding=coding), os.path.dirname(filepath))

pass
g_types['file'] = loadfile
import re
def need_qt(s):
    pt = "^[a-zA-Z0-9\_\.]+$"
    return re.match(pt, s) is None

pass
def out_str(val):
    global g_rtypes
    k = type(val)
    if k not in g_rtypes:
        raise Exception("Not simple value: "+k)
    if k == bool:
        val = str(val).lower()
    rst = "<"+str(val)+", "+g_rtypes[k]+">"
    return rst

pass
def oqt(s):
    if type(s)!= str:
        return out_str(s)
    s = str(s)
    if '"' in s and "'" in s or "\n" in s:
        match = '"""'
        if match in s:
            match = "'''"
        return match+s+match
    if not need_qt(s):
        return s
    return '"'+s+'"'

pass


def output(data, level = 0, simple = True, orders = [], format = False):
    rst = []
    wraps = "()"
    mark_min = simple
    if type(data) == dict:
        wraps = "{}"
        keys = list(data.keys())
        keys1 = []
        for k in keys:
            if k not in orders:
                keys1.append(k)
        keys = orders+keys1
        for key in keys:
            val = data[key]
            if type(val) in [list, dict]:
                val = output(val, level = level+1, simple = simple, orders = orders, format = format).strip()
                mark_min = False
            else:
                val = oqt(val)
            rst.append([oqt(key), val])
        key_map = ": "
        if not format:
            key_map = ":"
        rst = [(key_map.join(k)) for k in rst]
    elif type(data) in [list,tuple]:
        wraps = "[]"
        for val in data:
            if type(val) in [list, dict]:
                val = output(val, level = level+1, simple = simple, orders = orders, format = format).strip()
                mark_min = False
            else:
                val = oqt(val)
            rst.append(val)
    else:
        return oqt(data)
    spt = "\n"
    spt1 = "\n"
    spc0 = " "*(level<<2)
    spc = " "*(level<<2)
    spc1 = " "*((level+1)<<2)
    if mark_min:
        spt1 = ", "
        spc1 = ""
        spc = ""
        spt = ""
    if not format:
        spt1 = ","
        spc1 = ""
        spc = ""
        spt = ""
    rst = [spc1+k for k in rst]
    rs = spt1.join(rst)
    rs = spc0+wraps[0]+spt+rs+spt+spc+wraps[1]
    return rs

pass
dumps = output


def test():
    import sys
    fp = sys.argv[1]
    with open(fp, 'r') as file:
        s = file.read()
    rst = read(s)
    print("rst:", rst)

pass

if __name__=="__main__":
    test()

pass
