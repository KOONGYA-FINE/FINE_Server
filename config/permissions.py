from rest_framework.permissions import BasePermission
from accounts.models import User
from rest_framework import permissions


class IsWriterOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ("HEAD", "OPTIONS"):
            return True
        elif request.method == "GET":
            if request.user and request.user.is_authenticated:
                return True
            else:
                return False  # 로그인하지 않은 사용자의 GET 요청을 거부
        else:
            return obj.user_id == request.user


class IsWriterOrReadOnlyReview(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ("HEAD", "OPTIONS"):
            return True
        elif request.method == "GET":
            if request.user and request.user.is_authenticated:
                return True
            else:
                return False  # 로그인하지 않은 사용자의 GET 요청을 거부
        else:
            return obj.user_id == request.user.id


class IsOwnAccountOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, profile):
        if request.method in (
            "GET",
            "HEAD",
            "OPTIONS",
        ):  # SAFE_METHODS - IsAuthenticated
            return bool(request.user and request.user.is_authenticated)

        else:  # is_active + 본인 확인
            if User.objects.filter(email=request.user).exists():
                user = User.objects.get(email=request.user)
                if user.is_active:
                    return bool(
                        user.id == profile.id
                        and request.user
                        and request.user.is_authenticated
                    )
                else:
                    return False
            else:
                return False
