#

from ..base import Base
from .. import xf, dz, pyz, args as argx, log as logz, path as pathx
from os.path import dirname
gdp = dirname(__file__)
pth = pathx.Path()
pth.set([".", gdp])
"""
根据配置文件运行:
{
    target: 运行包地址
    args: 方法入参
    kwargs: 方法入参map
    fill: [
        {type: conf, pos: int|str}
        {type: pyrun, pos: int|str}
        {type: confpath, pos: int|str}
    ]
    io: {
        stdin: std|file|str
        stdout: std|file
        stderr: std|file
        // file: 
        // [file, filepath, mode]
        // std: 
        // std | [std]
        // str: 
        // [str, content]
    }
    log: filepath|{filepath:filepath, ...}
    dirs: [引入的地址]
    argv: [传入参数]
}
"""
class Runner(Base):
    """
        作为子进程实例运行用的
        python -m buildz.process.pyrun confpath --args="order -x test"
    """
    def run(self, fc, args, kwargs, dirs, argv, stdin, stdout, stderr):
        import sys
        self.argv = sys.argv
        self.stdin = sys.stdin
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        if len(dirs)>0:
            sys.path = sys.path+dirs
        sys.argv = argv
        sys.stdin = stdin
        sys.stdout = stdout
        sys.stderr = stderr
        if type(fc)==str:
            fc = pyz.load(fc)
        if callable(fc):
            return fc(*args, **kwargs)
    def get_fc(self, conf):
        target = conf.get("target")
        assert target is not None
        dirs = conf.get("dirs", [])
        if type(dirs)==str:
            dirs = [dirs]
        dirs = [pth(k) for k in dirs]
        args = conf.get("args", [])
        kwargs = conf.get("kwargs", {})
        return target, args, kwargs, dirs
    def get_io(self, conf, key, src, mode):
        conf = conf.get(key, src)
        if type(conf)==str:
            conf = ["str", conf]
        if type(conf) not in {tuple, list}:
            return conf
        if conf[0]=='str':
            out = io.StringIO(conf)
        elif conf[0]=='std':
            out = src
        elif conf[0]=='file':
            fp = conf[1]
            if len(conf)>2:
                mode = conf[2]
            key = mode+"|"+fp
            if key in self.files:
                out = open(fp, mode)
                self.files[key] = out
            out = self.files[key]
        else:
            assert False, f"unknown io type {conf[0]}'"
        return out
    def get_ios(self, conf):
        import sys
        conf = conf.get("io", {})
        stdin = self.get_io(conf, 'stdin', sys.stdin, 'r')
        stdout = self.get_io(conf, "stdout", sys.stdout, 'w')
        stderr = self.get_io(conf, "stderr", sys.stderr, "w")
        return stdin, stdout, stderr
    def fill(self, conf, conf_path, args, kwargs):
        fills = dz.get_one_default(conf, "fill", "fills", [])
        for obj in fills:
            _type = obj.get("type", "conf")
            target = None
            pos = obj.get("pos", 0)
            if _type=="conf":
                target = conf
            elif _type=="pyrun":
                target=self
            elif _type=="confpath":
                target = confpath
            else:
                assert False, f"unknown fill type: '{_type}'"
            if type(pos)==int:
                args.insert(pos, target)
            else:
                kwargs[pos] = target
        return args, kwargs
    def cmd(self):
        conf = self.fetch()
        confpath = conf.get("confpath", None)
        if confpath:
            confpath = pth(confpath)
            src_conf = conf
            conf = xf.loadf(confpath)
            conf.update(src_conf)
        'done init conf'
        return self.call(conf, confpath)
    def call(self, conf, confpath, argv=None, log=None):
        if argv is None:
            import sys
            argv = sys.argv
        if log is None:
            log = logz.build_conf(conf.get('log', None))
        self.log = log("pyrun")
        'done init conf'
        self.log = logz.build_conf(conf.get('log', None))("pyrun")
        fc, args, kwargs, dirs = self.get_fc(conf)
        stdin, stdout, stderr = self.get_ios(conf)
        args, kwargs = self.fill(conf, confpath, args, kwargs)
        argv = conf.get("argv", argv)
        try:
            return self.run(fc, args, kwargs, dirs, argv, stdin, stdout, stderr)
        finally:
            for k, file in self.files:
                file.flush()
                file.close()
    def init(self):
        args = xf.loads(r"""
        [confpath]
        {
            cf: confpath
        }
        ()
        """)
        self.fetch = argx.Fetch(*args)
        self.files = {}

def test():
    Runner().cmd()

pass
pyz.lc(locals(), test)
