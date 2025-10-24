// 7tỷ.vn Customer App - Service Worker
// PWA offline functionality and background sync for customer app

const CACHE_NAME = 'ty7-customer-v2.0.0';
const urlsToCache = [
    '/',
    '/index.html',
    '/css/app.css',
    '/css/mobile.css',
    '/css/components.css',
    '/css/themes.css',
    '/js/app.js',
    '/js/auth.js',
    '/js/wallet.js',
    '/js/bills.js',
    '/js/receipts.js',
    '/js/profile.js',
    '/js/notifications.js',
    '/js/api.js',
    '/components/modals.js',
    '/components/forms.js',
    '/components/camera.js',
    '/manifest.json',
    '/assets/icons/icon-192x192.png',
    '/assets/icons/icon-512x512.png',
    '/assets/images/default-avatar.png',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
];

// Install event - cache resources
self.addEventListener('install', (event) => {
    console.log('[Customer SW] Install event');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('[Customer SW] Opened cache');
                return cache.addAll(urlsToCache);
            })
            .catch((error) => {
                console.error('[Customer SW] Cache failed:', error);
            })
    );
    self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('[Customer SW] Activate event');
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('[Customer SW] Deleting old cache:', cacheName);
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

    // Handle API requests differently
    if (event.request.url.includes('/api/')) {
        event.respondWith(
            fetch(event.request)
                .then((response) => {
                    // Cache successful API responses for offline use
                    if (response.ok && event.request.method === 'GET') {
                        const responseClone = response.clone();
                        caches.open(CACHE_NAME).then((cache) => {
                            cache.put(event.request, responseClone);
                        });
                    }
                    return response;
                })
                .catch(() => {
                    // Return cached API response if available
                    return caches.match(event.request);
                })
        );
        return;
    }

    // Handle static resources
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                if (response) {
                    console.log('[Customer SW] Serving from cache:', event.request.url);
                    return response;
                }
                
                console.log('[Customer SW] Fetching from network:', event.request.url);
                return fetch(event.request).then((response) => {
                    if (!response || response.status !== 200 || response.type !== 'basic') {
                        return response;
                    }

                    const responseToCache = response.clone();
                    caches.open(CACHE_NAME)
                        .then((cache) => {
                            cache.put(event.request, responseToCache);
                        });

                    return response;
                }).catch((error) => {
                    console.error('[Customer SW] Fetch failed:', error);
                    
                    // Return offline page for navigation requests
                    if (event.request.mode === 'navigate') {
                        return caches.match('/offline.html') || 
                               caches.match('/index.html');
                    }
                    
                    throw error;
                });
            })
    );
});

// Background sync for offline operations
self.addEventListener('sync', (event) => {
    console.log('[Customer SW] Background sync:', event.tag);
    
    if (event.tag === 'background-sync') {
        event.waitUntil(doBackgroundSync());
    } else if (event.tag === 'receipt-upload') {
        event.waitUntil(syncReceiptUploads());
    } else if (event.tag === 'withdrawal-request') {
        event.waitUntil(syncWithdrawalRequests());
    } else if (event.tag === 'bill-collection') {
        event.waitUntil(syncBillCollections());
    }
});

// Push notifications
self.addEventListener('push', (event) => {
    console.log('[Customer SW] Push received');
    
    let notificationData = {
        title: '7tỷ.vn',
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
        vibrate: [200, 100, 200],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: notificationData.id || 1,
            url: notificationData.url || '/',
            type: notificationData.type || 'general'
        },
        actions: getNotificationActions(notificationData.type),
        requireInteraction: notificationData.requireInteraction || false,
        silent: false,
        renotify: true
    };

    event.waitUntil(
        self.registration.showNotification(notificationData.title, options)
    );
});

