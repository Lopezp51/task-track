import random
from datetime import datetime, timedelta
from pymongo import MongoClient

def seed_large_dataset(count=1500):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["dispor"]
    col = db["tarefas_finalizadas"]
    
    current_count = col.count_documents({})
    print(f"Current count in collection: {current_count}")
    
    processos = [
        "Radar Judicial | Robô",
        "Consulta Bureau de Crédito",
        "Emissão de Certidões",
        "Conciliação Financeira Diária",
        "Validação Cadastral PJ"
    ]
    
    robos = ["Localhost", "Worker-01-RS", "Worker-02-PR", "Worker-03-SP"]
    acoes = ["acao_1", "acao_2", "acao_3", "acao_4", "acao_notificacao", "acao_revisao"]
    statuses = ["sucesso", "sucesso", "sucesso", "sucesso", "erro_negocio", "erro_sistema"]
    nodos_pool = [59686, 56078, 57608, 59672, 52889, 58433, 56171, 57193, 54353, 53574, 54907, 53229, 53604]

    now = datetime.now()
    batch = []
    
    print(f"Generating {count} realistic automation tasks across last 180 days...")
    for i in range(count):
        days_ago = random.randint(0, 180)
        minutes_offset = random.randint(0, 1440)
        task_date = now - timedelta(days=days_ago, minutes=minutes_offset)
        duration_seconds = random.randint(5, 120)
        realizacao_date = task_date + timedelta(seconds=duration_seconds)
        
        proc = random.choice(processos)
        status = random.choice(statuses)
        acao = random.choice(acoes)
        nodo = random.choice(nodos_pool)
        
        doc = {
            "num_processo": 1000000 + current_count + i,
            "nome_processo": proc,
            "status": status,
            "prioridade": random.choice([0, 1, 2]),
            "etapa": 200,
            "desc_etapa": "Finalizar",
            "data_cadastro": task_date,
            "data_realizacao": realizacao_date,
            "robo": random.choice(robos),
            "execucoes": random.choice([1, 1, 1, 2, 3]),
            "detalhes": "Protocolado com sucesso" if status == "sucesso" else "Falha de validação ou timeout no portal",
            "fluid_infos": {
                "processo_id": random.randint(800, 950),
                "arvore": random.randint(1000, 2500),
                "nodo": nodo,
                "email_resp": "robo.automacao@empresa.com.br",
                "emp_origem": "Sede"
            },
            "infos_envio": {},
            "infos_retorno": {
                "fluid_api": {
                    "tipo_processo": random.randint(800, 950),
                    "tempo_processo": duration_seconds,
                    "versao_arvore": 1736,
                    "acao": acao,
                    "empresa_origem": [],
                    "empresa_destino": [],
                    "resp_destino": {
                        "acao_nodo": acao,
                        "nodo_atual": nodo,
                        "parecer": "Execução concluída" if status == "sucesso" else "Erro no processamento"
                    }
                },
                "infos_campos": {},
                "anexos": {}
            }
        }
        batch.append(doc)

    col.insert_many(batch)
    print(f"Successfully inserted {count} records! New total: {col.count_documents({})}")

if __name__ == "__main__":
    seed_large_dataset(1200)
