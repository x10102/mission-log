import bcrypt

def pw_hash(password: str) -> bytes:
    pw = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw, salt)

def pw_verify(pw_1: str, pw_2: bytes):
    passwd = pw_1.encode('utf-8')
    return bcrypt.checkpw(passwd, pw_2)