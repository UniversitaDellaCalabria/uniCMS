import logging

from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import Http404
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

# from cms.api.serializers import PublicationSerializer

from cms.contexts.decorators import detect_language
from cms.contexts.models import WebPath
from cms.contexts import settings as contexts_settings

from cms.publications.models import Publication, PublicationContext
from cms.publications.paginators import Paginator
from cms.publications.serializers import PublicationSerializer
from cms.publications.utils import publication_context_base_filter

from rest_framework import filters

from .. pagination import UniCmsApiPagination
from .. permissions import UserCanAddPublicationOrAdminReadonly
from .. utils import check_user_permission_on_object


CMS_CONTEXT_PERMISSIONS = getattr(settings, 'CMS_CONTEXT_PERMISSIONS',
                                  contexts_settings.CMS_CONTEXT_PERMISSIONS)

logger = logging.getLogger(__name__)


# TODO - better get with filters
class PublicationDetail(generics.RetrieveAPIView):
    name = 'publication-detail'
    description = 'News'
    queryset = Publication.objects.filter(is_active=True)
    # state='published')
    serializer_class = PublicationSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        for pub in super(PublicationDetail, self).get_queryset():
            # if pub.is_publicable:
            return pub


@method_decorator(detect_language, name='dispatch')
class ApiPublicationsByContext(APIView):
    """
    """
    description = 'ApiPublicationsByContext'
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAdminUser]

    def get(self, request, webpath_id, category_name=None):
        query_params = publication_context_base_filter()
        query_params.update({'webpath__pk': webpath_id})
        # 'publication__state': 'published'})

        category_name = category_name or request.GET.get('category_name')
        if category_name:
            query_params['publication__category__name__iexact'] = category_name
        pubcontx = PublicationContext.objects.filter(**query_params)
        paginator = Paginator(queryset=pubcontx, request=request)

        try:
            page_num = int(request.GET.get('page_number', 1))
        except Exception as e: # pragma: no cover
            logger.error(f'API {self.__class__.__name__} paginator number: {e}')
            raise ValidationError('Wrong page_number value')

        paged = paginator.get_page(page_num)
        result = paged.serialize()
        return Response(result)


@method_decorator(detect_language, name='dispatch')
class ApiContext(APIView): # pragma: no cover
    """
    """
    description = 'Get publications in Context (WebPath)'

    def get(self, request):
        webpaths = WebPath.objects.filter(is_active=True)
        pubs = ({i.pk: f'{i.site.domain}{i.get_full_path()}'}
                for i in webpaths if i.is_publicable)
        return Response(pubs)


class PublicationList(generics.ListCreateAPIView):
    """
    """
    description = ""
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'subheading', 'content']
    pagination_class = UniCmsApiPagination
    permission_classes = [UserCanAddPublicationOrAdminReadonly]
    serializer_class = PublicationSerializer
    queryset = Publication.objects.all()


class PublicationView(generics.RetrieveUpdateDestroyAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = PublicationSerializer
    error_msg = _("You don't have permissions")

    def get_queryset(self):
        """
        """
        pub_id = self.kwargs['pk']
        publications = Publication.objects.filter(pk=pub_id)
        return publications

    def patch(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        serializer = self.get_serializer(instance=item,
                                         data=request.data,
                                         partial=True)
        if serializer.is_valid(raise_exception=True):
            has_permission = item.is_editable_by(request.user)
            if not has_permission:
                return Response(self.error_msg, status=status.HTTP_403_FORBIDDEN)
            return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        serializer = self.get_serializer(instance=item,
                                         data=request.data)
        if serializer.is_valid(raise_exception=True):
            has_permission = item.is_editable_by(request.user)
            if not has_permission:
                return Response(self.error_msg, status=status.HTTP_403_FORBIDDEN)
            return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        permission = check_user_permission_on_object(request.user,
                                                     item,
                                                     'cmspublications.delete_publication')
        if not permission:
            return Response(self.error_msg, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)
