from .base import Base, fcBase
from buildz import xf,pyz
class EnvExp(Exception):
    def __init__(self, id):
        super().__init__(f"EnvExp id not found: '{id}'")
class BuildEnv(Base):
    """
        3种从环境获取参数的方式:
            从系统环境获取
            从命令行输入参数获取
            从本对象环境数据获取
        2种设置环境参数方式：
            设置到系统环境
            设置到本对象环境数据
    """
    def init(self, conf):
        self.conf = conf
        self.builds = {
        }
    def build_args(self):
        pass
    def build_conf(self, ids, flush, flush_list, exp, default):
        return Env(ids, None, flush, flush_list, exp, default)
    def deal(self, mg, args, spt, eglobal, orders, from_args, flush, flush_list, exp, default):
        envs = []
        env = None
        ids = ids.Ids(spt)
        if 'conf' not in orders:
            orders.append('conf')
        for order in orders:
            _env = self.builds[order](ids, flush, flush_list, exp, default)
            if order == 'conf':
                env = _env
            envs.append(_env)
        env = Envs(envs, env)
        return env
    def call(self, mg, conf, args):
        args, maps = self.conf([], conf)
        return self.deal(mg, args, **maps)

pass
class Env(Base):
    def _get(self, id):
        return xf.dhget(self.maps, id)
    def _set(self, id, val):
        return xf.dset(self.maps, id, val)
    def _has(self, id):
        return xf.dhas(self.maps, id)
    def _del(self, id):
        return xf.dremove(self.maps, id)
    def _fill(self, maps):
        return xf.fill(maps, self.maps)
    def init(self, ids=None, maps=None, flush=True, flush_list = False):
        self.flush_list = flush_list
        self.ids = ids
        self.flush = flush
        if maps is None:
            maps = {}
        if flush:
            maps=xf.flush_maps(maps, self.ids.ids, flush_list)
        self.maps = maps
    def update(self, maps, flush=None, flush_list=None):
        flush = pyz.nnull(flush, self.flush)
        flush_list = pyz.nnull(flush_list, self.flush_list)
        if flush:
            maps = xf.flush_maps(maps, self.ids.ids, flush_list)
        self._fill(maps)
    def has(self, id, flush=None):
        flush = pyz.not_null(flush, self.flush)
        full_id = id
        if flush:
            ids = self.ids.ids(id)
        else:
            ids = id
        return self._has(ids)
    def get(self, id, flush=None):
        flush = pyz.not_null(flush, self.flush)
        full_id = id
        if flush:
            ids = self.ids.ids(id)
        else:
            ids = id
        return self._get(ids)
    def set(self, id, val, flush=None):
        flush = pyz.not_null(flush, self.flush)
        if flush:
            id = self.ids.ids(id)
        self._set(self.maps, id, val)
 
class SysEnv(Env):
    def _get(self, id, exp_def=None):
        sysdt = os.getenv(id)
        return sysdt
    def _has(self, id):
        dt = self._get(id)
        return dt is not None
    def init(self, ids):
        super().init(ids, flush=False)

class Envs(Env):
    def init(self, envs, env):
        self.envs = envs
        self.env = env
    def get(self, id):
        for env in self.envs:
            if env.has(id):
                return env.get(id)
        return self.env.get(id)
    def set(self, id, val, *a,**b):
        return self.env.set(id, val, *a,**b)
    def has(self, id):
        for env in self.envs:
            if env.has(id):
                return True
        return self.env.has(id)
    def update(self, maps, *a,**b):
        return self.env.update(maps,*a,**b)
