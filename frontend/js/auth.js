// js/auth.js - Lógica de autenticação e gestão de estado do usuário

const loginSection = document.getElementById('loginSection');
const dashboardSection = document.getElementById('dashboardSection');
const loginForm = document.getElementById('loginForm');
const loginMessageText = document.getElementById('loginMessageText');
const loginMessage = document.getElementById('loginMessage');

function setLoginState(loggedIn) {
    if (loggedIn) {
        loginSection.style.display = 'none';
        dashboardSection.style.display = 'block';
    } else {
        loginSection.style.display = 'flex';
        dashboardSection.style.display = 'none';
    }
}

async function handleLoginSubmit(event) {
    event.preventDefault();
    const username = loginForm.username.value;
    const password = loginForm.password.value;
    const loginBtn = document.getElementById('loginBtn');
    loginBtn.textContent = 'Carregando...';
    loginBtn.disabled = true;
    loginMessage.style.display = 'none';

    try {
        const tokenData = await login(username, password);
        localStorage.setItem('access_token', tokenData.access_token);
        location.reload();
    } catch (error) {
        loginMessage.style.display = 'block';
        loginMessage.className = 'message-container error';
        loginMessageText.textContent = error.message || 'Falha no login.';
        loginBtn.textContent = 'Entrar';
        loginBtn.disabled = false;
    }
}

function handleLogout() {
    localStorage.removeItem('access_token');
    location.reload();
}

// Inicialização da lógica de autenticação
document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('access_token');
    if (token) {
        setLoginState(true);
        // CORREÇÃO: Chamando a função correta do dashboard.js
        loadInitialData();
    } else {
        setLoginState(false);
    }
});

// Adiciona os event listeners
loginForm.addEventListener('submit', handleLoginSubmit);
document.getElementById('logoutBtn').addEventListener('click', handleLogout);