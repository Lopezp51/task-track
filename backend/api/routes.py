import time
from fastapi import APIRouter, Depends, HTTPException
from backend.api.dependencies import get_dashboard_service
from backend.database.connection import MongoConnectionManager
from backend.models.schemas import FilterParams, TaskQueryRequest, TimeSeriesRequest
from backend.services.dashboard_service import DashboardService

router = APIRouter(prefix="/api", tags=["Dashboard"])

@router.get("/health")
def health_check():
    """Retorna o status de conexão com o banco de dados e contagem de registros."""
    return MongoConnectionManager.ping()

@router.get("/filters/options")
def get_filter_options(service: DashboardService = Depends(get_dashboard_service)):
    """Retorna metadados de filtros e lista completa de processos disponíveis no banco."""
    start_time = time.time()
    options = service.get_filter_options()
    duration_ms = round((time.time() - start_time) * 1000, 2)
    return {
        "data": options,
        "query_time_ms": duration_ms
    }

@router.post("/metrics/summary")
def get_summary(params: FilterParams, service: DashboardService = Depends(get_dashboard_service)):
    """Calcula os indicadores e KPIs consolidados com base nos filtros."""
    start_time = time.time()
    kpis = service.get_summary_kpis(params.dict(exclude_none=True))
    duration_ms = round((time.time() - start_time) * 1000, 2)
    return {
        "data": kpis,
        "query_time_ms": duration_ms
    }

@router.post("/metrics/timeseries")
def get_timeseries(req: TimeSeriesRequest, service: DashboardService = Depends(get_dashboard_service)):
    """Retorna série temporal de tarefas agrupadas por dia, mês ou ano."""
    start_time = time.time()
    series = service.get_timeseries_data(
        req.filters.dict(exclude_none=True),
        granularity=req.granularity
    )
    duration_ms = round((time.time() - start_time) * 1000, 2)
    return {
        "data": series,
        "granularity": req.granularity,
        "query_time_ms": duration_ms
    }

@router.post("/metrics/distribution")
def get_distribution(params: FilterParams, service: DashboardService = Depends(get_dashboard_service)):
    """Retorna a distribuição de tarefas por Ação, por Nodo e por Processo."""
    start_time = time.time()
    distributions = service.get_distribution_data(params.dict(exclude_none=True))
    duration_ms = round((time.time() - start_time) * 1000, 2)
    return {
        "data": distributions,
        "query_time_ms": duration_ms
    }

@router.post("/tasks")
def get_tasks(req: TaskQueryRequest, service: DashboardService = Depends(get_dashboard_service)):
    """Consulta paginada de tarefas com suporte a ordenação e busca textual."""
    start_time = time.time()
    result = service.get_paginated_tasks(
        filters=req.filters.dict(exclude_none=True),
        page=req.page,
        page_size=req.page_size,
        sort_by=req.sort_by,
        sort_desc=req.sort_desc
    )
    duration_ms = round((time.time() - start_time) * 1000, 2)
    result["query_time_ms"] = duration_ms
    return result

@router.get("/tasks/{task_id}")
def get_task_details(task_id: str, service: DashboardService = Depends(get_dashboard_service)):
    """Retorna o documento completo de uma tarefa por seu identificador único."""
    task = service.get_task_details(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return {"data": task}
