# -*- coding: utf-8 -*-
import random
from datetime import datetime, timedelta
from pymongo import MongoClient

PROCESSOS_SICREDI = [
    # Crédito e Financiamento
    "Análise de Crédito - Pronaf Custeio",
    "Análise de Crédito - Pronamp Investimento",
    "Crédito Pessoal - Aprovação Automática",
    "Crédito Consignado - Averbação INSS",
    "Crédito Consignado - Averbação Servidor Público",
    "Financiamento Solar - Análise Técnica",
    "Financiamento Veículos - Validação Detran",
    "Financiamento Imobiliário - Análise Documental",
    "Renovação de Limite - Cheque Especial",
    "Liberação de Capital de Giro PJ",
    "Antecipação de Recebíveis de Cartão",
    "Desconto de Duplicatas Mercantis",
    "Repactuação de Dívidas Agro",
    "Esteira de Crédito Imobiliário - Laudo de Avaliação",
    "Esteira de Crédito - Vistoria Rural Geoespacial",

    # Cadastro e Onboarding
    "Abertura de Conta Corrente PF Digital",
    "Abertura de Conta Corrente PJ Digital",
    "Abertura de Conta Poupança Integrada",
    "Atualização Cadastral Periódica PF",
    "Atualização Cadastral Periódica PJ",
    "Validação Biométrica Facial - Onboarding",
    "Validação de Documentos de Identificação (OCR)",
    "Consulta QSA (Quadro Societário) Receita Federal",
    "Validação de Comprovante de Renda Automática",
    "Validação de Procuradores e Contrato Social",
    "Enquadramento de Risco PLD-FT",
    "Consulta Sanções Internacionais e OFAC",
    "Monitoramento de Pessoas Politicamente Expostas (PEP)",
    "Homologação Cadastral de Novo Cooperado",
    "Integralização de Quota-Parte Cooperativa",

    # Cartões e Meios de Pagamento
    "Emissão de Cartão Sicredi Débito",
    "Emissão de Cartão Sicredi Touch / Internacional",
    "Emissão de Cartão Sicredi Gold / Platinum",
    "Emissão de Cartão Sicredi Mastercard Black",
    "Bloqueio Preventivo por Suspeita de Fraude",
    "Desbloqueio de Cartão por Autenticação Segura",
    "Contestação de Despesas de Cartão (Chargeback)",
    "Alteração de Limite Emergencial de Cartão",
    "Credenciamento de Maquininhas Sipag",
    "Conciliação Financeira Sipag Diária",
    "Geração de Cartão Virtual Temporário",
    "Gestão de Programa de Recompensas Sicredi",

    # Pix e Pagamentos Instantâneos
    "Validação e Registro de Chave Pix DICT",
    "Portabilidade de Chave Pix",
    "Reivindicação de Posse de Chave Pix",
    "Devolução de Pix via Mecanismo Especial (MED)",
    "Liquidação de Lotes Pix Noturno",
    "Auditoria de Fraude Transacional Pix",
    "Validação de QRCode Pix Dinâmico Cobrança",
    "Processamento de Pix Agendado",

    # Cobrança e Boletos
    "Registro Online de Boletos CIP",
    "Emissão de 2ª Via de Boleto Registrado",
    "Baixa Operacional de Título Liquidado",
    "Instrução de Protesto de Título em Cartório",
    "Sustação de Protesto de Cobrança",
    "Concessão de Abatimento e Desconto em Boleto",
    "Alteração de Data de Vencimento de Título",
    "Conciliação de Arquivo Retorno CNAB 240/400",
    "Envio de Remessa CNAB Bancária",

    # Jurídico e Regulatório
    "Radar Judicial - Monitoramento de Diários Oficiais",
    "Radar Judicial - Protocolo de Defesa Inicial",
    "SISBAJUD - Bloqueio de Valores em Conta",
    "SISBAJUD - Desbloqueio e Transferência Judicial",
    "RENAJUD - Bloqueio e Restrição de Veículos",
    "SERASAJUD - Inclusão e Baixa de Apontamentos",
    "Cumprimento de Ofício Judicial Trabalhista",
    "Resposta a Requisições BACEN / COAF",
    "Envio de Informes Cadastrais Judiciais",
    "Arquivo de Contestação Procon / Consumidor.gov",

    # Bureau e Análise de Risco
    "Consulta Bureau de Crédito - Serasa Experian",
    "Consulta Bureau de Crédito - Boa Vista SCPC",
    "Consulta SCR Banco Central (Registrato)",
    "Score de Crédito Cooperativo - Recálculo Mensal",
    "Consulta de Protestos IEPTB Nacional",
    "Consulta CND Receita Federal e PGFN",
    "Consulta Certidão Negativa de Débitos Trabalhistas (CNDT)",
    "Consulta Sintegra / Cadastro Estadual ICMS",
    "Consulta Regularidade FGTS (CRF Caixa)",
    "Emissão de Certidões Negativas Cíveis e Criminais",

    # Investimentos e Previdência
    "Aplicação em RDC (Recibo de Depósito Cooperativo)",
    "Resgate de Aplicação Financeira RDC",
    "Aplicação em LCA Agro Isenta de IR",
    "Adesão a Plano de Previdência Privada Multipatrocinado",
    "Portabilidade de Previdência Privada Entrada",
    "Portabilidade de Previdência Privada Saída",
    "Distribuição de Sobras Cooperativas (JCP)",
    "Pagamento de Juros sobre Capital Próprio",

    # Seguros e Consórcios
    "Emissão de Apólice - Seguro Agrícola Multirrisco",
    "Emissão de Apólice - Seguro Vida Associado",
    "Emissão de Apólice - Seguro Automóvel Frota",
    "Emissão de Apólice - Seguro Residencial e Empresarial",
    "Abertura e Regulação de Sinistro Agro",
    "Adesão a Cota de Consórcio Imobiliário",
    "Adesão a Cota de Consórcio Automóvel / Pesados",
    "Contemplação por Sorteio e Lance Consórcio",
    "Faturamento de Bem Imóvel Consórcio",

    # Operações de Tesouraria e Câmbio
    "Fechamento de Câmbio Exportação Agro",
    "Fechamento de Câmbio Importação Insumos",
    "Remessa Internacional Expressa",
    "Transferência Interbancária TED / STR",
    "Conciliação Contábil Fim de Dia Agência",
    "Compensação de Cheques Compe Central",
    "Suprimento e Recolhimento de Numerário ATM",
    "Fechamento de Caixa Físico Agência"
]

