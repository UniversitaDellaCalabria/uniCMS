from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import get_object_or_404

from cms.contacts.forms import ContactForm
from cms.contacts.models import *
from cms.contacts.serializers import *

from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.views import APIView

from . generics import *
from . logs import ObjectLogEntriesList
from .. exceptions import LoggedPermissionDenied
from .. permissions import ContactGetCreatePermissions
from .. serializers import UniCMSFormSerializer
from .. utils import check_user_permission_on_object


class ContactList(UniCMSListCreateAPIView):
    """
    """
    description = ""
    search_fields = ['name', 'description']
    permission_classes = [ContactGetCreatePermissions]
    filterset_fields = ['created', 'modified', 'created_by', 'contact_type']
    serializer_class = ContactSerializer
    queryset = Contact.objects.all()


class ContactView(UniCMSCachedRetrieveUpdateDestroyAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = ContactSerializer

    def get_queryset(self):
        """
        """
        contact_id = self.kwargs['pk']
        contacts = Contact.objects.filter(pk=contact_id)
        return contacts

    def patch(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        permission = check_user_permission_on_object(request.user,
                                                     item)
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        permission = check_user_permission_on_object(request.user,
                                                     item)
        if not permission['granted']:
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


class ContactFormView(APIView):

    def get(self, *args, **kwargs):
        form = ContactForm()
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)


class ContactLogsSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'listContactLogs'


class ContactLogsView(ObjectLogEntriesList):

    schema = ContactLogsSchema()

    def get_queryset(self, **kwargs):
        """
        """
        object_id = self.kwargs['pk']
        item = get_object_or_404(Contact, pk=object_id)
        content_type_id = ContentType.objects.get_for_model(item).pk
        return super().get_queryset(object_id, content_type_id)


class EditorialBoardContactOptionListSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'listContactSelectOptions'


class ContactOptionList(UniCMSListSelectOptionsAPIView):
    """
    """
    description = ""
    search_fields = ['name']
    serializer_class = ContactSelectOptionsSerializer
    queryset = Contact.objects.all()
    schema = EditorialBoardContactOptionListSchema()


class ContactOptionView(generics.RetrieveAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = ContactSelectOptionsSerializer

    def get_queryset(self):
        """
        """
        contact_id = self.kwargs['pk']
        contact = Contact.objects.filter(pk=contact_id)
        return contact
