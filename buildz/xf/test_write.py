
from writer import mg, itemz, base, conf
from writer.deal import listz, mapz, strz, reval
pts = [
    "[\+\-]?\d+",
    "[\+\-]?\d+\.\d+",
    "[\+\-]?\d+e[\+\-]?\d+",
    "null",
    "true",
    "false",
    ".*[\n\r\t\:\[\]\{\}].*"
]
def build():
    mgs = mg.Manager()
    mgs.add(strz.StrDeal('"','"', pts))
    mgs.add(reval.ValDeal(float, lambda x:str(x)))
    mgs.add(reval.ValDeal(int, lambda x:str(x)))
    mgs.add(reval.ValDeal(type(None), lambda x:'null'))
    mgs.add(reval.ValDeal(bool, lambda x:'true' if x else 'false'))
    mgs.add(listz.ListDeal('[',']',','))
    mgs.add(mapz.MapDeal('{','}',':',','))
    return mgs

pass
def dumps(obj):
    cf = conf.Conf()
    cf.set(bytes=0, format=1, deep=0)
    mgs = build()
    return mgs.dump(obj, cf)

pass

from buildz import xconfz as xf
s = r"""
{
    a:b,
    test: ???
    id: 123
    cid: '123'
    content: '''hehe
    hehehe
    '''
    b:xx,
    int: <1,i>
    null: <null, null>
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
    obj = xf.loads(s)
    rs = dumps(obj)
    print(obj)
    print(rs)

pass
test()


r"""

cd D:\rootz\python\gits\buildz_upd\buildz\xf

python test_write.py



"""