// 7tỷ.vn Staff App - Service Worker
// PWA offline functionality and background sync

const CACHE_NAME = 'ty7-staff-v2.0.0';
const urlsToCache = [
    '/',
    '/index.html',
    '/css/app.css',
    '/css/mobile.css',
    '/css/components.css',
    '/css/themes.css',
    '/js/app.js',
    '/js/auth.js',
    '/js/agents.js',
    '/js/finance.js',
    '/js/tasks.js',
    '/js/reports.js',
    '/js/notifications.js',
    '/js/api.js',
    '/components/modals.js',
    '/components/forms.js',
    '/components/charts.js',
    '/manifest.json',
    '/assets/icons/icon-192x192.png',
    '/assets/icons/icon-512x512.png',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
    'https://cdn.jsdelivr.net/npm/chart.js'
];

// Install event - cache resources
self.addEventListener('install', (event) => {
    console.log('[SW] Install event');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('[SW] Opened cache');
                return cache.addAll(urlsToCache);
            })
            .catch((error) => {
                console.error('[SW] Cache failed:', error);
            })
    );
    self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('[SW] Activate event');
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('[SW] Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
    // Skip cross-origin requests
    if (!event.request.url.startsWith(self.location.origin)) {
        return;
    }

    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                // Return cached version or fetch from network
                if (response) {
                    console.log('[SW] Serving from cache:', event.request.url);
                    return response;
                }
                
                console.log('[SW] Fetching from network:', event.request.url);
                return fetch(event.request).then((response) => {
                    // Check if we received a valid response
                    if (!response || response.status !== 200 || response.type !== 'basic') {
                        return response;
                    }

                    // Clone the response
                    const responseToCache = response.clone();

                    // Cache successful responses
                    caches.open(CACHE_NAME)
                        .then((cache) => {
                            cache.put(event.request, responseToCache);
                        });

                    return response;
                }).catch((error) => {
                    console.error('[SW] Fetch failed:', error);
                    
                    // Return offline page for navigation requests
                    if (event.request.mode === 'navigate') {
                        return caches.match('/offline.html');
                    }
                    
                    throw error;
                });
            })
    );
});

// Background sync for offline operations
self.addEventListener('sync', (event) => {
    console.log('[SW] Background sync:', event.tag);
    
    if (event.tag === 'background-sync') {
        event.waitUntil(doBackgroundSync());
    } else if (event.tag === 'agent-creation') {
        event.waitUntil(syncAgentCreation());
    } else if (event.tag === 'approval-actions') {
        event.waitUntil(syncApprovalActions());
    }
});

// Push notifications
self.addEventListener('push', (event) => {
    console.log('[SW] Push received');
    
    let notificationData = {
        title: '7tỷ.vn Staff',
        body: 'Bạn có thông báo mới',
        icon: '/assets/icons/icon-192x192.png',
        badge: '/assets/icons/badge-72x72.png',
        tag: 'default'
    };

    if (event.data) {
        try {
            const data = event.data.json();
            notificationData = { ...notificationData, ...data };
        } catch (e) {
            notificationData.body = event.data.text();
        }
    }

    const options = {
        body: notificationData.body,
        icon: notificationData.icon,
        badge: notificationData.badge,
        tag: notificationData.tag,
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: notificationData.id || 1,
            url: notificationData.url || '/'
        },
        actions: [
            {
                action: 'open',
                title: 'Xem chi tiết',
                icon: '/assets/icons/open.png'
            },
            {
                action: 'dismiss',
                title: 'Đóng',
                icon: '/assets/icons/close.png'
            }
        ],
        requireInteraction: notificationData.requireInteraction || false
    };

    event.waitUntil(
        self.registration.showNotification(notificationData.title, options)
    );
});

// Notification click handler
self.addEventListener('notificationclick', (event) => {
    console.log('[SW] Notification click:', event.action);
    
    event.notification.close();

    if (event.action === 'dismiss') {
        return;
    }

    const urlToOpen = event.notification.data.url || '/';

    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true })
            .then((clientList) => {
                // Check if there's already a window/tab open with the target URL
                for (const client of clientList) {
                    if (client.url === urlToOpen && 'focus' in client) {
                        return client.focus();
                    }
                }
                
                // If no window/tab is open, open a new one
                if (clients.openWindow) {
                    return clients.openWindow(urlToOpen);
                }
            })
    );
});

// Message handler for communication with main thread
self.addEventListener('message', (event) => {
    console.log('[SW] Message received:', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'CACHE_URLS') {
        event.waitUntil(
            caches.open(CACHE_NAME)
                .then((cache) => cache.addAll(event.data.payload))
        );
    }
});

// Background sync functions
async function doBackgroundSync() {
    try {
        console.log('[SW] Starting background sync');
        
        // Get pending operations from IndexedDB
        const pendingOperations = await getPendingOperations();
        
        for (const operation of pendingOperations) {
            try {
                await syncOperation(operation);
                await removePendingOperation(operation.id);
                console.log('[SW] Synced operation:', operation.id);
            } catch (error) {
                console.error('[SW] Failed to sync operation:', operation.id, error);
            }
        }
    } catch (error) {
        console.error('[SW] Background sync failed:', error);
    }
}

