from typing import Optional
from pymongo import MongoClient
from backend.core.config import config

class MongoConnectionManager:
    """Gerencia a conexão com o MongoDB utilizando padrão Singleton para reuso do pool de conexões."""
    _client: Optional[MongoClient] = None

    @classmethod
    def get_client(cls) -> MongoClient:
        """Obtém ou inicializa a instância do cliente MongoDB."""
        if cls._client is None:
            cls._client = MongoClient(config.mongo_uri, serverSelectionTimeoutMS=4000)
        return cls._client

    @classmethod
    def get_collection(cls):
        """Retorna a coleção configurada no banco de dados."""
        client = cls.get_client()
        return client[config.database_name][config.collection_name]

    @classmethod
    def ping(cls) -> dict:
        """Verifica a saúde da conexão com o banco de dados MongoDB."""
        try:
            client = cls.get_client()
            client.admin.command('ping')
            collection = cls.get_collection()
            count = collection.estimated_document_count()
            return {
                "status": "connected",
                "database": config.database_name,
                "collection": config.collection_name,
                "total_docs": count
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    @classmethod
    def close(cls) -> None:
        """Fecha a conexão com o MongoDB caso esteja aberta."""
        if cls._client:
            cls._client.close()
            cls._client = None
