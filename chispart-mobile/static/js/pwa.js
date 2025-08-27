
// Chispart Mobile PWA JavaScript
// Manejo de instalación, actualizaciones y funcionalidades offline

class ChispartPWA {
    constructor() {
        this.swRegistration = null;
        this.deferredPrompt = null;
        this.isOnline = navigator.onLine;
        this.syncQueue = [];
        
        this.init();
    }
    
    async init() {
        console.log('[PWA] Initializing Chispart Mobile PWA');
        
        // Registrar Service Worker
        if ('serviceWorker' in navigator) {
            try {
                this.swRegistration = await navigator.serviceWorker.register('/sw.js');
                console.log('[PWA] Service Worker registered');
                
                // Escuchar actualizaciones
                this.swRegistration.addEventListener('updatefound', () => {
                    this.handleUpdate();
                });
            } catch (error) {
                console.error('[PWA] Service Worker registration failed:', error);
            }
        }
        
        // Configurar eventos
        this.setupEventListeners();
        
        // Configurar sincronización
        this.setupSync();
        
        // Verificar instalación
        this.checkInstallPrompt();
        
        // Configurar notificaciones
        this.setupNotifications();
    }
    
    setupEventListeners() {
        // Evento de instalación
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            this.deferredPrompt = e;
            this.showInstallButton();
        });
        
        // Eventos de conexión
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.handleOnline();
        });
        
        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.handleOffline();
        });
        
        // Evento de instalación completada
        window.addEventListener('appinstalled', () => {
            console.log('[PWA] App installed successfully');
            this.hideInstallButton();
        });
    }
    
    async installApp() {
        if (!this.deferredPrompt) {
            console.log('[PWA] Install prompt not available');
            return;
        }
        
        try {
            this.deferredPrompt.prompt();
            const result = await this.deferredPrompt.userChoice;
            
            if (result.outcome === 'accepted') {
                console.log('[PWA] User accepted install');
            } else {
                console.log('[PWA] User dismissed install');
            }
            
            this.deferredPrompt = null;
        } catch (error) {
            console.error('[PWA] Install error:', error);
        }
    }
    
    showInstallButton() {
        const installBtn = document.getElementById('install-btn');
        if (installBtn) {
            installBtn.style.display = 'block';
            installBtn.onclick = () => this.installApp();
        }
    }
    
    hideInstallButton() {
        const installBtn = document.getElementById('install-btn');
        if (installBtn) {
            installBtn.style.display = 'none';
        }
    }
    
    handleUpdate() {
        const newWorker = this.swRegistration.installing;
        
        newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                this.showUpdateNotification();
            }
        });
    }
    
    showUpdateNotification() {
        const updateBanner = document.createElement('div');
        updateBanner.className = 'update-banner';
        updateBanner.innerHTML = `
            <div class="update-content">
                <span>🔄 Nueva versión disponible</span>
                <button onclick="window.location.reload()" class="update-btn">Actualizar</button>
            </div>
        `;
        
        document.body.appendChild(updateBanner);
        
        // Auto-ocultar después de 10 segundos
        setTimeout(() => {
            updateBanner.remove();
        }, 10000);
    }
    
    handleOnline() {
        console.log('[PWA] Connection restored');
        
        // Mostrar indicador de conexión
        this.showConnectionStatus('online');
        
        // Procesar cola de sincronización
        this.processSyncQueue();
        
        // Ocultar indicador después de 3 segundos
        setTimeout(() => {
            this.hideConnectionStatus();
        }, 3000);
    }
    
    handleOffline() {
        console.log('[PWA] Connection lost');
        this.showConnectionStatus('offline');
    }
    
    showConnectionStatus(status) {
        let statusEl = document.getElementById('connection-status');
        
        if (!statusEl) {
            statusEl = document.createElement('div');
            statusEl.id = 'connection-status';
            statusEl.className = 'connection-status';
            document.body.appendChild(statusEl);
        }
        
        statusEl.className = `connection-status ${status}`;
        statusEl.textContent = status === 'online' ? 
            '🟢 Conectado' : '🔴 Sin conexión';
        statusEl.style.display = 'block';
    }
    
    hideConnectionStatus() {
        const statusEl = document.getElementById('connection-status');
        if (statusEl) {
            statusEl.style.display = 'none';
        }
    }
    
    setupSync() {
        // Configurar sincronización en segundo plano
        if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
            console.log('[PWA] Background sync available');
        }
    }
    
    async addToSyncQueue(data) {
        this.syncQueue.push({
            ...data,
            timestamp: Date.now(),
            id: this.generateId()
        });
        
        // Guardar en localStorage
        localStorage.setItem('chispart-sync-queue', JSON.stringify(this.syncQueue));
        
        // Intentar sincronizar si está online
        if (this.isOnline) {
            this.processSyncQueue();
        }
    }
    
    async processSyncQueue() {
        if (this.syncQueue.length === 0) return;
        
        console.log('[PWA] Processing sync queue:', this.syncQueue.length, 'items');
        
        const itemsToSync = [...this.syncQueue];
        this.syncQueue = [];
        
        for (const item of itemsToSync) {
            try {
                const response = await fetch('/api/pwa/sync', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(item)
                });
                
                if (!response.ok) {
                    // Volver a agregar a la cola si falla
                    this.syncQueue.push(item);
                }
            } catch (error) {
                console.error('[PWA] Sync error:', error);
                this.syncQueue.push(item);
            }
        }
        
        // Actualizar localStorage
        localStorage.setItem('chispart-sync-queue', JSON.stringify(this.syncQueue));
    }
    
    async setupNotifications() {
        if (!('Notification' in window)) {
            console.log('[PWA] Notifications not supported');
            return;
        }
        
        if (Notification.permission === 'default') {
            const permission = await Notification.requestPermission();
            console.log('[PWA] Notification permission:', permission);
        }
    }
    
    async showNotification(title, options = {}) {
        if (Notification.permission !== 'granted') return;
        
        const defaultOptions = {
            icon: '/static/icons/icon-192x192.png',
            badge: '/static/icons/badge-72x72.png',
            vibrate: [200, 100, 200],
            ...options
        };
        
        if (this.swRegistration && this.swRegistration.showNotification) {
            return this.swRegistration.showNotification(title, defaultOptions);
        } else {
            return new Notification(title, defaultOptions);
        }
    }
    
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }
    
    checkInstallPrompt() {
        // Verificar si ya está instalado
        if (window.matchMedia('(display-mode: standalone)').matches) {
            console.log('[PWA] App is running in standalone mode');
            document.body.classList.add('standalone');
        }
    }
    
    // Métodos públicos para la aplicación
    async saveOfflineData(key, data) {
        try {
            localStorage.setItem(`chispart-offline-${key}`, JSON.stringify(data));
            return true;
        } catch (error) {
            console.error('[PWA] Error saving offline data:', error);
            return false;
        }
    }
    
    getOfflineData(key) {
        try {
            const data = localStorage.getItem(`chispart-offline-${key}`);
            return data ? JSON.parse(data) : null;
        } catch (error) {
            console.error('[PWA] Error getting offline data:', error);
            return null;
        }
    }
    
    clearOfflineData(key) {
        try {
            localStorage.removeItem(`chispart-offline-${key}`);
            return true;
        } catch (error) {
            console.error('[PWA] Error clearing offline data:', error);
            return false;
        }
    }
}

// Inicializar PWA cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.chispartPWA = new ChispartPWA();
});

// Exportar para uso en otros módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChispartPWA;
}
