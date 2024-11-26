from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff  # Admins have is_staff set to True

class IsModerator(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='moderators').exists()  # Assuming you have a "moderators" group

class IsUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated  # Any authenticated user can access their own profile
