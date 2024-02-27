
from xf import loads
from loader import mg, buffer

from loader.deal import nextz, spt, strz, listz, spc, setz, mapz, reval
s = r"""test,'test string',
test enter
"    kong ge  "
[1,2,,3, " asdf ", hehe]1.23
{1:2,3:[4,5,6]}true,false,truefalse,null,None
#asdf
[]
"""
s=r"""
{
    a:b,
    test: ???
    id: 123
    cid: '123'
    content: '''hehe
    hehehe
    '''
    b:,#test
    a:[1,2,3,]
    v:{
        a:r"xx\n"
        b:"\n"
        c:d
    }
}
"""
def build_val(mgs):
    mgs.add(reval.ValDeal("[\+\-]?\d+", int))
    mgs.add(reval.ValDeal("[\+\-]?\d+\.\d+", float))
    mgs.add(reval.ValDeal("[\+\-]?\d+e[\+\-]?\d+", float))
    mgs.add(reval.ValDeal("null", lambda x:None))
    mgs.add(reval.ValDeal("true", lambda x:True))
    mgs.add(reval.ValDeal("false", lambda x:False))

pass
mgs = mg.Manager()
mgs.add(spc.PrevSpcDeal())
build_val(mgs)
mgs.add(strz.PrevStrDeal("r'''","'''",0,0,0))
mgs.add(strz.PrevStrDeal('r"""','"""',0,0,0))
mgs.add(strz.PrevStrDeal("r'","'",1,0,0))
mgs.add(strz.PrevStrDeal('r"','"',1,0,0))
mgs.add(strz.PrevStrDeal("###","###",0,1))
mgs.add(strz.PrevStrDeal("/*","*/",0,1))
mgs.add(strz.PrevStrDeal("'''","'''",0,0,1))
mgs.add(strz.PrevStrDeal('"""','"""',0,0,1))
mgs.add(strz.PrevStrDeal("#","\n",1,1))
mgs.add(strz.PrevStrDeal("//","\n",1,1))
mgs.add(strz.PrevStrDeal("'","'",1,0,1))
mgs.add(strz.PrevStrDeal('"','"',1,0,1))
mgs.add(setz.SetDeal(':'))
mgs.add(spt.PrevSptDeal(',',1))
mgs.add(spt.PrevSptDeal('\n'))
mgs.add(listz.ListDeal("[", "]"))
mgs.add(mapz.MapDeal("{", "}"))
mgs.add(nextz.PrevNextDeal())
input = buffer.BufferInput(s)
queue = mgs.load(input)
print(queue)
#for k in queue:
#    print(k)
#
#pass
print(mgs.pos.get())