from django.http import JsonResponse
from rest_framework_simplejwt.serializers import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .serializers import RegisterSerializer, UserSerializer
from .models import User

class EmailVerificationView(APIView):
    serializer_class = UserSerializer

    def get(self, request, email):
        if User.objects.filter(email=email).exists():
            res = Response({
                "accept" : False,
                "message" : "email alreay exists"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            res = Response({
                "accept" : True,
                "message" : "can use email"
            }, status=status.HTTP_200_OK)
            
        return res
        
class RegisterView(APIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=False):
            user = serializer.create(request)
            token = RefreshToken.for_user(user)
            refresh_token = str(token)
            access_token = str(token.access_token)

            res = Response(
                {
                    "user":serializer.data,
                    "message":"register success",
                    "token":{
                        "access_token":access_token,
                        "refresh_token":refresh_token,
                    },
                },
                status=status.HTTP_201_CREATED,
            )
            return res
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        