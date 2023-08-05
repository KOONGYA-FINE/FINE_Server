from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Post, Post_KR

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
            # 영어 posts 중 파싱된 interest 값을 포함하는 게시물 필터링
            posts_en = posts_en.filter(interest__icontains=interest)
            serializer_en = PostSerializer(posts_en, many=True)

            # 한국어 posts 중 파싱된 interest 값을 포함하는 게시물 필터링
            posts_kr = posts_kr.filter(post__interest__icontains=interest)
            serializer_kr = Post_KRSerializer(posts_kr, many=True)

        data = {"post_en": serializer_en.data, "post_kr": serializer_kr.data}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# PostDetail(특정 값)
class PostDetail(APIView):
    def get(self, request, id):
        # 영어 post
        post_en = get_object_or_404(Post, post_id=id)
        serializer_en = PostSerializer(post_en)
        # 한국어 post
        post_kr = get_object_or_404(Post_KR, post_id=id)
        serializer_kr = Post_KRSerializer(post_kr)

        data = {"posts_en": serializer_en.data, "posts_kr": serializer_kr.data}
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
