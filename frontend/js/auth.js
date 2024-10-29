// 检查是否已登录，如果已登录则跳转到主页
async function checkAuth() {
    const token = localStorage.getItem('token');
    const isLoginPage = window.location.pathname.endsWith('login.html');
    const isRegisterPage = window.location.pathname.endsWith('register.html');

    if (!token) {
        if (!isLoginPage && !isRegisterPage) {
            window.location.href = '/login.html';
        }
        return;
    }

    try {
        const response = await fetch('/api/v1/auth/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('认证失败');
        }

        if (isLoginPage || isRegisterPage) {
            window.location.href = '/';
        }
    } catch (error) {
        console.error('认证检查失败:', error);
        localStorage.removeItem('token');
        if (!isLoginPage && !isRegisterPage) {
            window.location.href = '/login.html';
        }
    }
}

// 登录表单处理
document.getElementById('login-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // 重置错误信息
    const errorElement = document.getElementById('login-error');
    errorElement.style.display = 'none';
    errorElement.textContent = '';
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    try {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        
        const response = await fetch('/api/v1/auth/login', {
            method: 'POST',
            body: formData,
            headers: {
                'Accept': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || '登录失败');
        }
        
        // 保存token并跳转
        localStorage.setItem('token', data.access_token);
        window.location.href = '/';
        
    } catch (error) {
        errorElement.textContent = error.message;
        errorElement.style.display = 'block';
    }
});

// 页面加载时检查登录状态
document.addEventListener('DOMContentLoaded', checkAuth); 