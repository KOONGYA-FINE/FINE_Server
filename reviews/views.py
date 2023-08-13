from django.shortcuts import render
from django.http import Http404
from django.shortcuts import get_object_or_404

# models
from .models import Review, Review_KR
from places.models import Place

# serializer
from .serializers import ReviewSerializer, ReviewKRSerializer

# DRF
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# 인가
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from config.permissions import IsWriterOrReadOnly, IsWriterOrReadOnlyReview


# Tag 필터링
def apply_filters(queryset, filters):
    if filters.get("place"):
        queryset = queryset.filter(place=filters.get("place"))

    return queryset


def create_en_review(user_id, place, score, content, review_image=None, instance=None):
    data = {
        "user": user_id,
        "place": place,
        "score": score,
        "content": content,
        "review_image": review_image,
    }

    if instance:
        serializer_en = ReviewSerializer(instance, data=data)
    else:
        serializer_en = ReviewSerializer(data=data)

    if serializer_en.is_valid():
        serializer_en.save()
        return serializer_en
    else:
        return Response(serializer_en.errors, status=status.HTTP_400_BAD_REQUEST)


def create_kr_review(serializer_en, content, instance=None):
    data = {"review": serializer_en.data["review_id"], "content": content}

    if instance:
        serializer_kr = ReviewKRSerializer(instance, data=data)
    else:
        serializer_kr = ReviewKRSerializer(data=data)

    if serializer_kr.is_valid():
        serializer_kr.save()
        return serializer_kr
    else:
        return Response(serializer_kr.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewList(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        try:
            place = request.query_params.get("place")

            # 영어 리뷰
            reviews_en = Review.objects.all()
            reviews_en = reviews_en.order_by("-review_id")  # 최신순 정렬

            # 한국어 리뷰
            reviews_kr = Review_KR.objects.all()
            reviews_kr = reviews_kr.order_by("-review_id")

            # 필터링
            filters = {"place": place}
            reviews_en = apply_filters(reviews_en, filters)

            serializer_en = ReviewSerializer(reviews_en, many=True)

            # 한국어 리뷰 데이터 처리
            serializer_kr = None
            if serializer_en.data:
                review_id_list = [item["review_id"] for item in serializer_en.data]
                reviews_kr = reviews_kr.filter(review__review_id__in=review_id_list)
                serializer_kr = ReviewKRSerializer(reviews_kr, many=True)

            data = {
                "review_en": serializer_en.data,
                "review_kr": serializer_kr.data if serializer_kr else [],
                "review_num": len(serializer_en.data),
            }

            if data["review_en"] and data["review_kr"] is not []:
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"detail": "Not found in this filter"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        except Exception as e:
            return Response(
                {"detail": f"An error occurred: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def post(self, request):
        try:
            user_id = request.user.id
            place = request.query_params.get("place")
            language = request.data.get("language")
            score = request.data.get("score")
            content = request.data.get("content")
            review_image = request.data.get("review_image")
            translation = request.data.get("translate")

            if language == "en":
                kr_content = translation

                serializer_en = create_en_review(
                    user_id, place, score, content, review_image
                )
                serializer_kr = create_kr_review(serializer_en, kr_content)

                data = {
                    "review_en": serializer_en.data,
                    "review_kr": serializer_kr.data,
                }
                return Response(data, status.HTTP_201_CREATED)
            else:
                en_content = translation

                serializer_en = create_en_review(user_id, place, score, en_content)
                serializer_kr = create_kr_review(serializer_en, content)

                data = {
                    "review_en": serializer_en.data,
                    "review_kr": serializer_kr.data,
                }
                return Response(data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"detail": f"An error occurred: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ReviewDetail(APIView):
    permission_classes = [IsWriterOrReadOnlyReview]

    def put(self, request, reviewId):
        review_en = get_object_or_404(Review, review_id=reviewId)
        review_kr = get_object_or_404(Review_KR, review=review_en.pk)

        # 인가
        request.data["user_id"] = request.user.id
        self.check_object_permissions(self.request, review_en)

        try:
            user_id = request.user.id
            language = request.data.get("language")
            score = request.data.get("score")
            content = request.data.get("content")
            translation = request.data.get("translate")
            place = request.query_params.get("place")

            if language == "en":
                kr_content = translation

                serializer_en = create_en_review(
                    user_id, place, score, content, instance=review_en
                )
                serializer_kr = create_kr_review(
                    serializer_en, kr_content, instance=review_kr
                )

                data = {
                    "review_en": serializer_en.data,
                    "review_kr": serializer_kr.data,
                }
                return Response(data, status=status.HTTP_201_CREATED)
            else:
                en_content = translation

                serializer_en = create_en_review(
                    user_id, place, score, en_content, instance=review_en
                )
                serializer_kr = create_kr_review(
                    serializer_en, content, instance=review_kr
                )

                data = {
                    "review_en": serializer_en.data,
                    "review_kr": serializer_kr.data,
                }
                return Response(data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"detail": f"An error occurred: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, reviewId):
        review_en = get_object_or_404(Review, review_id=reviewId)
        review_kr = get_object_or_404(Review_KR, review=review_en.pk)

        request.data["user_id"] = request.user.id
        self.check_object_permissions(self.request, review_en)

        try:
            review_en.delete()
            review_kr.delete()
            return Response("DELETE complete", status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {"detail": f"An error occurred: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
