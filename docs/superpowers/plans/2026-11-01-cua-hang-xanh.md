# Cửa hàng Xanh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Xây website bán thực phẩm chạy trên máy cá nhân, nơi khách đặt hàng trả tiền khi nhận mà không cần tài khoản, còn chủ cửa hàng quản lý đơn và sản phẩm qua Django admin.

**Architecture:** Một project Django (`config`) với một app (`shop`). Trang do máy chủ tạo bằng template Django, giỏ hàng lưu trong session, dữ liệu lưu trong SQLite. Logic giỏ hàng nằm ở `shop/cart.py`, logic tạo đơn ở `shop/orders.py`, để view chỉ còn nhận yêu cầu và trả trang.

**Tech Stack:** Python 3.14, Django 6.1.2, Pillow 13.0.0 (cho trường ảnh), SQLite, HTML và CSS thuần.

**Spec:** `docs/superpowers/specs/2026-11-01-cua-hang-xanh-design.md`

## Global Constraints

- Mọi lệnh Python chạy qua môi trường ảo: `.venv/bin/python`.
- Chỉ dùng hai thư viện ngoài: `Django==6.1.2`, `Pillow==13.0.0`. Không framework giao diện, không JavaScript trừ khi task yêu cầu.
- Chữ hiển thị cho người dùng bằng tiếng Việt. Tên trong mã bằng tiếng Anh.
- Giá là số nguyên đồng Việt Nam, hiển thị dạng `85.000đ`.
- `LANGUAGE_CODE = "vi"`, `TIME_ZONE = "Asia/Ho_Chi_Minh"`, `USE_TZ = True`.
- Khách không cần đăng nhập. Thông tin khách không được xem nếu chưa đăng nhập admin.
- Chạy bằng `manage.py runserver`, mặc định chỉ mở tại `127.0.0.1:8000`.
- Không đưa vào git: `.venv/`, `db.sqlite3`, `media/`, `__pycache__/`, `.DS_Store`, `.superpowers/`.

## Review Focus

- Bấm Xác nhận đặt hàng hai lần hoặc gửi lại form: chỉ tạo đúng một đơn.
- Đoán địa chỉ trang thành công của đơn người khác: không thấy đơn đó, bị đưa về trang chủ.
- Nhập số lượng rác (`abc`, `0`, `-1`, `1000`): không lỗi 500, giỏ giữ nguyên số cũ và có thông báo.
- Nhập số điện thoại có dấu cách hoặc dấu chấm (`090 123 4567`): được chấp nhận và lưu dạng `0901234567`. Tên chỉ toàn dấu cách bị từ chối.
- Sản phẩm trong giỏ bị xóa hoặc hết hàng, hoặc sản phẩm của đơn cũ bị xóa: các trang không lỗi, đơn cũ vẫn giữ nguyên tên và giá.

---

### Task 1: Dựng project và mô hình dữ liệu

**Files:**
- Create: `requirements.txt`, `manage.py`, `config/` (do `startproject` tạo), `shop/` (do `startapp` tạo)
- Create: `shop/models.py`, `shop/templatetags/__init__.py`, `shop/templatetags/shop_extras.py`, `shop/migrations/0001_initial.py`
- Modify: `.gitignore`, `config/settings.py`
- Test: `shop/tests/__init__.py`, `shop/tests/test_models.py`

**Interfaces:**
- Produces:
  - `Category(name: str, position: int)`, sắp theo `position`.
  - `Product(name, category: FK Category, image: ImageField tùy chọn upload_to="products/", price: PositiveIntegerField, package_label: str, origin: "domestic"|"imported", is_available: bool=True)`, với `Product.Origin` là `TextChoices` có nhãn `Trong nước`, `Nhập khẩu`.
  - `Order(customer_name: max 100, phone: max 10, address: max 255, created_at: auto_now_add, total: PositiveIntegerField)`, sắp `-created_at`.
  - `OrderItem(order: FK related_name="items" CASCADE, product: FK SET_NULL null=True, product_name, package_label, unit_price: PositiveIntegerField, quantity: PositiveIntegerField)`, thuộc tính `line_total -> int`.
  - Bộ lọc template `vnd` và hàm `format_vnd(amount: int) -> str` trong `shop/templatetags/shop_extras.py`.
  - `verbose_name` tiếng Việt cho các model và trường.