// Get notification actions based on type
function getNotificationActions(type) {
    switch (type) {
        case 'withdrawal':
            return [
                {
                    action: 'view-withdrawal',
                    title: 'Xem chi tiết',
                    icon: '/assets/icons/view.png'
                },
                {
                    action: 'dismiss',
                    title: 'Đóng',
                    icon: '/assets/icons/close.png'
                }
            ];
        case 'receipt':
            return [
                {
                    action: 'view-receipt',
                    title: 'Xem biên nhận',
                    icon: '/assets/icons/receipt.png'
                },
                {
                    action: 'dismiss',
                    title: 'Đóng',
                    icon: '/assets/icons/close.png'
                }
            ];
        case 'bill':
            return [
                {
                    action: 'view-bills',
                    title: 'Xem hóa đơn',
                    icon: '/assets/icons/bill.png'
                },
                {
                    action: 'dismiss',
                    title: 'Đóng',
                    icon: '/assets/icons/close.png'
                }
            ];
        default:
            return [
                {
                    action: 'open',
                    title: 'Mở ứng dụng',
                    icon: '/assets/icons/open.png'
                },
                {
                    action: 'dismiss',
                    title: 'Đóng',
                    icon: '/assets/icons/close.png'
                }
            ];
    }
}

// Notification click handler
self.addEventListener('notificationclick', (event) => {
    console.log('[Customer SW] Notification click:', event.action);
    
    event.notification.close();

    if (event.action === 'dismiss') {
        return;
    }

    let urlToOpen = '/';
    
    // Determine URL based on action
    switch (event.action) {
        case 'view-withdrawal':
            urlToOpen = '/?page=wallet';
            break;
        case 'view-receipt':
            urlToOpen = '/?page=receipts';
            break;
        case 'view-bills':
            urlToOpen = '/?page=bills';
            break;
        default:
            urlToOpen = event.notification.data.url || '/';
    }

    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true })
            .then((clientList) => {
                // Check if there's already a window/tab open
                for (const client of clientList) {
                    if (client.url.includes(self.location.origin) && 'focus' in client) {
                        // Navigate to the specific page
                        client.postMessage({
                            type: 'NAVIGATE_TO',
                            url: urlToOpen
                        });
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
    console.log('[Customer SW] Message received:', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'CACHE_URLS') {
        event.waitUntil(
            caches.open(CACHE_NAME)
                .then((cache) => cache.addAll(event.data.payload))
        );
    }

    if (event.data && event.data.type === 'SYNC_RECEIPTS') {
        event.waitUntil(syncReceiptUploads());
    }

    if (event.data && event.data.type === 'SYNC_WITHDRAWALS') {
        event.waitUntil(syncWithdrawalRequests());
    }
});

// Background sync functions
async function doBackgroundSync() {
    try {
        console.log('[Customer SW] Starting background sync');
        
        // Sync all pending operations
        await Promise.all([
            syncReceiptUploads(),
            syncWithdrawalRequests(),
            syncBillCollections(),
            syncProfileUpdates()
        ]);
        
        console.log('[Customer SW] Background sync completed');
    } catch (error) {
        console.error('[Customer SW] Background sync failed:', error);
    }
}

async function syncReceiptUploads() {
    try {
        const pendingReceipts = await getPendingReceipts();
        
        for (const receipt of pendingReceipts) {
            try {
                const formData = new FormData();
                formData.append('image', receipt.file);
                formData.append('billId', receipt.billId);
                formData.append('notes', receipt.notes || '');

                const response = await fetch('/api/receipts/upload', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${receipt.token}`
                    },
                    body: formData
                });

                if (response.ok) {
                    await removePendingReceipt(receipt.id);
                    
                    // Show success notification
                    self.registration.showNotification('Tải biên nhận thành công', {
                        body: 'Biên nhận đã được tải lên và đang chờ duyệt',
                        icon: '/assets/icons/icon-192x192.png',
                        tag: 'receipt-uploaded',
                        actions: [
                            {
                                action: 'view-receipt',
                                title: 'Xem chi tiết'
                            }
                        ]
                    });
                }
            } catch (error) {
                console.error('[Customer SW] Failed to sync receipt:', error);
            }
        }
    } catch (error) {
        console.error('[Customer SW] Receipt sync failed:', error);
    }
}

async function syncWithdrawalRequests() {
    try {
        const pendingWithdrawals = await getPendingWithdrawals();
        
        for (const withdrawal of pendingWithdrawals) {
            try {
                const response = await fetch('/api/withdrawals', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${withdrawal.token}`
                    },
                    body: JSON.stringify(withdrawal.data)
                });

                if (response.ok) {
                    await removePendingWithdrawal(withdrawal.id);
                    
                    // Show success notification
                    self.registration.showNotification('Yêu cầu rút tiền thành công', {
                        body: `Yêu cầu rút ${withdrawal.data.amount.toLocaleString('vi-VN')} VND đã được gửi`,
                        icon: '/assets/icons/icon-192x192.png',
                        tag: 'withdrawal-requested',
                        actions: [
                            {
                                action: 'view-withdrawal',
                                title: 'Xem chi tiết'
                            }
                        ]
                    });
                }
            } catch (error) {
                console.error('[Customer SW] Failed to sync withdrawal:', error);
            }
        }
    } catch (error) {
        console.error('[Customer SW] Withdrawal sync failed:', error);
    }
}

