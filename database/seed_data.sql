-- =====================================================
-- DỮ LIỆU MẪU CHO HỆ THỐNG 7tỷ.vn
-- Created: 2025-01-27
-- Description: Dữ liệu mẫu để test và demo hệ thống
-- =====================================================

-- Xóa dữ liệu cũ (nếu có)
TRUNCATE TABLE lich_su_hoat_dong CASCADE;
TRUNCATE TABLE phe_duyet CASCADE;
TRUNCATE TABLE giao_dich CASCADE;
TRUNCATE TABLE hoa_don_dien CASCADE;
TRUNCATE TABLE tai_khoan_ngan_hang CASCADE;
TRUNCATE TABLE the_tin_dung CASCADE;
TRUNCATE TABLE khach_the CASCADE;
TRUNCATE TABLE dai_ly CASCADE;
TRUNCATE TABLE nhan_vien CASCADE;
TRUNCATE TABLE nguoi_dung CASCADE;
TRUNCATE TABLE nha_cung_cap_dien CASCADE;
TRUNCATE TABLE cau_hinh_he_thong CASCADE;

-- Reset sequences
ALTER SEQUENCE IF EXISTS nha_cung_cap_dien_id_seq RESTART WITH 1;

-- =====================================================
-- DỮ LIỆU CƠ BẢN
-- =====================================================

-- Nhà cung cấp điện
INSERT INTO nha_cung_cap_dien (id, ten_nha_cung_cap, ma_nha_cung_cap, vung_phuc_vu) VALUES
(188, 'Công ty Điện lực TP. Hồ Chí Minh', 'HCMC', 'TP. Hồ Chí Minh'),
(187, 'Tổng Công ty Điện lực Miền Nam', 'EVNSPC', 'Miền Nam'),
(189, 'Tổng Công ty Điện lực Miền Bắc', 'EVNNPC', 'Hà Nội và Miền Bắc'),
(190, 'Tổng Công ty Điện lực Miền Trung', 'EVNCPC', 'Miền Trung');

-- Cấu hình hệ thống
INSERT INTO cau_hinh_he_thong (khoa, gia_tri, mo_ta, loai_du_lieu) VALUES
('he_thong.ten', '7tỷ.vn', 'Tên hệ thống', 'string'),
('he_thong.phien_ban', '1.0.0', 'Phiên bản hệ thống', 'string'),
('he_thong.logo', '/assets/logo.png', 'Đường dẫn logo hệ thống', 'string'),
('giao_dich.phi_toi_thieu', '1000', 'Phí giao dịch tối thiểu (VND)', 'number'),
('giao_dich.phi_toi_da', '500000', 'Phí giao dịch tối đa (VND)', 'number'),
('rut_tien.so_tien_toi_thieu', '500000', 'Số tiền rút tối thiểu (VND)', 'number'),
('nap_tien.menh_gia', '[1000000, 2000000, 5000000, 10000000]', 'Các mệnh giá nạp tiền', 'json'),
('thong_bao.email_admin', 'admin@7ty.vn', 'Email quản trị viên', 'string'),
('thong_bao.sdt_hotline', '0855409876', 'Số điện thoại hotline', 'string'),
('ngan_hang.ten', 'Vietcombank', 'Tên ngân hàng nhận chuyển khoản', 'string'),
('ngan_hang.so_tk', '0123456789', 'Số tài khoản nhận chuyển khoản', 'string'),
('ngan_hang.chu_tk', 'CONG TY 7TY', 'Chủ tài khoản', 'string');

-- =====================================================
-- NGƯỜI DÙNG HỆ THỐNG
-- =====================================================

-- Admin
INSERT INTO nguoi_dung (
    id, ten_dang_nhap, mat_khau_hash, vai_tro, ho_ten, 
    so_dien_thoai, email, dia_chi, trang_thai
) VALUES (
    '694cd936-5b31-4931-a65c-d1f601eea037',
    'admin',
    '$2b$12$LQv3c1yqBwlVHpPjrPyFUOeCjmVdEzDxAJd/.OFrdJ9jNXfqrVzfW', -- admin123
    'quan_tri_vien',
    'Quản trị viên hệ thống',
    '0855409876',
    'admin@7ty.vn',
    'Tầng 10, Tòa nhà ABC, Quận 1, TP.HCM',
    'hoat_dong'
);

