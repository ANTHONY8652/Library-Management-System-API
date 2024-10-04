from rest_framework.permissions import BasePermission
from .models import UserProfile

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.userprofile.role == UserProfile.ADMIN

class IsMemberUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.userprofile.role == UserProfile.MEMBER

class CanViewBook(BasePermission):
    def has_permission(self, request, view):
        return request.user.userprofile.role in ['admin', 'member']

class CanDeleteBook(BasePermission):
    def has_permission(self, request, view):
        return request.user.userprofile.role == 'admin'