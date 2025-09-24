// js/api.js - Configurações e chamadas à API

const API_BASE_URL = 'http://127.0.0.1:8000';

async function apiRequest(endpoint, method = 'GET', body = null) {
    const token = localStorage.getItem('access_token');
    if (!token && endpoint !== '/token') {
        window.location.hash = '#login';
        throw new Error('Token de acesso não encontrado.');
    }
    const headers = { 'Content-Type': 'application/json' };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    const config = { method, headers };
    if (body) {
        config.body = JSON.stringify(body);
    }
    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erro na requisição da API.');
    }
    return response.json();
}

async function getMetricsData(dateFilter = null, sortBy = null, sortOrder = 'asc', page = 1, pageSize = 100) {
    const params = new URLSearchParams({ sort_order: sortOrder, page: page, page_size: pageSize });
    if (dateFilter) params.append('date_filter', dateFilter);
    if (sortBy) params.append('sort_by', sortBy);
    return apiRequest(`/metrics?${params.toString()}`);
}

async function getMetricsSummary() {
    return apiRequest('/metrics/summary');
}

async function login(username, password) {
    const formData = new URLSearchParams({ username, password });
    const response = await fetch(`${API_BASE_URL}/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData,
    });
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erro ao fazer login.');
    }
    return response.json();
}