- [ ] **Step 1: Tạo môi trường và project**

Run:
```bash
python3 -m venv .venv
printf 'Django==6.1.2\nPillow==13.0.0\n' > requirements.txt
.venv/bin/pip install -r requirements.txt
.venv/bin/django-admin startproject config .
.venv/bin/python manage.py startapp shop
```
Expected: có `manage.py`, `config/`, `shop/`.

- [ ] **Step 2: Cấu hình**

Thêm `.venv/`, `db.sqlite3`, `media/`, `__pycache__/`, `.DS_Store` vào `.gitignore`. Trong `config/settings.py`: thêm `"shop"` vào `INSTALLED_APPS`, đặt ngôn ngữ và múi giờ theo Global Constraints, `MEDIA_URL = "media/"`, `MEDIA_ROOT = BASE_DIR / "media"`.

- [ ] **Step 3: Viết test thất bại trong `shop/tests/test_models.py`**

Xóa `shop/tests.py` do `startapp` tạo.

```python
class FormatVndTests(SimpleTestCase):
    def test_formats_with_dot_separator(self):
        self.assertEqual(format_vnd(85000), "85.000đ")
        self.assertEqual(format_vnd(1205000), "1.205.000đ")
        self.assertEqual(format_vnd(0), "0đ")

class OrderItemTests(TestCase):
    def test_line_total(self):  # unit_price=15000, quantity=3
        self.assertEqual(item.line_total, 45000)

    def test_item_survives_product_deletion(self):
        product.delete()
        item.refresh_from_db()
        self.assertIsNone(item.product)
        self.assertEqual(item.product_name, "Rau muống")
        self.assertEqual(item.unit_price, 15000)
```

- [ ] **Step 4: Chạy test để thấy thất bại**

Run: `.venv/bin/python manage.py test shop.tests.test_models`
Expected: FAIL với lỗi import.

- [ ] **Step 5: Viết model và `format_vnd`, tạo migration**

Run: `.venv/bin/python manage.py makemigrations shop`

- [ ] **Step 6: Chạy test để thấy đạt**

Run: `.venv/bin/python manage.py test shop.tests.test_models`
Expected: PASS, 3 test.

- [ ] **Step 7: Commit**

```bash
git add .gitignore requirements.txt manage.py config shop
git commit -m "feat: scaffold Django project and shop models"
```

---

### Task 2: Trang chủ, giao diện chung và dữ liệu mẫu

**Files:**
- Create: `shop/urls.py`, `shop/views.py`, `shop/context_processors.py`, `shop/cart.py` (chỉ `Cart.count`, Task 3 làm tiếp), `shop/templates/shop/base.html`, `shop/templates/shop/home.html`, `shop/static/shop/style.css`, `shop/management/__init__.py`, `shop/management/commands/__init__.py`, `shop/management/commands/seed_shop.py`
- Modify: `config/settings.py` (đăng ký context processor `cart_count`), `config/urls.py` (nối `shop.urls`, thêm `MEDIA_URL`)
- Test: `shop/tests/test_home.py`, `shop/tests/test_seed.py`

**Interfaces:**
- Consumes: các model và bộ lọc `vnd` của Task 1.
- Produces:
  - `app_name = "shop"`, URL `shop:home` tại `/`, nhận `?category=<id>`.
  - `base.html` có block `content`, thanh trên cùng, hiển thị Django messages.
  - Context processor `shop.context_processors.cart_count` cấp biến `cart_count`.
  - `Cart(session)` và `Cart.count() -> int` (tổng số lượng), khóa session `"cart"` chứa `{"<product_id>": quantity}`.
  - Lệnh `manage.py seed_shop`.
  - `config/urls.py` phục vụ `MEDIA_URL` khi `DEBUG` bằng `static()`.

- [ ] **Step 1: Viết test thất bại trong `shop/tests/test_home.py` và `shop/tests/test_seed.py`**

