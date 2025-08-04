from django.urls import path,include, re_path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (UserCreationView,
                            UserLoginView,
                            UserProfileView,
                            # ResetPasswordEmailView,
                            ChangePasswordView,
                            ResetPasswordView,
                            UserLogout,
                            UserViewset,
                            # get_user_details_from_token,
                            check_refresh_token,
                            ForgotPasswordView,
                            ResetPasswordView,
                            OTPVerificationView,
                            )


router = DefaultRouter()
router.register(r'allusers', UserViewset, basename="all_users")


urlpatterns = [
    path('user-creation/', UserCreationView.as_view(), name='user_creation'),
    path('user-login/', UserLoginView.as_view(), name='user_login'),
    path('user-profile/', UserProfileView.as_view(), name='user_profile'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    # path('send-reset-password-email/', ResetPasswordEmailView.as_view(), name='rest_password_email'),
    path('user-logout/', UserLogout.as_view(), name='user_logout'),
    path('forgot-password-otp/', ForgotPasswordView.as_view(), name='forgot_password_otp'),
    path('otp-verification/', OTPVerificationView.as_view(), name='otp_verification_view'),
    path('reset-password-otp/', ResetPasswordView.as_view(), name='reset_password_otp'),
    # path('get-user-from-token/', get_user_details_from_token),
    path('check-refresh-token/', check_refresh_token),
]

urlpatterns += router.urls