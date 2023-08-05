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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class NationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nation
        fields = "__all__"