import hashlib, binascii, secrets
from datetime import timedelta
from django.utils import timezone

def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
    return binascii.hexlify(dk).decode(), salt

def verify_password(password, salt, stored):
    h, _ = hash_password(password, salt)
    return secrets.compare_digest(h, stored)

def make_token():
    return secrets.token_urlsafe(48)

def token_expires(hours=24):
    return timezone.now() + timedelta(hours=hours)

def calculate_new_marks(existing, add):
    # simple rule used in task: add marks, but do not allow >100
    if add < 0:
        raise ValueError("add must be >= 0")
    total = existing + add
    if total > 100:
        raise ValueError("total > 100")
    return total
