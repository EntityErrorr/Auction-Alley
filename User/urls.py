from django.urls import path
from . import views


app_name = 'User'

urlpatterns = [
    path('', views.home, name="home"),
    path('register/', views.register, name="register"),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('profile_view/', views.profile_view, name="profile_view"),
    path('profile_update/', views.profile_update, name="profile_update"),
    path('profile_update_page/', views.profile_update_page, name="profile_update_page"),
    path('otp-verification/', views.otp_verification, name='otp_verification'),
    path('mail-verification/', views.mail_verification, name='mail_verification'),
    # path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
]