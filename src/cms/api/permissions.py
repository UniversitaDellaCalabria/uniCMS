from rest_framework.permissions import BasePermission, SAFE_METHODS


class UserCanAddCarouselOrAdminReadonly(BasePermission):
    """
    """

    def has_permission(self, request, view):
        user = request.user
        if user.is_superuser and user.is_staff: return True
        if not user.is_staff: return False
        if request.method in SAFE_METHODS: return True
        return user.has_perm('cmscarousels.add_carousel')


class UserCanAddMediaOrAdminReadonly(BasePermission):
    """
    """

    def has_permission(self, request, view):
        user = request.user
        if user.is_superuser and user.is_staff: return True
        if not user.is_staff: return False
        if request.method in SAFE_METHODS: return True
        return user.has_perm('cmsmedias.add_media')
