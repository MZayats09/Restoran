from django.urls import path

from . import views

app_name = 'reservations'

urlpatterns = [
    path('', views.table_map, name='table_map'),
    path('reserve/<int:table_id>/', views.reserve_table, name='reserve_table'),
    path('my/', views.my_reservations, name='my_reservations'),
    path('cancel/<int:reservation_id>/', views.cancel_reservation, name='cancel_reservation'),
]
