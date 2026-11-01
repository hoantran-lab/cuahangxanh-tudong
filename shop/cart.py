CART_SESSION_KEY = "cart"


class Cart:
    """Giỏ hàng lưu trong session: {"<product_id>": số lượng}."""

    def __init__(self, session):
        self.session = session
        self.items = session.get(CART_SESSION_KEY, {})

    def count(self) -> int:
        return sum(self.items.values())
