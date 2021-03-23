from django.http import Http404
from django.shortcuts import get_object_or_404

from cms.pages.forms import PageLocalizationForm
from cms.pages.models import *
from cms.pages.serializers import *

from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from . generics import *

from .. exceptions import LoggedPermissionDenied
from .. serializers import UniCMSFormSerializer


class PageLocalizationList(UniCMSListCreateAPIView):
    """
    """
    description = ""
    filterset_fields = ['is_active', 'created', 'modified']
    search_fields = ['title', 'language']
    serializer_class = PageLocalizationSerializer

    def get_queryset(self):
        """
        """
        site_id = self.kwargs.get('site_id')
        webpath_id = self.kwargs.get('webpath_id')
        if site_id and webpath_id:
            site = get_object_or_404(WebSite, pk=site_id, is_active=True)
            if not site.is_managed_by(self.request.user):
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=site)
            pk = self.kwargs['page_id']
            page = get_object_or_404(Page,
                                     pk=pk,
                                     webpath__pk=webpath_id,
                                     webpath__site__pk=site_id)
            return PageLocalization.objects.filter(page=page)
        else:
            return PageLocalization.objects.none() # pragma: no cover

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # get page
            page = serializer.validated_data.get('page')
            # check permissions on page
            has_permission = page.is_localizable_by(request.user)
            if not has_permission:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            return super().post(request, *args, **kwargs)


class PageLocalizationView(UniCMSCachedRetrieveUpdateDestroyAPIView):
    """
    """
    description = ""
    serializer_class = PageLocalizationSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        """
        """
        site_id = self.kwargs['site_id']
        site = get_object_or_404(WebSite, pk=site_id, is_active=True)
        if not site.is_managed_by(self.request.user):
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=site)
        webpath_id = self.kwargs['webpath_id']
        page_id = self.kwargs['page_id']
        pk = self.kwargs['pk']
        page = get_object_or_404(Page,
                                 pk=page_id,
                                 webpath__pk=webpath_id,
                                 webpath__site__pk=site_id)
        items = PageLocalization.objects.filter(pk=pk, page=page)
        return items

    def patch(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        serializer = self.get_serializer(instance=item,
                                         data=request.data,
                                         partial=True)
        if serializer.is_valid(raise_exception=True):
            page = item.page
            # check permissions on page
            has_permission = page.is_localizable_by(request.user)
            if not has_permission:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        serializer = self.get_serializer(instance=item,
                                         data=request.data)
        if serializer.is_valid(raise_exception=True):
            page = item.page
            # check permissions on page
            has_permission = page.is_localizable_by(request.user)
            if not has_permission:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        page = item.page
        # check permissions on page
        has_permission = page.is_localizable_by(request.user)
        if not has_permission:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().delete(request, *args, **kwargs)


class PageLocalizationFormView(APIView):

    def get(self, *args, **kwargs):
        form = PageLocalizationForm(page_id=kwargs.get('page_id'))
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)