async function syncBillCollections() {
    try {
        const pendingCollections = await getPendingCollections();
        
        for (const collection of pendingCollections) {
            try {
                const response = await fetch(`/api/bills/${collection.billId}/collect`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${collection.token}`
                    }
                });

                if (response.ok) {
                    await removePendingCollection(collection.id);
                }
            } catch (error) {
                console.error('[Customer SW] Failed to sync collection:', error);
            }
        }
    } catch (error) {
        console.error('[Customer SW] Collection sync failed:', error);
    }
}

async function syncProfileUpdates() {
    try {
        const pendingUpdates = await getPendingProfileUpdates();
        
        for (const update of pendingUpdates) {
            try {
                const response = await fetch('/api/profile', {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${update.token}`
                    },
                    body: JSON.stringify(update.data)
                });

                if (response.ok) {
                    await removePendingProfileUpdate(update.id);
                }
            } catch (error) {
                console.error('[Customer SW] Failed to sync profile update:', error);
            }
        }
    } catch (error) {
        console.error('[Customer SW] Profile update sync failed:', error);
    }
}

// IndexedDB helper functions
async function getPendingReceipts() {
    return getFromIndexedDB('pending_receipts');
}

async function getPendingWithdrawals() {
    return getFromIndexedDB('pending_withdrawals');
}

async function getPendingCollections() {
    return getFromIndexedDB('pending_collections');
}

async function getPendingProfileUpdates() {
    return getFromIndexedDB('pending_profile_updates');
}

async function removePendingReceipt(id) {
    return removeFromIndexedDB('pending_receipts', id);
}

async function removePendingWithdrawal(id) {
    return removeFromIndexedDB('pending_withdrawals', id);
}

async function removePendingCollection(id) {
    return removeFromIndexedDB('pending_collections', id);
}

async function removePendingProfileUpdate(id) {
    return removeFromIndexedDB('pending_profile_updates', id);
}

async function getFromIndexedDB(storeName) {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('ty7-customer-db', 1);
        
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            
            if (!db.objectStoreNames.contains('pending_receipts')) {
                db.createObjectStore('pending_receipts', { keyPath: 'id' });
            }
            if (!db.objectStoreNames.contains('pending_withdrawals')) {
                db.createObjectStore('pending_withdrawals', { keyPath: 'id' });
            }
            if (!db.objectStoreNames.contains('pending_collections')) {
                db.createObjectStore('pending_collections', { keyPath: 'id' });
            }
            if (!db.objectStoreNames.contains('pending_profile_updates')) {
                db.createObjectStore('pending_profile_updates', { keyPath: 'id' });
            }
        };
        
        request.onsuccess = (event) => {
            const db = event.target.result;
            const transaction = db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const getAll = store.getAll();
            
            getAll.onsuccess = () => resolve(getAll.result);
            getAll.onerror = () => reject(getAll.error);
        };
        
        request.onerror = () => reject(request.error);
    });
}

async function removeFromIndexedDB(storeName, id) {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('ty7-customer-db', 1);
        
        request.onsuccess = (event) => {
            const db = event.target.result;
            const transaction = db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);
            const deleteRequest = store.delete(id);
            
            deleteRequest.onsuccess = () => resolve();
            deleteRequest.onerror = () => reject(deleteRequest.error);
        };
        
        request.onerror = () => reject(request.error);
    });
}