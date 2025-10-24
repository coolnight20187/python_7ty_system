// 7tỷ.vn Admin Interface - Configuration
// API endpoints and system configuration

const CONFIG = {
    // API Configuration
    API_BASE_URL: window.location.origin,
    API_ENDPOINTS: {
        // Authentication
        LOGIN: '/api/auth/login',
        LOGOUT: '/api/auth/logout',
        ME: '/api/auth/me',
        REFRESH_TOKEN: '/api/auth/refresh-token',
        
        // Dashboard
        DASHBOARD_STATS: '/api/admin/dashboard/stats',
        RECENT_ACTIVITIES: '/api/admin/activities/recent',
        PENDING_APPROVALS: '/api/approvals?status=cho_phe_duyet',
        
        // Agents
        AGENTS: '/api/agent',
        AGENTS_PENDING: '/api/approvals?type=dai_ly_moi',
        AGENTS_EXPORT: '/api/agent/export',
        
        // Bills
        BILLS: '/api/bills',
        BILLS_WAREHOUSE: '/api/bills/warehouse',
        BILLS_LOOKUP: '/api/bills/lookup',
        BILLS_BULK_LOOKUP: '/api/bills/bulk-lookup',
        BILLS_EXPORT: '/api/bills/export-warehouse',
        PROVIDERS: '/api/bills/providers',
        
        // Customers
        CUSTOMERS: '/api/customer',
        CUSTOMERS_PENDING: '/api/approvals?type=khach_the_moi',
        CREDIT_CARDS: '/api/customer/cards',
        CARDS_NEAR_DUE: '/api/customer/cards/near-due',
        
        // Transactions
        TRANSACTIONS: '/api/transactions',
        
        // Approvals
        APPROVALS: '/api/approvals',
        APPROVE: '/api/approvals/{id}/approve',
        REJECT: '/api/approvals/{id}/reject',
        
        // Staff
        STAFF: '/api/admin/staff',
        
        // Files
        FILE_UPLOAD: '/api/files/upload',
        
        // System
        HEALTH: '/health',
        SETTINGS: '/api/admin/settings'
    },
    
    // Application Settings
    APP: {
        NAME: '7tỷ.vn',
        VERSION: '2.0.0',
        DESCRIPTION: 'Hệ Thống Quản Trị Thanh Toán Hóa Đơn Điện',
        COPYRIGHT: '© 2025 7tỷ.vn. All rights reserved.',
        SUPPORT_PHONE: '085.540.9876',
        SUPPORT_EMAIL: 'admin@7ty.vn'
    },
    
    // UI Configuration
    UI: {
        ITEMS_PER_PAGE: 20,
        MAX_BULK_LOOKUP: 1000,
        AUTO_REFRESH_INTERVAL: 30000, // 30 seconds
        TOAST_DURATION: 5000, // 5 seconds
        MODAL_ANIMATION_DURATION: 300,
        TABLE_ANIMATION_DURATION: 200
    },
    
    // Vietnamese Localization
    MESSAGES: {
        // Success Messages
        SUCCESS: {
            LOGIN: 'Đăng nhập thành công!',
            LOGOUT: 'Đăng xuất thành công!',
            SAVE: 'Lưu thành công!',
            DELETE: 'Xóa thành công!',
            APPROVE: 'Phê duyệt thành công!',
            REJECT: 'Từ chối thành công!',
            EXPORT: 'Xuất dữ liệu thành công!',
            UPLOAD: 'Tải lên thành công!',
            COPY: 'Sao chép thành công!'
        },
        
        // Error Messages
        ERROR: {
            LOGIN_FAILED: 'Đăng nhập thất bại. Vui lòng kiểm tra lại thông tin.',
            NETWORK_ERROR: 'Lỗi kết nối mạng. Vui lòng thử lại.',
            SERVER_ERROR: 'Lỗi máy chủ. Vui lòng liên hệ quản trị viên.',
            UNAUTHORIZED: 'Bạn không có quyền truy cập.',
            VALIDATION_ERROR: 'Dữ liệu không hợp lệ.',
            NOT_FOUND: 'Không tìm thấy dữ liệu.',
            TIMEOUT: 'Hết thời gian chờ. Vui lòng thử lại.',
            UNKNOWN: 'Đã xảy ra lỗi không xác định.'
        },
        
        // Warning Messages
        WARNING: {
            UNSAVED_CHANGES: 'Bạn có thay đổi chưa lưu. Bạn có muốn tiếp tục?',
            DELETE_CONFIRM: 'Bạn có chắc chắn muốn xóa?',
            LOGOUT_CONFIRM: 'Bạn có chắc chắn muốn đăng xuất?',
            LARGE_DATA: 'Dữ liệu lớn có thể mất thời gian xử lý.',
            BULK_LIMIT: `Tối đa ${1000} mã khách hàng cho mỗi lần tra cứu.`
        },
        
        // Info Messages
        INFO: {
            LOADING: 'Đang tải dữ liệu...',
            PROCESSING: 'Đang xử lý...',
            SEARCHING: 'Đang tìm kiếm...',
            UPLOADING: 'Đang tải lên...',
            EXPORTING: 'Đang xuất dữ liệu...',
            NO_DATA: 'Không có dữ liệu.',
            EMPTY_RESULT: 'Không tìm thấy kết quả nào.',
            SELECT_ITEMS: 'Vui lòng chọn ít nhất một mục.'
        }
    },
    
    // Status Mappings
    STATUS: {
        // User Roles
        ROLES: {
            'quan_tri_vien': 'Quản Trị Viên',
            'nhan_vien': 'Nhân Viên',
            'dai_ly': 'Đại Lý',
            'khach_the': 'Khách Thẻ'
        },
        
        // Account Status
        ACCOUNT_STATUS: {
            'hoat_dong': { text: 'Hoạt Động', class: 'success' },
            'tam_khoa': { text: 'Tạm Khóa', class: 'warning' },
            'da_xoa': { text: 'Đã Xóa', class: 'danger' }
        },
        
        // Approval Status
        APPROVAL_STATUS: {
            'cho_phe_duyet': { text: 'Chờ Phê Duyệt', class: 'warning' },
            'da_phe_duyet': { text: 'Đã Phê Duyệt', class: 'success' },
            'tu_choi': { text: 'Từ Chối', class: 'danger' },
            'huy_bo': { text: 'Hủy Bỏ', class: 'secondary' }
        },
        
        // Transaction Status
        TRANSACTION_STATUS: {
            'cho_xu_ly': { text: 'Chờ Xử Lý', class: 'warning' },
            'dang_xu_ly': { text: 'Đang Xử Lý', class: 'info' },
            'thanh_cong': { text: 'Thành Công', class: 'success' },
            'that_bai': { text: 'Thất Bại', class: 'danger' },
            'huy_bo': { text: 'Hủy Bỏ', class: 'secondary' }
        },
        
        // Bill Status
        BILL_STATUS: {
            'trong_kho': { text: 'Trong Kho', class: 'info' },
            'da_ban': { text: 'Đã Bán', class: 'success' },
            'het_han': { text: 'Hết Hạn', class: 'danger' },
            'loi': { text: 'Lỗi', class: 'danger' }
        },
        
        // Card Status
        CARD_STATUS: {
            'binh_thuong': { text: 'Bình Thường', class: 'success' },
            'da_co_sao_ke': { text: 'Đã Có Sao Kê', class: 'info' },
            'sat_han': { text: 'Sát Hạn', class: 'warning' },
            'dao_xong': { text: 'Đáo Xong', class: 'success' }
        }
    },
    
    // Format Configuration
    FORMAT: {
        // Date formats
        DATE_FORMAT: 'DD/MM/YYYY',
        DATETIME_FORMAT: 'DD/MM/YYYY HH:mm:ss',
        TIME_FORMAT: 'HH:mm:ss',
        
        // Number formats
        CURRENCY_FORMAT: {
            style: 'currency',
            currency: 'VND',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        },
        
        NUMBER_FORMAT: {
            minimumFractionDigits: 0,
            maximumFractionDigits: 2
        },
        
        PERCENTAGE_FORMAT: {
            style: 'percent',
            minimumFractionDigits: 1,
            maximumFractionDigits: 2
        }
    },
    
    // Validation Rules
    VALIDATION: {
        PHONE_REGEX: /^[0-9]{10,11}$/,
        EMAIL_REGEX: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
        ID_NUMBER_REGEX: /^[0-9]{9,12}$/,
        CUSTOMER_CODE_REGEX: /^84[0-9]{11}$/,
        PASSWORD_MIN_LENGTH: 6,
        USERNAME_MIN_LENGTH: 3,
        MAX_FILE_SIZE: 5 * 1024 * 1024, // 5MB
        ALLOWED_IMAGE_TYPES: ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    },
    
    // Storage Keys
    STORAGE_KEYS: {
        TOKEN: 'ty7_admin_token',
        USER: 'ty7_admin_user',
        PREFERENCES: 'ty7_admin_preferences',
        DEVICE_MODE: 'ty7_device_mode',
        SIDEBAR_STATE: 'ty7_sidebar_state',
        TABLE_SETTINGS: 'ty7_table_settings'
    },
    
    // Device Modes
    DEVICE_MODES: {
        PC: 'pc',
        MOBILE: 'mobile'
    },
    
    // Theme Configuration
    THEME: {
        PRIMARY_COLOR: '#2d4a2b',
        ACCENT_COLOR: '#cd7f32',
        SUCCESS_COLOR: '#28a745',
        WARNING_COLOR: '#ffc107',
        DANGER_COLOR: '#dc3545',
        INFO_COLOR: '#17a2b8'
    }
};

// Export configuration for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}

// Make config globally available
window.CONFIG = CONFIG;