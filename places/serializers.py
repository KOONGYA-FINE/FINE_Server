from rest_framework import serializers
from .models import Place

class PlaceSerializer(serializers.ModelSerializer):   
    name = serializers.CharField(required=True)
    user_id = serializers.IntegerField(source='user.id', required=True)
    score = serializers.FloatField(required=True)  # 평점 - 리뷰 평점 평균
    address = serializers.CharField(required=True)
    latitude = serializers.CharField(required=True)
    longitude = serializers.CharField(required=True)
    tag = serializers.CharField(required=True)
    image = serializers.ImageField(required=False)  # S3
    
    class Meta:
        model = Place
        fields = "__all__"

    