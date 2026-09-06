from django.contrib import admin

from .models import Dish, Review, RestaurantTable, Booking, Order, OrderItem


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'available', 'average_rating')
    list_filter = ('category', 'available')
    search_fields = ('name', 'description')
    list_editable = ('available', 'price')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('dish', 'user', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('text', 'user__username', 'dish__name')
    actions = ['delete_selected']


@admin.register(RestaurantTable)
class RestaurantTableAdmin(admin.ModelAdmin):
    list_display = ('number', 'seats', 'is_vip', 'is_terrace', 'pos_x', 'pos_y')
    list_editable = ('seats', 'is_vip', 'is_terrace', 'pos_x', 'pos_y')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('table', 'date', 'time', 'guests', 'name', 'phone', 'user')
    list_filter = ('date',)
    search_fields = ('name', 'phone')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('dish_name', 'price', 'quantity')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'status', 'payment_method', 'total', 'created_at')
    list_filter = ('status', 'payment_method')
    list_editable = ('status',)
    inlines = [OrderItemInline]
