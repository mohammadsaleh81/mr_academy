# urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from user.views import RequestOTPView, VerifyOTPView, UserProfileView, UserAvatarView

urlpatterns = [
    
    path('auth/request-otp/', RequestOTPView.as_view(), name='request-otp'),
    path('auth/verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('profile/avatar/', UserAvatarView.as_view(), name='user-profile-avatar'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
]