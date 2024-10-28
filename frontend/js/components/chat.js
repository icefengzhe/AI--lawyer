import { state } from '../utils/state.js';
import { apiService } from '../services/api.service.js';
import { wsService } from '../services/ws.service.js';
import { logger } from '../utils/logger.js';

class ChatComponent {
    constructor() {
        this.elements = {
            messagesContainer: document.getElementById('messages'),
            chatForm: document.getElementById('chat-form'),
            userInput: document.getElementById('user-input')
        };
        this.setupEventListeners();
        this.ensureWebSocketConnection();
    }

    setupEventListeners() {
        this.elements.chatForm?.addEventListener('submit', this.handleSubmit.bind(this));
        state.on('message', this.displayMessage.bind(this));
    }

    async ensureWebSocketConnection() {
        try {
            if (!wsService.isConnected) {
                logger.info('Establishing WebSocket connection...');
                await wsService.connect();
                logger.info('WebSocket connection established');
            }
        } catch (error) {
            logger.error('Failed to establish WebSocket connection:', error);
            state.emit('error', 'Failed to connect to chat service');
        }
    }

    async handleSubmit(e) {
        e.preventDefault();
        const message = this.elements.userInput?.value.trim();
        if (!message) return;

        try {
            await this.ensureWebSocketConnection();
            
            if (!wsService.isConnected) {
                throw new Error('WebSocket is not connected');
            }

            let currentChatId = state.get('currentChatId');
            
            // 如果没有当前聊天，创建一个新的
            if (!currentChatId) {
                logger.info('Creating new chat...');
                const response = await apiService.createChat();
                currentChatId = response.id;  // 使用返回的chat.id
                state.set('currentChatId', currentChatId);
                logger.info(`New chat created with ID: ${currentChatId}`);
            }

            logger.info(`Sending message to chat ${currentChatId}: ${message}`);
            wsService.sendMessage(currentChatId, message);
            this.displayMessage({ content: message, role: 'user' });
            this.elements.userInput.value = '';
        } catch (error) {
            logger.error('Failed to send message:', error);
            state.emit('error', 'Failed to send message');
        }
    }

    displayMessage({ content, role }) {
        if (!this.elements.messagesContainer) return;

        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${role}-message`);
        messageElement.textContent = content;
        this.elements.messagesContainer.appendChild(messageElement);
        this.scrollToBottom();
    }

    scrollToBottom() {
        if (this.elements.messagesContainer) {
            this.elements.messagesContainer.scrollTop = this.elements.messagesContainer.scrollHeight;
        }
    }

    async loadChat(chatId) {
        try {
            state.set('loading', true);
            const chat = await apiService.getChat(chatId);
            this.elements.messagesContainer.innerHTML = '';
            chat.messages.forEach(msg => this.displayMessage(msg));
            state.set('currentChatId', chatId);
            logger.info(`Loaded chat ${chatId}`);
        } catch (error) {
            logger.error('Failed to load chat:', error);
            state.emit('error', 'Failed to load chat');
        } finally {
            state.set('loading', false);
        }
    }

    clearChat() {
        if (this.elements.messagesContainer) {
            this.elements.messagesContainer.innerHTML = '';
        }
        state.set('currentChatId', null);
        logger.info('Chat cleared');
    }
}

export const chatComponent = new ChatComponent();
