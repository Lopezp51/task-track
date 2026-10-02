from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class FilterParams(BaseModel):
    """Parâmetros de filtro aplicáveis a consultas, métricas e séries temporais."""
    processos: Optional[List[str]] = Field(default=None, description="Lista de nomes de processos selecionados ou vazio para todos")
    status: Optional[List[str]] = Field(default=None, description="Status de execução filtrados (ex: sucesso, erro_negocio)")
    nodos: Optional[List[Any]] = Field(default=None, description="Lista de identificadores de nodo do Fluid")
    acoes: Optional[List[str]] = Field(default=None, description="Ações executadas no Fluid (fluid_api.acao)")
    data_inicio: Optional[str] = Field(default=None, description="Data e hora inicial no formato ISO")
    data_fim: Optional[str] = Field(default=None, description="Data e hora final no formato ISO")
    search: Optional[str] = Field(default=None, description="Termo para busca textual por número ou detalhe")

class TaskQueryRequest(BaseModel):
    """Modelo de requisição para consulta paginada de tarefas."""
    filters: FilterParams = Field(default_factory=FilterParams, description="Critérios de filtragem")
    page: int = Field(default=1, ge=1, description="Número da página (1-indexada)")
    page_size: int = Field(default=25, ge=5, le=100, description="Quantidade de registros por página")
    sort_by: str = Field(default="data_realizacao", description="Campo para ordenação")
    sort_desc: bool = Field(default=True, description="Se verdadeiro, ordena de forma decrescente")

class TimeSeriesRequest(BaseModel):
    """Modelo de requisição para agregação temporal de histórico."""
    filters: FilterParams = Field(default_factory=FilterParams, description="Critérios de filtragem")
    granularity: str = Field(default="daily", description="Granularidade temporal: 'daily', 'monthly' ou 'yearly'")
