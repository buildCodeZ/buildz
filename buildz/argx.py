#coding=utf-8
import sys
def fetch(argv = None):
    r"""
    format: a b c -a 123 -b456 --c=789 +d  -x"??? ???" y z
    return: [a,b,c,y,z], {a:123,b:456,c:789,d:1,x:'??? ???'}
    """
    if argv is None:
        argv = sys.argv[1:]
    lists, maps = [],{}
    argv = [str(k).strip() for k in argv]
    argv = [k for k in argv if k!=""]
    i = 0
    while i<len(argv):
        v = argv[i]
        if v in ["-", "--", "+"]or v[0] not in "+-":
            lists.append(v)
            i+=1
            continue
        if v[0] == "+":
            key = v[1:]
            val = 1
        else:
            if v[1]=="-":
                kv = v[2:]
                x = kv.split("=")
                key = x[0]
                val = "=".join(x[1:])
                if len(val)==0:
                    val = 1
            else:
                key = v[1]
                if len(v)>2:
                    val = argv[2:]
                else:
                    if i+1>=len(argv):
                        val = 1
                    else:
                        val = argv[i+1]
                        i+=1
        if key not in maps:
            maps[key] = []
        maps[key].append(val)
        i+=1
    for k in maps:
        v = maps[k]
        if len(v)==1:
            maps[k] = v[0]
    return lists, maps

pass

        

