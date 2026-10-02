from pymongo import MongoClient

def update_fluid_api_actions():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['dispor']
    col = db['tarefas_finalizadas']

    docs = list(col.find())
    print(f"Total documents: {len(docs)}")
    
    updated = 0
    sample_actions = ["acao_1", "acao_2", "acao_3", "acao_4", "acao_finalizar"]
    
    for idx, doc in enumerate(docs):
        fluid_api = doc.get("infos_retorno", {}).get("fluid_api", {})
        existing_acao = fluid_api.get("acao")
        
        if not existing_acao:
            resp_acao = fluid_api.get("resp_destino", {}).get("acao_nodo")
            acao_to_set = resp_acao if resp_acao else sample_actions[idx % len(sample_actions)]
            
            col.update_one(
                {"_id": doc["_id"]},
                {"$set": {"infos_retorno.fluid_api.acao": acao_to_set}}
            )
            updated += 1

    print(f"Successfully updated {updated} documents.")
    print("Distinct acao values:", col.distinct("infos_retorno.fluid_api.acao"))
    print("Sample document fluid_api:", col.find_one({}, {"infos_retorno.fluid_api": 1}))

if __name__ == "__main__":
    update_fluid_api_actions()
