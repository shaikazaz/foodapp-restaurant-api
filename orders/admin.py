from django.contrib import admin
from .models import Restaurant, MenuItem, Order, OrderItem


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ["menu_item", "quantity"]


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ["name", "address"]
    search_fields = ["name"]
    inlines = [MenuItemInline]


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ["name", "restaurant", "price"]
    list_filter = ["restaurant"]
    search_fields = ["name"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "restaurant", "total"]
    list_filter = ["restaurant"]
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["id", "order", "menu_item", "quantity"]
    list_filter = ["order"]