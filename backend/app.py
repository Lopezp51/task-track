import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.database.connection import MongoConnectionManager
from backend.database.index_manager import MongoIndexManager
from backend.api.routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia ciclo de vida da aplicação: inicializa conexões e índices na subida."""
    collection = MongoConnectionManager.get_collection()
    MongoIndexManager.ensure_indexes(collection)
    yield
    MongoConnectionManager.close()

app = FastAPI(
    title="Sicredi RPA - Monitoramento de Tarefas Finalizadas",
    description="Dashboard analítico de alta performance para robôs e fluxos de automação Sicredi",
    version="2.0.0",
    lifespan=lifespan
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro das rotas da API
app.include_router(router)

# Montagem de arquivos estáticos do frontend
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/")
def serve_dashboard():
    """Entrega a página principal do dashboard."""
    index_file = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Interface do frontend não encontrada"}
