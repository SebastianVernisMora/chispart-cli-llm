/**
 * Chispart Mobile - Utilidades JavaScript
 * Funciones auxiliares y utilidades compartidas
 */

// Utilidades de validación
const Validators = {
    /**
     * Valida si un email es válido
     */
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },
    
    /**
     * Valida si una URL es válida
     */
    isValidURL(url) {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    },
    
    /**
     * Valida si una API key tiene formato válido
     */
    isValidAPIKey(key, provider) {
        if (!key || typeof key !== 'string') return false;
        
        const patterns = {
            openai: /^sk-[a-zA-Z0-9]{48,}$/,
            anthropic: /^sk-ant-[a-zA-Z0-9\-_]{95,}$/,
            groq: /^gsk_[a-zA-Z0-9]{52}$/,
            together: /^[a-f0-9]{64}$/,
            blackbox: /^[a-zA-Z0-9\-_]{20,}$/
        };
        
        const pattern = patterns[provider];
        return pattern ? pattern.test(key) : key.length >= 10;
    },
    
    /**
     * Valida archivos de imagen
     */
    isValidImageFile(file) {
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/gif'];
        const maxSize = 20 * 1024 * 1024; // 20MB
        
        return validTypes.includes(file.type) && file.size <= maxSize;
    },
    
    /**
     * Valida archivos PDF
     */
    isValidPDFFile(file) {
        const maxSize = 50 * 1024 * 1024; // 50MB
        return file.type === 'application/pdf' && file.size <= maxSize;
    }
};

// Utilidades de formato
const Formatters = {
    /**
     * Formatea el tamaño de archivo
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    /**
     * Formatea fecha y hora
     */
    formatDateTime(date, options = {}) {
        const defaultOptions = {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        
        return new Intl.DateTimeFormat('es-ES', { ...defaultOptions, ...options })
            .format(new Date(date));
    },
    
    /**
     * Formatea tiempo relativo (hace X minutos)
     */
    formatRelativeTime(date) {
        const now = new Date();
        const diff = now - new Date(date);
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);
        
        if (seconds < 60) return 'hace unos segundos';
        if (minutes < 60) return `hace ${minutes} minuto${minutes !== 1 ? 's' : ''}`;
        if (hours < 24) return `hace ${hours} hora${hours !== 1 ? 's' : ''}`;
        if (days < 7) return `hace ${days} día${days !== 1 ? 's' : ''}`;
        
        return this.formatDateTime(date, { year: 'numeric', month: 'short', day: 'numeric' });
    },
    
    /**
     * Formatea números con separadores de miles
     */
    formatNumber(number) {
        return new Intl.NumberFormat('es-ES').format(number);
    },
    
    /**
     * Formatea texto para mostrar en UI (truncar, etc.)
     */
    formatText(text, maxLength = 100) {
        if (!text) return '';
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    },
    
    /**
     * Formatea código para resaltado de sintaxis
     */
    formatCode(code, language = 'text') {
        // Escapar HTML
        const escaped = code
            .replace(/&/g, '&amp;')
            .replace(/</g, '<')
            .replace(/>/g, '>')
            .replace(/"/g, '"')
            .replace(/'/g, '&#39;');
        
        return `<pre><code class="language-${language}">${escaped}</code></pre>`;
    },
    
    /**
     * Formatea markdown básico
     */
    formatMarkdown(text) {
        return text
            // Código en bloque
            .replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
                return this.formatCode(code.trim(), lang || 'text');
            })
            // Código inline
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            // Enlaces
            .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
            // URLs automáticas
            .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>')
            // Negrita
            .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
            // Cursiva
            .replace(/\*([^*]+)\*/g, '<em>$1</em>')
            // Saltos de línea
            .replace(/\n/g, '<br>');
    }
};

