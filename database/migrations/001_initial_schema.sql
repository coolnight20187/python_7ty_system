-- =====================================================
-- MIGRATION 001: Initial Schema Creation
-- Created: 2025-01-27
-- Description: Tạo schema ban đầu cho hệ thống 7tỷ.vn
-- =====================================================

-- Chạy schema chính
\i schema.sql

-- =====================================================
-- DỮ LIỆU MẪU - Sample Data
-- =====================================================

-- Thêm nhà cung cấp điện
INSERT INTO nha_cung_cap_dien (id, ten_nha_cung_cap, ma_nha_cung_cap, vung_phuc_vu) VALUES
(188, 'Công ty Điện lực TP. Hồ Chí Minh', 'HCMC', 'TP. Hồ Chí Minh'),
(187, 'Tổng Công ty Điện lực Miền Nam', 'EVNSPC', 'Miền Nam'),
(189, 'Tổng Công ty Điện lực Miền Bắc', 'EVNNPC', 'Hà Nội và Miền Bắc'),
(190, 'Tổng Công ty Điện lực Miền Trung', 'EVNCPC', 'Miền Trung');

-- Thêm cấu hình hệ thống
INSERT INTO cau_hinh_he_thong (khoa, gia_tri, mo_ta, loai_du_lieu) VALUES
('he_thong.ten', '7tỷ.vn', 'Tên hệ thống', 'string'),
('he_thong.phien_ban', '1.0.0', 'Phiên bản hệ thống', 'string'),
('giao_dich.phi_toi_thieu', '1000', 'Phí giao dịch tối thiểu (VND)', 'number'),
('giao_dich.phi_toi_da', '500000', 'Phí giao dịch tối đa (VND)', 'number'),
('rut_tien.so_tien_toi_thieu', '500000', 'Số tiền rút tối thiểu (VND)', 'number'),
('nap_tien.menh_gia', '[1000000, 2000000, 5000000, 10000000]', 'Các mệnh giá nạp tiền', 'json'),
('thong_bao.email_admin', 'admin@7ty.vn', 'Email quản trị viên', 'string'),
('thong_bao.sdt_hotline', '0855409876', 'Số điện thoại hotline', 'string');

-- Tạo tài khoản admin mặc định
INSERT INTO nguoi_dung (
    id, ten_dang_nhap, mat_khau_hash, vai_tro, ho_ten, 
    so_dien_thoai, email, trang_thai
) VALUES (
    '694cd936-5b31-4931-a65c-d1f601eea037',
    'admin',
    '$2b$12$LQv3c1yqBwlVHpPjrPyFUOeCjmVdEzDxAJd/.OFrdJ9jNXfqrVzfW', -- admin123
    'quan_tri_vien',
    'Quản trị viên hệ thống',
    '0855409876',
    'admin@7ty.vn',
    'hoat_dong'
);

-- Tạo nhân viên mẫu
INSERT INTO nguoi_dung (
    ten_dang_nhap, mat_khau_hash, vai_tro, ho_ten, 
    so_dien_thoai, email, trang_thai
) VALUES (
    'nhanvien01',
    '$2b$12$LQv3c1yqBwlVHpPjrPyFUOeCjmVdEzDxAJd/.OFrdJ9jNXfqrVzfW', -- admin123
    'nhan_vien',
    'Nguyễn Văn A',
    '0901234567',
    'nhanvien01@7ty.vn',
    'hoat_dong'
);

INSERT INTO nhan_vien (
    nguoi_dung_id, ma_nhan_vien, chuc_vu, phong_ban, luong_co_ban
) SELECT 
    id, 'NV001', 'Nhân viên kinh doanh', 'Phòng kinh doanh', 15000000
FROM nguoi_dung WHERE ten_dang_nhap = 'nhanvien01';

-- Tạo đại lý mẫu
INSERT INTO nguoi_dung (
    ten_dang_nhap, mat_khau_hash, vai_tro, ho_ten, 
    so_dien_thoai, email, dia_chi, trang_thai
) VALUES (
    'daily01',
    '$2b$12$LQv3c1yqBwlVHpPjrPyFUOeCjmVdEzDxAJd/.OFrdJ9jNXfqrVzfW', -- admin123
    'dai_ly',
    'Trần Thị B',
    '0912345678',
    'daily01@7ty.vn',
    '123 Đường ABC, Quận 1, TP.HCM',
    'hoat_dong'
);

INSERT INTO dai_ly (
    nguoi_dung_id, ma_dai_ly, ten_dai_ly, ten_chu_dai_ly, 
    so_dien_thoai_chu, dia_chi_kinh_doanh, so_du_vi, 
    nhan_vien_cham_soc_id
) SELECT 
    nd.id, '912345678', 'Đại lý ABC', 'Trần Thị B',
    '0912345678', '123 Đường ABC, Quận 1, TP.HCM', 5000000,
    nv.id
