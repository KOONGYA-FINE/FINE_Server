from rest_framework import serializers
from accounts.serializers import UserSerializer
from .models import Post, Post_KR


class PostSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user_id.username", read_only=True)
    school = serializers.CharField(source="user_id.school", read_only=True)
    class Meta:
        model = Post
        fields = "__all__"


class Post_KRSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post_KR
        fields = "__all__"