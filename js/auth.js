// js/auth.js - Lógica de autenticação e gestão de estado do usuário

const loginSection = document.getElementById('loginSection');
const dashboardSection = document.getElementById('dashboardSection');
const loginForm = document.getElementById('loginForm');
const loginMessageText = document.getElementById('loginMessageText');
const loginMessage = document.getElementById('loginMessage');

/**
 * Define o estado de login, exibindo a seção correta e atualizando o status de autenticação.
 * @param {boolean} loggedIn Se o usuário está logado.
 */
function setLoginState(loggedIn) {
    if (loggedIn) {
        loginSection.style.display = 'none';
        dashboardSection.style.display = 'block'; // Usar 'block' em vez de 'flex' para o container principal
        // A chamada para carregar os dados do dashboard será feita no DOMContentLoaded ou após o login
    } else {
        loginSection.style.display = 'flex';
        dashboardSection.style.display = 'none';
    }
}


/**
 * Gerencia a submissão do formulário de login.
 * @param {Event} event O evento de submissão do formulário.
 */
async function handleLoginSubmit(event) {
    event.preventDefault();
    const username = loginForm.username.value;
    const password = loginForm.password.value;
    const loginBtn = document.getElementById('loginBtn');
    const originalText = loginBtn.textContent;

    loginBtn.textContent = 'Carregando...';
    loginBtn.disabled = true;
    loginMessage.style.display = 'none';

    try {
        const tokenData = await login(username, password);
        localStorage.setItem('access_token', tokenData.access_token);

        // CORREÇÃO: Força o recarregamento da página.
        // Ao recarregar, o script verificará o token e mostrará o dashboard.
        location.reload();

    } catch (error) {
        console.error('Login failed:', error);
        loginMessage.style.display = 'block';
        loginMessage.className = 'message-container error';
        loginMessageText.textContent = error.message || 'Falha no login. Verifique suas credenciais.';

        loginBtn.textContent = originalText;
        loginBtn.disabled = false;
    }
}

/**
 * Gerencia a ação de logout.
 */
function handleLogout() {
    localStorage.removeItem('access_token');
    location.reload(); // A forma mais simples de voltar para a tela de login
}

// Inicialização da lógica de autenticação
document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('access_token');
    if (token) {
        setLoginState(true);
        loadDashboardData(); // Carrega os dados se o usuário já estiver logado
    } else {
        setLoginState(false);
    }
});

// Adiciona os event listeners
loginForm.addEventListener('submit', handleLoginSubmit);
document.getElementById('logoutBtn').addEventListener('click', handleLogout);