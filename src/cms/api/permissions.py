from rest_framework.permissions import BasePermission, SAFE_METHODS


class AbstractUserGetCreatePermissions(BasePermission):
    """
    """

    def has_permission(self, request, view, class_name, item_name):
        user = request.user
        if not user.is_staff: return False
        if user.is_superuser: return True

        method = request.method
        if method in SAFE_METHODS:
            return True
        return user.has_perm(f'{class_name}.add_{item_name}')

    class Meta:
        abstract = True


class CarouselGetCreatePermissions(AbstractUserGetCreatePermissions):
    """
    """

    def has_permission(self, request, view):
        return super().has_permission(request, view, 'cmscarousels', 'carousel')


class PublicationGetCreatePermissions(AbstractUserGetCreatePermissions):
    """
    """

    def has_permission(self, request, view):
        return super().has_permission(request, view, 'cmspublications', 'publication')


class MediaGetCreatePermissions(AbstractUserGetCreatePermissions):
    """
    """

    def has_permission(self, request, view):
        return super().has_permission(request, view, 'cmsmedias', 'media')


class MediaCollectionGetCreatePermissions(AbstractUserGetCreatePermissions):
    """
    """

    def has_permission(self, request, view):
        return super().has_permission(request, view, 'cmsmedias', 'mediacollection')


class MenuGetCreatePermissions(AbstractUserGetCreatePermissions):
    """
    """

    def has_permission(self, request, view):
        return super().has_permission(request, view, 'cmsmenus', 'navigationbar')
