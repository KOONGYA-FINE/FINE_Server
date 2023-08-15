from rest_framework import serializers
from .models import Place


class PlaceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only = True)
    name = serializers.CharField(required=True)
    user = serializers.IntegerField(source="user.id", read_only = True)
    score = serializers.IntegerField(required=True)
    address = serializers.CharField(required=True)
    latitude = serializers.CharField(required=True)
    longitude = serializers.CharField(required=True)
    tag = serializers.CharField(required=True)
    content = serializers.CharField(required=False)
    image = serializers.ImageField(required=False)  # S3

    class Meta:
        model = Place
        fields = "__all__"
