import { chat } from './api/chat.js';

// 等待依赖加载完成
function waitForDependencies() {
    return new Promise((resolve, reject) => {
        let attempts = 0;
        const maxAttempts = 10;
        
        function checkDependencies() {
            if (window.marked && window.hljs) {
                resolve();
            } else if (attempts >= maxAttempts) {
                reject(new Error('依赖加载超时'));
            } else {
                attempts++;
                setTimeout(checkDependencies, 500);
            }
        }
        
        checkDependencies();
    });
}

export class ChatUI {
    constructor(container) {
        this.container = container;
        this.messagesContainer = container.querySelector('.chat-messages');
        this.input = container.querySelector('#user-input');
        this.sendButton = container.querySelector('#send-message');
        this.historyList = container.querySelector('.history-list');
        this.newChatButton = container.querySelector('.new-chat-btn');
        
        this.currentChatId = null;
        
        // 初始化依赖
        this.initDependencies();
    }
    
    async initDependencies() {
        try {
            await waitForDependencies();
            
            // 配置marked
            window.marked.setOptions({
                renderer: new window.marked.Renderer(),
                highlight: function(code, lang) {
                    if (lang && window.hljs.getLanguage(lang)) {
                        return window.hljs.highlight(code, { language: lang }).value;
                    }
                    return window.hljs.highlightAuto(code).value;
                },
                pedantic: false,
                gfm: true,
                breaks: true,
                sanitize: false,
                smartypants: true,
                xhtml: false
            });
            
            // 初始化其他功能
            this.setupEventListeners();
            this.loadChatHistory();
            
        } catch (error) {
            console.error('初始化失败:', error);
            this.showError('系统初始化失败，请刷新页面重试');
        }
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
            this.historyList.innerHTML = '';
            
            history.forEach(chat => {
                const item = document.createElement('div');
                item.className = `history-item ${chat.id === this.currentChatId ? 'active' : ''}`;
                item.dataset.chatId = chat.id;
                
                const content = document.createElement('div');
                content.className = 'history-item-content';
                
                const title = document.createElement('div');
                title.className = 'history-item-title';
                title.textContent = chat.title || '新对话';
                
                const deleteBtn = document.createElement('button');
                deleteBtn.className = 'history-item-delete';
                deleteBtn.innerHTML = `
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M12 4L4 12M4 4L12 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                `;
                
                content.appendChild(title);
                item.appendChild(content);
                item.appendChild(deleteBtn);
                
                // 点击切换对话
                item.addEventListener('click', () => this.loadChat(chat.id));
                
                // 点击删除按钮
                deleteBtn.addEventListener('click', async (e) => {
                    e.stopPropagation();
                    if (confirm('确定要删除这个对话吗？')) {
                        await this.deleteChat(chat.id);
                    }
                });
                
                this.historyList.appendChild(item);
            });
            
            // 如果有历史记录但没有当前对话，加载第一个
            if (history.length > 0 && !this.currentChatId) {
                await this.loadChat(history[0].id);
            }
        } catch (error) {
            console.error('加载历史记录失败:', error);
            this.showError('加载历史记录失败，请重试');
        }
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
            const [chatData, messages] = await Promise.all([
                chat.getChat(chatId),
                chat.getMessages(chatId)
            ]);
            
            this.currentChatId = chatId;
            this.messagesContainer.innerHTML = '';
            
