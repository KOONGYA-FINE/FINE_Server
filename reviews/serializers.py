from rest_framework import serializers
from .models import Review, Review_KR


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"


class ReviewKRSerializer(serializers.ModelSerializer):
    score = serializers.IntegerField(source="review.score", read_only=True)
    review_image = serializers.ImageField(source="review.review_image", read_only=True)

    class Meta:
        model = Review_KR
        fields = "__all__"