FROM nguoi_dung nd, nhan_vien nv
WHERE nd.ten_dang_nhap = 'daily01' 
AND nv.ma_nhan_vien = 'NV001';

-- Tạo khách thẻ mẫu
INSERT INTO nguoi_dung (
    ten_dang_nhap, mat_khau_hash, vai_tro, ho_ten, 
    so_dien_thoai, email, dia_chi, trang_thai
) VALUES (
    'khachthe01',
    '$2b$12$LQv3c1yqBwlVHpPjrPyFUOeCjmVdEzDxAJd/.OFrdJ9jNXfqrVzfW', -- admin123
    'khach_the',
    'Lê Văn C',
    '0923456789',
    'khachthe01@7ty.vn',
    '456 Đường XYZ, Quận 3, TP.HCM',
    'hoat_dong'
);

INSERT INTO khach_the (
    nguoi_dung_id, ma_khach_the, so_du_vi
) SELECT 
    id, '923456789', 2000000
FROM nguoi_dung WHERE ten_dang_nhap = 'khachthe01';

-- Tạo thẻ tín dụng mẫu
INSERT INTO the_tin_dung (
    khach_the_id, so_the, ten_ngan_hang, dong_the, 
    ngay_het_han, ngay_chot_sao_ke, loai_mien_lai, 
    han_muc_the, uu_dai, ten_thiet_bi_quan_ly
) SELECT 
    id, '****-****-****-1234', 'Vietcombank', 'Visa Platinum',
    '2027-12-31', 15, 'mien_lai_55', 50000000,
    'Miễn phí thường niên năm đầu', 'iPhone 15 Pro'
FROM khach_the WHERE ma_khach_the = '923456789';

-- Tạo hóa đơn điện mẫu
INSERT INTO hoa_don_dien (
    ma_khach_hang, ten_khach_hang, dia_chi, nha_cung_cap_id,
    ky_thanh_toan, tien_ky_truoc, tien_ky_nay, 
    dai_ly_nhap_kho_id, phi_giao_dich
) SELECT 
    '8412345678901', 'Nguyễn Văn D', '789 Đường DEF, Quận 5, TP.HCM', 188,
    '12/2024', 150000, 280000,
    dl.id, tinh_phi_giao_dich(430000)
FROM dai_ly dl WHERE ma_dai_ly = '912345678';

INSERT INTO hoa_don_dien (
    ma_khach_hang, ten_khach_hang, dia_chi, nha_cung_cap_id,
    ky_thanh_toan, tien_ky_truoc, tien_ky_nay, 
    dai_ly_nhap_kho_id, phi_giao_dich
) SELECT 
    '8498765432100', 'Phạm Thị E', '321 Đường GHI, Quận 7, TP.HCM', 188,
    '12/2024', 200000, 350000,
    dl.id, tinh_phi_giao_dich(550000)
FROM dai_ly dl WHERE ma_dai_ly = '912345678';

-- Tạo giao dịch mẫu
INSERT INTO giao_dich (
    ma_giao_dich, loai_giao_dich, nguoi_dung_id, so_tien,
    phi_giao_dich, noi_dung, trang_thai
) SELECT 
    tao_ma_giao_dich(), 'nap_tien', nd.id, 5000000,
    0, 'Nạp tiền vào ví đại lý', 'thanh_cong'
FROM nguoi_dung nd WHERE ten_dang_nhap = 'daily01';

INSERT INTO giao_dich (
    ma_giao_dich, loai_giao_dich, nguoi_dung_id, so_tien,
    phi_giao_dich, noi_dung, trang_thai
) SELECT 
    tao_ma_giao_dich(), 'nap_tien', nd.id, 2000000,
    0, 'Nạp tiền vào ví khách thẻ', 'thanh_cong'
FROM nguoi_dung nd WHERE ten_dang_nhap = 'khachthe01';

-- Tạo tài khoản ngân hàng mẫu
INSERT INTO tai_khoan_ngan_hang (
    khach_the_id, ten_ngan_hang, so_tai_khoan, 
    ten_chu_tai_khoan, chi_nhanh, la_tai_khoan_chinh
) SELECT 
    id, 'Vietcombank', '0123456789', 'LE VAN C',
    'Chi nhánh Sài Gòn', TRUE
FROM khach_the WHERE ma_khach_the = '923456789';

-- Tạo yêu cầu phê duyệt mẫu
INSERT INTO phe_duyet (
    loai_phe_duyet, nguoi_yeu_cau_id, noi_dung_yeu_cau, trang_thai
) SELECT 
    'nap_tien', nd.id, 
    '{"so_tien": 3000000, "phuong_thuc": "chuyen_khoan", "ghi_chu": "Nạp tiền để mua hóa đơn"}',
    'cho_phe_duyet'
FROM nguoi_dung nd WHERE ten_dang_nhap = 'daily01';

COMMIT;