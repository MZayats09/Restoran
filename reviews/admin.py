from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('dish', 'user', 'rating', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'rating')
    search_fields = ('dish__name', 'user__username', 'text')
    list_editable = ('is_approved',)
    actions = ['moderate_hide', 'moderate_show']

    @admin.action(description='Приховати вибрані відгуки (модерація)')
    def moderate_hide(self, request, queryset):
        queryset.update(is_approved=False)

    @admin.action(description='Показати вибрані відгуки')
    def moderate_show(self, request, queryset):
        queryset.update(is_approved=True)
