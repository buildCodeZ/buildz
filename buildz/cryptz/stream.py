#coding=utf-8
import base64
import hashlib
try:
    import cryptography
except ModuleNotFoundError as exp:
    raise Exception("require package cryptography, install it by 'python3 -m pip install cryptography'")
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, padding
import os
def xors(a,b):
    try:
        import numpy as np
        na = np.array(bytearray(a))
        nb = np.array(bytearray(b))
        rst = na^nb
        return rst.tobytes()
    except ModuleNotFoundError:
        rst = [i^j for i,j in zip(a,b)]
        return bytes(rst)

'''
字节流处理
'''
class ByteStream:
    """
        md5 hash + aes 加密
        加密方式大概逻辑：
            datas = (datas || hash(datas)) ^ base[:size]
            base = base[size:]+aes(md5(base))
            return datas
        这里其实应该新建个线程，不断生成密码流让密码流达到固定大小，达到提前生成密码流，节省时间的目的，否则和实时加密区别不大，但先不管了
    """
    def __init__(self, pwd = None, base = None, iv = None, crypt_hash = 32):
        self.cipher = None
        self.crypt_hash = crypt_hash
        if pwd is not None:
            self.init(pwd, base, iv)
    def init(self, pwd, base, iv):
        if iv is None:
            iv = os.urandom(16)
        if base is None:
            base = os.urandom(32)
        obj = hashlib.md5(pwd)
        self.pwd = obj.hexdigest().encode("ascii")
        self.iv = iv
        self.base = hashlib.md5(base).hexdigest().encode("ascii")
        self.cipher = Cipher(algorithms.AES(self.pwd), modes.CBC(self.iv))
        self.encryptor = self.cipher.encryptor()
        self.codes = b""
        #self.padder = padding.PKCS7(algorithms.AES.block_size).padder()
    def next(self):
        data = self.base
        nxt = hashlib.md5(data).hexdigest().encode("ascii")
        self.base = nxt
        out = self.encryptor.update(data)
        return out
    def encrypt(self, dts):
        if self.crypt_hash>0:
            hash = hashlib.md5(dts).hexdigest().encode("ascii")
            dts += hash[:self.crypt_hash]
        return self.update(dts)
    def decrypt(self, dts):
        dts = self.update(dts)
        if self.crypt_hash>0:
            hash = dts[-self.crypt_hash:]
            dts = dts[:-self.crypt_hash]
            vhash = hashlib.md5(dts).hexdigest().encode("ascii")
            assert hash == vhash
        return dts
    def update(self, dts):
        l = len(dts)
        while len(self.codes)<l:
            self.codes+=self.next()
        tmp = self.codes[:l]
        self.codes = self.codes[l:]
        rst = xors(dts, tmp)
        return rst
        # src = np.array(bytearray(dts))
        # cds = np.array(bytearray(self.codes[:l]))
        # self.codes = self.codes[l:]
        # rst = src^cds
        # return rst.tobytes()

pass

