// 7tỷ.vn Agent App - Service Worker
// PWA offline functionality and caching

const CACHE_NAME = 'ty7-agent-v2.0.0';
const urlsToCache = [
    '/',
    '/index.html',
    '/css/app.css',
    '/css/mobile.css',
    '/css/components.css',
    '/js/app.js',
    '/js/auth.js',
    '/js/wallet.js',
    '/js/scanner.js',
    '/js/bills.js',
    '/js/api.js',
    '/manifest.json',
    '/assets/icons/icon-192x192.png',
    '/assets/icons/icon-512x512.png',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
];

// Install event - cache resources
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('Opened cache');
                return cache.addAll(urlsToCache);
            })
    );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                // Return cached version or fetch from network
                if (response) {
                    return response;
                }
                
                return fetch(event.request).then((response) => {
                    // Check if we received a valid response
                    if (!response || response.status !== 200 || response.type !== 'basic') {
                        return response;
                    }

                    // Clone the response
                    const responseToCache = response.clone();

                    caches.open(CACHE_NAME)
                        .then((cache) => {
                            cache.put(event.request, responseToCache);
                        });

                    return response;
                });
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// Background sync for offline transactions
self.addEventListener('sync', (event) => {
    if (event.tag === 'background-sync') {
        event.waitUntil(doBackgroundSync());
    }
});

// Push notifications
self.addEventListener('push', (event) => {
    const options = {
        body: event.data ? event.data.text() : 'Bạn có thông báo mới từ 7tỷ.vn',
        icon: '/assets/icons/icon-192x192.png',
        badge: '/assets/icons/badge-72x72.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'Xem chi tiết',
                icon: '/assets/icons/checkmark.png'
            },
            {
                action: 'close',
                title: 'Đóng',
                icon: '/assets/icons/xmark.png'
            }
        ]
    };

    event.waitUntil(
        self.registration.showNotification('7tỷ.vn', options)
    );
});

// Notification click handler
self.addEventListener('notificationclick', (event) => {
    event.notification.close();

    if (event.action === 'explore') {
        // Open the app
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

// Background sync function
async function doBackgroundSync() {
    try {
        // Get pending transactions from IndexedDB
        const pendingTransactions = await getPendingTransactions();
        
        for (const transaction of pendingTransactions) {
            try {
                // Attempt to sync transaction
                const response = await fetch('/api/transactions/sync', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(transaction)
                });

                if (response.ok) {
                    // Remove from pending list
                    await removePendingTransaction(transaction.id);
                }
            } catch (error) {
                console.log('Failed to sync transaction:', transaction.id);
            }
        }
    } catch (error) {
        console.log('Background sync failed:', error);
    }
}

// IndexedDB helpers for offline storage
async function getPendingTransactions() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('ty7-agent-db', 1);
        
        request.onsuccess = (event) => {
            const db = event.target.result;
            const transaction = db.transaction(['pending_transactions'], 'readonly');
            const store = transaction.objectStore('pending_transactions');
            const getAll = store.getAll();
            
            getAll.onsuccess = () => {
                resolve(getAll.result);
            };
        };
        
        request.onerror = () => {
            reject(request.error);
        };
    });
}

async function removePendingTransaction(id) {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('ty7-agent-db', 1);
        
        request.onsuccess = (event) => {
            const db = event.target.result;
            const transaction = db.transaction(['pending_transactions'], 'readwrite');
            const store = transaction.objectStore('pending_transactions');
            const deleteRequest = store.delete(id);
            
            deleteRequest.onsuccess = () => {
                resolve();
            };
        };
        
        request.onerror = () => {
            reject(request.error);
        };
    });
}