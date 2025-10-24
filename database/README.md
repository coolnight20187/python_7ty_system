# 📊 HỆ THỐNG CƠ SỞ DỮ LIỆU 7tỷ.vn

## 🎯 Tổng quan

Hệ thống cơ sở dữ liệu PostgreSQL được thiết kế cho ứng dụng thanh toán hóa đơn điện và quản lý đại lý 7tỷ.vn với đầy đủ tính năng:

- **Multi-role Authentication**: Quản trị viên, nhân viên, đại lý, khách thẻ
- **Approval Workflow**: Hệ thống phê duyệt đa cấp
- **Commission System**: Tính toán hoa hồng tự động
- **Electric Bill Management**: Quản lý kho hóa đơn điện
- **Financial Transactions**: Giao dịch tài chính đầy đủ
- **Audit Trail**: Theo dõi hoạt động chi tiết

## 🏗️ Kiến trúc Database

### Các bảng chính:

1. **`nguoi_dung`** - Thông tin người dùng hệ thống
2. **`nhan_vien`** - Thông tin nhân viên
3. **`dai_ly`** - Thông tin đại lý thu hộ
4. **`khach_the`** - Thông tin khách hàng thẻ tín dụng
5. **`the_tin_dung`** - Thông tin thẻ tín dụng
6. **`hoa_don_dien`** - Kho hóa đơn điện
7. **`giao_dich`** - Giao dịch tài chính
8. **`phe_duyet`** - Hệ thống phê duyệt
9. **`lich_su_hoat_dong`** - Lịch sử hoạt động
10. **`tai_khoan_ngan_hang`** - Tài khoản ngân hàng
11. **`nha_cung_cap_dien`** - Nhà cung cấp điện
12. **`cau_hinh_he_thong`** - Cấu hình hệ thống

### ENUMs được định nghĩa:

- `vai_tro_nguoi_dung`: quan_tri_vien, nhan_vien, dai_ly, khach_the
- `trang_thai_tai_khoan`: hoat_dong, tam_khoa, da_xoa
- `trang_thai_phe_duyet`: cho_phe_duyet, da_phe_duyet, tu_choi, huy_bo
- `loai_giao_dich`: nap_tien, rut_tien, thanh_toan, hoa_hong, hoan_tien
- `trang_thai_giao_dich`: cho_xu_ly, dang_xu_ly, thanh_cong, that_bai, huy_bo
- `trang_thai_hoa_don`: trong_kho, da_ban, het_han, loi
- `tinh_trang_the`: binh_thuong, da_co_sao_ke, sat_han, dao_xong
- `loai_mien_lai`: mien_lai_45, mien_lai_55

## 🚀 Cài đặt và Migration

### 1. Tạo Database

```sql
CREATE DATABASE ty7_system;
CREATE USER ty7_user WITH ENCRYPTED PASSWORD 'ty7_password';
GRANT ALL PRIVILEGES ON DATABASE ty7_system TO ty7_user;
```

### 2. Chạy Migration

```bash
# Migration 001: Schema chính
psql -U ty7_user -d ty7_system -f migrations/001_initial_schema.sql

# Migration 002: Indexes bổ sung
psql -U ty7_user -d ty7_system -f migrations/002_add_indexes.sql

# Migration 003: Constraints
psql -U ty7_user -d ty7_system -f migrations/003_add_constraints.sql

# Import dữ liệu mẫu
psql -U ty7_user -d ty7_system -f seed_data.sql
```

### 3. Hoặc chạy toàn bộ:

```bash
psql -U ty7_user -d ty7_system -f schema.sql
```

## 📋 Dữ liệu mẫu

Sau khi chạy `seed_data.sql`, hệ thống sẽ có:

### Tài khoản đăng nhập:
- **Admin**: `admin` / `admin123`
- **Nhân viên**: `nhanvien01` / `admin123`, `nhanvien02` / `admin123`
- **Đại lý**: `daily01` / `admin123`, `daily02` / `admin123`, `daily03` / `admin123`
- **Khách thẻ**: `khachthe01` / `admin123`, `khachthe02` / `admin123`, `khachthe03` / `admin123`

