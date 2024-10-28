class Logger {
    constructor() {
        // 使用 localStorage 或自定义标志来控制调试模式
        this.debugMode = localStorage.getItem('debug') === 'true' || window.location.hostname === 'localhost';
    }

    info(message, ...args) {
        if (this.debugMode) {
            console.log(`[INFO] ${message}`, ...args);
        }
    }

    warn(message, ...args) {
        if (this.debugMode) {
            console.warn(`[WARN] ${message}`, ...args);
        }
    }

    error(message, ...args) {
        console.error(`[ERROR] ${message}`, ...args);
    }

    debug(message, ...args) {
        if (this.debugMode) {
            console.debug(`[DEBUG] ${message}`, ...args);
        }
    }

    // 添加一个方法来切换调试模式
    toggleDebug() {
        this.debugMode = !this.debugMode;
        localStorage.setItem('debug', this.debugMode);
        console.log(`Debug mode ${this.debugMode ? 'enabled' : 'disabled'}`);
    }
}

export const logger = new Logger();
