from django.shortcuts import render
from django.http import JsonResponse
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Post, Post_KR, SavedPosts
from accounts.models import User

# Q 객체
from django.db.models import Q

# decorator
from django.contrib.auth.decorators import login_required

# serializer
from .serializers import PostSerializer, Post_KRSerializer, SavedPostsSerializer

# DRF
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# 페이지네이션
from rest_framework.pagination import PageNumberPagination

# 인가
from config.permissions import IsWriterOrReadOnly
from rest_framework.permissions import IsAuthenticatedOrReadOnly


# 함수
# Tag 필터링
def apply_filters(queryset, filters):
    if filters.get("interest"):
        interest_list = filters.get("interest").split()
        q = Q()
        for inter in interest_list:
            q |= Q(interest__icontains=inter)
        queryset = queryset.filter(q)

    if filters.get("gender"):
        queryset = queryset.filter(user_id__gender=filters.get("gender"))

    if filters.get("nation"):
        queryset = queryset.filter(user_id__nation=filters.get("nation"))

    return queryset


# 영어 post 저장
def create_en_post(user_id, title, content, interest, instance=None):
    data = {
        "user_id": user_id,
        "title": title,
        "content": content,
        "interest": interest,
        "updated_at": timezone.now(),
    }
    # 인스턴스 값이 들어오면(PUT 요청) 그 인스턴스의 값 수정
    if instance:
        serializer_en = PostSerializer(instance, data=data)
    else:
        serializer_en = PostSerializer(data=data)

    if serializer_en.is_valid():
        serializer_en.save()
        return serializer_en
    else:
        return Response(serializer_en.errors, status=status.HTTP_400_BAD_REQUEST)


# 한국어 post 저장
def create_kr_post(serializer_en, title, content, instance=None):
    data = {
        "post": serializer_en.data["post_id"],
        "title": title,
        "content": content,
        "updated_at": timezone.now(),
    }

    if instance:
        serializer_kr = Post_KRSerializer(instance, data=data)
    else:
        serializer_kr = Post_KRSerializer(data=data)

    if serializer_kr.is_valid():
        serializer_kr.save()
        return serializer_kr
    else:
        return Response(serializer_en.errors, status=status.HTTP_400_BAD_REQUEST)


# 페이지네이션 클래스
class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


