import { request } from '../utils/request.js';

// 聊天相关的API请求
export const chat = {
    // 创建新对话
    createChat: async () => {
        const response = await fetch('/api/v1/chat/create', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '创建对话失败');
        }
        
        return response.json();
    },
    
    // 获取对话历史
    getHistory: async () => {
        const response = await fetch('/api/v1/chat/history', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '获取历史记录失败');
        }
        
        return response.json();
    },
    
    // 获取单个对话
    getChat: async (chatId) => {
        const response = await fetch(`/api/v1/chat/${chatId}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '获取对话失败');
        }
        
        return response.json();
    },
    
    // 获取对话消息
    getMessages: async (chatId) => {
        const response = await fetch(`/api/v1/chat/${chatId}/messages`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '获取消息失败');
        }
        
        return response.json();
    },
    
    // 删除对话
    deleteChat: async (chatId) => {
        const response = await fetch(`/api/v1/chat/${chatId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '删除对话失败');
        }
        
        return response.json();
    },
    
    // 上传文件
    async uploadFile(file) {
        const token = localStorage.getItem('token');
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/api/v1/files/upload', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
            },
            credentials: 'include',
            body: formData
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                localStorage.removeItem('token');
                window.location.href = '/login.html';
                throw new Error('Unauthorized');
            }
            throw new Error(response.statusText);
        }
        
        return response.json();
    },
    
    // 获取文件列表
    getFiles: async () => {
        return request('/api/v1/files/list');
    },
    
    // 删除文件
    async deleteFile(fileId) {
        return request(`/api/v1/files/${fileId}`, {
            method: 'DELETE'
        });
    }
}; 