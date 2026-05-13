

from buildz.base import Base
import base64
import json
'''
easy rpc by tcp socket
not really rpc
rest in fact
just to make it easy to use

'''
class Server(Base):
    def init(self, obj, skt, fns = None):
        self.obj = obj
        self.skt = skt
        skt.enable_v2bs()
        if fns is not None:
            if type(fns)==str:
                fns = fns.split(",")
                fns = [k.strip() for k in fns]
            fns = set(fns)
        self.fns = fns
    def deal(self, msg):
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
            out['error'] = str(exp)
        return out
    def single(self):
        msg = self.skt.recv()
        if msg is None or len(msg)==0:
            return False
        if msg.get("close", False):
            return False
        if msg.get("break", False):
            return False
        rst = self.deal(msg)
        #print(f"[DEBUG] single return: {rst}")
        self.skt.send(rst)
        return True
    def call(self):
        while self.single():
            pass
pass

class Client:
    def __init__(self, skt):
        self.skt = skt
        skt.enable_v2bs()
    def __call__(self, fn, *args, **maps):
        msg = {'args': args, 'maps': maps}
        msg['call'] = fn
        self.skt.send(msg)
        rst = self.skt.recv()
        err = rst.get("error", None)
        if err:
            raise Exception(err)
        return rst.get('data', None)
    def __getattr__(self, fn):
        def wfc(*args, **maps):
            return self.__call__(fn, *args, **maps)
        return wfc
    def breaks(self):
        msg = {'break':True}
        self.skt.send(msg)
    def close(self):
        msg = {'close':True}
        self.skt.send(msg)
        self.skt.close()

pass


