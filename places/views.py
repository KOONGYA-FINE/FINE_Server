from django.shortcuts import render
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.db.models import Q

# models
from .models import Place
from accounts.models import Nation

# serializer
from .serializers import PlaceSerializer


# DRF
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# 페이지네이션
from rest_framework.pagination import PageNumberPagination

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

class SearchPlace(APIView):
    def get(self, request):
        keyword = request.query_params.get("q")

        results = Place.objects.filter(
            Q(name__contains=keyword)|
            Q(address__contains=keyword)|
            Q(tag__contains=keyword)|
            Q(nation__name__contains=keyword)|
            Q(nation__name_KR__contains=keyword)
        )
        if results.exists() :
            paginator = CustomPageNumberPagination()
            paginated_results = paginator.paginate_queryset(results, request)
            serializer = PlaceSerializer(paginated_results, many=True)
            return Response(
                {
                    "data" : serializer.data,
                    "message": "return search results"
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "message": "no search results found"
                },
                status=status.HTTP_204_NO_CONTENT,
            )


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
