import { updateTimeSeriesChart, updateHealthDoughnut, updateActionsChart, updateNodosChart, setChartTheme } from './charts.js';

// Helper: Normalize string (remove accents and lowercase)
function normalizeText(str) {
  if (!str) return '';
  return str.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
}

// Application State
const state = {
  filters: {
    processos: [], // Empty array = "TODOS"
    status: 'TODOS',
    acoes: 'TODOS',
    nodos: 'TODOS',
    data_inicio: null,
    data_fim: null,
    search: ''
  },
  granularity: 'daily',
  pagination: {
    page: 1,
    page_size: 25,
    sort_by: 'data_realizacao',
    sort_desc: true,
    total_pages: 1,
    total_items: 0
  },
  availableOptions: {
    processos: [],
    processos_info: [], // { nome, count }
    statuses: [],
    nodos: [],
    acoes: []
  },
  nonErrorKeywords: ['fluid', 'repassad', 'manual', 'protocolad', 'pendente', 'em andamento'],
  modal: {
    searchTerm: '',
    selectedCategory: 'todas',
    tempSelectedProcessos: []
  }
};

// Classifica o status e retorna rótulo e classe CSS do badge
export function getStatusBadgeInfo(statusRaw) {
  const status = (statusRaw || '').trim();
  const lower = status.toLowerCase();

  // 1. Sucesso
  if (lower === 'sucesso' || lower === 'concluido' || lower === 'concluído') {
    return {
      category: 'sucesso',
      badgeClass: 'sucesso',
      label: status || 'Sucesso'
    };
  }

  // 2. Não-Erros (Fluid, Repassado Pedro, manual, etc.)
  const keywords = state.nonErrorKeywords || ['fluid', 'repassad', 'manual', 'protocolad', 'pendente', 'em andamento'];
  const isNonError = keywords.some(kw => lower.includes(kw));
  if (isNonError) {
    return {
      category: 'repassado',
      badgeClass: 'repassado',
      label: status // mantém o texto original ex: 'Fluid', 'Repassado Pedro', 'REPASSADO'
    };
  }

  // 3. Falhas reais
  const isSistema = lower.includes('sistema');
  return {
    category: 'erro',
    badgeClass: isSistema ? 'erro_sistema' : 'erro_negocio',
    label: status || 'Erro Negócio'
  };
}

// DOM Elements
const dbStatusPill = document.getElementById('dbStatusPill');
const activeProcessLabel = document.getElementById('activeProcessLabel');
const totalProcessCountBadge = document.getElementById('totalProcessCountBadge');
const topProcessesRow = document.getElementById('topProcessesRow');
const pillAllProcesses = document.getElementById('pillAllProcesses');
const pillTotalCount = document.getElementById('pillTotalCount');

// Filter Inputs
const statusSelect = document.getElementById('statusSelect');
const acaoSelect = document.getElementById('acaoSelect');
const nodoSelect = document.getElementById('nodoSelect');
const searchInput = document.getElementById('searchInput');
const dateStartInput = document.getElementById('dateStart');
const dateEndInput = document.getElementById('dateEnd');
const queryTimingEl = document.getElementById('queryTiming');

// Theme Toggle Elements
const themeToggleBtn = document.getElementById('themeToggleBtn');
const themeToggleIcon = document.getElementById('themeToggleIcon');
const themeToggleText = document.getElementById('themeToggleText');

// Process Multi-Selection Modal Elements
const btnOpenProcessModal = document.getElementById('btnOpenProcessModal');
const processModalOverlay = document.getElementById('processModalOverlay');
const btnCloseProcessModal = document.getElementById('btnCloseProcessModal');
const btnModalCancel = document.getElementById('btnModalCancel');
const btnModalApply = document.getElementById('btnModalApply');
const modalProcessSearch = document.getElementById('modalProcessSearch');
const modalProcessList = document.getElementById('modalProcessList');
const modalSelectedCount = document.getElementById('modalSelectedCount');
const modalProcessTotal = document.getElementById('modalProcessTotal');
const btnModalSelectAll = document.getElementById('btnModalSelectAll');
const btnModalDeselectAll = document.getElementById('btnModalDeselectAll');

