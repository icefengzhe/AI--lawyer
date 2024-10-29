import { ChatUI } from './chat.js';

// 初始化聊天界面
document.addEventListener('DOMContentLoaded', async () => {
    // 检查登录状态
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/login.html';
        return;
    }

    // 验证token
    try {
        const response = await fetch('/api/v1/auth/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('认证失败');
        }
    } catch (error) {
        console.error('认证检查失败:', error);
        localStorage.removeItem('token');
        window.location.href = '/login.html';
        return;
    }

    // 初始化聊天界面
    const chatContainer = document.querySelector('.chat-container');
    if (chatContainer) {
        const chatUI = new ChatUI(chatContainer);
        
        // 绑定退出登录按钮
        document.getElementById('logout')?.addEventListener('click', () => {
            localStorage.removeItem('token');
            window.location.href = '/login.html';
        });
    }
});