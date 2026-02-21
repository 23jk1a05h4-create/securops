from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('otp-verify/', views.otp_verify, name='otp_verify'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
