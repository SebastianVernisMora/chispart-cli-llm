/**
 * Chispart Mobile Service Worker
 * Maneja caché, sincronización offline y notificaciones push
 */

const CACHE_NAME = 'chispart-mobile-v1.0.0';
const STATIC_CACHE = 'chispart-static-v1.0.0';
const DYNAMIC_CACHE = 'chispart-dynamic-v1.0.0';
const API_CACHE = 'chispart-api-v1.0.0';

// Archivos estáticos para cachear
const STATIC_ASSETS = [
    '/',
    '/chat',
    '/config',
    '/offline',
    '/static/css/style.css',
    '/static/css/themes.css',
    '/static/css/mobile.css',
    '/static/js/app.js',
    '/static/js/utils.js',
    '/static/js/pwa.js',
    '/static/manifest.json',
    '/static/icons/icon-192x192.png',
    '/static/icons/icon-512x512.png'
];

// URLs de API para cachear
const API_URLS = [
    '/api/config',
    '/api/stats',
    '/api/api-keys'
];

// Estrategias de caché
const CACHE_STRATEGIES = {
    CACHE_FIRST: 'cache-first',
    NETWORK_FIRST: 'network-first',
    STALE_WHILE_REVALIDATE: 'stale-while-revalidate',
    NETWORK_ONLY: 'network-only',
    CACHE_ONLY: 'cache-only'
};

// Configuración de rutas y estrategias
const ROUTE_CONFIG = {
    // Archivos estáticos - Cache First
    static: {
        pattern: /\.(css|js|png|jpg|jpeg|gif|svg|ico|woff|woff2|ttf|eot)$/,
        strategy: CACHE_STRATEGIES.CACHE_FIRST,
        cache: STATIC_CACHE
    },
    
    // APIs de configuración - Network First con fallback
    api: {
        pattern: /^\/api\/(config|stats|api-keys)/,
        strategy: CACHE_STRATEGIES.NETWORK_FIRST,
        cache: API_CACHE
    },
    
    // APIs de chat - Network Only (requieren conexión)
    chat: {
        pattern: /^\/api\/(chat|image|validate-keys)/,
        strategy: CACHE_STRATEGIES.NETWORK_ONLY
    },
    
    // Páginas HTML - Stale While Revalidate
    pages: {
        pattern: /^\/(?:chat|config|offline)?$/,
        strategy: CACHE_STRATEGIES.STALE_WHILE_REVALIDATE,
        cache: DYNAMIC_CACHE
    }
};

/**
 * Evento de instalación del Service Worker
 */
self.addEventListener('install', event => {
    console.log('[SW] Installing Service Worker...');
    
    event.waitUntil(
        Promise.all([
            // Cachear archivos estáticos
            caches.open(STATIC_CACHE).then(cache => {
                console.log('[SW] Caching static assets...');
                return cache.addAll(STATIC_ASSETS);
            }),
            
            // Cachear APIs básicas
            caches.open(API_CACHE).then(cache => {
                console.log('[SW] Pre-caching API endpoints...');
                return Promise.allSettled(
                    API_URLS.map(url => 
                        fetch(url)
                            .then(response => response.ok ? cache.put(url, response) : null)
                            .catch(() => null) // Ignorar errores en pre-cache
                    )
                );
            })
        ]).then(() => {
            console.log('[SW] Installation complete');
            // Forzar activación inmediata
            return self.skipWaiting();
        })
    );
});

/**
 * Evento de activación del Service Worker
 */
self.addEventListener('activate', event => {
    console.log('[SW] Activating Service Worker...');
    
    event.waitUntil(
        Promise.all([
            // Limpiar cachés antiguos
            cleanupOldCaches(),
            
            // Tomar control de todos los clientes
            self.clients.claim()
        ]).then(() => {
            console.log('[SW] Activation complete');
        })
    );
});

/**
 * Evento de fetch - Intercepta todas las peticiones de red
 */
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Solo manejar peticiones del mismo origen
    if (url.origin !== location.origin) {
        return;
    }
    
    // Determinar estrategia basada en la URL
    const strategy = getStrategyForRequest(request);
    
    if (strategy) {
        event.respondWith(handleRequest(request, strategy));
    }
});

/**
 * Evento de sincronización en segundo plano
 */
self.addEventListener('sync', event => {
    console.log('[SW] Background sync triggered:', event.tag);
    
    switch (event.tag) {
        case 'sync-pending-messages':
            event.waitUntil(syncPendingMessages());
            break;
            
        case 'sync-offline-data':
            event.waitUntil(syncOfflineData());
            break;
            
        default:
            console.log('[SW] Unknown sync tag:', event.tag);
    }
});

