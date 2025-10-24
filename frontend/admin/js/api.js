// 7tỷ.vn Admin Interface - API Client
// Centralized API communication with Vietnamese error handling

class APIClient {
    constructor() {
        this.baseURL = CONFIG.API_BASE_URL;
        this.token = localStorage.getItem(CONFIG.STORAGE_KEYS.TOKEN);
        this.requestInterceptors = [];
        this.responseInterceptors = [];
    }

    // Set authentication token
    setToken(token) {
        this.token = token;
        if (token) {
            localStorage.setItem(CONFIG.STORAGE_KEYS.TOKEN, token);
        } else {
            localStorage.removeItem(CONFIG.STORAGE_KEYS.TOKEN);
        }
    }

    // Get authentication headers
    getAuthHeaders() {
        const headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        return headers;
    }

    // Make HTTP request
    async request(method, endpoint, data = null, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            method: method.toUpperCase(),
            headers: { ...this.getAuthHeaders(), ...options.headers },
            ...options
        };

        // Add request body for POST, PUT, PATCH
        if (data && ['POST', 'PUT', 'PATCH'].includes(config.method)) {
            if (data instanceof FormData) {
                // Remove Content-Type for FormData (browser will set it)
                delete config.headers['Content-Type'];
                config.body = data;
            } else {
                config.body = JSON.stringify(data);
            }
        }

        // Add query parameters for GET requests
        if (data && config.method === 'GET') {
            const params = new URLSearchParams(data);
            const separator = url.includes('?') ? '&' : '?';
            url += separator + params.toString();
        }

        try {
            // Apply request interceptors
            for (const interceptor of this.requestInterceptors) {
                await interceptor(config);
            }

            const response = await fetch(url, config);
            
            // Handle different response types
            let responseData;
            const contentType = response.headers.get('content-type');
            
            if (contentType && contentType.includes('application/json')) {
                responseData = await response.json();
            } else if (contentType && contentType.includes('text/')) {
                responseData = await response.text();
            } else {
                responseData = await response.blob();
            }

            // Apply response interceptors
            for (const interceptor of this.responseInterceptors) {
                await interceptor(response, responseData);
            }

            if (!response.ok) {
                throw new APIError(
                    responseData.detail || responseData.message || CONFIG.MESSAGES.ERROR.SERVER_ERROR,
                    response.status,
                    responseData
                );
            }

            return responseData;

        } catch (error) {
            if (error instanceof APIError) {
                throw error;
            }

            // Handle network errors
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                throw new APIError(CONFIG.MESSAGES.ERROR.NETWORK_ERROR, 0);
            }

            // Handle timeout errors
            if (error.name === 'AbortError') {
                throw new APIError(CONFIG.MESSAGES.ERROR.TIMEOUT, 0);
            }

