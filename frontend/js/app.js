import { state } from './utils/state.js';
import { logger } from './utils/logger.js';
import { apiService } from './services/api.service.js';
import { wsService } from './services/ws.service.js';
import { chatComponent } from './components/chat.js';
import { sidebarComponent } from './components/sidebar.js';
import { uiComponent } from './components/ui.js';
import { API_BASE_URL, fetchWithAuth } from './utils/api.js';

class App {
    constructor() {
        this.API_BASE_URL = 'http://localhost:8000/api';
        this.socket = null;
        this.state = {
            currentChatId: null,
            currentAIMessage: null,
            lastMessageId: null,
            isCreatingChat: false,
            chats: [],
            messageCache: new Map(),
            isSending: false  // 添加发送状态标记
        };

        this.elements = {
            chatForm: document.getElementById('chat-form'),
            userInput: document.getElementById('user-input'),
            messagesContainer: document.getElementById('messages'),
            chatHistory: document.getElementById('chat-history'),
            typingIndicator: document.getElementById('typing-indicator'),
            newChatBtn: document.getElementById('new-chat-btn'),
            currentChatTitle: document.getElementById('current-chat-title'),
            sendButton: document.getElementById('send-button')
        };

        this.lastSentMessage = null;

        // 检查登录状态
        if (!this.checkAuth()) {
            window.location.href = '/login.html';
            return;
        }

        this.setupEventListeners();
        this.setupWebSocket();
        this.loadChatHistory();
    }

    checkAuth() {
        const token = localStorage.getItem('token');
        if (!token) {
            return false;
        }
        return true;
    }

    // 添加登出方法
    logout() {
        localStorage.removeItem('token');
        window.location.href = '/login.html';
    }

