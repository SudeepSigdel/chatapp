from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"], deprecated=["auto"])

def hash(password: str):
    return pwd.hash(password)

def verify(plain:str, hash:str):
    return pwd.verify(plain, hash)