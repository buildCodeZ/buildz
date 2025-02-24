#
from .datas import Datas
from .dataset import Dataset
from .confs import Confs
class Encapes(Datas):
    def init(self, ns=None, id=None, dts=None, unit=None):
        super().init(ns, id, dts)
        self.confs = None
        self.deals = None
        self.deal_key = None
        self.unit = unit
        self.build()
    def build(self):
        if self.unit is None or self.confs is not None:
            return
        self.confs = self.unit.confs
        self.deals = self.unit.deals
        self.deal_key = self.unit.deal_key
    def make(self, key, ns=None, id=None):
        if self.confs is None or self.deals is None or self.deal_key is None:
            return 0,0,0
        conf, ctag, cfind = self.confs.tget(key, ns, id, False)
        if not cfind:
            return 0,0,0
        conf, deal_ns = conf
        encape, conf, upd = self.make_conf(conf, deal_ns, id)
        if upd:
            self.confs.set(key, conf, ctag)
        self.set(key, encape, ctag)
        return encape, ctag, 1
    def make_conf(self, conf, deal_ns=None, id=None):
        deal_key = self.deal_key(conf)
        deal, dtag, dfind = self.deals.tget(deal_key, deal_ns, id, True)
        assert dfind
        encape, conf, upd = deal(conf, self.unit)
        return encape, conf, upd
    def tget(self, key, src=None,id=None, gfind=True):
        if Confs.is_conf(key):
            encape, conf, upd = self.make_conf(key, self.deals.ns, id)
            return encape, Datas.Key.Pub, 1
        ns, id = self.nsid(src, id)
        obj, tag, find=super().tget(key, ns, id, False)
        if find:
            return obj, tag, find
        obj, tag, find = self.make(key, ns, id)
        if find:
            return obj, tag, find
        if not gfind:
            return 0,0,0
        return self.dts.tget(key, ns, id)
class Encapeset(Dataset):
    '''
        生成对象前的中间层
    '''
    def init(self, ids, mg=None):
        super().init(ids)
        self.confs = None
        self.deals = None
        self.deal_key = None
        self.mg = None
        self.bind(mg)
    def bind(self, mg):
        if self.mg==mg:
            return self
        self.mg = mg
        self.confs = mg.confs
        self.deals = mg.deals
        self.deal_key = mg.deal_key
        return self
    def make(self, key, ns=None, id = None):
        conf, cid, keys, ctag, cfind = self.confs.get(key, ns, id)
        if not cfind:
            return 0,0,0,0,0
        conf, deal_ns = conf
        encape, conf, upd  = self.make_conf(conf, deal_ns, id, cid)
        if cid in self.objs:
            obj = self.objs[id]
            if ns != obj.ns:
                ids_ns = self.ids(obj.ns)
                keys_ns = keys[:len(ids_ns)]
                assert ids_ns == keys_ns, f"{ids_ns}!={keys_ns}"
                keys = keys[len(ids_ns):]
                key = self.ids.id(keys)
            self.objs[cid].set(key, encape, ctag)
            if upd:
                self.confs.objs[cid].set(key, conf, ctag)
        else:
            self.set(key, encape, ns, ctag)
        return encape, cid, keys, ctag, 1
    def make_conf(self, conf, deal_ns=None, id=None,cid=None):
        deal_key = self.deal_key(conf)
        deal, dtag, dfind = self.deals.tget(deal_key, deal_ns, id)
        assert dfind
        unit = self.mg.get_unit(cid)
        encape, conf, upd = deal(conf, unit)
        return encape, conf, upd 
    def get(self, key, ns=None, id=None):
        if Confs.is_conf(key):
            encape, conf, upd = self.make_conf(key, None, id)
            return encape, None, None, Datas.Key.Pub, 1
        obj, eid, keys, tag, find = super().get(key, ns, id)
        if find:
            return obj, eid, keys, tag, find
        return self.make(key, ns, id)

    