import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.utils import timezone

from cms.carousels.tests import CarouselUnitTest
from cms.contexts.tests import ContextUnitTest
from cms.menus.tests import MenuUnitTest
from cms.templates.tests import TemplateUnitTest

from cms.carousels.tests import CarouselUnitTest
from cms.contexts.tests import ContextUnitTest
from cms.medias.tests import MediaUnitTest
from cms.menus.tests import MenuUnitTest
from cms.pages.tests import PageUnitTest
from cms.templates.tests import TemplateUnitTest

from . models import *


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PublicationUnitTest(TestCase):

    def setUp(self):
        pass


    @classmethod
    def create_pub(cls, **kwargs):
        data = {'is_active': 1,
                'title':'Papiri, Codex, Libri. La attraverso labora lorem ipsum',
                'subheading':'Itaque earum rerum hic tenetur a sapiente delectus',
                'content':'<p>Sed ut perspiciatis unde omnis iste natus error </p>',
                'content_type': 'html',
                'presentation_image': MediaUnitTest.create_media(),
                'state':'published',
                'date_start': timezone.localtime(),
                'date_end': timezone.localtime() + timezone.timedelta(hours=1),
                'note':'',
                'relevance':'0',
        }
        for k,v in kwargs.items():
            data[k] = v

        obj = Publication.objects.create(**data)
        obj.__str__()
        obj.tags.add('ciao')
        
        obj.category.add(PageUnitTest.create_category())
        
        ploc = PublicationLocalization.objects.create(publication=obj,
                                                      language='en',
                                                      title='pub eng',
                                                      subheading='',
                                                      content='',
                                                      is_active=1)
        ploc.__str__()
        
        return obj

    
    @classmethod
    def test_pub(cls):
        pub = cls.create_pub()
        
        pub.categories
        pub.serialize()
        
        pub.active_translations()
        pub.image_url()
        
        # related pub
        pubrel = PublicationRelated.objects.create(publication=pub,
                                                   related=pub,
                                                   is_active=1)
        pubrel.__str__()
        pub.related_publications
        
        # PublicationContext - related webpath
        webpath = ContextUnitTest.create_webpath()
        pubcont = PublicationContext.objects.create(publication=pub,
                                                    webpath=webpath,
                                                    is_active=1)
        pubcont.get_url_list(category_name='main')
        pubcont.name
        pubcont.path_prefix
        pubcont.url
        pubcont.name
        pubcont.translate_as('en')
        pubcont.serialize()
        pubcont.__str__()
        # end PubblicationContext
        
        pub.related_contexts
        pub.first_available_url
        
        # pub links
        publink = PublicationLink.objects.create(publication=pub,
                                                 name='that name',
                                                 url='https://example.org')
        publink.__str__()
        pub.related_links
        
        # pub gallery
        media_col = MediaUnitTest.create_media_collection()
        
        pubga = PublicationGallery.objects.create(publication = pub,
                                                  collection = media_col,
                                                  is_active=1)
        pubga.__str__()
        pub.related_galleries
        
        # pub loc
        pub.translate_as(lang='en')
        pub.available_in_languages
        
        # test slug pre pop
        pub.save()
        
        # pub attachments
        data = {'publication': pub,
                'file': f'{settings.MEDIA_ROOT}/images/categories/eventi.jpg',
                'description': 'blah blah',
                'is_active': 1
        }
        pubatt = PublicationAttachment.objects.create(**data)
        pubatt.__str__()
        pub.get_attachments()
        
        # pub context felix's
        pub.url(webpath=webpath)
        pub.get_url_list(webpath=webpath)
        pub.get_publication_context(webpath=webpath)
        
        # PublicationBlock
        pubblock = PublicationBlock.objects.create(
                        block = TemplateUnitTest.create_block_template(),
                        publication = pub,
                        is_active = True
        )
        pubblock.__str__()
        
        
        
        
