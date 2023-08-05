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


# User의 nation을 비교해서 한국인이면 True 반환
# @login_required
# def is_korean(request):
#     user_nation = request.user.nation

#     if user_nation and user_nation.name == "Korea" or "korea" or "한국" or "대한민국":
#         return True
#     else:
#         return False


# PostList(전체)
class PostList(APIView):
    def get(self, request):
        # if is_korean(request):
        #     posts = Post_KR.objects.all()
        # else:
        #     posts = Post.objects.all()
        print(request.user)

        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

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
        # if is_korean(request):
        #     post = get_object_or_404(Post_KR, post=id)
        # else:
        #     post = get_object_or_404(Post, post_id=id)

        post = get_object_or_404(Post, post_id=id)
        serializer = PostSerializer(post)
        return Response(serializer.data)

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
