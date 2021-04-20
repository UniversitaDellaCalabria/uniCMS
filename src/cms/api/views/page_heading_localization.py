from django.shortcuts import get_object_or_404

from cms.pages.forms import PageHeadingLocalizationForm
from cms.pages.models import *
from cms.pages.serializers import *

from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from . generics import UniCMSCachedRetrieveUpdateDestroyAPIView, UniCMSListCreateAPIView
from .. exceptions import LoggedPermissionDenied
from .. serializers import UniCMSFormSerializer


class PageHeadingLocalizationList(UniCMSListCreateAPIView):
    """
    """
    description = ""
    search_fields = ['language', 'title', 'description']
    serializer_class = PageHeadingLocalizationSerializer

    def get_queryset(self):
        """
        """
        site_id = self.kwargs.get('site_id')
        webpath_id = self.kwargs.get('webpath_id')
        page_id = self.kwargs.get('page_id')
        heading_id = self.kwargs.get('heading_id')

        if site_id and webpath_id:
            site = get_object_or_404(WebSite, pk=site_id, is_active=True)
            if not site.is_managed_by(self.request.user):
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=site)
            page = get_object_or_404(Page,
                                     pk=page_id,
                                     webpath__pk=webpath_id,
                                     webpath__site__pk=site_id)
            heading = get_object_or_404(PageHeading, page=page, pk=heading_id)
            return PageHeadingLocalization.objects.filter(heading=heading)
        return PageHeadingLocalization.objects.none() # pragma: no cover

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # get page
            page = serializer.validated_data.get('heading').page
            # check permissions on page
            has_permission = page.is_editable_by(request.user)
            if not has_permission:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            return super().post(request, *args, **kwargs)


class PageHeadingLocalizationView(UniCMSCachedRetrieveUpdateDestroyAPIView):
    """
    """
    description = ""
    serializer_class = PageHeadingLocalizationSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        """
        """
        site_id = self.kwargs.get('site_id')
        webpath_id = self.kwargs.get('webpath_id')
        page_id = self.kwargs.get('page_id')
        heading_id = self.kwargs.get('heading_id')
        pk = self.kwargs.get('pk')

        site = get_object_or_404(WebSite, pk=site_id, is_active=True)
        if not site.is_managed_by(self.request.user):
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=site)
        page = get_object_or_404(Page,
                                 pk=page_id,
                                 webpath__pk=webpath_id,
                                 webpath__site__pk=site_id)
        heading = get_object_or_404(PageHeading, page=page, pk=heading_id)
        items = PageHeadingLocalization.objects.filter(pk=pk, heading=heading)
        return items


    def patch(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        page = item.heading.page
        # check permissions on page
        has_permission = page.is_editable_by(request.user)
        if not has_permission:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        page = item.heading.page
        # check permissions on page
        has_permission = page.is_editable_by(request.user)
        if not has_permission:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        page = item.heading.page
        # check permissions on page
        has_permission = page.is_editable_by(request.user)
        if not has_permission:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().delete(request, *args, **kwargs)


class PageHeadingLocalizationFormView(APIView):

    def get(self, *args, **kwargs):
        form = PageHeadingLocalizationForm(page_id=kwargs.get('page_id'),
                                           heading_id=kwargs.get('heading_id'))
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)
