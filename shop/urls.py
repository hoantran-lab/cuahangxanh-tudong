from django.urls import path

from . import views

app_name = "shop"

urlpatterns = [
    path("", views.home, name="home"),
    path("gio-hang/", views.cart_detail, name="cart"),
    path("gio-hang/them/<int:product_id>/", views.cart_add, name="cart_add"),
    path("gio-hang/cap-nhat/<int:product_id>/", views.cart_update, name="cart_update"),
    path("gio-hang/xoa/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path("dat-hang/", views.checkout, name="checkout"),
    path("dat-hang/thanh-cong/<int:order_id>/", views.order_success, name="order_success"),
]
