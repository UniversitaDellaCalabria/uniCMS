import logging

from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator

from cms.contexts.decorators import detect_language
from cms.contexts.models import WebPath

from cms.publications.forms import PublicationForm
from cms.publications.models import Publication, PublicationContext
from cms.publications.paginators import Paginator
from cms.publications.serializers import PublicationSerializer, PublicationSelectOptionsSerializer
from cms.publications.utils import publication_context_base_filter

from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.views import APIView

from . generics import UniCMSCachedRetrieveUpdateDestroyAPIView, UniCMSListCreateAPIView, UniCMSListSelectOptionsAPIView, check_locks
from .. exceptions import LoggedPermissionDenied
from .. permissions import PublicationGetCreatePermissions
from .. serializers import UniCMSFormSerializer
from .. utils import check_user_permission_on_object


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
class ApiPublicationsByContextCategory(ApiPublicationsByContext):
    pass


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


class EditorialBoardPublicationsSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        if method == 'POST':
            return 'createEditorialBoardPublication'
        return 'listEditorialBoardPublications'


class PublicationList(UniCMSListCreateAPIView):
    """
    """
    description = ""
    search_fields = ['name', 'title', 'subheading', 'content']
    permission_classes = [PublicationGetCreatePermissions]
    serializer_class = PublicationSerializer
    queryset = Publication.objects.all()
    schema = EditorialBoardPublicationsSchema()


class EditorialBoardPublicationSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        if method == 'GET':
            return 'retrieveEditorialBoardPublication'
        if method == 'PATCH':
            return 'partialUpdateEditorialBoardPublication'
        if method == 'PUT':
            return 'updateEditorialBoardPublication'
        if method == 'DELETE':
            return 'deleteEditorialBoardPublication'


class PublicationView(UniCMSCachedRetrieveUpdateDestroyAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = PublicationSerializer
    schema = EditorialBoardPublicationSchema()

    def get_queryset(self):
        """
        """
        pub_id = self.kwargs['pk']
        publications = Publication.objects.filter(pk=pub_id)
        return publications

    def patch(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        has_permission = item.is_editable_by(request.user)
        if not has_permission:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        has_permission = item.is_editable_by(request.user)
        if not has_permission:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        permission = check_user_permission_on_object(request.user,
                                                     item, 'delete')
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().delete(request, *args, **kwargs)


class EditorialBoardPublicationChangeStatusSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'updateEditorialBoardPublicationStatus'


class PublicationChangeStateView(APIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = PublicationSerializer
    schema = EditorialBoardPublicationChangeStatusSchema()

    def get_queryset(self):
        """
        """
        pub_id = self.kwargs['pk']
        publications = Publication.objects.filter(pk=pub_id)
        return publications

    def get(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        has_permission = item.is_publicable_by(request.user)
        if has_permission:
            check_locks(item, request.user)
            item.is_active = not item.is_active
            item.save()
            result = self.serializer_class(item)
            return Response(result.data)
        raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                     resource=request.method)


# Abstract API classes for every related object of Publication

class PublicationRelatedObjectList(UniCMSListCreateAPIView):

    def get_data(self):
        """
        """
        pk = self.kwargs.get('publication_id')
        if pk:
            self.publication = get_object_or_404(Publication,
                                                 pk=pk)
        else:
            self.publication = None # pragma: no cover

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # get publication
            publication = serializer.validated_data.get('publication')
            # check permissions on publication
            has_permission = publication.is_editable_by(request.user)
            if not has_permission:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            return super().post(request, *args, **kwargs)

    class Meta:
        abstract = True


class PublicationRelatedObject(UniCMSCachedRetrieveUpdateDestroyAPIView):
    """
    """
    permission_classes = [IsAdminUser]

    def get_data(self):
        pub_id = self.kwargs['publication_id']
        self.pk = self.kwargs['pk']
        self.publication = get_object_or_404(Publication, pk=pub_id)

    def patch(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        serializer = self.get_serializer(instance=item,
                                         data=request.data,
                                         partial=True)
        if serializer.is_valid(raise_exception=True):
            publication = item.publication
            # check permissions on publication
            has_permission = publication.is_editable_by(request.user)
            if not has_permission:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        publication = item.publication
        # check permissions on publication
        has_permission = publication.is_editable_by(request.user)
        if not has_permission:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        publication = item.publication
        # check permissions on publication
        has_permission = publication.is_editable_by(request.user)
        if not has_permission:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().delete(request, *args, **kwargs)

    class Meta:
        abstract = True


class PublicationFormView(APIView):

    def get(self, *args, **kwargs):
        form = PublicationForm()
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)


class EditorialBoardPublicationOptionListSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'listPublicationSelectOptions'


class PublicationOptionList(UniCMSListSelectOptionsAPIView):
    """
    """
    description = ""
    search_fields = ['name', 'title']
    serializer_class = PublicationSelectOptionsSerializer
    queryset = Publication.objects.all()
    schema = EditorialBoardPublicationOptionListSchema()


class PublicationOptionView(generics.RetrieveAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = PublicationSelectOptionsSerializer

    def get_queryset(self):
        """
        """
        pub_id = self.kwargs['pk']
        publications = Publication.objects.filter(pk=pub_id)
        return publications
