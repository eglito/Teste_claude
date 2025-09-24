# auth.py - Autenticação JWT e gestão de usuários
import csv
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from models import User, UserInDB

SECRET_KEY = "monks-marketing-dashboard-secret-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def load_users(file_path: str = "data/users.csv") -> Dict[str, Dict]:
    """Carrega usuários a partir do CSV ou usa fallback se não existir."""
    users = {}
    try:
        with open(file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                users[row["username"]] = {
                    "username": row["username"],
                    "plain_password": row["password"],
                    "role": row["role"]
                }
    except FileNotFoundError:
        # fallback com dados básicos
        users = {
            "user1": {"username": "user1", "plain_password": "oeiruhn56146", "role": "admin"},
            "user2": {"username": "user2", "plain_password": "908ijofff", "role": "user"}
        }
    return users


users_db = load_users()


def verify_password_plain(plain_password: str, stored_password: str) -> bool:
    return plain_password == stored_password


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_user(db: Dict, username: str) -> Optional[UserInDB]:
    if username in db:
        u = db[username]
        return UserInDB(username=u["username"], hashed_password=u["plain_password"], role=u["role"])
    return None


def authenticate_user_credentials(users_db: Dict, username: str, password: str) -> Optional[UserInDB]:
    if username not in users_db:
        return None
    if not verify_password_plain(password, users_db[username]["plain_password"]):
        return None
    u = users_db[username]
    return UserInDB(username=u["username"], hashed_password=u["plain_password"], role=u["role"])


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    payload.update({"exp": expire})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise exc
    except JWTError:
        raise exc
    user = get_user(users_db, username=username)
    if user is None:
        raise exc
    return user


async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)) -> User:
    return User(username=current_user.username, role=current_user.role)
