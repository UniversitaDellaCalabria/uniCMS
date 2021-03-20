from rest_framework.permissions import BasePermission, SAFE_METHODS


class AbstractUserCanAddObjectorAdminReadonly(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        if user.is_superuser and user.is_staff: return True
        if not user.is_staff: return False
        if request.method in SAFE_METHODS: return True

    class Meta:
        abstract = True


class UserCanAddCarouselOrAdminReadonly(AbstractUserCanAddObjectorAdminReadonly):
    """
    """

    def has_permission(self, request, view):
        super().has_permission(request, view)
        return request.user.has_perm('cmscarousels.add_carousel')


class UserCanAddPublicationOrAdminReadonly(AbstractUserCanAddObjectorAdminReadonly):
    """
    """

    def has_permission(self, request, view):
        super().has_permission(request, view)
        return request.user.has_perm('cmspublications.add_publication')


class UserCanAddMediaOrAdminReadonly(AbstractUserCanAddObjectorAdminReadonly):
    """
    """

    def has_permission(self, request, view):
        super().has_permission(request, view)
        return request.user.has_perm('cmsmedias.add_media')


class UserCanAddMediaCollectionOrAdminReadonly(AbstractUserCanAddObjectorAdminReadonly):
    """
    """

    def has_permission(self, request, view):
        super().has_permission(request, view)
        return request.user.has_perm('cmsmedias.add_mediacollection')


class UserCanAddMenuOrAdminReadonly(AbstractUserCanAddObjectorAdminReadonly):
    """
    """

    def has_permission(self, request, view):
        super().has_permission(request, view)
        return request.user.has_perm('cmsmenus.add_navigationbar')
