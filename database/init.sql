-- 7tỷ.vn Database Initialization Script
-- PostgreSQL Database Schema

-- Create database if not exists (handled by Docker)
-- CREATE DATABASE IF NOT EXISTS ty7_db;

-- Connect to the database
\c ty7_db;

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create custom types
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('admin', 'agent', 'customer');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE transaction_type AS ENUM ('payment', 'topup', 'commission', 'withdrawal', 'refund');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE transaction_status AS ENUM ('pending', 'completed', 'failed', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE bill_status AS ENUM ('available', 'reserved', 'sold', 'expired');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE agent_status AS ENUM ('active', 'inactive', 'suspended');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    role user_role DEFAULT 'agent',
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agents table
CREATE TABLE IF NOT EXISTS agents (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    region VARCHAR(50) DEFAULT 'south',
    commission_rate DECIMAL(5,2) DEFAULT 1.0,
    wallet_balance BIGINT DEFAULT 0, -- Stored in VND cents
    total_sales BIGINT DEFAULT 0,
    total_commission BIGINT DEFAULT 0,
    status agent_status DEFAULT 'active',
    kyc_verified BOOLEAN DEFAULT false,
    kyc_documents JSONB DEFAULT '{}',
    bank_info JSONB DEFAULT '{}',
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    zalo VARCHAR(50),
    bank_info JSONB DEFAULT '{}',
    address TEXT,
    total_purchases BIGINT DEFAULT 0, -- VND cents
    order_count INTEGER DEFAULT 0,
    loyalty_points INTEGER DEFAULT 0,
    is_vip BOOLEAN DEFAULT false,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Bills table (Warehouse)
CREATE TABLE IF NOT EXISTS bills (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    customer_code VARCHAR(13) NOT NULL,
    customer_name VARCHAR(100) NOT NULL,
    address TEXT NOT NULL,
    provider_id VARCHAR(10) NOT NULL,
    provider_name VARCHAR(100),
    period VARCHAR(10) NOT NULL,
    previous_amount BIGINT DEFAULT 0, -- VND cents
    current_amount BIGINT NOT NULL,   -- VND cents
    total_amount BIGINT NOT NULL,     -- VND cents
    status bill_status DEFAULT 'available',
    due_date DATE,
    added_by UUID REFERENCES users(id),
    assigned_customer_id UUID REFERENCES customers(id),
    reserved_at TIMESTAMP WITH TIME ZONE,
    reserved_by UUID REFERENCES agents(id),
    sold_at TIMESTAMP WITH TIME ZONE,
    sold_by UUID REFERENCES agents(id),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    transaction_code VARCHAR(20) UNIQUE NOT NULL,
    type transaction_type NOT NULL,
    amount BIGINT NOT NULL, -- VND cents
    description TEXT,
    agent_id UUID REFERENCES agents(id),
    customer_id UUID REFERENCES customers(id),
    bill_id UUID REFERENCES bills(id),
    payment_method VARCHAR(50),
    payment_reference VARCHAR(100), -- External payment reference
    status transaction_status DEFAULT 'pending',
    processed_at TIMESTAMP WITH TIME ZONE,
    commission_amount BIGINT DEFAULT 0,
    fee_amount BIGINT DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Wallet transactions (for detailed wallet history)
CREATE TABLE IF NOT EXISTS wallet_transactions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    transaction_id UUID REFERENCES transactions(id),
    type VARCHAR(20) NOT NULL, -- 'credit', 'debit'
    amount BIGINT NOT NULL, -- VND cents
    balance_before BIGINT NOT NULL,
    balance_after BIGINT NOT NULL,
    description TEXT,
    reference VARCHAR(100),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Settings table (System configuration)
CREATE TABLE IF NOT EXISTS settings (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    category VARCHAR(50) DEFAULT 'general',
    is_public BOOLEAN DEFAULT false,
    data_type VARCHAR(20) DEFAULT 'string', -- 'string', 'number', 'boolean', 'json'
    validation_rules JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit logs table (for tracking changes)
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    action VARCHAR(50) NOT NULL,
    table_name VARCHAR(50) NOT NULL,
    record_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    session_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(20) DEFAULT 'info', -- 'info', 'success', 'warning', 'error'
    is_read BOOLEAN DEFAULT false,
    action_url TEXT,
    expires_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- API keys table (for external integrations)
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    key_hash VARCHAR(255) NOT NULL,
    permissions JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    last_used TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_by UUID REFERENCES users(id),
    rate_limit INTEGER DEFAULT 1000, -- requests per hour
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

CREATE INDEX IF NOT EXISTS idx_agents_code ON agents(code);
CREATE INDEX IF NOT EXISTS idx_agents_user_id ON agents(user_id);
CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
CREATE INDEX IF NOT EXISTS idx_agents_region ON agents(region);

CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone);
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_customers_created_at ON customers(created_at);

CREATE INDEX IF NOT EXISTS idx_bills_customer_code ON bills(customer_code);
CREATE INDEX IF NOT EXISTS idx_bills_status ON bills(status);
CREATE INDEX IF NOT EXISTS idx_bills_provider_id ON bills(provider_id);
CREATE INDEX IF NOT EXISTS idx_bills_period ON bills(period);
CREATE INDEX IF NOT EXISTS idx_bills_created_at ON bills(created_at);
CREATE INDEX IF NOT EXISTS idx_bills_due_date ON bills(due_date);

CREATE INDEX IF NOT EXISTS idx_transactions_code ON transactions(transaction_code);
CREATE INDEX IF NOT EXISTS idx_transactions_agent_id ON transactions(agent_id);
CREATE INDEX IF NOT EXISTS idx_transactions_customer_id ON transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_transactions_bill_id ON transactions(bill_id);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at);

CREATE INDEX IF NOT EXISTS idx_wallet_transactions_agent_id ON wallet_transactions(agent_id);
CREATE INDEX IF NOT EXISTS idx_wallet_transactions_created_at ON wallet_transactions(created_at);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_table_name ON audit_logs(table_name);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);

CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);

