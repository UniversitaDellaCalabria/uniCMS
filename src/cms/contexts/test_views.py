from unittest import mock

from django.conf import settings
from django.http import HttpResponse
from django.test import Client, TestCase
from django.urls import reverse

from cms.pages import tests as pages_tests

from . import views
from . handlers import BaseContentHandler
from . models import WebPath
from . import tests as context_tests


ROOT = context_tests.cms_path('/')


class FakeHandler(BaseContentHandler):

    def as_view(self):
        return HttpResponse(f'handled {self.webpath} {self.path}')


class FailingHandler(BaseContentHandler):

    def as_view(self):
        raise ValueError('handler error')


FAKE_HANDLERS = {
    FailingHandler: r'^(?P<webpath>[\/a-zA-Z0-9\.\-\_]*)(fake/failing)/?$',
    FakeHandler: r'^(?P<webpath>[\/a-zA-Z0-9\.\-\_]*)(fake/handler)/?$',
}


class BaseViewTest(TestCase):

    def setUp(self):
        # no search engine updates on pages/publications save
        patcher = mock.patch('cms.search.hooks.mongo_collection')
        patcher.start()
        self.addCleanup(patcher.stop)
        # no uniCMS cache: anonymous responses of previous tests
        # on the same urls must not be served
        patcher = mock.patch('cms.contexts.decorators.is_cache_available',
                             return_value=False)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.client = Client(HTTP_HOST='example.org')

    def create_page(self, **kwargs):
        return pages_tests.PageUnitTest.create_page(**kwargs)


class CmsDispatchTest(BaseViewTest):

    def test_published_page(self):
        page = self.create_page(webpath_path='/')
        response = self.client.get(ROOT)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page'], page)
        self.assertEqual(response.context['webpath'], page.webpath)
        self.assertEqual(response.context['path'], '/')

    def test_unknown_website(self):
        self.create_page(webpath_path='/')
        response = Client(HTTP_HOST='unknown.org').get(ROOT)
        self.assertEqual(response.status_code, 404)

    def test_unknown_webpath(self):
        self.create_page(webpath_path='/')
        url = context_tests.cms_path('/not-existent/')
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_webpath_without_page(self):
        context_tests.ContextUnitTest.create_webpath(path='/')
        self.assertEqual(self.client.get(ROOT).status_code, 404)

    def test_draft_page(self):
        page = self.create_page(webpath_path='/')
        draft = self.create_page(webpath=page.webpath, state='draft',
                                 name='draft page')
        # anonymous users get the published one
        response = self.client.get(ROOT)
        self.assertEqual(response.context['page'], page)

        # staff users in draft mode get the draft one
        user = context_tests.ContextUnitTest.create_user(is_staff=True)
        self.client.force_login(user)
        response = self.client.get(f'{ROOT}?draft_view_mode=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page'], draft)

        # without drafts the published one is shown
        draft.delete()
        response = self.client.get(ROOT)
        self.assertEqual(response.context['page'], page)

    def test_alias(self):
        root = context_tests.ContextUnitTest.create_webpath(path='/')
        WebPath.objects.create(name='alias', path='alias', parent=root,
                               alias_url='https://other.org/', is_active=True)
        response = self.client.get(context_tests.cms_path('/alias/'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'https://other.org/')

    def test_access_level(self):
        page = self.create_page(webpath_path='/')
        webpath = page.webpath
        webpath.access = '2'
        webpath.save()

        # anonymous users are redirected to login
        response = self.client.get(ROOT)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url,
                         f'{settings.LOGIN_URL}?next=http://example.org{ROOT}')

        # registered users
        user = context_tests.ContextUnitTest.create_user()
        self.client.force_login(user)
        self.assertEqual(self.client.get(ROOT).status_code, 200)

        # users without the required attribute
        with context_tests.custom_access_group():
            webpath.access = context_tests.CUSTOM_ACCESS_GROUP
            webpath.save()
            self.assertEqual(self.client.get(ROOT).status_code, 403)