-- Nhân viên
INSERT INTO nguoi_dung (
    id, ten_dang_nhap, mat_khau_hash, vai_tro, ho_ten, 
    so_dien_thoai, email, dia_chi, so_cmnd, trang_thai
) VALUES 
(
    uuid_generate_v4(),
    'nhanvien01',
    '$2b$12$LQv3c1yqBwlVHpPjrPyFUOeCjmVdEzDxAJd/.OFrdJ9jNXfqrVzfW', -- admin123
    'nhan_vien',
    'Nguyễn Văn An',
    '0901234567',
    'nhanvien01@7ty.vn',
    '123 Đường Lê Lợi, Quận 1, TP.HCM',
    '123456789',
    'hoat_dong'
),
(
    uuid_generate_v4(),
    'nhanvien02',
    '$2b$12$LQv3c1yqBwlVHpPjrPyFUOeCjmVdEzDxAJd/.OFrdJ9jNXfqrVzfW', -- admin123
    'nhan_vien',
    'Trần Thị Bình',
    '0907654321',
    'nhanvien02@7ty.vn',
    '456 Đường Nguyễn Huệ, Quận 1, TP.HCM',
    '987654321',
    'hoat_dong'
);

-- Thêm thông tin nhân viên
INSERT INTO nhan_vien (nguoi_dung_id, ma_nhan_vien, chuc_vu, phong_ban, luong_co_ban, ngay_vao_lam)
SELECT 
    id, 'NV001', 'Trưởng phòng kinh doanh', 'Phòng kinh doanh', 20000000, '2024-01-15'
FROM nguoi_dung WHERE ten_dang_nhap = 'nhanvien01';

INSERT INTO nhan_vien (nguoi_dung_id, ma_nhan_vien, chuc_vu, phong_ban, luong_co_ban, ngay_vao_lam)
SELECT 
    id, 'NV002', 'Nhân viên kinh doanh', 'Phòng kinh doanh', 15000000, '2024-02-01'
FROM nguoi_dung WHERE ten_dang_nhap = 'nhanvien02';

-- Đại lý
INSERT INTO nguoi_dung (
    id, ten_dang_nhap, mat_khau_hash, vai_tro, ho_ten, 
    so_dien_thoai, email, dia_chi, so_cmnd, ngay_sinh, gioi_tinh, trang_thai
) VALUES 
(
    uuid_generate_v4(),
    'daily01',
    '$2b$12$LQv3c1yqBwlVHpPjrPyFUOeCjmVdEzDxAJd/.OFrdJ9jNXfqrVzfW', -- admin123
    'dai_ly',
    'Lê Văn Cường',
    '0912345678',
    'daily01@7ty.vn',
    '789 Đường Điện Biên Phủ, Quận 3, TP.HCM',
    '234567890',
    '1985-05-15',
    'Nam',
    'hoat_dong'
),
(
    uuid_generate_v4(),
    'daily02',
    '$2b$12$LQv3c1yqBwlVHpPjrPyFUOeCjmVdEzDxAJd/.OFrdJ9jNXfqrVzfW', -- admin123
    'dai_ly',
    'Phạm Thị Dung',
    '0923456789',
    'daily02@7ty.vn',
    '321 Đường Cách Mạng Tháng 8, Quận 10, TP.HCM',
    '345678901',
    '1990-08-20',
    'Nữ',
    'hoat_dong'
),
(
    uuid_generate_v4(),
    'daily03',
    '$2b$12$LQv3c1yqBwlVHpPjrPyFUOeCjmVdEzDxAJd/.OFrdJ9jNXfqrVzfW', -- admin123
    'dai_ly',
    'Hoàng Minh Tuấn',
    '0934567890',
    'daily03@7ty.vn',
    '654 Đường Võ Văn Tần, Quận 3, TP.HCM',
    '456789012',
    '1988-12-10',
    'Nam',
    'hoat_dong'
);

-- Thêm thông tin đại lý
INSERT INTO dai_ly (
    nguoi_dung_id, ma_dai_ly, ten_dai_ly, ten_chu_dai_ly, 
    so_dien_thoai_chu, dia_chi_kinh_doanh, so_du_vi, diem_thuong,
    ty_le_hoa_hong, nhan_vien_cham_soc_id, ngay_dang_ky
)
SELECT 
    nd.id, '912345678', 'Đại lý Cường Phát', 'Lê Văn Cường',
    '0912345678', '789 Đường Điện Biên Phủ, Quận 3, TP.HCM', 
    8500000, 125.5, 0.015, nv.id, '2024-03-01'
