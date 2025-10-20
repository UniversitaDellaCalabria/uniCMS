# from django.contrib.admin.models import LogEntry
from cms.templates.models import Log

# from cms.contexts.serializers import LogEntrySerializer
from cms.templates.serializers import LogSerializer

from rest_framework import filters, generics
from rest_framework.permissions import IsAdminUser

from .. ordering import StableOrderingFilter
from .. pagination import UniCmsApiPagination


class ObjectLogEntriesList(generics.ListAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter,
                       StableOrderingFilter]
    search_fields = ['user__first_name','user__last_name',
                     'change_message']
    pagination_class = UniCmsApiPagination
    # serializer_class = LogEntrySerializer
    serializer_class = LogSerializer

    def get_queryset(self, object_id=None, content_type_id=None):
        """
        """
        if object_id and content_type_id:
            # return LogEntry.objects.filter(content_type__pk=content_type_id,
            return Log.objects.filter(content_type__pk=content_type_id,
                                           object_id=object_id)
        # return LogEntry.objects.none() # pragma: no cover
        return Log.objects.none() # pragma: no cover

    class Meta:
        abstract = True
