import sys
sys.path.insert(0,"/home/zzz/works/codes/python")
from buildz.netz.sslz import cert

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography import x509
from cryptography.x509.oid import NameOID
prv = cert.gen_prv(to_pem=False)
conf = {
    'common': 'android' 
}
crt = cert.gen_root_cert(prv, conf=conf, to_pem=False)
print("common:", cert.get_subject_val(crt, "common"))
print(f"cert: {crt}")
exit(0)
crt = cert.gen_root_cert(prv, )

root_prv = "root.prv"
test_prv = "test.prv"
cert.genf_prv(root_prv)
cert.genf_prv(test_prv)

cert.genf_root_cert("root.cert", cert.loadf_prv(root_prv))
cert.genf_csr("test.csr", cert.loadf_prv(test_prv))
cert.signf_csr("test.cert", cert.loadf_prv(root_prv), cert.loadf_csr("test.csr"), cert.loadf_cert("root.cert"))
vrf = cert.verifyf_certs("test.cert")
print(f"verify result: {vrf}")

#print(dir(csr))
#exit(0)
#csr.verify()