/**
 * Evento de notificación push
 */
self.addEventListener('push', event => {
    console.log('[SW] Push notification received');
    
    const options = {
        body: 'Tienes nuevos mensajes en Chispart Mobile',
        icon: '/static/icons/icon-192x192.png',
        badge: '/static/icons/badge-72x72.png',
        vibrate: [200, 100, 200],
        data: {
            url: '/chat'
        },
        actions: [
            {
                action: 'open',
                title: 'Abrir Chat',
                icon: '/static/icons/action-chat.png'
            },
            {
                action: 'dismiss',
                title: 'Descartar',
                icon: '/static/icons/action-dismiss.png'
            }
        ]
    };
    
    if (event.data) {
        try {
            const data = event.data.json();
            options.body = data.message || options.body;
            options.data = { ...options.data, ...data };
        } catch (e) {
            console.warn('[SW] Error parsing push data:', e);
        }
    }
    
    event.waitUntil(
        self.registration.showNotification('Chispart Mobile', options)
    );
});

/**
 * Evento de click en notificación
 */
self.addEventListener('notificationclick', event => {
    console.log('[SW] Notification clicked:', event.action);
    
    event.notification.close();
    
    if (event.action === 'dismiss') {
        return;
    }
    
    const urlToOpen = event.notification.data?.url || '/';
    
    event.waitUntil(
        self.clients.matchAll({ type: 'window' }).then(clients => {
            // Buscar ventana existente
            const existingClient = clients.find(client => 
                client.url.includes(self.location.origin)
            );
            
            if (existingClient) {
                // Enfocar ventana existente
                return existingClient.focus().then(client => {
                    if (client.url !== urlToOpen) {
                        return client.navigate(urlToOpen);
                    }
                    return client;
                });
            } else {
                // Abrir nueva ventana
                return self.clients.openWindow(urlToOpen);
            }
        })
    );
});

/**
 * Evento de mensaje desde el cliente
 */
self.addEventListener('message', event => {
    console.log('[SW] Message received:', event.data);
    
    const { type, payload } = event.data;
    
    switch (type) {
        case 'SKIP_WAITING':
            self.skipWaiting();
            break;
            
        case 'GET_VERSION':
            event.ports[0].postMessage({ version: CACHE_NAME });
            break;
            
        case 'CLEAR_CACHE':
            clearAllCaches().then(() => {
                event.ports[0].postMessage({ success: true });
            });
            break;
            
        case 'SYNC_DATA':
            syncOfflineData().then(() => {
                event.ports[0].postMessage({ success: true });
            });
            break;
            
        default:
            console.warn('[SW] Unknown message type:', type);
    }
});

/**
 * Determina la estrategia de caché para una petición
 */
function getStrategyForRequest(request) {
    const url = new URL(request.url);
    const pathname = url.pathname;
    
    // Verificar cada configuración de ruta
    for (const [name, config] of Object.entries(ROUTE_CONFIG)) {
        if (config.pattern.test(pathname)) {
            return {
                name: config.strategy,
                cache: config.cache || DYNAMIC_CACHE,
                config
            };
        }
    }
    
    // Estrategia por defecto para otras rutas
    return {
        name: CACHE_STRATEGIES.NETWORK_FIRST,
        cache: DYNAMIC_CACHE
    };
}

/**
 * Maneja una petición según la estrategia especificada
 */
async function handleRequest(request, strategy) {
    const { name, cache: cacheName } = strategy;
    
    switch (name) {
        case CACHE_STRATEGIES.CACHE_FIRST:
            return cacheFirst(request, cacheName);
            
        case CACHE_STRATEGIES.NETWORK_FIRST:
            return networkFirst(request, cacheName);
            
        case CACHE_STRATEGIES.STALE_WHILE_REVALIDATE:
            return staleWhileRevalidate(request, cacheName);
            
        case CACHE_STRATEGIES.NETWORK_ONLY:
            return networkOnly(request);
            
        case CACHE_STRATEGIES.CACHE_ONLY:
            return cacheOnly(request, cacheName);
            
        default:
            return fetch(request);
    }
}

/**
 * Estrategia Cache First
 */
async function cacheFirst(request, cacheName) {
    const cache = await caches.open(cacheName);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
        return cachedResponse;
    }
    
    try {
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        console.warn('[SW] Network failed for cache-first:', request.url);
        return new Response('Offline', { status: 503 });
    }
}

