from django.urls import path
from django.http import HttpResponse

app_name = 'bookings'

# Временные заглушки
def placeholder_view(request):
    return HttpResponse('Страница бронирования в разработке')

urlpatterns = [
    path('reservation/', placeholder_view, name='reservation_create'),
]