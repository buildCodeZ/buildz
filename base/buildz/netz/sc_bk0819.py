#
import random,struct,time
from os import urandom
from buildz.netz import certz as certz
from buildz import cryptz
from buildz.netz.tcp import BlockSocket
from threading import get_ident as gid
from buildz import log as logz
from buildz.base import Base
class Verify(Base):
    def init(self, cert=None, prv_key=None, sid=None, cas=None, log=None, do_yield=False):
        self.log = (log or logz.simple())("Verify")
        self.cert=cert
        self.prv_key = prv_key
        self.sid = sid
        self.cas = cas
        self.do_yield=do_yield
    def call(self, skt):
        self.log.debug(f"[TESTZ] Verify sid: {self.sid}, cert: {self.cert}")
        if not self.cert:
            return BlockSocket.wrap(skt, 0)
        if not self.do_yield:
            return verify(skt, self.cert, self.prv_key, self.sid, self.cas, log=self.log)
        obj = verify_yield(skt, self.cert, self.prv_key, self.sid, self.cas, log=self.log)
        def deal():
            rst = wrap_yield(obj)
            if type(rst)!=str and rst is not None:
                encrypt, decrypt=rst
                return wrap_skt(skt, encrypt, decrypt)
        test = deal()
        if type(test)!=str:
            return test
        return deal

def wrap_skt(skt, encrypt, decrypt):
    bskt = BlockSocket.wrap(skt, 0)
    bskt.add('crypt', 'recv', decrypt, 0)
    bskt.add('crypt', 'send', encrypt, 1)
    return bskt
def verify(skt, cert, prv_key, sid=None, cas=None, cls_crypt = cryptz.BlockCrypt, log=None):
    obj = verify_yield(skt.send, skt.recv, cert, prv_key, sid, cas, cls_crypt, log)
    while True:
        rst = wrap_yield(obj)
        if type(rst) !=str:
            encrypt, decrypt = rst
            return wrap_skt(skt, encrypt, decrypt)

def wrap_yield(obj):
    try:
        rst = obj.send(None)
        return rst
    except StopIteration:
        return None


def verify_yield(fc_send, fc_recv, cert, prv_key, sid=None, cas=None, cls_crypt = cryptz.BlockCrypt, log=None):
    '''
        双向验证证书和生成双向加密密码
        运行逻辑：
        发送本地证书
        接收远程证书
        验证远程证书
        验证远程证书的服务id（可选）
        生成发送本地密码和本地随机数，用远程证书公钥加密发送
        接收远程加密数据1，用本地私钥解密获取远程密码和远程随机数
        远程随机数+1,用远程密码加密后发送
        接收远程加密数据2，用本地密码解密后获取远程数值
        验证远程数值=本地随机数+1
        返回本地密码和远程密码
    '''
    log = log or logz.simple()
    log = log.sub("sc.verify")
    cert_obj = certz.load_cert(cert)
    bskt = BlockSocket.wrap(skt, 0)
    # 发送本地证书
    fc_send(cert)
    # 接收远程证书
    yield 'wait read cert'
    remote_cert = fc_recv()
    # 验证远程证书
    err = certz.verify_certs(remote_cert, cas)
    assert err is None, f"verify error: {err}"
    remote_cert = certz.load_cert(remote_cert)
    # 验证远程证书的服务id
    rids = certz.get_sub_val(remote_cert, 'common')
    if sid:
        assert sid in rids, f"{sid} not in {rids}"
    # 生成发送本地密码和本地随机数
    randn = struct.unpack("<I", urandom(4))[0]+int(time.time()*1000000)%1000
    randn = randn & ((1<<32)-1)
    bts_n = struct.pack("<I", randn)
    pwd = urandom(16)
    # 和远程交互的解密对象
    remote_decrypt = cls_crypt(pwd)
    bts = bts_n+remote_decrypt.to_bytes()
    remote_pub = remote_cert.public_key()
    # 远程公钥加密数据并发送
    crypts = certz.encrypt(remote_pub, bts)
    fc_send(crypts)
    # 接收远程加密数据1，用本地私钥解密获取远程密码和远程随机数
    yield 'wait read remote_crypts'
    remote_crypts = fc_recv()
    # 本地私钥解密，获取随机数和远程密码
    remote_bts = certz.decrypt(prv_key, remote_crypts)
    remote_n = remote_bts[:4]
    remote_pwd = remote_bts[4:]
    remote_n = struct.unpack("<I", remote_n)[0]
    # 用远程密码进行数据加密
    remote_encrypt = cls_crypt.from_bytes(remote_pwd)
    # 远程随机数+1,用远程密码加密后发送
    remote_n = struct.pack("<I", remote_n+1)
    remote_n = remote_encrypt.encrypt(remote_n)
    fc_send(remote_n)
    yield 'wait read remote bts'
    # 接收远程加密数据2，用本地密码解密后获取远程数值
    remote_bts = remote_decrypt.decrypt(fc_recv())
    remote_reply_n = struct.unpack("<I", remote_bts)[0]
    # 验证远程数值=本地随机数+1
    assert randn+1 == remote_reply_n
    # 返回本地密码和远程密码
    log.debug("done sc verify")
    yield remote_encrypt.encrypt, remote_decrypt.decrypt


    
