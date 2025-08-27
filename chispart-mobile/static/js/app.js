/**
 * Chispart Mobile - Aplicación JavaScript Principal
 * Maneja la interfaz de usuario, chat, configuración y funcionalidades PWA
 */

class ChispartMobile {
    constructor() {
        this.config = {};
        this.currentAPI = 'blackbox';
        this.currentModel = 'blackboxai/openai/gpt-3.5-turbo';
        this.isOnline = navigator.onLine;
        this.chatHistory = [];
        this.pendingMessages = [];
        
        this.init();
    }
    
    async init() {
        console.log('🚀 Inicializando Chispart Mobile');
        
        // Cargar configuración
        await this.loadConfig();
        
        // Configurar eventos
        this.setupEventListeners();
        
        // Inicializar interfaz
        this.initializeUI();
        
        // Configurar PWA
        this.initializePWA();
        
        // Cargar historial
        this.loadChatHistory();
        
        console.log('✅ Chispart Mobile inicializado');
    }
    
    async loadConfig() {
        try {
            const response = await fetch('/api/config');
            if (response.ok) {
                const data = await response.json();
                this.config = data.config || {};
                this.currentAPI = this.config.default_api || 'blackbox';
                this.currentModel = this.config.default_model || 'blackboxai/openai/gpt-3.5-turbo';
            }
        } catch (error) {
            console.error('Error cargando configuración:', error);
            this.config = this.getDefaultConfig();
        }
    }
    
    getDefaultConfig() {
        return {
            theme: 'dark',
            language: 'es',
            default_api: 'blackbox',
            default_model: 'blackboxai/openai/gpt-3.5-turbo',
            show_token_usage: true,
            compact_mode: false,
            animations_enabled: true,
            offline_mode: false,
            notifications_enabled: true,
            is_mobile: /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
        };
    }
    
    setupEventListeners() {
        // Eventos de conexión
        window.addEventListener('online', () => this.handleOnline());
        window.addEventListener('offline', () => this.handleOffline());
        
        // Eventos de formularios
        const chatForm = document.getElementById('chat-form');
        if (chatForm) {
            chatForm.addEventListener('submit', (e) => this.handleChatSubmit(e));
        }
        
        const imageForm = document.getElementById('image-form');
        if (imageForm) {
            imageForm.addEventListener('submit', (e) => this.handleImageSubmit(e));
        }
        
        const configForm = document.getElementById('config-form');
        if (configForm) {
            configForm.addEventListener('submit', (e) => this.handleConfigSubmit(e));
        }
        
        // Eventos de botones
        document.addEventListener('click', (e) => {
            if (e.target.matches('.clear-chat')) {
                this.clearChat();
            } else if (e.target.matches('.toggle-theme')) {
                this.toggleTheme();
            } else if (e.target.matches('.api-selector')) {
                this.selectAPI(e.target.dataset.api);
            } else if (e.target.matches('.model-selector')) {
                this.selectModel(e.target.dataset.model);
            } else if (e.target.matches('.copy-response')) {
                this.copyToClipboard(e.target.dataset.content);
            }
        });
        
        // Eventos de archivos
        const fileInput = document.getElementById('image-input');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        }
        
