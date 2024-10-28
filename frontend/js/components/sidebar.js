import { state } from '../utils/state.js';
import { apiService } from '../services/api.service.js';
import { chatComponent } from './chat.js';
import { logger } from '../utils/logger.js';

class SidebarComponent {
    constructor() {
        this.elements = {
            sidebar: document.getElementById('sidebar'),
            chatHistory: document.getElementById('chat-history'),
            searchInput: document.getElementById('search-input'),
            newChatBtn: document.getElementById('new-chat-btn')
        };
        this.setupEventListeners();
    }

    setupEventListeners() {
        this.elements.newChatBtn?.addEventListener('click', this.handleNewChat.bind(this));
        this.elements.searchInput?.addEventListener('input', this.handleSearch.bind(this));
        state.on('titleUpdate', this.updateChatTitle.bind(this));
    }

    async loadChatHistory() {
        try {
            const history = await apiService.getChatHistory();
            this.displayChatHistory(history);
        } catch (error) {
            logger.error('Failed to load chat history:', error);
            state.emit('error', 'Failed to load chat history');
        }
    }

    displayChatHistory(history) {
        if (!this.elements.chatHistory) return;

        this.elements.chatHistory.innerHTML = '';
        history.forEach(chat => {
            const chatElement = document.createElement('div');
            chatElement.classList.add('chat-history-item');
            chatElement.dataset.chatId = chat.id;

            const contentWrapper = document.createElement('div');
            contentWrapper.classList.add('chat-item-content');

            const titleSpan = document.createElement('span');
            titleSpan.textContent = chat.title;
            contentWrapper.appendChild(titleSpan);

            const deleteBtn = document.createElement('button');
            deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
            deleteBtn.classList.add('delete-chat-btn');
            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.handleDeleteChat(chat.id);
            });
            contentWrapper.appendChild(deleteBtn);

            chatElement.appendChild(contentWrapper);
            chatElement.addEventListener('click', () => this.handleChatSelect(chat.id));

            this.elements.chatHistory.appendChild(chatElement);
        });
    }

    async handleNewChat() {
        try {
            logger.info('Creating new chat...');
            const response = await apiService.createChat();
            logger.info('New chat created:', response);
            
            // 刷新聊天历史
            await this.loadChatHistory();
            
            // 清空当前消息并设置新的聊天ID
            chatComponent.clearChat();
            state.set('currentChatId', response.id);
            
            // 高亮新的聊天
            this.updateActiveChat(response.id);
            
        } catch (error) {
            logger.error('Failed to create new chat:', error);
            state.emit('error', 'Failed to create new chat');
        }
    }

    async handleDeleteChat(chatId) {
        if (!confirm('确定要删除这个对话吗？')) return;

        try {
            await apiService.deleteChat(chatId);
            if (state.get('currentChatId') === chatId) {
                chatComponent.clearChat();
            }
            await this.loadChatHistory();
        } catch (error) {
            logger.error('Failed to delete chat:', error);
            state.emit('error', 'Failed to delete chat');
        }
    }

    handleChatSelect(chatId) {
        if (!chatId) {
            logger.error('Invalid chat ID');
            return;
        }
        
        logger.info(`Selecting chat: ${chatId}`);
        state.set('currentChatId', chatId);
        this.updateActiveChat(chatId);
        chatComponent.loadChat(chatId);
    }

    updateActiveChat(chatId) {
        if (!this.elements.chatHistory) return;
        
        this.elements.chatHistory.querySelectorAll('.chat-history-item').forEach(item => {
            item.classList.toggle('active', item.dataset.chatId === String(chatId));
        });
    }

    updateChatTitle({ chat_id, title }) {
        if (!this.elements.chatHistory) return;
        
        const chatElement = this.elements.chatHistory.querySelector(
            `.chat-history-item[data-chat-id="${chat_id}"] span`
        );
        if (chatElement) {
            chatElement.textContent = title;
        }
    }

    handleSearch(e) {
        const searchTerm = e.target.value.toLowerCase();
        const chatItems = this.elements.chatHistory?.querySelectorAll('.chat-history-item');
        
        chatItems?.forEach(item => {
            const title = item.querySelector('span')?.textContent.toLowerCase();
            if (title?.includes(searchTerm)) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    }
}

export const sidebarComponent = new SidebarComponent();
