from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Hash a plain text password. Store the result, never the original."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compare plain text against hash. Returns True if they match."""
    return pwd_context.verify(plain_password, hashed_password)
