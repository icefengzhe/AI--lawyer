import { chat } from './api/chat.js';
import { fileApi } from './api/file.js';

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

// 创建一个全局状态管理器
const GlobalState = {
    uploadDialogCreated: false
};

export class ChatUI {
    constructor(container) {
        if (!container) {
            throw new Error('Container element is required');
        }
        
        this.container = container;
        this.messagesContainer = container.querySelector('.chat-messages');
        this.messageInput = container.querySelector('#message-input');
        this.sendButton = container.querySelector('#send-btn');
        this.uploadButton = container.querySelector('#upload-btn');
        this.fileInput = container.querySelector('#file-input');
        this.historyList = container.querySelector('.history-list');
        this.newChatButton = container.querySelector('.new-chat-btn');
        
        this.currentChatId = null;
        
        // 状态变量
        this.isStreaming = false;
        this.streamComplete = false;
        this.currentStreamOutput = '';
        this.autoSyncInterval = null;
        this.lastCompleteMessage = null;
        
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 3;
        this.pendingMessage = null;
        
        // 活动消息流追踪
        this.activeStreams = new Map();
        this.messageQueue = new Map();
        
        // 存储每个对话的消息容器
        this.chatContainers = new Map();
        
        // 流动画计时器Map
        this.streamAnimationTimers = new Map();
        
        // 验证必要的元素是否存在
        if (!this.messagesContainer) throw new Error('Messages container not found');
        if (!this.messageInput) throw new Error('Message input not found');
        if (!this.sendButton) throw new Error('Send button not found');
        if (!this.uploadButton) throw new Error('Upload button not found');
        if (!this.fileInput) throw new Error('File input not found');
        if (!this.historyList) throw new Error('History list not found');
        if (!this.newChatButton) throw new Error('New chat button not found');
        
        // 确保先创建上传对话框
        this.initUploadDialog();
        
        // 初始化
        this.initDependencies().catch(error => {
            console.error('初始化失败:', error);
            this.showError('系统初始化失败，请刷新页面重试');
        });
        
        // 添加页面可见性变化监听
        document.addEventListener('visibilitychange', () => {
            this.handleVisibilityChange();
        });
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
            
            // 初始化事件监听和加载历史记录
            this.setupEventListeners();
            await this.loadChatHistory();
            
        } catch (error) {
            console.error('初始化失败:', error);
            this.showError('系统初始化失败，请刷新页面重试');
            throw error;
        }
    }
    
    setupEventListeners() {
        // 发送消息
        this.sendButton.addEventListener('click', () => {
            const message = this.messageInput.value.trim();
            if (message) {
                this.sendMessage(message);
                this.messageInput.value = '';
                this.messageInput.style.height = 'auto';
            }
        });

        // 文件上传按钮点击
        this.uploadButton.addEventListener('click', (e) => {
            e.preventDefault();
            window.open('/upload.html', '_blank');
        });

        // 文件选择处理
        this.fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFiles(e.target.files);
            }
        });

        // 输入框回车发送
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                const message = this.messageInput.value.trim();
                if (message) {
                    this.sendMessage(message);
                    this.messageInput.value = '';
                    this.messageInput.style.height = 'auto';
                }
            }
        });

        // 自动调整输入框高度
        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = this.messageInput.scrollHeight + 'px';
        });

        // 退出登录按钮事件
        const logoutButton = this.container.querySelector('#logout');
        if (logoutButton) {
            logoutButton.addEventListener('click', () => {
                localStorage.removeItem('token');
                window.location.href = '/login.html';
            });
        }

        // 新对话按钮事件
        this.newChatButton.addEventListener('click', () => {
            this.createNewChat();
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
                
                // 击删除按钮
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
            if (error.message === 'Unauthorized' || error.message === '据') {
                localStorage.removeItem('token');
                window.location.href = '/login.html';
                return;
            }
            this.showError('加载历史记录失败，请重试');
        }
    }
    
    async deleteChat(chatId) {
        try {
            await chat.deleteChat(chatId);
            
            // 果删除的是当前对话，清空消息区域
            if (chatId === this.currentChatId) {
                this.currentChatId = null;
                this.messagesContainer.innerHTML = '';
            }
            
            // 重新加载历史记录
            await this.loadChatHistory();
        } catch (error) {
            console.error('删除对话失败:', error);
            this.showError('删除对话失败，请重试');
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
                    messageText.innerHTML = window.marked.parse(msg.content);
                } else {
                    messageText.textContent = msg.content;
                }
                
                const timeElement = document.createElement('div');
                timeElement.className = 'message-time';
                timeElement.textContent = this.formatMessageTime(msg.created_at);
                
                messageDiv.appendChild(messageText);
                messageDiv.appendChild(timeElement);
                this.messagesContainer.appendChild(messageDiv);
            });
            
            // 更新历史记录列表中的激活状态
            this.updateHistoryActiveState(chatId);
            
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
            
            // 重置状态
            this.currentStreamOutput = '';
            this.lastCompleteMessage = null;
            this.streamComplete = true;
            this.stopAutoSync();
            
            // 清空消息区域
            this.messagesContainer.innerHTML = '';
            
            // 重新加载历史记录
            await this.loadChatHistory();
            
        } catch (error) {
            console.error('创建新对话失败:', error);
            this.showError('创建新对话失败，请重试');
        }
    }
    
    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
    
    async sendMessage(message) {
        if (!message.trim() || !this.currentChatId) return;
        
        try {
            // 添加用户消息到界面
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message user';
            messageDiv.innerHTML = `
                <div class="message-text">${message}</div>
                <div class="message-time">${new Date().toLocaleTimeString()}</div>
            `;
            this.messagesContainer.appendChild(messageDiv);

            // 创建机器人消息元素
            const botDiv = document.createElement('div');
            botDiv.className = 'message bot typing';
            botDiv.innerHTML = `
                <div class="message-text markdown-body"></div>
                <div class="message-time">${new Date().toLocaleTimeString()}</div>
            `;
            this.messagesContainer.appendChild(botDiv);
            
            this.scrollToBottom();

            // 获取 token
            const token = localStorage.getItem('token');
            if (!token) {
                throw new Error('未登录');
            }

            // 创建 WebSocket 连接
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/api/v1/chat/${this.currentChatId}/messages/stream?token=${encodeURIComponent(token)}`;

            const ws = new WebSocket(wsUrl);
            let responseText = '';

            ws.onopen = () => {
                ws.send(JSON.stringify({ content: message }));
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    const textElement = botDiv.querySelector('.message-text');

                    switch(data.type) {
                        case 'token':
                            if (data.content) {
                                responseText += data.content;
                                if (textElement) {
                                    textElement.innerHTML = window.marked.parse(responseText);
                                    textElement.querySelectorAll('pre code').forEach((block) => {
                                        window.hljs.highlightElement(block);
                                    });
                                    this.scrollToBottom();
                                }
                            }
                            break;
                        case 'title':
                            if (data.content) {
                                this.updateChatTitle(this.currentChatId, data.content);
                            }
                            break;
                        case 'error':
                            this.showError(data.content || '发生错误');
                            botDiv.remove();
                            ws.close();
                            break;
                        case 'end':
                            botDiv.classList.remove('typing');
                            ws.close();
                            break;
                    }
                } catch (error) {
                    console.error('处理消息失败:', error);
                    this.showError('处理消息失败');
                    ws.close();
                }
            };

            ws.onclose = () => {
                botDiv.classList.remove('typing');
            };

            ws.onerror = (error) => {
                console.error('WebSocket 错误:', error);
                this.showError('连接错误，请重试');
                botDiv.remove();
                ws.close();
            };

        } catch (error) {
            console.error('发送消息失败:', error);
            this.showError(error.message || '发送消息失败，请重试');
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

    formatMessageTime(timestamp) {
        const messageDate = new Date(timestamp);
        const now = new Date();
        
        const timeStr = messageDate.toLocaleTimeString('zh-CN', {
            hour: '2-digit',
            minute: '2-digit'
        });
        
        // 判断是否是今天
        if (messageDate.toDateString() === now.toDateString()) {
            return timeStr;
        }
        
        // 判断是否是昨天
        const yesterday = new Date(now);
        yesterday.setDate(yesterday.getDate() - 1);
        if (messageDate.toDateString() === yesterday.toDateString()) {
            return `昨天 ${timeStr}`;
        }
        
        // 判断是否是本年
        if (messageDate.getFullYear() === now.getFullYear()) {
            return `${messageDate.getMonth() + 1}月${messageDate.getDate()}日 ${timeStr}`;
        }
        
        // 其他情况显示完整日期
        return `${messageDate.toLocaleDateString('zh-CN')} ${timeStr}`;
    }

    handleVisibilityChange() {
        if (document.visibilityState === 'visible' && !this.streamComplete) {
            this.startAutoSync();
        } else if (document.visibilityState === 'hidden') {
            this.stopAutoSync();
        }
    }

    startAutoSync() {
        if (this.autoSyncInterval) return;
        
        this.autoSyncInterval = setInterval(async () => {
            try {
                const response = await fetch(`/api/v1/chat/${this.currentChatId}/messages`, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                });
                
                if (!response.ok) throw new Error('同步失败');
                
                const messages = await response.json();
                const lastMessage = messages[messages.length - 1];
                
                if (lastMessage && lastMessage.role === 'assistant') {
                    const messageElement = this.messagesContainer.lastElementChild;
                    if (messageElement) {
                        const textElement = messageElement.querySelector('.message-text');
                        if (textElement) {
                            textElement.innerHTML = window.marked.parse(lastMessage.content);
                            if (lastMessage.is_complete) {
                                messageElement.classList.remove('typing');
                                this.stopAutoSync();
                            }
                        }
                    }
                }
            } catch (error) {
                console.error('同步消息失败:', error);
            }
        }, 1000);
    }

    stopAutoSync() {
        if (this.autoSyncInterval) {
            clearInterval(this.autoSyncInterval);
            this.autoSyncInterval = null;
        }
    }

    cleanup() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.reconnectAttempts = 0;
        this.pendingMessage = null;
        this.stopAutoSync();
        this.streamComplete = true;
        this.currentStreamOutput = '';
        
        // 清理所有消息容器
        this.chatContainers.forEach(container => {
            container.remove();
        });
        this.chatContainers.clear();
        this.activeStreams.clear();
    }

    static checkToken() {
        const token = localStorage.getItem('token');
        if (!token) {
            console.error('No token found in localStorage');
            return false;
        }
        try {
            const parts = token.split('.');
            if (parts.length !== 3) {
                console.error('Invalid token format');
                localStorage.removeItem('token');
                return false;
            }
        } catch (e) {
            console.error('Token validation failed:', e);
            localStorage.removeItem('token');
            return false;
        }
        return true;
    }

    updateHistoryActiveState(activeChatId) {
        document.querySelectorAll('.history-item').forEach(item => {
            item.classList.toggle('active', item.dataset.chatId === String(activeChatId));
        });
    }

    async handleFiles(files) {
        try {
            for (const file of files) {
                const formData = new FormData();
                formData.append('file', file);
                
                const response = await fileApi.uploadFile(formData);
                if (response && response.path) {
                    this.sendMessage(`文件路径：${response.path}`);
                }
            }
        } catch (error) {
            console.error('文件上传失败:', error);
            this.showError('文件上传失败，请重试');
        }
    }

    initUploadDialog() {
        // 检查全局状态
        if (GlobalState.uploadDialogCreated) {
            console.log('[Upload] 对话框已存在，跳过创建');
            this.uploadDialog = document.getElementById('upload-dialog');
            return;
        }

        console.log('[Upload] 创建新的上传对话框');
        
        // 创建对话框
        const dialogHTML = `
            <div id="upload-dialog" class="upload-dialog" style="display: none;">
                <div class="upload-content">
                    <div class="upload-header">
                        <h3>上传文件</h3>
                        <button class="close-btn" id="upload-close-btn">&times;</button>
                    </div>
                    <div class="upload-body">
                        <input type="file" id="file-input" multiple />
                        <div class="upload-list"></div>
                    </div>
                </div>
            </div>
        `;

        // 添加到body
        document.body.insertAdjacentHTML('beforeend', dialogHTML);
        
        // 设置全局状态
        GlobalState.uploadDialogCreated = true;
        
        // 获取对话框引用
        this.uploadDialog = document.getElementById('upload-dialog');
        
        // 绑定事件
        this.bindUploadEvents();
    }

    bindUploadEvents() {
        if (!this.uploadDialog) return;

        // 关闭按钮事件
        const closeBtn = this.uploadDialog.querySelector('#upload-close-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.hideUploadDialog());
        }

        // 点击背景关闭
        this.uploadDialog.addEventListener('click', (e) => {
            if (e.target === this.uploadDialog) {
                this.hideUploadDialog();
            }
        });

        // 文件选择事件
        const fileInput = this.uploadDialog.querySelector('#file-input');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        }
    }

    showUploadDialog() {
        // 如果对话框不存在，重新初始化
        if (!document.getElementById('upload-dialog')) {
            console.log('[Upload] 对话框不存在，重新初始化');
            GlobalState.uploadDialogCreated = false;
            this.initUploadDialog();
        }

        if (this.uploadDialog) {
            // 重置文件输入和上传列表
            const fileInput = this.uploadDialog.querySelector('#file-input');
            const uploadList = this.uploadDialog.querySelector('.upload-list');
            if (fileInput) fileInput.value = '';
            if (uploadList) uploadList.innerHTML = '';
            
            this.uploadDialog.style.display = 'flex';
            console.log('[Upload] 显示上传对话框');
        }
    }

    hideUploadDialog() {
        if (this.uploadDialog) {
            this.uploadDialog.style.display = 'none';
            console.log('[Upload] 隐藏上传对话框');
        }
    }

    handleFileSelect(event) {
        if (!this.uploadDialog) return;
        
        const files = event.target.files;
        const uploadList = this.uploadDialog.querySelector('.upload-list');
        if (!uploadList) return;

        uploadList.innerHTML = '';

        Array.from(files).forEach(file => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <span>${file.name}</span>
                <div class="progress-bar">
                    <div class="progress" style="width: 0%"></div>
                </div>
            `;
            uploadList.appendChild(fileItem);
        });

        this.uploadFiles(files);
    }

    async uploadFiles(files) {
        if (!this.uploadDialog) return;
        
        const uploadList = this.uploadDialog.querySelector('.upload-list');
        if (!uploadList) return;

        for (const file of files) {
            try {
                const formData = new FormData();
                formData.append('file', file);

                const response = await fetch('/api/v1/upload', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    },
                    body: formData
                });

                if (!response.ok) {
                    throw new Error('上传失败');
                }

                // 更新进度条
                const fileItems = uploadList.querySelectorAll('.file-item');
                const fileItem = Array.from(fileItems).find(item => 
                    item.querySelector('span').textContent === file.name
                );
                if (fileItem) {
                    const progressBar = fileItem.querySelector('.progress');
                    progressBar.style.width = '100%';
                    progressBar.style.backgroundColor = '#4CAF50';
                }

            } catch (error) {
                console.error('文件上传失败:', error);
                this.showError(`文件 ${file.name} 上传失败`);
            }
        }

        // 上传完成后延迟关闭
        setTimeout(() => this.hideUploadDialog(), 1500);
    }
}

// 在页面加载时清理可能存在的旧对话框
document.addEventListener('DOMContentLoaded', () => {
    const oldDialog = document.getElementById('upload-dialog');
    if (oldDialog) {
        oldDialog.remove();
    }
});

// 添加页面卸载事件处理
window.addEventListener('beforeunload', () => {
    // 重置全局状态
    GlobalState.uploadDialogCreated = false;
});

// 添加路由变化监听（如果使用了前端路由）
window.addEventListener('popstate', () => {
    // 检查并清理重复的对话框
    const dialogs = document.querySelectorAll('#upload-dialog');
    if (dialogs.length > 1) {
        // 保留第一个，删除其他的
        for (let i = 1; i < dialogs.length; i++) {
            dialogs[i].remove();
        }
    }
});