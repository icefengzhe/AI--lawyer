import { api } from '../utils/request.js';

const BASE_URL = '/api/v1/auth';

export const auth = {
    login: async (username, password) => {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        
        const response = await fetch(`${BASE_URL}/login`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '登录失败');
        }
        
        return response.json();
    },
    
    register: async (userData) => {
        const response = await fetch(`${BASE_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '注册失败');
        }
        
        return response.json();
    },
    
    getCurrentUser: async () => {
        const token = localStorage.getItem('token');
        if (!token) {
            throw new Error('未登录');
        }
        
        const response = await fetch(`${BASE_URL}/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error('获取用户信息失败');
        }
        
        return response.json();
    },
    
    logout: () => {
        localStorage.removeItem('token');
        window.location.href = '/login.html';
    }
}; 