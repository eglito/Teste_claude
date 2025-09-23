from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
from passlib.context import CryptContext
import csv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from models import User, UserInDB

SECRET_KEY = "monks-marketing-dashboard-secret-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def load_users(file_path: str = "data/users.csv") -> Dict[str, Dict]:
    """Carrega usuários do CSV com username, password E role"""
    users = {}
    try:
        with open(file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # IMPORTANTE: Senhas em TEXTO PLANO no CSV (conforme seus dados)
                users[row["username"]] = {
                    "username": row["username"],
                    "plain_password": row["password"],  # Texto plano como nos seus dados
                    "role": row["role"]
                }
    except FileNotFoundError:
        print(f"Arquivo {file_path} não encontrado!")
        # Dados de fallback baseados nos seus dados reais
        users = {
            "user1": {
                "username": "user1",
                "plain_password": "oeiruhn56146",
                "role": "admin"
            },
            "user2": {
                "username": "user2",
                "plain_password": "908ijofff",
                "role": "user"
            }
        }
    return users


# Carregar usuários na inicialização
users_db = load_users()


def verify_password_plain(plain_password: str, stored_password: str) -> bool:
    """Verificar senha em texto plano (para o case técnico)"""
    return plain_password == stored_password


def get_password_hash(password: str) -> str:
    """Gerar hash para uma senha (para uso futuro)"""
    return pwd_context.hash(password)


def get_user(db: Dict, username: str) -> Optional[UserInDB]:
    """Obter usuário do banco de dados"""
    if username in db:
        user_dict = db[username]
        # Converter para formato UserInDB
        return UserInDB(
            username=user_dict["username"],
            hashed_password=user_dict["plain_password"],  # Usando plain como hash temporário
            role=user_dict["role"]
        )
    return None


def authenticate_user_credentials(users_db: Dict, username: str, password: str) -> Optional[UserInDB]:
    """Verificar se username e senha estão corretos"""
    if username not in users_db:
        return None

    user_data = users_db[username]
    # Verificar senha em texto plano
    if not verify_password_plain(password, user_data["plain_password"]):
        return None

    return UserInDB(
        username=user_data["username"],
        hashed_password=user_data["plain_password"],  # Temporário
        role=user_data["role"]
    )


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Criar JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    """Obter usuário atual do JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user(users_db, username=username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)) -> User:
    """Obter usuário ativo atual (sem password)"""
    return User(username=current_user.username, role=current_user.role)