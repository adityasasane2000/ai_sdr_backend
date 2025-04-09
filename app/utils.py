from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    try:
        result = pwd_context.verify(plain_password, hashed_password)
        print(f"Password verification: {result}")
        return result
    except Exception as e:
        print(f"Error verifying password: {str(e)}")
        return False

def get_password_hash(password):
    return pwd_context.hash(password)
