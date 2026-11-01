from django.test import TestCase
from django.urls import reverse

from shop.models import Category, Product


class HomePageTests(TestCase):
    def setUp(self):
        veg = Category.objects.create(name="Rau", position=1)
        self.eggs = Category.objects.create(name="Trứng", position=2)
        Product.objects.create(
            name="Rau muống",
            category=veg,
            price=15000,
            package_label="Bó 500g",
            origin=Product.Origin.DOMESTIC,
        )
        Product.objects.create(
            name="Trứng gà",
            category=self.eggs,
            price=35000,
            package_label="Vỉ 10 quả",
        )
        self.lychee = Product.objects.create(
            name="Vải thiều",
            category=veg,
            price=60000,
            package_label="Kg",
            is_available=False,
        )

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
