from django.shortcuts import render

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