        // Eventos de teclado
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                if (e.key === 'Enter') {
                    const activeForm = document.querySelector('form:focus-within');
                    if (activeForm) {
                        activeForm.dispatchEvent(new Event('submit'));
                    }
                } else if (e.key === 'k') {
                    e.preventDefault();
                    this.focusMessageInput();
                }
            }
        });
    }
    
    initializeUI() {
        // Aplicar tema
        this.applyTheme(this.config.theme || 'dark');
        
        // Configurar modo compacto
        if (this.config.compact_mode) {
            document.body.classList.add('compact-mode');
        }
        
        // Configurar animaciones
        if (!this.config.animations_enabled) {
            document.body.classList.add('no-animations');
        }
        
        // Configurar interfaz móvil
        if (this.config.is_mobile) {
            document.body.classList.add('mobile-device');
        }
        
        // Inicializar selectores
        this.updateAPISelector();
        this.updateModelSelector();
        
        // Mostrar estado de conexión
        this.updateConnectionStatus();
    }
    
    initializePWA() {
        // El PWA manager se inicializa automáticamente
        // Aquí configuramos la integración con la UI
        
        // Botón de instalación
        const installBtn = document.getElementById('install-btn');
        if (installBtn) {
            installBtn.style.display = 'none'; // Se mostrará cuando esté disponible
        }
        
        // Configurar notificaciones
        if (this.config.notifications_enabled && 'Notification' in window) {
            this.requestNotificationPermission();
        }
    }
    
    async handleChatSubmit(e) {
        e.preventDefault();
        
        const messageInput = document.getElementById('message-input');
        const message = messageInput.value.trim();
        
        if (!message) return;
        
        // Limpiar input
        messageInput.value = '';
        
        // Mostrar mensaje del usuario
        this.addMessageToChat('user', message);
        
        // Mostrar indicador de carga
        const loadingId = this.showLoadingMessage();
        
        try {
            const response = await this.sendChatMessage(message);
            
            // Remover indicador de carga
            this.removeLoadingMessage(loadingId);
            
            if (response.error) {
                this.addMessageToChat('error', response.error);
                
                if (response.requires_setup) {
                    this.showAPISetupPrompt();
                }
            } else {
                this.addMessageToChat('assistant', response.response, {
                    model: response.model_used,
                    api: response.api_used,
                    usage: response.usage
                });
                
                // Guardar en historial
                this.chatHistory.push({
                    user: message,
                    assistant: response.response,
                    timestamp: response.timestamp,
                    model: response.model_used,
                    api: response.api_used,
                    usage: response.usage
                });
                
                this.saveChatHistory();
            }
        } catch (error) {
            this.removeLoadingMessage(loadingId);
            
            if (!this.isOnline) {
                // Guardar mensaje para sincronizar después
                this.addToPendingMessages({
                    type: 'chat',
                    message: message,
                    timestamp: new Date().toISOString()
                });
                
                this.addMessageToChat('info', '📱 Mensaje guardado. Se enviará cuando haya conexión.');
            } else {
                this.addMessageToChat('error', `Error: ${error.message}`);
            }
        }
    }
    
    async sendChatMessage(message) {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                api: this.currentAPI,
                model: this.currentModel,
                stream: false
            })
        });
        
        return await response.json();
    }
    
    async handleImageSubmit(e) {
        e.preventDefault();
        
        const fileInput = document.getElementById('image-input');
        const promptInput = document.getElementById('image-prompt');
        const file = fileInput.files[0];
        const prompt = promptInput.value.trim() || '¿Qué hay en esta imagen?';
        
        if (!file) {
            this.showNotification('Por favor selecciona una imagen', 'warning');
            return;
        }
        
        // Validar archivo
        if (!this.isValidImageFile(file)) {
            this.showNotification('Formato de imagen no válido. Use JPG, PNG o WebP.', 'error');
            return;
        }
        
        // Validar tamaño
        const maxSize = this.config.is_mobile ? 10 * 1024 * 1024 : 20 * 1024 * 1024;
        if (file.size > maxSize) {
            const maxSizeMB = this.config.is_mobile ? '10MB' : '20MB';
            this.showNotification(`Imagen demasiado grande. Máximo: ${maxSizeMB}`, 'error');
            return;
        }
        
        // Mostrar preview
        this.showImagePreview(file, prompt);
        
        // Mostrar indicador de carga
        const loadingId = this.showLoadingMessage('Analizando imagen...');
        
        try {
            const formData = new FormData();
            formData.append('image', file);
            formData.append('prompt', prompt);
            formData.append('api', this.currentAPI);
            formData.append('model', this.currentModel);
            
            const response = await fetch('/api/image', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            this.removeLoadingMessage(loadingId);
            
            if (result.error) {
                this.addMessageToChat('error', result.error);
            } else {
                this.addMessageToChat('assistant', result.response, {
                    model: result.model_used,
                    api: result.api_used,
                    usage: result.usage,
                    image: file.name
                });
            }
            
            // Limpiar formulario
            fileInput.value = '';
            promptInput.value = '';
            
        } catch (error) {
            this.removeLoadingMessage(loadingId);
            this.addMessageToChat('error', `Error procesando imagen: ${error.message}`);
        }
    }
    
    async handleConfigSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const config = {};
        
        for (const [key, value] of formData.entries()) {
            config[key] = value;
        }
        
        try {
            const response = await fetch('/api/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ config })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('Configuración guardada correctamente', 'success');
                this.config = { ...this.config, ...config };
                this.applyConfig();
            } else {
                this.showNotification('Error guardando configuración', 'error');
            }
        } catch (error) {
            this.showNotification(`Error: ${error.message}`, 'error');
        }
    }
    
    addMessageToChat(role, content, metadata = {}) {
        const chatContainer = document.getElementById('chat-messages');
        if (!chatContainer) return;
        
        const messageEl = document.createElement('div');
        messageEl.className = `message message-${role}`;
        
        let messageHTML = '';
        
        if (role === 'user') {
            messageHTML = `
                <div class="message-header">
                    <span class="message-role">👤 Tú</span>
                    <span class="message-time">${this.formatTime(new Date())}</span>
                </div>
                <div class="message-content">${this.escapeHTML(content)}</div>
            `;
        } else if (role === 'assistant') {
            messageHTML = `
                <div class="message-header">
                    <span class="message-role">🤖 ${metadata.api || 'IA'}</span>
                    <span class="message-model">${metadata.model || ''}</span>
                    <span class="message-time">${this.formatTime(new Date())}</span>
                    <button class="copy-response" data-content="${this.escapeHTML(content)}" title="Copiar respuesta">📋</button>
                </div>
                <div class="message-content">${this.formatResponse(content)}</div>
                ${metadata.usage ? this.formatUsageInfo(metadata.usage) : ''}
                ${metadata.image ? `<div class="message-image">📷 ${metadata.image}</div>` : ''}
            `;
        } else if (role === 'error') {
            messageHTML = `
                <div class="message-header">
                    <span class="message-role">❌ Error</span>
                    <span class="message-time">${this.formatTime(new Date())}</span>
                </div>
                <div class="message-content">${this.escapeHTML(content)}</div>
            `;
        } else if (role === 'info') {
            messageHTML = `
                <div class="message-header">
                    <span class="message-role">ℹ️ Info</span>
                    <span class="message-time">${this.formatTime(new Date())}</span>
                </div>
                <div class="message-content">${this.escapeHTML(content)}</div>
            `;
        }
        
        messageEl.innerHTML = messageHTML;
        chatContainer.appendChild(messageEl);
        
        // Scroll al final
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
        // Animación de entrada
        if (this.config.animations_enabled) {
            messageEl.style.opacity = '0';
            messageEl.style.transform = 'translateY(20px)';
            
            requestAnimationFrame(() => {
                messageEl.style.transition = 'opacity 0.3s, transform 0.3s';
                messageEl.style.opacity = '1';
                messageEl.style.transform = 'translateY(0)';
            });
        }
    }
    
    showLoadingMessage(text = 'Procesando...') {
        const loadingId = 'loading-' + Date.now();
        const chatContainer = document.getElementById('chat-messages');
        
        if (chatContainer) {
            const loadingEl = document.createElement('div');
            loadingEl.id = loadingId;
            loadingEl.className = 'message message-loading';
            loadingEl.innerHTML = `
                <div class="message-header">
                    <span class="message-role">⏳ ${text}</span>
                </div>
                <div class="message-content">
                    <div class="loading-dots">
                        <span></span><span></span><span></span>
                    </div>
                </div>
            `;
            
            chatContainer.appendChild(loadingEl);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        return loadingId;
    }
    
    removeLoadingMessage(loadingId) {
        const loadingEl = document.getElementById(loadingId);
        if (loadingEl) {
            loadingEl.remove();
        }
    }
    
    formatResponse(content) {
        // Formatear código
        content = content.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
            return `<pre><code class="language-${lang || 'text'}">${this.escapeHTML(code.trim())}</code></pre>`;
        });
        
        // Formatear código inline
        content = content.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        // Formatear enlaces
        content = content.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>');
        
        // Formatear saltos de línea
        content = content.replace(/\n/g, '<br>');
        
        return content;
    }
    
    formatUsageInfo(usage) {
        if (!this.config.show_token_usage || !usage) return '';
        
        return `
            <div class="usage-info">
                <small>
                    📊 Tokens: ${usage.prompt_tokens || 0} + ${usage.completion_tokens || 0} = ${usage.total_tokens || 0}
                    ${usage.cost ? ` | 💰 $${usage.cost}` : ''}
                </small>
            </div>
        `;
    }
    
    formatTime(date) {
        return date.toLocaleTimeString('es-ES', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    escapeHTML(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    isValidImageFile(file) {
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
        return validTypes.includes(file.type);
    }
    
    showImagePreview(file, prompt) {
        const reader = new FileReader();
        reader.onload = (e) => {
            this.addMessageToChat('user', `📷 ${file.name}\n💬 ${prompt}`, { image: true });
        };
        reader.readAsDataURL(file);
    }
    
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showNotification('Copiado al portapapeles', 'success');
        } catch (error) {
            // Fallback para navegadores sin soporte
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            this.showNotification('Copiado al portapapeles', 'success');
        }
    }
    
    clearChat() {
        const chatContainer = document.getElementById('chat-messages');
        if (chatContainer) {
            chatContainer.innerHTML = '';
        }
        
        this.chatHistory = [];
        this.saveChatHistory();
        this.showNotification('Chat limpiado', 'info');
    }
    
    toggleTheme() {
        const currentTheme = this.config.theme || 'dark';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        this.config.theme = newTheme;
        this.applyTheme(newTheme);
        this.saveConfig();
    }
    
    applyTheme(theme) {
        document.body.className = document.body.className.replace(/theme-\w+/g, '');
        document.body.classList.add(`theme-${theme}`);
    }
    
    applyConfig() {
        this.applyTheme(this.config.theme || 'dark');
        
        if (this.config.compact_mode) {
            document.body.classList.add('compact-mode');
        } else {
            document.body.classList.remove('compact-mode');
        }
        
        if (!this.config.animations_enabled) {
            document.body.classList.add('no-animations');
        } else {
            document.body.classList.remove('no-animations');
        }
    }
    
    selectAPI(api) {
        this.currentAPI = api;
        this.updateAPISelector();
        this.updateModelSelector();
    }
    
    selectModel(model) {
        this.currentModel = model;
        this.updateModelSelector();
    }
    
    updateAPISelector() {
        const selectors = document.querySelectorAll('.api-selector');
        selectors.forEach(selector => {
            selector.classList.toggle('active', selector.dataset.api === this.currentAPI);
        });
    }
    
    updateModelSelector() {
        const selectors = document.querySelectorAll('.model-selector');
        selectors.forEach(selector => {
            selector.classList.toggle('active', selector.dataset.model === this.currentModel);
        });
    }
    
    updateConnectionStatus() {
        const statusEl = document.getElementById('connection-status');
        if (statusEl) {
            statusEl.className = `connection-status ${this.isOnline ? 'online' : 'offline'}`;
            statusEl.textContent = this.isOnline ? '🟢 Conectado' : '🔴 Sin conexión';
        }
    }
    
    handleOnline() {
        this.isOnline = true;
        this.updateConnectionStatus();
        this.processPendingMessages();
        this.showNotification('Conexión restaurada', 'success');
    }
    
    handleOffline() {
        this.isOnline = false;
        this.updateConnectionStatus();
        this.showNotification('Sin conexión - Modo offline activado', 'warning');
    }
    
    addToPendingMessages(message) {
        this.pendingMessages.push(message);
        localStorage.setItem('chispart-pending-messages', JSON.stringify(this.pendingMessages));
    }
    
    async processPendingMessages() {
        if (this.pendingMessages.length === 0) return;
        
        const messages = [...this.pendingMessages];
        this.pendingMessages = [];
        
        for (const message of messages) {
            try {
                if (message.type === 'chat') {
                    await this.sendChatMessage(message.message);
                }
            } catch (error) {
                // Volver a agregar a pendientes si falla
                this.pendingMessages.push(message);
            }
        }
        
        localStorage.setItem('chispart-pending-messages', JSON.stringify(this.pendingMessages));
    }
    
    loadChatHistory() {
        try {
            const saved = localStorage.getItem('chispart-chat-history');
            if (saved) {
                this.chatHistory = JSON.parse(saved);
                this.displayChatHistory();
            }
        } catch (error) {
            console.error('Error cargando historial:', error);
        }
        
        // Cargar mensajes pendientes
        try {
            const pending = localStorage.getItem('chispart-pending-messages');
            if (pending) {
                this.pendingMessages = JSON.parse(pending);
            }
        } catch (error) {
            console.error('Error cargando mensajes pendientes:', error);
        }
    }
    
    saveChatHistory() {
        try {
            localStorage.setItem('chispart-chat-history', JSON.stringify(this.chatHistory));
        } catch (error) {
            console.error('Error guardando historial:', error);
        }
    }
    
    saveConfig() {
        try {
            localStorage.setItem('chispart-config', JSON.stringify(this.config));
        } catch (error) {
            console.error('Error guardando configuración:', error);
        }
    }
    
    displayChatHistory() {
        const chatContainer = document.getElementById('chat-messages');
        if (!chatContainer || this.chatHistory.length === 0) return;
        
        // Mostrar últimos 10 mensajes del historial
        const recentHistory = this.chatHistory.slice(-10);
        
        recentHistory.forEach(entry => {
            this.addMessageToChat('user', entry.user);
            this.addMessageToChat('assistant', entry.assistant, {
                model: entry.model,
                api: entry.api,
                usage: entry.usage
            });
        });
    }
    
    showNotification(message, type = 'info') {
        // Crear elemento de notificación
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Agregar al DOM
        document.body.appendChild(notification);
        
        // Mostrar con animación
        requestAnimationFrame(() => {
            notification.classList.add('show');
        });
        
        // Ocultar después de 3 segundos
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
    
    showAPISetupPrompt() {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h3>🔑 Configurar API Key</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    <p>Para usar ${this.currentAPI}, necesitas configurar tu API key.</p>
                    <a href="/config" class="btn btn-primary">Ir a Configuración</a>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Eventos
        modal.querySelector('.modal-close').onclick = () => modal.remove();
        modal.onclick = (e) => {
            if (e.target === modal) modal.remove();
        };
    }
    
    focusMessageInput() {
        const input = document.getElementById('message-input');
        if (input) {
            input.focus();
        }
    }
    
    async requestNotificationPermission() {
        if (Notification.permission === 'default') {
            const permission = await Notification.requestPermission();
            console.log('Permiso de notificaciones:', permission);
        }
    }
    
    handleFileSelect(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        // Mostrar información del archivo
        const fileInfo = document.getElementById('file-info');
        if (fileInfo) {
            fileInfo.textContent = `📷 ${file.name} (${this.formatFileSize(file.size)})`;
        }
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Inicializar aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.chispartMobile = new ChispartMobile();
});

// Exportar para uso en otros módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChispartMobile;
}
