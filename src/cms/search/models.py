from django.conf import settings
from django.utils import timezone

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

DEFAULT_LANGUAGE = dict(settings.LANGUAGES)[settings.LANGUAGE].lower()


class SearchTranslationEntry(BaseModel):
    language : str
    title : str
    subheading : Optional[str]
    content : Optional[str]


class SearchEntry(BaseModel):
    title : str
    heading : str
    content_type : str
    content_id : str
    image : Optional[str]
    content : Optional[str]
    sites : List[str]
    urls : List[str]
    tags : Optional[list]
    categories : Optional[list] = []
    indexed : datetime
    published : datetime
    viewed : Optional[int]
    relevance : Optional[int]
    language : str
    translations : List[SearchTranslationEntry] = None
    day : int
    month : int
    year : int


def page_to_entry(page_object):
    app_label, model = page_object._meta.label_lower.split('.')
    sites = [page_object.webpath.site.domain]
    data = {
        "title": page_object.name,
        "heading": page_object.description,
        "content_type": page_object._meta.label,
        "content_id": page_object.pk,
        "content": "",
        "sites": sites,
        "urls": [f'{sites[0]}{page_object.webpath.get_full_path()}',],
        "categories": [page_object.get_type_display()],
        "tags": [i for i in page_object.tags.values_list('name', flat=1)],
        "indexed": timezone.localtime(),
        "published": page_object.date_start,
        "viewed": 0,
        "language": DEFAULT_LANGUAGE,
        "day": page_object.date_start.day,
        "month": page_object.date_start.month,
        "year": page_object.date_start.year
    }
    search_entry = SearchEntry(**data)
    return search_entry.dict()


def publication_to_entry(pub_object, contexts=None):
    app_label, model = pub_object._meta.label_lower.split('.')
    # contexts = pub_object.publicationcontext_set.filter(is_active=True).\
    # order_by('date_start')
    if not contexts:
        # it doesn't have any real publication
        return
    first_context = contexts.first()
    urls = set([f'//{i.webpath.site.domain}{i.url}' for i in contexts])
    sites = set([f'{i.webpath.site.domain}' for i in contexts])
    data = {
        "title": pub_object.title,
        "heading": pub_object.subheading,
        "content_type": pub_object._meta.label,
        "image": pub_object.image_url(),
        "content_id": pub_object.pk,
        "content": pub_object.content,
        "sites": list(sites),
        "urls": list(urls),
        "categories": [i.name for i in pub_object.categories.all()],
        "tags": [i for i in pub_object.tags.values_list('name', flat=1)],
        "translations": [{'language': i[1].lower(),
                          'title': i[0].title,
                          'subheading': i[0].subheading,
                          'content': i[0].content
                         }
                         for i in pub_object.available_in_languages],
        "indexed": timezone.localtime(),
        "published": first_context.date_start,
        "viewed": 0,
        "language": DEFAULT_LANGUAGE,
        "day": first_context.date_start.day,
        "month": first_context.date_start.month,
        "year": first_context.date_start.year
    }
    search_entry = SearchEntry(**data)
    return search_entry.dict()