/**
 * Estrategia Network First
 */
async function networkFirst(request, cacheName) {
    const cache = await caches.open(cacheName);
    
    try {
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        console.warn('[SW] Network failed, trying cache:', request.url);
        const cachedResponse = await cache.match(request);
        
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Fallback para páginas HTML
        if (request.destination === 'document') {
            return cache.match('/offline') || new Response('Offline', { status: 503 });
        }
        
        throw error;
    }
}

/**
 * Estrategia Stale While Revalidate
 */
async function staleWhileRevalidate(request, cacheName) {
    const cache = await caches.open(cacheName);
    const cachedResponse = await cache.match(request);
    
    // Actualizar caché en segundo plano
    const networkPromise = fetch(request).then(response => {
        if (response.ok) {
            cache.put(request, response.clone());
        }
        return response;
    }).catch(() => null);
    
    // Devolver respuesta cacheada inmediatamente si existe
    return cachedResponse || networkPromise;
}

/**
 * Estrategia Network Only
 */
async function networkOnly(request) {
    try {
        return await fetch(request);
    } catch (error) {
        // Para APIs de chat, devolver error específico
        if (request.url.includes('/api/chat')) {
            return new Response(JSON.stringify({
                error: 'Sin conexión. El mensaje se guardará para enviar más tarde.',
                offline: true
            }), {
                status: 503,
                headers: { 'Content-Type': 'application/json' }
            });
        }
        throw error;
    }
}

/**
 * Estrategia Cache Only
 */
async function cacheOnly(request, cacheName) {
    const cache = await caches.open(cacheName);
    return cache.match(request) || new Response('Not found in cache', { status: 404 });
}

/**
 * Limpia cachés antiguos
 */
async function cleanupOldCaches() {
    const cacheNames = await caches.keys();
    const currentCaches = [CACHE_NAME, STATIC_CACHE, DYNAMIC_CACHE, API_CACHE];
    
    return Promise.all(
        cacheNames
            .filter(cacheName => !currentCaches.includes(cacheName))
            .map(cacheName => {
                console.log('[SW] Deleting old cache:', cacheName);
                return caches.delete(cacheName);
            })
    );
}

/**
 * Limpia todos los cachés
 */
async function clearAllCaches() {
    const cacheNames = await caches.keys();
    return Promise.all(cacheNames.map(name => caches.delete(name)));
}

/**
 * Sincroniza mensajes pendientes
 */
async function syncPendingMessages() {
    console.log('[SW] Syncing pending messages...');
    
    try {
        // Obtener mensajes pendientes del IndexedDB o localStorage
        const pendingMessages = await getPendingMessages();
        
        for (const message of pendingMessages) {
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(message)
                });
                
                if (response.ok) {
                    await removePendingMessage(message.id);
                    console.log('[SW] Message synced:', message.id);
                }
            } catch (error) {
                console.warn('[SW] Failed to sync message:', message.id, error);
            }
        }
        
        // Notificar al cliente sobre la sincronización
        const clients = await self.clients.matchAll();
        clients.forEach(client => {
            client.postMessage({
                type: 'SYNC_COMPLETE',
                payload: { messagesSynced: pendingMessages.length }
            });
        });
        
    } catch (error) {
        console.error('[SW] Error syncing messages:', error);
    }
}

/**
 * Sincroniza datos offline
 */
async function syncOfflineData() {
    console.log('[SW] Syncing offline data...');
    
    try {
        // Sincronizar configuración
        await fetch('/api/config');
        
        // Sincronizar estadísticas
        await fetch('/api/stats');
        
        // Marcar última sincronización
        const clients = await self.clients.matchAll();
        clients.forEach(client => {
            client.postMessage({
                type: 'DATA_SYNCED',
                payload: { timestamp: Date.now() }
            });
        });
        
    } catch (error) {
        console.error('[SW] Error syncing data:', error);
    }
}

/**
 * Obtiene mensajes pendientes (placeholder - implementar con IndexedDB)
 */
async function getPendingMessages() {
    // TODO: Implementar con IndexedDB para mejor persistencia
    return [];
}

/**
 * Elimina un mensaje pendiente (placeholder)
 */
async function removePendingMessage(messageId) {
    // TODO: Implementar con IndexedDB
    console.log('[SW] Removing pending message:', messageId);
}

// Logging de eventos para debugging
console.log('[SW] Service Worker loaded');
