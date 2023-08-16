from django.shortcuts import render
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Place
from accounts.models import User

from .serializers import PlaceSerializer

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

        results = Place.objects.filter(
            Q(name__contains=keyword)
            | Q(address__contains=keyword)
            | Q(tag__contains=keyword)
            | Q(content__contains=keyword)
        )

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
        paginator = CustomPageNumberPagination()
        paginated_results = paginator.paginate_queryset(places, request)
        serializer = PlaceSerializer(paginated_results, many=True)
        return Response(
            {"data": serializer.data, "message": "return places list"},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        request.data["user"] = request.user
        serializer = PlaceSerializer(data=request.data)
        if serializer.is_valid():
            place = serializer.create(request.data)
            result = {
                "message": "review create success",
                "id": place.id,
                "username": request.user.username,
            }
            result.update(serializer.data)
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
        self.check_object_permissions(self.request, place)
        request.data["id"] = place.id
        request.data["name"] = place.name
        request.data["user"] = request.user
        request.data["address"] = place.address
        request.data["latitude"] = place.latitude
        request.data["longitude"] = place.longitude

        if request.data.get("score") is None:
            request.data["score"] = place.score
        if request.data.get("tag") is None:
            request.data["tag"] = place.tag

        serializer = PlaceSerializer(place, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        place = get_object_or_404(Place, id=id)
        self.check_object_permissions(self.request, place)
        place.delete()
        return Response(
            {"message": "delete success"}, status=status.HTTP_204_NO_CONTENT
        )