// Task Detail Drawer
const drawerOverlay = document.getElementById('drawerOverlay');
const taskDrawer = document.getElementById('taskDrawer');
const drawerCloseBtn = document.getElementById('drawerCloseBtn');
const copyJsonBtn = document.getElementById('copyJsonBtn');

// Helper: Categorize Process (Accent-Insensitive)
function getProcessCategory(processName) {
  const p = normalizeText(processName);
  if (p.includes('credito') || p.includes('financiamento') || p.includes('pronaf') || p.includes('pronamp') || p.includes('consignado') || p.includes('cheque especial') || p.includes('capital de giro') || p.includes('recebiveis') || p.includes('duplicatas') || p.includes('dividas')) {
    return 'credito';
  }
  if (p.includes('conta corrente') || p.includes('poupanca') || p.includes('cadastral') || p.includes('biometrica') || p.includes('ocr') || p.includes('qsa') || p.includes('renda') || p.includes('procuradores') || p.includes('pld-ft') || p.includes('pep') || p.includes('cooperado') || p.includes('quota-parte')) {
    return 'cadastro';
  }
  if (p.includes('cartao') || p.includes('sipag') || p.includes('chargeback') || p.includes('recompensas')) {
    return 'cartoes';
  }
  if (p.includes('pix') || p.includes('med') || p.includes('qrcode')) {
    return 'pix';
  }
  if (p.includes('boleto') || p.includes('titulo') || p.includes('protesto') || p.includes('cnab') || p.includes('remessa')) {
    return 'cobranca';
  }
  if (p.includes('judicial') || p.includes('sisbajud') || p.includes('renajud') || p.includes('serasajud') || p.includes('bacen') || p.includes('coaf') || p.includes('procon') || p.includes('oficio')) {
    return 'juridico';
  }
  if (p.includes('bureau') || p.includes('serasa') || p.includes('scpc') || p.includes('scr') || p.includes('ieptb') || p.includes('cnd') || p.includes('sintegra') || p.includes('fgts') || p.includes('certidoes')) {
    return 'bureau';
  }
  if (p.includes('rdc') || p.includes('lca') || p.includes('previdencia') || p.includes('sobras') || p.includes('juros sobre capital')) {
    return 'investimentos';
  }
  if (p.includes('seguro') || p.includes('sinistro') || p.includes('consorcio') || p.includes('apolice') || p.includes('contemplacao')) {
    return 'seguros';
  }
  if (p.includes('cambio') || p.includes('internacional') || p.includes('ted') || p.includes('contabil') || p.includes('compe') || p.includes('atm') || p.includes('caixa')) {
    return 'tesouraria';
  }
  return 'outros';
}

// Gerenciamento de Tema (Claro / Escuro)
function applyTheme(isDark) {
  if (isDark) {
    document.body.classList.add('dark-theme');
    if (themeToggleIcon) themeToggleIcon.innerText = '☀️';
    if (themeToggleText) themeToggleText.innerText = 'Modo Claro';
  } else {
    document.body.classList.remove('dark-theme');
    if (themeToggleIcon) themeToggleIcon.innerText = '🌙';
    if (themeToggleText) themeToggleText.innerText = 'Modo Escuro';
  }
  localStorage.setItem('sicredi-theme', isDark ? 'dark' : 'light');
  setChartTheme(isDark);
}

function initTheme() {
  const saved = localStorage.getItem('sicredi-theme');
  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  const isDark = saved ? saved === 'dark' : prefersDark;
  applyTheme(isDark);
}

// Initialize Application
async function initApp() {
  initTheme();
  setupEventListeners();
  await checkHealth();
  await loadFilterOptions();
  await refreshDashboard();
}

