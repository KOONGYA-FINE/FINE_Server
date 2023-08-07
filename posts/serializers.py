from rest_framework import serializers
from accounts.serializers import UserSerializer
from .models import Post, Post_KR


class PostSerializer(serializers.ModelSerializer):
    user_id = UserSerializer()
    class Meta:
        model = Post
        fields = "__all__"


class Post_KRSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post_KR
        fields = "__all__"