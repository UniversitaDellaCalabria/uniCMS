from rest_framework.permissions import BasePermission, SAFE_METHODS


class UNICMSSafePermissions(BasePermission):
    """
    """

    def has_permission(self, request, view):

        method = request.method
        if method in SAFE_METHODS:
            return True

        user = request.user
        if user.is_staff: return True
        if user.is_superuser: return True


class UNICMSUserGetCreatePermissions(BasePermission):
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


class CarouselGetCreatePermissions(UNICMSUserGetCreatePermissions):
    """
    """

    def has_permission(self, request, view):
        return super().has_permission(request, view, 'cmscarousels', 'carousel')


class ContactGetCreatePermissions(UNICMSUserGetCreatePermissions):
    """
    """

    def has_permission(self, request, view):
        return super().has_permission(request, view, 'cmscontacts', 'contact')


class PublicationGetCreatePermissions(UNICMSUserGetCreatePermissions):
    """
    """

    def has_permission(self, request, view):
        return super().has_permission(request, view, 'cmspublications', 'publication')


class MediaGetCreatePermissions(UNICMSUserGetCreatePermissions):
    """
    """

    def has_permission(self, request, view):
        return super().has_permission(request, view, 'cmsmedias', 'media')


class MediaCollectionGetCreatePermissions(UNICMSUserGetCreatePermissions):
    """
    """

    def has_permission(self, request, view):
        return super().has_permission(request, view, 'cmsmedias', 'mediacollection')


class MenuGetCreatePermissions(UNICMSUserGetCreatePermissions):
    """
    """

    def has_permission(self, request, view):
        return super().has_permission(request, view, 'cmsmenus', 'navigationbar')
