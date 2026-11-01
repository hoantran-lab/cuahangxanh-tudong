from django.core.management import call_command
from django.test import TestCase

from shop.models import Category, Product


class SeedTests(TestCase):
    def test_creates_all_categories_and_products(self):
        call_command("seed_shop")
        self.assertEqual(
            list(Category.objects.values_list("name", flat=True)),
            ["Rau", "Củ", "Quả trong nước", "Quả nhập khẩu", "Trứng"],
        )
        self.assertGreaterEqual(Product.objects.count(), 20)
        for category in Category.objects.all():
            self.assertTrue(category.products.exists())

    def test_rerun_keeps_edited_prices_and_adds_no_duplicates(self):
        call_command("seed_shop")
        count = Product.objects.count()
        Product.objects.filter(name="Rau muống").update(price=99000)
        call_command("seed_shop")
        self.assertEqual(Product.objects.count(), count)
        self.assertEqual(Product.objects.get(name="Rau muống").price, 99000)
