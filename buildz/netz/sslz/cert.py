#coding=utf-8
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography import x509
from cryptography.x509.oid import NameOID
import datetime
from buildz import xf, pyz
from buildz import fz
from .pk import *
__doc__='''
cert和csr的区别：
    csr是用自己的私钥签名，对象里包含自身信息和公钥（用公钥可以验证私钥签名是否有效），用于发给证书机构，让证书机构验证和签发cert用的
    cert是被证书机构私钥签名，包含被签对象自身信息和公钥，以及签名机构的信息（无公钥），对外使用
        cert验证过程:
            根据签名机构信息查找签名机构的证书（验证方要自己存储签名机构公钥）
    cert链：
        被签对象的cert，中间节点的cert，CA(根签名机构)的cert（自签名，可以不包含）
        验证过程:
            用上层节点的cert的公钥验证下层节点cert是否是它签名的，
            最后用CA的cert的公钥验证它自己（为了安全，验证方要自己存储CA的自签名cert证书，用自己存的cert的公钥验证cert链的最高层）
'''
def load_names():
    import os
    dp = os.path.dirname(__file__)
    with open(os.path.join(dp, "names.txt"), 'rb') as f:
        s = f.read().decode("utf-8")
    arr = s.split("\n")[1:]
    arr = [k.split(",") for k in arr]
    arr = [[v.strip() for v in k] for k in arr]
    for it in arr:
        it[-1] = it[-1].split("|")
        it[-1] = [k.strip() for k in it[-1] if k.strip()!=""]
    return arr

pass
arr_names = load_names()
dict_names = {k[0]:k for k in arr_names}
def a2n(arr_names):
    rst = {}
    for item in arr_names:
        oid = item[0]
        als = item[3]
        rst[oid] = oid
        for al in als:
            rst[al] = oid
    return rst
al2names = a2n(arr_names)
def get_subject_val(obj, key):
    '从subject（或cert/csr）获取key对应的值，返回列表'
    if key not in al2names:
        return []
    key = al2names[key]
    key = getattr(NameOID, key)
    if not hasattr(obj, 'get_attributes_for_oid') and hasattr(obj, 'subject'):
        obj = obj.subject
    rst = obj.get_attributes_for_oid(key)
    rst = [k.value for k in rst]
    return rst
get_sub_val = get_subject_val
def gen_subject(conf = {}):
    "生成证书的主体信息"
    names = []
    for item in arr_names:
        OID,des,df,als = item
        val = conf.get(OID)
        for al in als:
            if val:
                break
            val = conf.get(al)
        val = val or df
        if val:
            names.append(x509.NameAttribute(getattr(NameOID, OID), val))
    subject = x509.Name(names)
    return subject

pass
def add_extension_dns(builder, dns):
    '添加dns信息，暂不清楚有什么用'
    if type(dns)!=list:
        dns = [dns]    
    dns_arr = [x509.DNSName(k) for k in dns]
    dns_arr = x509.SubjectAlternativeName(dns_arr)
    builder = builder.add_extension(dns_arr, critical=False)
    return builder
def add_extension_ca(builder):
    '添加ca信息（说明当前证书是ca）'
    builder = builder.add_extension(
        x509.BasicConstraints(ca=True, path_length=None),
        critical=True
    )
    return builder
def add_extensions(builder, conf = {}):
    "添加额外信息"
    dns = xf.g(conf, dns = [])
    if len(dns)>0:
        builder = add_extension_dns(builder, dns)
    ca = xf.g(conf, ca = False)
    if ca:
        builder = add_extension_ca(builder)
    return builder

pass

def load_csr(pem):
    '从bytes载入csr对象'
    csr= x509.load_pem_x509_csr(pem)
    return csr 
pass
def load_cert(pem):
    '从bytes载入cert对象'
    cert = x509.load_pem_x509_certificate(pem)
    return cert

