from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator

from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from cms.contexts.decorators import detect_language

from . models import NavigationBar


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
