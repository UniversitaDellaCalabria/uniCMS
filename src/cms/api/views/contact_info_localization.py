from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import get_object_or_404

from cms.contacts.forms import ContactInfoLocalizationForm
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


class ContactInfoLocalizationList(UniCMSListCreateAPIView):
    """
    """
    description = ""
    search_fields = ['language', 'label', 'value']
    permission_classes = [IsAdminUser]
    serializer_class = ContactInfoLocalizationSerializer

    def get_queryset(self):
        """
        """
        contact_id = self.kwargs.get('contact_id')
        contact_info_id = self.kwargs.get('contact_info_id')
        if contact_id and contact_info_id:
            return ContactInfoLocalization.objects.filter(contact_info__contact__pk=contact_id,
                                                          contact_info__pk=contact_info_id)
        return ContactInfoLocalization.objects.none() # pragma: no cover

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # get contact info
            contact_info = serializer.validated_data.get('contact_info')
            # check permissions on contact
            permission = check_user_permission_on_object(request.user,
                                                         contact_info.contact)
            if not permission['granted']:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            return super().post(request, *args, **kwargs)


class ContactInfoLocalizationView(UniCMSCachedRetrieveUpdateDestroyAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = ContactInfoLocalizationSerializer

    def get_queryset(self):
        """
        """
        contact_id = self.kwargs['contact_id']
        contact_info_id = self.kwargs['contact_info_id']
        item_id = self.kwargs['pk']
        items = ContactInfoLocalization.objects\
                                       .select_related('contact_info')\
                                       .filter(pk=item_id,
                                               contact_info__contact__pk=contact_id,
                                               contact_info__pk=contact_info_id)
        return items

    def patch(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        contact_info = item.contact_info
        # check permissions on contact
        permission = check_user_permission_on_object(request.user,
                                                     contact_info.contact)
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        contact_info = item.contact_info
        # check permissions on contact
        permission = check_user_permission_on_object(request.user,
                                                     contact_info.contact)
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        contact_info = item.contact_info
        # check permissions on contact
        permission = check_user_permission_on_object(request.user,
                                                     contact_info.contact)
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().delete(request, *args, **kwargs)


class ContactInfoLocalizationFormView(APIView):

    def get(self, *args, **kwargs):
        form = ContactInfoLocalizationForm(contact_info_id=kwargs.get('contact_info_id'),
                                           contact_id=kwargs.get('contact_id'))
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)


class ContactInfoLocalizationLogsSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'listContactInfoLocalizationLogs'


class ContactInfoLocalizationLogsView(ObjectLogEntriesList):

    schema = ContactInfoLocalizationLogsSchema()

    def get_queryset(self, **kwargs):
        """
        """
        contact_id = self.kwargs['contact_id']
        contact_info_id = self.kwargs['contact_info_id']
        object_id = self.kwargs['pk']
        item = get_object_or_404(ContactInfoLocalization.objects.select_related('contact_info'),
                                 pk=object_id,
                                 contact_info__contact__pk=contact_id,
                                 contact_info__pk=contact_info_id)
        content_type_id = ContentType.objects.get_for_model(item).pk
        return super().get_queryset(object_id, content_type_id)
