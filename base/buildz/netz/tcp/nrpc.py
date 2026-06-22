

from buildz.base import Base
import base64
import json
from buildz import log as logz
from threading import get_ident as gid
'''
easy rpc by tcp socket
not really rpc
rest in fact
just to make it easy to use

'''
class Server(Base):
    def init(self, obj, skt, fns = None, log=None):
        log = log or logz.simple()
        self.log = log.sub("nrpc.server")
        self.obj = obj
        self.skt = skt
        #skt.enable_v2bs()
        if fns is not None:
            if type(fns)==str:
                fns = fns.split(",")
                fns = [k.strip() for k in fns]
            fns = set(fns)
        self.fns = fns
        self.sends={}
        self.rst = None
    def deal(self, msg):
        #print(f"[DEBUG] call {msg} on {self.obj}")
        fn = msg.get("call")
        out = {}
        if self.fns is not None and fn not in self.fns:
            out['error'] = f"method '{fn}' is not allow to called"
            return out
        if not hasattr(self.obj, fn):
            out['error'] = f"method '{fn}' not exists in obj"
            return out
        args = msg.get("args", [])
        maps = msg.get("maps", {})
        try:
            self.log.debug(f"nrpc server.deal get: {fn}({len(args)}, {len(maps)})")
            fc = getattr(self.obj, fn)
            rst = fc(*args, **maps)
            self.log.debug(f"nrpc server.deal done: {fn}({len(args)}, {len(maps)})")
            out['data'] = rst
        except Exception as exp:
            self.log.error(f"exp: {exp}")
            import traceback as tb
            err = tb.format_exc()
            self.log.error(f"traceback: {err}")
            out['error'] = str(exp)
        return out
    def send(self, msg=None, tid=None):
        tid = tid or gid()
        out = {'data': msg}
        self.skt.send(out)
        self.sends[tid] = True
    def single(self, tid = None):
        self.rst = None
        tid = tid or gid()
        self.log.debug(f"single before recv")
        msg = self.skt.recv()
        self.log.debug(f"single recv: {len(msg)}")
        self.sends[tid]=False
        if msg is None or len(msg)==0:
            #self.rst = 'null'
            self.log.debug(f"single done for null msg")
            return False, 'null'
        if msg.get("close", False):
            #self.rst = msg.get('msg', 'close')
            self.log.debug(f"single done for close msg")
            return False, msg.get('msg', 'close')
        if msg.get("break", False):
            #self.rst = msg.get('msg', 'break')
            self.log.debug(f"single done for break msg")
            return False, msg.get('msg', 'break')
        rst = self.deal(msg)
        self.log.debug(f"single done deal")
        #print(f"[DEBUG] single return: {rst}")
        if not self.sends[tid]:
            self.log.debug(f"single before send {len(rst)}")
            self.skt.send(rst)
            self.log.debug(f"single done send {len(rst)}")
        else:
            self.log.debug(f"single not send mark")
        return True, None
    def run(self):
        return self.call()
    def call(self):
        tid = gid()
        #print(f"[DEBUG] call nrpc.run in {self.obj}")
        run = True
        while run:
            run, rst = self.single(tid)
        return rst
        while self.single(tid):
            pass
        return self.rst
pass

class Client:
    def __init__(self, skt, caches = None, log=None):
        log = log or logz.simple()
        self.log = log.sub("nrpc.client")
        if type(caches)==str:
            caches = caches.split(",")
            caches = [k.strip() for k in caches]
        if type(caches)==list:
            caches = set(caches)
        self.caches = caches
        self.datas = {}
        self.skt = skt
        #skt.enable_v2bs()
    def set_cache(self, fn, args, maps, rst):
        if not self.caches or fn not in self.caches:
            return
        key = f"{fn}(*{args}, **{maps})"
        self.datas[key] = rst
    def get_cache(self, fn, args, maps):
        if not self.caches or fn not in self.caches:
            return None
        key = f"{fn}(*{args}, **{maps})"
        if key not in self.datas:
            return None
        return self.datas[key]
    def __call__(self, fn, *args, **maps):
        self.log.debug(f"nrpc.client.call: {fn}(*{args}, **{maps})")
        rst = self.get_cache(fn, args, maps)
        if rst:
            self.log.debug(f"get from caches: {fn}")
            return rst.get('data', None)
        msg = {'args': args, 'maps': maps}
        msg['call'] = fn
        self.log.debug("call before send")
        self.skt.send(msg)
        self.log.debug("call done send")
        rst = self.skt.recv()
        self.log.debug("call done recv")
        err = rst.get("error", None)
        if err:
            self.log.debug(f"nrpc client get error: {err}")
            raise Exception(err)
        self.log.debug(f"nrpc.client.call done result for {fn}")
        self.set_cache(fn, args, maps, rst)
        return rst.get('data', None)
    def __getattr__(self, fn):
        def wfc(*args, **maps):
            return self.__call__(fn, *args, **maps)
        return wfc
    def breaks(self, msg=None):
        out = {'break':True}
        if msg is not None:
            out['msg'] = msg
        self.skt.send(out)
    def close(self, msg=None):
        out = {'close':True}
        if msg is not None:
            out['msg'] = msg
        self.skt.send(out)
        self.skt.close()

pass


