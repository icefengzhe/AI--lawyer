import { ChatUI } from './chat.js';

document.addEventListener('DOMContentLoaded', () => {
    const container = document.querySelector('.chat-container');
    if (!container) {
        console.error('Chat container not found');
        return;
    }
    
    try {
        const chatUI = new ChatUI(container);
    } catch (error) {
        console.error('Failed to initialize ChatUI:', error);
    }
});