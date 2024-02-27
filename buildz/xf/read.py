
from .loader import mg, buffer

from .loader.deal import nextz, spt, strz, listz, spc, setz, mapz, reval

def build_val(mgs):
    mgs.add(reval.ValDeal("[\+\-]?\d+", int))
    mgs.add(reval.ValDeal("[\+\-]?\d+\.\d+", float))
    mgs.add(reval.ValDeal("[\+\-]?\d+e[\+\-]?\d+", float))
    mgs.add(reval.ValDeal("null", lambda x:None))
    mgs.add(reval.ValDeal("true", lambda x:True))
    mgs.add(reval.ValDeal("false", lambda x:False))

pass
def build():
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
    return mgs

pass
def load(read):
    mgs = build()
    return msg.load(read)
def loads(s):
    mgs = build()
    input = buffer.BufferInput(s)
    return mgs.load(input)

pass
