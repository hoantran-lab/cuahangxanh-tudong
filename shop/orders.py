import uuid

from django.db import transaction

from .cart import Cart
from .models import Order, OrderItem


class CartChanged(Exception):
    """Giỏ hàng trống, có hàng hết hoặc đã đổi so với lúc khách xem."""


def place_order(
    cart: Cart,
    customer_name: str,
    phone: str,
    address: str,
    expected_signature: str,
    submission_token: uuid.UUID,
) -> Order:
    with transaction.atomic():
        existing = Order.objects.filter(submission_token=submission_token).first()
        if existing:
            # Form này đã gửi rồi. Chỉ xóa giỏ nếu vẫn là giỏ của form đó,
            # để form cũ gửi lại không xóa giỏ mới của khách.
            if cart.signature() == expected_signature:
                cart.clear()
            return existing

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
            total=sum(line.line_total for line in lines),
            submission_token=submission_token,
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
