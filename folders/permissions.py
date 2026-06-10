from rest_framework import permissions


class IsOwnerOrCommercial(permissions.BasePermission):
    """
    Custom permission to only allow owners of a folder or commercial users to access it.
    """

    def has_object_permission(self, request, view, obj):
        """
        Allow access if the user is the owner of the folder or a commercial user.
        """
        if obj.user == request.user:
            return True
        return request.user.groups.filter(name__in=['commercial', 'admin']).exists()


class CanValidateFolder(permissions.BasePermission):
    """
    Custom permission to only allow commercial users to validate or reject a folder.
    """

    def has_permission(self, request, view):
        """
        Allow access if the user is connected, is in commercial/admin group and has the permission.
        """
        return (request.user.is_authenticated and
                request.user.groups.filter(name__in=['commercial', 'admin']).exists() and
                request.user.has_perm('folders.can_validate_folder'))