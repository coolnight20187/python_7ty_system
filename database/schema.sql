-- =====================================================
-- HỆ THỐNG CƠ SỞ DỮ LIỆU 7tỷ.vn
-- Vietnamese Electric Bill Payment & Agent Management System
-- Created: 2025-01-27
-- Version: 1.0.0
-- =====================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- ENUMS - Định nghĩa các trạng thái và loại
-- =====================================================

-- Vai trò người dùng
CREATE TYPE vai_tro_nguoi_dung AS ENUM (
    'quan_tri_vien',    -- Quản trị viên
    'nhan_vien',        -- Nhân viên
    'dai_ly',           -- Đại lý
    'khach_the'         -- Khách thẻ
);

-- Trạng thái tài khoản
CREATE TYPE trang_thai_tai_khoan AS ENUM (
    'hoat_dong',        -- Hoạt động
    'tam_khoa',         -- Tạm khóa
    'da_xoa'            -- Đã xóa
);

-- Trạng thái phê duyệt
CREATE TYPE trang_thai_phe_duyet AS ENUM (
    'cho_phe_duyet',    -- Chờ phê duyệt
    'da_phe_duyet',     -- Đã phê duyệt
    'tu_choi',          -- Từ chối
    'huy_bo'            -- Hủy bỏ
);

-- Loại giao dịch
CREATE TYPE loai_giao_dich AS ENUM (
    'nap_tien',         -- Nạp tiền
    'rut_tien',         -- Rút tiền
    'thanh_toan',       -- Thanh toán
    'hoa_hong',         -- Hoa hồng
    'hoan_tien'         -- Hoàn tiền
);

-- Trạng thái giao dịch
CREATE TYPE trang_thai_giao_dich AS ENUM (
    'cho_xu_ly',        -- Chờ xử lý
    'dang_xu_ly',       -- Đang xử lý
    'thanh_cong',       -- Thành công
    'that_bai',         -- Thất bại
    'huy_bo'            -- Hủy bỏ
);

-- Trạng thái hóa đơn
CREATE TYPE trang_thai_hoa_don AS ENUM (
    'trong_kho',        -- Trong kho
    'da_ban',           -- Đã bán
    'het_han',          -- Hết hạn
    'loi'               -- Lỗi
);

-- Loại phê duyệt
CREATE TYPE loai_phe_duyet AS ENUM (
    'dai_ly_moi',       -- Đại lý mới
    'khach_the_moi',    -- Khách thẻ mới
    'nap_tien',         -- Nạp tiền
    'rut_tien',         -- Rút tiền
    'the_moi'           -- Thẻ mới
);

-- Tình trạng thẻ tín dụng
CREATE TYPE tinh_trang_the AS ENUM (
    'binh_thuong',      -- Bình thường
    'da_co_sao_ke',     -- Đã có sao kê
    'sat_han',          -- Sát hạn
    'dao_xong'          -- Đáo xong
);

-- Loại miễn lãi
CREATE TYPE loai_mien_lai AS ENUM (
    'mien_lai_45',      -- 45 ngày
    'mien_lai_55'       -- 55 ngày
);

-- =====================================================
-- BẢNG CHÍNH - Main Tables
-- =====================================================