```python
class HomePageTests(TestCase):
    def test_shows_product_details(self):
        response = self.client.get(reverse("shop:home"))
        for text in ["Rau muống", "Bó 500g", "Trong nước", "15.000đ"]:
            self.assertContains(response, text)

    def test_filters_by_category(self):
        response = self.client.get(reverse("shop:home"), {"category": self.eggs.id})
        self.assertContains(response, "Trứng gà")
        self.assertNotContains(response, "Rau muống")

    def test_bad_category_shows_all(self):
        for value in ["abc", "999999"]:
            response = self.client.get(reverse("shop:home"), {"category": value})
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "Rau muống")

    def test_out_of_stock_has_label_and_no_add_form(self):
        response = self.client.get(reverse("shop:home"))
        self.assertContains(response, "Hết hàng")
        self.assertNotContains(response, f"/gio-hang/them/{self.lychee.id}/")

    def test_product_without_image_renders_placeholder(self):
        self.assertContains(self.client.get(reverse("shop:home")), 'class="no-image"')

class SeedTests(TestCase):
    def test_creates_all_categories_and_products(self):
        call_command("seed_shop")
        self.assertEqual(
            list(Category.objects.values_list("name", flat=True)),
            ["Rau", "Củ", "Quả trong nước", "Quả nhập khẩu", "Trứng"],
        )
        self.assertGreaterEqual(Product.objects.count(), 20)
        for category in Category.objects.all():
            self.assertTrue(category.product_set.exists())

    def test_rerun_keeps_edited_prices_and_adds_no_duplicates(self):
        call_command("seed_shop")
        count = Product.objects.count()
        Product.objects.filter(name="Rau muống").update(price=99000)
        call_command("seed_shop")
        self.assertEqual(Product.objects.count(), count)
        self.assertEqual(Product.objects.get(name="Rau muống").price, 99000)
```

- [ ] **Step 2: Chạy test để thấy thất bại**

Run: `.venv/bin/python manage.py test shop.tests.test_home shop.tests.test_seed`
Expected: FAIL.

- [ ] **Step 3: Viết view `home(request)`, template, CSS và context processor**

Lọc category bằng cách thử đổi sang số nguyên, sai hoặc không tồn tại thì hiện tất cả. Sắp sản phẩm theo vị trí nhóm hàng rồi tên. Nút Thêm vào giỏ là form POST tới `/gio-hang/them/<id>/` có `{% csrf_token %}`. Task 3 mới tạo URL đó, nên tạm viết đường dẫn trực tiếp trong template Task 2 và đổi sang `{% url %}` ở Task 3. Sản phẩm hết hàng mang class `out-of-stock` (mờ đi). Sản phẩm không có ảnh hiện `<div class="no-image">`. CSS tông xanh lá, lưới sản phẩm tự xuống dòng để xem được trên điện thoại, có `<meta name="viewport">`.

- [ ] **Step 4: Viết lệnh `seed_shop`**

Dùng `get_or_create` theo tên, giá đặt trong `defaults`, để chạy lại không đè giá đã sửa. Năm nhóm hàng theo đúng thứ tự trong test. Ít nhất 20 sản phẩm, có `Rau muống` (Bó 500g), trứng gà và trứng vịt (Vỉ 10 quả), vài quả theo mùa ở Việt Nam, vài quả nhập khẩu với `origin="imported"`.

- [ ] **Step 5: Chạy test để thấy đạt**

