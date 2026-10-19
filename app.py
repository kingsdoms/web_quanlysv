import csv
import io
import os
import sqlite3
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, send_file, g
from werkzeug.security import generate_password_hash, check_password_hash

Chinh = Flask(__name__)

# File database tạo từ QL_SINHVIEN_sqlite.sql, đặt cùng thư mục với file này
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'QL_SINHVIEN.db')


# ---------------------------------------------------------------- Kết nối DB
def get_db():
    """Mỗi request dùng một kết nối riêng, tự đóng khi request kết thúc."""
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row            # truy cập cột theo tên: row['MSV'] hoặc row.MSV trong Jinja
        g.db.execute("PRAGMA foreign_keys = ON")  # SQLite mặc định không kiểm tra khóa ngoại
    return g.db


@Chinh.teardown_appcontext
def close_db(exc):
    db = g.pop('db', None)
    if db is not None:
        db.close()


@Chinh.errorhandler(sqlite3.IntegrityError)
def loi_rang_buoc(e):
    return (f"Lỗi ràng buộc dữ liệu: {e}<br>"
            "(trùng mã, hoặc dữ liệu đang được bảng khác tham chiếu)<br>"
            '<a href="javascript:history.back()">Quay lại</a>'), 400


# ------------------------------------------------------------------ Đăng nhập
@Chinh.route('/')
def index():
    return render_template('Dangnhap.html')


@Chinh.route('/dangnhap', methods=['POST'])
def dangnhap():
    username = request.form['username']
    password = request.form['password']
    db = get_db()
    row = db.execute("SELECT * FROM Login WHERE TenDN=?", (username,)).fetchone()
    if row and check_password_hash(row['MK'], password):
        return render_template('Quanly.html', username=username)
    return "Sai Tên hoặc MK"


@Chinh.route('/dangky', methods=['GET'])
def hienthi_dangky():
    return render_template('Dangky.html')


@Chinh.route('/dangky', methods=['POST'])
def dangky():
    username = request.form['username']
    password = request.form['password']

    db = get_db()
    if db.execute("SELECT 1 FROM Login WHERE TenDN=?", (username,)).fetchone():
        return "Tên đăng nhập đã tồn tại!"

    db.execute("INSERT INTO Login (TenDN, MK) VALUES (?, ?)",
               (username, generate_password_hash(password)))
    db.commit()

    return '''
        <h3>Đăng ký thành công!</h3>
        <a href="/">Quay lại trang Đăng nhập</a>
    '''


# ------------------------------------------------------------------ Sinh viên
@Chinh.route('/hososv')
def hososv():
    data = get_db().execute(
        "SELECT MSV, HODEM, TEN, GIOITINH, NGAYSINH, MANGANH, MALOP FROM HSSV"
    ).fetchall()
    return render_template('Hososv.html', sinhvien=data)


@Chinh.route('/them_sv', methods=['POST'])
def them_sv():
    msv = request.form['msv']
    hodem = request.form['hodem']
    ten = request.form['ten']
    gioitinh_val = 1 if request.form.get('gioitinh', '0') == "1" else 0
    ngaysinh = request.form['ngaysinh']
    manganh = request.form['manganh']
    malop = request.form['malop']

    db = get_db()
    db.execute(
        "INSERT INTO HSSV (MSV, HODEM, TEN, GIOITINH, NGAYSINH, MANGANH, MALOP) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (msv, hodem, ten, gioitinh_val, ngaysinh, manganh, malop)
    )
    db.commit()
    return redirect(url_for('hososv'))


@Chinh.route('/xoa_sv/<msv>')
def xoa_sv(msv):
    db = get_db()
    db.execute("DELETE FROM HSSV WHERE MSV=?", (msv,))
    db.commit()
    return redirect(url_for('hososv'))


@Chinh.route('/sua_sv/<msv>', methods=['GET', 'POST'])
def sua_sv(msv):
    db = get_db()
    if request.method == 'POST':
        hodem = request.form['hodem']
        ten = request.form['ten']
        gioitinh_val = 1 if request.form['gioitinh'] == "1" else 0
        manganh = request.form['manganh']
        malop = request.form['malop']

        # Kiểm tra định dạng ngày rồi lưu dạng chuỗi YYYY-MM-DD
        ngaysinh_val = datetime.strptime(request.form['ngaysinh'], "%Y-%m-%d").strftime("%Y-%m-%d")

        db.execute("""
            UPDATE HSSV
            SET HODEM=?, TEN=?, GIOITINH=?, NGAYSINH=?, MANGANH=?, MALOP=?
            WHERE MSV=?
        """, (hodem, ten, gioitinh_val, ngaysinh_val, manganh, malop, msv))
        db.commit()
        return redirect(url_for('hososv'))

    sv = db.execute("SELECT * FROM HSSV WHERE MSV=?", (msv,)).fetchone()
    return render_template('SuaSV.html', sv=sv)


@Chinh.route('/xuat_csv')
def xuat_csv():
    rows = get_db().execute("SELECT MSV, HODEM, TEN, MALOP FROM HSSV").fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Mã sinh viên', 'Họ đệm', 'Tên', 'Lớp'])
    for r in rows:
        writer.writerow([r['MSV'], r['HODEM'], r['TEN'], r['MALOP']])

    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='danh_sach_sv.csv'
    )


