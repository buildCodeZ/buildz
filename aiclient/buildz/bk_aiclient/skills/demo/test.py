
import hashlib
def hashval(text, alg="md5",coding="utf-8"):
    text = text.encode(coding)
    return getattr(hashlib, alg)(text).hexdigest().encode("ascii")
def base64_encode(text, coding="utf-8"):
    import base64
    text = text.encode(coding)
    return base64.b64encode(text).decode("ascii")
def base64_decode(text, coding="utf-8"):
    import base64
    text = text.encode("ascii")
    return base64.b64decode(text).decode(coding)