            throw new APIError(CONFIG.MESSAGES.ERROR.UNKNOWN, 0, error);
        }
    }

    // HTTP method shortcuts
    async get(endpoint, params = null, options = {}) {
        return this.request('GET', endpoint, params, options);
    }

    async post(endpoint, data = null, options = {}) {
        return this.request('POST', endpoint, data, options);
    }

    async put(endpoint, data = null, options = {}) {
        return this.request('PUT', endpoint, data, options);
    }

    async patch(endpoint, data = null, options = {}) {
        return this.request('PATCH', endpoint, data, options);
    }

    async delete(endpoint, options = {}) {
        return this.request('DELETE', endpoint, null, options);
    }

    // Authentication methods
    async login(username, password) {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        const response = await this.post(CONFIG.API_ENDPOINTS.LOGIN, formData);
        
        if (response.access_token) {
            this.setToken(response.access_token);
        }

        return response;
    }

    async logout() {
        try {
            await this.post(CONFIG.API_ENDPOINTS.LOGOUT);
        } finally {
            this.setToken(null);
            localStorage.removeItem(CONFIG.STORAGE_KEYS.USER);
        }
    }

    async getCurrentUser() {
        return this.get(CONFIG.API_ENDPOINTS.ME);
    }

    async refreshToken() {
        const response = await this.post(CONFIG.API_ENDPOINTS.REFRESH_TOKEN);
        
        if (response.access_token) {
            this.setToken(response.access_token);
        }

        return response;
    }

    // Dashboard methods
    async getDashboardStats() {
        return this.get(CONFIG.API_ENDPOINTS.DASHBOARD_STATS);
    }

    async getRecentActivities(limit = 10) {
        return this.get(CONFIG.API_ENDPOINTS.RECENT_ACTIVITIES, { limit });
    }

    async getPendingApprovals(limit = 10) {
        return this.get(CONFIG.API_ENDPOINTS.PENDING_APPROVALS, { limit });
    }

    // Agent methods
    async getAgents(params = {}) {
        return this.get(CONFIG.API_ENDPOINTS.AGENTS, params);
    }

    async getAgent(id) {
        return this.get(`${CONFIG.API_ENDPOINTS.AGENTS}/${id}`);
    }

    async createAgent(agentData) {
        return this.post(CONFIG.API_ENDPOINTS.AGENTS, agentData);
    }

    async updateAgent(id, agentData) {
        return this.put(`${CONFIG.API_ENDPOINTS.AGENTS}/${id}`, agentData);
    }

    async deleteAgent(id) {
        return this.delete(`${CONFIG.API_ENDPOINTS.AGENTS}/${id}`);
    }

    async getPendingAgents() {
        return this.get(CONFIG.API_ENDPOINTS.AGENTS_PENDING);
    }

    async exportAgents(params = {}) {
        return this.get(CONFIG.API_ENDPOINTS.AGENTS_EXPORT, params);
    }

    // Bill methods
    async getBills(params = {}) {
        return this.get(CONFIG.API_ENDPOINTS.BILLS, params);
    }

    async getWarehouseBills(params = {}) {
        return this.get(CONFIG.API_ENDPOINTS.BILLS_WAREHOUSE, params);
    }

    async lookupBill(customerCode, providerId) {
        return this.post(CONFIG.API_ENDPOINTS.BILLS_LOOKUP, {
            customer_code: customerCode,
            provider_id: providerId
        });
    }

    async bulkLookupBills(customerCodes, providerId, useExternalAPI = true) {
        return this.post(CONFIG.API_ENDPOINTS.BILLS_BULK_LOOKUP, {
            customer_codes: customerCodes,
            provider_id: providerId,
            use_external_api: useExternalAPI
        });
    }

    async getProviders() {
        return this.get(CONFIG.API_ENDPOINTS.PROVIDERS);
    }

    async exportWarehouse(params = {}) {
        return this.get(CONFIG.API_ENDPOINTS.BILLS_EXPORT, params);
    }

    async uploadReceiptImage(billId, file) {
        const formData = new FormData();
        formData.append('file', file);
        return this.post(`${CONFIG.API_ENDPOINTS.BILLS}/${billId}/upload-receipt`, formData);
    }

    // Customer methods
    async getCustomers(params = {}) {
        return this.get(CONFIG.API_ENDPOINTS.CUSTOMERS, params);
    }

    async getCustomer(id) {
        return this.get(`${CONFIG.API_ENDPOINTS.CUSTOMERS}/${id}`);
    }

    async createCustomer(customerData) {
        return this.post(CONFIG.API_ENDPOINTS.CUSTOMERS, customerData);
    }

    async updateCustomer(id, customerData) {
        return this.put(`${CONFIG.API_ENDPOINTS.CUSTOMERS}/${id}`, customerData);
    }

    async deleteCustomer(id) {
        return this.delete(`${CONFIG.API_ENDPOINTS.CUSTOMERS}/${id}`);
    }

    async getPendingCustomers() {
        return this.get(CONFIG.API_ENDPOINTS.CUSTOMERS_PENDING);
    }

    async getCreditCards(customerId = null) {
        const endpoint = customerId 
            ? `${CONFIG.API_ENDPOINTS.CREDIT_CARDS}?customer_id=${customerId}`
            : CONFIG.API_ENDPOINTS.CREDIT_CARDS;
        return this.get(endpoint);
    }

    async getNearDueCards() {
        return this.get(CONFIG.API_ENDPOINTS.CARDS_NEAR_DUE);
    }

    // Transaction methods
    async getTransactions(params = {}) {
        return this.get(CONFIG.API_ENDPOINTS.TRANSACTIONS, params);
    }

    async getTransaction(id) {
        return this.get(`${CONFIG.API_ENDPOINTS.TRANSACTIONS}/${id}`);
    }

    // Approval methods
    async getApprovals(params = {}) {
        return this.get(CONFIG.API_ENDPOINTS.APPROVALS, params);
    }

    async getApproval(id) {
        return this.get(`${CONFIG.API_ENDPOINTS.APPROVALS}/${id}`);
    }

    async approveRequest(id, notes = '') {
        const endpoint = CONFIG.API_ENDPOINTS.APPROVE.replace('{id}', id);
        return this.post(endpoint, { notes });
    }

    async rejectRequest(id, reason = '') {
        const endpoint = CONFIG.API_ENDPOINTS.REJECT.replace('{id}', id);
        return this.post(endpoint, { reason });
    }

    // Staff methods
    async getStaff(params = {}) {
        return this.get(CONFIG.API_ENDPOINTS.STAFF, params);
    }

    async createStaff(staffData) {
        return this.post(CONFIG.API_ENDPOINTS.STAFF, staffData);
    }

    async updateStaff(id, staffData) {
        return this.put(`${CONFIG.API_ENDPOINTS.STAFF}/${id}`, staffData);
    }

    async deleteStaff(id) {
        return this.delete(`${CONFIG.API_ENDPOINTS.STAFF}/${id}`);
    }

    // File upload methods
    async uploadFile(file, type = 'document') {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('type', type);
        return this.post(CONFIG.API_ENDPOINTS.FILE_UPLOAD, formData);
    }

    // System methods
    async getHealth() {
        return this.get(CONFIG.API_ENDPOINTS.HEALTH);
    }

    async getSettings() {
        return this.get(CONFIG.API_ENDPOINTS.SETTINGS);
    }

    async updateSettings(settings) {
        return this.put(CONFIG.API_ENDPOINTS.SETTINGS, settings);
    }

    // Add request interceptor
    addRequestInterceptor(interceptor) {
        this.requestInterceptors.push(interceptor);
    }

    // Add response interceptor
    addResponseInterceptor(interceptor) {
        this.responseInterceptors.push(interceptor);
    }
}