Run: `.venv/bin/python manage.py test shop.tests.test_home shop.tests.test_seed`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add config shop
git commit -m "feat: add storefront page and sample products"
```

---

### Task 3: Giỏ hàng

**Files:**
- Modify: `shop/cart.py`, `shop/views.py`, `shop/urls.py`, `shop/templates/shop/home.html`
- Create: `shop/templates/shop/cart.html`
- Test: `shop/tests/test_cart.py`

**Interfaces:**
- Consumes: `Cart(session)`, URL và `base.html` của Task 2.
- Produces:
  - `MAX_QUANTITY = 99`.
  - `Cart.count()` đổi sang tính từ `lines()`, để sản phẩm đã xóa không còn được đếm.
  - `CartLine` (dataclass): `product: Product`, `quantity: int`, thuộc tính `line_total -> int`.
  - `Cart.add(product_id: int) -> None` (cộng 1, tối đa 99), `Cart.set_quantity(product_id: int, quantity: int) -> None`, `Cart.remove(product_id: int) -> None`, `Cart.clear() -> None`.
  - `Cart.lines() -> list[CartLine]`, tự bỏ qua sản phẩm không còn trong cơ sở dữ liệu.
  - `Cart.total() -> int`, `Cart.has_unavailable() -> bool`.
  - `Cart.signature() -> str`, chuỗi ổn định từ `id:số lượng:giá:còn hàng` của từng dòng sắp theo id. Giỏ trống trả về chuỗi rỗng.
  - URL: `shop:cart` tại `/gio-hang/`, và các URL chỉ nhận POST `shop:cart_add` tại `/gio-hang/them/<int:product_id>/`, `shop:cart_update` tại `/gio-hang/cap-nhat/<int:product_id>/` (trường `quantity`), `shop:cart_remove` tại `/gio-hang/xoa/<int:product_id>/`.

- [ ] **Step 1: Viết test thất bại trong `shop/tests/test_cart.py`**

```python
class CartViewTests(TestCase):
    def test_add_shows_line_and_total(self):
        self.client.post(reverse("shop:cart_add", args=[self.spinach.id]))
        self.client.post(reverse("shop:cart_add", args=[self.spinach.id]))
        response = self.client.get(reverse("shop:cart"))
        self.assertContains(response, "Rau muống")
        self.assertContains(response, "30.000đ")
        self.assertEqual(response.context["cart_count"], 2)

    def test_add_out_of_stock_rejected_with_message(self):
        response = self.client.post(reverse("shop:cart_add", args=[self.lychee.id]), follow=True)
        self.assertEqual(response.context["cart_count"], 0)
        self.assertContains(response, "đã hết hàng")

    def test_add_unknown_product_is_404(self):
        self.assertEqual(self.client.post(reverse("shop:cart_add", args=[999999])).status_code, 404)

    def test_add_by_get_not_allowed(self):
        self.assertEqual(self.client.get(reverse("shop:cart_add", args=[self.spinach.id])).status_code, 405)

    def test_update_quantity(self):  # thêm 1 rồi đặt quantity="3"
        self.assertEqual(self.client.get(reverse("shop:cart")).context["cart_count"], 3)

    def test_bad_quantity_keeps_old_value_with_message(self):
        for bad in ["abc", "0", "-1", "1000", ""]:
            response = self.client.post(
                reverse("shop:cart_update", args=[self.spinach.id]), {"quantity": bad}, follow=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["cart_count"], 1)
            self.assertContains(response, "Số lượng phải từ 1 đến 99")

    def test_remove(self):  # thêm 1 rồi xóa
        self.assertEqual(self.client.get(reverse("shop:cart")).context["cart_count"], 0)

    def test_deleted_product_drops_from_cart(self):
        self.client.post(reverse("shop:cart_add", args=[self.spinach.id]))
        self.spinach.delete()
        self.assertEqual(self.client.get(reverse("shop:cart")).status_code, 200)

    def test_unavailable_line_is_flagged_and_order_button_hidden(self):
        self.client.post(reverse("shop:cart_add", args=[self.spinach.id]))
        Product.objects.filter(id=self.spinach.id).update(is_available=False)
        response = self.client.get(reverse("shop:cart"))
        self.assertContains(response, "Hết hàng")
        self.assertNotContains(response, "/dat-hang/")

    def test_empty_cart_message(self):
        self.assertContains(self.client.get(reverse("shop:cart")), "Giỏ hàng đang trống")
