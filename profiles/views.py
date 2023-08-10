from django.shortcuts import render
from django.http import JsonResponse
from django.http import Http404
from django.shortcuts import get_object_or_404
from posts.models import Post, Post_KR, SavedPosts
from accounts.models import User

# serializer
from posts.serializers import PostSerializer, Post_KRSerializer, SavedPostsSerializer

# DRF
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# 인가
from rest_framework.permissions import IsAuthenticated


class GetPosts(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, userid):
        try:
            posts_en = Post.objects.filter(user_id=userid)
            self.check_object_permissions(self.request, posts_en)
            serializer_en = PostSerializer(posts_en, many=True)

            serializer_kr = None
            if serializer_en.data:
                post_id_list = [item["post_id"] for item in serializer_en.data]
                posts_kr = Post_KR.objects.filter(post__post_id__in=post_id_list)
                serializer_kr = Post_KRSerializer(posts_kr, many=True)

            data = {
                "post_en": serializer_en.data,
                "post_kr": serializer_kr.data if serializer_kr else [],
            }
            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetSavedPosts(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, userid):
        try:
            saved_posts = SavedPosts.objects.filter(user=userid)
            self.check_object_permissions(self.request, saved_posts)
            serializer_saved = SavedPostsSerializer(saved_posts, many=True)

            data = {"post_en": serializer_saved.data}
            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