async function syncAgentCreation() {
    try {
        const pendingAgents = await getPendingAgents();
        
        for (const agent of pendingAgents) {
            try {
                const response = await fetch('/api/agents', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${agent.token}`
                    },
                    body: JSON.stringify(agent.data)
                });

                if (response.ok) {
                    await removePendingAgent(agent.id);
                    
                    // Show success notification
                    self.registration.showNotification('Tạo đại lý thành công', {
                        body: `Đại lý ${agent.data.name} đã được tạo thành công`,
                        icon: '/assets/icons/icon-192x192.png',
                        tag: 'agent-created'
                    });
                }
            } catch (error) {
                console.error('[SW] Failed to sync agent creation:', error);
            }
        }
    } catch (error) {
        console.error('[SW] Agent sync failed:', error);
    }
}

async function syncApprovalActions() {
    try {
        const pendingApprovals = await getPendingApprovals();
        
        for (const approval of pendingApprovals) {
            try {
                const response = await fetch(`/api/approvals/${approval.id}/${approval.action}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${approval.token}`
                    },
                    body: JSON.stringify(approval.data)
                });

                if (response.ok) {
                    await removePendingApproval(approval.id);
                    
                    // Show success notification
                    const actionText = approval.action === 'approve' ? 'phê duyệt' : 'từ chối';
                    self.registration.showNotification(`${actionText} thành công`, {
                        body: `Yêu cầu đã được ${actionText}`,
                        icon: '/assets/icons/icon-192x192.png',
                        tag: 'approval-processed'
                    });
                }
            } catch (error) {
                console.error('[SW] Failed to sync approval:', error);
            }
        }
    } catch (error) {
        console.error('[SW] Approval sync failed:', error);
    }
}

// IndexedDB helper functions
async function getPendingOperations() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('ty7-staff-db', 1);
        
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            
            if (!db.objectStoreNames.contains('pending_operations')) {
                db.createObjectStore('pending_operations', { keyPath: 'id' });
            }
            if (!db.objectStoreNames.contains('pending_agents')) {
                db.createObjectStore('pending_agents', { keyPath: 'id' });
            }
            if (!db.objectStoreNames.contains('pending_approvals')) {
                db.createObjectStore('pending_approvals', { keyPath: 'id' });
            }
        };
        
        request.onsuccess = (event) => {
            const db = event.target.result;
            const transaction = db.transaction(['pending_operations'], 'readonly');
            const store = transaction.objectStore('pending_operations');
            const getAll = store.getAll();
            
            getAll.onsuccess = () => resolve(getAll.result);
            getAll.onerror = () => reject(getAll.error);
        };
        
        request.onerror = () => reject(request.error);
    });
}

async function getPendingAgents() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('ty7-staff-db', 1);
        
        request.onsuccess = (event) => {
            const db = event.target.result;
            const transaction = db.transaction(['pending_agents'], 'readonly');
            const store = transaction.objectStore('pending_agents');
            const getAll = store.getAll();
            
            getAll.onsuccess = () => resolve(getAll.result);
            getAll.onerror = () => reject(getAll.error);
        };
        
        request.onerror = () => reject(request.error);
    });
}

async function getPendingApprovals() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('ty7-staff-db', 1);
        
        request.onsuccess = (event) => {
            const db = event.target.result;
            const transaction = db.transaction(['pending_approvals'], 'readonly');
            const store = transaction.objectStore('pending_approvals');
            const getAll = store.getAll();
            
            getAll.onsuccess = () => resolve(getAll.result);
            getAll.onerror = () => reject(getAll.error);
        };
        
        request.onerror = () => reject(request.error);
    });
}

async function removePendingOperation(id) {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('ty7-staff-db', 1);
        
        request.onsuccess = (event) => {
            const db = event.target.result;
            const transaction = db.transaction(['pending_operations'], 'readwrite');
            const store = transaction.objectStore('pending_operations');
            const deleteRequest = store.delete(id);
            
            deleteRequest.onsuccess = () => resolve();
            deleteRequest.onerror = () => reject(deleteRequest.error);
        };
        
        request.onerror = () => reject(request.error);
    });
}

async function removePendingAgent(id) {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('ty7-staff-db', 1);
        
        request.onsuccess = (event) => {
            const db = event.target.result;
            const transaction = db.transaction(['pending_agents'], 'readwrite');
            const store = transaction.objectStore('pending_agents');
            const deleteRequest = store.delete(id);
            
            deleteRequest.onsuccess = () => resolve();
            deleteRequest.onerror = () => reject(deleteRequest.error);
        };
        
        request.onerror = () => reject(request.error);
    });
}

async function removePendingApproval(id) {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('ty7-staff-db', 1);
        
        request.onsuccess = (event) => {
            const db = event.target.result;
            const transaction = db.transaction(['pending_approvals'], 'readwrite');
            const store = transaction.objectStore('pending_approvals');
            const deleteRequest = store.delete(id);
            
            deleteRequest.onsuccess = () => resolve();
            deleteRequest.onerror = () => reject(deleteRequest.error);
        };
        
        request.onerror = () => reject(request.error);
    });
}

async function syncOperation(operation) {
    const response = await fetch(operation.url, {
        method: operation.method,
        headers: operation.headers,
        body: operation.body
    });

    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }

    return response;
}