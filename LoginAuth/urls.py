from django.urls import path
from .views import * 
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
urlpatterns = [

    path('register/', RegisterView.as_view(), name="register"),
    path('login/', Login.as_view(), name="login"),
    # path('LogByMail/',Login.as_view()),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('forgotPassword/', forgot_password_request, name='forgot-password'),
    path('resetPassword/', reset_password, name='reset-password'),
    path('verify-otp/', verify_otp, name='verify-otp'),
    
    path('testing/', testing),

    path('createModule/',createModule),
    path('updateModule/',updateModule)
]

