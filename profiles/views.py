from django.http import Http404
from django.shortcuts import get_object_or_404
from posts.models import Post, Post_KR, SavedPosts
from accounts.models import User

# serializer
from posts.serializers import PostSerializer, Post_KRSerializer, SavedPostsSerializer
from .serializers import UserProfileSerializer

# DRF
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# 인가
from rest_framework.permissions import IsAuthenticated
from config.permissions import IsOwnAccountOrReadOnly


class UserProfile(APIView):
    permission_classes = [IsOwnAccountOrReadOnly]

    def get(self, request, userId):
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            self.check_object_permissions(
                self.request, userId
            )  # userId와 관계없이 로그인 여부 확인
            try:
                user = User.objects.get(id=userId)
            except:
                return Response(
                    {"message": "user profile not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if user.is_active:
                return Response(
                    {
                        "info": serializer.get_data(user),
                        "message": "get user profile success",
                    },
                    status=status.HTTP_200_OK,
                )

            return Response(
                {"message": "user profile not found"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, userId):
        profile = User.objects.get(id=userId)
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            self.check_object_permissions(
                self.request, profile
            )  # user_id와 관계없이 로그인 여부 확인

            user = serializer.put_data(userId, request.data)
            return Response(
                {"info": user, "message": "user info update success"},
                status=status.HTTP_202_ACCEPTED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, userId):
        profile = User.objects.get(id=userId)
        self.check_object_permissions(request, profile)
        User.objects.delete(request.user)
        return Response(
            {"message": "user delete success"}, status=status.HTTP_204_NO_CONTENT
        )


class GetPosts(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, userId):
        try:
            posts_en = Post.objects.filter(user_id=userId, is_deleted=False)
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

    def get(self, request, userId):
        try:
            # 스크랩된 게시물 필터링
            saved_posts = SavedPosts.objects.filter(user=userId, is_deleted=False)

            self.check_object_permissions(self.request, saved_posts)
            serializer_saved = SavedPostsSerializer(saved_posts, many=True)

            data = {"post_en": serializer_saved.data}
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
