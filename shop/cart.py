from dataclasses import dataclass

from .models import Product

CART_SESSION_KEY = "cart"
MAX_QUANTITY = 99


@dataclass
class CartLine:
    product: Product
    quantity: int

    @property
    def line_total(self) -> int:
        return self.product.price * self.quantity


class Cart:
    """Giỏ hàng lưu trong session: {"<product_id>": số lượng}."""

    def __init__(self, session):
        self.session = session
        self.items = session.get(CART_SESSION_KEY, {})

    def _save(self):
        self.session[CART_SESSION_KEY] = self.items
        self.session.modified = True  # session chứa dict lồng nhau

    def add(self, product_id: int) -> None:
        key = str(product_id)
        self.items[key] = min(self.items.get(key, 0) + 1, MAX_QUANTITY)
        self._save()

    def set_quantity(self, product_id: int, quantity: int) -> None:
        self.items[str(product_id)] = quantity
        self._save()

    def remove(self, product_id: int) -> None:
        self.items.pop(str(product_id), None)
        self._save()

    def clear(self) -> None:
        self.items = {}
        self._save()

    def lines(self) -> list[CartLine]:
        products = Product.objects.in_bulk([int(pk) for pk in self.items])
        return [
            CartLine(product=products[pk], quantity=self.items[str(pk)])
            for pk in sorted(products)
        ]

    def count(self) -> int:
        return sum(line.quantity for line in self.lines())

    def total(self) -> int:
        return sum(line.line_total for line in self.lines())

    def has_unavailable(self) -> bool:
        return any(not line.product.is_available for line in self.lines())

    def signature(self) -> str:
        """Chuỗi đổi khi giỏ, giá hoặc tình trạng hàng đổi; giỏ trống trả về ''."""
        return ",".join(
            f"{line.product.id}:{line.quantity}:{line.product.price}:{int(line.product.is_available)}"
            for line in self.lines()
        )
