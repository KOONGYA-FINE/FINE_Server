from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenVerifyView

urlpatterns = [
    # 이메일 중복 확인
    path('email/<str:email>/', EmailCheckView.as_view(), name='email_check'),

    # 이메일 인증 코드 전송 및 확인
    path('email-verify/', EmailVerifyView.as_view(), name='email_verify'),

    #회원가입, 회원정보 입력, 로그인/로그아웃
    path('signup/', RegisterView.as_view()),
    path('userInfo/', UserInfoView.as_view()),
    path('signin/', AuthView.as_view()),

    #토큰
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]