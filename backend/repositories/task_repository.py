from typing import Dict, Any, List, Optional
from bson import ObjectId
from pymongo import ASCENDING, DESCENDING
from pymongo.collection import Collection
from backend.repositories.interfaces import ITaskRepository, IMetricsRepository, IFilterMetadataRepository
from backend.core.status_config import (
    STATUS_NAO_ERRO_KEYWORDS,
    classify_status,
    get_mongo_is_success_cond,
    get_mongo_is_non_error_cond,
    get_mongo_is_error_cond
)

class MongoTaskRepository(ITaskRepository, IMetricsRepository, IFilterMetadataRepository):
    """Implementação concreta de persistência no MongoDB com alta eficiência de indexação."""

    def __init__(self, collection: Collection):
        """Inicializa o repositório com a coleção injetada (Dependency Inversion)."""
        self._collection = collection

    def fetch_filter_metadata(self) -> Dict[str, Any]:
        """Obtém valores distintos de processos com contagem, nodos, ações e datas limites."""
        proc_pipeline = [
            {"$group": {"_id": "$nome_processo", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]
        proc_results = list(self._collection.aggregate(proc_pipeline))
        processos = [p["_id"] for p in proc_results if p["_id"]]
        processos_info = [{"nome": p["_id"], "count": p["count"]} for p in proc_results if p["_id"]]

        statuses = [s for s in self._collection.distinct("status") if s]
        nodos = [n for n in self._collection.distinct("fluid_infos.nodo") if n is not None]
        
        acoes_primary = set([a for a in self._collection.distinct("infos_retorno.fluid_api.acao_nodo") if a])
        acoes = sorted(list(acoes_primary))
        
        robos = [r for r in self._collection.distinct("robo") if r]

        oldest = self._collection.find_one({}, sort=[("data_realizacao", 1)], projection={"data_realizacao": 1})
        newest = self._collection.find_one({}, sort=[("data_realizacao", -1)], projection={"data_realizacao": 1})

        min_date = oldest.get("data_realizacao") if oldest else None
        max_date = newest.get("data_realizacao") if newest else None

        return {
            "processos": sorted(processos),
            "processos_info": processos_info,
            "statuses": sorted(statuses),
            "nodos": sorted(nodos),
            "acoes": acoes,
            "robos": sorted(robos),
            "data_min": min_date.isoformat() if min_date else None,
            "data_max": max_date.isoformat() if max_date else None,
            "total_geral": self._collection.estimated_document_count(),
            "status_nao_erro_keywords": STATUS_NAO_ERRO_KEYWORDS
        }

    def aggregate_summary_kpis(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula totais, sucessos, repassados/fluid, erros reais e taxas agregadas no MongoDB via facet."""
        is_succ = get_mongo_is_success_cond()
        is_rep = get_mongo_is_non_error_cond()
        is_err = get_mongo_is_error_cond()

        pipeline = [
            {"$match": query},
            {
                "$facet": {
                    "totals": [
                        {
                            "$group": {
                                "_id": None,
                                "total": {"$sum": 1},
                                "sucesso": {
                                    "$sum": {"$cond": [is_succ, 1, 0]}
                                },
                                "repassado": {
                                    "$sum": {"$cond": [is_rep, 1, 0]}
                                },
                                "erro": {
                                    "$sum": {"$cond": [is_err, 1, 0]}
                                },
                                "avg_execucoes": {"$avg": "$execucoes"}
                            }
                        }
                    ],
                    "status_breakdown": [
                        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
                    ],
                    "processos_count": [
                        {"$group": {"_id": "$nome_processo", "count": {"$sum": 1}}}
                    ]
                }
            }
        ]

        result = list(self._collection.aggregate(pipeline))
        totals = result[0]["totals"][0] if result and result[0]["totals"] else {
            "total": 0, "sucesso": 0, "repassado": 0, "erro": 0, "avg_execucoes": 0
        }
        status_breakdown = result[0]["status_breakdown"] if result else []
        processos_count = result[0]["processos_count"] if result else []

        total = totals.get("total", 0)
        sucesso = totals.get("sucesso", 0)
        repassado = totals.get("repassado", 0)
        erro = totals.get("erro", 0)
        taxa_sucesso = round((sucesso / total * 100), 1) if total > 0 else 0.0
        taxa_sem_erro = round(((total - erro) / total * 100), 1) if total > 0 else 0.0

        return {
            "total": total,
            "sucesso": sucesso,
            "repassado": repassado,
            "erro": erro,
            "taxa_sucesso": taxa_sucesso,
            "taxa_sem_erro": taxa_sem_erro,
            "avg_execucoes": round(totals.get("avg_execucoes") or 0, 2),
            "status_breakdown": status_breakdown,
            "processos_count": processos_count
        }

    def aggregate_timeseries(self, query: Dict[str, Any], date_format: str) -> List[Dict[str, Any]]:
        """Executa agregação temporal agrupando por período e status classificado."""
        pipeline = [
            {"$match": query},
            {
                "$project": {
                    "period": {
                        "$dateToString": {
                            "format": date_format,
                            "date": {"$ifNull": ["$data_realizacao", "$data_cadastro"]}
                        }
                    },
                    "status": 1
                }
            },
            {
                "$group": {
                    "_id": {
                        "period": "$period",
                        "status": "$status"
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id.period": 1}}
        ]

        results = list(self._collection.aggregate(pipeline))

        buckets = {}
        for row in results:
            period = row["_id"]["period"]
            if not period:
                continue
            status_val = str(row["_id"].get("status") or "")
            count = row["count"]

            if period not in buckets:
                buckets[period] = {"period": period, "sucesso": 0, "repassado": 0, "erro": 0, "total": 0}

            cat = classify_status(status_val)
            buckets[period][cat] += count
            buckets[period]["total"] += count

        return sorted(buckets.values(), key=lambda x: x["period"])

    def aggregate_distributions(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula distribuição por ação, nodo e processo com categorias de sucesso, repassado e erro."""
        is_succ = get_mongo_is_success_cond()
        is_rep = get_mongo_is_non_error_cond()
        is_err = get_mongo_is_error_cond()

        pipeline = [
            {"$match": query},
            {
                "$facet": {
                    "by_acao": [
                        {
                            "$project": {
                                "acao": {
                                    "$ifNull": [
                                        "$infos_retorno.fluid_api.acao_nodo",
                                        "Não Informada"
                                    ]
                                },
                                "status": 1
                            }
                        },
                        {
                            "$group": {
                                "_id": "$acao",
                                "total": {"$sum": 1},
                                "sucesso": {
                                    "$sum": {"$cond": [is_succ, 1, 0]}
                                },
                                "repassado": {
                                    "$sum": {"$cond": [is_rep, 1, 0]}
                                },
                                "erro": {
                                    "$sum": {"$cond": [is_err, 1, 0]}
                                }
                            }
                        },
                        {"$sort": {"total": -1}}
                    ],
                    "by_nodo": [
                        {
                            "$group": {
                                "_id": "$fluid_infos.nodo",
                                "total": {"$sum": 1},
                                "sucesso": {
                                    "$sum": {"$cond": [is_succ, 1, 0]}
                                },
                                "repassado": {
                                    "$sum": {"$cond": [is_rep, 1, 0]}
                                },
                                "erro": {
                                    "$sum": {"$cond": [is_err, 1, 0]}
                                }
                            }
                        },
                        {"$sort": {"total": -1}},
                        {"$limit": 10}
                    ],
                    "by_processo": [
                        {
                            "$group": {
                                "_id": "$nome_processo",
                                "total": {"$sum": 1},
                                "sucesso": {
                                    "$sum": {"$cond": [is_succ, 1, 0]}
                                },
                                "repassado": {
                                    "$sum": {"$cond": [is_rep, 1, 0]}
                                },
                                "erro": {
                                    "$sum": {"$cond": [is_err, 1, 0]}
                                }
                            }
                        },
                        {"$sort": {"total": -1}}
                    ]
                }
            }
        ]

        result = list(self._collection.aggregate(pipeline))
        return result[0] if result else {"by_acao": [], "by_nodo": [], "by_processo": []}

    def find_paginated_tasks(self, query: Dict[str, Any], page: int, page_size: int, sort_by: str, sort_desc: bool) -> Dict[str, Any]:
        """Consulta paginada com projeção para máxima eficiência de rede e memória."""
        total_count = self._collection.count_documents(query)
        sort_direction = DESCENDING if sort_desc else ASCENDING
        skip = (page - 1) * page_size

        projection = {
            "_id": 1,
            "num_processo": 1,
            "nome_processo": 1,
            "status": 1,
            "data_cadastro": 1,
            "data_realizacao": 1,
            "robo": 1,
            "execucoes": 1,
            "detalhes": 1,
            "fluid_infos.nodo": 1,
            "fluid_infos.processo_id": 1,
            "infos_retorno.fluid_api.acao_nodo": 1
        }

        cursor = self._collection.find(query, projection).sort([(sort_by, sort_direction)]).skip(skip).limit(page_size)
        items = []
        for doc in cursor:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            if doc.get("data_cadastro"):
                doc["data_cadastro"] = doc["data_cadastro"].isoformat()
            if doc.get("data_realizacao"):
                doc["data_realizacao"] = doc["data_realizacao"].isoformat()
            
            fluid_api = doc.get("infos_retorno", {}).get("fluid_api", {})
            doc["acao"] = fluid_api.get("acao_nodo") or "-"
            doc["nodo"] = doc.get("fluid_infos", {}).get("nodo") or "-"
            items.append(doc)

        total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 1

        return {
            "items": items,
            "page": page,
            "page_size": page_size,
            "total_items": total_count,
            "total_pages": total_pages
        }

    def find_task_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Localiza e formata uma tarefa específica pelo ObjectId do MongoDB."""
        try:
            doc = self._collection.find_one({"_id": ObjectId(task_id)})
        except Exception:
            return None

        if not doc:
            return None

        doc["id"] = str(doc["_id"])
        del doc["_id"]
        if doc.get("data_cadastro"):
            doc["data_cadastro"] = doc["data_cadastro"].isoformat()
        if doc.get("data_realizacao"):
            doc["data_realizacao"] = doc["data_realizacao"].isoformat()
        return doc
