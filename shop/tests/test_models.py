from django.test import SimpleTestCase, TestCase

from shop.models import Category, Order, OrderItem, Product
from shop.templatetags.shop_extras import format_vnd


class FormatVndTests(SimpleTestCase):
    def test_formats_with_dot_separator(self):
        self.assertEqual(format_vnd(85000), "85.000đ")
        self.assertEqual(format_vnd(1205000), "1.205.000đ")
        self.assertEqual(format_vnd(0), "0đ")


class OrderItemTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name="Rau", position=1)
        self.product = Product.objects.create(
            name="Rau muống",
            category=category,
            price=15000,
            package_label="bó 500g",
            origin=Product.Origin.DOMESTIC,
        )
        order = Order.objects.create(
            customer_name="An", phone="0901234567", address="1 Lê Lợi", total=45000
        )
        self.item = OrderItem.objects.create(
            order=order,
            product=self.product,
            product_name="Rau muống",
            package_label="bó 500g",
            unit_price=15000,
            quantity=3,
        )

    def test_line_total(self):
        self.assertEqual(self.item.line_total, 45000)

    def test_item_survives_product_deletion(self):
        self.product.delete()
        self.item.refresh_from_db()
        self.assertIsNone(self.item.product)
        self.assertEqual(self.item.product_name, "Rau muống")
        self.assertEqual(self.item.unit_price, 15000)


class WordingTests(SimpleTestCase):
    def test_uses_spec_terms_for_category_and_origin(self):
        self.assertEqual(Category._meta.verbose_name, "nhóm hàng")
        self.assertEqual(Category._meta.verbose_name_plural, "nhóm hàng")
        self.assertEqual(Category._meta.get_field("name").verbose_name, "tên nhóm hàng")
        self.assertEqual(Product._meta.get_field("category").verbose_name, "nhóm hàng")
        self.assertEqual(Product._meta.get_field("origin").verbose_name, "nguồn gốc")
