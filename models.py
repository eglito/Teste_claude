# models.py - Modelos de dados Pydantic
from pydantic import BaseModel
from typing import Optional, List, Dict


class User(BaseModel):
    username: str
    role: str


class UserInDB(BaseModel):
    username: str
    hashed_password: str
    role: str


class UserCreate(BaseModel):
    username: str
    password: str
    role: Optional[str] = "user"


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class MetricsResponse(BaseModel):
    data: List[dict]
    total_records: int
    columns_visible: List[str]
    user_role: str
    cost_micros_visible: bool
    filters_applied: Dict
