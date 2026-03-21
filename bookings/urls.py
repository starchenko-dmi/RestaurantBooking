from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('reservation/create/', views.reservation_create, name='reservation_create'),
    path('reservation/table-select/', views.table_select, name='table_select'),
    path('reservations/', views.reservation_list, name='reservation_list'),
    path('reservation/<int:pk>/', views.reservation_detail, name='reservation_detail'),
    path('reservation/<int:pk>/cancel/', views.reservation_cancel, name='reservation_cancel'),
]