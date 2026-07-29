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
    def init(self, cert=None, prv_key=None, sid=None, cas=None, log=None):
        self.log = (log or logz.simple())("Verify")
        self.cert=cert
        self.prv_key = prv_key
        self.sid = sid
        self.cas = cas
    def call(self, skt):
        self.log.debug(f"[TESTZ] Verify sid: {self.sid}, cert: {self.cert}")
        if not self.cert:
            return BlockSocket.wrap(skt)
        return verify(skt, self.cert, self.prv_key, self.sid, self.cas, log=self.log)
def verify(skt, cert, prv_key, sid=None, cas=None, cls_crypt = cryptz.BlockCrypt, log=None):
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
    log.debug(f"start sc verify: {skt}")
    cert_obj = certz.load_cert(cert)
    bskt = BlockSocket.wrap(skt)
    log.debug(f"sc verify bskt: {bskt}")
    # 发送本地证书
    log.debug(f"[{gid()}] before send cert")
    bskt.send(cert)
    log.debug(f"[TESTZ] send cert: {cert}")
    # 接收远程证书
    log.debug(f"[{gid()}] before get remote_cert")
    remote_cert = bskt.recv()
    log.debug(f"[TESTZ] recv remote_cert: {remote_cert}")
    # 验证远程证书
    log.debug(f"[{gid()}] C")
    err = certz.verify_certs(remote_cert, cas)
    assert err is None, f"verify error: {err}"
    remote_cert = certz.load_cert(remote_cert)
    # 验证远程证书的服务id
    log.debug(f"[{gid()}] D")
    rids = certz.get_sub_val(remote_cert, 'common')
    if sid:
        assert sid in rids, f"{sid} not in {rids}"
    # 生成发送本地密码和本地随机数
    log.debug(f"[{gid()}] E")
    randn = struct.unpack("<I", urandom(4))[0]+int(time.time()*1000000)%1000
    randn = randn & ((1<<32)-1)
    bts_n = struct.pack("<I", randn)
    pwd = urandom(16)
    remote_decrypt = cls_crypt(pwd)
    log.debug(f"before add crypt to recv")
    bskt.add('crypt', 'recv', remote_decrypt.decrypt, 0)
    log.debug(f"done add crypt to recv")
    bts = bts_n+remote_decrypt.to_bytes()
    remote_pub = remote_cert.public_key()
    crypts = certz.encrypt(remote_pub, bts)
    log.debug(f"before send crypts")
    bskt.send(crypts)
    log.debug(f"done send crypts")
    # 接收远程加密数据1，用本地私钥解密获取远程密码和远程随机数
    log.debug(f"[{gid()}] before recv remote_crypts")
    remote_crypts = bskt.recv()
    log.debug(f"[{gid()}] done recv remote_crypts")
    remote_bts = certz.decrypt(prv_key, remote_crypts)
    remote_n = remote_bts[:4]
    remote_pwd = remote_bts[4:]
    remote_n = struct.unpack("<I", remote_n)[0]
    remote_encrypt = cls_crypt.from_bytes(remote_pwd)
    log.debug(f"before add crypt to send")
    bskt.add('crypt', 'send', remote_encrypt.encrypt, 1)
    log.debug(f"done add crypt to send")
    # 远程随机数+1,用远程密码加密后发送
    remote_n = struct.pack("<I", remote_n+1)
    #bskt.adds('crypt', 1, send=remote_encrypt.encrypt, recv = remote_decrypt.decrypt)
    log.debug(f"[{gid()}] before send remote_n")
    bskt.send(remote_n)
    log.debug(f"[{gid()}] done send remote_n")
    #remote_bts = remote_encrypt.encrypt(remote_n)
    #bskt.send(remote_bts)
    # 接收远程加密数据2，用本地密码解密后获取远程数值
    log.debug(f"[{gid()}] before recv remote_bts")
    remote_bts = bskt.recv()
    log.debug(f"[{gid()}] done recv remote_bts")
    #remote_bts = remote_decrypt.decrypt(remote_bts)
    remote_reply_n = struct.unpack("<I", remote_bts)[0]
    # 验证远程数值=本地随机数+1
    #log.debug(f"[{gid()}] I")
    assert randn+1 == remote_reply_n
    # 返回本地密码和远程密码
    #log.debug(f"[{gid()}] J")
    log.debug("done sc verify")
    return bskt



    
