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
        maps[key] = val
        i+=1
    return lists, maps

pass

        

