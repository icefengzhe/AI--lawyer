import { state } from '../utils/state.js';
import { logger } from '../utils/logger.js';

class UIComponent {
    constructor() {
        this.elements = {
            loadingOverlay: document.getElementById('loading-overlay'),
            errorToast: document.getElementById('error-toast'),
            themeToggleBtn: document.getElementById('theme-toggle-btn')
        };
        this.setupEventListeners();
    }

    setupEventListeners() {
        state.on('loading', this.handleLoadingState.bind(this));
        state.on('error', this.showError.bind(this));
        this.elements.themeToggleBtn.addEventListener('click', this.toggleTheme.bind(this));
    }

    handleLoadingState(isLoading) {
        if (isLoading) {
            this.showLoading();
        } else {
            this.hideLoading();
        }
    }

    showLoading() {
        logger.info('显示加载动画');
        this.elements.loadingOverlay.classList.remove('hidden');
    }

    hideLoading() {
        logger.info('隐藏加载动画');
        this.elements.loadingOverlay.classList.add('hidden');
    }

    showError(message) {
        logger.error('显示错误信息:', message);
        this.elements.errorToast.textContent = message;
        this.elements.errorToast.classList.remove('hidden');
        setTimeout(() => {
            this.elements.errorToast.classList.add('hidden');
        }, 3000);
    }

    toggleTheme() {
        const isDarkTheme = document.body.classList.toggle('dark-theme');
        this.elements.themeToggleBtn.innerHTML = isDarkTheme ? 
            '<i class="fas fa-sun"></i>' : 
            '<i class="fas fa-moon"></i>';
        localStorage.setItem('theme', isDarkTheme ? 'dark' : 'light');
        logger.info(`主题切换为: ${isDarkTheme ? '深色' : '浅色'}`);
    }

    checkAndApplyTheme() {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-theme');
            this.elements.themeToggleBtn.innerHTML = '<i class="fas fa-sun"></i>';
        }
    }
}

export const uiComponent = new UIComponent();
