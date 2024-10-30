import { request } from './utils/request.js';
import { chat } from './api/chat.js';

class FileUploader {
    constructor() {
        this.uploadArea = document.getElementById('upload-area');
        this.fileInput = document.getElementById('file-input');
        this.fileGrid = document.getElementById('file-grid');
        
        this.maxFileSize = 10 * 1024 * 1024; // 10MB
        this.allowedTypes = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain',
            'image/jpeg',
            'image/png',
            'image/gif'
        ];
        
        this.setupEventListeners();
        this.loadExistingFiles();
    }
    
    setupEventListeners() {
        // 点击上传区域触发文件选择
        this.uploadArea.addEventListener('click', () => {
            this.fileInput.click();
        });
        
        // 文件选择处理
        this.fileInput.addEventListener('change', (e) => {
            this.handleFiles(e.target.files);
        });
        
        // 拖放处理
        this.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.uploadArea.classList.add('drag-over');
        });
        
        this.uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.uploadArea.classList.remove('drag-over');
        });
        
        this.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.uploadArea.classList.remove('drag-over');
            this.handleFiles(e.dataTransfer.files);
        });
    }
    
    async handleFiles(files) {
        for (const file of files) {
            if (!this.validateFile(file)) continue;
            await this.uploadFile(file);
        }
    }
    
    validateFile(file) {
        if (file.size > this.maxFileSize) {
            this.showError(`文件 ${file.name} 超过10MB限制`);
            return false;
        }
        
        if (!this.allowedTypes.includes(file.type)) {
            this.showError(`不支持的文件类型: ${file.name}`);
            return false;
        }
        
        return true;
    }
    
    async uploadFile(file) {
        // 创建文件预览
        const fileItem = this.createFilePreview(file);
        this.fileGrid.appendChild(fileItem);
        
        try {
            const data = await chat.uploadFile(file);
            this.updateFilePreview(fileItem, data);
        } catch (error) {
            console.error('文件上传失败:', error);
            fileItem.remove();
            this.showError(`文件 ${file.name} 上传失败`);
        }
    }
    
    async loadExistingFiles() {
        try {
            const files = await chat.getFiles();
            if (files && files.length > 0) {
                this.displayFiles(files);
            }
        } catch (error) {
            console.error('加载文件列表失败:', error);
            if (error.message === 'Unauthorized') {
                // 可以在这里处理未登录的情况
                window.location.href = '/login.html';
            }
        }
    }
    
    createFilePreview(file) {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <div class="file-icon ${this.getFileTypeClass(file)}">
                ${this.getFileTypeIcon(file)}
            </div>
            <div class="file-info">
                <div class="file-name">${file.name}</div>
                <div class="file-meta">
                    ${this.formatFileSize(file.size)} • 上传中...
                </div>
            </div>
            <div class="file-actions">
                <button class="file-action-btn delete" title="删除">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M12 4L4 12M4 4L12 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                    </svg>
                </button>
            </div>
        `;
        return fileItem;
    }
    
    updateFilePreview(fileItem, fileData) {
        const meta = fileItem.querySelector('.file-meta');
        meta.textContent = `${this.formatFileSize(fileData.size)} • 已完成`;
        
        // 添加删除功能
        const deleteBtn = fileItem.querySelector('.delete');
        deleteBtn.addEventListener('click', () => this.deleteFile(fileData.id, fileItem));
    }
    
    async deleteFile(fileId, fileItem) {
        try {
            const result = await chat.deleteFile(fileId);
            if (result && result.status === 'success') {
                fileItem.remove();
            } else {
                throw new Error('删除失败');
            }
        } catch (error) {
            console.error('删除文件失败:', error);
            this.showError('删除文件失败');
        }
    }
    
    getFileTypeClass(file) {
        if (file.type.startsWith('image/')) return 'image';
        if (file.type === 'application/pdf') return 'pdf';
        return 'document';
    }
    
    getFileTypeIcon(file) {
        // 返回不同文件类型的SVG图标
        const icons = {
            image: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                        <path d="M19 3H5C3.89543 3 3 3.89543 3 5V19C3 20.1046 3.89543 21 5 21H19C20.1046 21 21 20.1046 21 19V5C21 3.89543 20.1046 3 19 3Z" stroke="currentColor" stroke-width="2"/>
                        <path d="M8.5 10C9.32843 10 10 9.32843 10 8.5C10 7.67157 9.32843 7 8.5 7C7.67157 7 7 7.67157 7 8.5C7 9.32843 7.67157 10 8.5 10Z" fill="currentColor"/>
                        <path d="M21 15L16 10L7 19H19C20.1046 19 21 18.1046 21 17V15Z" fill="currentColor"/>
                    </svg>`,
            pdf: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M19 3H5C3.89543 3 3 3.89543 3 5V19C3 20.1046 3.89543 21 5 21H19C20.1046 21 21 20.1046 21 19V5C21 3.89543 20.1046 3 19 3Z" stroke="currentColor" stroke-width="2"/>
                    <path d="M7 12H17M7 16H12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>`,
            document: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                        <path d="M19 3H5C3.89543 3 3 3.89543 3 5V19C3 20.1046 3.89543 21 5 21H19C20.1046 21 21 20.1046 21 19V5C21 3.89543 20.1046 3 19 3Z" stroke="currentColor" stroke-width="2"/>
                        <path d="M7 7H17M7 12H17M7 17H12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>`
        };
        
        return icons[this.getFileTypeClass(file)];
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    showError(message) {
        // 创建错误提示
        const error = document.createElement('div');
        error.className = 'error-message';
        error.textContent = message;
        document.body.appendChild(error);
        
        // 3秒后自动移除
        setTimeout(() => error.remove(), 3000);
    }
    
    displayFiles(files) {
        files.forEach(file => {
            const fileItem = this.createFilePreview({
                name: file.filename,
                size: file.file_size,
                type: file.file_type
            });
            this.updateFilePreview(fileItem, file);
            this.fileGrid.appendChild(fileItem);
        });
    }
}

// 初始化上传器
document.addEventListener('DOMContentLoaded', () => {
    new FileUploader();
}); 