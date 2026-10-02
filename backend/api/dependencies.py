from functools import lru_cache
from backend.database.connection import MongoConnectionManager
from backend.repositories.task_repository import MongoTaskRepository
from backend.services.dashboard_service import DashboardService

@lru_cache()
def get_task_repository() -> MongoTaskRepository:
    """Provedor injetável do repositório de tarefas."""
    collection = MongoConnectionManager.get_collection()
    return MongoTaskRepository(collection)

@lru_cache()
def get_dashboard_service() -> DashboardService:
    """Provedor injetável do serviço de dashboard."""
    repo = get_task_repository()
    return DashboardService(repo)