@mock.patch.object(views, 'CMS_APP_REGEXP_URLPATHS_LOADED', FAKE_HANDLERS)
class CmsDispatchHandlersTest(BaseViewTest):

    def setUp(self):
        super().setUp()
        self.root = context_tests.ContextUnitTest.create_webpath(path='/')

    def test_handler(self):
        response = self.client.get(context_tests.cms_path('/fake/handler/'))
        self.assertEqual(response.status_code, 200)
        # webpath is the regexp named group
        self.assertIn('handled / /fake/handler/', response.content.decode())

    def test_handler_unknown_webpath(self):
        url = context_tests.cms_path('/other/fake/handler/')
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_handler_error(self):
        with self.assertLogs('cms.contexts.views', level='ERROR'):
            response = self.client.get(context_tests.cms_path('/fake/failing/'))
        self.assertEqual(response.status_code, 404)

    def test_handler_access_level(self):
        self.root.access = '2'
        self.root.save()
        response = self.client.get(context_tests.cms_path('/fake/handler/'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(f'{settings.LOGIN_URL}?next='))


class PagePreviewTest(BaseViewTest):

    def setUp(self):
        super().setUp()
        self.page = self.create_page()
        self.url = reverse('unicms:page-preview',
                           kwargs={'page_id': self.page.pk})

    def test_anonymous(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_staff_without_permissions(self):
        user = context_tests.ContextUnitTest.create_user(is_staff=True)
        self.client.force_login(user)
        response = self.client.get(self.url, HTTP_ACCEPT_LANGUAGE='en')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Permission Denied on this webpath',
                      response.content.decode())
        self.assertNotIn('page', response.context or {})

    def test_superuser(self):
        user = context_tests.ContextUnitTest.create_user(is_staff=True, is_superuser=True)
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['preview_mode'])
        self.assertEqual(response.context['page'], self.page)

    def test_not_existent_page(self):
        user = context_tests.ContextUnitTest.create_user(is_staff=True, is_superuser=True)
        self.client.force_login(user)
        url = reverse('unicms:page-preview', kwargs={'page_id': 999999})
        self.assertEqual(self.client.get(url).status_code, 404)


class SitemapRobotsTest(BaseViewTest):

    def test_sitemap(self):
        root = context_tests.ContextUnitTest.create_webpath(path='/')
        WebPath.objects.create(name='child', path='child', parent=root,
                               is_active=True)
        WebPath.objects.create(name='inactive', path='inactive', parent=root,
                               is_active=False)
        WebPath.objects.create(name='alias', path='alias', parent=root,
                               alias=root, is_active=True)
        WebPath.objects.create(name='alias url', path='alias-url',
                               parent=root, alias_url='https://other.org',
                               is_active=True)

        response = self.client.get(reverse('unicms_sitemap'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/xml')
        content = response.content.decode()
        self.assertIn('<loc>http://example.org/</loc>', content)
        self.assertIn('<loc>http://example.org/child/</loc>', content)
        self.assertIn('<priority>0.6</priority>', content)
        self.assertIn('<changefreq>weekly</changefreq>', content)
        for excluded in ('inactive', 'alias'):
            self.assertNotIn(f'/{excluded}/', content)

    def test_sitemap_unknown_site(self):
        response = Client(HTTP_HOST='unknown.org').get(reverse('unicms_sitemap'))
        self.assertEqual(response.status_code, 404)

    def test_robots(self):
        context_tests.ContextUnitTest.create_website()
        response = self.client.get(reverse('unicms_robots'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain')
        self.assertEqual(response.content.decode(),
                         'User-agent: *\nAllow: /\n\n'
                         f"Sitemap: http://example.org{reverse('unicms_sitemap')}")

    def test_robots_site_settings(self):
        context_tests.ContextUnitTest.create_website()
        robots = {'*': [],
                  'example.org': [{'User-agent': ['bot1', 'bot2'],
                                   'Allow': ['/a'],
                                   'Disallow': ['/b', '/c']}]}
        with mock.patch.object(views, 'ROBOTS_SETTINGS', robots):
            response = self.client.get(reverse('unicms_robots'))
        self.assertEqual(response.content.decode(),
                         'User-agent: bot1\nUser-agent: bot2\n'
                         'Allow: /a\nDisallow: /b\nDisallow: /c\n\n'
                         f"Sitemap: http://example.org{reverse('unicms_sitemap')}")
