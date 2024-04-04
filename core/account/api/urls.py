from django.urls import path

from core.account.api.views import *

urlpatterns = [
    path('user/', UserRegistrationAV.as_view(), name='user_registration'),
    path('login/', UserLoginAV.as_view(), name='user_login'),
    path('logout/', UserLogoutAV.as_view(), name='user_logout'),
    path('activate/<str:encoded_pk>/<str:token>/', ActivateAccountAV.as_view(), name='activate-account'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('reset/password/', ResetPasswordAV.as_view(), name='reset_password'),
    path('forgot/password/', ForgotPasswordEmailAV.as_view(), name='forgot_password'),
    path('reset/password/<str:encoded_pk>/<str:token>/', RestPasswordEmailAV.as_view(), name='forgot-password'),
]