FROM nguoi_dung nd, nhan_vien nv
WHERE nd.ten_dang_nhap = 'daily01' AND nv.ma_nhan_vien = 'NV001';

INSERT INTO dai_ly (
    nguoi_dung_id, ma_dai_ly, ten_dai_ly, ten_chu_dai_ly, 
    so_dien_thoai_chu, dia_chi_kinh_doanh, so_du_vi, diem_thuong,
    ty_le_hoa_hong, nhan_vien_cham_soc_id, ngay_dang_ky
)
SELECT 
    nd.id, '923456789', 'Đại lý Dung Thịnh', 'Phạm Thị Dung',
    '0923456789', '321 Đường Cách Mạng Tháng 8, Quận 10, TP.HCM', 
    12000000, 89.2, 0.012, nv.id, '2024-04-15'
FROM nguoi_dung nd, nhan_vien nv
WHERE nd.ten_dang_nhap = 'daily02' AND nv.ma_nhan_vien = 'NV002';

INSERT INTO dai_ly (
    nguoi_dung_id, ma_dai_ly, ten_dai_ly, ten_chu_dai_ly, 
    so_dien_thoai_chu, dia_chi_kinh_doanh, so_du_vi, diem_thuong,
    ty_le_hoa_hong, nhan_vien_cham_soc_id, ngay_dang_ky
)
SELECT 
    nd.id, '934567890', 'Đại lý Tuấn Anh', 'Hoàng Minh Tuấn',
    '0934567890', '654 Đường Võ Văn Tần, Quận 3, TP.HCM', 
    6750000, 156.8, 0.018, nv.id, '2024-05-20'
FROM nguoi_dung nd, nhan_vien nv
WHERE nd.ten_dang_nhap = 'daily03' AND nv.ma_nhan_vien = 'NV001';

-- Khách thẻ
INSERT INTO nguoi_dung (
    id, ten_dang_nhap, mat_khau_hash, vai_tro, ho_ten, 
    so_dien_thoai, email, dia_chi, so_cmnd, ngay_sinh, gioi_tinh, trang_thai
) VALUES 
(
    uuid_generate_v4(),
    'khachthe01',
    '$2b$12$LQv3c1yqBwlVHpPjrPyFUOeCjmVdEzDxAJd/.OFrdJ9jNXfqrVzfW', -- admin123
    'khach_the',
    'Nguyễn Thị Hoa',
    '0945678901',
    'khachthe01@gmail.com',
    '147 Đường Pasteur, Quận 1, TP.HCM',
    '567890123',
    '1992-03-25',
    'Nữ',
    'hoat_dong'
),
(
    uuid_generate_v4(),
    'khachthe02',
    '$2b$12$LQv3c1yqBwlVHpPjrPyFUOeCjmVdEzDxAJd/.OFrdJ9jNXfqrVzfW', -- admin123
    'khach_the',
    'Võ Minh Khang',
    '0956789012',
    'khachthe02@gmail.com',
    '258 Đường Hai Bà Trưng, Quận 3, TP.HCM',
    '678901234',
    '1987-11-12',
    'Nam',
    'hoat_dong'
),
(
    uuid_generate_v4(),
    'khachthe03',
    '$2b$12$LQv3c1yqBwlVHpPjrPyFUOeCjmVdEzDxAJd/.OFrdJ9jNXfqrVzfW', -- admin123
    'khach_the',
    'Đặng Thị Lan',
    '0967890123',
    'khachthe03@gmail.com',
    '369 Đường Trần Hưng Đạo, Quận 5, TP.HCM',
    '789012345',
    '1995-07-08',
    'Nữ',
    'hoat_dong'
);

-- Thêm thông tin khách thẻ
INSERT INTO khach_the (nguoi_dung_id, ma_khach_the, so_du_vi, tong_chi_tieu, ngay_dang_ky)
SELECT 
    id, '945678901', 3250000, 15600000, '2024-06-10'
FROM nguoi_dung WHERE ten_dang_nhap = 'khachthe01';

INSERT INTO khach_the (nguoi_dung_id, ma_khach_the, so_du_vi, tong_chi_tieu, ngay_dang_ky)
SELECT 
    id, '956789012', 1890000, 8750000, '2024-07-22'
