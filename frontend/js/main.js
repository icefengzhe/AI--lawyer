import { ChatUI } from './chat.js';

// 检查登录状态
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

// 初始化聊天界面
document.addEventListener('DOMContentLoaded', async () => {
    // 先检查认证状态
    await checkAuth();

    const chatContainer = document.querySelector('.chat-container');
    if (chatContainer) {
        const chatUI = new ChatUI(chatContainer);
        
        // 绑定退出登录按钮
        document.getElementById('logout')?.addEventListener('click', () => {
            localStorage.removeItem('token');
            window.location.href = '/login.html';
        });

        // 添加全局错误处理
        window.addEventListener('unhandledrejection', (event) => {
            console.error('未处理的Promise错误:', event.reason);
            if (event.reason.message?.includes('认证失败') || 
                event.reason.message?.includes('401') ||
                event.reason.message?.includes('403')) {
                localStorage.removeItem('token');
                window.location.href = '/login.html';
            }
        });

        // 添加请求拦截器
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            try {
                const response = await originalFetch(...args);
                if (response.status === 401 || response.status === 403) {
                    localStorage.removeItem('token');
                    window.location.href = '/login.html';
                    throw new Error('认证失败');
                }
                return response;
            } catch (error) {
                if (error.message.includes('Failed to fetch')) {
                    console.error('网络请求失败:', error);
                    // 可以添加重试逻辑或显示错误提示
                }
                throw error;
            }
        };
    }
});

// 定期检查认证状态
setInterval(checkAuth, 60000); // 每分钟检查一次