// Utilidades de almacenamiento
const Storage = {
    /**
     * Guarda datos en localStorage con manejo de errores
     */
    set(key, value) {
        try {
            const serialized = JSON.stringify(value);
            localStorage.setItem(`chispart_${key}`, serialized);
            return true;
        } catch (error) {
            console.error('Error guardando en localStorage:', error);
            return false;
        }
    },
    
    /**
     * Obtiene datos de localStorage
     */
    get(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(`chispart_${key}`);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('Error leyendo de localStorage:', error);
            return defaultValue;
        }
    },
    
    /**
     * Elimina datos de localStorage
     */
    remove(key) {
        try {
            localStorage.removeItem(`chispart_${key}`);
            return true;
        } catch (error) {
            console.error('Error eliminando de localStorage:', error);
            return false;
        }
    },
    
    /**
     * Limpia todos los datos de Chispart
     */
    clear() {
        try {
            const keys = Object.keys(localStorage);
            keys.forEach(key => {
                if (key.startsWith('chispart_')) {
                    localStorage.removeItem(key);
                }
            });
            return true;
        } catch (error) {
            console.error('Error limpiando localStorage:', error);
            return false;
        }
    },
    
    /**
     * Obtiene el tamaño usado en localStorage
     */
    getUsage() {
        let total = 0;
        const keys = Object.keys(localStorage);
        
        keys.forEach(key => {
            if (key.startsWith('chispart_')) {
                total += localStorage.getItem(key).length;
            }
        });
        
        return total;
    }
};

