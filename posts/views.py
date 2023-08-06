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


# PostList(전체)
class PostList(APIView):
    def get(self, request):
        interest = request.query_params.get("interest")

        # 영어 posts
        posts_en = Post.objects.all()
        serializer_en = PostSerializer(posts_en, many=True)

        # 한국어 posts
        posts_kr = Post_KR.objects.all()
        serializer_kr = Post_KRSerializer(posts_kr, many=True)

        if interest:
            # 입력받은 query 파싱
            interest_list = interest.split()

            # Q 객체를 통해 파싱된 interest를 포함하는 post만 필터링
            q = Q()
            for inter in interest_list:
                q |= Q(interest__icontains=inter)

            # 영어 posts 중 파싱된 interest 값을 포함하는 게시물 필터링
            posts_en = posts_en.filter(q)
            serializer_en = PostSerializer(posts_en, many=True)

            print(serializer_en.data)
            # 한국어 posts 중 필터링된 영어 post와 짝꿍 게시물 필터링
            if serializer_en.data != []:
                post_id_list = [item["post_id"] for item in serializer_en.data]
                posts_kr = posts_kr.filter(post__post_id__in=post_id_list)
                serializer_kr = Post_KRSerializer(posts_kr, many=True)

        data = {"post_en": serializer_en.data, "post_kr": serializer_kr.data}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        user_id = request.data.get("user_id")
        language = request.data.get("language")
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

            # translation을 파싱하여 한국어 post에 값 저장
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

            data = {
                "serializer_en": serializer_en.data,
                "serializer_kr": serializer_kr.data,
            }
            return Response(data, status.HTTP_201_CREATED)

        # 가져온 데이터의 language가 한국어일 경우 (translation == english)
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
                "serializer_en": serializer_en.data,
                "serializer_kr": serializer_kr.data,
            }
            return Response(data, status=status.HTTP_201_CREATED)


# PostDetail(특정 값)
class PostDetail(APIView):
    def get(self, request, id):
        # 게시물 불러오기
        post_en = get_object_or_404(Post, post_id=id)
        # post_kr = get_object_or_404(Post_KR, post_id=id)

        # 시리얼라이저 생성
        serializer_en = PostSerializer(post_en)
        # serializer_kr = Post_KRSerializer(post_kr)

        # 데이터 조합
        data = {
            "post_en": serializer_en.data,
            # "post_kr": serializer_kr.data,
        }

        return Response(data, status=status.HTTP_200_OK)

    def put(self, request, id):
        post = get_object_or_404(Post, post_id=id)
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        post = get_object_or_404(Post, post_id=id)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