@Chinh.route('/quanly')
def quanly():
    return render_template('Quanly.html')


# ------------------------------------------------------------------ Ngành học
@Chinh.route('/nganhhoc')
def nganhhoc():
    data = get_db().execute("SELECT MANGANH, TENNGANH FROM NGANHHOC").fetchall()
    return render_template('NganhHoc.html', danhsach=data)


@Chinh.route('/them_nganh', methods=['POST'])
def them_nganh():
    db = get_db()
    db.execute("INSERT INTO NGANHHOC (MANGANH, TENNGANH) VALUES (?, ?)",
               (request.form['manganh'], request.form['tennganh']))
    db.commit()
    return redirect(url_for('nganhhoc'))


@Chinh.route('/xoa_nganh/<manganh>')
def xoa_nganh(manganh):
    db = get_db()
    db.execute("DELETE FROM NGANHHOC WHERE MANGANH=?", (manganh,))
    db.commit()
    return redirect(url_for('nganhhoc'))


@Chinh.route('/sua_nganh/<manganh>', methods=['GET', 'POST'])
def sua_nganh(manganh):
    db = get_db()
    if request.method == 'POST':
        db.execute("UPDATE NGANHHOC SET TENNGANH=? WHERE MANGANH=?",
                   (request.form['tennganh'], manganh))
        db.commit()
        return redirect(url_for('nganhhoc'))
    nganh = db.execute("SELECT MANGANH, TENNGANH FROM NGANHHOC WHERE MANGANH=?",
                       (manganh,)).fetchone()
    return render_template('SuaNganhHoc.html', nganh=nganh)


# ------------------------------------------------------------------ Khóa học
@Chinh.route('/khoahoc')
def khoahoc():
    data = get_db().execute(
        "SELECT MAKH, TENKH, NAMBATDAU, NAMKETTHUC FROM KHOAHOC"
    ).fetchall()
    return render_template('KhoaHoc.html', danhsach=data)


@Chinh.route('/them_khoa', methods=['POST'])
def them_khoa():
    db = get_db()
    db.execute(
        "INSERT INTO KHOAHOC (MAKH, TENKH, NAMBATDAU, NAMKETTHUC) VALUES (?, ?, ?, ?)",
        (request.form['makh'], request.form['tenkh'],
         request.form['nambatdau'], request.form['namketthuc'])
    )
    db.commit()
    return redirect(url_for('khoahoc'))


@Chinh.route('/xoa_khoa/<makh>')
def xoa_khoa(makh):
    db = get_db()
    db.execute("DELETE FROM KHOAHOC WHERE MAKH=?", (makh,))
    db.commit()
    return redirect(url_for('khoahoc'))


@Chinh.route('/sua_khoa/<makh>', methods=['GET', 'POST'])
def sua_khoa(makh):
    db = get_db()
    if request.method == 'POST':
        db.execute(
            "UPDATE KHOAHOC SET TENKH=?, NAMBATDAU=?, NAMKETTHUC=? WHERE MAKH=?",
            (request.form['tenkh'], request.form['nambatdau'],
             request.form['namketthuc'], makh)
        )
        db.commit()
        return redirect(url_for('khoahoc'))
    khoa = db.execute(
        "SELECT MAKH, TENKH, NAMBATDAU, NAMKETTHUC FROM KHOAHOC WHERE MAKH=?", (makh,)
    ).fetchone()
    return render_template('SuaKhoaHoc.html', khoa=khoa)


# ------------------------------------------------------------------ Lớp học
@Chinh.route('/lophoc')
def lophoc():
    db = get_db()
    data = db.execute("""
        SELECT L.MALOP, L.TENLOP, L.MANGANH, N.TENNGANH, L.MAKH, K.TENKH
        FROM LOPHOC L
        LEFT JOIN NGANHHOC N ON L.MANGANH = N.MANGANH
        LEFT JOIN KHOAHOC K ON L.MAKH = K.MAKH
    """).fetchall()
    dsnganh = db.execute("SELECT MANGANH, TENNGANH FROM NGANHHOC").fetchall()
    dskhoa = db.execute("SELECT MAKH, TENKH FROM KHOAHOC").fetchall()
    return render_template('LopHoc.html', danhsach=data, dsnganh=dsnganh, dskhoa=dskhoa)


@Chinh.route('/them_lop', methods=['POST'])
def them_lop():
    db = get_db()
    db.execute(
        "INSERT INTO LOPHOC (MALOP, TENLOP, MANGANH, MAKH) VALUES (?, ?, ?, ?)",
        (request.form['malop'], request.form['tenlop'],
         request.form['manganh'], request.form['makh'])
    )
    db.commit()
    return redirect(url_for('lophoc'))


@Chinh.route('/xoa_lop/<malop>')
def xoa_lop(malop):
    db = get_db()
    db.execute("DELETE FROM LOPHOC WHERE MALOP=?", (malop,))
    db.commit()
    return redirect(url_for('lophoc'))


