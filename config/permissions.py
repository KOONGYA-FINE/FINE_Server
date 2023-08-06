from rest_framework.permissions import BasePermission
from accounts.models import User
from rest_framework import permissions


class IsWriterOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # 모든 요청에 대해 읽기 권한은 허용
        # SAFE_METHODS에는 GET, HEAD, OPTIONS가 있음
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user_id == request.user