-- Bảng người dùng (Users)
CREATE TABLE nguoi_dung (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ten_dang_nhap VARCHAR(50) UNIQUE NOT NULL,
    mat_khau_hash VARCHAR(255) NOT NULL,
    vai_tro vai_tro_nguoi_dung NOT NULL DEFAULT 'khach_the',
    trang_thai trang_thai_tai_khoan NOT NULL DEFAULT 'hoat_dong',
    ho_ten VARCHAR(100),
    so_dien_thoai VARCHAR(15) UNIQUE,
    email VARCHAR(100),
    ngay_sinh DATE,
    gioi_tinh VARCHAR(10),
    dia_chi TEXT,
    so_cmnd VARCHAR(20),
    ngay_cap_cmnd DATE,
    noi_cap_cmnd VARCHAR(100),
    anh_dai_dien TEXT,
    anh_cmnd_mat_truoc TEXT,
    anh_cmnd_mat_sau TEXT,
    lan_dang_nhap_cuoi TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- Bảng nhân viên (Staff)
CREATE TABLE nhan_vien (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nguoi_dung_id UUID NOT NULL REFERENCES nguoi_dung(id) ON DELETE CASCADE,
    ma_nhan_vien VARCHAR(20) UNIQUE NOT NULL,
    chuc_vu VARCHAR(50),
    phong_ban VARCHAR(50),
    luong_co_ban DECIMAL(15,2) DEFAULT 0,
    ngay_vao_lam DATE,
    trang_thai trang_thai_tai_khoan NOT NULL DEFAULT 'hoat_dong',
    ghi_chu TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- Bảng đại lý (Agents)
CREATE TABLE dai_ly (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nguoi_dung_id UUID NOT NULL REFERENCES nguoi_dung(id) ON DELETE CASCADE,
    ma_dai_ly VARCHAR(20) UNIQUE NOT NULL, -- Số điện thoại không có số 0 đầu
    ten_dai_ly VARCHAR(100) NOT NULL,
    ten_chu_dai_ly VARCHAR(100) NOT NULL,
    so_dien_thoai_chu VARCHAR(15) NOT NULL,
    dia_chi_kinh_doanh TEXT,
    so_du_vi DECIMAL(15,2) DEFAULT 0,
    diem_thuong DECIMAL(10,2) DEFAULT 0,
    ty_le_hoa_hong DECIMAL(5,4) DEFAULT 0.01, -- 1% mặc định
    nhan_vien_cham_soc_id UUID REFERENCES nhan_vien(id),
    trang_thai trang_thai_tai_khoan NOT NULL DEFAULT 'hoat_dong',
    ngay_dang_ky DATE DEFAULT CURRENT_DATE,
    ghi_chu TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- Bảng khách thẻ (Credit Card Customers)
CREATE TABLE khach_the (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nguoi_dung_id UUID NOT NULL REFERENCES nguoi_dung(id) ON DELETE CASCADE,
    ma_khach_the VARCHAR(20) UNIQUE NOT NULL, -- Số điện thoại không có số 0 đầu
    so_du_vi DECIMAL(15,2) DEFAULT 0,
    tong_chi_tieu DECIMAL(15,2) DEFAULT 0,
    trang_thai trang_thai_tai_khoan NOT NULL DEFAULT 'hoat_dong',
    ngay_dang_ky DATE DEFAULT CURRENT_DATE,
    ghi_chu TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- Bảng thẻ tín dụng (Credit Cards)
CREATE TABLE the_tin_dung (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    khach_the_id UUID NOT NULL REFERENCES khach_the(id) ON DELETE CASCADE,
    so_the VARCHAR(19) NOT NULL, -- Số thẻ được mã hóa
    ten_ngan_hang VARCHAR(100) NOT NULL,
    dong_the VARCHAR(50),
    ngay_het_han DATE NOT NULL,
    cvv VARCHAR(4), -- Được mã hóa
    ngay_chot_sao_ke INTEGER NOT NULL CHECK (ngay_chot_sao_ke BETWEEN 1 AND 31),
    loai_mien_lai loai_mien_lai NOT NULL DEFAULT 'mien_lai_45',
    han_muc_the DECIMAL(15,2) NOT NULL,
    uu_dai TEXT,
    ten_thiet_bi_quan_ly VARCHAR(100),
    tinh_trang tinh_trang_the DEFAULT 'binh_thuong',
    so_tien_can_dao DECIMAL(15,2) DEFAULT 0,
    so_tien_da_dao DECIMAL(15,2) DEFAULT 0,
    ngay_cuoi_thanh_toan DATE,
    trang_thai trang_thai_tai_khoan NOT NULL DEFAULT 'hoat_dong',
    ghi_chu TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- Bảng nhà cung cấp điện (Electric Providers)
CREATE TABLE nha_cung_cap_dien (
    id INTEGER PRIMARY KEY,
    ten_nha_cung_cap VARCHAR(100) NOT NULL,
    ma_nha_cung_cap VARCHAR(10) NOT NULL,
    vung_phuc_vu VARCHAR(100),
    api_endpoint TEXT,
    trang_thai trang_thai_tai_khoan NOT NULL DEFAULT 'hoat_dong',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bảng hóa đơn điện (Electric Bills)
CREATE TABLE hoa_don_dien (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ma_khach_hang VARCHAR(20) NOT NULL,
    ten_khach_hang VARCHAR(100) NOT NULL,
    dia_chi TEXT,
    nha_cung_cap_id INTEGER REFERENCES nha_cung_cap_dien(id),
    ky_thanh_toan VARCHAR(10), -- MM/YYYY
    tien_ky_truoc DECIMAL(15,2) DEFAULT 0,
    tien_ky_nay DECIMAL(15,2) NOT NULL,
    tong_tien DECIMAL(15,2) GENERATED ALWAYS AS (tien_ky_truoc + tien_ky_nay) STORED,
    dai_ly_nhap_kho_id UUID REFERENCES dai_ly(id),
    nhan_vien_nhap_kho_id UUID REFERENCES nhan_vien(id),
    ngay_nhap_kho TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    khach_the_mua_id UUID REFERENCES khach_the(id),
    ngay_xuat_kho TIMESTAMP,
    phi_giao_dich DECIMAL(15,2), -- Phí 0.005% - 1.8%
    anh_bien_nhan TEXT,
    ma_qr TEXT, -- Mã QR của hóa đơn
    trang_thai trang_thai_hoa_don NOT NULL DEFAULT 'trong_kho',
    con_no_cuoc BOOLEAN DEFAULT TRUE, -- Trạng thái nợ cước
    ghi_chu TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- Bảng giao dịch (Transactions)
CREATE TABLE giao_dich (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ma_giao_dich VARCHAR(50) UNIQUE NOT NULL,
    loai_giao_dich loai_giao_dich NOT NULL,
    nguoi_dung_id UUID NOT NULL REFERENCES nguoi_dung(id),
    so_tien DECIMAL(15,2) NOT NULL,
    phi_giao_dich DECIMAL(15,2) DEFAULT 0,
    so_tien_thuc_nhan DECIMAL(15,2) GENERATED ALWAYS AS (so_tien - phi_giao_dich) STORED,
    noi_dung TEXT,
    thong_tin_ngan_hang JSONB, -- Thông tin chuyển khoản
    trang_thai trang_thai_giao_dich NOT NULL DEFAULT 'cho_xu_ly',
    hoa_don_dien_id UUID REFERENCES hoa_don_dien(id),
    nguoi_xu_ly_id UUID REFERENCES nguoi_dung(id),
    ngay_xu_ly TIMESTAMP,
    ghi_chu TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bảng phê duyệt (Approvals)
CREATE TABLE phe_duyet (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    loai_phe_duyet loai_phe_duyet NOT NULL,
    nguoi_yeu_cau_id UUID NOT NULL REFERENCES nguoi_dung(id),
    noi_dung_yeu_cau JSONB NOT NULL, -- Chi tiết yêu cầu
    trang_thai trang_thai_phe_duyet NOT NULL DEFAULT 'cho_phe_duyet',
    nguoi_phe_duyet_id UUID REFERENCES nguoi_dung(id),
    ngay_phe_duyet TIMESTAMP,
    ly_do_tu_choi TEXT,
    ghi_chu TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bảng lịch sử hoạt động (Activity Log)
CREATE TABLE lich_su_hoat_dong (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nguoi_dung_id UUID NOT NULL REFERENCES nguoi_dung(id),
    hanh_dong VARCHAR(100) NOT NULL,
    bang_lien_quan VARCHAR(50),
    id_ban_ghi UUID,
    du_lieu_cu JSONB,
    du_lieu_moi JSONB,
    dia_chi_ip INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bảng tài khoản ngân hàng (Bank Accounts)
CREATE TABLE tai_khoan_ngan_hang (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    khach_the_id UUID NOT NULL REFERENCES khach_the(id) ON DELETE CASCADE,
    ten_ngan_hang VARCHAR(100) NOT NULL,
    so_tai_khoan VARCHAR(50) NOT NULL,
    ten_chu_tai_khoan VARCHAR(100) NOT NULL,
    chi_nhanh VARCHAR(100),
    la_tai_khoan_chinh BOOLEAN DEFAULT FALSE,
    trang_thai trang_thai_tai_khoan NOT NULL DEFAULT 'hoat_dong',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- Bảng cấu hình hệ thống (System Settings)
CREATE TABLE cau_hinh_he_thong (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    khoa VARCHAR(100) UNIQUE NOT NULL,
    gia_tri TEXT NOT NULL,
    mo_ta TEXT,
    loai_du_lieu VARCHAR(20) DEFAULT 'string', -- string, number, boolean, json
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- INDEXES - Tối ưu hóa hiệu suất
-- =====================================================

-- Indexes cho bảng người dùng
CREATE INDEX idx_nguoi_dung_ten_dang_nhap ON nguoi_dung(ten_dang_nhap);
CREATE INDEX idx_nguoi_dung_so_dien_thoai ON nguoi_dung(so_dien_thoai);
CREATE INDEX idx_nguoi_dung_vai_tro ON nguoi_dung(vai_tro);
CREATE INDEX idx_nguoi_dung_trang_thai ON nguoi_dung(trang_thai);
CREATE INDEX idx_nguoi_dung_deleted_at ON nguoi_dung(deleted_at);

-- Indexes cho bảng đại lý
CREATE INDEX idx_dai_ly_ma_dai_ly ON dai_ly(ma_dai_ly);
CREATE INDEX idx_dai_ly_nhan_vien_cham_soc ON dai_ly(nhan_vien_cham_soc_id);
CREATE INDEX idx_dai_ly_trang_thai ON dai_ly(trang_thai);
CREATE INDEX idx_dai_ly_deleted_at ON dai_ly(deleted_at);

-- Indexes cho bảng khách thẻ
CREATE INDEX idx_khach_the_ma_khach_the ON khach_the(ma_khach_the);
CREATE INDEX idx_khach_the_trang_thai ON khach_the(trang_thai);
CREATE INDEX idx_khach_the_deleted_at ON khach_the(deleted_at);

-- Indexes cho bảng thẻ tín dụng
CREATE INDEX idx_the_tin_dung_khach_the_id ON the_tin_dung(khach_the_id);
CREATE INDEX idx_the_tin_dung_ngay_chot_sao_ke ON the_tin_dung(ngay_chot_sao_ke);
CREATE INDEX idx_the_tin_dung_tinh_trang ON the_tin_dung(tinh_trang);
CREATE INDEX idx_the_tin_dung_deleted_at ON the_tin_dung(deleted_at);

-- Indexes cho bảng hóa đơn điện
CREATE INDEX idx_hoa_don_dien_ma_khach_hang ON hoa_don_dien(ma_khach_hang);
CREATE INDEX idx_hoa_don_dien_nha_cung_cap ON hoa_don_dien(nha_cung_cap_id);
CREATE INDEX idx_hoa_don_dien_trang_thai ON hoa_don_dien(trang_thai);
CREATE INDEX idx_hoa_don_dien_dai_ly_nhap_kho ON hoa_don_dien(dai_ly_nhap_kho_id);
CREATE INDEX idx_hoa_don_dien_khach_the_mua ON hoa_don_dien(khach_the_mua_id);
CREATE INDEX idx_hoa_don_dien_tong_tien ON hoa_don_dien(tong_tien);
CREATE INDEX idx_hoa_don_dien_ngay_nhap_kho ON hoa_don_dien(ngay_nhap_kho);
CREATE INDEX idx_hoa_don_dien_deleted_at ON hoa_don_dien(deleted_at);

-- Indexes cho bảng giao dịch
CREATE INDEX idx_giao_dich_ma_giao_dich ON giao_dich(ma_giao_dich);
CREATE INDEX idx_giao_dich_nguoi_dung_id ON giao_dich(nguoi_dung_id);
CREATE INDEX idx_giao_dich_loai_giao_dich ON giao_dich(loai_giao_dich);
CREATE INDEX idx_giao_dich_trang_thai ON giao_dich(trang_thai);
CREATE INDEX idx_giao_dich_created_at ON giao_dich(created_at);

-- Indexes cho bảng phê duyệt
CREATE INDEX idx_phe_duyet_loai_phe_duyet ON phe_duyet(loai_phe_duyet);
CREATE INDEX idx_phe_duyet_nguoi_yeu_cau ON phe_duyet(nguoi_yeu_cau_id);
CREATE INDEX idx_phe_duyet_trang_thai ON phe_duyet(trang_thai);
CREATE INDEX idx_phe_duyet_created_at ON phe_duyet(created_at);

-- Indexes cho bảng lịch sử hoạt động
CREATE INDEX idx_lich_su_nguoi_dung_id ON lich_su_hoat_dong(nguoi_dung_id);
CREATE INDEX idx_lich_su_hanh_dong ON lich_su_hoat_dong(hanh_dong);
CREATE INDEX idx_lich_su_created_at ON lich_su_hoat_dong(created_at);

-- =====================================================
-- TRIGGERS - Tự động cập nhật timestamps
-- =====================================================

-- Function để cập nhật updated_at
CREATE OR REPLACE FUNCTION cap_nhat_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Tạo triggers cho tất cả bảng có updated_at
CREATE TRIGGER trigger_nguoi_dung_updated_at
    BEFORE UPDATE ON nguoi_dung
    FOR EACH ROW
    EXECUTE FUNCTION cap_nhat_updated_at();

CREATE TRIGGER trigger_nhan_vien_updated_at
    BEFORE UPDATE ON nhan_vien
    FOR EACH ROW
    EXECUTE FUNCTION cap_nhat_updated_at();

CREATE TRIGGER trigger_dai_ly_updated_at
    BEFORE UPDATE ON dai_ly
    FOR EACH ROW
    EXECUTE FUNCTION cap_nhat_updated_at();

CREATE TRIGGER trigger_khach_the_updated_at
    BEFORE UPDATE ON khach_the
    FOR EACH ROW
    EXECUTE FUNCTION cap_nhat_updated_at();

CREATE TRIGGER trigger_the_tin_dung_updated_at
    BEFORE UPDATE ON the_tin_dung
    FOR EACH ROW
    EXECUTE FUNCTION cap_nhat_updated_at();

CREATE TRIGGER trigger_hoa_don_dien_updated_at
    BEFORE UPDATE ON hoa_don_dien
    FOR EACH ROW
    EXECUTE FUNCTION cap_nhat_updated_at();

CREATE TRIGGER trigger_giao_dich_updated_at
    BEFORE UPDATE ON giao_dich
    FOR EACH ROW
    EXECUTE FUNCTION cap_nhat_updated_at();

CREATE TRIGGER trigger_phe_duyet_updated_at
    BEFORE UPDATE ON phe_duyet
    FOR EACH ROW
    EXECUTE FUNCTION cap_nhat_updated_at();

CREATE TRIGGER trigger_tai_khoan_ngan_hang_updated_at
    BEFORE UPDATE ON tai_khoan_ngan_hang
    FOR EACH ROW
    EXECUTE FUNCTION cap_nhat_updated_at();

CREATE TRIGGER trigger_cau_hinh_he_thong_updated_at
    BEFORE UPDATE ON cau_hinh_he_thong
    FOR EACH ROW
    EXECUTE FUNCTION cap_nhat_updated_at();

-- =====================================================
-- FUNCTIONS - Các hàm hỗ trợ business logic
-- =====================================================

-- Function tính phí giao dịch dựa trên mệnh giá
CREATE OR REPLACE FUNCTION tinh_phi_giao_dich(so_tien DECIMAL)
RETURNS DECIMAL AS $$
BEGIN
    -- Công thức: 1đ - 20.000.000đ tương đương 0.005% - 1.8%
    -- Sử dụng công thức tuyến tính
    IF so_tien <= 1 THEN
        RETURN so_tien * 0.00005; -- 0.005%
    ELSIF so_tien >= 20000000 THEN
        RETURN so_tien * 0.018; -- 1.8%
    ELSE
        -- Tính phí theo tỷ lệ tuyến tính
        RETURN so_tien * (0.00005 + (so_tien - 1) / 19999999 * (0.018 - 0.00005));
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Function tính ngày cuối thanh toán thẻ
CREATE OR REPLACE FUNCTION tinh_ngay_cuoi_thanh_toan(
    ngay_chot INTEGER, 
    loai_mien_lai loai_mien_lai,
    thang INTEGER DEFAULT EXTRACT(MONTH FROM CURRENT_DATE),
    nam INTEGER DEFAULT EXTRACT(YEAR FROM CURRENT_DATE)
)
RETURNS DATE AS $$
DECLARE
    ngay_chot_date DATE;
    so_ngay_them INTEGER;
BEGIN
    -- Tạo ngày chốt sao kê
    ngay_chot_date := make_date(nam, thang, ngay_chot);
    
    -- Xác định số ngày thêm dựa trên loại miễn lãi
    IF loai_mien_lai = 'mien_lai_45' THEN
        so_ngay_them := 15;
    ELSE -- mien_lai_55
        so_ngay_them := 25;
    END IF;
    
    RETURN ngay_chot_date + INTERVAL '1 day' * so_ngay_them;
END;
$$ LANGUAGE plpgsql;

-- Function tạo mã giao dịch tự động
CREATE OR REPLACE FUNCTION tao_ma_giao_dich()
RETURNS TEXT AS $$
DECLARE
    ma_moi TEXT;
    dem INTEGER := 0;
BEGIN
    LOOP
        ma_moi := 'GD' || TO_CHAR(CURRENT_DATE, 'YYYYMMDD') || 
                  LPAD(FLOOR(RANDOM() * 10000)::TEXT, 4, '0');
        
        -- Kiểm tra mã đã tồn tại chưa
        SELECT COUNT(*) INTO dem FROM giao_dich WHERE ma_giao_dich = ma_moi;
        
        EXIT WHEN dem = 0;
    END LOOP;
    
    RETURN ma_moi;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- VIEWS - Các view hỗ trợ báo cáo
-- =====================================================

-- View thống kê đại lý
CREATE VIEW v_thong_ke_dai_ly AS
SELECT 
    dl.id,
    dl.ma_dai_ly,
    dl.ten_dai_ly,
    nd.ho_ten as ten_chu_dai_ly,
    dl.so_du_vi,
    dl.diem_thuong,
    dl.ty_le_hoa_hong,
    COUNT(hdd.id) as tong_hoa_don_nhap,
    SUM(hdd.tong_tien) as tong_gia_tri_nhap,
    dl.trang_thai,
    dl.created_at as ngay_dang_ky
FROM dai_ly dl
LEFT JOIN nguoi_dung nd ON dl.nguoi_dung_id = nd.id
LEFT JOIN hoa_don_dien hdd ON dl.id = hdd.dai_ly_nhap_kho_id
WHERE dl.deleted_at IS NULL
GROUP BY dl.id, nd.ho_ten;

-- View thống kê khách thẻ
CREATE VIEW v_thong_ke_khach_the AS
SELECT 
    kt.id,
    kt.ma_khach_the,
    nd.ho_ten,
    kt.so_du_vi,
    kt.tong_chi_tieu,
    COUNT(ttd.id) as so_luong_the,
    COUNT(hdd.id) as so_hoa_don_da_mua,
    SUM(hdd.tong_tien) as tong_gia_tri_mua,
    kt.trang_thai,
    kt.created_at as ngay_dang_ky
FROM khach_the kt
LEFT JOIN nguoi_dung nd ON kt.nguoi_dung_id = nd.id
LEFT JOIN the_tin_dung ttd ON kt.id = ttd.khach_the_id AND ttd.deleted_at IS NULL
LEFT JOIN hoa_don_dien hdd ON kt.id = hdd.khach_the_mua_id
WHERE kt.deleted_at IS NULL
GROUP BY kt.id, nd.ho_ten;

-- View hóa đơn cần chú ý
CREATE VIEW v_hoa_don_can_chu_y AS
SELECT 
    hdd.*,
    ncc.ten_nha_cung_cap,
    CASE 
        WHEN hdd.trang_thai = 'trong_kho' AND hdd.created_at < CURRENT_DATE - INTERVAL '30 days' 
        THEN 'Tồn kho lâu'
        WHEN hdd.tong_tien > 5000000 
        THEN 'Mệnh giá cao'
        ELSE 'Bình thường'
    END as muc_do_uu_tien
FROM hoa_don_dien hdd
LEFT JOIN nha_cung_cap_dien ncc ON hdd.nha_cung_cap_id = ncc.id
WHERE hdd.deleted_at IS NULL
AND (
    hdd.trang_thai = 'trong_kho' 
    OR hdd.tong_tien > 5000000
    OR hdd.created_at < CURRENT_DATE - INTERVAL '30 days'
);

-- View thẻ sắp đến hạn thanh toán
CREATE VIEW v_the_sat_han AS
SELECT 
    ttd.*,
    kt.ma_khach_the,
    nd.ho_ten as ten_khach_hang,
    nd.so_dien_thoai,
    tinh_ngay_cuoi_thanh_toan(
        ttd.ngay_chot_sao_ke, 
        ttd.loai_mien_lai
    ) as ngay_cuoi_thanh_toan,
    tinh_ngay_cuoi_thanh_toan(
        ttd.ngay_chot_sao_ke, 
        ttd.loai_mien_lai
    ) - CURRENT_DATE as so_ngay_con_lai
FROM the_tin_dung ttd
JOIN khach_the kt ON ttd.khach_the_id = kt.id
JOIN nguoi_dung nd ON kt.nguoi_dung_id = nd.id
WHERE ttd.deleted_at IS NULL
AND ttd.trang_thai = 'hoat_dong'
AND tinh_ngay_cuoi_thanh_toan(
    ttd.ngay_chot_sao_ke, 
    ttd.loai_mien_lai
) - CURRENT_DATE <= 5;

-- =====================================================
-- COMMENTS - Ghi chú cho các bảng và cột
-- =====================================================

COMMENT ON TABLE nguoi_dung IS 'Bảng lưu thông tin người dùng hệ thống';
COMMENT ON TABLE nhan_vien IS 'Bảng lưu thông tin nhân viên';
COMMENT ON TABLE dai_ly IS 'Bảng lưu thông tin đại lý thu hộ';
COMMENT ON TABLE khach_the IS 'Bảng lưu thông tin khách hàng sử dụng thẻ tín dụng';
COMMENT ON TABLE the_tin_dung IS 'Bảng lưu thông tin thẻ tín dụng';
COMMENT ON TABLE hoa_don_dien IS 'Bảng lưu thông tin hóa đơn điện trong kho';
COMMENT ON TABLE giao_dich IS 'Bảng lưu thông tin các giao dịch tài chính';
COMMENT ON TABLE phe_duyet IS 'Bảng lưu thông tin các yêu cầu phê duyệt';
COMMENT ON TABLE lich_su_hoat_dong IS 'Bảng lưu lịch sử hoạt động của người dùng';

-- Comments cho các cột quan trọng
COMMENT ON COLUMN dai_ly.ma_dai_ly IS 'Mã đại lý = số điện thoại không có số 0 đầu';
COMMENT ON COLUMN khach_the.ma_khach_the IS 'Mã khách thẻ = số điện thoại không có số 0 đầu';
COMMENT ON COLUMN the_tin_dung.ngay_chot_sao_ke IS 'Ngày cố định hàng tháng chốt dư nợ thẻ (1-31)';
COMMENT ON COLUMN hoa_don_dien.phi_giao_dich IS 'Phí giao dịch tính theo công thức 0.005% - 1.8%';
COMMENT ON COLUMN hoa_don_dien.con_no_cuoc IS 'TRUE = còn nợ cước, FALSE = không còn nợ';