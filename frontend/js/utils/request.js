const BASE_URL = '/api/v1';

async function request(url, options = {}) {
    const token = localStorage.getItem('token');
    
    const defaultOptions = {
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': token ? `Bearer ${token}` : '',
        },
    };

    // 合并headers
    const mergedOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...(options.headers || {}),
        },
    };

    const response = await fetch(url, mergedOptions);
    
    if (!response.ok) {
        if (response.status === 401) {
            // 可以在这里处理token过期的情况
            localStorage.removeItem('token');
            window.location.href = '/login.html';
            throw new Error('Unauthorized');
        }
        throw new Error(response.statusText);
    }
    
    // 如果响应是空的，返回null
    if (response.status === 204) {
        return null;
    }
    
    return response.json();
}

export { request }; 