```

Với `Cart.count()`, sản phẩm đã xóa cũng phải không được tính: bổ sung `self.assertEqual(response.context["cart_count"], 0)` vào `test_deleted_product_drops_from_cart`.

- [ ] **Step 2: Chạy test để thấy thất bại**

Run: `.venv/bin/python manage.py test shop.tests.test_cart`
Expected: FAIL.

- [ ] **Step 3: Viết `Cart` và các view giỏ hàng**

Sau khi POST thành công thì chuyển hướng: thêm sản phẩm về trang trước đó nếu hợp lệ (`url_has_allowed_host_and_scheme`), còn lại về `shop:cart`. Đổi đường dẫn tạm trong `home.html` sang `{% url 'shop:cart_add' product.id %}`. Task 4 mới có URL đặt hàng, nên nút Đặt hàng tạm viết `href="/dat-hang/"` và đổi sang `{% url %}` ở Task 4.

- [ ] **Step 4: Chạy test để thấy đạt**

Run: `.venv/bin/python manage.py test shop`
Expected: PASS toàn bộ.

- [ ] **Step 5: Commit**

```bash
git add shop
git commit -m "feat: add session-based cart"
```

---

### Task 4: Đặt hàng

**Files:**
- Create: `shop/orders.py`, `shop/forms.py`, `shop/templates/shop/checkout.html`, `shop/templates/shop/order_success.html`
- Modify: `shop/views.py`, `shop/urls.py`, `shop/templates/shop/cart.html`
- Test: `shop/tests/test_checkout.py`

**Interfaces:**
- Consumes: `Cart.lines`, `Cart.total`, `Cart.has_unavailable`, `Cart.signature`, `Cart.clear` của Task 3.
- Produces:
  - `CheckoutForm` là `forms.Form`, không phải `ModelForm`: `customer_name` (tối đa 100), `phone` (tối đa 20 để chứa dấu phân cách trước khi chuẩn hóa), `address` (tối đa 255), trường ẩn `cart_signature`. `clean_phone` bỏ dấu cách, dấu chấm, dấu gạch rồi kiểm tra `^0\d{9}$`, sai thì báo `Số điện thoại phải có 10 chữ số và bắt đầu bằng 0.`
  - `class CartChanged(Exception)`.
  - `place_order(cart: Cart, customer_name: str, phone: str, address: str, expected_signature: str) -> Order`. Trong `transaction.atomic`: giỏ trống, có hàng hết, hoặc `signature` khác `expected_signature` thì raise `CartChanged`. Ngược lại tạo `Order` và các `OrderItem` với bản sao tên, quy cách, đơn giá, rồi `cart.clear()`.
  - URL `shop:checkout` tại `/dat-hang/`, `shop:order_success` tại `/dat-hang/thanh-cong/<int:order_id>/`.
  - Khóa session `"last_order_id"`.

- [ ] **Step 1: Viết test thất bại trong `shop/tests/test_checkout.py`**

```python
class CheckoutTests(TestCase):
    # setUp: thêm spinach (15.000đ) x2 vào giỏ
    # submit(): GET checkout, lấy cart_signature từ response.context["form"], POST kèm thông tin khách

    def test_success_creates_order_with_snapshot(self):
        response = self.submit(follow=True)
        order = Order.objects.get()
        self.assertEqual(order.total, 30000)
        item = order.items.get()
        self.assertEqual((item.product_name, item.package_label, item.unit_price, item.quantity),
                         ("Rau muống", "Bó 500g", 15000, 2))
        self.assertContains(response, f"#{order.id}")
        self.assertEqual(response.context["cart_count"], 0)

    def test_later_price_change_keeps_old_order(self):
        self.submit()
        Product.objects.update(price=99000)
        self.assertEqual(Order.objects.get().items.get().unit_price, 15000)

    def test_page_shows_total_and_cash_on_delivery(self):
        response = self.client.get(reverse("shop:checkout"))
        self.assertContains(response, "30.000đ")
        self.assertContains(response, "trả tiền khi nhận hàng")

    def test_empty_cart_redirects_to_cart(self):
        self.client.post(reverse("shop:cart_remove", args=[self.spinach.id]))
        self.assertRedirects(self.client.get(reverse("shop:checkout")), reverse("shop:cart"))

    def test_price_change_before_submit_creates_no_order(self):
        data = self.form_data()
        Product.objects.update(price=20000)
        response = self.client.post(reverse("shop:checkout"), data, follow=True)
        self.assertEqual(Order.objects.count(), 0)
        self.assertRedirects(response, reverse("shop:cart"))
        self.assertContains(response, "Giỏ hàng vừa thay đổi")
        self.assertContains(response, "40.000đ")

    def test_out_of_stock_before_submit_creates_no_order(self):
        data = self.form_data()
        Product.objects.update(is_available=False)
        self.client.post(reverse("shop:checkout"), data)
        self.assertEqual(Order.objects.count(), 0)

    def test_double_submit_creates_one_order(self):
        data = self.form_data()
        self.client.post(reverse("shop:checkout"), data)
        response = self.client.post(reverse("shop:checkout"), data)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(response.status_code, 302)

    def test_phone_with_separators_is_normalized(self):
        self.submit(phone="090 123.4567")
        self.assertEqual(Order.objects.get().phone, "0901234567")

    def test_invalid_customer_data_rejected_and_cart_kept(self):
        for field, value in [("phone", "12345"), ("phone", "1901234567"),
                             ("customer_name", "   "), ("address", "")]:
            response = self.submit(**{field: value})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(Order.objects.count(), 0)
            self.assertEqual(response.context["cart_count"], 2)

    def test_vietnamese_text_saved_intact(self):
        self.submit(customer_name="Nguyễn Thị Ánh")
        self.assertEqual(Order.objects.get().customer_name, "Nguyễn Thị Ánh")

