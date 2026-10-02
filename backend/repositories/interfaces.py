from typing import Protocol, Dict, Any, List, Optional

class ITaskRepository(Protocol):
    """Interface segregada para consulta e busca de tarefas no banco de dados."""
    def find_paginated_tasks(self, query: Dict[str, Any], page: int, page_size: int, sort_by: str, sort_desc: bool) -> Dict[str, Any]:
        """Recupera lista paginada de tarefas aplicando projeção e ordenação."""
        ...

    def find_task_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Recupera documento completo de uma tarefa por seu identificador único."""
        ...


class IMetricsRepository(Protocol):
    """Interface segregada para agregações analíticas e consolidação de KPIs."""
    def aggregate_summary_kpis(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula totais, sucessos, erros e taxas agregadas."""
        ...

    def aggregate_timeseries(self, query: Dict[str, Any], date_format: str) -> List[Dict[str, Any]]:
        """Executa agregação temporal agrupada pelo formato de data especificado."""
        ...

    def aggregate_distributions(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula distribuição por ação, por nodo e por processo."""
        ...


class IFilterMetadataRepository(Protocol):
    """Interface segregada para obtenção de metadados e opções de filtros."""
    def fetch_filter_metadata(self) -> Dict[str, Any]:
        """Obtém valores distintos de processos, nodos, ações, status e limites de datas."""
        ...
