document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // 重置错误信息
    document.querySelectorAll('.error-message').forEach(el => {
        el.style.display = 'none';
        el.textContent = '';
    });
    
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    
    // 表单验证
    let hasError = false;
    
    if (!username) {
        document.getElementById('username-error').textContent = '请输入用户名';
        document.getElementById('username-error').style.display = 'block';
        hasError = true;
    }
    
    if (password.length < 6) {
        document.getElementById('password-error').textContent = '密码长度至少6位';
        document.getElementById('password-error').style.display = 'block';
        hasError = true;
    }
    
    if (password !== confirmPassword) {
        document.getElementById('confirm-password-error').textContent = '两次输入的密码不一致';
        document.getElementById('confirm-password-error').style.display = 'block';
        hasError = true;
    }
    
    if (hasError) return;
    
    try {
        const response = await fetch('/api/v1/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username,
                password
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || '注册失败');
        }
        
        // 保存token并跳转
        localStorage.setItem('token', data.access_token);
        window.location.href = '/';
        
    } catch (error) {
        document.getElementById('register-error').textContent = error.message;
        document.getElementById('register-error').style.display = 'block';
    }
}); 