// Health Check
async function checkHealth() {
  try {
    const res = await fetch('/api/health');
    const data = await res.json();
    if (data.status === 'connected') {
      dbStatusPill.innerHTML = `
        <span class="db-indicator"></span>
        <span>Conectado: <strong>${data.database}.${data.collection}</strong> (${data.total_docs.toLocaleString()} tarefas)</span>
      `;
    } else {
      dbStatusPill.innerHTML = `<span class="db-indicator" style="background:#ED5A6C"></span> <span>Erro de Conexão</span>`;
    }
  } catch (err) {
    dbStatusPill.innerHTML = `<span class="db-indicator" style="background:#ED5A6C"></span> <span>Offline</span>`;
  }
}

// Load Filter Options from MongoDB
async function loadFilterOptions() {
  try {
    const res = await fetch('/api/filters/options');
    const json = await res.json();
    const opts = json.data;
    state.availableOptions = opts;

    if (opts.status_nao_erro_keywords && opts.status_nao_erro_keywords.length) {
      state.nonErrorKeywords = opts.status_nao_erro_keywords;
    }

    const totalProcesses = opts.processos.length;
    totalProcessCountBadge.innerText = totalProcesses;
    modalProcessTotal.innerText = totalProcesses;
    pillTotalCount.innerText = opts.total_geral.toLocaleString();

    renderTopProcessShortcuts(opts.processos_info);
    populateSelect(statusSelect, opts.statuses, 'Status');
    populateSelect(acaoSelect, opts.acoes, 'Ação Fluid');
    populateSelect(nodoSelect, opts.nodos, 'Nodo');

    if (opts.data_min && opts.data_max) {
      dateStartInput.min = opts.data_min.split('T')[0];
      dateStartInput.max = opts.data_max.split('T')[0];
      dateEndInput.min = opts.data_min.split('T')[0];
      dateEndInput.max = opts.data_max.split('T')[0];
    }

    updateActiveProcessBadge();
  } catch (err) {
    console.error('Erro ao carregar opções de filtro:', err);
  }
}

// Render Top 5 Most Active Processes as 1-Click Shortcuts
function renderTopProcessShortcuts(processosInfo = []) {
  if (!Array.isArray(processosInfo) || processosInfo.length === 0) return;
  const sorted = [...processosInfo].sort((a, b) => b.count - a.count);
  const top5 = sorted.slice(0, 5);

  const existingPills = topProcessesRow.querySelectorAll('.process-pill:not(#pillAllProcesses)');
  existingPills.forEach(p => p.remove());

  top5.forEach(proc => {
    const pill = document.createElement('div');
    const isSelected = state.filters.processos.length === 1 && state.filters.processos[0] === proc.nome;
    pill.className = `process-pill ${isSelected ? 'active' : ''}`;
    pill.innerHTML = `
      <span>${proc.nome}</span>
      <span class="count">${proc.count}</span>
    `;
    pill.onclick = () => {
      if (isSelected) {
        state.filters.processos = [];
      } else {
        state.filters.processos = [proc.nome];
      }
      state.pagination.page = 1;
      updateActiveProcessBadge();
      refreshDashboard();
      renderTopProcessShortcuts(processosInfo);
    };
    topProcessesRow.appendChild(pill);
  });
}

function updateActiveProcessBadge() {
  const selectedCount = state.filters.processos.length;
  const totalCount = state.availableOptions.processos.length;

  if (selectedCount === 0 || selectedCount === totalCount) {
    activeProcessLabel.innerText = `Todos os ${totalCount} Processos`;
    activeProcessLabel.style.background = 'var(--sicredi-green-light)';
    activeProcessLabel.style.color = 'var(--sicredi-green-dark)';
    pillAllProcesses.classList.add('active');
  } else {
    activeProcessLabel.innerText = `${selectedCount} de ${totalCount} selecionados`;
    activeProcessLabel.style.background = '#E0F2FE';
    activeProcessLabel.style.color = '#0284C7';
    pillAllProcesses.classList.remove('active');
  }
}

