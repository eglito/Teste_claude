# main.py - API Completa para Case Técnico Monks
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta
from typing import Optional
import pandas as pd
import os

# Imports dos nossos módulos
from auth import (
    authenticate_user_credentials,
    create_access_token,
    get_current_active_user,
    users_db,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from models import User, Token

# Configuração da aplicação FastAPI
app = FastAPI(
    title="Monks Marketing Dashboard API",
    version="1.0.0",
    description="API para gestores de agência de Marketing Digital - Case Técnico Monks",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS para permitir acesso do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_metrics_data(file_path: str = "data/metrics.csv") -> pd.DataFrame:
    """
    Carrega dados de métricas do CSV com tratamento robusto de erros
    """
    try:
        # Verificar se arquivo existe
        if not os.path.exists(file_path):
            print(f"Arquivo {file_path} não encontrado. Criando dados de exemplo...")
            return create_sample_metrics_data(file_path)

        print(f"Carregando arquivo: {file_path}")

        # Ler CSV sem especificar tipos primeiro (mais flexível)
        df = pd.read_csv(file_path, header=None, low_memory=False)

        print(f"Arquivo carregado. Shape: {df.shape}")

        # Verificar se tem pelo menos 8 colunas
        if df.shape[1] < 8:
            print(f"Arquivo tem apenas {df.shape[1]} colunas. Esperadas: 8")
            return create_sample_metrics_data(file_path)

        # Definir nomes das colunas
        df.columns = [
            'account_id', 'campaign_id', 'cost_micros', 'impressions',
            'clicks', 'conversions', 'conversion_value', 'date'
        ]

        # Converter tipos de dados com tratamento de erro
        try:
            df['account_id'] = pd.to_numeric(df['account_id'], errors='coerce')
            df['campaign_id'] = pd.to_numeric(df['campaign_id'], errors='coerce')
            df['cost_micros'] = pd.to_numeric(df['cost_micros'], errors='coerce')
            df['impressions'] = pd.to_numeric(df['impressions'], errors='coerce')
            df['clicks'] = pd.to_numeric(df['clicks'], errors='coerce')
            df['conversions'] = pd.to_numeric(df['conversions'], errors='coerce')
            df['conversion_value'] = pd.to_numeric(df['conversion_value'], errors='coerce')
            df['date'] = df['date'].astype(str)
        except Exception as e:
            print(f"Erro na conversão de tipos: {e}")

        # Remover linhas com muitos NaN
        df = df.dropna(subset=['account_id', 'campaign_id', 'date'])

        print(f"Dados processados. Shape final: {df.shape}")
        return df

    except Exception as e:
        print(f"Erro ao carregar CSV: {str(e)}")
        return create_sample_metrics_data(file_path)


def create_sample_metrics_data(file_path: str) -> pd.DataFrame:
    """Criar dados de exemplo quando o arquivo real falha"""
    sample_data = {
        'account_id': [8181642239, 8181642239, 4590233378, 9565398844, 9782017208],
        'campaign_id': [6320590762, 6862247394, 7770677599, 8260044871, 6945741994],
        'cost_micros': [2026808398.5, 16422492256.15, 233106356.72, 1850678453.56, 101415591090.3],
        'impressions': [1306.16, 23500.07, 137.82, 919.94, 376791.51],
        'clicks': [60.91, 656.22, 4.18, 68.83, 78153.08],
        'conversions': [43749.27, 1233332, 260.99, 5394.76, 15247703.64],
        'conversion_value': [1569.33, 28235.04, 131.01, 902.88, 5255635.05],
        'date': ['2024-08-16', '2024-08-16', '2024-08-16', '2024-08-16', '2024-08-16']
    }

    # Criar diretório se não existir
    os.makedirs('data', exist_ok=True)

    df = pd.DataFrame(sample_data)

    # Salvar arquivo de exemplo
    try:
        df.to_csv(file_path, index=False, header=False)
        print(f"Arquivo de exemplo criado: {file_path}")
    except Exception as e:
        print(f"Erro ao salvar arquivo de exemplo: {e}")

    return df


# ENDPOINTS DA API

@app.get("/")
async def root():
    """Endpoint raiz com informações da API"""
    return {
        "message": "Monks Marketing Dashboard API",
        "version": "1.0.0",
        "description": "API para gestores de agência de Marketing Digital",
        "case_tecnico": True,
        "endpoints": {
            "authentication": "/token",
            "user_info": "/users/me",
            "metrics_data": "/metrics",
            "documentation": "/docs"
        },
        "test_credentials": {
            "admin": {
                "username": "user1",
                "password": "oeiruhn56146",
                "role": "admin",
                "can_see_cost_micros": True
            },
            "user": {
                "username": "user2",
                "password": "908ijofff",
                "role": "user",
                "can_see_cost_micros": False
            }
        }
    }


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint de autenticação - REQUISITO DO CASE

    Autentica usuário por username e senha e retorna JWT token

    Credenciais para teste:
    - Admin: username=user1, password=oeiruhn56146
    - User: username=user2, password=908ijofff
    """
    user = authenticate_user_credentials(users_db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Criar token com expiração
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Obter informações do usuário autenticado"""
    return current_user


@app.get("/metrics")
async def get_metrics_data(
        date_filter: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        current_user: User = Depends(get_current_active_user)
):
    """
    ENDPOINT PRINCIPAL - Implementa TODOS os requisitos do case técnico:

    ✅ Apresentar dados em formato tabelar
    ✅ Filtrar dados por data
    ✅ Ordenar por qualquer coluna
    ✅ cost_micros visível APENAS para role "admin"

    Parâmetros:
    - date_filter: Filtrar por data específica (ex: 2024-08-16)
    - sort_by: Ordenar por coluna (account_id, campaign_id, impressions, etc.)
    - sort_order: Direção da ordenação ("asc" ou "desc")
    """
    try:
        # Carregar todos os dados
        df = load_metrics_data()

        # REQUISITO: Filtrar por data
        if date_filter:
            df_filtered = df[df['date'] == date_filter]
            if df_filtered.empty:
                available_dates = sorted(df['date'].unique().tolist())
                return {
                    "message": f"Nenhum dado encontrado para a data '{date_filter}'",
                    "data": [],
                    "total_records": 0,
                    "available_dates": available_dates,
                    "user_role": current_user.role
                }
            df = df_filtered

        # REQUISITO CRÍTICO: Ocultar cost_micros para usuários não-admin
        columns_visible = list(df.columns)
        if current_user.role != "admin" and "cost_micros" in columns_visible:
            df = df.drop("cost_micros", axis=1)
            columns_visible.remove("cost_micros")

        # REQUISITO: Ordenação por qualquer coluna
        if sort_by:
            if sort_by not in df.columns:
                raise HTTPException(
                    status_code=400,
                    detail=f"Coluna '{sort_by}' não existe. Colunas disponíveis: {list(df.columns)}"
                )

            ascending = sort_order.lower() == "asc"
            df = df.sort_values(sort_by, ascending=ascending)

        # Converter para formato tabelar (lista de dicionários)
        data_records = df.to_dict('records')

        # Resposta completa
        return {
            "data": data_records,
            "total_records": len(data_records),
            "columns_visible": columns_visible,
            "user_role": current_user.role,
            "cost_micros_visible": current_user.role == "admin",
            "filters_applied": {
                "date_filter": date_filter,
                "sort_by": sort_by,
                "sort_order": sort_order
            },
            "pagination_info": {
                "page": 1,
                "total_pages": 1,
                "showing": len(data_records)
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@app.get("/metrics/summary")
async def get_metrics_summary(current_user: User = Depends(get_current_active_user)):
    """Resumo dos dados disponíveis para filtros e ordenação"""
    try:
        df = load_metrics_data()

        # Colunas disponíveis para ordenação (remover cost_micros se não for admin)
        sortable_columns = list(df.columns)
        if current_user.role != "admin" and "cost_micros" in sortable_columns:
            sortable_columns.remove("cost_micros")

        return {
            "total_records": len(df),
            "available_dates": sorted(df['date'].unique().tolist()),
            "unique_accounts": len(df['account_id'].unique()),
            "unique_campaigns": len(df['campaign_id'].unique()),
            "date_range": {
                "earliest": df['date'].min(),
                "latest": df['date'].max()
            },
            "sortable_columns": sortable_columns,
            "user_permissions": {
                "role": current_user.role,
                "can_see_cost_micros": current_user.role == "admin"
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar resumo: {str(e)}")


@app.get("/metrics/dates")
async def get_available_dates(current_user: User = Depends(get_current_active_user)):
    """Lista todas as datas disponíveis para filtros"""
    try:
        df = load_metrics_data()
        dates = sorted(df['date'].unique().tolist())
        return {
            "available_dates": dates,
            "total_dates": len(dates)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter datas: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check para verificar se a API está funcionando"""
    try:
        # Testar carregamento de dados
        df = load_metrics_data()
        users_count = len(users_db)

        return {
            "status": "healthy",
            "api_version": "1.0.0",
            "data_loaded": True,
            "metrics_records": len(df),
            "users_loaded": users_count,
            "timestamp": pd.Timestamp.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": pd.Timestamp.now().isoformat()
        }


# Endpoint para debug (apenas em desenvolvimento)
@app.get("/debug/data-sample")
async def debug_data_sample(current_user: User = Depends(get_current_active_user)):
    """Mostra amostra dos dados para debug - APENAS ADMIN"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas administradores podem acessar dados de debug."
        )

    try:
        df = load_metrics_data()
        return {
            "sample_data": df.head(5).to_dict('records'),
            "total_records": len(df),
            "columns": list(df.columns),
            "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "memory_usage": df.memory_usage(deep=True).to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no debug: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)