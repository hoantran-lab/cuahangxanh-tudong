from django.db import transaction

from .cart import Cart
from .models import Order, OrderItem


class CartChanged(Exception):
    """Giỏ hàng trống, có hàng hết hoặc đã đổi so với lúc khách xem."""


def place_order(
    cart: Cart, customer_name: str, phone: str, address: str, expected_signature: str
) -> Order:
    with transaction.atomic():
        lines = cart.lines()
        if (
            not lines
            or cart.has_unavailable()
            or cart.signature() != expected_signature
        ):
            raise CartChanged
        order = Order.objects.create(
            customer_name=customer_name,
            phone=phone,
            address=address,
            total=cart.total(),
        )
        OrderItem.objects.bulk_create(
            OrderItem(
                order=order,
                product=line.product,
                product_name=line.product.name,
                package_label=line.product.package_label,
                unit_price=line.product.price,
                quantity=line.quantity,
            )
            for line in lines
        )
        cart.clear()
    return order
