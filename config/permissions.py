from rest_framework.permissions import BasePermission
from accounts.models import User
from rest_framework import permissions


class IsWriterOrReadOnly(permissions.BasePermission):  # 근데 왜안됀ㅇ,ㄴㅇ,.ㄴ,.ㅇㄴ,.ㅇ.
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
