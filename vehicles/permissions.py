from rest_framework import permissions

class IsCommercialOrAdmin(permissions.BasePermission):
    """
    Custom permission to check if the user belongs to 'commercial' or 'admin' group.
    """
    def has_permission(self, request, view):
        """
        Check if the user is authenticated and belongs to 'commercial' or 'admin' group.
        """
        return request.user.is_authenticated and request.user.groups.filter(name__in=['commercial', 'admin']).exists()

class CanManageVehicles(permissions.BasePermission):
    """
    Custom permission to check if the user has the 'can_manage_vehicles' permission.
    """
    def has_permission(self, request, view):
        """
        Check if the user is authenticated and has the 'can_manage_vehicles' permission.
        """
        return request.user.is_authenticated and request.user.has_perm('vehicles.can_manage_vehicles')