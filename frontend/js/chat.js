import { chat } from './api/chat.js';

export class ChatUI {
    constructor(container) {
        this.container = container;
        this.messagesContainer = container.querySelector('.chat-messages');
        this.input = container.querySelector('#user-input');
        this.sendButton = container.querySelector('#send-message');
        this.historyList = container.querySelector('.history-list');
        this.newChatButton = container.querySelector('.new-chat-btn');
        
        this.currentChatId = null;
        this.setupEventListeners();
        this.loadChatHistory();
    }
    
    setupEventListeners() {
        // 发送消息
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // 新对话
        this.newChatButton.addEventListener('click', () => this.createNewChat());
        
        // 自动调整输入框高度
        this.input.addEventListener('input', () => {
            this.input.style.height = 'auto';
            this.input.style.height = (this.input.scrollHeight) + 'px';
        });
    }
    
    async loadChatHistory() {
        try {
            const history = await chat.getHistory();
            this.renderChatHistory(history);
            
            // 如果有历史记录，加载最新的对话
            if (history.length > 0) {
                await this.loadChat(history[0].id);
            } else {
                // 如果没有历史记录，创建新对话
                await this.createNewChat();
            }
        } catch (error) {
            console.error('加载历史记录失败:', error);
            // TODO: 显示错误提示
        }
    }
    
    renderChatHistory(history) {
        this.historyList.innerHTML = '';
        history.forEach(chat => {
            const item = document.createElement('div');
            item.className = `history-item ${chat.id === this.currentChatId ? 'active' : ''}`;
            item.dataset.chatId = chat.id;

            const content = document.createElement('div');
            content.className = 'history-item-content';

            // 添加标题
            const title = document.createElement('div');
            title.className = 'history-item-title';
            title.textContent = chat.title || '新对话';

            // 添加删除按钮
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'history-item-delete';
            deleteBtn.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <path d="M12 4L4 12M4 4L12 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            `;
            deleteBtn.addEventListener('click', async (e) => {
                e.stopPropagation();
                if (confirm('确定要删除这个对话吗？')) {
                    await this.deleteChat(chat.id);
                }
            });

            content.appendChild(title);
            item.appendChild(content);
            item.appendChild(deleteBtn);

            // 点击切换对话
            item.addEventListener('click', () => this.loadChat(chat.id));
            
            this.historyList.appendChild(item);
        });
    }
    
    async deleteChat(chatId) {
        try {
            await chat.deleteChat(chatId);
            
            // 如果删除的是当前对话，清空消息区域
            if (chatId === this.currentChatId) {
                this.currentChatId = null;
                this.messagesContainer.innerHTML = '';
            }
            
            // 重新加载历史记录
            await this.loadChatHistory();
        } catch (error) {
            console.error('删除对话失败:', error);
            // TODO: 显示错误提示
        }
    }
    
    async loadChat(chatId) {
        try {
            const messages = await chat.getMessages(chatId);
            this.currentChatId = chatId;
            
            // 更新UI
            this.messagesContainer.innerHTML = '';
            messages.forEach(msg => {
                this.addMessage(msg.content, msg.role === 'user');
            });
            
            // 更新历史记录的激活状态
            document.querySelectorAll('.history-item').forEach(item => {
                item.classList.toggle('active', item.dataset.chatId === String(chatId));
            });
        } catch (error) {
            console.error('加载对话失败:', error);
            // TODO: 显示错误提示
        }
    }
    
    async createNewChat() {
        try {
            const newChat = await chat.createChat();
            this.currentChatId = newChat.id;
            
            // 清空消息区域
            this.messagesContainer.innerHTML = '';
            
            // 重新加载历史记录
            await this.loadChatHistory();
        } catch (error) {
            console.error('创建新对话失败:', error);
            // TODO: 显示错误提示
        }
    }
    
    addMessage(message, isUser = false) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${isUser ? 'user' : 'bot'}`;
        
        const textElement = document.createElement('div');
        textElement.className = 'message-text';
        textElement.textContent = message;
        
        const timeElement = document.createElement('div');
        timeElement.className = 'message-time';
        timeElement.textContent = new Date().toLocaleTimeString();
        
        messageElement.appendChild(textElement);
        messageElement.appendChild(timeElement);
        
        this.messagesContainer.appendChild(messageElement);
        this.scrollToBottom();
    }
    
    showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'typing-indicator';
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('div');
            dot.className = 'typing-dot';
            indicator.appendChild(dot);
        }
        this.messagesContainer.appendChild(indicator);
        this.scrollToBottom();
        return indicator;
    }
    
    removeTypingIndicator(indicator) {
        if (indicator && indicator.parentNode) {
            indicator.parentNode.removeChild(indicator);
        }
    }
    
    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
    
    formatMessage(text) {
        // 将连续的换行符替换为单个换行符
        text = text.replace(/\n{3,}/g, '\n\n');
        
        // 处理标题格式
        text = text.replace(/###\s+(.*)/g, '<h3>$1</h3>');
        
        // 处理项目符号
        text = text.replace(/[•·]\s+(.*)/g, '<li>$1</li>');
        text = text.replace(/(?:^|\n)[-*]\s+(.*)/g, '<li>$1</li>');
        
        // 处理加粗文本
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // 将连续的列表项包装在ul标签中
        text = text.replace(/(<li>.*?<\/li>)\s*(?=<li>|$)/g, '<ul>$1</ul>');
        
        // 处理段落
        const paragraphs = text.split('\n\n');
        text = paragraphs.map(p => {
            if (!p.startsWith('<') && p.trim()) {
                return `<p>${p}</p>`;
            }
            return p;
        }).join('\n');
        
        return text;
    }
    
    async sendMessage() {
        const message = this.input.value.trim();
        if (!message || !this.currentChatId) return;
        
        // 添加用户消息
        this.addMessage(message, true);
        this.input.value = '';
        this.input.style.height = 'auto';
        
        // 创建AI消息容器
        const aiMessageContainer = document.createElement('div');
        aiMessageContainer.className = 'message bot';
        const aiMessageText = document.createElement('div');
        aiMessageText.className = 'message-text';
        const timeElement = document.createElement('div');
        timeElement.className = 'message-time';
        timeElement.textContent = new Date().toLocaleTimeString();
        aiMessageContainer.appendChild(aiMessageText);
        aiMessageContainer.appendChild(timeElement);
        this.messagesContainer.appendChild(aiMessageContainer);
        this.scrollToBottom();
        
        let responseText = '';
        
        try {
            const response = await fetch(`/api/v1/chat/${this.currentChatId}/messages/stream`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({ content: message })
            });
            
            if (!response.ok) {
                throw new Error('发送消息失败');
            }
            
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            
            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const content = line.slice(6);
                        responseText += content;
                        // 使用格式化函数处理文本
                        aiMessageText.innerHTML = this.formatMessage(responseText);
                        this.scrollToBottom();
                    } else if (line.startsWith('event: title')) {
                        const titleLine = lines[lines.indexOf(line) + 1];
                        if (titleLine?.startsWith('data: ')) {
                            const title = titleLine.slice(6);
                            this.updateChatTitle(this.currentChatId, title);
                        }
                    }
                }
            }
        } catch (error) {
            console.error('发送消息失败:', error);
            aiMessageText.textContent = '发送消息失败，请重试';
        }
    }
    
    updateChatTitle(chatId, title) {
        const historyItem = this.historyList.querySelector(`[data-chat-id="${chatId}"]`);
        if (historyItem) {
            const titleElement = historyItem.querySelector('.history-item-title');
            if (titleElement) {
                titleElement.textContent = title;
            }
        }
    }
} 