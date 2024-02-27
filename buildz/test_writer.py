

from buildz import xconfz as xfz
import xf
import json 
s = r"""
{
    a:b,
    test: ???
    id: 123
    cid: '123' # nothing here
    /*
    >>>>>>>
    */
    content: '''hehe
    hehehe
    '''
    b:xx,
    int: 1
    null: null
    a:[1,2,3,]
    v:{
        a:r"xx\n"
        b:"\n"
        c:d
        url:"http://test.com.cn"
    }
}
"""
def test():
    obj = xfz.loads(s)
    obj = xf.loads(s)
    rs = xf.dumps(obj,format=0,deep=0,json_format=1)
    print(obj)
    print(json.dumps(obj))
    print(rs)

pass
test()


r"""

cd D:\rootz\python\gits\buildz_upd\buildz\xf

python test_write.py



"""