
from . import lst, subrun
from buildz import args as argx, xf, fz, log as logz, path as pathx
from buildz.base import Base
import sys
from os.path import dirname
'''
fps: [...]
wait_sec: 0.1
target: ...

'''
xargs = r"""
[confpath]
{
sec:wait_sec
f:fps
fp:fps
t:target
}
()
"""
gdp = dirname(__file__)
pth = pathx.Path()
pth.set([".", gdp])
args = xf.loads(xargs)
fetch =argx.Fetch(*args)
class Runner(Base):
    def cmd(self):
        conf = fetch()
        src_conf = conf
        confpath = conf.get("confpath")
        if confpath:
            confpath = pth(confpath)
            src_conf = conf
            conf = xf.loadf(confpath)
            conf.update(src_conf)
        return self.call(conf)
    def call(self, conf, argv=None, log=None):
        if argv is None:
            import sys
            argv = sys.argv[1:]
        if log is None:
            log = logz.build_conf(conf.get('log', None))
        log = log('fpscall')
        self.log = log
        self.argv = argv
        fps = conf.get("fps", [])
        wait_sec = conf.get("wait_sec", 0.1)
        if type(fps)==str:
            fps = [fps]
        fps = [pth(k) for k in fps]
        fcs = lst.FcFpsListener(wait_sec)
        fcs.adds(fps)
        fcs.set_update(self.update)
        fcs.set_deal_exp(self.deal_exp)
        cmds = [sys.executable, "-m", "buildz.process.pyrun"]+self.argv
        self.subrun = subrun.Runner(cmds, self.log)
        fcs.run()
    def update(self, fps):
        self.subrun()
    def deal_exp(self, exp, trs):
        self.log.info(f"call exp: {exp}, trs: {trs}")


if __name__=="__main__":
    Runner().cmd()
