from types import SimpleNamespace
from unittest import mock

from django.test import RequestFactory, TestCase

from cms.pages import tests as pages_tests
from cms.pages.models import PageBlock, PageMedia, PagePublication
from cms.publications.models import Publication

from . import blocks
from . import placeholders
from . models import TemplateBlock
from . utils import import_string_block


BLOCKS_PREFIX = 'cms.templates.blocks.'


class PlaceholdersTest(TestCase):

    def setUp(self):
        # no search engine updates on pages/publications save
        patcher = mock.patch('cms.search.hooks.mongo_collection')
        patcher.start()
        self.addCleanup(patcher.stop)

        # capture the data passed to the templates
        self.rendered = []

        def fake_render(template, data, name=''):
            self.rendered.append((template, data, name))
            return f'rendered {name}'

        patcher = mock.patch.object(placeholders, 'handle_faulty_templates',
                                    side_effect=fake_render)
        patcher.start()
        self.addCleanup(patcher.stop)

        self.page = pages_tests.PageUnitTest.create_page()
        self.request = RequestFactory().get('/')
        self.request.LANGUAGE_CODE = 'en'

    def add_block(self, block_type, content='{"template": "test.html"}',
                  section='1-top-a'):
        block = TemplateBlock.objects.create(name=block_type,
                                             type=f'{BLOCKS_PREFIX}{block_type}',
                                             content=content,
                                             is_active=True)
        PageBlock.objects.create(page=self.page, block=block,
                                 section=section, is_active=True)
        return block

    def render_blocks(self, block_type):
        page_blocks = self.page.get_blocks()
        results = []
        for block in page_blocks:
            if block.type != f'{BLOCKS_PREFIX}{block_type}':
                continue
            obj = import_string_block(block=block, request=self.request,
                                      page=self.page,
                                      webpath=self.page.webpath,
                                      blocks=page_blocks)
            results.append(obj.render())
        return results

    def test_carousel(self):
        self.add_block('CarouselPlaceholderBlock')
        # a second placeholder without carousels left to render
        self.add_block('CarouselPlaceholderBlock')
        page_carousel = self.page.get_carousels()[0]

        results = self.render_blocks('CarouselPlaceholderBlock')
        self.assertEqual(results, ['rendered CarouselPlaceHolder', None])
        self.assertEqual(len(self.rendered), 1)
        template, data, name = self.rendered[0]
        self.assertEqual(template, 'test.html')
        self.assertEqual(data['uid'], f'id_{page_carousel.pk}')
        self.assertEqual(data['request'], self.request)
        self.assertEqual(list(data['carousel_items']),
                         list(page_carousel.carousel.get_items('en')))
        self.assertTrue(data['carousel_items'])

    def test_contact(self):
        self.add_block('ContactPlaceholderBlock')
        page_contact = self.page.get_contacts()[0]
        self.assertEqual(self.render_blocks('ContactPlaceholderBlock'),
                         ['rendered ContactPlaceHolder'])
        data = self.rendered[0][1]
        self.assertEqual(data['uid'], f'id_{page_contact.pk}')
        self.assertEqual(data['contact'], page_contact.contact)
        self.assertEqual(list(data['contact_infos']),
                         list(page_contact.contact.get_infos('en')))

    def test_heading(self):
        self.add_block('HeadingPlaceholderBlock')
        self.assertEqual(self.render_blocks('HeadingPlaceholderBlock'),
                         ['rendered HeadingPlaceholder'])
        data = self.rendered[0][1]
        # translated heading
        self.assertEqual(data['heading'].title, 'page heading en')
        self.assertEqual(data['webpath'], self.page.webpath)

    def test_link(self):
        self.add_block('LinkPlaceholderBlock')
        self.assertEqual(self.render_blocks('LinkPlaceholderBlock'),
                         ['rendered LinkPlaceHolder'])
        data = self.rendered[0][1]
        self.assertEqual(data['name'], 'page link')
        self.assertEqual(data['url'], 'https://example.org')

    def test_media_collection(self):
        self.add_block('MediaCollectionPlaceholderBlock')
        page_collection = self.page.get_media_collections()[0]
        self.assertEqual(self.render_blocks('MediaCollectionPlaceholderBlock'),
                         ['rendered MediaCollectionPlaceHolder'])
        self.assertEqual(self.rendered[0][1]['collection'],
                         page_collection.collection)

    def test_media(self):
        self.add_block('MediaPlaceholderBlock')
        # reuse the media of the page media collection
        collection = self.page.get_media_collections()[0].collection
        media = collection.mediacollectionitem_set.first().media
        PageMedia.objects.create(page=self.page, media=media,
                                 url='https://example.org/media',
                                 is_active=True)
        self.assertEqual(self.render_blocks('MediaPlaceholderBlock'),
                         ['rendered MediaPlaceHolder'])
        data = self.rendered[0][1]
        self.assertEqual(data['media'], media)
        self.assertEqual(data['url'], 'https://example.org/media')

    def test_menu(self):
        self.add_block('MenuPlaceholderBlock')
        page_menu = self.page.get_menus()[0]
        self.assertEqual(self.render_blocks('MenuPlaceholderBlock'),
                         ['rendered MenuPlaceHolder'])
        data = self.rendered[0][1]
        self.assertEqual(data['page'], self.page)
        self.assertEqual(list(data['items']),
                         list(page_menu.menu.get_items(lang='en',
                                                       parent__isnull=True)))

    def test_publication(self):
        self.add_block('PublicationContentPlaceholderBlock')
        publication = Publication.objects.create(name='pub', title='pub title',
                                                 content='content',
                                                 is_active=True)
        page_pub = PagePublication.objects.create(page=self.page,
                                                  publication=publication,
                                                  is_active=True)
        self.assertEqual(self.render_blocks('PublicationContentPlaceholderBlock'),
                         ['rendered PublicationPlaceHolder'])
        data = self.rendered[0][1]
        self.assertEqual(data['uid'], f'id_{publication.pk}')
        self.assertEqual(data['publication'], publication)
        self.assertEqual(data['page_publication'], page_pub)
        self.assertEqual(data['webpath'], self.page.webpath)

    def test_without_template(self):
        self.add_block('LinkPlaceholderBlock', content='{}')
        self.render_blocks('LinkPlaceholderBlock')
        self.assertEqual(self.rendered[0][0], '')

    def test_not_runnable(self):
        context = {'request': self.request, 'page': self.page,
                   'webpath': self.page.webpath, 'blocks': []}
        content = {'template': 'test.html'}

        # without a block
        with self.assertLogs('cms.templates.placeholders', level='WARNING'):
            self.assertEqual(placeholders.load_link_placeholder(context=context,
                                                                content=content),
                             '')

        # without entries in the page
        context['block'] = 'block'
        self.assertEqual(placeholders.load_media_placeholder(context=context,
                                                             content=content),
                         '')
        self.assertEqual(placeholders.load_publication_content_placeholder(
            context=context, content=content), '')

        # with entries but without placeholder blocks
        with self.assertLogs('cms.templates.placeholders', level='WARNING'):
            self.assertEqual(placeholders.load_link_placeholder(context=context,
                                                                content=content),
                             '')
        self.assertEqual(self.rendered, [])

    def test_placeholder_properties(self):
        context = {'request': self.request, 'page': self.page,
                   'webpath': self.page.webpath, 'blocks': []}
        ph = placeholders.LinkPlaceHolder(context, {'template': 't.html'})
        self.assertEqual(ph.iam, 'LinkPlaceHolder')
        self.assertEqual(ph.log_msg, 'Template Tag LinkPlaceHolder')
        self.assertEqual(ph.language, 'en')
        self.assertIsNone(ph.hook())
        self.assertIsNone(ph.block)