# PostList(전체)
class PostList(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]  # 로그인 해야만 post 가능

    # Tag로 필터링 + 페이지네이션 + 정렬 -> 영어 한국어 게시물 모두 response
    def get(self, request):
        order = "-post_id"  # 정렬 기본값
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

        # 적용 필터
        filters = {"interest": interest, "gender": gender, "nation": nation}

        # 필터링 적용
        posts_en = apply_filters(posts_en, filters)

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

        data = {
            "post_en": serializer_en.data,
            "post_kr": serializer_kr.data if serializer_kr else [],
        }
        if data:
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        try:
            language = request.data.get("language")  # 작성한 언어 판단
            user_id = request.data.get("user_id")
            title = request.data.get("title")
            content = request.data.get("content")
            interest = request.data.get("interest")
            translation = request.data.get("translate")

            # 가져온 데이터의 language가 영어일 경우
            if language == "en":
                # translation을 파싱하여(\n을 기준으로) 한국어 post에 값 저장
                if "\n" in translation:
                    translation_list = translation.split("\n", 1)
                    kr_title = translation_list[0].strip()
                    kr_content = translation_list[1].strip()

                # post에 값 저장
                serializer_en = create_en_post(user_id, title, content, interest)
                serializer_kr = create_kr_post(serializer_en, kr_title, kr_content)

                # en, kr 한 번에 담아서 response
                data = {
                    "post_en": serializer_en.data,
                    "post_kr": serializer_kr.data,
                }
                return Response(data, status.HTTP_201_CREATED)

            # 가져온 데이터의 language가 한국어일 경우 (translation == english) language가 영어일 경우와 반대
            else:
                # 번역 데이터 파싱
                if "\n" in translation:
                    translation_list = translation.split("\n", 1)
                    en_title = translation_list[0].strip()
                    en_content = translation_list[1].strip()

                # post에 값 저장
                serializer_en = create_en_post(user_id, en_title, en_content, interest)
                serializer_kr = create_kr_post(serializer_en, title, content)

                data = {
                    "post_en": serializer_en.data,
                    "post_kr": serializer_kr.data,
                }
                return Response(data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"detail": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# PostDetail(특정 값)
class PostDetail(APIView):
    permission_classes = [IsWriterOrReadOnly]  # 로그인 하면 get 가능, 작성자만 put, delete 가능

    def get(self, request, id):
        # 게시물 불러오기
        post_en = get_object_or_404(Post, post_id=id)
        post_kr = get_object_or_404(Post_KR, post_id=id)
        self.check_object_permissions(self.request, post_en)

        # 삭제된 posts인지 확인
        if post_en.is_deleted == True:
            return Response(
                {"detail": "This post is deleted"}, status=status.HTTP_404_NOT_FOUND
            )

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
        post_en = get_object_or_404(Post, post_id=id)
        post_kr = get_object_or_404(Post_KR, post=post_en)
        request.data["user_id"] = request.user.id
        self.check_object_permissions(request, post_en)  # 작성자가 같은지 체크

        # 삭제된 posts인지 확인
        if post_en.is_deleted == True:
            return Response(
                {"detail": "This post is deleted"}, status=status.HTTP_404_NOT_FOUND
            )

        language = request.data.get("language")  # 작성한 언어 판단
        user_id = request.data.get("user_id")
        title = request.data.get("title")
        content = request.data.get("content")
        interest = post_en.interest  # 이전에 작성되었던 interest 유지
        translation = request.data.get("translate")

        # 가져온 데이터의 language가 영어일 경우
        if language == "en":
            # translation을 파싱하여(\n을 기준으로) 한국어 post에 값 저장
            if "\n" in translation:
                translation_list = translation.split("\n", 1)
                kr_title = translation_list[0].strip()
                kr_content = translation_list[1].strip()

            # post에 값 저장
            serializer_en = create_en_post(
                user_id, title, content, interest, instance=post_en
            )
            serializer_kr = create_kr_post(
                serializer_en, kr_title, kr_content, instance=post_kr
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

            # post에 값 저장
            serializer_en = create_en_post(
                user_id, en_title, en_content, interest, instance=post_en
            )
            serializer_kr = create_kr_post(
                serializer_en, title, content, instance=post_kr
            )

            data = {
                "post_en": serializer_en.data,
                "post_kr": serializer_kr.data,
            }
            return Response(data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        try:
            post_en = get_object_or_404(Post, post_id=id)
            post_kr = get_object_or_404(Post_KR, post=post_en)

            # 삭제된 posts인지 확인
            if post_en.is_deleted == True:
                return Response(
                    {"detail": "This post is already deleted"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            request.data["user_id"] = request.user.id
            self.check_object_permissions(request, post_en)  # 작성자가 같은지 체크

            post_en.is_deleted = True
            post_kr.is_deleted = True

            post_en.save()
            post_kr.save()

            return Response("DELETE complete", status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {"detail": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SavePost(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]  # 로그인 해야만 post, delete 가능

    def post(self, request, postId, userid):
        try:
            user = User.objects.get(pk=userid)
            post_en = Post.objects.get(pk=postId)
            post_kr = Post_KR.objects.get(post=post_en)

            data = {"user": user.pk, "post_en": post_en.pk, "post_kr": post_kr.pk}

            serializer_saved = SavedPostsSerializer(data=data)
            if serializer_saved.is_valid():
                serializer_saved.save()
                return Response(serializer_saved.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    serializer_saved.errors, status=status.HTTP_400_BAD_REQUEST
                )
        except:
            return Response(
                {"detail": "Post is not exist"}, status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, postId, userid):
        try:
            user = User.objects.get(pk=userid)
            post_en = Post.objects.get(pk=postId)

            saved_post = SavedPosts.objects.filter(user=user, post_en=post_en).first()

            if saved_post:
                saved_post.is_deleted = True
                saved_post.save()
                return Response("DELETE complete", status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {"detail": "Saved post is not exist"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        except:
            return Response({"detail": "Saved post is not exist"})
