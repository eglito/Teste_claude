# models.py - Modelos de dados para o case técnico
from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    username: str
    role: str  # 'admin' ou 'user'

class UserInDB(BaseModel):
    username: str
    hashed_password: str
    role: str

class UserCreate(BaseModel):
    username: str
    password: str
    role: Optional[str] = "user"""

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class MetricsResponse(BaseModel):
    data: list
    total_records: int
    columns_visible: list
    user_role: str
    cost_micros_visible: bool
    filters_applied: dict