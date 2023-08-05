from rest_framework_simplejwt.serializers import RefreshToken
from rest_framework import serializers
from .models import User, Nation

class RegisterSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            email = self.validated_data['email'],
            password = self.validated_data['password']
        )

        return user

    def validate(self, data):
        email = data.get('email', None)

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('email already exists')
        
        return data

class AuthSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password']

    def validate(self, data):
        email = data.get('email', None)
        password = data.get('password', None)

        # Member DB에서 username과 일치하는 데이터 존재 여부
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)

            # 데이터 존재하는데 password 불일치
            if not user.check_password(password):
                raise serializers.ValidationError("wrong password")
        else:
            raise serializers.ValidationError("member account not exists")

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
        fields = "__all__"


class NationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nation
        fields = "__all__"