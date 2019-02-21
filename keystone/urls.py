from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('logout', views.logout, name='logout'),
    path('', views.online_reg, name='online_reg'),
    # path('dashboard', views.dashboard, name='dashboard'),
    path('register', views.temp_reg, name='temp_reg'),
    path('temp/<int:id>', views.temp_submit, name="temp_submit"),
    path('zeal_reg', views.register, name='register'),
]
