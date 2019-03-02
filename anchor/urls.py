from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login, name='reg_login'),
    path('<int:evid>', views.ev_register, name='ev_register'),
    path('ev_dashboard', views.ev_dashboard, name='ev_dashboard'),
    path('details', views.details, name='details'),
]
