#coding=utf-8
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography import x509
from cryptography.x509.oid import NameOID
import datetime
from buildz import xf
from buildz import fz
def sign(private_key, bs):
    '私钥签名，只返回签名数据，不包括本体'
    return private_key.sign(bs, padding.PKCS1v15(), hashes.SHA256())
def verify(public_key, bs, sig):
    '公钥认证'
    public_key.verify(sig,bs, padding.PKCS1v15(), hashes.SHA256())

pass
def encrypt(public_key, bs):
    '公钥加密'
    encrypted = public_key.encrypt(
        bs,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted

pass
def decrypt(private_key, bs):
    '私钥解密'
    decrypted = private_key.decrypt(
        bs,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted

pass
# 生成RSA私钥
def gen_prv(pwd = None, to_pem=True):
    """
        生成pem格式私钥
    """
    if type(pwd)==str:
        pwd = pwd.encode()
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    if not to_pem:
        return private_key
    # 将私钥序列化为PEM格式
    if pwd is None:
        alg = serialization.NoEncryption()
    else:
        alg = serialization.BestAvailableEncryption(pwd)
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=alg
    )
    return pem

pass
def gen_pub(private_key, pwd = None, to_pem=True):
    """
        从私钥生成pem格式公钥
    """
    if type(private_key)==bytes:
        private_key = load_prv(private_key, pwd)
    # 生成RSA公钥
    public_key = private_key.public_key()
    if not to_pem:
        return public_key
    # 将RSA公钥序列化为PEM格式
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return pem

pass

def load_prv(pem_data, pwd = None):
    if type(pwd)==str:
        pwd = pwd.encode()
    '将PEM格式的私钥反序列化为私钥对象'
    private_key = serialization.load_pem_private_key(pem_data, password=pwd, backend=default_backend())
    return private_key

pass
def load_pub(pem_data):
    '将PEM格式的公钥反序列化为公钥对象'
    public_key = serialization.load_pem_public_key(pem_data, backend=default_backend())
    return public_key

pass
