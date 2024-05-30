
from .loaderz import mg, buffer, base
from . import file
from .loaderz.deal import nextz, spt, strz, listz, spc, setz, mapz, reval, lrval
class BoolFc:
    def __init__(self, mg):
        trues = [mg.like(k) for k in ["true", "True", "1"]]   
        trues += [1,True] 
        falses = [mg.like(k) for k in ["false", "False", "0"]]
        falses += [0,False]
        self.trues = set(trues)
        self.falses = set(falses)
    def __call__(self, val):
        if val in self.trues:
            return True
        elif val in self.falses:
            return False
        else:
            raise Exception("unknown bool val")

pass
def build_lrval(mgs):
    bl = BoolFc(mgs)
    fcs = lrval.Fcs()
    fcs.set("float", float)
    fcs.set("f", float)
    fcs.set("int", int)
    fcs.set("i", int)
    fcs.set("bool", bl)
    fcs.set("bl", bl)
    fcs.set("null", lambda x:None)
    fcs.set("nil", lambda x:None)
    fcs.set("n", lambda x:None)
    mgs.add(lrval.LRValDeal("<",">",fcs))

pass
def build_val(mgs):
    mgs.add(reval.ValDeal("[\+\-]?\d+", int))
    mgs.add(reval.ValDeal("[\+\-]?\d*\.\d+", float))
    mgs.add(reval.ValDeal("[\+\-]?\d+e[\+\-]?\d+", float))
    mgs.add(reval.ValDeal("null", lambda x:None))
    mgs.add(reval.ValDeal("true", lambda x:True))
    mgs.add(reval.ValDeal("false", lambda x:False))

pass
def build(as_bytes=False):
    mgs = mg.Manager(as_bytes)
    build_val(mgs)
    #1,0,0,1: 没引号当r"..."
    #1,0,1,1: 没引导当"..."
    mgs.add(strz.PrevStrDeal("r'''","'''",0,0,0))
    mgs.add(strz.PrevStrDeal('r"""','"""',0,0,0))
    mgs.add(strz.PrevStrDeal("r'","'",1,0,0,1))
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
    mgs.add(setz.SetDeal('='))
    mgs.add(spt.PrevSptDeal(",",1))
    mgs.add(spt.PrevSptDeal(';',1))
    mgs.add(spt.PrevSptDeal('\n'))
    build_lrval(mgs)
    mgs.add(listz.ListDeal("(", ")"))
    mgs.add(listz.ListDeal("[", "]"))
    mgs.add(mapz.MapDeal("{", "}"))
    mgs.add(nextz.PrevNextDeal())
    return mgs

pass
def load(read, as_bytes = False):
    mgs = build(as_bytes)
    return msg.loads(read)
def loads(s):
    mgs = build(type(s)==bytes)
    #input = buffer.BufferInput(s)
    return mgs.loads(s)

pass

def loadf(fp, bts = False):
    if bts:
        s = file.bread(fp)
    else:
        s = file.fread(fp)
    return loads(s)

pass