FROM nguoi_dung WHERE ten_dang_nhap = 'khachthe02';

INSERT INTO khach_the (nguoi_dung_id, ma_khach_the, so_du_vi, tong_chi_tieu, ngay_dang_ky)
SELECT 
    id, '967890123', 4100000, 22300000, '2024-08-05'
FROM nguoi_dung WHERE ten_dang_nhap = 'khachthe03';

-- =====================================================
-- THẺ TÍN DỤNG
-- =====================================================

-- Thẻ của khách thẻ 01
INSERT INTO the_tin_dung (
    khach_the_id, so_the, ten_ngan_hang, dong_the, ngay_het_han,
    ngay_chot_sao_ke, loai_mien_lai, han_muc_the, uu_dai, 
    ten_thiet_bi_quan_ly, so_tien_can_dao, so_tien_da_dao
)
SELECT 
    id, '****-****-****-1234', 'Vietcombank', 'Visa Platinum',
    '2028-03-31', 15, 'mien_lai_55', 80000000,
    'Miễn phí thường niên, tích điểm đổi quà', 'iPhone 15 Pro Max',
    12500000, 8200000
FROM khach_the WHERE ma_khach_the = '945678901';

INSERT INTO the_tin_dung (
    khach_the_id, so_the, ten_ngan_hang, dong_the, ngay_het_han,
    ngay_chot_sao_ke, loai_mien_lai, han_muc_the, uu_dai, 
    ten_thiet_bi_quan_ly, so_tien_can_dao, so_tien_da_dao
)
SELECT 
    id, '****-****-****-5678', 'Techcombank', 'Mastercard World',
    '2027-11-30', 25, 'mien_lai_45', 50000000,
    'Cashback 1.5%, miễn phí sân bay', 'Samsung Galaxy S24 Ultra',
    6800000, 3400000
FROM khach_the WHERE ma_khach_the = '945678901';

-- Thẻ của khách thẻ 02
INSERT INTO the_tin_dung (
    khach_the_id, so_the, ten_ngan_hang, dong_the, ngay_het_han,
    ngay_chot_sao_ke, loai_mien_lai, han_muc_the, uu_dai, 
    ten_thiet_bi_quan_ly, so_tien_can_dao, so_tien_da_dao, tinh_trang
)
SELECT 
    id, '****-****-****-9012', 'BIDV', 'Visa Signature',
    '2029-05-31', 10, 'mien_lai_55', 100000000,
    'Ưu đãi golf, spa, nhà hàng cao cấp', 'MacBook Pro M3',
    18200000, 15600000, 'sat_han'
FROM khach_the WHERE ma_khach_the = '956789012';

-- Thẻ của khách thẻ 03
INSERT INTO the_tin_dung (
    khach_the_id, so_the, ten_ngan_hang, dong_the, ngay_het_han,
    ngay_chot_sao_ke, loai_mien_lai, han_muc_the, uu_dai, 
    ten_thiet_bi_quan_ly, so_tien_can_dao, so_tien_da_dao, tinh_trang
)
SELECT 
    id, '****-****-****-3456', 'ACB', 'Mastercard Platinum',
    '2026-12-31', 5, 'mien_lai_45', 60000000,
    'Tích điểm mua sắm, giảm giá online', 'iPad Pro M2',
    9500000, 9500000, 'dao_xong'
FROM khach_the WHERE ma_khach_the = '967890123';

-- =====================================================
-- TÀI KHOẢN NGÂN HÀNG
-- =====================================================

INSERT INTO tai_khoan_ngan_hang (
    khach_the_id, ten_ngan_hang, so_tai_khoan, ten_chu_tai_khoan, 
    chi_nhanh, la_tai_khoan_chinh
) VALUES
((SELECT id FROM khach_the WHERE ma_khach_the = '945678901'), 
 'Vietcombank', '0123456789', 'NGUYEN THI HOA', 'Chi nhánh Sài Gòn', TRUE),
((SELECT id FROM khach_the WHERE ma_khach_the = '945678901'), 
 'Techcombank', '9876543210', 'NGUYEN THI HOA', 'Chi nhánh TP.HCM', FALSE),
((SELECT id FROM khach_the WHERE ma_khach_the = '956789012'), 
 'BIDV', '1122334455', 'VO MINH KHANG', 'Chi nhánh Đống Đa', TRUE),
