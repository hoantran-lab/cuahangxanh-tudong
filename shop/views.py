from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .cart import MAX_QUANTITY, Cart
from .models import Category, Product


def home(request):
    categories = Category.objects.all()
    products = Product.objects.select_related("category")

    selected = None
    try:
        selected = categories.filter(pk=int(request.GET.get("category", ""))).first()
    except ValueError:
        pass
    if selected:
        products = products.filter(category=selected)

    products = products.order_by("category__position", "name")
    return render(
        request,
        "shop/home.html",
        {"categories": categories, "products": products, "selected": selected},
    )


def cart_detail(request):
    cart = Cart(request.session)
    return render(
        request,
        "shop/cart.html",
        {"lines": cart.lines(), "total": cart.total(), "has_unavailable": cart.has_unavailable()},
    )


def _redirect_back(request):
    """Về trang trước đó nếu an toàn, không thì về giỏ hàng."""
    referer = request.META.get("HTTP_REFERER", "")
    if url_has_allowed_host_and_scheme(
        referer, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return redirect(referer)
    return redirect("shop:cart")


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if product.is_available:
        Cart(request.session).add(product.id)
        messages.success(request, f"Đã thêm {product.name} vào giỏ hàng.")
    else:
        messages.error(request, f"{product.name} đã hết hàng.")
    return _redirect_back(request)


@require_POST
def cart_update(request, product_id):
    cart = Cart(request.session)
    try:
        quantity = int(request.POST.get("quantity", ""))
    except ValueError:
        quantity = 0
    if not 1 <= quantity <= MAX_QUANTITY:
        messages.error(request, f"Số lượng phải từ 1 đến {MAX_QUANTITY}.")
    elif str(product_id) in cart.items:
        cart.set_quantity(product_id, quantity)
    return redirect("shop:cart")


@require_POST
def cart_remove(request, product_id):
    Cart(request.session).remove(product_id)
    return redirect("shop:cart")
