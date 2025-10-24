-- 7tỷ.vn Sample Data for Testing
-- Insert demo users, agents, customers, bills, and transactions

\c ty7_db;

-- Insert demo users
INSERT INTO users (id, username, password_hash, full_name, phone, email, role, is_active) VALUES
    ('550e8400-e29b-41d4-a716-446655440000', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3L3jzjvG4i', 'Quản trị viên', '0901234567', 'admin@7ty.vn', 'admin', true),
    ('550e8400-e29b-41d4-a716-446655440001', 'demo', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3L3jzjvG4i', 'Đại lý Demo', '0987654321', 'demo@7ty.vn', 'agent', true),
    ('550e8400-e29b-41d4-a716-446655440002', 'agent001', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3L3jzjvG4i', 'Nguyễn Văn A', '0912345678', 'agent001@7ty.vn', 'agent', true),
    ('550e8400-e29b-41d4-a716-446655440003', 'agent002', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3L3jzjvG4i', 'Trần Thị B', '0923456789', 'agent002@7ty.vn', 'agent', true)
ON CONFLICT (id) DO NOTHING;

-- Insert demo agents
INSERT INTO agents (id, user_id, code, name, phone, email, region, commission_rate, wallet_balance, total_sales, total_commission, status) VALUES
    ('660e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440001', 'AG001', 'Đại lý Demo', '0987654321', 'demo@7ty.vn', 'south', 1.5, 500000000, 10000000000, 150000000, 'active'),
    ('660e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440002', 'AG002', 'Nguyễn Văn A', '0912345678', 'agent001@7ty.vn', 'north', 1.0, 200000000, 5000000000, 50000000, 'active'),
    ('660e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440003', 'AG003', 'Trần Thị B', '0923456789', 'agent002@7ty.vn', 'central', 1.2, 300000000, 7500000000, 90000000, 'active')
ON CONFLICT (id) DO NOTHING;

-- Insert demo customers
INSERT INTO customers (id, name, phone, email, address, total_purchases, order_count) VALUES
    ('770e8400-e29b-41d4-a716-446655440001', 'Lê Văn C', '0123456789', 'customer1@example.com', 'Số 123, Đường ABC, Quận 1, TP.HCM', 2500000000, 15),
    ('770e8400-e29b-41d4-a716-446655440002', 'Phạm Thị D', '0987654321', 'customer2@example.com', 'Số 456, Đường XYZ, Quận 2, TP.HCM', 1800000000, 12),
    ('770e8400-e29b-41d4-a716-446655440003', 'Hoàng Văn E', '0345678901', 'customer3@example.com', 'Số 789, Đường DEF, Quận 3, TP.HCM', 3200000000, 20),
    ('770e8400-e29b-41d4-a716-446655440004', 'Ngô Thị F', '0567890123', 'customer4@example.com', 'Số 101, Đường GHI, Quận 4, TP.HCM', 1500000000, 8),
    ('770e8400-e29b-41d4-a716-446655440005', 'Vũ Văn G', '0789012345', 'customer5@example.com', 'Số 202, Đường JKL, Quận 5, TP.HCM', 2100000000, 14)
ON CONFLICT (id) DO NOTHING;

-- Insert demo bills
INSERT INTO bills (id, customer_code, customer_name, address, provider_id, provider_name, period, previous_amount, current_amount, total_amount, status, due_date, added_by) VALUES
    ('880e8400-e29b-41d4-a716-446655440001', '8412345678901', 'Lê Văn C', 'Số 123, Đường ABC, Quận 1, TP.HCM', '188', 'TP. Hồ Chí Minh', '12/2024', 15000000, 18500000, 33500000, 'available', '2024-12-31', '550e8400-e29b-41d4-a716-446655440000'),
    ('880e8400-e29b-41d4-a716-446655440002', '8498765432100', 'Phạm Thị D', 'Số 456, Đường XYZ, Quận 2, TP.HCM', '188', 'TP. Hồ Chí Minh', '12/2024', 12000000, 16200000, 28200000, 'available', '2024-12-31', '550e8400-e29b-41d4-a716-446655440000'),
    ('880e8400-e29b-41d4-a716-446655440003', '8434567890123', 'Hoàng Văn E', 'Số 789, Đường DEF, Quận 3, TP.HCM', '187', 'Điện Miền Nam', '12/2024', 20000000, 24800000, 44800000, 'reserved', '2024-12-31', '550e8400-e29b-41d4-a716-446655440000'),
    ('880e8400-e29b-41d4-a716-446655440004', '8456789012345', 'Ngô Thị F', 'Số 101, Đường GHI, Quận 4, TP.HCM', '189', 'Hà Nội', '12/2024', 8500000, 11200000, 19700000, 'available', '2024-12-31', '550e8400-e29b-41d4-a716-446655440000'),
    ('880e8400-e29b-41d4-a716-446655440005', '8478901234567', 'Vũ Văn G', 'Số 202, Đường JKL, Quận 5, TP.HCM', '190', 'Miền Trung', '12/2024', 17500000, 21300000, 38800000, 'sold', '2024-12-31', '550e8400-e29b-41d4-a716-446655440000'),
    ('880e8400-e29b-41d4-a716-446655440006', '8401234567890', 'Khách hàng Test 1', 'Số 303, Đường Test, Quận 6, TP.HCM', '188', 'TP. Hồ Chí Minh', '12/2024', 13500000, 17800000, 31300000, 'available', '2024-12-31', '550e8400-e29b-41d4-a716-446655440000'),
    ('880e8400-e29b-41d4-a716-446655440007', '8409876543210', 'Khách hàng Test 2', 'Số 404, Đường Test, Quận 7, TP.HCM', '187', 'Điện Miền Nam', '12/2024', 19200000, 23600000, 42800000, 'available', '2024-12-31', '550e8400-e29b-41d4-a716-446655440000')
ON CONFLICT (id) DO NOTHING;

-- Insert demo transactions
INSERT INTO transactions (id, transaction_code, type, amount, description, agent_id, customer_id, bill_id, payment_method, status, processed_at, commission_amount) VALUES
    ('990e8400-e29b-41d4-a716-446655440001', 'TX20241201120001', 'payment', 33500000, 'Thanh toán tiền điện - 8412345678901', '660e8400-e29b-41d4-a716-446655440001', '770e8400-e29b-41d4-a716-446655440001', '880e8400-e29b-41d4-a716-446655440001', 'momo', 'completed', NOW() - INTERVAL '2 days', 502500),
    ('990e8400-e29b-41d4-a716-446655440002', 'TX20241201120002', 'payment', 28200000, 'Thanh toán tiền điện - 8498765432100', '660e8400-e29b-41d4-a716-446655440001', '770e8400-e29b-41d4-a716-446655440002', '880e8400-e29b-41d4-a716-446655440002', 'banking', 'completed', NOW() - INTERVAL '1 day', 423000),
    ('990e8400-e29b-41d4-a716-446655440003', 'TX20241201120003', 'topup', 100000000, 'Nạp tiền vào ví', '660e8400-e29b-41d4-a716-446655440002', NULL, NULL, 'banking', 'completed', NOW() - INTERVAL '3 hours', 0),
    ('990e8400-e29b-41d4-a716-446655440004', 'TX20241201120004', 'commission', 502500, 'Hoa hồng từ giao dịch TX20241201120001', '660e8400-e29b-41d4-a716-446655440001', NULL, NULL, 'wallet', 'completed', NOW() - INTERVAL '2 days', 0),
    ('990e8400-e29b-41d4-a716-446655440005', 'TX20241201120005', 'commission', 423000, 'Hoa hồng từ giao dịch TX20241201120002', '660e8400-e29b-41d4-a716-446655440001', NULL, NULL, 'wallet', 'completed', NOW() - INTERVAL '1 day', 0),
    ('990e8400-e29b-41d4-a716-446655440006', 'TX20241201120006', 'payment', 38800000, 'Thanh toán tiền điện - 8478901234567', '660e8400-e29b-41d4-a716-446655440003', '770e8400-e29b-41d4-a716-446655440005', '880e8400-e29b-41d4-a716-446655440005', 'zalopay', 'completed', NOW() - INTERVAL '6 hours', 465600)
ON CONFLICT (id) DO NOTHING;

-- Insert wallet transactions
INSERT INTO wallet_transactions (agent_id, transaction_id, type, amount, balance_before, balance_after, description) VALUES
    ('660e8400-e29b-41d4-a716-446655440001', '990e8400-e29b-41d4-a716-446655440004', 'credit', 502500, 499497500, 500000000, 'Hoa hồng từ giao dịch TX20241201120001'),
    ('660e8400-e29b-41d4-a716-446655440001', '990e8400-e29b-41d4-a716-446655440005', 'credit', 423000, 499577000, 500000000, 'Hoa hồng từ giao dịch TX20241201120002'),
    ('660e8400-e29b-41d4-a716-446655440002', '990e8400-e29b-41d4-a716-446655440003', 'credit', 100000000, 100000000, 200000000, 'Nạp tiền vào ví'),
    ('660e8400-e29b-41d4-a716-446655440003', '990e8400-e29b-41d4-a716-446655440006', 'credit', 465600, 299534400, 300000000, 'Hoa hồng từ giao dịch TX20241201120006')
ON CONFLICT DO NOTHING;

-- Insert notifications
INSERT INTO notifications (user_id, title, message, type, is_read) VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 'Chào mừng đến với 7tỷ.vn!', 'Tài khoản của bạn đã được kích hoạt thành công.', 'success', false),
    ('550e8400-e29b-41d4-a716-446655440001', 'Giao dịch thành công', 'Bạn đã nhận được hoa hồng 502.500 VND từ giao dịch TX20241201120001', 'info', false),
    ('550e8400-e29b-41d4-a716-446655440002', 'Nạp tiền thành công', 'Tài khoản của bạn đã được nạp 1.000.000 VND', 'success', true),
    ('550e8400-e29b-41d4-a716-446655440000', 'Hệ thống hoạt động bình thường', 'Tất cả các dịch vụ đang hoạt động ổn định.', 'info', true)
ON CONFLICT DO NOTHING;

-- Update bill statuses based on transactions
UPDATE bills SET 
    status = 'sold',
    sold_at = NOW() - INTERVAL '2 days',
    sold_by = '660e8400-e29b-41d4-a716-446655440001'
WHERE id IN ('880e8400-e29b-41d4-a716-446655440001', '880e8400-e29b-41d4-a716-446655440002');

UPDATE bills SET 
    status = 'reserved',
    reserved_at = NOW() - INTERVAL '1 hour',
    reserved_by = '660e8400-e29b-41d4-a716-446655440002'
WHERE id = '880e8400-e29b-41d4-a716-446655440003';

-- Create views for reporting
CREATE OR REPLACE VIEW agent_performance AS
SELECT 
    a.id,
    a.code,
    a.name,
    a.region,
    a.commission_rate,
    a.wallet_balance,
    a.total_sales,
    a.total_commission,
    COUNT(t.id) as transaction_count,
    COALESCE(SUM(CASE WHEN t.type = 'payment' AND t.status = 'completed' THEN t.amount ELSE 0 END), 0) as total_payments,
    COALESCE(SUM(CASE WHEN t.type = 'commission' AND t.status = 'completed' THEN t.amount ELSE 0 END), 0) as total_earned_commission,
    a.created_at,
    a.updated_at
FROM agents a
LEFT JOIN transactions t ON a.id = t.agent_id
WHERE a.status = 'active'
GROUP BY a.id, a.code, a.name, a.region, a.commission_rate, a.wallet_balance, a.total_sales, a.total_commission, a.created_at, a.updated_at;

CREATE OR REPLACE VIEW daily_revenue AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as transaction_count,
    SUM(CASE WHEN type = 'payment' AND status = 'completed' THEN amount ELSE 0 END) as total_revenue,
    SUM(CASE WHEN type = 'commission' AND status = 'completed' THEN amount ELSE 0 END) as total_commission,
    COUNT(DISTINCT agent_id) as active_agents,
    COUNT(DISTINCT customer_id) as active_customers
FROM transactions
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Sample data inserted successfully!';
    RAISE NOTICE '👥 Created % users, % agents, % customers', 
        (SELECT COUNT(*) FROM users),
        (SELECT COUNT(*) FROM agents),
        (SELECT COUNT(*) FROM customers);
    RAISE NOTICE '📋 Created % bills, % transactions', 
        (SELECT COUNT(*) FROM bills),
        (SELECT COUNT(*) FROM transactions);
    RAISE NOTICE '🚀 Demo accounts ready:';
    RAISE NOTICE '   Admin: admin / admin123';
    RAISE NOTICE '   Agent: demo / 123456 (5M VND wallet)';
    RAISE NOTICE '   Test phones: 0123456789, 0987654321';
END $$;