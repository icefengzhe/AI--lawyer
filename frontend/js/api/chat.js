import { api } from '../utils/request.js';

export const chat = {
    createChat: async () => {
        return api.post('/chat/create');
    },
    
    getChat: async (chatId) => {
        return api.get(`/chat/${chatId}`);
    },
    
    getHistory: async () => {
        return api.get('/chat/history');
    },
    
    getMessages: async (chatId) => {
        return api.get(`/chat/${chatId}/messages`);
    },
    
    sendMessage: async (chatId, content) => {
        return api.post(`/chat/${chatId}/messages`, {
            content
        });
    },
    
    deleteChat: async (chatId) => {
        return api.delete(`/chat/${chatId}`);
    }
}; 