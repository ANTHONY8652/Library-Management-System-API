from rest_framework.permissions import BasePermission
from .models import UserProfile

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.userprofile.role == UserProfile.ADMIN

class IsMemberUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.userprofile.role == UserProfile.MEMBER