// Utilidades de red
const Network = {
    /**
     * Verifica si hay conexión a internet
     */
    isOnline() {
        return navigator.onLine;
    },
    
    /**
     * Hace una petición HTTP con reintentos
     */
    async fetchWithRetry(url, options = {}, maxRetries = 3) {
        let lastError;
        
        for (let i = 0; i <= maxRetries; i++) {
            try {
                const response = await fetch(url, {
                    ...options,
                    timeout: 10000 // 10 segundos
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                return response;
            } catch (error) {
                lastError = error;
                
                if (i < maxRetries) {
                    // Esperar antes del siguiente intento (backoff exponencial)
                    await this.delay(Math.pow(2, i) * 1000);
                }
            }
        }
        
        throw lastError;
    },
    
    /**
     * Verifica la latencia de red
     */
    async checkLatency() {
        const start = performance.now();
        
        try {
            await fetch('/api/ping', { method: 'HEAD' });
            return performance.now() - start;
        } catch (error) {
            return -1; // Error de conexión
        }
    },
    
    /**
     * Espera un tiempo determinado
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
};

// Utilidades de dispositivo
const Device = {
    /**
     * Detecta si es un dispositivo móvil
     */
    isMobile() {
        return /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    },
    
    /**
     * Detecta si es Termux
     */
    isTermux() {
        return navigator.userAgent.includes('Termux') || 
               window.location.hostname === 'localhost' && this.isMobile();
    },
    
    /**
     * Obtiene información del dispositivo
     */
    getInfo() {
        return {
            userAgent: navigator.userAgent,
            platform: navigator.platform,
            language: navigator.language,
            cookieEnabled: navigator.cookieEnabled,
            onLine: navigator.onLine,
            screen: {
                width: screen.width,
                height: screen.height,
                colorDepth: screen.colorDepth
            },
            viewport: {
                width: window.innerWidth,
                height: window.innerHeight
            },
            isMobile: this.isMobile(),
            isTermux: this.isTermux()
        };
    },
    
    /**
     * Detecta capacidades del dispositivo
     */
    getCapabilities() {
        return {
            serviceWorker: 'serviceWorker' in navigator,
            pushNotifications: 'PushManager' in window,
            backgroundSync: 'serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype,
            webShare: 'share' in navigator,
            clipboard: 'clipboard' in navigator,
            geolocation: 'geolocation' in navigator,
            camera: 'mediaDevices' in navigator && 'getUserMedia' in navigator.mediaDevices,
            vibration: 'vibrate' in navigator,
            fullscreen: 'requestFullscreen' in document.documentElement,
            wakeLock: 'wakeLock' in navigator
        };
    }
};

// Utilidades de UI
const UI = {
    /**
     * Muestra una notificación toast
     */
    showToast(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        // Estilos inline para asegurar visibilidad
        Object.assign(toast.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '12px 20px',
            borderRadius: '8px',
            color: 'white',
            fontWeight: '500',
            zIndex: '10000',
            transform: 'translateX(100%)',
            transition: 'transform 0.3s ease',
            maxWidth: '300px',
            wordWrap: 'break-word'
        });
        
        // Colores por tipo
        const colors = {
            info: '#2196F3',
            success: '#4CAF50',
            warning: '#FF9800',
            error: '#F44336'
        };
        
        toast.style.backgroundColor = colors[type] || colors.info;
        
        document.body.appendChild(toast);
        
        // Mostrar con animación
        requestAnimationFrame(() => {
            toast.style.transform = 'translateX(0)';
        });
        
        // Ocultar después del tiempo especificado
        setTimeout(() => {
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, duration);
        
        return toast;
    },
    
    /**
     * Muestra un modal de confirmación
     */
    showConfirm(message, title = 'Confirmar') {
        return new Promise((resolve) => {
            const modal = document.createElement('div');
            modal.className = 'modal-overlay';
            modal.innerHTML = `
                <div class="modal confirm-modal">
                    <div class="modal-header">
                        <h3>${title}</h3>
                    </div>
                    <div class="modal-body">
                        <p>${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary cancel-btn">Cancelar</button>
                        <button class="btn btn-primary confirm-btn">Confirmar</button>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            
            // Eventos
            modal.querySelector('.cancel-btn').onclick = () => {
                modal.remove();
                resolve(false);
            };
            
            modal.querySelector('.confirm-btn').onclick = () => {
                modal.remove();
                resolve(true);
            };
            
            modal.onclick = (e) => {
                if (e.target === modal) {
                    modal.remove();
                    resolve(false);
                }
            };
        });
    },
    
    /**
     * Muestra un loading overlay
     */
    showLoading(message = 'Cargando...') {
        const loading = document.createElement('div');
        loading.className = 'loading-overlay';
        loading.innerHTML = `
            <div class="loading-content">
                <div class="loading-spinner"></div>
                <p>${message}</p>
            </div>
        `;
        
        document.body.appendChild(loading);
        return loading;
    },
    
    /**
     * Oculta el loading overlay
     */
    hideLoading(loadingElement) {
        if (loadingElement && loadingElement.parentNode) {
            loadingElement.parentNode.removeChild(loadingElement);
        }
    },
    
    /**
     * Copia texto al portapapeles
     */
    async copyToClipboard(text) {
        try {
            if (navigator.clipboard && window.isSecureContext) {
                await navigator.clipboard.writeText(text);
                return true;
            } else {
                // Fallback para navegadores sin soporte
                const textArea = document.createElement('textarea');
                textArea.value = text;
                textArea.style.position = 'fixed';
                textArea.style.left = '-999999px';
                textArea.style.top = '-999999px';
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                
                const result = document.execCommand('copy');
                document.body.removeChild(textArea);
                return result;
            }
        } catch (error) {
            console.error('Error copiando al portapapeles:', error);
            return false;
        }
    },
    
    /**
     * Hace scroll suave a un elemento
     */
    scrollToElement(element, offset = 0) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        
        if (element) {
            const elementPosition = element.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - offset;
            
            window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth'
            });
        }
    },
    
    /**
     * Detecta si un elemento está visible en el viewport
     */
    isElementVisible(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }
};

// Utilidades de archivos
const Files = {
    /**
     * Lee un archivo como texto
     */
    readAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(e);
            reader.readAsText(file);
        });
    },
    
    /**
     * Lee un archivo como Data URL
     */
    readAsDataURL(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(e);
            reader.readAsDataURL(file);
        });
    },
    
    /**
     * Descarga un archivo
     */
    download(data, filename, type = 'text/plain') {
        const blob = new Blob([data], { type });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    },
    
    /**
     * Comprime una imagen
     */
    compressImage(file, maxWidth = 1920, maxHeight = 1080, quality = 0.8) {
        return new Promise((resolve) => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const img = new Image();
            
            img.onload = () => {
                // Calcular nuevas dimensiones
                let { width, height } = img;
                
                if (width > height) {
                    if (width > maxWidth) {
                        height = (height * maxWidth) / width;
                        width = maxWidth;
                    }
                } else {
                    if (height > maxHeight) {
                        width = (width * maxHeight) / height;
                        height = maxHeight;
                    }
                }
                
                canvas.width = width;
                canvas.height = height;
                
                // Dibujar imagen redimensionada
                ctx.drawImage(img, 0, 0, width, height);
                
                // Convertir a blob
                canvas.toBlob(resolve, file.type, quality);
            };
            
            img.src = URL.createObjectURL(file);
        });
    }
};

// Utilidades de seguridad
const Security = {
    /**
     * Escapa HTML para prevenir XSS
     */
    escapeHTML(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },
    
    /**
     * Sanitiza una URL
     */
    sanitizeURL(url) {
        try {
            const parsed = new URL(url);
            // Solo permitir HTTP y HTTPS
            if (!['http:', 'https:'].includes(parsed.protocol)) {
                return null;
            }
            return parsed.toString();
        } catch {
            return null;
        }
    },
    
    /**
     * Genera un ID único
     */
    generateId(prefix = 'id') {
        return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    },
    
    /**
     * Hash simple para strings
     */
    simpleHash(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convertir a 32bit integer
        }
        return hash.toString(36);
    }
};

// Utilidades de debug
const Debug = {
    /**
     * Log con timestamp
     */
    log(...args) {
        if (window.location.hostname === 'localhost' || window.location.search.includes('debug=true')) {
            console.log(`[${new Date().toISOString()}]`, ...args);
        }
    },
    
    /**
     * Mide el tiempo de ejecución de una función
     */
    async measureTime(fn, label = 'Function') {
        const start = performance.now();
        const result = await fn();
        const end = performance.now();
        this.log(`${label} took ${(end - start).toFixed(2)}ms`);
        return result;
    },
    
    /**
     * Obtiene información de rendimiento
     */
    getPerformanceInfo() {
        if ('performance' in window) {
            const navigation = performance.getEntriesByType('navigation')[0];
            return {
                loadTime: navigation.loadEventEnd - navigation.loadEventStart,
                domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
                firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime || 0,
                firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0
            };
        }
        return null;
    }
};

// Exportar utilidades
window.ChispartUtils = {
    Validators,
    Formatters,
    Storage,
    Network,
    Device,
    UI,
    Files,
    Security,
    Debug,
    
    // Función de inicialización
    init() {
        console.log('[ChispartUtils] Inicializando utilidades');
        
        // Configurar eventos globales
        this.setupGlobalEvents();
        
        // Inicializar debug si está en modo desarrollo
        if (window.location.hostname === 'localhost' || window.location.search.includes('debug=true')) {
            this.Debug.log('ChispartUtils inicializado en modo debug');
        }
        
        return this;
    },
    
    // Configurar eventos globales
    setupGlobalEvents() {
        // Evento para cambios de conexión
        window.addEventListener('online', () => {
            this.Debug.log('Conexión restaurada');
        });
        
        window.addEventListener('offline', () => {
            this.Debug.log('Conexión perdida');
        });
        
        // Evento para errores no capturados
        window.addEventListener('error', (e) => {
            this.Debug.log('Error no capturado:', e.error);
        });
        
        // Evento para promesas rechazadas no capturadas
        window.addEventListener('unhandledrejection', (e) => {
            this.Debug.log('Promesa rechazada no capturada:', e.reason);
        });
    }
};

// Para compatibilidad con módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        Validators,
        Formatters,
        Storage,
        Network,
        Device,
        UI,
        Files,
        Security,
        Debug
    };
}
