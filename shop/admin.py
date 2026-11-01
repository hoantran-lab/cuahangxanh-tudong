from django.contrib import admin

from .models import Category, Order, OrderItem, Product
from .templatetags.shop_extras import format_vnd


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "position"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "package_label", "origin", "price", "is_available"]
    list_editable = ["price", "is_available"]
    list_filter = ["category", "is_available"]
    search_fields = ["name"]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ["product_name", "package_label", "unit_price", "quantity"]
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at", "customer_name", "phone", "total_display"]
    inlines = [OrderItemInline]

    @admin.display(description="tổng tiền", ordering="total")
    def total_display(self, obj):
        return format_vnd(obj.total)

    # Đơn hàng chỉ để xem: chặn thêm và sửa, vẫn giữ quyền xem và xóa.
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
