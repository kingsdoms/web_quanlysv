# web_quanlysv – Phần mềm Quản lý Sinh viên

Ứng dụng web quản lý sinh viên xây dựng bằng **Flask** và **SQLite**, giao diện tiếng Việt.
Hỗ trợ đăng ký / đăng nhập, quản lý hồ sơ sinh viên, các danh mục (ngành, khóa, lớp, môn học) và kết quả học tập.

## Tính năng

- Đăng ký, đăng nhập (mật khẩu được băm bằng `werkzeug.security`)
- **Hồ sơ sinh viên**: thêm, sửa, xóa, xuất danh sách ra file CSV (mở được bằng Excel, hỗ trợ tiếng Việt)
- **Danh mục ngành học**: thêm, sửa, xóa
- **Danh mục khóa học**: thêm, sửa, xóa
- **Danh mục lớp học**: thêm, sửa, xóa (chọn ngành và khóa từ danh sách)
- **Danh mục môn học**: thêm, sửa, xóa
- **Kết quả học tập**: nhập, sửa, xóa điểm theo sinh viên và môn học

## Công nghệ

| Thành phần | Công nghệ |
|------------|-----------|
| Backend    | Python 3, Flask |
| Cơ sở dữ liệu | SQLite (module `sqlite3` có sẵn trong Python) |
| Giao diện  | HTML + CSS thuần, template Jinja2 |

## Cấu trúc thư mục

```
web_quanlysv/
├── app.py                  # Ứng dụng Flask (toàn bộ route)
├── QL_SINHVIEN_sqlite.sql  # Script tạo CSDL SQLite (cần đặt cùng thư mục)
├── QL_SINHVIEN.db          # File CSDL, sinh ra từ file .sql ở trên
├── static/
│   └── logo_HUBT.png       # Logo hiển thị ở trang chính
├── templates/
│   ├── Dangnhap.html, Dangky.html, Quanly.html
│   ├── Hososv.html, SuaSV.html
│   ├── NganhHoc.html, SuaNganhHoc.html
│   ├── KhoaHoc.html, SuaKhoaHoc.html
│   ├── LopHoc.html, SuaLopHoc.html
│   ├── MonHoc.html, SuaMonHoc.html
│   └── KetQua.html, SuaKetQua.html
├── LICENSE
└── README.md
```

## Cơ sở dữ liệu

Ứng dụng chỉ **kết nối** tới CSDL có sẵn, không tự tạo bảng. Các bảng được ứng dụng sử dụng:

| Bảng | Cột chính | Ý nghĩa |
|------|-----------|---------|
| `Login` | `TenDN`, `MK` | Tài khoản đăng nhập (`MK` lưu mật khẩu đã băm) |
| `NGANHHOC` | `MANGANH`, `TENNGANH` | Ngành học |
| `KHOAHOC` | `MAKH`, `TENKH`, `NAMBATDAU`, `NAMKETTHUC` | Khóa học |
| `LOPHOC` | `MALOP`, `TENLOP`, `MANGANH`, `MAKH` | Lớp học |
| `MONHOC` | `MAMH`, `TENMH`, `SOTINCHI` | Môn học |
| `HSSV` | `MSV`, `HODEM`, `TEN`, `GIOITINH`, `NGAYSINH`, `MANGANH`, `MALOP` | Hồ sơ sinh viên (`GIOITINH`: 1 = Nam, 0 = Nữ; `NGAYSINH` dạng `YYYY-MM-DD`) |
| `KETQUA` | `MSV`, `MAMH`, `DIEM` | Điểm của sinh viên theo môn |

Khóa ngoại được bật bằng `PRAGMA foreign_keys = ON`, nên không thể xóa dữ liệu đang được bảng khác tham chiếu
(ví dụ xóa lớp khi vẫn còn sinh viên thuộc lớp đó).

## Cài đặt và chạy

**Yêu cầu:** Python 3.9 trở lên.

```bash
# 1. Lấy mã nguồn
git clone <đường-dẫn-repo>
cd web_quanlysv

# 2. (Khuyến nghị) tạo môi trường ảo
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Cài thư viện
pip install flask

# 4. Tạo CSDL từ file SQL (đặt QL_SINHVIEN_sqlite.sql cùng thư mục với app.py)
sqlite3 QL_SINHVIEN.db < QL_SINHVIEN_sqlite.sql

# 5. Chạy ứng dụng
python app.py
```

Mở trình duyệt tại <http://127.0.0.1:5000>, bấm **Đăng ký** để tạo tài khoản rồi đăng nhập.

> Nếu chưa có file `QL_SINHVIEN.db`, `app.py` sẽ báo lỗi và dừng thay vì tự tạo CSDL rỗng.
> Để chỉnh sửa dữ liệu trực tiếp có thể dùng *DB Browser for SQLite*.

## Danh sách đường dẫn (route)

| Đường dẫn | Phương thức | Chức năng |
|-----------|-------------|-----------|
| `/` | GET | Trang đăng nhập |
| `/dangnhap` | POST | Xử lý đăng nhập |
| `/dangky` | GET, POST | Đăng ký tài khoản |
| `/quanly` | GET | Trang chính |
| `/hososv`, `/them_sv`, `/sua_sv/<msv>`, `/xoa_sv/<msv>` | GET, POST | Hồ sơ sinh viên |
| `/xuat_csv` | GET | Xuất danh sách sinh viên ra CSV |
| `/nganhhoc`, `/them_nganh`, `/sua_nganh/<ma>`, `/xoa_nganh/<ma>` | GET, POST | Ngành học |
| `/khoahoc`, `/them_khoa`, `/sua_khoa/<ma>`, `/xoa_khoa/<ma>` | GET, POST | Khóa học |
| `/lophoc`, `/them_lop`, `/sua_lop/<ma>`, `/xoa_lop/<ma>` | GET, POST | Lớp học |
| `/monhoc`, `/them_mon`, `/sua_mon/<ma>`, `/xoa_mon/<ma>` | GET, POST | Môn học |
| `/ketqua`, `/them_ketqua`, `/sua_ketqua/<msv>/<mamh>`, `/xoa_ketqua/<msv>/<mamh>` | GET, POST | Kết quả học tập |
| `/thoat` | GET | Thoát về trang đăng nhập |




