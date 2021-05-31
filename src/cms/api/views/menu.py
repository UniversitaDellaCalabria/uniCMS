from django.contrib.contenttypes.models import ContentType
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator

from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.views import APIView

from cms.contexts.decorators import detect_language
from cms.contexts.utils import clone
from cms.menus.forms import MenuForm
from cms.menus.models import NavigationBar
from cms.menus.serializers import MenuSelectOptionsSerializer, MenuSerializer

from . generics import *
from . logs import ObjectLogEntriesList
from .. exceptions import LoggedPermissionDenied, LoggedValidationException
from .. permissions import MenuGetCreatePermissions
from .. serializers import UniCMSFormSerializer
from .. utils import check_user_permission_on_object


@method_decorator(detect_language, name='dispatch')
class ApiMenu(APIView):
    """
    """
    description = 'Get a Menu in JSON format'
    # permission_classes = [permissions.IsAdminUser]

    def get(self, request, menu_id):
        """
        free access
        """
        menu = NavigationBar.objects.filter(is_active=True,
                                            pk=menu_id).first()
        if not menu:
            raise NotFound(detail="Error 404, page not found", code=404)
        lang = getattr(request, 'LANGUAGE_CODE', '')
        res = menu.serialize(lang=lang)
        return Response(res)

    def post(self, request, menu_id=None):
        """
        create a new menu, only for staff users
        """
        if not request.user.is_staff:
            raise PermissionDenied(detail="Error 403, forbidden", code=403)

        childs = request.data.get('childs')

        # post method
        if not menu_id:
            name = request.data['name']
            is_active = request.data['is_active']
            menu = NavigationBar.objects.create(name=name,
                                                is_active=is_active)
        # put method
        else:
            menu = NavigationBar.objects.filter(pk=menu_id).first()
            if not menu:
                raise NotFound(detail="Error 404, menu not found", code=404)
            # remove childs
            for i in menu.get_items():
                i.delete()

        menu.import_childs(childs)

        url = reverse('unicms_api:api-menu', kwargs={'menu_id': menu.pk})
        return HttpResponseRedirect(url)


@method_decorator(detect_language, name='dispatch')
class ApiMenuId(ApiMenu):
    pass


# Editorial board APIs

class MenuList(UniCMSListCreateAPIView):
    """
    """
    description = ""
    search_fields = ['name']
    permission_classes = [MenuGetCreatePermissions]
    serializer_class = MenuSerializer
    queryset = NavigationBar.objects.all()


class MenuView(UniCMSCachedRetrieveUpdateDestroyAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = MenuSerializer

    def get_queryset(self):
        """
        """
        menu_id = self.kwargs['pk']
        menus = NavigationBar.objects.filter(pk=menu_id)
        return menus

    # def get(self, request, pk):
        # """
        # free access
        # """
        # menu = NavigationBar.objects.filter(is_active=True,
        # pk=pk).first()
        # if not menu:
        # raise NotFound(detail="Error 404, page not found", code=404)
        # lang = getattr(request, 'LANGUAGE_CODE', '')
        # res = menu.serialize(lang=lang)
        # return Response(res)

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


class MenuFormView(APIView):

    def get(self, *args, **kwargs):
        form = MenuForm()
        form_fields = UniCMSFormSerializer.serialize(form)
        return Response(form_fields)


class MenuLogsSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'listMenuLogs'


class MenuLogsView(ObjectLogEntriesList):

    schema = MenuLogsSchema()

    def get_queryset(self, **kwargs):
        """
        """
        object_id = self.kwargs['pk']
        item = get_object_or_404(NavigationBar, pk=object_id)
        content_type_id = ContentType.objects.get_for_model(item).pk
        return super().get_queryset(object_id, content_type_id)


class MenuCloneSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'cloneMenu'


class MenuCloneView(APIView):

    schema = MenuCloneSchema()
    description = ""
    permission_classes = [MenuGetCreatePermissions]
    serializer_class = MenuSerializer

    def get_queryset(self):
        """
        """
        menu_id = self.kwargs['pk']
        menus = NavigationBar.objects.filter(pk=menu_id)
        return menus

    def get(self, request, *args, **kwargs):
        item = self.get_queryset().first()
        if not item: raise Http404
        try:
            new_menu = clone(item,
                             excluded_fields=['created', 'modified'],
                             excluded_childrens=['pagemenu'],
                             custom_values={'name': f'{item.name} (copy {timezone.localtime()})'},
                             recursive_custom_values={'created_by': request.user,
                                                      'modified_by': None})
        except Exception as e:
            raise LoggedValidationException(classname=self.__class__.__name__,
                                            resource=request.method,
                                            detail=e)
        result = self.serializer_class(new_menu)
        return Response(result.data)


class EditorialBoardMenuOptionListSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        return 'listMenuSelectOptions'


class MenuOptionList(UniCMSListSelectOptionsAPIView):
    """
    """
    description = ""
    search_fields = ['name']
    serializer_class = MenuSelectOptionsSerializer
    queryset = NavigationBar.objects.all()
    schema = EditorialBoardMenuOptionListSchema()


class MenuOptionView(generics.RetrieveAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = MenuSelectOptionsSerializer

    def get_queryset(self):
        """
        """
        menu_id = self.kwargs['pk']
        menu = NavigationBar.objects.filter(pk=menu_id)
        return menu
