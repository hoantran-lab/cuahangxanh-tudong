import uuid

from django.db import models


class Category(models.Model):
    name = models.CharField("tên nhóm hàng", max_length=100)
    position = models.PositiveIntegerField("thứ tự", default=0)

    class Meta:
        ordering = ["position"]
        verbose_name = "nhóm hàng"
        verbose_name_plural = "nhóm hàng"

    def __str__(self):
        return self.name


class Product(models.Model):
    class Origin(models.TextChoices):
        DOMESTIC = "domestic", "Trong nước"
        IMPORTED = "imported", "Nhập khẩu"

    name = models.CharField("tên sản phẩm", max_length=200)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="nhóm hàng",
    )
    image = models.ImageField("hình ảnh", upload_to="products/", blank=True)
    price = models.PositiveIntegerField("giá (đồng)")
    package_label = models.CharField("quy cách", max_length=50)
    origin = models.CharField(
        "nguồn gốc", max_length=10, choices=Origin.choices, default=Origin.DOMESTIC
    )
    is_available = models.BooleanField("còn hàng", default=True)

    class Meta:
        verbose_name = "sản phẩm"
        verbose_name_plural = "sản phẩm"

    def __str__(self):
        return self.name


class Order(models.Model):
    customer_name = models.CharField("tên khách hàng", max_length=100)
    phone = models.CharField("số điện thoại", max_length=10)
    address = models.CharField("địa chỉ", max_length=255)
    created_at = models.DateTimeField("thời gian đặt", auto_now_add=True)
    total = models.PositiveIntegerField("tổng tiền (đồng)")
    # Mỗi trang đặt hàng có một mã riêng, nên gửi lại cùng form không tạo thêm đơn.
    submission_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "đơn hàng"
        verbose_name_plural = "đơn hàng"

    def __str__(self):
        return f"Đơn #{self.pk} - {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="đơn hàng",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="sản phẩm",
    )
    product_name = models.CharField("tên sản phẩm", max_length=200)
    package_label = models.CharField("quy cách", max_length=50)
    unit_price = models.PositiveIntegerField("đơn giá (đồng)")
    quantity = models.PositiveIntegerField("số lượng")

    class Meta:
        verbose_name = "chi tiết đơn hàng"
        verbose_name_plural = "chi tiết đơn hàng"

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"

    @property
    def line_total(self) -> int:
        return self.unit_price * self.quantity
