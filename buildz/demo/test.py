#coding=utf-8
from buildz import xf, argx, pyz, ioc, fz
from os.path import dirname, join
class Help:
    def __init__(self, dp, fp):
        fp = join(dp, fp)
        self.text = xf.loads(xf.fread(fp))['text']
    def deal(self):
        print(self.text)

pass
class Deal:
    def __init__(self, conf, deals, default):
        self.deals = {}
        self.default = default
        for md in deals:
            self.deals[md] = {}
            refs = deals[md]
            for key in refs:
                ref = refs[key]
                obj = conf.get(ref)
                self.deals[md][key] = obj
    def run(self):
        args, maps = argx.fetch()
        if len(args)==0:
            return self.default.deal()
        md = args[0]
        help = "h" in maps or "help" in maps
        key = "deal" if not help else "help"
        obj = self.deals[md][key]
        obj.deal()

pass
dp = dirname(__file__)
def test():
    fps = fz.search(join(dp, 'res', 'conf'), ".*\.js")
    confs = ioc.build()
    confs.add_fps(fps)
    confs.get("run")

pass
    
