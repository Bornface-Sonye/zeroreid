from django.urls import path
from .views import *
urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('reset-password/', reset_password, name='reset_password'),
    path('reset-password/<str:token>/', reset_password_confirm, name='reset_password_confirm'),
    path('success/<str:serial_number>/', SuccessPageView.as_view(), name='success'),
    path('error/', ErrorPageView.as_view(), name='error'),
    path('logout/', logout, name='logout'),
    
    ]