class OrderSuccessPrivacyTests(TestCase):
    def test_other_visitor_cannot_view_success_page(self):
        response = Client().get(reverse("shop:order_success", args=[self.order.id]))
        self.assertRedirects(response, reverse("shop:home"))

    def test_success_page_has_no_customer_details(self):
        response = self.submit(follow=True)
        self.assertNotContains(response, "0901234567")
```

- [ ] **Step 2: Chạy test để thấy thất bại**

Run: `.venv/bin/python manage.py test shop.tests.test_checkout`
Expected: FAIL.

- [ ] **Step 3: Viết `CheckoutForm`, `place_order` và view**

GET: giỏ trống hoặc có hàng hết thì chuyển về `shop:cart`, ngược lại đưa `cart.signature()` vào giá trị ban đầu của `cart_signature`. POST: giỏ trống thì chuyển về `shop:cart`. Form sai thì hiện lại form kèm lỗi. Bắt `CartChanged` thì thêm thông báo `Giỏ hàng vừa thay đổi, vui lòng kiểm tra lại trước khi đặt.` rồi chuyển về `shop:cart`. Thành công thì lưu `last_order_id` vào session rồi chuyển sang `shop:order_success`. Trang thành công so sánh `order_id` với `last_order_id`, không khớp thì chuyển về `shop:home`, và chỉ hiện thông báo kèm mã đơn dạng `#<id>`. Đổi `href="/dat-hang/"` trong `cart.html` sang `{% url 'shop:checkout' %}`.

- [ ] **Step 4: Chạy test để thấy đạt**

Run: `.venv/bin/python manage.py test shop`
Expected: PASS toàn bộ.

- [ ] **Step 5: Commit**

```bash
git add shop
git commit -m "feat: add cash-on-delivery checkout"
```

---

### Task 5: Trang quản lý bằng Django admin

**Files:**
- Modify: `shop/admin.py`
- Test: `shop/tests/test_admin.py`

**Interfaces:**
- Consumes: các model của Task 1, `format_vnd`.
- Produces: admin cho `Category`, `Product`, `Order` (kèm dòng đơn hiển thị trong trang đơn).

- [ ] **Step 1: Viết test thất bại trong `shop/tests/test_admin.py`**

