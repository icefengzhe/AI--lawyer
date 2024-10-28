import { state } from '../utils/state.js';
import { logger } from '../utils/logger.js';

class WebSocketService {
    constructor(baseURL) {
        this.baseURL = baseURL;
        this.socket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.isConnected = false;
        this.connectPromise = null;  // 添加连接Promise
    }

    async connect() {
        if (this.connectPromise) {
            return this.connectPromise;
        }

        const token = localStorage.getItem('token');
        if (!token) {
            logger.error('No token found for WebSocket connection');
            return false;
        }

        // 移除Bearer前缀（如果存在）
        const cleanToken = token.replace('Bearer ', '');

        this.connectPromise = new Promise((resolve, reject) => {
            try {
                logger.info('Connecting to WebSocket...');
                this.socket = new WebSocket(`${this.baseURL}/ws?token=${encodeURIComponent(cleanToken)}`);
                
                this.socket.onopen = () => {
                    logger.info('WebSocket connected successfully');
                    this.isConnected = true;
                    this.reconnectAttempts = 0;
                    state.set('wsConnected', true);
                    resolve(true);
                };

                this.socket.onmessage = (event) => {
                    this.handleMessage(event.data);
                };

                this.socket.onclose = () => {
                    logger.warn('WebSocket disconnected');
                    this.isConnected = false;
                    state.set('wsConnected', false);
                    this.connectPromise = null;  // 清除连接Promise
                    this.handleReconnect();
                };

                this.socket.onerror = (error) => {
                    logger.error('WebSocket error:', error);
                    this.isConnected = false;
                    reject(error);
                    this.connectPromise = null;  // 清除连接Promise
                };
            } catch (error) {
                logger.error('Failed to create WebSocket connection:', error);
                this.connectPromise = null;  // 清除连接Promise
                reject(error);
            }
        });

        return this.connectPromise;
    }

    handleMessage(data) {
        try {
            const parsedData = JSON.parse(data);
            if (parsedData.error) {
                state.emit('error', parsedData.error);
            } else if (parsedData.type === 'title_update') {
                state.emit('titleUpdate', parsedData);
            } else if (parsedData.message) {
                state.emit('message', {
                    content: parsedData.message,
                    role: 'ai'
                });
            }
        } catch (error) {
            logger.error('Error handling WebSocket message:', error);
        }
    }

    async handleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 10000);
            logger.info(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);
            
            await new Promise(resolve => setTimeout(resolve, delay));
            try {
                await this.connect();
            } catch (error) {
                logger.error('Reconnection failed:', error);
            }
        } else {
            logger.error('Max reconnection attempts reached');
            state.emit('error', '连接失败，请刷新页面重试');
        }
    }

    async sendMessage(chatId, message) {
        if (!this.isConnected) {
            try {
                logger.info('WebSocket not connected, attempting to connect...');
                await this.connect();
            } catch (error) {
                logger.error('Failed to establish connection:', error);
                throw new Error('WebSocket is not connected');
            }
        }

        if (!this.socket || !this.isConnected) {
            throw new Error('WebSocket is not connected');
        }

        try {
            this.socket.send(JSON.stringify({
                chat_id: chatId,
                message: message
            }));
            return true;
        } catch (error) {
            logger.error('Error sending message:', error);
            throw error;
        }
    }

    disconnect() {
        if (this.socket) {
            this.socket.close();
            this.socket = null;
            this.isConnected = false;
            this.connectPromise = null;
        }
    }
}

export const wsService = new WebSocketService('ws://localhost:8000/api/chat');