function populateSelect(selectEl, items, placeholder) {
  selectEl.innerHTML = `<option value="TODOS">Todos (${placeholder})</option>`;
  items.forEach(item => {
    const opt = document.createElement('option');
    opt.value = item;
    opt.textContent = item;
    selectEl.appendChild(opt);
  });
}

// Build Filter Payload for API calls
function getActiveFiltersPayload() {
  const p = {};
  if (state.filters.processos.length > 0) {
    p.processos = state.filters.processos;
  }
  if (state.filters.status && state.filters.status !== 'TODOS') {
    p.status = [state.filters.status];
  }
  if (state.filters.acoes && state.filters.acoes !== 'TODOS') {
    p.acoes = [state.filters.acoes];
  }
  if (state.filters.nodos && state.filters.nodos !== 'TODOS') {
    p.nodos = [state.filters.nodos];
  }
  if (state.filters.data_inicio) {
    p.data_inicio = state.filters.data_inicio + "T00:00:00";
  }
  if (state.filters.data_fim) {
    p.data_fim = state.filters.data_fim + "T23:59:59";
  }
  if (state.filters.search) {
    p.search = state.filters.search;
  }
  return p;
}

// Refresh Entire Dashboard
async function refreshDashboard() {
  const filtersPayload = getActiveFiltersPayload();
  const startTime = performance.now();

  try {
    const [summaryRes, timeSeriesRes, distRes, tasksRes] = await Promise.all([
      fetch('/api/metrics/summary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(filtersPayload)
      }).then(r => r.json()),

      fetch('/api/metrics/timeseries', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filters: filtersPayload, granularity: state.granularity })
      }).then(r => r.json()),

      fetch('/api/metrics/distribution', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(filtersPayload)
      }).then(r => r.json()),

      fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          filters: filtersPayload,
          page: state.pagination.page,
          page_size: state.pagination.page_size,
          sort_by: state.pagination.sort_by,
          sort_desc: state.pagination.sort_desc
        })
      }).then(r => r.json())
    ]);

    const totalDuration = (performance.now() - startTime).toFixed(0);
    queryTimingEl.innerText = `Consultas concluídas em ${totalDuration}ms (MongoDB Agregações Indexadas)`;

    // Update KPI Cards
    renderKPIs(summaryRes.data);

    // Update Charts
    updateTimeSeriesChart(timeSeriesRes.data);
    updateHealthDoughnut(summaryRes.data.sucesso, summaryRes.data.repassado || 0, summaryRes.data.erro);
    updateActionsChart(distRes.data.by_acao || []);
    updateNodosChart(distRes.data.by_nodo || []);

    // Update Paginated Table
    renderTasksTable(tasksRes);

  } catch (err) {
    console.error('Erro ao atualizar dashboard:', err);
    queryTimingEl.innerText = `Erro ao carregar dados: ${err.message}`;
  }
}

function renderKPIs(kpis) {
  document.getElementById('kpiTotal').innerText = kpis.total.toLocaleString();
  document.getElementById('kpiSucesso').innerText = kpis.sucesso.toLocaleString();
  const repassadoEl = document.getElementById('kpiRepassado');
  if (repassadoEl) {
    repassadoEl.innerText = (kpis.repassado || 0).toLocaleString();
  }
  document.getElementById('kpiErro').innerText = kpis.erro.toLocaleString();
  document.getElementById('kpiTaxa').innerText = `${kpis.taxa_sucesso}%`;
  document.getElementById('kpiAvgExec').innerText = `${kpis.avg_execucoes}x`;

  const healthBadge = document.getElementById('kpiHealthBadge');
  const taxaEfetiva = kpis.taxa_sem_erro !== undefined ? kpis.taxa_sem_erro : kpis.taxa_sucesso;
  if (taxaEfetiva >= 85) {
    healthBadge.className = 'kpi-badge kpi-badge-success';
    healthBadge.innerText = 'Excelente';
  } else if (taxaEfetiva >= 70) {
    healthBadge.className = 'kpi-badge kpi-badge-warning';
    healthBadge.innerText = 'Atenção';
  } else {
    healthBadge.className = 'kpi-badge kpi-badge-danger';
    healthBadge.innerText = 'Crítico';
  }
}

