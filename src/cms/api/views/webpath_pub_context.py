from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from cms.contexts.forms import EditorialBoardLockUserForm, PublicationContextForm
from cms.contexts.models import WebPath, WebSite

from cms.publications.models import PublicationContext
from cms.publications.serializers import PublicationContextSerializer

from . generics import UniCMSCachedRetrieveUpdateDestroyAPIView, UniCMSListCreateAPIView
from .. exceptions import LoggedPermissionDenied
from .. serializers import UniCMSFormSerializer


class EditorWebpathPublicationContextList(UniCMSListCreateAPIView):
    """
    """
    description = ""
    search_fields = ['publication__name', 'publication__title']
    serializer_class = PublicationContextSerializer

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
            webpath = get_object_or_404(WebPath,
                                        pk=webpath_id,
                                        site=site)
            return PublicationContext.objects.filter(webpath=webpath)
        return PublicationContext.objects.none() # pragma: no cover

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # get webpath
            webpath = serializer.validated_data.get('webpath')
            # check permissions on webpath
            perms = webpath.is_publicable_by(user=request.user)
            if not perms:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            return super().post(request, *args, **kwargs)


class EditorWebpathPublicationContextView(UniCMSCachedRetrieveUpdateDestroyAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = PublicationContextSerializer

    def get_queryset(self):
        """
        """
        site_id = self.kwargs['site_id']
        site = get_object_or_404(WebSite, pk=site_id, is_active=True)
        if not site.is_managed_by(self.request.user):
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=site)
        webpath_id = self.kwargs['webpath_id']
        pk = self.kwargs['pk']
        contexts = PublicationContext.objects\
                                     .select_related('webpath')\
                                     .filter(pk=pk,
                                             webpath__pk=webpath_id,
                                             webpath__site__pk=site_id)
        return contexts

    def patch(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        webpath = item.webpath
        perms = webpath.is_publicable_by(user=request.user)
        if not perms:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        serializer = self.get_serializer(instance=item,
                                         data=request.data,
                                         partial=True)
        if serializer.is_valid(raise_exception=True):
            new_webpath = serializer.validated_data.get('webpath')
            if new_webpath and new_webpath != item.webpath:
                # check permissions and locks on webpath
                webpath_perms = new_webpath.is_publicable_by(user=request.user)
                if not webpath_perms:
                    raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                                 resource=request.method)
        return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        webpath = item.webpath
        perms = webpath.is_publicable_by(user=request.user)
        if not perms:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        serializer = self.get_serializer(instance=item,
                                         data=request.data,
                                         partial=True)
        if serializer.is_valid(raise_exception=True):
            new_webpath = serializer.validated_data.get('webpath')
            if new_webpath and new_webpath != item.webpath:
                # check permissions and locks on webpath
                webpath_perms = new_webpath.is_publicable_by(user=request.user)
                if not webpath_perms:
                    raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                                 resource=request.method)
        return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        webpath = item.webpath
        perms = webpath.is_publicable_by(user=request.user)
        if not perms:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().delete(request, *args, **kwargs)


class PublicationContextFormView(APIView):

    def get(self, *args, **kwargs):
        form = PublicationContextForm(site_id=kwargs.get('site_id'),
                                      webpath_id=kwargs.get('webpath_id'))
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)


class PublicationContextGenericFormView(APIView):

    def get(self, *args, **kwargs):
        form = PublicationContextForm(site_id=kwargs.get('site_id'))
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)


class EditorialBoardLockUserFormView(APIView):

    def get(self, *args, **kwargs):
        form = EditorialBoardLockUserForm()
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)
