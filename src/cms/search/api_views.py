import logging
import math
import re
import pymongo

from pymongo.errors import ServerSelectionTimeoutError

from django.conf import settings
from django.utils import timezone, dateparse
from django.utils.decorators import method_decorator


from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import APIView

from cms.api.filters import GenericApiFilter
from cms.contexts.decorators import detect_language

from . import MongoClientFactory


logger = logging.getLogger(__name__)


class ServiceUnavailable(APIException): # pragma: no cover
    status_code = 503
    default_detail = 'Service temporarily unavailable, try again later.'
    default_code = 'service_unavailable'


def _handle_date_string(date_string):
    date = dateparse.parse_date(date_string)
    dt = timezone.datetime(date.year, date.month, date.day)
    return timezone.make_aware(dt)


class ApiSearchEngineFilter(GenericApiFilter):
    search_params = [
        {'name': 'categories',
         'description': 'comma separated values',
         'required': False,
         'schema':
             {'type': 'string'},
        },
        {'name': 'year',
         'description': 'Year',
         'required': False,
         'schema':
             {'type': 'integer',
              'format': 'int32'},
        },
        {'name': 'sites',
         'description': 'comma separated values: www.unical.it,dimes.unical.it',
         'required': False,
         'schema':
             {'type': 'string'},
        },
        {'name': 'tags',
         'description': 'comma separated values',
         'required': False,
         'schema':
             {'type': 'string'},
        },
        {'name': 'date_start',
         'description': 'date start YYY-mm-dd',
         'required': False,
         'schema':
             {'type': 'string'},
        },
        {'name': 'date_end',
         'description': 'date end YYY-mm-dd',
         'required': False,
         'schema':
             {'type': 'string'},
        }
    ]


@method_decorator(detect_language, name='dispatch')
class ApiSearchEngine(APIView):
    """
    """
    description = 'Search Engine'
    filter_backends = [ApiSearchEngineFilter,]

    def get(self, request):
        # get collection
        collection = MongoClientFactory().unicms.search

        # get only what's really needed
        search_regexp = re.match(r'^[\w\+\-\s\(\)\[\]\=\"\'\.\_]*',
                                 request.GET.get('search', ''),
                                 re.UNICODE)
        query = {}
        if search_regexp:
            search = search_regexp.group()
            if search:
                query = {"$text": {"$search": search}}

        # year
        year = request.GET.get('year', None)
        if year:
            if isinstance(year, str):
                year = int(year)
            query['year'] = year

        # date range
        date_start = request.GET.get('date_start')
        date_end = request.GET.get('date_end')
        if date_start or date_end:
            query['published'] = {}
        if date_start:
            query['published']["$gte"] = _handle_date_string(date_start)
        if date_end:
            query['published']["$lt"] = _handle_date_string(date_end)

        # tags
        tags = request.GET.get('tags')
        if tags:
            try:
                tags = [i.strip() for i in tags.split(',')]
                query['tags'] = {'$all': tags}
            except ValueError: # pragma: no cover
                logger.debug(f'API Search: Bad tags: {tags}')

        # web site
        sites = request.GET.get('sites')
        if sites:
            try:
                sites = [i.strip() for i in sites.split(',')]
                query['sites'] = {'$all': sites}
            except ValueError: # pragma: no cover
                logger.debug(f'API Search: Bad sites: {sites}')

        # categories
        categories = request.GET.get('categories')
        if categories:
            try:
                categories = [i.strip() for i in categories.split(',')]
                query['categories'] = {'$all': categories}
            except ValueError: # pragma: no cover
                logger.debug(f'API Search: Bad categories: {categories}')

        # run query
        logger.debug('Search query: {}'.format(query))
        try:
            if search:
                res = collection.find(query, {'relevance': {'$meta': "textScore"}}).\
                                 sort([('relevance', {'$meta': 'textScore'})])
            else:
                res = collection.find(query).sort('published',
                                                  pymongo.DESCENDING)
        except ServerSelectionTimeoutError as e: # pragma: no cover
            logger.critical(e)
            raise ServiceUnavailable()

        # pagination
        elements_in_page = getattr(settings, 'SEARCH_ELEMENTS_IN_PAGE', 25)
        total_elements = res.count()
        if total_elements >= elements_in_page:
            total_pages = math.ceil(total_elements / elements_in_page)
        else:
            total_pages = 1

        try:
            page = int(request.GET.get('page_number', 1)) or 1
        except ValueError:
            page = 1
        if page > total_pages:
            page = total_pages

        # get page
        end = elements_in_page * page
        start = end - elements_in_page

        # this commented if should be checked!
        # if total_elements == total_pages:
        # page_number = total_elements
        # else:
        page_number = int(end / elements_in_page)

        entries = res[start:end]
        # dumped = dumps(result)
        data = [{k:v for k,v in entry.items() if k != '_id'}
                for entry in entries]
        result = {"results": data,
                  "count": total_elements,
                  "total_pages": total_pages,
                  "max_per_page": elements_in_page,
                  "page_number": page_number
        }
        return Response(result)