function renderTasksTable(tasksData) {
  const tbody = document.getElementById('tasksTableBody');
  const countBadge = document.getElementById('tableCountBadge');
  state.pagination.total_items = tasksData.total_items;
  state.pagination.total_pages = tasksData.total_pages;

  countBadge.innerText = `${tasksData.total_items.toLocaleString()} tarefas encontradas`;

  if (!tasksData.items || tasksData.items.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="8" class="empty-state">
          <div>Nenhuma tarefa encontrada com os filtros selecionados.</div>
        </td>
      </tr>
    `;
    updatePaginationControls();
    return;
  }

  tbody.innerHTML = tasksData.items.map(task => {
    const statusInfo = getStatusBadgeInfo(task.status);
    const formattedDate = task.data_realizacao ? new Date(task.data_realizacao).toLocaleString('pt-BR') : '-';
    
    return `
      <tr style="cursor: pointer;" onclick="window.viewTaskDetails('${task.id}')">
        <td style="font-weight: 700; color: var(--sicredi-green-dark);">#${task.num_processo || '-'}</td>
        <td style="font-weight: 600; color: var(--text-main);">${task.nome_processo || '-'}</td>
        <td><span class="status-badge ${statusInfo.badgeClass}">${statusInfo.label}</span></td>
        <td><span class="tag-badge tag-action">${task.acao || '-'}</span></td>
        <td><span class="tag-badge">Nodo ${task.nodo || '-'}</span></td>
        <td style="color: var(--text-muted); font-size: 0.78rem;">${task.robo || '-'}</td>
        <td style="font-size: 0.78rem;">${formattedDate}</td>
        <td>
          <button class="btn btn-secondary btn-sm" onclick="event.stopPropagation(); window.viewTaskDetails('${task.id}')">
            Detalhes
          </button>
        </td>
      </tr>
    `;
  }).join('');

  updatePaginationControls();
}

function updatePaginationControls() {
  document.getElementById('pageInfo').innerText = `Página ${state.pagination.page} de ${state.pagination.total_pages || 1}`;
  document.getElementById('btnPrevPage').disabled = state.pagination.page <= 1;
  document.getElementById('btnNextPage').disabled = state.pagination.page >= state.pagination.total_pages;
}

// -------------------------------------------------------------
// MODAL DE GERENCIAMENTO DE 100+ PROCESSOS
// -------------------------------------------------------------
function openProcessModal() {
  state.modal.tempSelectedProcessos = [...state.filters.processos];
  state.modal.searchTerm = '';
  modalProcessSearch.value = '';
  renderModalProcessList();
  processModalOverlay.classList.add('open');
}

function closeProcessModal() {
  processModalOverlay.classList.remove('open');
}

function renderModalProcessList() {
  const term = normalizeText(state.modal.searchTerm);
  const category = state.modal.selectedCategory;
  const list = state.availableOptions.processos_info || [];

  const filtered = list.filter(item => {
    const normName = normalizeText(item.nome);
    const matchesSearch = term === '' || normName.includes(term);
    const itemCat = getProcessCategory(item.nome);
    const matchesCat = category === 'todas' || itemCat === category;
    return matchesSearch && matchesCat;
  });

  modalProcessList.innerHTML = '';

  if (filtered.length === 0) {
    modalProcessList.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 2rem; color: var(--text-muted);">
        Nenhum processo encontrado para a busca ou categoria selecionada.
      </div>
    `;
    updateModalSelectionCounter();
    return;
  }

  filtered.forEach(item => {
    const isChecked = state.modal.tempSelectedProcessos.includes(item.nome);
    const card = document.createElement('div');
    card.className = `process-checkbox-card ${isChecked ? 'selected' : ''}`;
    card.innerHTML = `
      <input type="checkbox" ${isChecked ? 'checked' : ''}>
      <span class="process-checkbox-name">${item.nome}</span>
      <span class="process-checkbox-badge">${item.count}</span>
    `;

    const toggleSelection = () => {
      const idx = state.modal.tempSelectedProcessos.indexOf(item.nome);
      if (idx > -1) {
        state.modal.tempSelectedProcessos.splice(idx, 1);
        card.classList.remove('selected');
        card.querySelector('input').checked = false;
      } else {
        state.modal.tempSelectedProcessos.push(item.nome);
        card.classList.add('selected');
        card.querySelector('input').checked = true;
      }
      updateModalSelectionCounter();
    };

    card.onclick = (e) => {
      if (e.target.tagName !== 'INPUT') {
        toggleSelection();
      }
    };
    card.querySelector('input').onchange = () => {
      toggleSelection();
    };

    modalProcessList.appendChild(card);
  });

  updateModalSelectionCounter();
}

