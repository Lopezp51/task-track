"""
Configuração Central de Categorização de Status de Execução
-----------------------------------------------------------
Este módulo define quais status representam Sucesso, quais representam tarefas
repassadas / protocolos manuais / Fluid (que NÃO devem ser contabilizadas como erro),
e quais são falhas reais.

Como adicionar novos status que NÃO são erro:
Basta adicionar a palavra ou termo desejado (em minúsculas) na lista
`STATUS_NAO_ERRO_KEYWORDS` abaixo.
Exemplo: Se você passar a usar "REDIRECIONADO", adicione "redirecionad".
"""

from typing import List, Optional, Dict, Any

# ==============================================================================
# CONFIGURAÇÃO DE PALAVRAS-CHAVE / PREFIXOS (CASE-INSENSITIVE)
# ==============================================================================

# Status ou termos que NÃO representam erro (ex: Fluid, Repassado Pedro, manual, etc.)
# Se o status contiver qualquer um desses termos, NÃO será contabilizado como erro.
STATUS_NAO_ERRO_KEYWORDS: List[str] = [
    "fluid",           # Encaminhado para a etapa Fluid
    "repassad",        # Cobre: 'repassado', 'REPASSADO', 'Repassado Pedro', 'repassada', etc.
    "manual",          # Protocolo manual, intervenção manual, etc.
    "protocolad",      # Protocolado, protocolado manual, etc.
    "em andamento",    # Tarefas em fluxo
    "pendente",        # Tarefas aguardando
]

# Status que representam Sucesso direto da automação
STATUS_SUCESSO_KEYWORDS: List[str] = [
    "sucesso",
    "concluido",
    "concluído"
]

# ==============================================================================
# FUNÇÕES UTILITÁRIAS
# ==============================================================================

def get_non_error_regex() -> str:
    """Gera padrão Regex para casar qualquer termo da lista de não-erros."""
    return "|".join(STATUS_NAO_ERRO_KEYWORDS)

def get_success_regex() -> str:
    """Gera padrão Regex para casar qualquer termo da lista de sucessos."""
    return "|".join(STATUS_SUCESSO_KEYWORDS)

def classify_status(status_raw: Optional[str]) -> str:
    """
    Classifica um status textual em uma das três categorias:
    - 'sucesso': execução concluída com êxito
    - 'repassado': etapa do Fluid, repassado manual, em andamento (NÃO é erro)
    - 'erro': falhas de negócio ou de sistema
    """
    if not status_raw:
        return "erro"
    
    st_clean = str(status_raw).strip().lower()

    # 1. Verifica Sucesso
    for kw in STATUS_SUCESSO_KEYWORDS:
        if kw in st_clean:
            return "sucesso"

    # 2. Verifica se é Fluid / Repassado / Manual (NÃO é erro)
    for kw in STATUS_NAO_ERRO_KEYWORDS:
        if kw in st_clean:
            return "repassado"

    # 3. Caso contrário, considera erro
    return "erro"

# ==============================================================================
# EXPRESSÕES MONGODB ($cond / $regexMatch)
# ==============================================================================

def get_mongo_is_success_cond() -> Dict[str, Any]:
    """Retorna expressão booleana MongoDB para identificar status de sucesso."""
    return {
        "$regexMatch": {
            "input": {"$toLower": {"$ifNull": ["$status", ""]}},
            "regex": get_success_regex()
        }
    }

def get_mongo_is_non_error_cond() -> Dict[str, Any]:
    """Retorna expressão booleana MongoDB para identificar tarefas Repassadas / Fluid (não erro)."""
    return {
        "$and": [
            {"$not": get_mongo_is_success_cond()},
            {
                "$regexMatch": {
                    "input": {"$toLower": {"$ifNull": ["$status", ""]}},
                    "regex": get_non_error_regex()
                }
            }
        ]
    }

def get_mongo_is_error_cond() -> Dict[str, Any]:
    """Retorna expressão booleana MongoDB para identificar falhas reais."""
    return {
        "$and": [
            {"$not": get_mongo_is_success_cond()},
            {
                "$not": {
                    "$regexMatch": {
                        "input": {"$toLower": {"$ifNull": ["$status", ""]}},
                        "regex": get_non_error_regex()
                    }
                }
            }
        ]
    }
