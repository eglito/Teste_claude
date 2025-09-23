# Monks Marketing Dashboard API

API para gestores de agência de Marketing Digital desenvolvida em FastAPI com autenticação JWT e manipulação de dados CSV usando Pandas.

## Requisitos do Sistema

- Python 3.8+
- pip (gerenciador de pacotes Python)

## Instalação e Configuração

### 1. Clonar/Baixar o Projeto

```bash
# Navegar para o diretório do projeto
cd monks-case-tecnico
```

### 2. Criar Ambiente Virtual

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate

# Linux/macOS:
source venv/bin/activate
```

### 3. Instalar Dependências

```bash
# Instalar todas as dependências
pip install -r requirements.txt

# OU instalar individualmente:
pip install fastapi==0.104.1
pip install uvicorn==0.24.0
pip install pandas==2.1.3
pip install python-multipart==0.0.6
pip install python-jose[cryptography]==3.3.0
pip install passlib[bcrypt]==1.7.4
```

### 4. Estrutura de Arquivos

Certifique-se de que a estrutura está assim:

```
monks-case-tecnico/
├── venv/
├── main.py
├── auth.py
├── models.py
├── requirements.txt
├── README.md
└── data/
    ├── users.csv
    └── metrics.csv
```

### 5. Preparar Dados

**Criar arquivo `data/users.csv`:**
```csv
username,password,role
user1,oeiruhn56146,admin
user2,908ijofff,user
```

**Arquivo `data/metrics.csv`:**
- Deve conter seus dados reais de métricas
- Formato: 8 colunas sem cabeçalho
- A API criará dados de exemplo automaticamente se o arquivo não existir

## Execução da Aplicação

### Método 1: Uvicorn (Recomendado)

```bash
# Certificar que o ambiente virtual está ativo
# Deve aparecer (venv) no início da linha

# Executar aplicação
uvicorn main:app --reload

# A aplicação estará disponível em:
# http://127.0.0.1:8000
```

### Método 2: Python Direto

```bash
# Executar diretamente
python main.py
```

## Acesso à Documentação

Após executar a aplicação, acesse:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **OpenAPI JSON**: http://127.0.0.1:8000/openapi.json

## Testando a API

### 1. Verificar Status

```
GET http://127.0.0.1:8000/
GET http://127.0.0.1:8000/health
```

### 2. Fazer Login (Obter Token)

**Endpoint**: `POST /token`

**Credenciais Admin**:
- username: `user1`
- password: `oeiruhn56146`

**Credenciais User**:
- username: `user2`
- password: `908ijofff`

### 3. Autorizar no Swagger

1. Clique em "Authorize" no topo da página
2. Insira username e password
3. Clique "Authorize"

### 4. Testar Endpoints Principais

- `GET /users/me` - Informações do usuário
- `GET /metrics` - Dados de performance (com filtros)
- `GET /metrics/summary` - Resumo dos dados
- `GET /metrics/dates` - Datas disponíveis

## Endpoints da API

| Método | Endpoint | Descrição | Autenticação |
|--------|----------|-----------|-------------|
| GET | / | Informações da API | Não |
| POST | /token | Login e obtenção de token JWT | Não |
| GET | /users/me | Dados do usuário atual | Sim |
| GET | /metrics | Dados de métricas com filtros | Sim |
| GET | /metrics/summary | Resumo dos dados | Sim |
| GET | /metrics/dates | Datas disponíveis | Sim |
| GET | /health | Status da aplicação | Não |

## Funcionalidades Principais

### Autenticação
- Sistema de login com username/password
- Tokens JWT com expiração
- Dois níveis de usuário: admin e user

### Dados de Métricas
- Carregamento de dados CSV
- Filtros por data
- Ordenação por qualquer coluna
- Controle de acesso por role

### Controle de Acesso
- Campo `cost_micros` visível APENAS para administradores
- Usuários normais não veem informações financeiras sensíveis

## Exemplos de Uso

### Filtrar por Data
```
GET /metrics?date_filter=2024-08-16
```

### Ordenar por Impressões (Decrescente)
```
GET /metrics?sort_by=impressions&sort_order=desc
```

### Filtro + Ordenação
```
GET /metrics?date_filter=2024-08-16&sort_by=clicks&sort_order=asc
```

## Solução de Problemas

### Erro: "uvicorn não é reconhecido"
- Verifique se o ambiente virtual está ativo
- Instale uvicorn: `pip install uvicorn`

### Erro 500 nos endpoints
- Verifique se os arquivos CSV estão no diretório `data/`
- Teste o endpoint `/debug/csv-info` para diagnóstico

### Problemas de Dependências
```bash
# Reinstalar dependências
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

## Estrutura do Projeto

- **main.py**: Aplicação principal FastAPI
- **auth.py**: Sistema de autenticação JWT
- **models.py**: Modelos de dados Pydantic
- **data/users.csv**: Dados de usuários
- **data/metrics.csv**: Dados de métricas de marketing

## Tecnologias Utilizadas

- **FastAPI**: Framework web moderno e rápido
- **Pandas**: Manipulação e análise de dados
- **JWT**: Autenticação baseada em tokens
- **Pydantic**: Validação de dados
- **Uvicorn**: Servidor ASGI

## Desenvolvido por

Case Técnico - Marketing Dashboard API
Monks Digital Agency Challenge