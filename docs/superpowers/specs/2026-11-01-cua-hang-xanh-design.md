# Thiết kế: website Cửa hàng Xanh

Ngày: 2026-11-01

## Mục đích

Chủ dự án muốn xây một website bán hàng nhỏ tên "Cửa hàng Xanh" để **học quy trình làm phần mềm với Superpowers**. Chủ dự án chưa rành lập trình, nên mọi lựa chọn phải ưu tiên sự đơn giản, dễ chạy và dễ đọc.

Cửa hàng bán thực phẩm: rau, củ, quả theo mùa ở Việt Nam, một số loại quả nhập khẩu, trứng gà, trứng vịt và các mặt hàng tương tự.

Dự án thành công khi chủ dự án chạy được web trên máy mình, tự đặt thử một đơn từ đầu đến cuối, thấy đơn đó trong trang quản lý và tự đổi được giá, tình trạng còn hàng của sản phẩm.

## Mục tiêu

- Khách xem sản phẩm, lọc theo nhóm hàng, thêm vào giỏ, sửa giỏ và đặt hàng trả tiền khi nhận mà không cần tài khoản.
- Chủ cửa hàng đăng nhập trang quản lý để xem đơn, sửa giá và bật tắt tình trạng còn hàng.
- Toàn bộ chạy trên máy của chủ dự án, dữ liệu lưu trong SQLite.

## Ngoài phạm vi

- Tài khoản khách hàng, lịch sử mua hàng của khách.
- Thanh toán online.
- Đưa web lên mạng thật.
- Theo dõi số lượng tồn kho (chỉ có Còn hàng hoặc Hết hàng).
- Trạng thái xử lý đơn (đã giao, đã hủy), phí giao hàng, mã giảm giá, gửi email hoặc tin nhắn.
- Bán theo cân thực tế.

## Điều phải tránh

- Dự án trở nên quá phức tạp so với mục đích học: không thêm thư viện, công cụ build hay framework giao diện nếu không thực sự cần.
- Thông tin khách (tên, số điện thoại, địa chỉ) xem được mà không đăng nhập.
- Tổng tiền khách thấy khi đặt khác với số tiền phải trả.

## Ràng buộc

- Cơ sở dữ liệu SQLite, chạy trên máy macOS của chủ dự án.
- Máy đã có Python 3.14 và SQLite. Django chưa được cài.
- Chủ dự án yêu cầu chưa cần đăng nhập cho khách và chưa cần thanh toán online.

## Các cách đã cân nhắc

| Cách | Đánh đổi |
|---|---|
| Python + Flask | Ít file và ít khái niệm nhất, nhưng phải tự viết trang quản lý. Đây là đề xuất ban đầu của Claude. |
| **Python + Django (đã chọn)** | Có sẵn trang quản trị, đăng nhập và kết nối cơ sở dữ liệu, nhưng nhiều khái niệm và nhiều file hơn. |
| JavaScript + Express | Cùng ngôn ngữ với trình duyệt, nhưng phải ghép nhiều thư viện. |

Chủ dự án chọn Python + Django. Với phần quản lý, chủ dự án chọn dùng trang quản trị có sẵn của Django thay vì tự viết trang không cần đăng nhập. Vì vậy có đúng một loại đăng nhập, chỉ dành cho chủ cửa hàng. Giao diện quản lý sẽ theo mẫu của Django, không theo bản phác.

## Các trang cho khách

Không cần đăng nhập. Giao diện bằng tiếng Việt. Thanh trên cùng có tên cửa hàng và liên kết giỏ hàng kèm số sản phẩm trong giỏ.

1. **Trang chủ:** lưới sản phẩm, có bộ lọc theo nhóm hàng và lựa chọn Tất cả. Mỗi sản phẩm hiện ảnh, tên, quy cách, nguồn gốc, giá và nút Thêm vào giỏ. Sản phẩm hết hàng vẫn hiện nhưng mờ đi, ghi "Hết hàng" và không thêm được vào giỏ.
2. **Giỏ hàng:** danh sách sản phẩm, số lượng, thành tiền và tổng cộng. Khách đổi được số lượng hoặc xóa sản phẩm. Có nút Đặt hàng.
3. **Đặt hàng:** form họ và tên, số điện thoại, địa chỉ giao hàng, kèm tổng cộng và dòng "trả tiền khi nhận hàng". Giỏ trống thì không vào được bước này.
4. **Đặt hàng thành công:** thông báo thành công kèm mã đơn. Giỏ hàng được làm trống.

