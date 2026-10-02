from datetime import datetime
from typing import Dict, Any, List

class MongoQueryBuilder:
    """Constrói dinamicamente filtros para consultas MongoDB aderindo ao Open/Closed Principle (OCP)."""

    @classmethod
    def build_query(cls, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera o dicionário de filtros estruturado para o MongoDB a partir dos parâmetros fornecidos.
        
        :param filters: Dicionário com opções de filtros (processos, status, nodos, acoes, datas, search)
        :return: Expressão de consulta pronta para `$match` ou `.find()`
        """
        query: Dict[str, Any] = {}

        # 1. Filtro por Processos
        processos = filters.get("processos")
        if processos:
            if isinstance(processos, list) and len(processos) > 0 and "TODOS" not in [p.upper() for p in processos]:
                query["nome_processo"] = {"$in": processos}
            elif isinstance(processos, str) and processos.upper() != "TODOS":
                query["nome_processo"] = processos

        # 2. Filtro por Status
        status = filters.get("status")
        if status and status.upper() != "TODOS":
            if isinstance(status, list) and len(status) > 0 and "TODOS" not in [s.upper() for s in status]:
                query["status"] = {"$in": status}
            elif isinstance(status, str):
                query["status"] = status

        # 3. Filtro por Nodo
        nodos = filters.get("nodos")
        if nodos:
            if isinstance(nodos, list) and len(nodos) > 0 and "TODOS" not in nodos:
                int_nodos = []
                for n in nodos:
                    try:
                        int_nodos.append(int(n))
                    except (ValueError, TypeError):
                        pass
                if int_nodos:
                    query["fluid_infos.nodo"] = {"$in": int_nodos}
            elif isinstance(nodos, (int, str)) and str(nodos).upper() != "TODOS":
                try:
                    query["fluid_infos.nodo"] = int(nodos)
                except (ValueError, TypeError):
                    pass

        # 4. Filtro por Ação
        acoes = filters.get("acoes")
        if acoes:
            if isinstance(acoes, list) and len(acoes) > 0 and "TODOS" not in [a.upper() for a in acoes]:
                query["infos_retorno.fluid_api.acao_nodo"] = {"$in": acoes}
            elif isinstance(acoes, str) and acoes.upper() != "TODOS":
                query["infos_retorno.fluid_api.acao_nodo"] = acoes

        # 5. Filtro por Intervalo de Datas
        data_inicio = filters.get("data_inicio")
        data_fim = filters.get("data_fim")
        if data_inicio or data_fim:
            date_clause = {}
            if data_inicio:
                if isinstance(data_inicio, str):
                    data_inicio = datetime.fromisoformat(data_inicio.replace("Z", "+00:00"))
                date_clause["$gte"] = data_inicio
            if data_fim:
                if isinstance(data_fim, str):
                    data_fim = datetime.fromisoformat(data_fim.replace("Z", "+00:00"))
                date_clause["$lte"] = data_fim
            if date_clause:
                query["data_realizacao"] = date_clause

        # 6. Busca Textual por Número de Processo ou Detalhes
        search = filters.get("search")
        if search:
            search_str = str(search).strip()
            if search_str:
                clauses = [{"detalhes": {"$regex": search_str, "$options": "i"}}]
                try:
                    clauses.append({"num_processo": int(search_str)})
                except ValueError:
                    pass
                if "$or" in query:
                    query["$and"] = [{"$or": query.pop("$or")}, {"$or": clauses}]
                else:
                    query["$or"] = clauses

        return query
