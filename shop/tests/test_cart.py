from django.contrib.sessions.backends.db import SessionStore
from django.test import TestCase
from django.urls import reverse

from shop.cart import MAX_QUANTITY, Cart
from shop.models import Category, Product


class CartTestBase(TestCase):
    def setUp(self):
        veg = Category.objects.create(name="Rau", position=1)
        self.spinach = Product.objects.create(
            name="Rau muống", category=veg, price=15000, package_label="Bó 500g"
        )
        self.eggs = Product.objects.create(
            name="Trứng gà", category=veg, price=35000, package_label="Vỉ 10 quả"
        )
        self.lychee = Product.objects.create(
            name="Vải thiều",
            category=veg,
            price=60000,
            package_label="Kg",
            is_available=False,
        )

    def add(self, product, times=1):
        for _ in range(times):
            self.client.post(reverse("shop:cart_add", args=[product.id]))


class CartViewTests(CartTestBase):
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

    def test_add_redirects_back_to_safe_referer_only(self):
        url = reverse("shop:cart_add", args=[self.spinach.id])
        response = self.client.post(url, HTTP_REFERER="http://testserver/?category=1")
        self.assertRedirects(response, "http://testserver/?category=1", fetch_redirect_response=False)
        response = self.client.post(url, HTTP_REFERER="http://evil.example/")
        self.assertRedirects(response, reverse("shop:cart"))

    def test_update_quantity(self):
        self.add(self.spinach)
        self.client.post(reverse("shop:cart_update", args=[self.spinach.id]), {"quantity": "3"})
        self.assertEqual(self.client.get(reverse("shop:cart")).context["cart_count"], 3)

    def test_update_item_not_in_cart_is_ignored(self):
        self.client.post(reverse("shop:cart_update", args=[self.spinach.id]), {"quantity": "3"})
        self.assertEqual(self.client.get(reverse("shop:cart")).context["cart_count"], 0)

    def test_bad_quantity_keeps_old_value_with_message(self):
        self.add(self.spinach)
        for bad in ["abc", "0", "-1", "1000", ""]:
            response = self.client.post(
                reverse("shop:cart_update", args=[self.spinach.id]), {"quantity": bad}, follow=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["cart_count"], 1)
            self.assertContains(response, "Số lượng phải từ 1 đến 99")

    def test_remove(self):
        self.add(self.spinach)
        self.client.post(reverse("shop:cart_remove", args=[self.spinach.id]))
        self.assertEqual(self.client.get(reverse("shop:cart")).context["cart_count"], 0)

    def test_deleted_product_drops_from_cart(self):
        self.client.post(reverse("shop:cart_add", args=[self.spinach.id]))
        self.spinach.delete()
        response = self.client.get(reverse("shop:cart"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["cart_count"], 0)

    def test_unavailable_line_is_flagged_and_order_button_hidden(self):
        self.client.post(reverse("shop:cart_add", args=[self.spinach.id]))
        Product.objects.filter(id=self.spinach.id).update(is_available=False)
        response = self.client.get(reverse("shop:cart"))
        self.assertContains(response, "Hết hàng")
        self.assertNotContains(response, "/dat-hang/")

    def test_order_button_shown_when_all_available(self):
        self.add(self.spinach)
        self.assertContains(self.client.get(reverse("shop:cart")), "/dat-hang/")

    def test_empty_cart_message(self):
        self.assertContains(self.client.get(reverse("shop:cart")), "Giỏ hàng đang trống")


class CartUnitTests(CartTestBase):
    def test_add_caps_at_max_quantity(self):
        cart = Cart(SessionStore())
        for _ in range(MAX_QUANTITY + 5):
            cart.add(self.spinach.id)
        self.assertEqual(cart.lines()[0].quantity, MAX_QUANTITY)

    def test_totals_and_line_total(self):
        cart = Cart(SessionStore())
        cart.add(self.spinach.id)
        cart.add(self.spinach.id)
        cart.add(self.eggs.id)
        self.assertEqual(cart.total(), 2 * 15000 + 35000)
        self.assertEqual(sorted(l.line_total for l in cart.lines()), [30000, 35000])

    def test_signature_empty_and_stable(self):
        cart = Cart(SessionStore())
        self.assertEqual(cart.signature(), "")
        cart.add(self.eggs.id)
        cart.add(self.spinach.id)
        first = cart.signature()
        self.assertEqual(first, f"{self.spinach.id}:1:15000:1,{self.eggs.id}:1:35000:1")
        self.assertEqual(first, cart.signature())

    def test_signature_changes_with_price_and_availability(self):
        cart = Cart(SessionStore())
        cart.add(self.spinach.id)
        before = cart.signature()
        Product.objects.filter(id=self.spinach.id).update(price=16000)
        priced = cart.signature()
        self.assertNotEqual(before, priced)
        Product.objects.filter(id=self.spinach.id).update(is_available=False)
        self.assertNotEqual(priced, cart.signature())

    def test_has_unavailable_and_clear(self):
        cart = Cart(SessionStore())
        cart.add(self.spinach.id)
        self.assertFalse(cart.has_unavailable())
        Product.objects.filter(id=self.spinach.id).update(is_available=False)
        self.assertTrue(cart.has_unavailable())
        cart.clear()
        self.assertEqual(cart.lines(), [])
        self.assertFalse(cart.has_unavailable())
