from django.http import JsonResponse
from rest_framework_simplejwt.serializers import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .serializers import RegisterSerializer, AuthSerializer, UserInfoSerializer
from .models import User

class EmailVerificationView(APIView):

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
            serializer.save_token(user, refresh_token)

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
        
class UserInfoView(APIView):    
    serializer_class = UserInfoSerializer

    def put(self, request):

        serializer = self.serializer_class(data=request.data)
        print("activate")

        if serializer.is_valid(raise_exception=False):
            if User.objects.filter(email=request.user).exists():
                serializer.set_is_allowed(request.user)
                serializer.put(request.user, request)
                res = Response(
                {
                    "user": serializer.data,
                    "message":"Insert user_info success"
                },
                status=status.HTTP_200_OK,
            )
            return res
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AuthView(APIView):
    serializer_class = AuthSerializer

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
						
        if serializer.is_valid(raise_exception=False):
            user = serializer.validated_data['user']
            access_token = serializer.validated_data['access_token']
            refresh_token = serializer.validated_data['refresh_token']
            serializer.save_token(user, refresh_token)

            res = Response(
                {
                    "user": {
                            "id":user.id,
                            "email":user.email,
                    },
                    "message":"login success",
                    "token":{
                        "access_token":access_token,
                        "refresh_token":refresh_token,
                    },
                },
                status=status.HTTP_200_OK,
            )
            res.set_cookie("access-token", access_token, httponly=True)
            res.set_cookie("refresh-token", refresh_token, httponly=True)
            return res
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request):
        res = Response({
			"message":"logout success"
		}, status=status.HTTP_202_ACCEPTED)
				
		# cookie에서 token 값들을 제거함
        res.delete_cookie("access-token")
        res.delete_cookie("refresh-token")
        return res