function updateModalSelectionCounter() {
  const count = state.modal.tempSelectedProcessos.length;
  modalSelectedCount.innerText = count === 0 ? 'Todos os' : count;
}

// Task Details Slide-over Drawer
window.viewTaskDetails = async function(taskId) {
  try {
    const res = await fetch(`/api/tasks/${taskId}`);
    const json = await res.json();
    const task = json.data;

    document.getElementById('drawerProcessTitle').innerText = task.nome_processo || 'Detalhes da Tarefa';
    document.getElementById('drawerNumProcesso').innerText = `#${task.num_processo || '-'}`;
    
    const statusInfo = getStatusBadgeInfo(task.status);
    const statusBadge = document.getElementById('drawerStatusBadge');
    statusBadge.className = `status-badge ${statusInfo.badgeClass}`;
    statusBadge.innerText = task.status || '-';

    document.getElementById('drawerRobo').innerText = task.robo || '-';
    document.getElementById('drawerDataCad').innerText = task.data_cadastro ? new Date(task.data_cadastro).toLocaleString('pt-BR') : '-';
    document.getElementById('drawerDataReal').innerText = task.data_realizacao ? new Date(task.data_realizacao).toLocaleString('pt-BR') : '-';
    document.getElementById('drawerExecucoes').innerText = `${task.execucoes || 1} execução(ões)`;
    document.getElementById('drawerDetalhes').innerText = task.detalhes || '-';

    const fi = task.fluid_infos || {};
    document.getElementById('drawerFluidProcessoId').innerText = fi.processo_id || '-';
    document.getElementById('drawerFluidArvore').innerText = fi.arvore || '-';
    document.getElementById('drawerFluidNodo').innerText = fi.nodo || '-';
    document.getElementById('drawerFluidResp').innerText = fi.email_resp || '-';

    const fa = (task.infos_retorno || {}).fluid_api || {};
    const acao = fa.acao_nodo || '-';
    document.getElementById('drawerFluidAcao').innerText = acao;
    document.getElementById('drawerFluidTempo').innerText = `${fa.tempo_processo || 0}s`;
    document.getElementById('drawerFluidParecer').innerText = fa.parecer || '-';

    const jsonStr = JSON.stringify(task, null, 2);
    document.getElementById('drawerJsonContent').innerText = jsonStr;
    window.currentTaskJson = jsonStr;

    drawerOverlay.classList.add('open');
    taskDrawer.classList.add('open');
  } catch (err) {
    alert(`Erro ao carregar detalhes: ${err.message}`);
  }
};

function closeDrawer() {
  drawerOverlay.classList.remove('open');
  taskDrawer.classList.remove('open');
}