```python
class AdminAccessTests(TestCase):
    def test_anonymous_cannot_see_orders(self):
        for name in ["admin:shop_order_changelist", "admin:shop_product_changelist"]:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 302)
            self.assertIn("/admin/login/", response["Location"])

class ProductAdminTests(TestCase):  # đăng nhập bằng superuser
    def test_price_and_availability_editable_in_list(self):
        admin = site._registry[Product]
        self.assertEqual(set(admin.list_editable), {"price", "is_available"})
        self.assertIn("category", admin.list_filter)

    def test_changelist_edit_saves(self):  # POST form changelist với form-0-price=20000, form-0-is_available bỏ trống
        self.product.refresh_from_db()
        self.assertEqual(self.product.price, 20000)
        self.assertFalse(self.product.is_available)

class OrderAdminTests(TestCase):  # đăng nhập bằng superuser
    def test_list_shows_customer_and_total(self):
        response = self.client.get(reverse("admin:shop_order_changelist"))
        for text in ["Khách A", "0901234567", "30.000đ"]:
            self.assertContains(response, text)

    def test_detail_shows_address_and_items(self):
        response = self.client.get(reverse("admin:shop_order_change", args=[self.order.id]))
        for text in ["12 Lê Lợi", "Rau muống", "Bó 500g"]:
            self.assertContains(response, text)

    def test_detail_works_after_product_deleted(self):
        self.product.delete()
        response = self.client.get(reverse("admin:shop_order_change", args=[self.order.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rau muống")

    def test_orders_cannot_be_added_or_edited(self):
        self.assertEqual(self.client.get(reverse("admin:shop_order_add")).status_code, 403)
        self.client.post(reverse("admin:shop_order_change", args=[self.order.id]), {"total": 1})
        self.order.refresh_from_db()
        self.assertEqual(self.order.total, 30000)
```

- [ ] **Step 2: Chạy test để thấy thất bại**

Run: `.venv/bin/python manage.py test shop.tests.test_admin`
Expected: FAIL.

- [ ] **Step 3: Viết `shop/admin.py`**

`ProductAdmin`: `list_display` gồm tên, nhóm hàng, quy cách, nguồn gốc, giá, còn hàng. `list_editable` gồm giá và còn hàng. `list_filter` gồm nhóm hàng và còn hàng. `search_fields` theo tên. `OrderAdmin`: `list_display` gồm mã đơn, thời gian, tên khách, số điện thoại, tổng tiền định dạng bằng `format_vnd`. Chặn thêm và sửa (`has_add_permission`, `has_change_permission` trả về `False`, để superuser vẫn xem được qua quyền xem). `OrderItemInline` chỉ đọc, không thêm, không xóa. Giữ quyền xóa đơn để chủ cửa hàng dọn đơn thử.

- [ ] **Step 4: Chạy test để thấy đạt**

Run: `.venv/bin/python manage.py test shop`
Expected: PASS toàn bộ.

- [ ] **Step 5: Commit**

```bash
git add shop
git commit -m "feat: configure admin for products and orders"
```

---

### Task 6: Hướng dẫn chạy và kiểm tra toàn bộ

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: toàn bộ các task trước, lệnh `seed_shop`.

- [ ] **Step 1: Viết `README.md` tiếng Việt cho người mới**

Gồm lần lượt, mỗi lệnh một khối có giải thích một dòng: tạo môi trường ảo, cài thư viện, `migrate`, `seed_shop`, `createsuperuser` (chủ dự án tự đặt mật khẩu), `runserver`, địa chỉ `http://127.0.0.1:8000/` và `http://127.0.0.1:8000/admin/`, chạy kiểm thử. Có một đoạn cảnh báo: web chưa sẵn sàng để đưa lên mạng thật.

- [ ] **Step 2: Làm theo README từ đầu trên một thư mục sạch**

Run: `git clone . <thư mục tạm>`, rồi chạy đúng các lệnh trong README, thay `createsuperuser` tương tác bằng tài khoản thử nghiệm với `--noinput` và biến môi trường `DJANGO_SUPERUSER_PASSWORD`, tạo trong thư mục tạm và xóa cùng thư mục đó.
Expected: `manage.py test` PASS toàn bộ, `manage.py check` báo không có vấn đề.

- [ ] **Step 3: Kiểm tra bằng trình duyệt**

Chạy web, rồi đi hết luồng: lọc nhóm hàng, thêm vào giỏ, đổi số lượng, đặt hàng, thấy mã đơn. Đăng nhập admin, thấy đơn vừa đặt, đổi giá và tình trạng một sản phẩm, quay lại trang chủ thấy thay đổi. Xem lại ở khổ điện thoại, trang không bị tràn ngang.
Expected: mọi bước đúng như spec. Xóa dữ liệu thử sau khi xong.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: add Vietnamese setup guide"
```
