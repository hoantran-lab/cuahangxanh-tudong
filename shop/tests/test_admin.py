from django.contrib.admin import site
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from shop.models import Category, Order, OrderItem, Product


class AdminAccessTests(TestCase):
    def test_anonymous_cannot_see_orders(self):
        for name in ["admin:shop_order_changelist", "admin:shop_product_changelist"]:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 302)
            self.assertIn("/admin/login/", response["Location"])


class AdminTestBase(TestCase):
    def setUp(self):
        get_user_model().objects.create_superuser("chu", "chu@example.com", "mat-khau-thu")
        self.client.login(username="chu", password="mat-khau-thu")
        category = Category.objects.create(name="Rau củ")
        self.product = Product.objects.create(
            name="Rau muống",
            category=category,
            price=15000,
            package_label="Bó 500g",
        )
        self.order = Order.objects.create(
            customer_name="Khách A",
            phone="0901234567",
            address="12 Lê Lợi",
            total=30000,
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            product_name="Rau muống",
            package_label="Bó 500g",
            unit_price=15000,
            quantity=2,
        )


class ProductAdminTests(AdminTestBase):
    def test_price_and_availability_editable_in_list(self):
        admin = site._registry[Product]
        self.assertEqual(set(admin.list_editable), {"price", "is_available"})
        self.assertIn("category", admin.list_filter)

    def test_changelist_edit_saves(self):
        self.client.post(
            reverse("admin:shop_product_changelist"),
            {
                "form-TOTAL_FORMS": "1",
                "form-INITIAL_FORMS": "1",
                "form-MIN_NUM_FORMS": "0",
                "form-MAX_NUM_FORMS": "1000",
                "form-0-id": self.product.id,
                "form-0-price": "20000",
                "_save": "Save",
            },
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.price, 20000)
        self.assertFalse(self.product.is_available)


class OrderAdminTests(AdminTestBase):
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
