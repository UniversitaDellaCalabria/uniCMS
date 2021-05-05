from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import get_object_or_404

from cms.menus.forms import MenuItemLocalizationForm
from cms.menus.models import *
from cms.menus.serializers import *

from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.views import APIView

from . generics import *
from . logs import ObjectLogEntriesList
from .. exceptions import LoggedPermissionDenied
from .. serializers import UniCMSFormSerializer
from .. utils import check_user_permission_on_object


class MenuItemLocalizationList(UniCMSListCreateAPIView):
    """
    """
    description = ""
    search_fields = ['language', 'name']
    permission_classes = [IsAdminUser]
    serializer_class = MenuItemLocalizationSerializer

    def get_queryset(self):
        """
        """
        menu_id = self.kwargs.get('menu_id')
        menu_item_id = self.kwargs.get('menu_item_id')
        if menu_id and menu_item_id:
            return NavigationBarItemLocalization.objects.filter(item__menu__pk=menu_id,
                                                                item__pk=menu_item_id)
        return NavigationBarItemLocalization.objects.none() # pragma: no cover

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # get menu item
            menu_item = serializer.validated_data.get('item')
            # check permissions on carousel
            permission = check_user_permission_on_object(request.user,
                                                         menu_item.menu)
            if not permission['granted']:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            return super().post(request, *args, **kwargs)


class MenuItemLocalizationView(UniCMSCachedRetrieveUpdateDestroyAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = MenuItemLocalizationSerializer

    def get_queryset(self):
        """
        """
        menu_id = self.kwargs['menu_id']
        menu_item_id = self.kwargs['menu_item_id']
        item_id = self.kwargs['pk']
        items = NavigationBarItemLocalization.objects\
                                        .select_related('item')\
                                        .filter(pk=item_id,
                                                item__menu__pk=menu_id,
                                                item__pk=menu_item_id)
        return items

    def patch(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        menu_item = item.item
        # check permissions on menu
        permission = check_user_permission_on_object(request.user,
                                                     menu_item.menu)
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        menu_item = item.item
        # check permissions on menu
        permission = check_user_permission_on_object(request.user,
                                                     menu_item.menu)
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        menu_item = item.item
        # check permissions on menu
        permission = check_user_permission_on_object(request.user,
                                                     menu_item.menu)
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().delete(request, *args, **kwargs)


class MenuItemLocalizationFormView(APIView):

    def get(self, *args, **kwargs):
        form = MenuItemLocalizationForm(menu_item_id=kwargs.get('menu_item_id'),
                                        menu_id=kwargs.get('menu_id'))
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)


class MenuItemLocalizationLogsSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'listMenuItemLocalizationLogs'


class MenuItemLocalizationLogsView(ObjectLogEntriesList):

    schema = MenuItemLocalizationLogsSchema()

    def get_queryset(self, **kwargs):
        """
        """
        menu_id = self.kwargs['menu_id']
        menu_item_id = self.kwargs['menu_item_id']
        object_id = self.kwargs['pk']
        item = get_object_or_404(NavigationBarItemLocalization.objects.select_related('item'),
                                 pk=object_id,
                                 item__menu__pk=menu_id,
                                 item__pk=menu_item_id)
        content_type_id = ContentType.objects.get_for_model(item).pk
        return super().get_queryset(object_id, content_type_id)
