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
class CryptBase:
    '''
        基础类，不可直接调用
    '''
    def __init__(self, pwd, coding = "utf-8", hash_pwd=True):
        self.coding = coding
        pwd = self.s2bytes(pwd)
        if hash_pwd:
            # 32
            pwd = hashlib.md5(pwd).hexdigest().encode("ascii")
        self.pwd = pwd
    def build(self, iv=None):
        self.iv = iv
        self.cipher = Cipher(algorithms.AES(self.pwd), modes.CBC(self.iv))
        self.padding = padding.PKCS7(algorithms.AES.block_size)
        self.hash_obj = hashlib.md5()
    def reset(self):
        self.build(self.iv)
    def s2bytes(self, data):
        if type(data) == str:
            data = data.encode(self.coding)
        return data

class Encrypt(CryptBase):
    """
        md5 hash + aes 加密
        加密方式：
            aes(data+md5(data))
    """
    def __init__(self, pwd, iv=None, coding = "utf-8", iv2dt=True, hash_pwd = True):
        super().__init__(pwd, coding, hash_pwd)
        self.iv2dt = iv2dt
        self.build(iv)
    def build(self, iv=None):
        if iv is None:
            iv = os.urandom(16)
        super().build(iv)
        self.encryptor = self.cipher.encryptor()
        self.padder = self.padding.padder()
        self.hash_obj.update(self.iv)
        self.first = 1
    def __call__(self, data=None, done=False):
        done = done or data is None
        if data is not None:
            data = self.update(data)
        else:
            data = b""
        if done:
            data += self.finalize()
        return data
    def update(self, data):
        data = self.s2bytes(data)
        self.hash_obj.update(data)
        pdt = self.padder.update(data)
        out = self.encryptor.update(pdt)
        if self.first:
            self.first = 0
            if self.iv2dt:
                out = self.iv+out
        return out
    def finalize(self):
        hash = self.hash_obj.hexdigest().encode("ascii")
        pdt = self.padder.update(hash)+ self.padder.finalize()
        out = self.encryptor.update(pdt) + self.encryptor.finalize()
        return out

pass
class Decrypt(CryptBase):
    """
        md5 hash + aes 解密
        加密方式：
            aes解密成data+hash，校验md5(data)和hash是否一致
            aes(data+md5(data))
        update是解密数据，会保留解密后的最后32位不返回，留作最后当作hash值
    """
    def __init__(self, pwd, iv=None, coding = "utf-8", iv2dt=True, hash_pwd = True):
        super().__init__(pwd, coding, hash_pwd)
        self.iv = iv
        self.iv2dt = iv2dt
        if iv is not None:
            self.build(iv)
    def __call__(self, data=None, done=False):
        done = done or data is None
        if data is not None:
            data = self.update(data)
        else:
            data = b""
        if done:
            data += self.finalize()
        return data
    def reset(self):
        if self.iv2dt:
            self.iv = None
        else:
            super().reset()
    def build(self, iv):
        super().build(iv)
        self.unpadder = self.padding.unpadder()
        self.decryptor = self.cipher.decryptor()
        self.remain = b""
    def update(self, data):
        data = self.s2bytes(data)
        if self.iv is None:
            iv = data[:16]
            self.build(iv)
            data = data[16:]
            self.hash_obj.update(iv)
        pdt = self.decryptor.update(data)
        out = self.unpadder.update(pdt)
        out = self.remain+out
        if len(out)>32:
            self.remain = out[-32:]
            out = out[:-32]
            self.hash_obj.update(out)
        else:
            self.remain=out
            out = b""
        return out
    def finalize(self):
        pdt = self.decryptor.finalize()
        out = self.unpadder.update(pdt)+self.unpadder.finalize()
        out = self.remain+out
        self.remain = out[-32:]
        out = out[:-32]
        self.hash_obj.update(out)
        hash = self.hash_obj.hexdigest().encode("ascii")
        if self.remain != hash:
            raise Exception("Error pwd")
        return out

pass

class BlockCrypt:
    def __init__(self, pwd, iv=None, iv2dt = True, hash_pwd=True):
        if hash_pwd:
            pwd = hashlib.md5(pwd).hexdigest().encode("ascii")
        self.pwd = pwd
        self.iv = iv
        self.iv2dt = iv2dt
        self.encryptor=None
        self.decryptor=None
    def encrypt(self, dts, done=True):
        if len(dts)==0:
            return dts
        self.encryptor = self.encryptor or Encrypt(self.pwd, self.iv, "utf-8", self.iv2dt, False)
        rst = self.encryptor(dts, done)
        self.encryptor.reset()
        return rst
    def decrypt(self, dts, done=True):
        if len(dts)==0:
            return dts
        self.decryptor = self.decryptor or Decrypt(self.pwd, self.iv, "utf-8", self.iv2dt, False)
        rst = self.decryptor(dts, done)
        self.decryptor.reset()
        return rst
    @staticmethod
    def from_bytes(dt):
        if len(dt)==32:
            pwd = dt
            iv = None
            iv2dt=True
        else:
            pwd = dt[:32]
            iv = dt[32:]
            iv2dt=False
        return BlockCrypt(pwd, iv, iv2dt, False)
    def to_bytes(self):
        if self.iv2dt:
            # 16
            return self.pwd
        self.iv = self.iv or os.urandom(16)
        # 32+16
        return self.pwd+self.iv
