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
    def deal(self):
        self.log.debug(f"[TESTZ] Verify sid: {self.sid}, cert: {self.cert}")
        if not self.cert:
            return None
        if not self.do_yield:
            return None
        obj = verify_yield(self.cert, self.prv_key, self.sid, self.cas, log=self.log)
        deal_fc = wrap_yield(obj)
        # deal_fc([recvs]) => [sends], rst
        return deal_fc
    def call(self, skt):
        self.log.debug(f"[TESTZ] Verify sid: {self.sid}, cert: {self.cert}")
        if not self.cert:
            return BlockSocket.wrap(skt, 0)
        skt = BlockSocket.wrap(skt, 0)
        if not self.do_yield:
            return verify(skt, self.cert, self.prv_key, self.sid, self.cas, log=self.log)
        obj = verify_yield(self.cert, self.prv_key, self.sid, self.cas, log=self.log)
        deal_fc = wrap_yield_skt(obj, skt)
        def deal():
            rst = deal_fc()
            if rst is not None:
                encrypt, decrypt=rst
                self.log.debug("done sc verify")
                return wrap_skt(skt, encrypt, decrypt)
            return None
        test = deal()
        if test is not None:
            return test
        return deal

def wrap_skt(skt, encrypt, decrypt):
    bskt = BlockSocket.wrap(skt, 0)
    bskt.add('crypt', 'recv', decrypt, 0)
    bskt.add('crypt', 'send', encrypt, 1)
    return bskt
def verify(skt, cert, prv_key, sid=None, cas=None, cls_crypt = cryptz.BlockCrypt, log=None):
    skt = BlockSocket.wrap(skt, 0)
    obj = verify_yield(cert, prv_key, sid, cas, cls_crypt, log)
    deal = wrap_yield_skt(obj, skt)
    rst = deal()
    while rst is None:
        rst = deal()
    encrypt, decrypt = rst
    return wrap_skt(skt, encrypt, decrypt)

def wrap_yield_skt(obj, skt):
    deal = wrap_yield(obj)
    first_call=[True]
    def fc():
        recvs = []
        if first_call[0]:
            first_call[0]=False
        else:
            recvs.append(skt.recv())
        sends, rst = deal(recvs)
        for snd in sends:
            skt.send(snd)
        return rst
    return fc

def wrap_yield(obj, init=False):
    first_call=[not init]
    def fc(recvs=[]):
        if type(recvs) not in {list, tuple}:
            recvs = [recvs]
        sends,rst=[],None
        if first_call[0]:
            sends, rst = obj.send(None)
            first_call[0]=False
        for recv in recvs:
            try:
                snds, rst = obj.send(recv)
                sends+=snds
            except StopIteration:
                pass
        return sends, rst
    return fc
pass
def verify_yield(cert, prv_key, sid=None, cas=None, cls_crypt = cryptz.BlockCrypt, log=None):
    '''
        返回generator对象，建议用wrap_yield封装
        封装后使用:
            fc(recvs=[])=>[sends], rst
            入参是读取的数据的队列，可以为空
            返回：
                sends: 要输出的数据的队列
                rst: 最终生成的结果
            如果没有执行结束，rst返回的只会是None，rst返回不是None的时候说明执行结束，不用再调用了
        yield: [send], out=None
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
    # 发送本地证书
    # 接收远程证书
    remote_cert = yield [cert],None
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
    # 接收远程加密数据1，用本地私钥解密获取远程密码和远程随机数
    remote_crypts = yield [crypts], None
    # 本地私钥解密，获取随机数和远程密码
    remote_bts = certz.decrypt(prv_key, remote_crypts)
    remote_n = remote_bts[:4]
    remote_pwd = remote_bts[4:]
    remote_n = struct.unpack("<I", remote_n)[0]
    r_n = remote_n
    # 用远程密码进行数据加密
    remote_encrypt = cls_crypt.from_bytes(remote_pwd)
    # 远程随机数+1,用远程密码加密后发送
    remote_n = struct.pack("<I", remote_n+1)
    remote_n = remote_encrypt.encrypt(remote_n)
    # 接收远程加密数据2，用本地密码解密后获取远程数值
    remote_bts = yield [remote_n], None
    remote_bts = remote_decrypt.decrypt(remote_bts)
    remote_reply_n = struct.unpack("<I", remote_bts)[0]
    # 验证远程数值=本地随机数+1
    assert randn+1 == remote_reply_n
    # 返回本地密码和远程密码
    log.debug("done sc verify")
    #yield [], [remote_encrypt.encrypt, remote_decrypt.decrypt]
    yield [], [CryptCount(remote_encrypt, r_n+1).encrypt, CryptCount(remote_decrypt, remote_reply_n).decrypt]


class CryptCount(Base):
    '''
        加解密里加个随机数防止重发
        接受和发送分成两个独立的随机数
    '''
    N_1 = (1<<32)-1
    N = 1<<32
    def init(self, crypt, count):
        self.crypt = crypt
        self.count=count
    def encrypt(self, bts):
        self.count=(self.count+1)&self.N_1
        bts_n = struct.pack("<I", self.count)
        return self.crypt.encrypt(bts_n+bts)
    def decrypt(self, bts):
        bts = self.crypt.decrypt(bts)
        assert len(bts)>=4
        bts_n = bts[:4]
        bts=bts[4:]
        count = struct.unpack("<I", bts_n)[0]
        if count<self.count:
            count+=self.N
        diff = count-self.count
        assert diff>0 and diff<3
        self.count=count&self.N_1
        return bts

pass