            // 渲染历史消息
            messages.forEach(msg => {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${msg.role === 'user' ? 'user' : 'bot'}`;
                
                const messageText = document.createElement('div');
                messageText.className = `message-text ${msg.role === 'bot' ? 'markdown-body' : ''}`;
                
                // 对AI回复使用Markdown解析
                if (msg.role === 'bot') {
                    messageText.innerHTML = window.marked.parse(msg.content, {
                        breaks: true,
                        gfm: true,
                        pedantic: false,
                        mangle: false,
                        headerIds: false,
                        smartLists: true,
                        smartypants: true
                    });
                } else {
                    messageText.textContent = msg.content;
                }
                
                const timeElement = document.createElement('div');
                timeElement.className = 'message-time';
                timeElement.textContent = new Date(msg.created_at).toLocaleTimeString();
                
                messageDiv.appendChild(messageText);
                messageDiv.appendChild(timeElement);
                this.messagesContainer.appendChild(messageDiv);
            });
            
            // 更新历史记录列表中的激活状态
            document.querySelectorAll('.history-item').forEach(item => {
                item.classList.toggle('active', item.dataset.chatId === String(chatId));
            });
            
            this.scrollToBottom();
            
        } catch (error) {
            console.error('加载对话失败:', error);
            this.showError('加载对话失败，请重试');
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
        
        // 添加思考中动画
        const thinkingDiv = document.createElement('div');
        thinkingDiv.className = 'thinking';
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('div');
            dot.className = 'thinking-dot';
            thinkingDiv.appendChild(dot);
        }
        this.messagesContainer.appendChild(thinkingDiv);
        this.scrollToBottom();
        
        try {
            // 创建AI消息容器
            const aiMessageContainer = document.createElement('div');
            aiMessageContainer.className = 'message bot typing';
            const aiMessageText = document.createElement('div');
            aiMessageText.className = 'message-text markdown-body';
            const timeElement = document.createElement('div');
            timeElement.className = 'message-time';
            
            let responseText = '';
            let currentParagraph = '';
            let isInCodeBlock = false;
            let codeBlockContent = '';
            let codeBlockLanguage = '';
            
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
            
            // 移除思考中动画
            thinkingDiv.remove();
            
            // 添加AI消息容器
            this.messagesContainer.appendChild(aiMessageContainer);
            aiMessageContainer.appendChild(aiMessageText);
            aiMessageContainer.appendChild(timeElement);
            
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
                        
                        // 文本预处理
                        const processedText = responseText
                            // 处理段落
                            .split('\n\n')
                            .map(paragraph => {
                                // 处理每个段落
                                return paragraph
                                    .split('\n')
                                    .map(line => line.trim())
                                    .filter(line => line)
                                    .join('\n');
                            })
                            .filter(paragraph => paragraph)
                            .join('\n\n');
                        
                        // 处理特殊格式
                        const formattedText = processedText
                            // 处理代码块
                            .replace(/```([\s\S]*?)```/g, (match, code) => {
                                const lines = code.trim().split('\n');
                                const language = lines[0].trim();
                                const codeContent = lines.slice(1).join('\n');
                                return `\n\`\`\`${language}\n${codeContent}\n\`\`\`\n`;
                            })
                            // 处理行内代码
                            .replace(/`([^`]+)`/g, '`$1`')
                            // 处理列表
                            .replace(/^[*-]\s+/gm, '• ')
                            .replace(/^\d+\.\s+/gm, (match) => match)
                            // 处理引用
                            .replace(/^>\s+/gm, '> ')
                            // 处理标题
                            .replace(/^(#{1,6})\s+/gm, (match, hashes) => hashes + ' ');
                        
                        // 使用marked渲染Markdown
                        const htmlContent = window.marked.parse(formattedText, {
                            breaks: true,
                            gfm: true,
                            pedantic: false,
                            mangle: false,
                            headerIds: false,
                            smartLists: true,
                            smartypants: true
                        });
                        
                        // 添加样式处理
                        const styledContent = htmlContent
                            // 段落样式
                            .replace(/<p>/g, '<p style="margin: 1em 0; line-height: 1.8;">')
                            // 列表样式
                            .replace(/<ul>/g, '<ul style="margin: 1em 0; padding-left: 2em;">')
                            .replace(/<ol>/g, '<ol style="margin: 1em 0; padding-left: 2em;">')
                            .replace(/<li>/g, '<li style="margin: 0.5em 0;">')
                            // 代码块样式
                            .replace(/<pre><code/g, '<pre style="margin: 1em 0; padding: 1em; background: #f6f8fa; border-radius: 6px; overflow-x: auto;"><code')
                            // 行内代码样式
                            .replace(/<code>/g, '<code style="padding: 0.2em 0.4em; background: #f6f8fa; border-radius: 3px;">')
                            // 引用样式
                            .replace(/<blockquote>/g, '<blockquote style="margin: 1em 0; padding: 0.5em 1em; border-left: 4px solid #ddd; background: #f9f9f9;">')
                            // 标题样式
                            .replace(/<h([1-6])>/g, (_, level) => `<h${level} style="margin: 1.5em 0 1em; font-weight: 600; line-height: 1.4;">`);
                        
                        aiMessageText.innerHTML = styledContent;
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
            
            // 消息接收完成后
            aiMessageContainer.classList.remove('typing');
            timeElement.textContent = new Date().toLocaleTimeString();
            
        } catch (error) {
            console.error('发送消息失败:', error);
            thinkingDiv.remove();
            this.showError('发送消息失败，请重试');
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
    
    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'message-error';
        errorDiv.textContent = message;
        this.messagesContainer.appendChild(errorDiv);
        this.scrollToBottom();
        
        // 3秒后自动移除错误提示
        setTimeout(() => {
            errorDiv.remove();
        }, 3000);
    }
} 