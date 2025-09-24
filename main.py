# main.py - API para Case Técnico Monks (Versão Final com Paginação)
import os
import logging
from datetime import timedelta
from typing import Optional
import math

import pandas as pd
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse

from auth import (
    authenticate_user_credentials,
    create_access_token,
    get_current_active_user,
    users_db,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from models import User, Token

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Monks Marketing Dashboard API",
    version="1.1.0",
    description="API para gestores de agência de Marketing Digital - Case Técnico Monks",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/css", StaticFiles(directory="css"), name="css")
app.mount("/js", StaticFiles(directory="js"), name="js")


def load_metrics_data(file_path: str = "data/metrics.csv") -> pd.DataFrame:
    if not os.path.exists(file_path):
        return pd.DataFrame()
    try:
        df = pd.read_csv(file_path, header=None, low_memory=False)
        df.columns = [
            'account_id', 'campaign_id', 'cost_micros', 'impressions',
            'clicks', 'conversions', 'conversion_value', 'date'
        ]
        for col in df.columns:
            if col != 'date':
                df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna()
        return df
    except Exception as e:
        logger.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

metrics_df_global = load_metrics_data()


@app.get("/", response_class=FileResponse, include_in_schema=False)
async def read_index():
    return "index.html"


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user_credentials(users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.get("/metrics")
async def get_metrics_data(
    date_filter: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: str = "asc",
    page: int = 1,
    page_size: int = 100,
    current_user: User = Depends(get_current_active_user)
):
    df = metrics_df_global.copy()

    if date_filter:
        df = df[df['date'] == date_filter]

    visible_cols = list(df.columns)
    if current_user.role != "admin":
        if "cost_micros" in visible_cols:
            df = df.drop("cost_micros", axis=1)
            visible_cols.remove("cost_micros")

    if sort_by and sort_by in df.columns:
        df = df.sort_values(by=sort_by, ascending=(sort_order.lower() == "asc"))

    total_records = len(df)
    total_pages = math.ceil(total_records / page_size)

    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    paginated_data = df.iloc[start_index:end_index]

    return {
        "data": paginated_data.to_dict('records'),
        "total_records": total_records,
        "columns_visible": visible_cols,
        "pagination": {
            "current_page": page,
            "total_pages": total_pages,
            "page_size": page_size
        }
    }

@app.get("/metrics/summary")
async def get_metrics_summary(current_user: User = Depends(get_current_active_user)):
    df = metrics_df_global
    sortable_columns = list(df.columns)
    if current_user.role != "admin" and "cost_micros" in sortable_columns:
        sortable_columns.remove("cost_micros")

    return {
        "total_records": len(df),
        "available_dates": sorted(df['date'].unique().tolist()),
        "sortable_columns": sortable_columns,
        "user_permissions": {
            "role": current_user.role,
            "can_see_cost_micros": current_user.role == "admin"
        }
    }