((SELECT id FROM khach_the WHERE ma_khach_the = '967890123'), 
 'ACB', '5544332211', 'DANG THI LAN', 'Chi nhánh Quận 5', TRUE);

-- =====================================================
-- HÓA ĐƠN ĐIỆN
-- =====================================================

-- Hóa đơn trong kho (từ đại lý)
INSERT INTO hoa_don_dien (
    ma_khach_hang, ten_khach_hang, dia_chi, nha_cung_cap_id,
    ky_thanh_toan, tien_ky_truoc, tien_ky_nay, dai_ly_nhap_kho_id,
    phi_giao_dich, ma_qr, trang_thai
) VALUES
('8412345678901', 'Nguyễn Văn Nam', '123 Đường ABC, Quận 1, TP.HCM', 188,
 '12/2024', 150000, 280000, (SELECT id FROM dai_ly WHERE ma_dai_ly = '912345678'),
 tinh_phi_giao_dich(430000), 'QR001', 'trong_kho'),
('8498765432100', 'Trần Thị Bích', '456 Đường DEF, Quận 3, TP.HCM', 188,
 '12/2024', 200000, 350000, (SELECT id FROM dai_ly WHERE ma_dai_ly = '912345678'),
 tinh_phi_giao_dich(550000), 'QR002', 'trong_kho'),
('8434567890123', 'Lê Minh Hoàng', '789 Đường GHI, Quận 5, TP.HCM', 188,
 '12/2024', 180000, 420000, (SELECT id FROM dai_ly WHERE ma_dai_ly = '923456789'),
 tinh_phi_giao_dich(600000), 'QR003', 'trong_kho'),
('8456789012345', 'Phạm Thị Lan', '321 Đường JKL, Quận 7, TP.HCM', 187,
 '12/2024', 300000, 450000, (SELECT id FROM dai_ly WHERE ma_dai_ly = '923456789'),
 tinh_phi_giao_dich(750000), 'QR004', 'trong_kho'),
('8478901234567', 'Võ Văn Tài', '654 Đường MNO, Quận 10, TP.HCM', 187,
 '12/2024', 250000, 380000, (SELECT id FROM dai_ly WHERE ma_dai_ly = '934567890'),
 tinh_phi_giao_dich(630000), 'QR005', 'trong_kho');

-- Hóa đơn đã bán
INSERT INTO hoa_don_dien (
    ma_khach_hang, ten_khach_hang, dia_chi, nha_cung_cap_id,
    ky_thanh_toan, tien_ky_truoc, tien_ky_nay, dai_ly_nhap_kho_id,
    khach_the_mua_id, ngay_xuat_kho, phi_giao_dich, ma_qr, 
    anh_bien_nhan, trang_thai, con_no_cuoc
) VALUES
('8490123456789', 'Hoàng Thị Mai', '987 Đường PQR, Quận 2, TP.HCM', 188,
 '11/2024', 120000, 320000, (SELECT id FROM dai_ly WHERE ma_dai_ly = '912345678'),
 (SELECT id FROM khach_the WHERE ma_khach_the = '945678901'), 
 CURRENT_TIMESTAMP - INTERVAL '2 days', tinh_phi_giao_dich(440000), 'QR006',
 '/uploads/receipts/receipt_001.jpg', 'da_ban', FALSE),
('8401234567890', 'Đặng Văn Hùng', '147 Đường STU, Quận 4, TP.HCM', 189,
 '11/2024', 180000, 290000, (SELECT id FROM dai_ly WHERE ma_dai_ly = '923456789'),
 (SELECT id FROM khach_the WHERE ma_khach_the = '956789012'), 
 CURRENT_TIMESTAMP - INTERVAL '1 day', tinh_phi_giao_dich(470000), 'QR007',
 '/uploads/receipts/receipt_002.jpg', 'da_ban', FALSE);

-- =====================================================
-- GIAO DỊCH
-- =====================================================

-- Giao dịch nạp tiền đại lý
INSERT INTO giao_dich (
    ma_giao_dich, loai_giao_dich, nguoi_dung_id, so_tien, phi_giao_dich,
    noi_dung, thong_tin_ngan_hang, trang_thai, ngay_xu_ly
) VALUES
(tao_ma_giao_dich(), 'nap_tien', 
 (SELECT nguoi_dung_id FROM dai_ly WHERE ma_dai_ly = '912345678'),
 5000000, 0, 'Nạp tiền vào ví đại lý - Chuyển khoản',
 '{"ngan_hang": "Vietcombank", "so_tk": "0123456789", "ten_tk": "LE VAN CUONG"}',
 'thanh_cong', CURRENT_TIMESTAMP - INTERVAL '3 days'),
