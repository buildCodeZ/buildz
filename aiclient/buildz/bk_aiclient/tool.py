
from buildz import pyz, xf, fz, path as pathz, dz, log as logz
from os.path import join, dirname, isfile
from os import listdir
from .caches import Caches
import sys
pkg_dir = dirname(__file__)
tl_dp = join(pkg_dir, "skills")
'''
confs/dp/conf.js:
[
    {
        @fc: ...
        @folder: 
        @depends: [...]
        @depend_skills: [...]
        name: ...
        ...
    }
]
'''
class NoSkillFound(Exception):
    def __init__(self, name, src=None):
        req = ""
        if src is not None:
            req = f"required by skill '{src}' "
        msg = f"skill '{name}' {req}not found in local"
        super().__init__(msg)
class ToolsManager:
    def __init__(self, dp=tl_dp, profile=None, log=None):
        dp = dp or tl_dp
        log = log or logz.simple()
        self.dp = dp
        self.pth = pathz.Path(dp)
        self.confs = {}
        self.fcs = {}
        self.log = log("tools")
        self.profile = profile
        self.pkg_dir = pkg_dir
        cache_size = int(profile.get("cache_size", 100))
        key_size = int(profile.get("cache_key_size", 64))
        self.caches = Caches(cache_size,key_size)
    def get_profile(self):
        return self.profile
    def format(self, conf):
        rst = {}
        for k, v in conf.items():
            if k.find("@")==0:
                continue
            if k == 'des' or k == 'desc':
                k = 'description'
            if k =='inputs' or k == 'input':
                k = 'parameters'
            if k == 'req' or k == 'reqs':
                k = 'required'
            rst[k] = v
        inputs = rst.get("parameters")
        if inputs:
            inputs = inputs.get("properties")
        for var, var_conf in inputs.items():
            for k_des in 'des,desc'.split(','):
                if k_des in var_conf:
                    var_conf['description'] = var_conf[k_des]
                    del var_conf[k_des]
        rst = dz.maps(type="function", function=rst)
        return rst
    def add_conf(self, name, maps):
        self.confs[name] = maps
    def add_fc(self, name, fc):
        self.fcs[name] = fc
    def add(self, conf, dp):
        site = conf.get("@folder", "../..")
        dp = self.pth(dp, site)
        fc = conf.get("@fc")
        dep_skills = conf.get("@depend_skills")
        deps = conf.get("@depends")
        name = conf.get("name")
        # self.log.info(f"add skill: {name}")
        # if name != "file.write":
        #     return
        # self.log.info(f"success add skill: {name}")
        assert name is not None
        assert fc is not None
        self.confs[name] = dz.maps(name=name, fc =fc, dp = dp, dep_skills=dep_skills, deps=deps, conf=self.format(conf))
    def clean(self):
        self.confs = {}
        self.fcs = {}
    def scan(self):
        log = self.log("tools.scan")
        dps = listdir(self.dp)
        for dp in dps:
            fp = self.pth(dp, "conf.js")
            scfp = self.pth(dp, "conf.py")
            log.debug(f"scan {dp}: {fp} or {scfp}")
            if isfile(fp):
                log.debug("json exists")
                confs = xf.loadf(fp)
            elif isfile(scfp):
                log.debug("py exists")
                conf_obj = pyz.load("buildz.aiclient.skills."+dp+".conf")
                confs = None
                if hasattr(conf_obj, "build"):
                    confs = conf_obj.build(self)
                elif hasattr(conf_obj, "all"):
                    confs = conf_obj.all
                if confs is None:
                    continue
                if callable(confs):
                    confs = confs()
            else:
                log.debug("not conf.* exists")
                continue
            if type(confs)==dict:
                confs = [confs]
            for conf in confs:
                self.add(conf,  dp)
    def out(self):
        confs = [it['conf'] for it in self.confs.values()]
        return confs
    def get_fc(self, name, src=None, refresh=False):
        if name in self.fcs and not refresh:
            return self.fcs[name]
        if name not in self.confs:
            if name in self.fcs:
                return self.fcs[name]
            raise NoSkillFound(name, src)
        fc, dp, dep_skills, deps = dz.g(self.confs[name], fc=None, dp=None, dep_skills=None, deps=None)
        assert fc is not None, f'unexcept fc is None for skill {name}'
        if deps is not None and len(deps)>0:
            self.log.warn(f"[WARN] deps not impl yet")
        if dep_skills is not None and len(dep_skills)>0:
            for dep in dep_skills:
                self.get_fc(dep, src or dep, refresh)
        if dp is not None and dp not in sys.path:
            sys.path.append(dp)
        if type(fc)==str:
            fc = pyz.load(fc)
        self.fcs[name] = fc
        return fc
    def call(self, name, args):
        try:
            fc = self.get_fc(name)
        except NoSkillFound as exp:
            return str(exp)
        try:
            rst = fc(**args)
            if rst is None:
                rst = "执行成功"
            return str(rst)
        except Exception as exp:
            self.log.warn(f"skill '{name}' called error: {exp}")
            return f"exception in running skill '{name}': {exp}"

pass