// Custom API Error class
class APIError extends Error {
    constructor(message, status = 0, data = null) {
        super(message);
        this.name = 'APIError';
        this.status = status;
        this.data = data;
    }

    // Get user-friendly error message in Vietnamese
    getUserMessage() {
        switch (this.status) {
            case 400:
                return CONFIG.MESSAGES.ERROR.VALIDATION_ERROR;
            case 401:
                return CONFIG.MESSAGES.ERROR.UNAUTHORIZED;
            case 403:
                return CONFIG.MESSAGES.ERROR.UNAUTHORIZED;
            case 404:
                return CONFIG.MESSAGES.ERROR.NOT_FOUND;
            case 408:
                return CONFIG.MESSAGES.ERROR.TIMEOUT;
            case 500:
            case 502:
            case 503:
            case 504:
                return CONFIG.MESSAGES.ERROR.SERVER_ERROR;
            default:
                return this.message || CONFIG.MESSAGES.ERROR.UNKNOWN;
        }
    }
}

// Create global API client instance
const api = new APIClient();

// Add automatic token refresh interceptor
api.addResponseInterceptor(async (response, data) => {
    if (response.status === 401 && api.token) {
        try {
            await api.refreshToken();
            // Retry the original request would go here in a more sophisticated implementation
        } catch (error) {
            // Redirect to login if refresh fails
            window.location.href = '/admin';
            throw error;
        }
    }
});

// Export API client
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { APIClient, APIError, api };
}

// Make API client globally available
window.api = api;
window.APIError = APIError;