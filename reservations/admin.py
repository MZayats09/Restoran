from django.contrib import admin

from .models import Reservation, Table


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('number', 'seats', 'pos_x', 'pos_y', 'is_active')
    list_editable = ('seats', 'pos_x', 'pos_y', 'is_active')


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('table', 'full_name', 'phone', 'guests', 'date', 'time_slot', 'status')
    list_filter = ('status', 'date', 'time_slot')
    search_fields = ('full_name', 'phone')
    list_editable = ('status',)
