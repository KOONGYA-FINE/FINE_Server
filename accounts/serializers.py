from rest_framework import serializers
from .models import User, Nation


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class NationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nation
        fields = "__all__"
