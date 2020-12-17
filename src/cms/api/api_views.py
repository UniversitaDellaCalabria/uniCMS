import time # debug wait

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.decorators import method_decorator

from rest_framework import generics, viewsets, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from cms.contexts.decorators import detect_language
from cms.contexts.models import WebPath

from cms.publications.models import Publication, PublicationContext
from cms.publications.paginators import Paginator
from cms.api.serializers import *
from cms.publications.utils import publication_context_base_filter


class PublicationDetail(generics.RetrieveAPIView):
    name = 'publication-detail'
    description = 'News'
    queryset = Publication.objects.filter(is_active=True)
    serializer_class = PublicationSerializer
    lookup_field = 'slug'


@method_decorator(detect_language, name='dispatch')
class ApiPublicationsByContext(APIView):
    """
    """
    description = 'ApiPublicationsByContext'
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAdminUser]
    
    def get(self, request, webpath_id, category_name=None):
        query_params = publication_context_base_filter()
        query_params.update({'webpath__pk': webpath_id})
        
        category_name = category_name or request.GET.get('category_name')
        if category_name:
            query_params['publication__category__name__iexact'] = category_name
        pubcontx = PublicationContext.objects.filter(**query_params)
        count = pubcontx.count()
        paginator = Paginator(queryset=pubcontx, request=request)
        
        try:
            page_num = int(request.GET.get('page_number', 1))
        except:
            raise ValidationError('Wrong page_number value')

        paged = paginator.get_page(page_num)
        result = paged.serialize()
        return Response(result)



@method_decorator(detect_language, name='dispatch')
class ApiContext(APIView):
    """
    """
    description = 'Get publications in Context (WebPath)'
    
    def get(self, request):
        webpaths = WebPath.objects.filter(is_active=True)
        pubs = ({i.pk: f'{i.site.domain}{i.get_full_path()}'} for i in webpaths)
        return Response(pubs)
    
