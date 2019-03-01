from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login, name='reg_login'),
    path('<int:evid>', views.ev_register, name='ev_register')
]
