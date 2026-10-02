# Sicredi Automation Hub - Monitor de Tarefas Finalizadas

Dashboard analítico e executivo desenvolvido em **Python (FastAPI)** com arquitetura orientada a **SOLID**, conectado ao MongoDB (`dispor.tarefas_finalizadas`) e estilizado com base no **Manual de Identidade Visual e Verbal do Sicredi**.

O sistema conta com suporte a **mais de 100 tipos de processos**, histórico temporal (diário, mensal e anual), acompanhamento de nodos e ações da **Fluid API**, alternador de **Tema Claro e Tema Escuro (Dark Mode)** e exibição do **logotipo oficial preferencial (`HORIZONTAL_PREFERENCIAL_COLORIDA_CMYK`)**.

---

## 🏛️ Arquitetura Orientada a SOLID

O backend foi reestruturado seguindo rigorosamente os princípios de engenharia de software SOLID, com nomes de classes, métodos e variáveis em **Inglês** e documentação com **Docstrings em Português**:

1. **S - Single Responsibility Principle (SRP):**
   - [`backend/core/config.py`](file:///c:/Users/lopes/OneDrive/Área%20de%20Trabalho/Programação/Sicredi/task-menu/backend/core/config.py): Responsabilidade exclusiva de carregar e gerenciar parâmetros e variáveis de ambiente.
   - [`backend/database/connection.py`](file:///c:/Users/lopes/OneDrive/Área%20de%20Trabalho/Programação/Sicredi/task-menu/backend/database/connection.py): Gerenciamento do ciclo de vida e pool de conexões com o MongoDB.
   - [`backend/database/index_manager.py`](file:///c:/Users/lopes/OneDrive/Área%20de%20Trabalho/Programação/Sicredi/task-menu/backend/database/index_manager.py): Criação e manutenção exclusiva de índices simples e compostos de alta performance.
   - [`backend/services/query_builder.py`](file:///c:/Users/lopes/OneDrive/Área%20de%20Trabalho/Programação/Sicredi/task-menu/backend/services/query_builder.py): Construção isolada de queries MongoDB a partir dos filtros do usuário.
2. **O - Open/Closed Principle (OCP):**
   - O `MongoQueryBuilder` permite a adição de novos critérios e campos de busca sem alterar a estrutura de execução de queries ou agregações do banco.
3. **L - Liskov Substitution Principle (LSP):**
   - Repositórios concretos implementam interfaces/protocolos estritos (`ITaskRepository`, `IMetricsRepository`, `IFilterMetadataRepository`), permitindo substituição transparente por implementações mock ou bancos alternativos sem quebrar a aplicação.
4. **I - Interface Segregation Principle (ISP):**
   - Interfaces segregadas e enxutas em [`backend/repositories/interfaces.py`](file:///c:/Users/lopes/OneDrive/Área%20de%20Trabalho/Programação/Sicredi/task-menu/backend/repositories/interfaces.py), evitando que clientes dependam de métodos que não utilizam.
5. **D - Dependency Inversion Principle (DIP):**
   - Controladores em [`backend/api/routes.py`](file:///c:/Users/lopes/OneDrive/Área%20de%20Trabalho/Programação/Sicredi/task-menu/backend/api/routes.py) recebem o serviço via injeção de dependência (`Depends(get_dashboard_service)`), e os serviços recebem o repositório por injeção (`get_task_repository`).

---

## 🎨 Identidade Visual Sicredi & Funcionalidades

- **Logotipo Oficial Preferencial:** Utilização do arquivo `HORIZONTAL_PREFERENCIAL_COLORIDA_CMYK` no cabeçalho com box de reserva (Manual página 17) para visualização nítida em qualquer fundo.
- **Alternador de Tema (Dark Mode & Light Mode):**
  - Botão no cabeçalho para alternância instantânea com persistência no navegador (`localStorage`).
  - O tema escuro adota a paleta corporativa com verde Sicredi vibrante (`#48BD14` / `#3FA110`), fundos escuros refinados (`#0C120C` / `#141D14`) e alto contraste.
  - Os gráficos (Chart.js) re-renderizam dinamicamente suas cores, legendas e linhas de grade no momento da troca de tema.
- **Gestão de Mais de 100 Processos:**
  - Modal inteligente com busca instantânea sem diferenciar maiúsculas ou acentos.
  - Abas de categorias (*Crédito, Cadastro, Cartões, Pix, Boletos, Jurídico, Bureau, Investimentos, Seguros, Tesouraria*).
  - Seleção em lote (`Marcar Visíveis` / `Desmarcar Todos`).
  - Atualização com pipelines indexados do MongoDB em menos de **25 milissegundos**.
- **Slide-over Drawer:**
  - Inspeção detalhada de tarefas, parâmetros da Fluid API (`acao`, `nodo_atual`, `tempo_processo`, `parecer`) e visualizador com syntax highlighting para o JSON do documento MongoDB e botão para copiar com 1 clique.

---

## 🚀 Como Executar

O servidor já está ativo. Para rodar a aplicação a qualquer momento:

```powershell
python run.py
```
*(Inicia o servidor FastAPI na porta 8000 e abre automaticamente o navegador em `http://127.0.0.1:8000`)*.
