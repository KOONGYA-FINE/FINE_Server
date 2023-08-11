from django.shortcuts import render
from django.http import Http404
from django.shortcuts import get_object_or_404

# models
from .models import Place

# serializer
from .serializers import PlaceSerializer


# DRF
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# 페이지네이션
from rest_framework.pagination import PageNumberPagination


# PlaceList(전체)
class PlaceList(APIView):
    def get(self, request):
        places = Place.objects.all()
        serializer = PlaceSerializer(places, many=True)
        return Response(serializer.data)

    def place(self, request):
        serializer = PlaceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# PlaceDetail(특정 값)
class PlaceDetail(APIView):
    def get(self, request, id):
        place = get_object_or_404(Place, post_id=id)
        serializer = PlaceSerializer(place)
        return Response(serializer.data)

    def put(self, request, id):
        place = get_object_or_404(Place, post_id=id)
        serializer = PlaceSerializer(place, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        place = get_object_or_404(Place, post_id=id)
        place.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
