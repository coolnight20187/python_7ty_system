-- =====================================================
-- MIGRATION 002: Additional Indexes and Optimizations
-- Created: 2025-01-27
-- Description: Thêm indexes và tối ưu hóa hiệu suất
-- =====================================================

-- Composite indexes cho các truy vấn phức tạp
CREATE INDEX idx_hoa_don_dien_composite_search ON hoa_don_dien(trang_thai, nha_cung_cap_id, tong_tien);
CREATE INDEX idx_giao_dich_composite_user_date ON giao_dich(nguoi_dung_id, created_at DESC);
CREATE INDEX idx_phe_duyet_composite_status_type ON phe_duyet(trang_thai, loai_phe_duyet, created_at DESC);

-- Partial indexes cho các trường hợp đặc biệt
CREATE INDEX idx_hoa_don_trong_kho ON hoa_don_dien(created_at) WHERE trang_thai = 'trong_kho';
CREATE INDEX idx_giao_dich_cho_xu_ly ON giao_dich(created_at) WHERE trang_thai = 'cho_xu_ly';
CREATE INDEX idx_phe_duyet_cho_duyet ON phe_duyet(created_at) WHERE trang_thai = 'cho_phe_duyet';

-- GIN indexes cho JSONB fields
CREATE INDEX idx_giao_dich_thong_tin_ngan_hang ON giao_dich USING GIN(thong_tin_ngan_hang);
CREATE INDEX idx_phe_duyet_noi_dung_yeu_cau ON phe_duyet USING GIN(noi_dung_yeu_cau);

-- Text search indexes
CREATE INDEX idx_hoa_don_dien_text_search ON hoa_don_dien USING GIN(to_tsvector('vietnamese', ten_khach_hang || ' ' || COALESCE(dia_chi, '')));
CREATE INDEX idx_nguoi_dung_text_search ON nguoi_dung USING GIN(to_tsvector('vietnamese', COALESCE(ho_ten, '') || ' ' || COALESCE(dia_chi, '')));

COMMIT;