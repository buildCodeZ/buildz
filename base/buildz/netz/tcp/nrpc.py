

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
        self.log = log
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
            fc = getattr(self.obj, fn)
            rst = fc(*args, **maps)
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
        msg = self.skt.recv()
        #print(f"[NRPC] server get msg: {msg}")
        self.sends[tid]=False
        if msg is None or len(msg)==0:
            #self.rst = 'null'
            return False, 'null'
        if msg.get("close", False):
            #self.rst = msg.get('msg', 'close')
            return False, msg.get('msg', 'close')
        if msg.get("break", False):
            #self.rst = msg.get('msg', 'break')
            return False, msg.get('msg', 'break')
        rst = self.deal(msg)
        #print(f"[DEBUG] single return: {rst}")
        if not self.sends[tid]:
            self.skt.send(rst)
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
        self.log = log
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
            return rst.get('data', None)
        msg = {'args': args, 'maps': maps}
        msg['call'] = fn
        self.skt.send(msg)
        rst = self.skt.recv()
        err = rst.get("error", None)
        if err:
            raise Exception(err)
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


