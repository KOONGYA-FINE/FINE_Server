from rest_framework_simplejwt.serializers import RefreshToken
from rest_framework import serializers
from .models import User, Nation

class RegisterSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    
    class Meta:
        model = User
        exclude = ['password']

    def create(self, validated_data):
        user = User.objects.create_user(
            email = self.validated_data['email'],
            password = self.validated_data['password']
        )
        return user
    
    def save_token(self, user, token):
        user = User.objects.put_token(user, token)
        return user

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
        fields = "__all__"

class NationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nation
        fields = "__all__"