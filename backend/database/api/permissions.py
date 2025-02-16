from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Solo el propietario puede escribir
        return obj.user == request.user

class IsSellerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['seller', 'admin']

class IsCustomerOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user