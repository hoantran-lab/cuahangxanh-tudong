import uuid

from django.test import Client, TestCase
from django.urls import reverse

from shop.cart import Cart
from shop.models import Category, Order, Product
from shop.orders import place_order


class CheckoutBase(TestCase):
    def setUp(self):
        veg = Category.objects.create(name="Rau", position=1)
        self.spinach = Product.objects.create(
            name="Rau muống", category=veg, price=15000, package_label="Bó 500g"
        )
        for _ in range(2):
            self.client.post(reverse("shop:cart_add", args=[self.spinach.id]))

    def form_data(self, **overrides):
        response = self.client.get(reverse("shop:checkout"))
        data = {
            "customer_name": "Nguyễn Văn A",
            "phone": "0901234567",
            "address": "12 Lê Lợi, Quận 1",
            "cart_signature": response.context["form"].initial["cart_signature"],
            "submission_token": response.context["form"].initial["submission_token"],
        }
        data.update(overrides)
        return data

    def submit(self, follow=False, **overrides):
        return self.client.post(
            reverse("shop:checkout"), self.form_data(**overrides), follow=follow
        )


class CheckoutTests(CheckoutBase):
    def test_success_creates_order_with_snapshot(self):
        response = self.submit(follow=True)
        order = Order.objects.get()
        self.assertEqual(order.total, 30000)
        item = order.items.get()
        self.assertEqual(
            (item.product_name, item.package_label, item.unit_price, item.quantity),
            ("Rau muống", "Bó 500g", 15000, 2),
        )
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

    def test_phone_with_separators_is_normalized(self):
        self.submit(phone="090 123.4567")
        self.assertEqual(Order.objects.get().phone, "0901234567")

    def test_invalid_customer_data_rejected_and_cart_kept(self):
        for field, value in [
            ("phone", "12345"),
            ("phone", "1901234567"),
            ("customer_name", "   "),
            ("address", ""),
        ]:
            response = self.submit(**{field: value})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(Order.objects.count(), 0)
            self.assertEqual(response.context["cart_count"], 2)

    def test_vietnamese_text_saved_intact(self):
        self.submit(customer_name="Nguyễn Thị Ánh")
        self.assertEqual(Order.objects.get().customer_name, "Nguyễn Thị Ánh")

    def test_redirect_url_has_no_customer_details(self):
        response = self.submit()
        order = Order.objects.get()
        self.assertEqual(response.url, reverse("shop:order_success", args=[order.id]))


class DoubleSubmitTests(CheckoutBase):
    def test_same_token_on_two_loaded_carts_creates_one_order(self):
        first = Cart(self.client.session)
        second = Cart(self.client.session)
        signature = first.signature()
        token = uuid.uuid4()
        customer = ("Nguyễn Văn A", "0901234567", "12 Lê Lợi")

        order = place_order(first, *customer, signature, token)
        again = place_order(second, *customer, signature, token)

        self.assertEqual(again.pk, order.pk)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(order.submission_token, token)
        self.assertEqual(second.items, {})

    def test_sequential_double_submit_ends_on_success_page(self):
        data = self.form_data()
        self.client.post(reverse("shop:checkout"), data)
        response = self.client.post(reverse("shop:checkout"), data, follow=True)
        order = Order.objects.get()
        self.assertRedirects(response, reverse("shop:order_success", args=[order.id]))
        self.assertContains(response, f"#{order.id}")

    def test_old_form_resubmitted_keeps_new_cart(self):
        veg = self.spinach.category
        eggs = Product.objects.create(
            name="Trứng gà", category=veg, price=35000, package_label="Vỉ 10 quả"
        )
        data = self.form_data()
        self.client.post(reverse("shop:checkout"), data)
        self.client.post(reverse("shop:cart_add", args=[eggs.id]))

        response = self.client.post(reverse("shop:checkout"), data, follow=True)

        order = Order.objects.get()
        self.assertContains(response, f"#{order.id}")
        self.assertEqual(response.context["cart_count"], 1)
        self.assertEqual(Cart(self.client.session).items, {str(eggs.id): 1})

    def test_each_checkout_page_gets_a_fresh_token(self):
        self.assertNotEqual(
            self.form_data()["submission_token"], self.form_data()["submission_token"]
        )

    def test_invalid_form_keeps_posted_token(self):
        data = self.form_data(phone="12345")
        response = self.client.post(reverse("shop:checkout"), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(data["submission_token"]))

    def test_missing_token_is_rejected(self):
        data = self.form_data()
        del data["submission_token"]
        response = self.client.post(reverse("shop:checkout"), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.count(), 0)

    def test_invalid_form_with_empty_cart_redirects_to_cart(self):
        data = self.form_data(phone="12345")
        self.client.post(reverse("shop:cart_remove", args=[self.spinach.id]))
        response = self.client.post(reverse("shop:checkout"), data)
        self.assertRedirects(response, reverse("shop:cart"))

    def test_new_token_with_empty_cart_creates_no_order(self):
        data = self.form_data()
        self.client.post(reverse("shop:cart_remove", args=[self.spinach.id]))
        response = self.client.post(reverse("shop:checkout"), data)
        self.assertRedirects(response, reverse("shop:cart"))
        self.assertEqual(Order.objects.count(), 0)


class OrderSuccessPrivacyTests(CheckoutBase):
    def test_other_visitor_cannot_view_success_page(self):
        self.submit()
        order = Order.objects.get()
        response = Client().get(reverse("shop:order_success", args=[order.id]))
        self.assertRedirects(response, reverse("shop:home"))

    def test_success_page_has_no_customer_details(self):
        response = self.submit(follow=True)
        self.assertNotContains(response, "0901234567")
        self.assertNotContains(response, "Nguyễn Văn A")
        self.assertNotContains(response, "Lê Lợi")
