from cryptography.fernet import Fernet
import pickle
import hashlib

def GenerateKeyFile(filename: str) -> bytes:
    key = Fernet.generate_key()
    with open(filename, "wb") as f:
        f.write(pickle.dumps(key))
    return key

def GetKeyFile(filename: str) -> bytes:
    with open(filename, "rb") as f:
        return pickle.loads(f.read())

def Encrypt(key: bytes, message: bytes) -> bytes:
    fernet = Fernet(key)
    message = fernet.encrypt(message)
    return message

def Decrypt(key: bytes, message: bytes) -> bytes:
    fernet = Fernet(key)
    return fernet.decrypt(message)

def PasswordHash(password: str) -> str:
    hasher = hashlib.sha512()
    hasher.update(password.encode("ascii"))
    return hasher.hexdigest()