def gen_cert(private_key, subject_csr = None, issuer_cert = None, conf={}, to_pem=True, add_chains=True):
    '''
       生成cert或csr
       to_pem=True则返回序列化后的pem的bytes数据
       否则返回cert或csr对象
       private_key: 私钥对象，必须是对象
       subject_csr: 可选值:
                        csr对象或序列化bytes
                        空
                    为空的时候，从conf生成csr对象
       issuer_cert: 可选值:
                        用于签名的cert对象或序列化bytes
                        布尔值(True/False/1/0)
                        空
                    issuer_cert为布尔值True/1的时候，将subject_csr当作cert，也就是自签名
                    issuer_cert为布尔值False/0或空的时候，方法返回csr，否则返回cert
       conf: 配置信息，用于生成csr和cert签名的时候设置日期属性
       to_pem: 是否返回序列化后的bytes
       add_chains: 是否返回证书链，只在to_pem=True, issuer_cert非空并且非布尔值False/0时生效
    '''
    if issuer_cert:
        builder = x509.CertificateBuilder()
    else:
        builder = x509.CertificateSigningRequestBuilder()
    if subject_csr is not None:
        if type(subject_csr)==bytes:
            subject_csr = load_csr(subject_csr)
        subject = subject_csr.subject
        verify_csr(subject_csr)
    else:
        subject = gen_subject(conf)
    builder = builder.subject_name(subject)
    issuer = None
    issuer_src = None
    if issuer_cert:
        if type(issuer_cert) in {bool, int}:
            issuer = subject
        else:
            issuer_src = issuer_cert
            if type(issuer_cert)==bytes:
                issuer_cert = load_cert(issuer_cert)
            issuer = issuer_cert.subject
    if issuer:
        builder = builder.issuer_name(issuer)
        if subject_csr:
            public_key=subject_csr.public_key()
        else:
            public_key = private_key.public_key()
        builder = builder.public_key(public_key)
        builder = builder.serial_number(x509.random_serial_number())
        builder = builder.not_valid_before(datetime.datetime.utcnow() - datetime.timedelta(days=xf.g(conf, valid_before=1)))
        builder = builder.not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=xf.g(conf, valid=365)))
    if subject_csr:
        for extension in subject_csr.extensions:
            builder = builder.add_extension(extension.value, extension.critical)
    else:
        builder = add_extensions(builder, conf)
    # 将证书签名
    certificate = builder.sign(
        private_key=private_key,
        algorithm=hashes.SHA256(),
        backend=default_backend()
    )
    if to_pem:
        certificate = certificate.public_bytes(serialization.Encoding.PEM)
        if add_chains and issuer_src:
            if type(issuer_src)!=bytes:
                issuer_src = issuer_src.public_bytes(serialization.Encoding.PEM)
            certificate += issuer_src
    return certificate
pass

def gen_csr(private_key, conf={}, to_pem=True):
    return gen_cert(private_key, conf=conf, to_pem=to_pem)
pass
def sign_csr(private_key, subject_csr, issuer_cert, conf={}, to_pem=True, add_chains=True):
    assert subject_csr is not None and issuer_cert is not None
    return gen_cert(private_key, subject_csr, issuer_cert, conf, to_pem, add_chains)
def gen_root_cert(private_key, conf={}, to_pem=True):
    return gen_cert(private_key, issuer_cert=True, conf=conf, to_pem=to_pem)
#要生成证书链，是从网站证书开始写入，往上写到根证书
"""
chains.cert文件结构:
网站证书
中间节点证书
...
根证书

该结构保证load_cert(数据)的时候，拿到的是最上面的网站证书
"""
class CertVerifyException(Exception):
    pass

pass
def load_certs(bs):
    '加载证书对象列表'
    spt = b"-----END CERTIFICATE-----"
    pems = bs.split(spt)
    pems = [k+spt for k in pems if k.strip()!=b""]
    certs = [load_cert(pem) for pem in pems]
    return certs
def verify_certs(certs, cas = None, verify_time=True):
    if type(certs)==bytes:
        certs = load_certs(certs)
    if certs is None:
        certs = []
    if type(certs)!=list:
        certs = [certs]
    if len(certs)==0:
        raise CertVerifyException(f"not any cert info in certs")
    if cas is None:
        cas = []
    if type(cas)!=list:
        cas = [cas]
    #cas = [load_cert(ca) for ca in cas]
    roots = {ca.subject:[ca.public_key(), ca.signature_hash_algorithm] for ca in cas}
    #print(f"[TESTZ] verify certs: {len(certs)}")
    for i in range(len(certs)-1):
        #print(f"verify[{i}]")
        curr = certs[i]
        up = certs[i+1]
        err = verify_cert(curr, up.public_key(), verify_time, up.signature_hash_algorithm)
        if err:
            return err
    #print(f"verify last")
    cert = certs[-1]
    issuer = cert.issuer
    if issuer == cert.subject and len(roots)==0:
        roots[cert.subject] = [cert.public_key(), cert.signature_hash_algorithm]
    if issuer not in roots:
        return f"not root cert find: {issuer}"
        raise CertVerifyException(f"not root cert find: {issuer}")
    pk, hash_alg = roots[issuer]
    return verify_cert(cert, pk, verify_time, hash_alg)

pass

def verify_csr(csr, public_key = None, hash_alg=None):
    if type(csr)==bytes:
        csr = load_csr(csr)
    return verify_cert(csr, public_key, False, hash_alg, csr=True)
