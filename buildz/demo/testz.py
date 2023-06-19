s = r'''
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
'''
s = r"""
[as/df, 'asdf', t est , 测试,'''
''',,]
{
    x:"\""
    a=0, #note 1
    b= 1;
    c= x;
    d= [a,b,c]y=0,
    y = 1,
    val = <1, i>
    bl = 1|b
    x = 0|nil
}
"""
try:
    from buildz import build
except:
    import sys
    import os
    sys.path.append(os.path.abspath("./../.."))
    from buildz import build
from buildz import xconfz as confz

import os
os.system("clear")
rst= confz.loads(s)
print(type(rst))
print(rst)
from buildz import confz as bk

print(bk.dumps(rst, format=True))