@Chinh.route('/sua_lop/<malop>', methods=['GET', 'POST'])
def sua_lop(malop):
    db = get_db()
    if request.method == 'POST':
        db.execute(
            "UPDATE LOPHOC SET TENLOP=?, MANGANH=?, MAKH=? WHERE MALOP=?",
            (request.form['tenlop'], request.form['manganh'], request.form['makh'], malop)
        )
        db.commit()
        return redirect(url_for('lophoc'))
    lop = db.execute("SELECT MALOP, TENLOP, MANGANH, MAKH FROM LOPHOC WHERE MALOP=?",
                     (malop,)).fetchone()
    dsnganh = db.execute("SELECT MANGANH, TENNGANH FROM NGANHHOC").fetchall()
    dskhoa = db.execute("SELECT MAKH, TENKH FROM KHOAHOC").fetchall()
    return render_template('SuaLopHoc.html', lop=lop, dsnganh=dsnganh, dskhoa=dskhoa)


# ------------------------------------------------------------------ Môn học
@Chinh.route('/monhoc')
def monhoc():
    data = get_db().execute("SELECT MAMH, TENMH, SOTINCHI FROM MONHOC").fetchall()
    return render_template('MonHoc.html', danhsach=data)


@Chinh.route('/them_mon', methods=['POST'])
def them_mon():
    db = get_db()
    db.execute("INSERT INTO MONHOC (MAMH, TENMH, SOTINCHI) VALUES (?, ?, ?)",
               (request.form['mamh'], request.form['tenmh'], request.form['sotinchi']))
    db.commit()
    return redirect(url_for('monhoc'))


@Chinh.route('/xoa_mon/<mamh>')
def xoa_mon(mamh):
    db = get_db()
    db.execute("DELETE FROM MONHOC WHERE MAMH=?", (mamh,))
    db.commit()
    return redirect(url_for('monhoc'))


@Chinh.route('/sua_mon/<mamh>', methods=['GET', 'POST'])
def sua_mon(mamh):
    db = get_db()
    if request.method == 'POST':
        db.execute("UPDATE MONHOC SET TENMH=?, SOTINCHI=? WHERE MAMH=?",
                   (request.form['tenmh'], request.form['sotinchi'], mamh))
        db.commit()
        return redirect(url_for('monhoc'))
    mon = db.execute("SELECT MAMH, TENMH, SOTINCHI FROM MONHOC WHERE MAMH=?",
                     (mamh,)).fetchone()
    return render_template('SuaMonHoc.html', mon=mon)


# ------------------------------------------------------------------ Kết quả
@Chinh.route('/ketqua')
def ketqua():
    db = get_db()
    data = db.execute("""
        SELECT K.MSV, S.TEN, K.MAMH, M.TENMH, K.DIEM
        FROM KETQUA K
        LEFT JOIN HSSV S ON K.MSV = S.MSV
        LEFT JOIN MONHOC M ON K.MAMH = M.MAMH
    """).fetchall()
    dssv = db.execute("SELECT MSV, TEN FROM HSSV").fetchall()
    dsmon = db.execute("SELECT MAMH, TENMH FROM MONHOC").fetchall()
    return render_template('KetQua.html', danhsach=data, dssv=dssv, dsmon=dsmon)


@Chinh.route('/them_ketqua', methods=['POST'])
def them_ketqua():
    db = get_db()
    db.execute("INSERT INTO KETQUA (MSV, MAMH, DIEM) VALUES (?, ?, ?)",
               (request.form['msv'], request.form['mamh'], request.form['diem']))
    db.commit()
    return redirect(url_for('ketqua'))


@Chinh.route('/xoa_ketqua/<msv>/<mamh>')
def xoa_ketqua(msv, mamh):
    db = get_db()
    db.execute("DELETE FROM KETQUA WHERE MSV=? AND MAMH=?", (msv, mamh))
    db.commit()
    return redirect(url_for('ketqua'))


@Chinh.route('/sua_ketqua/<msv>/<mamh>', methods=['GET', 'POST'])
def sua_ketqua(msv, mamh):
    db = get_db()
    if request.method == 'POST':
        db.execute("UPDATE KETQUA SET DIEM=? WHERE MSV=? AND MAMH=?",
                   (request.form['diem'], msv, mamh))
        db.commit()
        return redirect(url_for('ketqua'))
    kq = db.execute("SELECT MSV, MAMH, DIEM FROM KETQUA WHERE MSV=? AND MAMH=?",
                    (msv, mamh)).fetchone()
    return render_template('SuaKetQua.html', kq=kq)


@Chinh.route('/thoat')
def thoat():
    return render_template('Dangnhap.html')


if __name__ == '__main__':
    # sqlite3.connect() sẽ tự tạo file rỗng nếu chưa có, nên kiểm tra trước để báo lỗi rõ ràng
    if not os.path.exists(DB_PATH):
        raise SystemExit(
            f"Không tìm thấy database: {DB_PATH}\n"
            "Hãy tạo bằng: sqlite3 QL_SINHVIEN.db < QL_SINHVIEN_sqlite.sql"
        )
    Chinh.run(debug=True)