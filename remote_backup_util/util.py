
import hashlib

def calc_sha1(content: bytes) -> str:
    obj = hashlib.sha1()
    obj.update(content)
    return obj.hexdigest()

def calc_str_utf8_sha1(content: str) -> str:
    return calc_sha1(content.encode("utf-8"))
