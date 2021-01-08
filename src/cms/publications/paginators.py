import math
from copy import deepcopy as copy

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from . import settings as app_settings

CMS_PAGE_SIZE = getattr(settings, 'CMS_PAGE_SIZE',
                        app_settings.CMS_PAGE_SIZE)


class Page(object):
    schema = {'results': [],
              'total': 0,
              'total_pages': 0,
              'count': 0,
              'page_number': 1,

              'current_url': None,
              'next_url': None,
              'previous_url': None,
    }

    def __init__(self, queryset, request=None, **kwargs):
        for k,v in copy(self.schema).items():
            setattr(self, k, v)

        for k,v in kwargs.items():
            setattr(self, k, v)

        self.queryset = queryset
        self.request = request

        if self.request:
            self.build_urls()

    def build_urls(self):
        self.current_url = self.request.get_full_path()
        if self.request.GET.get('page_number'):
            page_number = int(self.request.GET['page_number'][0])
            if page_number > 1:
                prev_num = self.page_number - 1
                self.previous_url = self.current_url.replace(f'page_number={self.page_number}',
                                                             f'page_number={prev_num}',)
        if self.page_number < self.total_pages:
            next_num = self.page_number + 1
            self.next_url = self.current_url.replace(f'page_number={self.page_number}',
                                                     f'page_number={next_num}',)

    def has_next(self):
        return self.next_url

    def has_previous(self):
        return self.previous_url

    def has_other_pages(self):
        raise NotImplementedError()

    def next_page_number(self):
        if self.has_next():
            return self.page_number + 1

    def previous_page_number(self):
        if self.has_previous():
            return self.page_number - 1

    def serialize(self):
        for i in self.queryset:
            if self.request:
                # i18n
                if hasattr(i, 'translate_as'):
                    i.translate_as(lang=self.request.LANGUAGE_CODE)

            if hasattr(i, 'serialize'):
                self.results.append(i.serialize())
            else:
                self.results.append(i)
            self.count += 1
        return {k:getattr(self, k) for k in self.schema.keys()}


class Paginator(object):
    schema = {'count': 0,
              'num_pages': 0,
    }

    def __init__(self, queryset, request=None, **kwargs):
        for k,v in copy(self.schema).items():
            setattr(self, k, v)

        for k,v in kwargs.items():
            setattr(self, k, v)

        self.queryset = queryset
        self.request = request
        self.count = queryset.count()
        self.num_pages = 0
        self.paginate()

    def paginate(self):
        if self.count >= CMS_PAGE_SIZE:
            self.num_pages = math.ceil(self.count / CMS_PAGE_SIZE)
        elif self.count:
            self.num_pages = 1

    def get_page(self, num):
        if num > self.num_pages:
            raise ObjectDoesNotExist('Page number out of bound')
        elif num < 1:
            raise ValidationError('Wrong page_number value')
        end = CMS_PAGE_SIZE * num
        start = end - CMS_PAGE_SIZE
        if num == self.num_pages:
            page_number = num
        else:
            page_number = int(end / CMS_PAGE_SIZE)

        return Page(queryset=self.queryset[start:end],
                    total=self.count,
                    total_pages=self.num_pages,
                    page_number=page_number,
                    request=self.request)
