from django.urls import path
from django.http import HttpResponse

app_name = 'users'

# Временные заглушки (view-функции)
def placeholder_view(request):
    return HttpResponse('Страница в разработке')

urlpatterns = [
    path('login/', placeholder_view, name='login'),
    path('register/', placeholder_view, name='register'),
    path('profile/', placeholder_view, name='profile'),
    path('logout/', placeholder_view, name='logout'),
]