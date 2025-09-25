from cryptography.fernet import Fernet
import os

keyfile = "fernet.key"
if not os.path.exists(keyfile):
    with open(keyfile, "wb") as f:
        f.write(Fernet.generate_key())
with open(keyfile, "rb") as f:
    _FERNET = Fernet(f.read())

def encrypt(data: str) -> str:
    return _FERNET.encrypt(data.encode()).decode()

def decrypt(token: str) -> str:
    return _FERNET.decrypt(token.encode()).decode()