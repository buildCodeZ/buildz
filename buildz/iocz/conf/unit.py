
#
from ..ioc.unit import Unit
from ... import dz,xf
from ..ioc.datas import Datas
'''
id|namespace|ns:
deal_id|deal_ns: 
env_id|env_ns:
envs.pub|envs.pri|envs.ns|envs: {
    
}
confs.pub|confs.pri|confs.ns|confs: [

]
confs.pub|confs.pri|confs.ns|confs: {

}
builds: [
    
]

or

[
    ...
]
'''
class ConfUnit(Unit):
    key_ns = ('id', 'namespace', 'ns')
    key_deal_ns = "deal_id,deal_ns,deal_namespace".split(",")
    key_env_ns = "env_id,env_ns,env_namespace".split(",")
    key_confs_pub = "confs.pub,confs".split(",")
    key_confs_pri = "confs.pri,confs.prv".split(",")
    key_confs_ns = "confs.ns,confs.namespace".split(",")
    key_envs_pub = "envs.pub,envs".split(",")
    key_envs_pri = "envs.pri,envs.prv".split(",")
    key_envs_ns = "envs.ns,envs.namespace".split(",")
    key_builds = "builds,build".split(",")
    def init(self, conf, mg):
        if type(conf)==str:
            conf = xf.loads(conf)
        if dz.islist(conf):
            conf = {'confs': conf}
        ns = dz.get_one(conf, self.key_ns)
        deal_ns = dz.get_one(conf, self.key_deal_ns)
        env_ns = dz.get_one(conf, self.key_env_ns)
        super().init(ns, deal_ns, env_ns)
        self.bind(mg)
        self.load(conf)
    def load_confs(self, confs, tag=None):
        rst = []
        if dz.isdict(confs):
            for k,v in confs.items():
                self.conf_key.fill(v, k)
                rst.append(v)
            confs = rst
        for item in confs:
            key,find = self.conf_key(item)
            if find:
                self.set_conf(key, item, tag)
    def load_envs(self, envs, tag=None):
        for key, val in envs.items():
            self.set_env(key, val, tag)
    def load(self, conf):
        tags = [Datas.Key.Pub, Datas.Key.Ns, Datas.Key.Pri]
        keys = [self.key_confs_pub, self.key_confs_ns, self.key_confs_pri]
        for key, tag in zip(keys, tags):
            tag_confs = dz.get_one(conf, key, [])
            self.load_confs(tag_confs, tag)
        keys = [self.key_envs_pub, self.key_envs_ns, self.key_envs_pri]
        for key, tag in zip(keys, tags):
            tag_envs = dz.get_one(conf, key, {})
            self.load_envs(tag_envs, tag)
        builds = dz.get_one(conf, self.key_builds, [])
        for item in builds:
            self.add_build(item)

pass
