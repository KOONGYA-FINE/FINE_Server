from django.shortcuts import render
from rest_framework_simplejwt.serializers import RefreshToken
from rest_framework import serializers
from .models import User, Nation, EmailCode, generate_code, expire_dt
from config.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, SES_SENDER
from django.utils import timezone

import boto3
import botocore

def send_email(to_email, code):
    client = boto3.client('ses',
                aws_access_key_id = AWS_ACCESS_KEY_ID,
                aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
                region_name = AWS_REGION)
    sender = SES_SENDER

    content = render(None, "email.html", {"code": code}).content.decode("utf-8") 

    try:
        response = client.send_email(
            Source = sender,
            Destination={
                "ToAddresses": [
                    to_email,
                ],
            },
            Message={
                "Body": {
                    "Html": {
                        "Charset": "UTF-8",
                        "Data": content,
                    },
                    "Text": {
                        "Charset": "UTF-8",
                        "Data": f"인증번호를 입력해주세요.\n인증번호: {code}",
                    },
                },
                "Subject": {
                    "Charset": "UTF-8",
                    "Data": "[FINE] Email Address Verification Code",
                },
            },
            
        )
        print("success")
    except botocore.exceptions.ClientError as e:
        print(e.response["Error"]["Message"])
    else:
        print("Email sent! Message ID:"),
        print(response["MessageId"])


class EmailVerifySerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)

    class Meta: 
        model = EmailCode
        exclude = ['code']

    def send_code(self, email):
        if EmailCode.objects.filter(email=email).exists():      # 재전송
            new_code = generate_code()
            EmailCode.objects.filter(email=email).update(code=new_code, expired_dt=expire_dt())
            send_email(to_email=email, code=new_code)
            
        else:   # 신규 전송
            email_code = EmailCode.objects.create(email=email)
            send_email(to_email=email, code=email_code.code)
    
    def verify_code(self, code):
        if EmailCode.objects.filter(code=code).exists():
            verify = EmailCode.objects.get(code=code)
            if verify.expired_dt > timezone.now():
                verify.is_verified = True
                verify.save()
            return verify.is_verified
        else:
            return False
    
    

class RegisterSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            email = self.validated_data['email'],
            password = self.validated_data['password']
        )
        return user
    
    def save_token(self, user, token):
        user_permission = User.objects.put_token(user, token)
        return user_permission

    def validate(self, data):
        email = data.get('email', None)

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('email already exists')
        return data

class UserInfoSerializer(serializers.ModelSerializer):

    username = serializers.CharField(required=True)
    nation = serializers.IntegerField(required=True)
    birth = serializers.DateField(required=True)
    school = serializers.CharField(required=True)
    gender = serializers.CharField(required=True)

    class Meta:
        model = User
        exclude = ['id', 'email', 'token', 'password', 'last_login']

    def set_is_allowed(self, email):
        user = User.objects.activate(email)
        return user
    
    def put(self, email, validated_data):
        user = User.objects.put_info(email, 
            username = self.validated_data['username'],
            nation = self.validated_data['nation'],    
            birth = self.validated_data['birth'], 
            school = self.validated_data['school'], 
            gender = self.validated_data['gender'], 
        )
        return user

    def validate(self, data):
        username = data.get('username', None)
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError('username already exists')
        return data

class AuthSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password']

    def save_token(self, user, token):
        user = User.objects.put_token(user, token)
        return user

    def validate(self, data):
        email = data.get('email', None)
        password = data.get('password', None)

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)

            # password 불일치 
            if not user.check_password(password):           
                raise serializers.ValidationError("wrong password")
        else:
            raise serializers.ValidationError("user account not exists")

        token = RefreshToken.for_user(user)
        refresh_token = str(token)
        access_token = str(token.access_token)

        data = {
            'user': user,
            'refresh_token': refresh_token,
            'access_token': access_token,
        }

        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ["token", "is_staff", "is_admin", "is_superuser", "is_active", "is_allowed", "date_joined", "password", "last_login", "birth", "groups", "user_permissions"]

class NationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nation
        fields = "__all__"