ROBOS_POOL = [
    "Robo-RS-PortoAlegre-01",
    "Robo-PR-Curitiba-02",
    "Robo-MT-Cuiaba-03",
    "Robo-SP-Capital-04",
    "Robo-MS-CampoGrande-05",
    "Robo-GO-Goiania-06",
    "Robo-Localhost-Dev"
]

STATUSES_WEIGHTED = ["sucesso"] * 82 + ["erro_negocio"] * 12 + ["erro_sistema"] * 6
ACOES_POOL = [
    "acao_1",
    "acao_2",
    "acao_3",
    "acao_4",
    "acao_concluir",
    "acao_retorno_pendencia",
    "acao_encaminhar_mesa",
    "acao_notificar_agencia",
    "acao_revisao_manual",
    "acao_reprocessar"
]

NODOS_BASE = [
    50100, 50200, 50350, 51400, 52100, 52889, 53229, 53574, 53604,
    54090, 54353, 54546, 54907, 55000, 55929, 56016, 56078, 56171,
    56624, 56845, 57193, 57608, 58367, 58433, 58732, 59412, 59672,
    59686, 60120, 61200, 62300, 63400, 64500, 65600, 67800, 69900
]

def populate_100_processes(total_records=3500):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["dispor"]
    col = db["tarefas_finalizadas"]

    print("=" * 60)
    print(f"Limpando e repovoando banco com {len(PROCESSOS_SICREDI)} processos em UTF-8...")
    print("=" * 60)

    col.delete_many({})

    now = datetime.now()
    batch = []
    
    process_list_expanded = []
    for proc in PROCESSOS_SICREDI:
        process_list_expanded.extend([proc] * 12)
    
    while len(process_list_expanded) < total_records:
        process_list_expanded.append(random.choice(PROCESSOS_SICREDI))

    random.shuffle(process_list_expanded)

    for i, proc in enumerate(process_list_expanded):
        days_ago = random.randint(0, 180)
        minutes_offset = random.randint(0, 1440)
        data_cad = now - timedelta(days=days_ago, minutes=minutes_offset)
        duration_s = random.randint(2, 95)
        data_real = data_cad + timedelta(seconds=duration_s)

        status = random.choice(STATUSES_WEIGHTED)
        acao = random.choice(ACOES_POOL)
        nodo = random.choice(NODOS_BASE)
        robo = random.choice(ROBOS_POOL)
        execucoes = 1 if status == "sucesso" else random.choice([1, 2, 3])

        if status == "sucesso":
            detalhe = random.choice([
                "Execução concluída com sucesso no portal",
                "Protocolado no sistema de destino",
                "Validação automatizada sem ressalvas",
                "Comprovante gerado e armazenado",
                "Fluxo concluído dentro do SLA estipulado"
            ])
            parecer = "Aprovado / Finalizado sem inconsistências"
        elif status == "erro_negocio":
            detalhe = random.choice([
                "Pendência de documentação do cooperado",
                "Score abaixo do corte parametrizado",
                "Chave Pix já vinculada a outra titularidade",
                "Saldo insuficiente para quitação",
                "Dados cadastrais divergentes na Receita Federal"
            ])
            parecer = "Encaminhado para mesa operacional / análise humana"
        else: # erro_sistema
            detalhe = random.choice([
                "Timeout de conexão no Webservice externo",
                "Portal governamental indisponível (HTTP 503)",
                "Falha na quebra de Captcha / Recaptcha",
                "Sessão expirada durante processamento"
            ])
            parecer = "Reagendado para fila de retry automático"

        num_proc = 1000000 + i

        doc = {
            "num_processo": num_proc,
            "nome_processo": proc,
            "status": status,
            "prioridade": random.choice([0, 1, 2]),
            "etapa": 200,
            "desc_etapa": "Finalizar",
            "data_cadastro": data_cad,
            "data_realizacao": data_real,
            "robo": robo,
            "execucoes": execucoes,
            "detalhes": detalhe,
            "fluid_infos": {
                "processo_id": random.randint(1000, 9999),
                "arvore": random.randint(100, 3000),
                "nodo": nodo,
                "email_resp": "automacao.rpa@sicredi.com.br",
                "emp_origem": "CAS - Centro Administrativo Sicredi"
            },
            "infos_envio": {},
            "infos_retorno": {
                "fluid_api": {
                    "tipo_processo": random.randint(100, 900),
                    "tempo_processo": duration_s,
                    "versao_arvore": random.randint(1, 15),
                    "acao": acao,
                    "empresa_origem": [],
                    "empresa_destino": [],
                    "resp_destino": {
                        "acao_nodo": acao,
                        "nodo_atual": nodo,
                        "parecer": parecer
                    }
                },
                "infos_campos": {},
                "anexos": {}
            }
        }
        batch.append(doc)

        if len(batch) >= 500:
            col.insert_many(batch)
            batch = []

    if batch:
        col.insert_many(batch)

    print(f"Sucesso! Banco populado com {col.count_documents({})} tarefas em UTF-8.")
    print(f"Total de processos distintos no banco: {len(col.distinct('nome_processo'))}")

if __name__ == "__main__":
    populate_100_processes(3500)