def verify_cert(cert, public_key=None, verify_time=True, hash_alg = None, csr=False):
    '''
        证书验证，用public_key验证证书，如果public_key为空，用证书的public_key验证（只有自签名证书才能用证书的公钥验证）
        verify_time: 是否验证证书是否在有效期（证书签名的时候可以设置有效期，默认是1年有效期）
        验证通过返回空，否则返回报错信息
    '''
    if type(cert)==bytes:
        cert = load_cert(cert)
    if public_key is None:
        public_key = cert.public_key()
    if hash_alg is None:
        hash_alg = cert.signature_hash_algorithm
    if csr:
        tbs_bytes = cert.tbs_certrequest_bytes
    else:
        tbs_bytes = cert.tbs_certificate_bytes
    try:
        public_key.verify(cert.signature,tbs_bytes, padding.PKCS1v15(),hash_alg)
    except Exception as exp:
        return f"sign verify error: {exp}"
    if not verify_time:
        return None
    if cert.not_valid_before_utc<datetime.datetime.now(datetime.timezone.utc)<cert.not_valid_after_utc:
        return None
    return "date not pass"
    raise CertVerifyException("date not pass")

pass

def load_der(der):
    cert = x509.load_der_x509_certificate(der)
    return cert

pass
def mk_load(fc):
    def wrap(fp, *a, **b):
        bs = fz.read(fp)
        return fc(bs, *a, **b)
    return wrap
def mk_gen(fc):
    def wrap(fp, *a, **b):
        bs = fc(*a, **b)
        fz.write(bs, fp)
    return wrap
loadf_cert = mk_load(load_cert)
loadf_csr = mk_load(load_csr)
loadf_certs = mk_load(load_certs)
genf_cert = mk_gen(gen_cert)
genf_csr = mk_gen(gen_csr)
signf_csr = mk_gen(sign_csr)
genf_root_cert = mk_gen(gen_root_cert)
verifyf_certs = mk_load(verify_certs)
verifyf_cert = mk_load(verify_cert)
verifyf_csr = mk_load(verify_csr)
loadf_prv=mk_load(load_prv)
loadf_pub = mk_load(load_pub)
genf_prv = mk_gen(gen_prv)
genf_pub = mk_gen(gen_pub)

SOIDS = "COUNTRY_NAME,STATE_OR_PROVINCE_NAME,LOCALITY_NAME,ORGANIZATION_NAME,COMMON_NAME,EMAIL_ADDRESS".split(",")
OIDS = ['BUSINESS_CATEGORY', 'COMMON_NAME', 'COUNTRY_NAME', 'DN_QUALIFIER', 'DOMAIN_COMPONENT', 'EMAIL_ADDRESS', 'GENERATION_QUALIFIER', 'GIVEN_NAME', 'INITIALS', 'INN', 'JURISDICTION_COUNTRY_NAME', 'JURISDICTION_LOCALITY_NAME', 'JURISDICTION_STATE_OR_PROVINCE_NAME', 'LOCALITY_NAME', 'OGRN', 'ORGANIZATIONAL_UNIT_NAME', 'ORGANIZATION_IDENTIFIER', 'ORGANIZATION_NAME', 'POSTAL_ADDRESS', 'POSTAL_CODE', 'PSEUDONYM', 'SERIAL_NUMBER', 'SNILS', 'STATE_OR_PROVINCE_NAME', 'STREET_ADDRESS', 'SURNAME', 'TITLE', 'UNSTRUCTURED_NAME', 'USER_ID', 'X500_UNIQUE_IDENTIFIER']
#oids = [getattr(NameOID, oid) for oid in OIDS if hasattr(NameOID, oid)]

NAMES = ['业务类别', '公共名称', '国家名称', ' DN_限定符', '域_组件', '电子邮件_地址', '代_限定符', '名字', '旅馆', '管辖区_国家名称', '管辖区_地点_名称', '管辖区_州_或_省_名称', '地点_名称', 'OGRN', '组织_单位_名称', '组织_标识符', '组织_名称', '邮政_地址', '邮政_代码', '假名', '序列号', ' SNILS ', '州_或_省_名称', '街道_地址', '姓氏', '头衔', '非结构化名称', '用户_ID ', 'X500']
names = {getattr(NameOID, OID): f"{NAME}({OID.lower()})" for NAME, OID in zip(NAMES, OIDS) if hasattr(NameOID, OID)}
def des_subject(subject):
    arr = subject._attributes
    rst = {}
    for its in arr:
        for it in its:
            oid = it.oid
            val = it.value
            if oid not in dict_names:
                name = oid.dotted_string
            else:
                name = f"{dict_names[oid][1]}({dict_names[oid][0].lower()})"
            rst[name]=val
    return rst

pass
def test():
    pass

pass

if __name__=="__main__":
    test()

pass
