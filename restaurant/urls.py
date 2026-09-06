from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import StyledAuthenticationForm

urlpatterns = [
    path('', views.home, name='home'),

    path('menu/', views.MenuListView.as_view(), name='menu'),
    path('menu/<int:pk>/', views.DishDetailView.as_view(), name='dish_detail'),
    path('menu/<int:pk>/toggle-availability/', views.toggle_availability, name='toggle_availability'),
    path('reviews/<int:pk>/delete/', views.delete_review, name='delete_review'),

    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:pk>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:pk>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:pk>/', views.cart_remove, name='cart_remove'),

    path('checkout/', views.checkout_view, name='checkout'),

    path('orders/', views.order_history, name='order_history'),
    path('orders/<int:pk>/reorder/', views.order_reorder, name='order_reorder'),

    path('booking/', views.booking_map, name='booking_map'),
    path('booking/book/<int:pk>/', views.booking_create, name='booking_create'),
    path('booking/cancel/<int:pk>/', views.booking_cancel, name='booking_cancel'),

    path('accounts/register/', views.register, name='register'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html', authentication_form=StyledAuthenticationForm), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
]
