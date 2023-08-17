from django.shortcuts import render
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Place
from accounts.models import User

from .serializers import PlaceSerializer, PlaceImageSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from config.permissions import IsWriterOrReadOnlyReview


def apply_filters(queryset, filters):
    if filters.get("tag"):
        tag_list = filters.get("tag").split()
        q = Q()
        for tag in tag_list:
            q |= Q(tag__icontains=tag)
        queryset = queryset.filter(q)
    return queryset


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 9
    page_size_query_param = "page_size"
    max_page_size = 100


class SearchPlace(APIView):
    def get(self, request):
        keyword = request.query_params.get("q")
        tag = request.query_params.get("tag")
        filters = {"tag": tag}

        results = Place.objects.filter(
            Q(name__icontains=keyword)
            | Q(address__icontains=keyword)
            | Q(tag__icontains=keyword)
            | Q(content__icontains=keyword)
        )

        results = apply_filters(results, filters)

        if results.exists():
            paginator = CustomPageNumberPagination()
            paginated_results = paginator.paginate_queryset(results, request)
            serializer = PlaceSerializer(paginated_results, many=True)

            return Response(
                {"data": serializer.data, "message": "return search results"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": "no search results found"},
                status=status.HTTP_204_NO_CONTENT,
            )


# PlaceList(전체)
class PlaceList(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        tag = request.query_params.get("tag")
        filters = {"tag": tag}
        places = Place.objects.all()
        places = apply_filters(places, filters)
        places = places.order_by("-id")  # 내림차순 정렬
        paginator = CustomPageNumberPagination()
        paginated_results = paginator.paginate_queryset(places, request)
        serializer = PlaceSerializer(paginated_results, many=True)
        return Response(
            {"data": serializer.data, "message": "return places list"},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        request.data._mutable = True
        request.data["user"] = request.user.id
        request.data._mutable = False
        serializer = PlaceImageSerializer(data=request.data)
        if serializer.is_valid():
            info = serializer.create(request.data)
            result = {"message": "review create success"}
            result.update({"data": info})
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# PlaceDetail(특정 값)
class PlaceDetail(APIView):
    permission_classes = [IsWriterOrReadOnlyReview]

    def get(self, request, id):
        place = get_object_or_404(Place, id=id)
        serializer = PlaceSerializer(place)
        return Response(
            {"data": serializer.data, "message": "return place info"},
            status=status.HTTP_200_OK,
        )

    def put(self, request, id):  # score, tag, content, image 수정 가능
        place = get_object_or_404(Place, id=id)
        self.check_object_permissions(request, place)
        request.data._mutable = True
        request.data["user"] = request.user.id
        request.data.update(
            {
                "id": id,
                "name": place.name,
                "address": place.address,
                "longitude": place.longitude,
                "latitude": place.latitude,
            }
        )
        request.data._mutable = False
        serializer = PlaceImageSerializer(place, data=request.data)

        if serializer.is_valid():
            place = serializer.update(place, request.data)
            result = {"message": "review put request success"}
            result.update({"data": place})
            return Response(result, status=status.HTTP_200_OK)
        else:
            request.data._mutable = False
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        place = get_object_or_404(Place, id=id)
        self.check_object_permissions(self.request, place)
        place.delete()
        return Response(
            {"message": "delete success"}, status=status.HTTP_204_NO_CONTENT
        )
