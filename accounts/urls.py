from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

urlpatterns = [
    # 이메일 중복 확인
    path('email/<str:email>/', EmailVerificationView.as_view(), name='email_verification'),

    #회원가입/로그인/로그아웃
    path('signup/', RegisterView.as_view()),
    # path('signin/', AuthView.as_view()),
    #토큰
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]