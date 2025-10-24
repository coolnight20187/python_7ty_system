-- =====================================================
-- MIGRATION 003: Additional Constraints and Validations
-- Created: 2025-01-27
-- Description: Thêm ràng buộc và validation cho dữ liệu
-- =====================================================

-- Ràng buộc cho số điện thoại (format Việt Nam)
ALTER TABLE nguoi_dung ADD CONSTRAINT chk_so_dien_thoai 
CHECK (so_dien_thoai ~ '^0[0-9]{9,10}$');

-- Ràng buộc cho email
ALTER TABLE nguoi_dung ADD CONSTRAINT chk_email 
CHECK (email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

-- Ràng buộc cho số CMND/CCCD
ALTER TABLE nguoi_dung ADD CONSTRAINT chk_so_cmnd 
CHECK (so_cmnd ~ '^[0-9]{9,12}$');

-- Ràng buộc cho mã khách hàng điện (13 số bắt đầu bằng 84)
ALTER TABLE hoa_don_dien ADD CONSTRAINT chk_ma_khach_hang 
CHECK (ma_khach_hang ~ '^84[0-9]{11}$');

-- Ràng buộc cho số tiền (không âm)
ALTER TABLE dai_ly ADD CONSTRAINT chk_so_du_vi_dai_ly 
CHECK (so_du_vi >= 0);

ALTER TABLE khach_the ADD CONSTRAINT chk_so_du_vi_khach_the 
CHECK (so_du_vi >= 0);

ALTER TABLE giao_dich ADD CONSTRAINT chk_so_tien_giao_dich 
CHECK (so_tien > 0);

ALTER TABLE hoa_don_dien ADD CONSTRAINT chk_tien_hoa_don 
CHECK (tien_ky_truoc >= 0 AND tien_ky_nay >= 0);

-- Ràng buộc cho tỷ lệ hoa hồng (0-100%)
ALTER TABLE dai_ly ADD CONSTRAINT chk_ty_le_hoa_hong 
CHECK (ty_le_hoa_hong >= 0 AND ty_le_hoa_hong <= 1);

-- Ràng buộc cho hạn mức thẻ
ALTER TABLE the_tin_dung ADD CONSTRAINT chk_han_muc_the 
CHECK (han_muc_the > 0);

-- Ràng buộc cho ngày hết hạn thẻ (phải trong tương lai)
ALTER TABLE the_tin_dung ADD CONSTRAINT chk_ngay_het_han 
CHECK (ngay_het_han > CURRENT_DATE);

-- Ràng buộc unique cho một số trường hợp đặc biệt
ALTER TABLE dai_ly ADD CONSTRAINT uk_dai_ly_so_dien_thoai_chu 
UNIQUE (so_dien_thoai_chu);

-- Ràng buộc cho kỳ thanh toán (format MM/YYYY)
ALTER TABLE hoa_don_dien ADD CONSTRAINT chk_ky_thanh_toan 
CHECK (ky_thanh_toan ~ '^(0[1-9]|1[0-2])/[0-9]{4}$');

-- Ràng buộc logic: không thể tự phê duyệt
ALTER TABLE phe_duyet ADD CONSTRAINT chk_khong_tu_phe_duyet 
CHECK (nguoi_yeu_cau_id != nguoi_phe_duyet_id);

-- Ràng buộc: ngày phê duyệt phải sau ngày yêu cầu
ALTER TABLE phe_duyet ADD CONSTRAINT chk_ngay_phe_duyet 
CHECK (ngay_phe_duyet IS NULL OR ngay_phe_duyet >= created_at);

COMMIT;