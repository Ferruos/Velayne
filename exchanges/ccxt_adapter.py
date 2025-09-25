from cryptography.fernet import Fernet

class KeyVault:
    def __init__(self, secret: bytes):
        self.fernet = Fernet(secret)

    def encrypt(self, key: str) -> bytes:
        return self.fernet.encrypt(key.encode())

    def decrypt(self, token: bytes) -> str:
        return self.fernet.decrypt(token).decode()