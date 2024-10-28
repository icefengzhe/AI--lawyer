class Auth {
    constructor() {
        this.API_BASE_URL = 'http://localhost:8000/api';
        this.loginForm = document.getElementById('login-form');
        this.registerForm = document.getElementById('register-form');
        this.errorMessage = document.getElementById('error-message');
        this.tabButtons = document.querySelectorAll('.tab-btn');
        
        this.setupEventListeners();
        this.checkLoginStatus();
    }

    checkLoginStatus() {
        const token = localStorage.getItem('token');
        if (token) {
            window.location.href = '/';
        }
    }

    setupEventListeners() {
        this.loginForm.addEventListener('submit', this.handleLogin.bind(this));
        this.registerForm.addEventListener('submit', this.handleRegister.bind(this));
        
        // 标签切换
        this.tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                this.switchTab(button.dataset.tab);
                this.errorMessage.textContent = '';
            });
        });
    }

    switchTab(tabName) {
        // 更新标签按钮状态
        this.tabButtons.forEach(button => {
            button.classList.toggle('active', button.dataset.tab === tabName);
        });

        // 更新表单显示
        document.querySelectorAll('.form-panel').forEach(panel => {
            panel.classList.toggle('active', panel.id === `${tabName}-form`);
        });
    }

    async handleLogin(e) {
        e.preventDefault();
        
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;

        try {
            const response = await fetch(`${this.API_BASE_URL}/auth/token`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
            });

            const data = await response.json();

            if (response.ok) {
                localStorage.setItem('token', data.access_token);
                window.location.href = '/';
            } else {
                this.showError(data.detail || '登录失败');
            }
        } catch (error) {
            console.error('Login error:', error);
            this.showError('登录失败，请稍后重试');
        }
    }

    async handleRegister(e) {
        e.preventDefault();
        
        const username = document.getElementById('register-username').value;
        const password = document.getElementById('register-password').value;
        const confirmPassword = document.getElementById('register-confirm-password').value;

        if (password !== confirmPassword) {
            this.showError('两次输入的密码不一致');
            return;
        }

        try {
            const response = await fetch(`${this.API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username,
                    password
                })
            });

            const data = await response.json();

            if (response.ok) {
                // 注册成功后自动登录
                this.showError('注册成功，正在登录...', 'success');
                setTimeout(() => this.autoLogin(username, password), 1000);
            } else {
                this.showError(data.detail || '注册失败');
            }
        } catch (error) {
            console.error('Register error:', error);
            this.showError('注册失败，请稍后重试');
        }
    }

    async autoLogin(username, password) {
        try {
            const response = await fetch(`${this.API_BASE_URL}/auth/token`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
            });

            const data = await response.json();

            if (response.ok) {
                localStorage.setItem('token', data.access_token);
                window.location.href = '/';
            } else {
                this.showError('自动登录失败，请手动登录');
                this.switchTab('login');
            }
        } catch (error) {
            console.error('Auto login error:', error);
            this.showError('自动登录失败，请手动登录');
            this.switchTab('login');
        }
    }

    showError(message, type = 'error') {
        this.errorMessage.textContent = message;
        this.errorMessage.className = `error-message ${type}`;
    }
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    new Auth();
});
