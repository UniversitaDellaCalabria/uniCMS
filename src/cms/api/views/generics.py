import logging

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import generics
from rest_framework import filters
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAdminUser

from .. concurrency import (is_lock_cache_available,
                            get_lock_from_cache,
                            set_lock_to_cache,
                            LOCK_MESSAGE)
from .. pagination import UniCmsApiPagination, UniCmsSelectOptionsApiPagination


logger = logging.getLogger(__name__)


class UniCMSListCreateAPIView(generics.ListCreateAPIView):

    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter,
                       DjangoFilterBackend,
                       filters.OrderingFilter]
    filterset_fields = ['is_active', 'created', 'modified']
    pagination_class = UniCmsApiPagination

    class Meta:
        abstract = True


def check_locks(item, user, force=False):
    content_type_id = ContentType.objects.get_for_model(item).pk
    object_id = item.pk
    user_id = user.pk
    if is_lock_cache_available() or force:
        lock = get_lock_from_cache(content_type_id, object_id)
        user_lock = lock[0]
        owner_user = get_user_model().objects.filter(pk=user_lock).first()
        if user_lock and not user_lock == user_id:
            logger.debug(f'{user} tried to access to {owner_user} actually used by {item}')
            raise PermissionDenied(LOCK_MESSAGE.format(user=owner_user,
                                                       ttl=lock[1]),
                                   403)
        set_lock_to_cache(user_id, content_type_id, object_id)


class UniCMSCachedRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):

    def patch(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        check_locks(item, request.user)
        return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        check_locks(item, request.user)
        return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        check_locks(item, request.user)
        return super().delete(request, *args, **kwargs)

    class Meta:
        abstract = True


class UniCMSListSelectOptionsAPIView(generics.ListAPIView):

    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter,
                       DjangoFilterBackend,
                       filters.OrderingFilter]
    pagination_class = UniCmsSelectOptionsApiPagination
    ordering = ['id']

    class Meta:
        abstract = True
