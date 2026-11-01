# Cửa hàng xanh

Một trang web bán hàng nhỏ viết bằng Django. Khách xem sản phẩm, bỏ vào giỏ và đặt hàng, trả tiền mặt khi nhận hàng. Chủ cửa hàng quản lý sản phẩm và đơn hàng ở trang quản trị.

Hướng dẫn dưới đây dành cho người mới. Hãy gõ lần lượt từng lệnh trong cửa sổ Terminal, đang đứng trong thư mục của dự án (thư mục có file `manage.py`).

## Cần có trước

Máy đã cài Python 3 (gõ `python3 --version` để kiểm tra, nên là 3.12 trở lên).

## 1. Tạo môi trường ảo

```bash
python3 -m venv .venv
```

Lệnh này tạo một thư mục `.venv` để chứa riêng các thư viện của dự án, không làm lộn xộn máy của bạn.

## 2. Cài thư viện

```bash
.venv/bin/python -m pip install -r requirements.txt
```

Lệnh này cài Django và Pillow (thư viện xử lý ảnh) theo danh sách trong file `requirements.txt`.

## 3. Tạo cơ sở dữ liệu

```bash
.venv/bin/python manage.py migrate
```

Lệnh này tạo file dữ liệu `db.sqlite3` và các bảng cần thiết bên trong.

## 4. Nạp sản phẩm mẫu

```bash
.venv/bin/python manage.py seed_shop
```

Lệnh này thêm sẵn một số nhóm hàng và sản phẩm mẫu để trang chủ không bị trống.

## 5. Tạo tài khoản quản trị

```bash
.venv/bin/python manage.py createsuperuser
```

Lệnh này hỏi tên đăng nhập, email (có thể để trống) và mật khẩu. Bạn tự đặt mật khẩu và tự nhớ, đừng gửi cho ai. Khi gõ mật khẩu, màn hình không hiện ký tự nào, đó là bình thường.

## 6. Chạy web

```bash
.venv/bin/python manage.py runserver
```

Lệnh này bật web ngay trên máy của bạn. Giữ cửa sổ Terminal mở trong lúc dùng, muốn tắt thì nhấn `Ctrl + C`.

Sau đó mở trình duyệt:

- Trang cửa hàng: http://127.0.0.1:8000/
- Trang quản trị: http://127.0.0.1:8000/admin/ (đăng nhập bằng tài khoản vừa tạo ở bước 5)

Trong trang quản trị, bạn thêm hoặc sửa sản phẩm, đổi giá, đổi tình trạng còn hàng hay hết hàng, và xem các đơn khách đã đặt.

## 7. Chạy kiểm thử

```bash
.venv/bin/python manage.py test
```

Lệnh này chạy các bài kiểm tra tự động để chắc rằng mọi chức năng vẫn hoạt động đúng. Cuối kết quả phải có chữ `OK`.

```bash
.venv/bin/python manage.py check
```

Lệnh này soát nhanh cấu hình của dự án, kết quả đúng là `System check identified no issues`.

## Cảnh báo: chưa sẵn sàng để đưa lên mạng thật

Web này mới chỉ để chạy thử trên máy của bạn. Đừng đưa lên mạng thật khi chưa làm thêm các việc sau:

- Cấu hình hiện đang ở chế độ thử nghiệm (`DEBUG` bật) và dùng khóa bí mật mặc định, cần đổi sang khóa riêng và giữ kín.
- Cần khai báo tên miền được phép truy cập (`ALLOWED_HOSTS`) và bật HTTPS.
- Cơ sở dữ liệu SQLite chỉ hợp để thử, chưa phù hợp khi có nhiều người mua cùng lúc.
- Chưa có thanh toán trực tuyến, chỉ có trả tiền mặt khi nhận hàng.
- Ảnh sản phẩm tải lên chưa được cấu hình để phục vụ ngoài môi trường thử.

Nếu muốn mở cho khách thật, hãy nhờ người có kinh nghiệm triển khai rà soát trước.
