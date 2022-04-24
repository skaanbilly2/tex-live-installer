import hashlib


def sha512(data):
    return hashlib.sha512(data).hexdigest()