(tao_ma_giao_dich(), 'nap_tien', 
 (SELECT nguoi_dung_id FROM dai_ly WHERE ma_dai_ly = '923456789'),
 8000000, 0, 'Nạp tiền vào ví đại lý - Nhân viên thu',
 '{"phuong_thuc": "nhan_vien_thu", "nhan_vien_id": "NV002"}',
 'thanh_cong', CURRENT_TIMESTAMP - INTERVAL '2 days');

-- Giao dịch thanh toán hóa đơn
INSERT INTO giao_dich (
    ma_giao_dich, loai_giao_dich, nguoi_dung_id, so_tien, phi_giao_dich,
    noi_dung, hoa_don_dien_id, trang_thai, ngay_xu_ly
) VALUES
(tao_ma_giao_dich(), 'thanh_toan', 
 (SELECT nguoi_dung_id FROM khach_the WHERE ma_khach_the = '945678901'),
 440000, tinh_phi_giao_dich(440000), 'Thanh toán hóa đơn điện',
 (SELECT id FROM hoa_don_dien WHERE ma_khach_hang = '8490123456789'),
 'thanh_cong', CURRENT_TIMESTAMP - INTERVAL '2 days'),
(tao_ma_giao_dich(), 'thanh_toan', 
 (SELECT nguoi_dung_id FROM khach_the WHERE ma_khach_the = '956789012'),
 470000, tinh_phi_giao_dich(470000), 'Thanh toán hóa đơn điện',
 (SELECT id FROM hoa_don_dien WHERE ma_khach_hang = '8401234567890'),
 'thanh_cong', CURRENT_TIMESTAMP - INTERVAL '1 day');

-- Giao dịch rút tiền
INSERT INTO giao_dich (
    ma_giao_dich, loai_giao_dich, nguoi_dung_id, so_tien, phi_giao_dich,
    noi_dung, thong_tin_ngan_hang, trang_thai
) VALUES
(tao_ma_giao_dich(), 'rut_tien', 
 (SELECT nguoi_dung_id FROM khach_the WHERE ma_khach_the = '945678901'),
 2000000, 10000, 'Rút tiền về tài khoản ngân hàng',
 '{"ngan_hang": "Vietcombank", "so_tk": "0123456789", "ten_tk": "NGUYEN THI HOA"}',
 'cho_phe_duyet');

-- Giao dịch hoa hồng
INSERT INTO giao_dich (
    ma_giao_dich, loai_giao_dich, nguoi_dung_id, so_tien, phi_giao_dich,
    noi_dung, trang_thai, ngay_xu_ly
) VALUES
(tao_ma_giao_dich(), 'hoa_hong', 
 (SELECT nguoi_dung_id FROM dai_ly WHERE ma_dai_ly = '912345678'),
 6600, 0, 'Hoa hồng từ việc bán hóa đơn điện',
 'thanh_cong', CURRENT_TIMESTAMP - INTERVAL '2 days'),
(tao_ma_giao_dich(), 'hoa_hong', 
 (SELECT nguoi_dung_id FROM dai_ly WHERE ma_dai_ly = '923456789'),
 5640, 0, 'Hoa hồng từ việc bán hóa đơn điện',
 'thanh_cong', CURRENT_TIMESTAMP - INTERVAL '1 day');

-- =====================================================
-- PHÊ DUYỆT
-- =====================================================

-- Yêu cầu phê duyệt đại lý mới
INSERT INTO phe_duyet (
    loai_phe_duyet, nguoi_yeu_cau_id, noi_dung_yeu_cau, trang_thai
) VALUES
('dai_ly_moi', 
 (SELECT id FROM nhan_vien WHERE ma_nhan_vien = 'NV001'),
 '{"ten_dai_ly": "Đại lý Thành Đạt", "ten_chu_dai_ly": "Nguyễn Thành Đạt", "so_dien_thoai": "0978901234", "dia_chi": "159 Đường XYZ, Quận 6, TP.HCM", "so_cmnd": "890123456", "anh_cmnd_truoc": "/uploads/cmnd_truoc.jpg", "anh_cmnd_sau": "/uploads/cmnd_sau.jpg"}',
 'cho_phe_duyet');

