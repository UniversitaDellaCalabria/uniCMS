from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import get_object_or_404

from cms.menus.forms import MenuItemForm
from cms.menus.models import *
from cms.menus.serializers import *

from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.views import APIView

from . generics import *
from . logs import ObjectLogEntriesList
from .. exceptions import LoggedPermissionDenied
from .. serializers import UniCMSFormSerializer
from .. utils import check_user_permission_on_object


class MenuItemList(UniCMSListCreateAPIView):
    """
    """
    description = ""
    search_fields = ['name', 'webpath', 'url', 'parent', 'publication']
    serializer_class = MenuItemSerializer

    def get_queryset(self): # pragma: no cover
        pass
    # def get_queryset(self):
        # """
        # """
        # menu_id = self.kwargs.get('menu_id')
        # if menu_id:
        # return NavigationBarItem.objects.filter(menu__pk=menu_id)
        # return NavigationBarItem.objects.none()

    def get(self, request, *args, **kwargs):
        """
        tree view
        """
        menu_id = kwargs['menu_id']
        menu = get_object_or_404(NavigationBar, pk=menu_id)
        res = menu.serialize(only_active=False)
        return Response(res)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # get menu
            menu = serializer.validated_data.get('menu')
            # check permissions on menu
            permission = check_user_permission_on_object(request.user,
                                                         menu)
            if not permission['granted']:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)

            try:
                return super().post(request, *args, **kwargs)
            except Exception as e: # pragma: no cover
                raise ValidationError(e)


class MenuItemView(UniCMSCachedRetrieveUpdateDestroyAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = MenuItemSerializer

    def get_queryset(self):
        """
        """
        menu_id = self.kwargs['menu_id']
        item_id = self.kwargs['pk']
        items = NavigationBarItem.objects\
                                 .select_related('menu')\
                                 .filter(pk=item_id,
                                         menu__pk=menu_id)
        return items

    def patch(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        menu = item.menu
        permission = check_user_permission_on_object(request.user,
                                                     menu)
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        serializer = self.get_serializer(instance=item,
                                         data=request.data,
                                         partial=True)
        if serializer.is_valid(raise_exception=True):
            new_menu = serializer.validated_data.get('menu')
            # check permissions on menu
            if new_menu:
                permission = check_user_permission_on_object(request.user,
                                                             new_menu)
                if not permission['granted']:
                    raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                                 resource=request.method)
            try:
                return super().patch(request, *args, **kwargs)
            except Exception as e:
                raise ValidationError(e)

    def put(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        menu = item.menu
        permission = check_user_permission_on_object(request.user,
                                                     menu)
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        serializer = self.get_serializer(instance=item,
                                         data=request.data)
        if serializer.is_valid(raise_exception=True):
            # get menu
            new_menu = serializer.validated_data.get('menu')
            # check permissions on menu
            permission = check_user_permission_on_object(request.user,
                                                         new_menu)
            if not permission['granted']:
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            try:
                return super().put(request, *args, **kwargs)
            except Exception as e: # pragma: no cover
                raise ValidationError(e)

    def delete(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        # get menu
        menu = item.menu
        # check permissions on menu
        permission = check_user_permission_on_object(request.user,
                                                     menu)
        if not permission['granted']:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().delete(request, *args, **kwargs)


class MenuItemFormView(APIView):

    def get(self, *args, **kwargs):
        form = MenuItemForm(menu_id=kwargs.get('menu_id'))
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)


class MenuItemLogsSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'listMenuItemLogs'


class MenuItemLogsView(ObjectLogEntriesList):

    schema = MenuItemLogsSchema()

    def get_queryset(self, **kwargs):
        """
        """
        menu_id = self.kwargs['menu_id']
        object_id = self.kwargs['pk']
        item = get_object_or_404(NavigationBarItem.objects.select_related('menu'),
                                 pk=object_id,
                                 menu__pk=menu_id)
        content_type_id = ContentType.objects.get_for_model(item).pk
        return super().get_queryset(object_id, content_type_id)
