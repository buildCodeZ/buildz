
from cryptography.x509.oid import NameOID
OIDS = ['BUSINESS_CATEGORY', 'COMMON_NAME', 'COUNTRY_NAME', 'DN_QUALIFIER', 'DOMAIN_COMPONENT', 'EMAIL_ADDRESS', 
        'GENERATION_QUALIFIER', 'GIVEN_NAME', 'INITIALS', 'INN', 'JURISDICTION_COUNTRY_NAME', 'JURISDICTION_LOCALITY_NAME', 
        'JURISDICTION_STATE_OR_PROVINCE_NAME', 'LOCALITY_NAME', 'OGRN', 'ORGANIZATIONAL_UNIT_NAME', 'ORGANIZATION_IDENTIFIER', 'ORGANIZATION_NAME', 
        'POSTAL_ADDRESS', 'POSTAL_CODE', 'PSEUDONYM', 'SERIAL_NUMBER', 'SNILS', 'STATE_OR_PROVINCE_NAME', 
        'STREET_ADDRESS', 'SURNAME', 'TITLE', 'UNSTRUCTURED_NAME', 'USER_ID', 'X500_UNIQUE_IDENTIFIER']
NAMES = ['业务类别', '公共名称', '国家名称', ' DN_限定符', '域_组件', '电子邮件_地址', 
         '代_限定符', '名字', '旅馆', '管辖区_国家名称', '管辖区_地点_名称', '管辖区_州_或_省_名称', 
         '地点_名称', 'OGRN', '组织_单位_名称', '组织_标识符', '组织_名称', '邮政_地址', 
         '邮政_代码', '假名', '序列号', ' SNILS ', '州_或_省_名称', '街道_地址', 
         '姓氏', '头衔', '非结构化名称', '用户_ID ', 'X500']
from buildz import xf

als = xf.loads(r"""
COUNTRY_NAME: [CN,country]
STATE_OR_PROVINCE_NAME: [CN, provice],
LOCALITY_NAME: [cityz, local],
ORGANIZATION_NAME: [orgz,org],
COMMON_NAME: [commonz, common],
EMAIL_ADDRESS: [emailz,email]
""")

rst = []
for OID, NAME in zip(OIDS, NAMES):
    df = ""
    obj = getattr(NameOID, OID)
    an=[obj.dotted_string]
    if obj._name!="Unknown OID":
        an.append(obj._name)
    al = als.get(OID)
    if al is not None:
        df = al[0]
        an.append(al[1])
    an = " | ".join(an)
    tmp = f"{OID}, {NAME}, {df}, {an}"
    rst.append(tmp)
    
rs = "\n".join(rst)
rs = "NAMEOID, Des, Default, Aliase\n"+rs
from os.path import join, dirname
dp = dirname(__file__)
with open(join(dp,"names.txt"), 'wb') as f:
    f.write(rs.encode("utf-8"))

