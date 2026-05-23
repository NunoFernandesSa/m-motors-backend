from rest_framework import permissions


class IsOwnerOrCommercial(permissions.BasePermission):
    """
    Custom permission to only allow owners of a folder or commercial users to access it.
    """

    def has_object_permission(self, request, view, obj):
        """
        Allow access if the user is the owner of the folder or a commercial user.
        """

        # Allow access if the user is the owner of the folder
        if obj.user == request.user:
            return True
        
        # Allow access if the user is a commercial
        if request.user.is_commercial:
            return True
        
        # Deny access otherwise
        return False


class CanValidateFolder(permissions.BasePermission):
    """
    Custom permission to only allow commercial users to validate or reject a folder.
    """

    def has_permission(self, request, view):
        """
        Allow access if the user is connected, is a commercial and has the 'can_validate_folder' permission.
        """
        return request.user.is_authenticated and request.user.is_commercial and request.user.has_perm('folders.can_validate_folder')