### Dữ liệu mẫu:
- **3 đại lý** với số dư ví và hoa hồng
- **3 khách thẻ** với thẻ tín dụng và tài khoản ngân hàng
- **7 hóa đơn điện** (5 trong kho, 2 đã bán)
- **8 giao dịch** các loại
- **4 yêu cầu phê duyệt**
- **Lịch sử hoạt động** chi tiết

## 🔧 Functions và Triggers

### Functions hỗ trợ:

1. **`tinh_phi_giao_dich(so_tien)`**: Tính phí giao dịch theo công thức 0.005% - 1.8%
2. **`tinh_ngay_cuoi_thanh_toan()`**: Tính ngày cuối thanh toán thẻ tín dụng
3. **`tao_ma_giao_dich()`**: Tạo mã giao dịch tự động
4. **`cap_nhat_updated_at()`**: Cập nhật timestamp tự động

### Triggers:
- Tự động cập nhật `updated_at` cho tất cả bảng
- Validation dữ liệu khi insert/update

## 📊 Views hỗ trợ báo cáo

1. **`v_thong_ke_dai_ly`**: Thống kê tổng quan đại lý
2. **`v_thong_ke_khach_the`**: Thống kê khách thẻ
3. **`v_hoa_don_can_chu_y`**: Hóa đơn cần chú ý (tồn kho lâu, mệnh giá cao)
4. **`v_the_sat_han`**: Thẻ tín dụng sắp đến hạn thanh toán

## 🔍 Indexes tối ưu

### Primary Indexes:
- Tất cả khóa chính và khóa ngoại
- Các trường tìm kiếm thường xuyên (mã đại lý, mã khách thẻ, số điện thoại)
- Trạng thái và ngày tạo

### Composite Indexes:
- `(trang_thai, nha_cung_cap_id, tong_tien)` cho hóa đơn
- `(nguoi_dung_id, created_at)` cho giao dịch
- `(trang_thai, loai_phe_duyet, created_at)` cho phê duyệt

### Partial Indexes:
- Chỉ index các bản ghi có trạng thái cần thiết
- Tối ưu cho các truy vấn điều kiện

### GIN Indexes:
- Full-text search cho tên khách hàng và địa chỉ
- JSONB fields cho thông tin ngân hàng và nội dung phê duyệt

## 🛡️ Bảo mật và Constraints

### Validation Rules:
- Số điện thoại: Format Việt Nam (0xxxxxxxxx)
- Email: Format chuẩn RFC
- Số CMND/CCCD: 9-12 chữ số
- Mã khách hàng điện: 13 số bắt đầu bằng 84
- Số tiền: Không âm
- Tỷ lệ hoa hồng: 0-100%

### Business Logic:
- Không thể tự phê duyệt
- Ngày phê duyệt phải sau ngày yêu cầu
- Ngày hết hạn thẻ phải trong tương lai
- Kỳ thanh toán đúng format MM/YYYY

### Soft Delete:
- Tất cả bảng chính có `deleted_at` timestamp
- Dữ liệu không bị xóa vật lý, chỉ đánh dấu xóa

## 📈 Performance Tips

1. **Sử dụng indexes phù hợp** cho các truy vấn thường xuyên
2. **Partition tables** nếu dữ liệu lớn (theo tháng/năm)
3. **Connection pooling** để tối ưu kết nối
4. **Read replicas** cho các báo cáo
5. **Vacuum và analyze** định kỳ

## 🔄 Backup và Maintenance

### Backup hàng ngày:
```bash
pg_dump -U ty7_user -h localhost ty7_system > backup_$(date +%Y%m%d).sql
```

### Maintenance:
```sql
-- Vacuum và analyze
VACUUM ANALYZE;

-- Reindex nếu cần
REINDEX DATABASE ty7_system;

-- Kiểm tra thống kê
SELECT schemaname, tablename, n_tup_ins, n_tup_upd, n_tup_del 
FROM pg_stat_user_tables;
```

## 📞 Hỗ trợ

Nếu có vấn đề với database, vui lòng liên hệ:
- Email: admin@7ty.vn
- Hotline: 085.540.9876

---

**Phiên bản**: 1.0.0  
**Cập nhật cuối**: 27/01/2025  
**Tác giả**: 7tỷ.vn Development Team