-- Yêu cầu phê duyệt nạp tiền
INSERT INTO phe_duyet (
    loai_phe_duyet, nguoi_yeu_cau_id, noi_dung_yeu_cau, trang_thai
) VALUES
('nap_tien', 
 (SELECT nguoi_dung_id FROM dai_ly WHERE ma_dai_ly = '934567890'),
 '{"so_tien": 3000000, "phuong_thuc": "chuyen_khoan", "ngan_hang": "Techcombank", "so_tk": "9988776655", "noi_dung_ck": "nap 3000000 vi 934567890", "anh_bien_lai": "/uploads/bien_lai_001.jpg"}',
 'cho_phe_duyet');

-- Yêu cầu phê duyệt rút tiền
INSERT INTO phe_duyet (
    loai_phe_duyet, nguoi_yeu_cau_id, noi_dung_yeu_cau, trang_thai
) VALUES
('rut_tien', 
 (SELECT nguoi_dung_id FROM khach_the WHERE ma_khach_the = '945678901'),
 '{"so_tien": 2000000, "ngan_hang": "Vietcombank", "so_tk": "0123456789", "ten_tk": "NGUYEN THI HOA", "chi_nhanh": "Chi nhánh Sài Gòn"}',
 'cho_phe_duyet');

-- Yêu cầu đã được phê duyệt
INSERT INTO phe_duyet (
    loai_phe_duyet, nguoi_yeu_cau_id, noi_dung_yeu_cau, trang_thai,
    nguoi_phe_duyet_id, ngay_phe_duyet
) VALUES
('nap_tien', 
 (SELECT nguoi_dung_id FROM dai_ly WHERE ma_dai_ly = '912345678'),
 '{"so_tien": 5000000, "phuong_thuc": "chuyen_khoan", "ngan_hang": "Vietcombank", "so_tk": "0123456789", "noi_dung_ck": "nap 5000000 vi 912345678"}',
 'da_phe_duyet',
 '694cd936-5b31-4931-a65c-d1f601eea037',
 CURRENT_TIMESTAMP - INTERVAL '3 days');

-- =====================================================
-- LỊCH SỬ HOẠT ĐỘNG
-- =====================================================

INSERT INTO lich_su_hoat_dong (
    nguoi_dung_id, hanh_dong, bang_lien_quan, id_ban_ghi, 
    du_lieu_moi, dia_chi_ip
) VALUES
('694cd936-5b31-4931-a65c-d1f601eea037', 'Đăng nhập hệ thống', 'nguoi_dung', 
 '694cd936-5b31-4931-a65c-d1f601eea037', '{"thoi_gian": "2025-01-27 10:30:00"}', '192.168.1.100'),
((SELECT nguoi_dung_id FROM dai_ly WHERE ma_dai_ly = '912345678'), 'Nhập hóa đơn vào kho', 'hoa_don_dien',
 (SELECT id FROM hoa_don_dien WHERE ma_khach_hang = '8412345678901'), 
 '{"ma_khach_hang": "8412345678901", "tong_tien": 430000}', '192.168.1.101'),
((SELECT nguoi_dung_id FROM khach_the WHERE ma_khach_the = '945678901'), 'Thanh toán hóa đơn', 'giao_dich',
 (SELECT id FROM giao_dich WHERE noi_dung LIKE '%8490123456789%'), 
 '{"so_tien": 440000, "phi": 1936}', '192.168.1.102');

COMMIT;

-- Hiển thị thống kê sau khi import
SELECT 'Tổng số người dùng: ' || COUNT(*) FROM nguoi_dung WHERE deleted_at IS NULL;
SELECT 'Tổng số đại lý: ' || COUNT(*) FROM dai_ly WHERE deleted_at IS NULL;
SELECT 'Tổng số khách thẻ: ' || COUNT(*) FROM khach_the WHERE deleted_at IS NULL;
SELECT 'Tổng số hóa đơn: ' || COUNT(*) FROM hoa_don_dien WHERE deleted_at IS NULL;
SELECT 'Tổng số giao dịch: ' || COUNT(*) FROM giao_dich;
SELECT 'Tổng số yêu cầu phê duyệt: ' || COUNT(*) FROM phe_duyet;