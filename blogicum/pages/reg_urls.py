from django.urls import path
from .views import register

app_name = 'reg'

urlpatterns = [
    path('auth/registration/', register, name='registration'),
]