    setupEventListeners() {
        // 新对话按钮事件
        this.elements.newChatBtn.addEventListener('click', async () => {
            if (!this.state.isCreatingChat) {
                await this.handleNewChat();
            }
        });

        this.elements.chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleMessageSend();
        });
        
        this.elements.userInput.addEventListener('input', this.handleInput.bind(this));
        
        // 处理回车键
        this.elements.userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleMessageSend();
            }
        });

        // 处理发送按钮点击
        this.elements.sendButton.addEventListener('click', (e) => {
            e.preventDefault();
            this.handleMessageSend();
        });

        // 添加登出按钮事件监听
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.logout());
        }
    }

    setupWebSocket() {
        const token = localStorage.getItem('token');
        if (!token) {
            console.error('No token found');
            return;
        }

        this.socket = new WebSocket(`ws://localhost:8000/api/chat/ws?token=${token}`);
        
        this.socket.onopen = () => {
            console.log('WebSocket connected');
        };

        this.socket.onmessage = this.handleWebSocketMessage.bind(this);
        
        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        this.socket.onclose = () => {
            console.log('WebSocket disconnected');
            // 可以添加重逻辑
        };
    }

    async handleNewChat() {
        try {
            // 设置创建状态
            this.state.isCreatingChat = true;
            this.elements.newChatBtn.disabled = true;

            // 创建新对话
            const response = await fetch(`${this.API_BASE_URL}/chat/chats`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) {
                throw new Error('Failed to create new chat');
            }

            const newChat = await response.json();

            // 更新状态
            this.state.currentChatId = newChat.id;
            
            // 清空消息区域
            this.elements.messagesContainer.innerHTML = '';
            
            // 更新标题
            this.elements.currentChatTitle.textContent = '新对话';

            // 创建新的聊天项
            const chatElement = this.createChatElement(newChat);
            
            // 将新的聊天项添加到列表开头
            if (this.elements.chatHistory.firstChild) {
                this.elements.chatHistory.insertBefore(chatElement, this.elements.chatHistory.firstChild);
            } else {
                this.elements.chatHistory.appendChild(chatElement);
            }

            // 更新状态数组
            this.state.chats.unshift(newChat);
            
            // 更新选中状态
            this.updateActiveChatItem(newChat.id);
            
            // 聚焦输入框
            this.elements.userInput.focus();

        } catch (error) {
            console.error('Failed to create new chat:', error);
            this.showError('创建新对话失败');
        } finally {
            // 重置创建状态
            this.state.isCreatingChat = false;
            this.elements.newChatBtn.disabled = false;
        }
    }

    createChatElement(chat) {
        const chatElement = document.createElement('div');
        chatElement.classList.add('chat-item');
        chatElement.dataset.chatId = chat.id;

        // 如果是当前选中的对话，添加active类
        if (chat.id === this.state.currentChatId) {
            chatElement.classList.add('active');
        }

        const contentElement = document.createElement('div');
        contentElement.classList.add('chat-item-content');
        contentElement.textContent = chat.title || '新对话';
        chatElement.appendChild(contentElement);

        const deleteButton = document.createElement('button');
        deleteButton.classList.add('delete-chat-btn');
        deleteButton.innerHTML = '<svg class="icon"><use href="#icon-trash"></use></svg>';
        deleteButton.title = "删除对话";
        deleteButton.addEventListener('click', (e) => {
            e.stopPropagation();
            this.deleteChat(chat.id);
        });
        chatElement.appendChild(deleteButton);

        chatElement.addEventListener('click', () => {
            if (chat.id !== this.state.currentChatId) {
                this.loadChat(chat.id);
            }
        });

        return chatElement;
    }

    updateActiveChatItem(chatId) {
        const chatItems = this.elements.chatHistory.querySelectorAll('.chat-item');
        chatItems.forEach(item => {
            item.classList.toggle('active', item.dataset.chatId === String(chatId));
        });
    }

    clearMessages() {
        this.elements.messagesContainer.innerHTML = '';
        this.currentAIMessage = null;
        this.lastSentMessage = null;
    }

    updateChatTitle(title) {
        if (this.elements.currentChatTitle) {
            this.elements.currentChatTitle.textContent = title;
        }
    }

    async loadChatHistory() {
        try {
            const response = await fetch(`${this.API_BASE_URL}/chat/chats`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) {
                throw new Error('Failed to load chat history');
            }

            this.state.chats = await response.json();
            
            // 清空现有历史
            this.elements.chatHistory.innerHTML = '';
            
            // 渲染所有对话
            this.state.chats.forEach(chat => {
                const chatElement = this.createChatElement(chat);
                this.elements.chatHistory.appendChild(chatElement);
            });

            // 如果有当前选中的对话，更新其状态
            if (this.state.currentChatId) {
                this.updateActiveChatItem(this.state.currentChatId);
            }

        } catch (error) {
            console.error('Failed to load chat history:', error);
            this.showError('加载对话历史失败');
        }
    }

    async deleteChat(chatId) {
        if (confirm('确定要删除这个对话吗？')) {
            try {
                await fetch(`${this.API_BASE_URL}/chat/chats/${chatId}`, {
                    method: 'DELETE',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                });
                this.loadChatHistory();
                if (this.state.currentChatId === chatId) {
                    this.elements.messagesContainer.innerHTML = '';
                    this.state.currentChatId = null;
                    document.getElementById('current-chat-title').textContent = '新对话';
                }
            } catch (error) {
                console.error('Failed to delete chat:', error);
                this.showError('Failed to delete chat');
            }
        }
    }

    async loadChat(chatId) {
        if (chatId === this.state.currentChatId) return;

        try {
            const response = await fetch(`${this.API_BASE_URL}/chat/chats/${chatId}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) throw new Error('Failed to load chat');

            const chat = await response.json();
            this.state.currentChatId = chatId;
            
            // 清空消息显示区域
            this.clearMessages();

            // 显示历史消息
            if (chat.messages && Array.isArray(chat.messages)) {
                chat.messages.forEach(msg => {
                    this.displayMessage(msg.content, msg.role, new Date(msg.timestamp), true);
                });
            }
            
            this.updateChatTitle(chat.title);
            this.updateActiveChatItem(chatId);
            
            // 缓存当前对话的消息
            this.state.messageCache.set(chatId, chat.messages);
            
        } catch (error) {
            console.error('Failed to load chat:', error);
            this.showError('加载对话失败');
        }
    }

    displayMessages(messages) {
        this.elements.messagesContainer.innerHTML = '';
        messages.forEach(msg => {
            if (!msg.timestamp) {
                console.warn('Message without timestamp:', msg);
            }
            this.displayMessage(
                msg.content, 
                msg.role, 
                msg.timestamp
            );
        });
    }

    displayMessage(content, role, timestamp, isHistory = false) {
        // 如果是新发送的用户消息且与最后发送的消息相同，则跳过
        if (!isHistory && role === 'user' && content === this.lastSentMessage) {
            return;
        }

        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${role}-message`);
        
        const contentElement = document.createElement('div');
        contentElement.classList.add('message-content');
        contentElement.textContent = content;
        messageElement.appendChild(contentElement);
        
        if (timestamp) {
            const timeElement = document.createElement('div');
            timeElement.classList.add('message-time');
            timeElement.textContent = this.formatTime(timestamp);
            messageElement.appendChild(timeElement);
        }
        
        this.elements.messagesContainer.appendChild(messageElement);
        this.scrollToBottom();

        // 如果不是历史消息，则添加到缓存
        if (!isHistory && this.state.currentChatId) {
            const messages = this.state.messageCache.get(this.state.currentChatId) || [];
            messages.push({
                content,
                role,
                timestamp: timestamp.toISOString()
            });
            this.state.messageCache.set(this.state.currentChatId, messages);
        }
    }

    formatTime(timestamp) {
        try {
            if (!timestamp) {
                console.warn('No timestamp provided');
                return '';
            }

            const date = new Date(timestamp);
            if (isNaN(date.getTime())) {
                console.error('Invalid timestamp:', timestamp);
                return '';
            }

            return date.toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit'
            });
        } catch (error) {
            console.error('Error formatting time:', error);
            return '';
        }
    }

    scrollToBottom() {
        this.elements.messagesContainer.scrollTop = this.elements.messagesContainer.scrollHeight;
    }

    handleMessageSend() {
        if (this.state.isSending) return;

        const message = this.elements.userInput.value.trim();
        if (!message) return;

        if (!this.state.currentChatId) {
            this.showError('请先选择或创建一个对话');
            return;
        }

        this.state.isSending = true;
        this.elements.sendButton.disabled = true;

        try {
            // 立即显示用户消息
            this.displayMessage(message, 'user', new Date());
            
            // 清空输入框更新UI
            this.elements.userInput.value = '';
            this.updateCharCount();
            this.adjustTextareaHeight();
            
            // 滚动到底部
            this.scrollToBottom();

            // 显示AI正在输入的提示
            this.elements.typingIndicator.classList.remove('hidden');

            // 发送消息到服务器
            if (this.socket?.readyState === WebSocket.OPEN) {
                this.lastSentMessage = message;
                this.socket.send(JSON.stringify({
                    chat_id: this.state.currentChatId,
                    message: message
                }));
            } else {
                this.showError('连接已断开，请刷新页面重试');
            }
        } finally {
            this.state.isSending = false;
            this.elements.sendButton.disabled = false;
        }
    }

    handleInput() {
        if (this.elements.charCount) {  // 检查元素是否存在
            this.updateCharCount();
        }
        this.adjustTextareaHeight();
    }

    updateCharCount() {
        if (this.elements.charCount) {  // 检查元素是否存在
            const count = this.elements.userInput.value.length;
            this.elements.charCount.textContent = `${count} / 2000`;
        }
    }

    adjustTextareaHeight() {
        this.elements.userInput.style.height = 'auto';
        this.elements.userInput.style.height = this.elements.userInput.scrollHeight + 'px';
    }

    handleWebSocketMessage(event) {
        try {
            const data = JSON.parse(event.data);
            console.log('Received message:', data);

            if (data.error) {
                this.showError(data.error);
            } else if (data.type === 'message') {
                // 跳过重复的用户消息
                if (data.role === 'user' && data.content === this.lastSentMessage) {
                    return;
                }
                this.displayMessage(data.content, data.role, new Date(data.timestamp));
            } else if (data.type === 'token') {
                this.appendToken(data.content);
            } else if (data.type === 'done') {
                this.finishAIMessage(new Date(data.timestamp));
            } else if (data.type === 'title_update') {
                this.updateChatTitle(data.chat_id, data.title);
            }
        } catch (error) {
            console.error('Error handling WebSocket message:', error);
        }
    }

    appendToken(token) {
        if (!this.state.currentAIMessage) {
            this.state.currentAIMessage = document.createElement('div');
            this.state.currentAIMessage.classList.add('message', 'ai-message');
            
            const contentElement = document.createElement('div');
            contentElement.classList.add('message-content');
            this.state.currentAIMessage.appendChild(contentElement);
            
            this.elements.messagesContainer.appendChild(this.state.currentAIMessage);
        }

        const contentElement = this.state.currentAIMessage.querySelector('.message-content');
        contentElement.textContent += token;
        this.scrollToBottom();
    }

    finishAIMessage(timestamp) {
        if (this.state.currentAIMessage) {
            const timeElement = document.createElement('div');
            timeElement.classList.add('message-time');
            timeElement.textContent = this.formatTime(timestamp);
            this.state.currentAIMessage.appendChild(timeElement);
            this.state.currentAIMessage = null;
        }
        this.elements.typingIndicator.classList.add('hidden');
    }

    updateChatTitle(chatId, newTitle) {
        // 更新左侧对话列表中的标题
        const chatItem = this.elements.chatHistory.querySelector(`[data-chat-id="${chatId}"]`);
        if (chatItem) {
            const titleElement = chatItem.querySelector('.chat-item-content');
            if (titleElement) {
                titleElement.textContent = newTitle;
            }
        }

        // 如果是当前对话，也更新顶部标题
        if (this.state.currentChatId === chatId) {
            const currentTitleElement = document.getElementById('current-chat-title');
            if (currentTitleElement) {
                currentTitleElement.textContent = newTitle;
            }
        }
    }

    openSettings() {
        // 实现设置功能
        console.log('Open settings');
    }

    toggleTheme() {
        document.body.classList.toggle('dark-theme');
    }

    clearChat() {
        if (confirm('Are you sure you want to clear this chat?')) {
            this.elements.messagesContainer.innerHTML = '';
            // 可以在这里添加清除服务器端聊天记录的API调用
        }
    }

    exportChat() {
        // 实现导出聊天功能
        console.log('Export chat');
    }

    showError(message) {
        console.error(message);
        
        // 创建一个临时的错误提示元素
        const errorToast = document.createElement('div');
        errorToast.className = 'error-toast';
        errorToast.textContent = message;
        document.body.appendChild(errorToast);

        // 3秒自动移除
        setTimeout(() => {
            errorToast.remove();
        }, 3000);
    }

    showLoading() {
        this.elements.loadingOverlay.classList.remove('hidden');
    }

    hideLoading() {
        this.elements.loadingOverlay.classList.add('hidden');
    }
}

// 添加错误提示的样式到 styles.css
const style = document.createElement('style');
style.textContent = `
    .error-toast {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background-color: #ff4d4f;
        color: white;
        padding: 12px 24px;
        border-radius: 4px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        z-index: 1000;
        animation: fadeIn 0.3s ease;
    }

    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translate(-50%, 20px);
        }
        to {
            opacity: 1;
            transform: translate(-50%, 0);
        }
    }
`;
document.head.appendChild(style);

// 导出 App 类（如果需要）
export default App;

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new App();
});
