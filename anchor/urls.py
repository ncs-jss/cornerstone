from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login, name='reg_login'),
]
