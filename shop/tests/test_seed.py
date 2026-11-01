from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from shop.models import Category, Product


def seed():
    call_command("seed_shop", stdout=StringIO())


class SeedTests(TestCase):
    def test_creates_all_categories_and_products(self):
        seed()
        self.assertEqual(
            list(Category.objects.values_list("name", flat=True)),
            ["Rau", "Củ", "Quả trong nước", "Quả nhập khẩu", "Trứng"],
        )
        self.assertGreaterEqual(Product.objects.count(), 20)
        for category in Category.objects.all():
            self.assertTrue(category.products.exists())

    def test_rerun_keeps_edited_prices_and_adds_no_duplicates(self):
        seed()
        count = Product.objects.count()
        Product.objects.filter(name="Rau muống").update(price=99000)
        seed()
        self.assertEqual(Product.objects.count(), count)
        self.assertEqual(Product.objects.get(name="Rau muống").price, 99000)

    def test_rerun_after_moving_product_to_other_category_adds_no_duplicate(self):
        seed()
        count = Product.objects.count()
        other = Category.objects.get(name="Củ")
        Product.objects.filter(name="Rau muống").update(category=other)
        seed()
        self.assertEqual(Product.objects.count(), count)
        self.assertEqual(Product.objects.get(name="Rau muống").category, other)
