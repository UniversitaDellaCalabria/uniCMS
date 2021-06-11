import math
import re

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class UniCmsApiPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 250

    def url_refactor(self, url):
        pattern = re.compile(r"https?://")
        return pattern.sub('//', url) if url else None

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next':  self.url_refactor(self.get_next_link()),
            'previous': self.url_refactor(self.get_previous_link()),
            'page': int(self.request.query_params.get('page', 1)),
            'per_page': self.page_size,
            'total_pages': math.ceil(self.page.paginator.count / self.page_size),
            'results': data,
        })


class UniCmsSelectOptionsApiPagination(UniCmsApiPagination):
    page_size = 50