class BlocksTest(TestCase):

    def setUp(self):
        self.request = RequestFactory().get('/')
        self.page = SimpleNamespace(title='the title',
                                    get_blocks=lambda: ['page blocks'])

    def test_abstract_block(self):
        block = blocks.AbstractBlock(content='<b>bold</b>',
                                     request=self.request,
                                     page=self.page, webpath='webpath')
        self.assertFalse(block._rendered)
        self.assertEqual(block.render(), '<b>bold</b>')

        # page blocks are used if blocks are missing
        context = block.get_context()
        self.assertEqual(context['blocks'], ['page blocks'])
        self.assertEqual(context['block'], block)
        self.assertEqual(context['webpath'], 'webpath')

        block.blocks = ['blocks']
        self.assertEqual(block.get_context()['blocks'], ['blocks'])

    def test_html_block(self):
        block = blocks.HtmlBlock(content='{{ page.title }} {{ webpath }}',
                                 request=self.request, page=self.page,
                                 webpath='/path/', blocks=[])
        self.assertEqual(block.render(), 'the title /path/')

    def test_json_block(self):
        self.assertEqual(blocks.JSONBlock().content, {})
        block = blocks.JSONBlock(content='{"a": 1}', page=self.page)
        self.assertEqual(block.content, {'a': 1})

    def test_placeholder_block_sanitize_template(self):
        block = blocks.PlaceHolderBlock(content='{"a": 1}')
        block.sanitize_template()
        self.assertEqual(block.content, {'a': 1, 'template': ''})

        block = blocks.PlaceHolderBlock(content='{"template": "t.html"}')
        block.sanitize_template()
        self.assertEqual(block.content['template'], 't.html')
