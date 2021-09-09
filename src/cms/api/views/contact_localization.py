from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import get_object_or_404

from cms.contacts.forms import ContactLocalizationForm
from cms.contacts.models import *
from cms.contacts.serializers import *

from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.views import APIView

from . generics import *
from . logs import ObjectLogEntriesList
from .. exceptions import LoggedPermissionDenied
from .. serializers import UniCMSFormSerializer
from .. utils import check_user_permission_on_object


class ContactLocalizationList(UniCMSListCreateAPIView):
    """
    """
    description = ""
    search_fields = ['language', 'name', 'description']
    permission_classes = [IsAdminUser]
    serializer_class = ContactLocalizationSerializer

    def get_queryset(self):
        """
        """
        contact_id = self.kwargs.get('contact_id')
        if contact_id:
            return ContactLocalization.objects.filter(contact__pk=contact_id)
        return ContactLocalization.objects.none() # pragma: no cover

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # get contact
            contact = serializer.validated_data.get('contact')
            # check permissions on contact
            permission = check_user_permission_on_object(request.user,
                                                         contact)
            if not permission['granted']:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            return super().post(request, *args, **kwargs)


class ContactLocalizationView(UniCMSCachedRetrieveUpdateDestroyAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = ContactLocalizationSerializer

    def get_queryset(self):
        """
        """
        contact_id = self.kwargs['contact_id']
        item_id = self.kwargs['pk']
        items = ContactLocalization.objects\
                                   .select_related('contact')\
                                   .filter(pk=item_id,
                                           contact__pk=contact_id)
        return items

    def patch(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        contact = item.contact
        # check permissions on contact
        permission = check_user_permission_on_object(request.user,
                                                     contact)
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        contact = item.contact
        # check permissions on contact
        permission = check_user_permission_on_object(request.user,
                                                     contact)
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        contact = item.contact
        # check permissions on contact
        permission = check_user_permission_on_object(request.user,
                                                     contact)
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().delete(request, *args, **kwargs)


class ContactLocalizationFormView(APIView):

    def get(self, *args, **kwargs):
        form = ContactLocalizationForm(contact_id=kwargs.get('contact_id'))
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)


class ContactLocalizationLogsSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'listContactLocalizationLogs'


class ContactLocalizationLogsView(ObjectLogEntriesList):

    schema = ContactLocalizationLogsSchema()

    def get_queryset(self, **kwargs):
        """
        """
        contact_id = self.kwargs['contact_id']
        object_id = self.kwargs['pk']
        item = get_object_or_404(ContactLocalization.objects.select_related('contact'),
                                 pk=object_id,
                                 contact__pk=contact_id)
        content_type_id = ContentType.objects.get_for_model(item).pk
        return super().get_queryset(object_id, content_type_id)
