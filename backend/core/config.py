import os
from dataclasses import dataclass

@dataclass(frozen=True)
class AppConfig:
    """Configurações centrais da aplicação carregadas a partir de variáveis de ambiente."""
    mongo_uri: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    database_name: str = os.getenv("DB_NAME", "dispor")
    collection_name: str = os.getenv("COLLECTION_NAME", "tarefas_finalizadas")
    server_host: str = os.getenv("SERVER_HOST", "127.0.0.1")
    server_port: int = int(os.getenv("SERVER_PORT", "8000"))

config = AppConfig()
