from rest_framework.permissions import BasePermission
from .models import UserProfile

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        try:
            return request.user.userprofile.role == UserProfile.ADMIN
        except:
            return False

class IsMemberUser(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        try:
            return request.user.userprofile.role == UserProfile.MEMBER
        except:
            return False

class CanViewBook(BasePermission):
    def has_permission(self, request, view):
        # Allow read operations (GET, HEAD, OPTIONS) for authenticated users
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            if request.user.is_authenticated:
                # Check if user has a profile (should always exist due to signal)
                try:
                    return request.user.userprofile.role in ['admin', 'member']
                except:
                    # If profile doesn't exist, still allow read (will be created)
                    return True
            return False  # Require authentication for viewing
        
        # For write operations (POST, PUT, PATCH, DELETE), require authentication and proper role
        if request.user.is_authenticated:
            try:
                return request.user.userprofile.role in ['admin', 'member']
            except:
                return False
        return False

class CanDeleteBook(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        try:
            return request.user.userprofile.role == 'admin'
        except:
            return False

class IsAdminOrMember(BasePermission):
    """Allow access if user is admin OR member"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        try:
            return request.user.userprofile.role in ['admin', 'member']
        except:
            return False