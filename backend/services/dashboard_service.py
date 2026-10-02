from typing import Dict, Any, List, Optional
from backend.repositories.task_repository import MongoTaskRepository
from backend.services.query_builder import MongoQueryBuilder

class DashboardService:
    """
    Serviço orquestrador do dashboard executivo.
    Aplica regras de negócio e delega persistência para a camada de repositório.
    """

    def __init__(self, task_repo: MongoTaskRepository):
        """Injeta a dependência do repositório (Dependency Inversion Principle)."""
        self._repo = task_repo

    def get_filter_options(self) -> Dict[str, Any]:
        """Obtém metadados de filtros e lista completa de processos disponíveis."""
        return self._repo.fetch_filter_metadata()

    def get_summary_kpis(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula os indicadores executivos a partir dos filtros fornecidos."""
        query = MongoQueryBuilder.build_query(filters)
        return self._repo.aggregate_summary_kpis(query)

    def get_timeseries_data(self, filters: Dict[str, Any], granularity: str = "daily") -> List[Dict[str, Any]]:
        """
        Gera a série histórica de tarefas segmentada pelo nível de agregação temporal.
        
        :param filters: Critérios de filtragem
        :param granularity: 'daily' para diário, 'monthly' para mensal ou 'yearly' para anual
        :return: Lista de períodos consolidados com contagem de sucessos e falhas
        """
        query = MongoQueryBuilder.build_query(filters)

        if granularity == "yearly":
            date_format = "%Y"
        elif granularity == "monthly":
            date_format = "%Y-%m"
        else:
            date_format = "%Y-%m-%d"

        return self._repo.aggregate_timeseries(query, date_format)

    def get_distribution_data(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula distribuição categórica de tarefas por Ação, Nodo e Processo."""
        query = MongoQueryBuilder.build_query(filters)
        return self._repo.aggregate_distributions(query)

    def get_paginated_tasks(self, filters: Dict[str, Any], page: int, page_size: int, sort_by: str, sort_desc: bool) -> Dict[str, Any]:
        """Obtém conjunto paginado de tarefas ordenado."""
        query = MongoQueryBuilder.build_query(filters)
        return self._repo.find_paginated_tasks(query, page, page_size, sort_by, sort_desc)

    def get_task_details(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Recupera informações completas de uma tarefa específica."""
        return self._repo.find_task_by_id(task_id)