Bản phác nằm ở `.superpowers/brainstorm/`, dùng để tham khảo bố cục, không phải thiết kế cuối cùng.

## Trang quản lý

Dùng Django admin, hiển thị tiếng Việt, đăng nhập bằng một tài khoản quản lý. Chủ dự án tự đặt mật khẩu trên máy mình khi cài đặt.

- **Sản phẩm:** danh sách cho phép sửa giá và tình trạng còn hàng ngay trên một màn hình, lọc được theo nhóm hàng. Thêm sản phẩm và tải ảnh dùng chức năng sẵn có của admin.
- **Đơn hàng:** danh sách mới nhất ở trên, hiện mã đơn, thời gian, tên khách, số điện thoại, tổng tiền. Mở một đơn thấy địa chỉ và các dòng sản phẩm.

## Dữ liệu

- **Nhóm hàng:** Rau, Củ, Quả trong nước, Quả nhập khẩu, Trứng.
- **Sản phẩm:** tên, nhóm hàng, ảnh, giá, quy cách (ví dụ "Bó 500g", "Vỉ 10 quả"), nguồn gốc (Trong nước hoặc Nhập khẩu), còn hàng hay không.
- **Đơn hàng:** họ tên, số điện thoại, địa chỉ, thời gian đặt, tổng tiền.
- **Dòng đơn hàng:** thuộc một đơn, tham chiếu sản phẩm, kèm bản sao tên, quy cách, đơn giá tại lúc đặt và số lượng. Đổi giá hay sửa sản phẩm về sau không làm thay đổi đơn cũ.

Giá là số nguyên đồng Việt Nam, hiển thị dạng `85.000đ`.

## Quy tắc nghiệp vụ

- Giỏ hàng lưu trong phiên trình duyệt, không cần tài khoản, chỉ lưu sản phẩm và số lượng. Giá luôn đọc mới từ cơ sở dữ liệu.
- Sản phẩm bán theo quy cách cố định, số lượng là số nguyên dương.
- Khi xác nhận đặt hàng, hệ thống kiểm tra lại. Nếu có sản phẩm đã hết hàng hoặc giá đã đổi, đơn chưa được tạo, khách quay lại giỏ hàng kèm thông báo rõ ràng, để tổng tiền khách đồng ý luôn đúng.
- Đã tạo đơn thì đơn và các dòng đơn được lưu cùng một lúc, không có đơn dở dang.

## Các quyết định Claude tự đưa ra

Chủ dự án có thể sửa khi đọc bản này:

- Form đặt hàng chỉ có ba trường: họ tên, số điện thoại, địa chỉ. Cả ba đều bắt buộc. Số điện thoại phải là 10 chữ số bắt đầu bằng 0.
- Nhập sẵn khoảng 20 sản phẩm mẫu phủ đủ các nhóm hàng, với giá ví dụ. Chủ dự án sẽ sửa lại thành giá thật.
- Ảnh không bắt buộc. Sản phẩm chưa có ảnh hiện một ô thay thế. Dự án không kèm ảnh thật, chủ dự án tự tải lên qua admin.
- Giao diện dùng CSS thuần tông xanh lá, xem được cả trên điện thoại.
- Chạy bằng máy chủ phát triển của Django, chỉ mở được từ chính máy đó.
- Múi giờ Việt Nam.

## Phần để người xây dựng quyết định

Cấu trúc thư mục và tên app, phiên bản Django tương thích Python 3.14, cách nhập dữ liệu mẫu, cách viết kiểm thử, chi tiết CSS. Nên có README tiếng Việt, dễ hiểu với người mới, chỉ từng lệnh để cài đặt, tạo tài khoản quản lý, chạy web và chạy kiểm thử. Dùng môi trường ảo Python. Cơ sở dữ liệu và ảnh tải lên không đưa vào git.
