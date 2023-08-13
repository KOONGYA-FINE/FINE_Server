from rest_framework import serializers
from .models import Place

class PlaceSerializer(serializers.ModelSerializer):
    nation = serializers.CharField(source='nation.name', read_only=True)
    
    class Meta:
        model = Place
        fields = "__all__"