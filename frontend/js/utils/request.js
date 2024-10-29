const BASE_URL = '/api/v1';

export const api = {
    get: async (url) => {
        const token = localStorage.getItem('token');
        const response = await fetch(`${BASE_URL}${url}`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '请求失败');
        }
        
        return response.json();
    },
    
    post: async (url, data) => {
        const token = localStorage.getItem('token');
        const response = await fetch(`${BASE_URL}${url}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '请求失败');
        }
        
        return response.json();
    },
    
    delete: async (url) => {
        const token = localStorage.getItem('token');
        const response = await fetch(`${BASE_URL}${url}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '请求失败');
        }
        
        return response.json();
    }
}; 