from rest_framework import serializers
from .models import Place
from accounts.models import Nation


class PlaceSerializer(serializers.ModelSerializer):
    nation = serializers.CharField(source='nation.name', read_only=True)
    nation_KR = serializers.CharField(source='nation.name_KR', read_only=True)
    class Meta:
        model = Place
        fields = "__all__"