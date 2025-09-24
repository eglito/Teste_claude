// js/dashboard.js - Lógica do dashboard (Versão Final com Paginação)

// Estado da aplicação
let currentPage = 1;
let totalPages = 1;

// Seletores de Elementos
const loadingContainer = document.getElementById('loadingContainer');
const tableContainer = document.getElementById('tableContainer');
const emptyState = document.getElementById('emptyState');
const errorState = document.getElementById('errorState');
const errorStateMessage = document.getElementById('errorStateMessage');
const totalRecordsEl = document.getElementById('totalRecords');
const totalDatesEl = document.getElementById('totalDates');
const userRoleDisplayEl = document.getElementById('userRoleDisplay');
const costVisibilityEl = document.getElementById('costVisibility');
const costVisibilityCardEl = document.getElementById('costVisibilityCard');
const dateFilterEl = document.getElementById('dateFilter');
const sortColumnEl = document.getElementById('sortColumn');
const sortOrderEl = document.getElementById('sortOrder');
const applyFiltersBtn = document.getElementById('applyFiltersBtn');
const clearFiltersBtn = document.getElementById('clearFiltersBtn');
const refreshDataBtn = document.getElementById('refreshDataBtn');
const tableHeader = document.getElementById('tableHeader');
const tableBody = document.getElementById('tableBody');
const recordsCountEl = document.getElementById('recordsCount');
const lastUpdatedEl = document.getElementById('lastUpdated');
const currentUserEl = document.getElementById('currentUser');
const userRoleEl = document.getElementById('userRole');
const paginationControls = document.getElementById('paginationControls');
const prevPageBtn = document.getElementById('prevPageBtn');
const nextPageBtn = document.getElementById('nextPageBtn');
const pageInfo = document.getElementById('pageInfo');

// Funções de UI
function setLoadingState(show) {
    loadingContainer.style.display = show ? 'flex' : 'none';
    if(show) {
        tableContainer.style.display = 'none';
        paginationControls.style.display = 'none';
    }
}

function renderTable(data, columns) {
    if (!data || data.length === 0) {
        emptyState.style.display = 'block';
        tableContainer.style.display = 'none';
        paginationControls.style.display = 'none';
        return;
    }
    emptyState.style.display = 'none';
    tableContainer.style.display = 'block';
    paginationControls.style.display = 'flex';

    tableHeader.innerHTML = `<tr>${columns.map(c => `<th>${c.replace(/_/g, ' ')}</th>`).join('')}</tr>`;
    tableBody.innerHTML = data.map(record => `
        <tr>
            ${columns.map(col => `<td>${formatCell(record[col], col)}</td>`).join('')}
        </tr>
    `).join('');
}

function formatCell(value, colName) {
    if (typeof value !== 'number') return value;
    if (colName === 'cost_micros') {
        return (value / 1000000).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    }
    return value.toLocaleString('pt-BR');
}

function renderPagination(pagination) {
    currentPage = pagination.current_page;
    totalPages = pagination.total_pages;
    pageInfo.textContent = `Página ${currentPage} de ${totalPages}`;
    prevPageBtn.disabled = currentPage === 1;
    nextPageBtn.disabled = currentPage === totalPages;
}

// Lógica de Dados
async function applyFilters(resetPage = false) {
    if (resetPage) currentPage = 1;
    setLoadingState(true);
    try {
        const metrics = await getMetricsData(
            dateFilterEl.value || null,
            sortColumnEl.value || null,
            sortOrderEl.value,
            currentPage
        );
        renderTable(metrics.data, metrics.columns_visible);
        renderPagination(metrics.pagination);
        recordsCountEl.textContent = `${metrics.total_records.toLocaleString('pt-BR')} registros`;
        lastUpdatedEl.textContent = `Última atualização: ${new Date().toLocaleString('pt-BR')}`;
    } catch (e) {
        errorState.style.display = 'block';
        errorStateMessage.textContent = e.message;
    } finally {
        setLoadingState(false);
    }
}

async function loadInitialData() {
    try {
        const [summary, user] = await Promise.all([getMetricsSummary(), apiRequest('/users/me')]);

        // Preenche info do usuário
        currentUserEl.textContent = `Olá, ${user.username}`;
        userRoleEl.textContent = user.role;

        // Preenche resumo
        totalRecordsEl.textContent = summary.total_records.toLocaleString('pt-BR');
        totalDatesEl.textContent = summary.available_dates.length;
        userRoleDisplayEl.textContent = summary.user_permissions.role;
        costVisibilityEl.textContent = summary.user_permissions.can_see_cost_micros ? 'Visível' : 'Oculto';
        costVisibilityEl.style.color = summary.user_permissions.can_see_cost_micros ? 'var(--success-color)' : 'var(--error-color)';

        // Preenche filtros
        dateFilterEl.innerHTML = `<option value="">Todas as Datas</option>${summary.available_dates.map(d => `<option value="${d}">${d}</option>`).join('')}`;
        sortColumnEl.innerHTML = `<option value="">Sem Ordenação</option>${summary.sortable_columns.map(c => `<option value="${c}">${c.replace(/_/g, ' ')}</option>`).join('')}`;

        await applyFilters(true);
    } catch (e) {
        setErrorState(e.message);
    }
}

// Event Listeners
applyFiltersBtn.addEventListener('click', () => applyFilters(true));
clearFiltersBtn.addEventListener('click', () => {
    dateFilterEl.value = '';
    sortColumnEl.value = '';
    sortOrderEl.value = 'asc';
    applyFilters(true);
});
refreshDataBtn.addEventListener('click', loadInitialData);
prevPageBtn.addEventListener('click', () => {
    if (currentPage > 1) {
        currentPage--;
        applyFilters();
    }
});
nextPageBtn.addEventListener('click', () => {
    if (currentPage < totalPages) {
        currentPage++;
        applyFilters();
    }
});