// Event Listeners Setup
function setupEventListeners() {
  // Theme Toggle (Dark / Light)
  if (themeToggleBtn) {
    themeToggleBtn.onclick = () => {
      const isDark = !document.body.classList.contains('dark-theme');
      applyTheme(isDark);
    };
  }

  // Modal Open/Close
  btnOpenProcessModal.onclick = openProcessModal;
  btnCloseProcessModal.onclick = closeProcessModal;
  btnModalCancel.onclick = closeProcessModal;
  processModalOverlay.onclick = (e) => {
    if (e.target === processModalOverlay) closeProcessModal();
  };

  // Modal Category Tabs
  document.querySelectorAll('.category-tab').forEach(tab => {
    tab.onclick = () => {
      document.querySelectorAll('.category-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      state.modal.selectedCategory = tab.getAttribute('data-cat');
      renderModalProcessList();
    };
  });

  // Modal Search
  modalProcessSearch.oninput = () => {
    state.modal.searchTerm = modalProcessSearch.value.trim();
    renderModalProcessList();
  };

  // Modal Select / Deselect All
  btnModalSelectAll.onclick = () => {
    const term = normalizeText(state.modal.searchTerm);
    const category = state.modal.selectedCategory;
    const list = state.availableOptions.processos_info || [];

    const visibleItems = list.filter(item => {
      const matchesSearch = term === '' || normalizeText(item.nome).includes(term);
      const matchesCat = category === 'todas' || getProcessCategory(item.nome) === category;
      return matchesSearch && matchesCat;
    });

    visibleItems.forEach(item => {
      if (!state.modal.tempSelectedProcessos.includes(item.nome)) {
        state.modal.tempSelectedProcessos.push(item.nome);
      }
    });
    renderModalProcessList();
  };

  btnModalDeselectAll.onclick = () => {
    state.modal.tempSelectedProcessos = [];
    renderModalProcessList();
  };

  // Modal Apply Selection
  btnModalApply.onclick = () => {
    state.filters.processos = [...state.modal.tempSelectedProcessos];
    state.pagination.page = 1;
    updateActiveProcessBadge();
    closeProcessModal();
    refreshDashboard();
    renderTopProcessShortcuts(state.availableOptions.processos_info);
  };

  // Shortcut "Todos"
  pillAllProcesses.onclick = () => {
    state.filters.processos = [];
    state.pagination.page = 1;
    updateActiveProcessBadge();
    refreshDashboard();
    renderTopProcessShortcuts(state.availableOptions.processos_info);
  };

  // Granularity toggles
  document.querySelectorAll('.granularity-btn').forEach(btn => {
    btn.onclick = () => {
      document.querySelectorAll('.granularity-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.granularity = btn.getAttribute('data-granularity');
      refreshDashboard();
    };
  });

  // Filter dropdowns
  statusSelect.onchange = () => {
    state.filters.status = statusSelect.value;
    state.pagination.page = 1;
    refreshDashboard();
  };

  acaoSelect.onchange = () => {
    state.filters.acoes = acaoSelect.value;
    state.pagination.page = 1;
    refreshDashboard();
  };

  nodoSelect.onchange = () => {
    state.filters.nodos = nodoSelect.value;
    state.pagination.page = 1;
    refreshDashboard();
  };

  // Date inputs
  dateStartInput.onchange = () => {
    state.filters.data_inicio = dateStartInput.value || null;
    state.pagination.page = 1;
    refreshDashboard();
  };

  dateEndInput.onchange = () => {
    state.filters.data_fim = dateEndInput.value || null;
    state.pagination.page = 1;
    refreshDashboard();
  };

  // Date Presets
  document.querySelectorAll('.date-preset-btn').forEach(btn => {
    btn.onclick = () => {
      const preset = btn.getAttribute('data-preset');
      const now = new Date();
      let start = null;

      if (preset === 'today') {
        start = now;
      } else if (preset === '7d') {
        start = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      } else if (preset === '30d') {
        start = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
      } else if (preset === '6m') {
        start = new Date(now.getTime() - 180 * 24 * 60 * 60 * 1000);
      } else if (preset === 'all') {
        start = null;
      }

      if (start) {
        state.filters.data_inicio = start.toISOString().split('T')[0];
        state.filters.data_fim = now.toISOString().split('T')[0];
        dateStartInput.value = state.filters.data_inicio;
        dateEndInput.value = state.filters.data_fim;
      } else {
        state.filters.data_inicio = null;
        state.filters.data_fim = null;
        dateStartInput.value = '';
        dateEndInput.value = '';
      }

      state.pagination.page = 1;
      refreshDashboard();
    };
  });

  // Search input debounce
  let searchTimeout = null;
  searchInput.oninput = () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      state.filters.search = searchInput.value.trim();
      state.pagination.page = 1;
      refreshDashboard();
    }, 350);
  };

  // Reset Filters Button
  document.getElementById('btnResetFilters').onclick = () => {
    state.filters = {
      processos: [],
      status: 'TODOS',
      acoes: 'TODOS',
      nodos: 'TODOS',
      data_inicio: null,
      data_fim: null,
      search: ''
    };
    statusSelect.value = 'TODOS';
    acaoSelect.value = 'TODOS';
    nodoSelect.value = 'TODOS';
    searchInput.value = '';
    dateStartInput.value = '';
    dateEndInput.value = '';
    state.pagination.page = 1;
    updateActiveProcessBadge();
    refreshDashboard();
    renderTopProcessShortcuts(state.availableOptions.processos_info);
  };

  // Refresh Button
  document.getElementById('btnRefreshAll').onclick = () => {
    refreshDashboard();
  };

  // Pagination navigation
  document.getElementById('btnPrevPage').onclick = () => {
    if (state.pagination.page > 1) {
      state.pagination.page--;
      refreshDashboard();
    }
  };

  document.getElementById('btnNextPage').onclick = () => {
    if (state.pagination.page < state.pagination.total_pages) {
      state.pagination.page++;
      refreshDashboard();
    }
  };

  document.getElementById('pageSizeSelect').onchange = (e) => {
    state.pagination.page_size = parseInt(e.target.value);
    state.pagination.page = 1;
    refreshDashboard();
  };

  // Drawer events
  drawerCloseBtn.onclick = closeDrawer;
  drawerOverlay.onclick = closeDrawer;

  copyJsonBtn.onclick = () => {
    if (window.currentTaskJson) {
      navigator.clipboard.writeText(window.currentTaskJson);
      copyJsonBtn.innerText = 'Copiado!';
      setTimeout(() => { copyJsonBtn.innerText = 'Copiar JSON'; }, 1500);
    }
  };

  // Export CSV
  document.getElementById('btnExportCsv').onclick = exportTasksCsv;
}

// Export Filtered Tasks to CSV
async function exportTasksCsv() {
  const filtersPayload = getActiveFiltersPayload();
  const res = await fetch('/api/tasks', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      filters: filtersPayload,
      page: 1,
      page_size: 1000,
      sort_by: state.pagination.sort_by,
      sort_desc: state.pagination.sort_desc
    })
  });
  const json = await res.json();
  const items = json.items || [];

  if (items.length === 0) {
    alert('Nenhum dado para exportar com os filtros atuais.');
    return;
  }

  const headers = ['Num Processo', 'Processo', 'Status', 'Acao', 'Nodo', 'Robo', 'Data Realizacao', 'Detalhes'];
  const rows = items.map(t => [
    t.num_processo || '',
    `"${(t.nome_processo || '').replace(/"/g, '""')}"`,
    t.status || '',
    t.acao || '',
    t.nodo || '',
    t.robo || '',
    t.data_realizacao || '',
    `"${(t.detalhes || '').replace(/"/g, '""')}"`
  ]);

  const csvContent = "data:text/csv;charset=utf-8," + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", `tarefas_sicredi_${new Date().toISOString().slice(0,10)}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// Start App
document.addEventListener('DOMContentLoaded', initApp);
