

from django.urls import path
from . import views
from .views import ChangePasswordView
from django.contrib.auth import views as auth_views
from .views import ResetPasswordView

app_name = 'User'

urlpatterns = [
    path('', views.home, name="home"),
    path('register/', views.register, name="register"),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    path("aboutus/",views.aboutUs,name="aboutus"),
    path('profile_view/', views.profile_view, name="profile_view"),
    path('seller_profile_view/<int:id>/', views.seller_profile_view, name="seller_profile_view"),
    path('profile_update/', views.profile_update, name="profile_update"),
    path('profile_update_page/', views.profile_update_page, name="profile_update_page"),
    path('update-profile-pic/', views.upload_profile_pic, name='upload_profile_pic'),
    path('otp-verification/', views.otp_verification, name='otp_verification'),
    path('mail-verification/', views.mail_verification, name='mail_verification'),
    path('depo-verification/', views.depo_otp_verification, name='depo_verification'),
    path('change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('password_reset/', ResetPasswordView.as_view(), name='password_reset'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('deposite/', views.deposite, name="deposite"),
    path('get-membership/', views.membership, name="membership"),
    path('confirm-membership/', views.confirm_membership, name='confirm_membership'),
    path('confirm-seller/', views.confirm_seller_request, name='confirm_seller_request'),
]