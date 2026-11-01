from django.core.management.base import BaseCommand

from shop.models import Category, Product

DOMESTIC = Product.Origin.DOMESTIC
IMPORTED = Product.Origin.IMPORTED

# (tên nhóm hàng, [(tên, giá, quy cách, nguồn gốc), ...])
SAMPLE_DATA = [
    ("Rau", [
        ("Rau muống", 15000, "Bó 500g", DOMESTIC),
        ("Cải xanh", 18000, "Bó 500g", DOMESTIC),
        ("Cải ngọt", 18000, "Bó 500g", DOMESTIC),
        ("Rau muống nước", 16000, "Bó 500g", DOMESTIC),
        ("Xà lách", 25000, "Cây 300g", DOMESTIC),
    ]),
    ("Củ", [
        ("Cà rốt", 22000, "Túi 500g", DOMESTIC),
        ("Khoai tây", 30000, "Túi 1kg", DOMESTIC),
        ("Củ cải trắng", 20000, "Túi 500g", DOMESTIC),
        ("Hành tây", 28000, "Túi 500g", DOMESTIC),
    ]),
    ("Quả trong nước", [
        ("Xoài cát Hòa Lộc", 85000, "Kg", DOMESTIC),
        ("Bưởi da xanh", 60000, "Quả 1,5kg", DOMESTIC),
        ("Thanh long ruột đỏ", 45000, "Kg", DOMESTIC),
        ("Chuối tiêu", 25000, "Nải 1kg", DOMESTIC),
        ("Cam sành", 40000, "Kg", DOMESTIC),
    ]),
    ("Quả nhập khẩu", [
        ("Táo Envy New Zealand", 120000, "Kg", IMPORTED),
        ("Nho đỏ không hạt Mỹ", 180000, "Kg", IMPORTED),
        ("Lê Hàn Quốc", 130000, "Kg", IMPORTED),
        ("Kiwi vàng New Zealand", 150000, "Hộp 500g", IMPORTED),
    ]),
    ("Trứng", [
        ("Trứng gà", 35000, "Vỉ 10 quả", DOMESTIC),
        ("Trứng vịt", 38000, "Vỉ 10 quả", DOMESTIC),
        ("Trứng cút", 20000, "Vỉ 30 quả", DOMESTIC),
    ]),
]


class Command(BaseCommand):
    help = "Tạo dữ liệu mẫu (nhóm hàng và sản phẩm). Chạy lại không đè giá đã sửa."

    def handle(self, *args, **options):
        created = 0
        for position, (category_name, products) in enumerate(SAMPLE_DATA, start=1):
            category, _ = Category.objects.get_or_create(
                name=category_name, defaults={"position": position}
            )
            for name, price, package_label, origin in products:
                _, was_created = Product.objects.get_or_create(
                    name=name,
                    defaults={
                        "category": category,
                        "price": price,
                        "package_label": package_label,
                        "origin": origin,
                    },
                )
                created += was_created
        self.stdout.write(self.style.SUCCESS(f"Đã thêm {created} sản phẩm mới."))