-- Create functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_agents_updated_at ON agents;
CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON agents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_customers_updated_at ON customers;
CREATE TRIGGER update_customers_updated_at BEFORE UPDATE ON customers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_bills_updated_at ON bills;
CREATE TRIGGER update_bills_updated_at BEFORE UPDATE ON bills FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_transactions_updated_at ON transactions;
CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON transactions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_settings_updated_at ON settings;
CREATE TRIGGER update_settings_updated_at BEFORE UPDATE ON settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to generate transaction code
CREATE OR REPLACE FUNCTION generate_transaction_code()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.transaction_code IS NULL OR NEW.transaction_code = '' THEN
        NEW.transaction_code := 'TX' || TO_CHAR(NOW(), 'YYYYMMDDHH24MISS') || LPAD(EXTRACT(MICROSECONDS FROM NOW())::TEXT, 6, '0');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for transaction code generation
DROP TRIGGER IF EXISTS generate_transaction_code_trigger ON transactions;
CREATE TRIGGER generate_transaction_code_trigger
    BEFORE INSERT ON transactions
    FOR EACH ROW
    EXECUTE FUNCTION generate_transaction_code();

-- Insert default settings
INSERT INTO settings (key, value, description, category, is_public, data_type) VALUES
    ('system_name', '7tỷ.vn', 'Tên hệ thống', 'general', true, 'string'),
    ('system_version', '2.0.0-docker', 'Phiên bản hệ thống', 'general', true, 'string'),
    ('maintenance_mode', 'false', 'Chế độ bảo trì', 'general', false, 'boolean'),
    ('default_commission_rate', '1.0', 'Tỷ lệ hoa hồng mặc định (%)', 'commission', false, 'number'),
    ('max_bill_amount', '10000000', 'Số tiền hóa đơn tối đa (VND)', 'limits', false, 'number'),
    ('session_timeout', '1440', 'Thời gian timeout session (phút)', 'security', false, 'number'),
    ('api_rate_limit', '100', 'Giới hạn API requests/phút', 'security', false, 'number'),
    ('backup_retention_days', '30', 'Số ngày lưu trữ backup', 'backup', false, 'number'),
    ('email_notifications', 'true', 'Bật thông báo email', 'notifications', false, 'boolean'),
    ('sms_notifications', 'false', 'Bật thông báo SMS', 'notifications', false, 'boolean'),
    ('realtime_sync', 'true', 'Bật đồng bộ real-time', 'features', false, 'boolean'),
    ('auto_backup', 'true', 'Tự động backup', 'backup', false, 'boolean')
ON CONFLICT (key) DO NOTHING;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Database schema initialized successfully!';
    RAISE NOTICE '📊 Created % tables with indexes and triggers', 
        (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE');
    RAISE NOTICE '🚀 Ready for 7tỷ.vn system!';
END $$;