import sys
sys.path.insert(0,"/home/zzz/works/codes/python")
from buildz.netz.sslz import cert

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography import x509
from cryptography.x509.oid import NameOID

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
