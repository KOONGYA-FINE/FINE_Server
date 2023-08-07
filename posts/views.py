from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Post, Post_KR

# Q 객체
from django.db.models import Q

# decorator
from django.contrib.auth.decorators import login_required

# serializer
from .serializers import PostSerializer, Post_KRSerializer

# DRF
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404

# 페이지네이션
from rest_framework.pagination import PageNumberPagination


# 인가
from config.permissions import IsWriterOrReadOnly
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 100


# PostList(전체)
class PostList(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    # Tag로 필터링 + 페이지네이션 + 정렬 -> 영어 한국어 게시물 모두 response
    def get(self, request):
        interest = request.query_params.get("interest")
        gender = request.query_params.get("gender")
        nation = request.query_params.get("nation")
        order = request.query_params.get("order")

        # 영어 posts
        posts_en = Post.objects.all()
        # 영어 정렬
        if order:
            posts_en = posts_en.order_by(order)

        # 한국어 posts
        posts_kr = Post_KR.objects.all()
        # 한국어 정렬
        if order:
            posts_kr = posts_kr.order_by(order)

        # interest Tag 검색
        if interest:
            interest_list = interest.split()
            q = Q()
            for inter in interest_list:
                q |= Q(interest__icontains=inter)
            posts_en = posts_en.filter(q)
        
        # gender Tag 검색
        if gender:
            posts_en = posts_en.filter(user_id__gender=gender)
        
        # nation Tag 검색
        if nation:
            posts_en = posts_en.filter(user_id__nation=nation)

        # 페이지네이션
        paginator = CustomPageNumberPagination()
        paginated_posts_en = paginator.paginate_queryset(posts_en, request)
        serializer_en = PostSerializer(paginated_posts_en, many=True)
        
        # 한국어 게시물 데이터 처리
        serializer_kr = None
        if serializer_en.data:
            # 한국어 posts 중 필터링된 영어 post와 짝꿍 게시물 필터링
            post_id_list = [item["post_id"] for item in serializer_en.data]
            posts_kr = posts_kr.filter(post__post_id__in=post_id_list)
            serializer_kr = Post_KRSerializer(posts_kr, many=True)

        data = {"post_en": serializer_en.data, "post_kr": serializer_kr.data if serializer_kr else []}
        return Response(data, status=status.HTTP_200_OK)


    def post(self, request):
        
        language = request.data.get("language")  # 작성한 언어 판단
        user_id = request.data.get("user_id")
        title = request.data.get("title")
        content = request.data.get("content")
        interest = request.data.get("interest")
        image = request.data.get("image")
        translation = request.data.get("translate")

        # 가져온 데이터의 language가 영어일 경우
        if language == "en":
            # 영어 post에 값 저장
            serializer_en = PostSerializer(
                data={
                    "user_id": user_id,
                    "title": title,
                    "content": content,
                    "interest": interest,
                    "image": image,
                }
            )
            if serializer_en.is_valid():
                serializer_en.save()
            else:
                return Response(
                    serializer_en.errors, status=status.HTTP_400_BAD_REQUEST
                )

            # translation을 파싱하여(\n을 기준으로) 한국어 post에 값 저장
            if "\n" in translation:
                translation_list = translation.split("\n", 1)
                kr_title = translation_list[0].strip()
                kr_content = translation_list[1].strip()

            serializer_kr = Post_KRSerializer(
                data={
                    "post": serializer_en.data["post_id"],
                    "title": kr_title,
                    "content": kr_content,
                }
            )
            if serializer_kr.is_valid():
                serializer_kr.save()
            else:
                return Response(
                    serializer_kr.errors, status=status.HTTP_400_BAD_REQUEST
                )

            # en, kr 한 번에 담아서 response
            data = {
                "post_en": serializer_en.data,
                "post_kr": serializer_kr.data,
            }
            return Response(data, status.HTTP_201_CREATED)

        # 가져온 데이터의 language가 한국어일 경우 (translation == english) language가 영어일 경우와 반대
        else:
            if "\n" in translation:
                translation_list = translation.split("\n", 1)
                en_title = translation_list[0].strip()
                en_content = translation_list[1].strip()

            serializer_en = PostSerializer(
                data={
                    "user_id": user_id,
                    "title": en_title,
                    "content": en_content,
                    "interest": interest,
                    "image": image,
                }
            )
            if serializer_en.is_valid():
                serializer_en.save()
            else:
                return Response(
                    serializer_en.errors, status=status.HTTP_400_BAD_REQUEST
                )

            serializer_kr = Post_KRSerializer(
                data={
                    "post": serializer_en.data["post_id"],
                    "title": title,
                    "content": content,
                }
            )
            if serializer_kr.is_valid():
                serializer_kr.save()
            else:
                return Response(
                    serializer_kr.errors, status=status.HTTP_400_BAD_REQUEST
                )

            data = {
                "post_en": serializer_en.data,
                "post_kr": serializer_kr.data,
            }
            return Response(data, status=status.HTTP_201_CREATED)


# PostDetail(특정 값)
class PostDetail(APIView):
    permission_classes = [IsWriterOrReadOnly]

    def get(self, request, id):
        # 게시물 불러오기
        post_en = get_object_or_404(Post, post_id=id)
        post_kr = get_object_or_404(Post_KR, post_id=id)

        # 시리얼라이저 생성
        serializer_en = PostSerializer(post_en)
        serializer_kr = Post_KRSerializer(post_kr)

        # 데이터 조합
        data = {
            "post_en": serializer_en.data,
            "post_kr": serializer_kr.data,
        }

        return Response(data, status=status.HTTP_200_OK)

    def put(self, request, id):
        post = get_object_or_404(Post, post_id=id)
        request.data["user_id"] = request.user.id
        self.check_object_permissions(request, post)   # 작성자가 같은지 체크
        
        language = request.data.get("language")  # 작성한 언어 판단
        user_id = request.data.get("user_id")
        title = request.data.get("title")
        content = request.data.get("content")
        interest = request.data.get("interest")
        image = request.data.get("image")
        translation = request.data.get("translate")
        
        # 가져온 데이터의 language가 영어일 경우
        if language == "en":
            # 영어 post에 값 저장
            serializer_en = PostSerializer(
                data={
                    "user_id": user_id,
                    "title": title,
                    "content": content,
                    "interest": interest,
                    "image": image,
                }
            )
            if serializer_en.is_valid():
                serializer_en.save()
            else:
                return Response(
                    serializer_en.errors, status=status.HTTP_400_BAD_REQUEST
                )

            # translation을 파싱하여(\n을 기준으로) 한국어 post에 값 저장
            if "\n" in translation:
                translation_list = translation.split("\n", 1)
                kr_title = translation_list[0].strip()
                kr_content = translation_list[1].strip()

            serializer_kr = Post_KRSerializer(
                data={
                    "post": serializer_en.data["post_id"],
                    "title": kr_title,
                    "content": kr_content,
                }
            )
            if serializer_kr.is_valid():
                serializer_kr.save()
            else:
                return Response(
                    serializer_kr.errors, status=status.HTTP_400_BAD_REQUEST
                )

            # en, kr 한 번에 담아서 response
            data = {
                "post_en": serializer_en.data,
                "post_kr": serializer_kr.data,
            }
            return Response(data, status.HTTP_201_CREATED)

        # 가져온 데이터의 language가 한국어일 경우 (translation == english) language가 영어일 경우와 반대
        else:
            if "\n" in translation:
                translation_list = translation.split("\n", 1)
                en_title = translation_list[0].strip()
                en_content = translation_list[1].strip()

            serializer_en = PostSerializer(
                data={
                    "user_id": user_id,
                    "title": en_title,
                    "content": en_content,
                    "interest": interest,
                    "image": image,
                }
            )
            if serializer_en.is_valid():
                serializer_en.save()
            else:
                return Response(
                    serializer_en.errors, status=status.HTTP_400_BAD_REQUEST
                )

            serializer_kr = Post_KRSerializer(
                data={
                    "post": serializer_en.data["post_id"],
                    "title": title,
                    "content": content,
                }
            )
            if serializer_kr.is_valid():
                serializer_kr.save()
            else:
                return Response(
                    serializer_kr.errors, status=status.HTTP_400_BAD_REQUEST
                )

            data = {
                "post_en": serializer_en.data,
                "post_kr": serializer_kr.data,
            }
            return Response(data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        post = get_object_or_404(Post, post_id=id)
        request.data["user_id"] = request.user.id
        self.check_object_permissions(request, post)  # 작성자가 같은지 체크
        post.delete()
        return Response("DELETE complete", status=status.HTTP_204_NO_CONTENT)
