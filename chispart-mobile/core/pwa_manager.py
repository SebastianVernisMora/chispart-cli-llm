"""
Sistema PWA Avanzado para Chispart Mobile
Maneja Service Workers, caché offline, sincronización y notificaciones
Optimizado para dispositivos móviles y Termux
"""

import os
import json
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import asyncio
from flask import Flask, request, jsonify, render_template_string


class PWAManager:
    """
    Gestor avanzado de Progressive Web App con capacidades offline
    """

    def __init__(self, app: Flask = None, config: Dict = None):
        """
        Inicializa el gestor PWA

        Args:
            app: Instancia de Flask
            config: Configuración personalizada
        """
        self.app = app
        self.config = config or self._get_default_config()
        self.cache_version = self._generate_cache_version()
        self.offline_storage = {}

        if app:
            self.init_app(app)

    def init_app(self, app: Flask):
        """Inicializa la extensión con la app Flask"""
        self.app = app
        self._register_routes()
        self._setup_static_files()

    def _get_default_config(self) -> Dict:
        """Configuración por defecto para PWA móvil"""
        return {
            "app_name": "Chispart Mobile",
            "short_name": "Chispart",
            "description": "Universal LLM Terminal for Mobile Devices",
            "theme_color": "#00FF88",
            "background_color": "#1A1A1A",
            "display": "standalone",
            "orientation": "portrait-primary",
            "start_url": "/",
            "scope": "/",
            "cache_strategy": "cache_first",
            "offline_fallback": "/offline",
            "sync_enabled": True,
            "notifications_enabled": True,
            "install_prompt": True,
            "update_check_interval": 3600000,  # 1 hora en ms
            "max_cache_size": 50 * 1024 * 1024,  # 50MB para móviles
            "cache_expiry": 7 * 24 * 60 * 60 * 1000,  # 7 días en ms
        }

    def _generate_cache_version(self) -> str:
        """Genera versión de caché basada en contenido"""
        try:
            # Usar timestamp y hash de archivos críticos
            timestamp = str(int(datetime.now().timestamp()))

            # Hash de archivos principales
            files_to_hash = ["app.py", "static/js/app.js", "static/css/style.css"]
            file_hashes = []

            for file_path in files_to_hash:
                if os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()[:8]
                        file_hashes.append(file_hash)

            combined = timestamp + "".join(file_hashes)
            return hashlib.sha256(combined.encode()).hexdigest()[:16]

        except Exception:
            return datetime.now().strftime("%Y%m%d_%H%M%S")

    def _register_routes(self):
        """Registra rutas PWA en Flask"""

        @self.app.route("/manifest.json")
        def manifest():
            """Genera el Web App Manifest dinámicamente"""
            manifest_data = {
                "name": self.config["app_name"],
                "short_name": self.config["short_name"],
                "description": self.config["description"],
                "start_url": self.config["start_url"],
                "scope": self.config["scope"],
                "display": self.config["display"],
                "orientation": self.config["orientation"],
                "theme_color": self.config["theme_color"],
                "background_color": self.config["background_color"],
                "icons": [
                    {
                        "src": "/static/icons/icon-72x72.png",
                        "sizes": "72x72",
                        "type": "image/png",
                        "purpose": "maskable any",
                    },
                    {
                        "src": "/static/icons/icon-96x96.png",
                        "sizes": "96x96",
                        "type": "image/png",
                        "purpose": "maskable any",
                    },
                    {
                        "src": "/static/icons/icon-128x128.png",
                        "sizes": "128x128",
                        "type": "image/png",
                        "purpose": "maskable any",
                    },
                    {
                        "src": "/static/icons/icon-144x144.png",
                        "sizes": "144x144",
                        "type": "image/png",
                        "purpose": "maskable any",
                    },
                    {
                        "src": "/static/icons/icon-152x152.png",
                        "sizes": "152x152",
                        "type": "image/png",
                        "purpose": "maskable any",
                    },
                    {
                        "src": "/static/icons/icon-192x192.png",
                        "sizes": "192x192",
                        "type": "image/png",
                        "purpose": "maskable any",
                    },
                    {
                        "src": "/static/icons/icon-384x384.png",
                        "sizes": "384x384",
                        "type": "image/png",
                        "purpose": "maskable any",
                    },
                    {
                        "src": "/static/icons/icon-512x512.png",
                        "sizes": "512x512",
                        "type": "image/png",
                        "purpose": "maskable any",
                    },
                ],
                "categories": ["productivity", "utilities", "developer"],
                "lang": "es",
                "dir": "ltr",
                "prefer_related_applications": False,
                "shortcuts": [
                    {
                        "name": "Chat Rápido",
                        "short_name": "Chat",
                        "description": "Iniciar chat con IA",
                        "url": "/chat",
                        "icons": [
                            {"src": "/static/icons/chat-icon.png", "sizes": "96x96"}
                        ],
                    },
                    {
                        "name": "Analizar Imagen",
                        "short_name": "Imagen",
                        "description": "Analizar imagen con IA",
                        "url": "/image",
                        "icons": [
                            {"src": "/static/icons/image-icon.png", "sizes": "96x96"}
                        ],
                    },
                    {
                        "name": "Configuración",
                        "short_name": "Config",
                        "description": "Configurar API Keys",
                        "url": "/config",
                        "icons": [
                            {"src": "/static/icons/config-icon.png", "sizes": "96x96"}
                        ],
                    },
                ],
            }

            response = jsonify(manifest_data)
            response.headers["Content-Type"] = "application/manifest+json"
            return response

        @self.app.route("/sw.js")
        def service_worker():
            """Genera el Service Worker dinámicamente"""
            sw_content = self._generate_service_worker()
            response = self.app.response_class(
                sw_content, mimetype="application/javascript"
            )
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Service-Worker-Allowed"] = "/"
            return response

        @self.app.route("/offline")
        def offline_page():
            """Página offline para cuando no hay conexión"""
            return render_template_string(self._get_offline_template())

        @self.app.route("/api/pwa/sync", methods=["POST"])
        def sync_data():
            """Endpoint para sincronización de datos offline"""
            try:
                data = request.get_json()
                sync_type = data.get("type")
                payload = data.get("payload", {})

                if sync_type == "chat_history":
                    return self._sync_chat_history(payload)
                elif sync_type == "api_keys":
                    return self._sync_api_keys(payload)
                elif sync_type == "settings":
                    return self._sync_settings(payload)
                else:
                    return jsonify({"error": "Unknown sync type"}), 400

            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/pwa/cache-status")
        def cache_status():
            """Estado del caché PWA"""
            return jsonify(
                {
                    "cache_version": self.cache_version,
                    "last_updated": datetime.now().isoformat(),
                    "config": {
                        "max_size": self.config["max_cache_size"],
                        "expiry": self.config["cache_expiry"],
                        "strategy": self.config["cache_strategy"],
                    },
                }
            )

    def _generate_service_worker(self) -> str:
        """Genera el código del Service Worker"""
        return f"""
// Chispart Mobile Service Worker
// Versión: {self.cache_version}
// Generado automáticamente

const CACHE_NAME = 'chispart-mobile-v{self.cache_version}';
const CACHE_VERSION = '{self.cache_version}';
const MAX_CACHE_SIZE = {self.config['max_cache_size']};
const CACHE_EXPIRY = {self.config['cache_expiry']};

// Recursos críticos para caché
const CRITICAL_RESOURCES = [
    '/',
    '/static/css/style.css',
    '/static/js/app.js',
    '/static/js/pwa.js',
    '/static/icons/icon-192x192.png',
    '/offline',
    '/manifest.json'
];

// Recursos opcionales para caché
const OPTIONAL_RESOURCES = [
    '/static/css/themes.css',
    '/static/js/utils.js',
    '/static/fonts/inter.woff2'
];

// Instalación del Service Worker
self.addEventListener('install', event => {{
    console.log('[SW] Installing Service Worker v{self.cache_version}');
    
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {{
                console.log('[SW] Caching critical resources');
                return cache.addAll(CRITICAL_RESOURCES);
            }})
            .then(() => {{
                console.log('[SW] Critical resources cached');
                return self.skipWaiting();
            }})
            .catch(error => {{
                console.error('[SW] Error caching critical resources:', error);
            }})
    );
}});

// Activación del Service Worker
self.addEventListener('activate', event => {{
    console.log('[SW] Activating Service Worker v{self.cache_version}');
    
    event.waitUntil(
        caches.keys()
            .then(cacheNames => {{
                return Promise.all(
                    cacheNames.map(cacheName => {{
                        if (cacheName !== CACHE_NAME) {{
                            console.log('[SW] Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }}
                    }})
                );
            }})
            .then(() => {{
                console.log('[SW] Service Worker activated');
                return self.clients.claim();
            }})
    );
}});

// Estrategia de caché: Cache First para recursos estáticos
self.addEventListener('fetch', event => {{
    const request = event.request;
    const url = new URL(request.url);
    
    // Solo manejar requests GET
    if (request.method !== 'GET') {{
        return;
    }}
    
    // Estrategia para diferentes tipos de recursos
    if (url.pathname.startsWith('/api/')) {{
        // API calls: Network First con fallback a caché
        event.respondWith(networkFirstStrategy(request));
    }} else if (url.pathname.startsWith('/static/')) {{
        // Recursos estáticos: Cache First
        event.respondWith(cacheFirstStrategy(request));
    }} else if (url.pathname === '/' || url.pathname.startsWith('/chat') || url.pathname.startsWith('/config')) {{
        // Páginas principales: Stale While Revalidate
        event.respondWith(staleWhileRevalidateStrategy(request));
    }} else {{
        // Otros recursos: Network First
        event.respondWith(networkFirstStrategy(request));
    }}
}});

// Estrategia Cache First
async function cacheFirstStrategy(request) {{
    try {{
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {{
            return cachedResponse;
        }}
        
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {{
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, networkResponse.clone());
        }}
        
        return networkResponse;
    }} catch (error) {{
        console.error('[SW] Cache First error:', error);
        return caches.match('/offline');
    }}
}}

// Estrategia Network First
async function networkFirstStrategy(request) {{
    try {{
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {{
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, networkResponse.clone());
        }}
        
        return networkResponse;
    }} catch (error) {{
        console.log('[SW] Network failed, trying cache:', request.url);
        const cachedResponse = await caches.match(request);
        
        if (cachedResponse) {{
            return cachedResponse;
        }}
        
        // Fallback para páginas
        if (request.destination === 'document') {{
            return caches.match('/offline');
        }}
        
        throw error;
    }}
}}

// Estrategia Stale While Revalidate
async function staleWhileRevalidateStrategy(request) {{
    const cache = await caches.open(CACHE_NAME);
    const cachedResponse = await cache.match(request);
    
    const fetchPromise = fetch(request).then(networkResponse => {{
        if (networkResponse.ok) {{
            cache.put(request, networkResponse.clone());
        }}
        return networkResponse;
    }}).catch(() => cachedResponse);
    
    return cachedResponse || fetchPromise;
}}

// Sincronización en segundo plano
self.addEventListener('sync', event => {{
    console.log('[SW] Background sync:', event.tag);
    
    if (event.tag === 'chat-sync') {{
        event.waitUntil(syncChatHistory());
    }} else if (event.tag === 'settings-sync') {{
        event.waitUntil(syncSettings());
    }}
}});

// Sincronizar historial de chat
async function syncChatHistory() {{
    try {{
        const pendingChats = await getStoredData('pending-chats') || [];
        
        for (const chat of pendingChats) {{
            const response = await fetch('/api/chat', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify(chat)
            }});
            
            if (response.ok) {{
                // Remover del almacenamiento local
                await removeStoredData('pending-chats', chat.id);
            }}
        }}
    }} catch (error) {{
        console.error('[SW] Error syncing chat history:', error);
    }}
}}

// Notificaciones Push
self.addEventListener('push', event => {{
    if (!event.data) return;
    
    const data = event.data.json();
    const options = {{
        body: data.body,
        icon: '/static/icons/icon-192x192.png',
        badge: '/static/icons/badge-72x72.png',
        vibrate: [200, 100, 200],
        data: data.data || {{}},
        actions: [
            {{
                action: 'open',
                title: 'Abrir',
                icon: '/static/icons/open-icon.png'
            }},
            {{
                action: 'dismiss',
                title: 'Descartar',
                icon: '/static/icons/dismiss-icon.png'
            }}
        ]
    }};
    
    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
}});

// Manejo de clicks en notificaciones
self.addEventListener('notificationclick', event => {{
    event.notification.close();
    
    if (event.action === 'open') {{
        event.waitUntil(
            clients.openWindow(event.notification.data.url || '/')
        );
    }}
}});

// Utilidades de almacenamiento
async function getStoredData(key) {{
    const cache = await caches.open(CACHE_NAME + '-data');
    const response = await cache.match(key);
    return response ? response.json() : null;
}}

async function setStoredData(key, data) {{
    const cache = await caches.open(CACHE_NAME + '-data');
    const response = new Response(JSON.stringify(data));
    await cache.put(key, response);
}}

async function removeStoredData(key, itemId) {{
    const data = await getStoredData(key) || [];
    const filtered = data.filter(item => item.id !== itemId);
    await setStoredData(key, filtered);
}}

// Limpieza periódica de caché
async function cleanupCache() {{
    const cacheNames = await caches.keys();
    const totalSize = await getCacheSize();
    
    if (totalSize > MAX_CACHE_SIZE) {{
        console.log('[SW] Cache size exceeded, cleaning up');
        // Implementar lógica de limpieza LRU
    }}
}}

async function getCacheSize() {{
    let totalSize = 0;
    const cacheNames = await caches.keys();
    
    for (const cacheName of cacheNames) {{
        const cache = await caches.open(cacheName);
        const keys = await cache.keys();
        
        for (const key of keys) {{
            const response = await cache.match(key);
            if (response) {{
                const blob = await response.blob();
                totalSize += blob.size;
            }}
        }}
    }}
    
    return totalSize;
}}

console.log('[SW] Service Worker v{self.cache_version} loaded');
"""

    def _get_offline_template(self) -> str:
        """Template para la página offline"""
        return """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sin Conexión - Chispart Mobile</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            color: #ffffff;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
        }
        
        .offline-container {
            max-width: 400px;
            padding: 40px 20px;
        }
        
        .offline-icon {
            font-size: 4rem;
            margin-bottom: 20px;
            opacity: 0.7;
        }
        
        h1 {
            color: #00FF88;
            margin-bottom: 10px;
            font-size: 1.5rem;
        }
        
        p {
            color: #cccccc;
            line-height: 1.6;
            margin-bottom: 30px;
        }
        
        .retry-btn {
            background: linear-gradient(135deg, #00FF88 0%, #00CC6A 100%);
            color: #1a1a1a;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .retry-btn:hover {
            transform: translateY(-2px);
        }
        
        .features {
            margin-top: 40px;
            text-align: left;
        }
        
        .feature {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            color: #cccccc;
        }
        
        .feature-icon {
            margin-right: 10px;
            color: #00FF88;
        }
    </style>
</head>
<body>
    <div class="offline-container">
        <div class="offline-icon">📱</div>
        <h1>Sin Conexión a Internet</h1>
        <p>No se puede conectar a los servidores. Verifica tu conexión a internet e intenta nuevamente.</p>
        
        <button class="retry-btn" onclick="window.location.reload()">
            🔄 Reintentar
        </button>
        
        <div class="features">
            <div class="feature">
                <span class="feature-icon">✅</span>
                <span>Historial guardado localmente</span>
            </div>
            <div class="feature">
                <span class="feature-icon">✅</span>
                <span>Configuración preservada</span>
            </div>
            <div class="feature">
                <span class="feature-icon">✅</span>
                <span>Sincronización automática</span>
            </div>
        </div>
    </div>
    
    <script>
        // Intentar reconectar automáticamente
        let retryCount = 0;
        const maxRetries = 3;
        
        function checkConnection() {
            if (navigator.onLine && retryCount < maxRetries) {
                retryCount++;
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            }
        }
        
        window.addEventListener('online', checkConnection);
        
        // Verificar conexión cada 30 segundos
        setInterval(() => {
            if (navigator.onLine) {
                fetch('/', { method: 'HEAD', cache: 'no-cache' })
                    .then(() => window.location.reload())
                    .catch(() => {});
            }
        }, 30000);
    </script>
</body>
</html>
"""

    def _sync_chat_history(self, payload: Dict) -> Dict:
        """Sincroniza historial de chat"""
        try:
            # Implementar lógica de sincronización
            # Por ahora, simplemente confirmar recepción
            return {
                "success": True,
                "synced_items": len(payload.get("items", [])),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _sync_api_keys(self, payload: Dict) -> Dict:
        """Sincroniza configuración de API keys"""
        try:
            # Implementar lógica de sincronización segura
            return {
                "success": True,
                "message": "API keys sync not implemented for security",
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _sync_settings(self, payload: Dict) -> Dict:
        """Sincroniza configuraciones"""
        try:
            # Implementar lógica de sincronización
            return {
                "success": True,
                "synced_settings": list(payload.keys()),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _setup_static_files(self):
        """Configura archivos estáticos necesarios para PWA"""
        static_dir = Path("static")
        static_dir.mkdir(exist_ok=True)

        # Crear directorios necesarios
        (static_dir / "icons").mkdir(exist_ok=True)
        (static_dir / "js").mkdir(exist_ok=True)
        (static_dir / "css").mkdir(exist_ok=True)

        # Generar archivo PWA JavaScript
        pwa_js_content = self._generate_pwa_js()
        with open(static_dir / "js" / "pwa.js", "w", encoding="utf-8") as f:
            f.write(pwa_js_content)

    def _generate_pwa_js(self) -> str:
        """Genera el JavaScript para funcionalidades PWA"""
        return f"""
// Chispart Mobile PWA JavaScript
// Manejo de instalación, actualizaciones y funcionalidades offline

class ChispartPWA {{
    constructor() {{
        this.swRegistration = null;
        this.deferredPrompt = null;
        this.isOnline = navigator.onLine;
        this.syncQueue = [];
        
        this.init();
    }}
    
    async init() {{
        console.log('[PWA] Initializing Chispart Mobile PWA');
        
        // Registrar Service Worker
        if ('serviceWorker' in navigator) {{
            try {{
                this.swRegistration = await navigator.serviceWorker.register('/sw.js');
                console.log('[PWA] Service Worker registered');
                
                // Escuchar actualizaciones
                this.swRegistration.addEventListener('updatefound', () => {{
                    this.handleUpdate();
                }});
            }} catch (error) {{
                console.error('[PWA] Service Worker registration failed:', error);
            }}
        }}
        
        // Configurar eventos
        this.setupEventListeners();
        
        // Configurar sincronización
        this.setupSync();
        
        // Verificar instalación
        this.checkInstallPrompt();
        
        // Configurar notificaciones
        this.setupNotifications();
    }}
    
    setupEventListeners() {{
        // Evento de instalación
        window.addEventListener('beforeinstallprompt', (e) => {{
            e.preventDefault();
            this.deferredPrompt = e;
            this.showInstallButton();
        }});
        
        // Eventos de conexión
        window.addEventListener('online', () => {{
            this.isOnline = true;
            this.handleOnline();
        }});
        
        window.addEventListener('offline', () => {{
            this.isOnline = false;
            this.handleOffline();
        }});
        
        // Evento de instalación completada
        window.addEventListener('appinstalled', () => {{
            console.log('[PWA] App installed successfully');
            this.hideInstallButton();
        }});
    }}
    
    async installApp() {{
        if (!this.deferredPrompt) {{
            console.log('[PWA] Install prompt not available');
            return;
        }}
        
        try {{
            this.deferredPrompt.prompt();
            const result = await this.deferredPrompt.userChoice;
            
            if (result.outcome === 'accepted') {{
                console.log('[PWA] User accepted install');
            }} else {{
                console.log('[PWA] User dismissed install');
            }}
            
            this.deferredPrompt = null;
        }} catch (error) {{
            console.error('[PWA] Install error:', error);
        }}
    }}
    
    showInstallButton() {{
        const installBtn = document.getElementById('install-btn');
        if (installBtn) {{
            installBtn.style.display = 'block';
            installBtn.onclick = () => this.installApp();
        }}
    }}
    
    hideInstallButton() {{
        const installBtn = document.getElementById('install-btn');
        if (installBtn) {{
            installBtn.style.display = 'none';
        }}
    }}
    
    handleUpdate() {{
        const newWorker = this.swRegistration.installing;
        
        newWorker.addEventListener('statechange', () => {{
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {{
                this.showUpdateNotification();
            }}
        }});
    }}
    
    showUpdateNotification() {{
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
        setTimeout(() => {{
            updateBanner.remove();
        }}, 10000);
    }}
    
    handleOnline() {{
        console.log('[PWA] Connection restored');
        
        // Mostrar indicador de conexión
        this.showConnectionStatus('online');
        
        // Procesar cola de sincronización
        this.processSyncQueue();
        
        // Ocultar indicador después de 3 segundos
        setTimeout(() => {{
            this.hideConnectionStatus();
        }}, 3000);
    }}
    
    handleOffline() {{
        console.log('[PWA] Connection lost');
        this.showConnectionStatus('offline');
    }}
    
    showConnectionStatus(status) {{
        let statusEl = document.getElementById('connection-status');
        
        if (!statusEl) {{
            statusEl = document.createElement('div');
            statusEl.id = 'connection-status';
            statusEl.className = 'connection-status';
            document.body.appendChild(statusEl);
        }}
        
        statusEl.className = `connection-status ${{status}}`;
        statusEl.textContent = status === 'online' ? 
            '🟢 Conectado' : '🔴 Sin conexión';
        statusEl.style.display = 'block';
    }}
    
    hideConnectionStatus() {{
        const statusEl = document.getElementById('connection-status');
        if (statusEl) {{
            statusEl.style.display = 'none';
        }}
    }}
    
    setupSync() {{
        // Configurar sincronización en segundo plano
        if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {{
            console.log('[PWA] Background sync available');
        }}
    }}
    
    async addToSyncQueue(data) {{
        this.syncQueue.push({{
            ...data,
            timestamp: Date.now(),
            id: this.generateId()
        }});
        
        // Guardar en localStorage
        localStorage.setItem('chispart-sync-queue', JSON.stringify(this.syncQueue));
        
        // Intentar sincronizar si está online
        if (this.isOnline) {{
            this.processSyncQueue();
        }}
    }}
    
    async processSyncQueue() {{
        if (this.syncQueue.length === 0) return;
        
        console.log('[PWA] Processing sync queue:', this.syncQueue.length, 'items');
        
        const itemsToSync = [...this.syncQueue];
        this.syncQueue = [];
        
        for (const item of itemsToSync) {{
            try {{
                const response = await fetch('/api/pwa/sync', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(item)
                }});
                
                if (!response.ok) {{
                    // Volver a agregar a la cola si falla
                    this.syncQueue.push(item);
                }}
            }} catch (error) {{
                console.error('[PWA] Sync error:', error);
                this.syncQueue.push(item);
            }}
        }}
        
        // Actualizar localStorage
        localStorage.setItem('chispart-sync-queue', JSON.stringify(this.syncQueue));
    }}
    
    async setupNotifications() {{
        if (!('Notification' in window)) {{
            console.log('[PWA] Notifications not supported');
            return;
        }}
        
        if (Notification.permission === 'default') {{
            const permission = await Notification.requestPermission();
            console.log('[PWA] Notification permission:', permission);
        }}
    }}
    
    async showNotification(title, options = {{}}) {{
        if (Notification.permission !== 'granted') return;
        
        const defaultOptions = {{
            icon: '/static/icons/icon-192x192.png',
            badge: '/static/icons/badge-72x72.png',
            vibrate: [200, 100, 200],
            ...options
        }};
        
        if (this.swRegistration && this.swRegistration.showNotification) {{
            return this.swRegistration.showNotification(title, defaultOptions);
        }} else {{
            return new Notification(title, defaultOptions);
        }}
    }}
    
    generateId() {{
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }}
    
    checkInstallPrompt() {{
        // Verificar si ya está instalado
        if (window.matchMedia('(display-mode: standalone)').matches) {{
            console.log('[PWA] App is running in standalone mode');
            document.body.classList.add('standalone');
        }}
    }}
    
    // Métodos públicos para la aplicación
    async saveOfflineData(key, data) {{
        try {{
            localStorage.setItem(`chispart-offline-${{key}}`, JSON.stringify(data));
            return true;
        }} catch (error) {{
            console.error('[PWA] Error saving offline data:', error);
            return false;
        }}
    }}
    
    getOfflineData(key) {{
        try {{
            const data = localStorage.getItem(`chispart-offline-${{key}}`);
            return data ? JSON.parse(data) : null;
        }} catch (error) {{
            console.error('[PWA] Error getting offline data:', error);
            return null;
        }}
    }}
    
    clearOfflineData(key) {{
        try {{
            localStorage.removeItem(`chispart-offline-${{key}}`);
            return true;
        }} catch (error) {{
            console.error('[PWA] Error clearing offline data:', error);
            return false;
        }}
    }}
}}

// Inicializar PWA cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {{
    window.chispartPWA = new ChispartPWA();
}});

// Exportar para uso en otros módulos
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = ChispartPWA;
}}
"""

    def get_pwa_config(self) -> Dict:
        """Obtiene la configuración PWA actual"""
        return {
            "cache_version": self.cache_version,
            "config": self.config,
            "features": {
                "offline_support": True,
                "background_sync": True,
                "push_notifications": self.config["notifications_enabled"],
                "install_prompt": self.config["install_prompt"],
                "auto_update": True,
            },
        }

    def update_config(self, new_config: Dict):
        """Actualiza la configuración PWA"""
        self.config.update(new_config)
        self.cache_version = self._generate_cache_version()

    def get_cache_stats(self) -> Dict:
        """Obtiene estadísticas del caché (placeholder)"""
        return {
            "version": self.cache_version,
            "max_size": self.config["max_cache_size"],
            "estimated_size": 0,  # Se calculará en el cliente
            "last_updated": datetime.now().isoformat(),
        }


# Instancia global para uso en la aplicación
pwa_manager = PWAManager()
