from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import generics
from rest_framework import filters
from rest_framework.permissions import IsAdminUser

from .. pagination import UniCmsApiPagination


class UniCMSListCreateAPIView(generics.ListCreateAPIView):

    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['is_active', 'created', 'modified']
    pagination_class = UniCmsApiPagination

    class Meta:
        abstract = True
