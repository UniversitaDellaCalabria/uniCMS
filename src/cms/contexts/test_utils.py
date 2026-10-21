import importlib

from types import SimpleNamespace
from unittest import mock

from django.contrib.admin.models import ADDITION, CHANGE
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.template.exceptions import TemplateSyntaxError
from django.test import RequestFactory, TestCase, override_settings
from django.utils import translation

from cms.templates.models import Log

from . import cache as cms_cache
from . import utils
from . decorators import detect_language, unicms_cache
from . handlers import BaseContentHandler
from . models import (EditorialBoardLock, EditorialBoardLockUser,
                      WebPath, WebSite)
from . serializers import (EditorialBoardLockUserSerializer,
                           WebPathSelectOptionsSerializer,
                           WebPathSerializer)
from . templatetags.unicms_contexts import (breadcrumbs,
                                            get_site_path,
                                            language_menu)
from . import tests as context_tests
from . validators import validate_safe_url


# hooks used by load_hooks tests
HOOK_CALLS = []


def recording_hook(obj):
    HOOK_CALLS.append(obj)


def failing_hook(obj):
    raise ValueError('hook failure')


class SessionRequestMixin:

    def get_request(self, url='/', user=None, **extra):
        request = RequestFactory().get(url, **extra)
        request.session = {}
        request.user = user or AnonymousUser()
        return request


class DetectUserLanguageTest(SessionRequestMixin, TestCase):

    def tearDown(self):
        translation.deactivate()

    def test_browser_language(self):
        request = self.get_request(HTTP_ACCEPT_LANGUAGE='fr',
                                   HTTP_HOST='unknown.org')
        self.assertEqual(utils.detect_user_language(request), 'fr')
        self.assertEqual(request.LANGUAGE_CODE, 'fr')
        self.assertEqual(translation.get_language(), 'fr')
        # unknown website: nothing stored in session
        self.assertNotIn('_unicms_unknown.org_lang', request.session)

    def test_website_language(self):
        context_tests.ContextUnitTest.create_website(name='example.org',
                                       domain='example.org',
                                       is_active=True,
                                       lang='es')
        request = self.get_request(HTTP_ACCEPT_LANGUAGE='fr',
                                   HTTP_HOST='example.org:8000')
        self.assertEqual(utils.detect_user_language(request), 'es')
        # website language is cached in session
        self.assertEqual(request.session['_unicms_example.org_lang'], 'es')
        with self.assertNumQueries(0):
            self.assertEqual(utils.detect_user_language(request), 'es')

    def test_url_and_session_language(self):
        request = self.get_request('/?lang=it', HTTP_ACCEPT_LANGUAGE='fr')
        self.assertEqual(utils.detect_user_language(request), 'it')
        self.assertEqual(request.session['_unicms_lang'], 'it')

        # session language is kept on next requests
        request2 = self.get_request(HTTP_ACCEPT_LANGUAGE='fr')
        request2.session = request.session
        self.assertEqual(utils.detect_user_language(request2), 'it')

    def test_url_language_not_allowed(self):
        request = self.get_request('/?lang=xx', HTTP_ACCEPT_LANGUAGE='fr')
        utils.detect_user_language(request)
        # not stored in session
        self.assertNotIn('_unicms_lang', request.session)


class TemplateUtilsTest(TestCase):

    def test_handle_faulty_templates(self):
        res = utils.handle_faulty_templates('breadcrumbs.html',
                                            {'breadcrumbs': []})
        self.assertNotIn('Error', res)

        res = utils.handle_faulty_templates('not-existent.html', {},
                                            name='test')
        self.assertEqual(res, '<!-- Error {} template tags. See log file. -->')

        with mock.patch('cms.contexts.utils.render_to_string',
                        side_effect=TemplateSyntaxError('bad')):
            with self.assertLogs('cms.contexts.utils', level='ERROR') as logs:
                res = utils.handle_faulty_templates('breadcrumbs.html', {},
                                                    name='test')
        self.assertIn('ERROR: test template tags: bad', logs.output[0])
        self.assertIn('See log file', res)

    def test_contextualize_template(self):
        page = SimpleNamespace(
            base_template=SimpleNamespace(template_file='italia.html')
        )
        source = utils.contextualize_template('publication_view.html', page)
        self.assertIn('{% extends "italia.html" %}', source)


class AccessAndPathUtilsTest(TestCase):

    def test_webpath_access_granted(self):
        webpath = context_tests.ContextUnitTest.create_webpath()
        anonymous = AnonymousUser()
        user = context_tests.ContextUnitTest.create_user()
        superuser = context_tests.ContextUnitTest.create_user(username='admin',
                                                is_superuser=True)

        # public
        self.assertTrue(utils.webpath_access_granted(anonymous, webpath))

        # registered users
        webpath.access = '2'
        self.assertFalse(utils.webpath_access_granted(anonymous, webpath))
        self.assertTrue(utils.webpath_access_granted(user, webpath))

        # user attribute
        webpath.access = context_tests.CUSTOM_ACCESS_GROUP
        with context_tests.custom_access_group():
            self.assertFalse(utils.webpath_access_granted(anonymous, webpath))
            self.assertFalse(utils.webpath_access_granted(user, webpath))
            self.assertTrue(utils.webpath_access_granted(superuser, webpath))
            setattr(user, context_tests.CUSTOM_ACCESS_GROUP, '12345')
            self.assertTrue(utils.webpath_access_granted(user, webpath))

    def test_paths(self):
        self.assertEqual(utils.sanitize_path('//a///b/c//'), '/a/b/c/')
        self.assertEqual(utils.append_slash(''), '/')
        self.assertEqual(utils.append_slash('a'), 'a/')
        self.assertEqual(utils.append_slash('a/'), 'a/')


class ToggleSessionStateTest(SessionRequestMixin, TestCase):

    def _request(self, url, session=None):
        request = self.get_request(url)
        if session is not None:
            request.session = session
        request._messages = FallbackStorage(request)
        return request

    def _messages(self, request):
        return [str(m) for m in get_messages(request)]

    @translation.override('en')
    def test_toggle(self):
        arg = 'draft_view_mode'
        for value in ('1', 'true', 'True'):
            request = self._request(f'/?{arg}={value}')
            utils.toggle_session_state(request, arg)
            self.assertTrue(request.session[arg])
            self.assertEqual(self._messages(request),
                             ['You entered in DRAFT_VIEW_MODE'])

        for value in ('0', 'false', 'False'):
            request = self._request(f'/?{arg}={value}', {arg: True})
            utils.toggle_session_state(request, arg)
            self.assertFalse(request.session[arg])
            self.assertEqual(self._messages(request), [])

        # empty value toggles
        request = self._request(f'/?{arg}', {arg: True})
        utils.toggle_session_state(request, arg)
        self.assertFalse(request.session[arg])
        self.assertEqual(self._messages(request), [])
        request = self._request(f'/?{arg}', {arg: False})
        utils.toggle_session_state(request, arg)
        self.assertTrue(request.session[arg])
        self.assertEqual(len(self._messages(request)), 1)

        # not set or unknown values don't change anything
        for url in ('/', f'/?{arg}=other'):
            request = self._request(url, {arg: True})
            utils.toggle_session_state(request, arg)
            self.assertTrue(request.session[arg])
            self.assertEqual(self._messages(request), [])


class HooksUtilsTest(TestCase):

    def setUp(self):
        HOOK_CALLS.clear()

    def test_load_hooks(self):
        site = context_tests.ContextUnitTest.create_website()
        hooks = {'WebSite': {'POSTSAVE': [f'{__name__}.failing_hook',
                                          f'{__name__}.recording_hook']}}
        with override_settings(CMS_HOOKS=hooks):
            self.assertEqual(list(utils.get_CMS_HOOKS()['WebSite']['POSTSAVE']),
                             [failing_hook, recording_hook])
            with self.assertLogs('cms.contexts.utils', level='ERROR') as logs:
                utils.load_hooks(site, 'POSTSAVE')
            # no hooks for this flow
            utils.load_hooks(site, 'PRESAVE')
        self.assertIn('hook failure', logs.output[0])
        # the failing hook doesn't stop the others
        self.assertEqual(HOOK_CALLS, [site])


class CreatedModifiedByTest(SessionRequestMixin, TestCase):

    def test_fill_created_modified_by(self):
        user = context_tests.ContextUnitTest.create_user()
        other = context_tests.ContextUnitTest.create_user(username='other')
        webpath = WebPath(name='test', path='test')

        # anonymous
        request = self.get_request()
        self.assertFalse(utils.fill_created_modified_by(request, webpath))
        self.assertIsNone(webpath.created_by)

        request = self.get_request(user=user)
        utils.fill_created_modified_by(request, webpath)
        self.assertEqual(webpath.created_by, user)
        self.assertEqual(webpath.modified_by, user)

        # created_by is kept
        request = self.get_request(user=other)
        utils.fill_created_modified_by(request, webpath)
        self.assertEqual(webpath.created_by, user)
        self.assertEqual(webpath.modified_by, other)

        # objects without these fields
        site = WebSite(name='a', domain='a')
        utils.fill_created_modified_by(request, site)
        self.assertFalse(hasattr(site, 'created_by'))


class PermissionsUtilsTest(TestCase):

    def test_is_translator(self):
        self.assertIsNone(utils.is_translator(-1))
        self.assertEqual(utils.is_translator(0), {})
        self.assertEqual(utils.is_translator(1), {'only_created_by': False,
                                                  'allow_descendant': False})
        self.assertEqual(utils.is_translator(2), {'only_created_by': False,
                                                  'allow_descendant': True})

    def test_is_editor(self):
        self.assertIsNone(utils.is_editor(-1))
        self.assertEqual(utils.is_editor(2), {})
        self.assertEqual(utils.is_editor(3), {'only_created_by': True,
                                              'allow_descendant': False})
        self.assertEqual(utils.is_editor(4), {'only_created_by': False,
                                              'allow_descendant': False})
        self.assertEqual(utils.is_editor(5), {'only_created_by': False,
                                              'allow_descendant': True})

    def test_is_publisher(self):
        self.assertIsNone(utils.is_publisher(-1))
        self.assertEqual(utils.is_publisher(5), {})
        self.assertEqual(utils.is_publisher(6), {'only_created_by': False,
                                                 'allow_descendant': False})
        self.assertEqual(utils.is_publisher(7), {'only_created_by': False,
                                                 'allow_descendant': True})


class LogAndCloneUtilsTest(TestCase):

    @translation.override('en')
    def test_log_obj_event(self):
        user = context_tests.ContextUnitTest.create_user()
        site = context_tests.ContextUnitTest.create_website()
        ct = ContentType.objects.get_for_model(site)

        data = {'id': 1, 'created': 'x', 'modified': 'x', 'created_by': 1,
                'modified_by': 1, 'object_content_type': 1, 'name': 'new'}
        utils.log_obj_event(user, site, data)
        log = Log.objects.get(content_type=ct, object_id=site.pk)
        self.assertEqual(log.action_flag, CHANGE)
        self.assertEqual(log.change_message, "changed: {'name': 'new'}")
        self.assertEqual(log.user, user)
        self.assertEqual(log.object_repr, str(site))
        # data is not modified
        self.assertIn('id', data)

        Log.objects.all().delete()
        utils.log_obj_event(user, site, action_flag=ADDITION)
        self.assertEqual(Log.objects.get().change_message, 'added')

        # not copyable data are not logged
        Log.objects.all().delete()
        with mock.patch('cms.contexts.utils.deepcopy',
                        side_effect=TypeError('cannot pickle')):
            utils.log_obj_event(user, site, {'file': 'x'})
        self.assertEqual(Log.objects.get().change_message, 'changed')

    def test_clone(self):
        site = context_tests.ContextUnitTest.create_website()
        clone = utils.clone(site)
        self.assertNotEqual(clone.pk, site.pk)
        self.assertEqual(WebSite.objects.count(), 2)

        with self.assertRaises(Exception):
            utils.clone(object())


class CacheTest(SessionRequestMixin, TestCase):

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def _request(self, url='/', lang='en', **kwargs):
        request = self.get_request(url, **kwargs)
        request.LANGUAGE_CODE = lang
        return request

    def test_make_cache_key(self):
        key = cms_cache.make_cache_key(self._request('/a/?b=1&c=2'))
        self.assertTrue(key.startswith(cms_cache.CMS_CACHE_KEY_PREFIX))
        # query params order doesn't matter
        self.assertEqual(key, cms_cache.make_cache_key(self._request('/a/?c=2&b=1')))
        # request language is used if lang is missing
        self.assertNotEqual(key,
                            cms_cache.make_cache_key(self._request('/a/?c=2&b=1',
                                                                   lang='it')))
        self.assertEqual(cms_cache.make_cache_key(self._request('/a/?lang=it')),
                         cms_cache.make_cache_key(self._request('/a/', lang='it')))
        # path and host matter
        self.assertNotEqual(key, cms_cache.make_cache_key(self._request('/b/?b=1&c=2')))
        self.assertNotEqual(key,
                            cms_cache.make_cache_key(self._request('/a/?b=1&c=2',
                                                                   HTTP_HOST='other.org')))

    def test_get_set(self):
        request = self._request('/a/')
        self.assertIsNone(cms_cache.get_from_cache(request))
        self.assertTrue(cms_cache.set_to_cache(request, 'value'))
        self.assertEqual(cms_cache.get_from_cache(request), 'value')

    def test_set_max_entries(self):
        request = self._request('/a/')
        fake_cache = mock.MagicMock()
        with mock.patch.object(cms_cache, 'cache', fake_cache), \
             mock.patch.object(cms_cache, 'CMS_CACHE_MAX_ENTRIES', 2):
            fake_cache.keys.return_value = ['k1']
            self.assertTrue(cms_cache.set_to_cache(request, 'value'))
            fake_cache.set.assert_called_once()
            fake_cache.keys.assert_called_with(f'{cms_cache.CMS_CACHE_KEY_PREFIX}*')

            # cache full
            fake_cache.reset_mock()
            fake_cache.keys.return_value = ['k1', 'k2']
            self.assertIsNone(cms_cache.set_to_cache(request, 'value'))
            fake_cache.set.assert_not_called()

    def test_cacheable(self):
        self.assertTrue(cms_cache.is_request_cacheable(self._request('/a/')))
        self.assertFalse(cms_cache.is_request_cacheable(self._request('/search?q=1')))
        self.assertTrue(cms_cache.is_response_cacheable(HttpResponse()))
        self.assertFalse(cms_cache.is_response_cacheable(HttpResponse(status=404)))

    def test_is_cache_available(self):
        for value in (True, False):
            with mock.patch.object(cms_cache, 'CMS_CACHE_ENABLED', value):
                self.assertEqual(cms_cache.is_cache_available(), value)


class DecoratorsTest(SessionRequestMixin, TestCase):

    def setUp(self):
        cache.clear()
        self.calls = []

    def tearDown(self):
        cache.clear()
        translation.deactivate()

    def _view(self, status=200):
        @unicms_cache
        def view(request):
            self.calls.append(request)
            return HttpResponse(f'content {len(self.calls)}', status=status)
        return view

    def _request(self, url='/a/', user=None):
        request = self.get_request(url, user=user)
        request.LANGUAGE_CODE = 'en'
        return request

    def test_detect_language(self):
        @detect_language
        def view(request, arg):
            return request.LANGUAGE_CODE, arg

        request = self.get_request('/?lang=it')
        self.assertEqual(view(request, 'arg'), ('it', 'arg'))

    def test_cache_disabled(self):
        view = self._view()
        with mock.patch.object(cms_cache, 'CMS_CACHE_ENABLED', False):
            view(self._request())
            view(self._request())
        self.assertEqual(len(self.calls), 2)

    def test_cache_enabled(self):
        view = self._view()
        with mock.patch.object(cms_cache, 'CMS_CACHE_ENABLED', True):
            res1 = view(self._request())
            res2 = view(self._request())
            # authenticated users skip the cache
            user = context_tests.ContextUnitTest.create_user()
            res3 = view(self._request(user=user))
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(res1.content, b'content 1')
        self.assertEqual(res2.content, b'content 1')
        self.assertEqual(res3.content, b'content 2')

    def test_cache_enabled_not_cacheable(self):
        with mock.patch.object(cms_cache, 'CMS_CACHE_ENABLED', True):
            # excluded request
            view = self._view()
            view(self._request('/search?q=1'))
            view(self._request('/search?q=1'))
            self.assertEqual(len(self.calls), 2)

            # not 200 responses
            view = self._view(status=404)
            view(self._request())
            res = view(self._request())
        self.assertEqual(len(self.calls), 4)
        self.assertEqual(res.status_code, 404)


class ValidatorsTest(TestCase):

    def test_validate_safe_url(self):
        for value in ('', None, '/relative/path', 'relative',
                      'https://example.org', 'http://example.org',
                      'mailto:a@example.org', 'tel:+39000', '#anchor'):
            self.assertIsNone(validate_safe_url(value))

        for value in ('javascript:alert(1)', 'JavaScript:alert(1)',
                      'java\tscript:alert(1)', ' javascript:alert(1)',
                      'data:text/html;base64,AAAA', 'vbscript:msgbox',
                      'ftp://example.org'):
            with self.assertRaises(ValidationError):
                validate_safe_url(value)

        with self.assertRaisesMessage(ValidationError, 'Invalid url'):
            validate_safe_url('http://[::1')


class HandlersTest(TestCase):

    def test_base_content_handler(self):
        handler = BaseContentHandler(path='/a/', webpath='webpath',
                                     extra='value')
        self.assertEqual(handler.path, '/a/')
        self.assertEqual(handler.webpath, 'webpath')
        self.assertEqual(handler.extra, 'value')
        self.assertEqual(handler.template, 'default_template.html')
        self.assertEqual(BaseContentHandler(path='/', template_fname='a.html').template,
                         'a.html')
        for method in ('match', 'get', 'url', 'as_view'):
            with self.assertRaises(NotImplementedError):
                getattr(handler, method)()


class SerializersTest(TestCase):

    def test_webpath_serializer(self):
        root = context_tests.ContextUnitTest.create_webpath(path='/')
        child = WebPath.objects.create(name='child', path='child',
                                       parent=root)
        alias = WebPath.objects.create(name='alias', path='alias',
                                       parent=root, alias=child)

        data = WebPathSerializer(root).data
        self.assertIsNone(data['parent'])
        self.assertIsNone(data['alias'])
        self.assertEqual(data['full_name'], str(root))
        self.assertEqual(data['object_content_type'],
                         ContentType.objects.get_for_model(WebPath).pk)

        data = WebPathSerializer(alias).data
        self.assertEqual(data['parent']['id'], root.pk)
        self.assertEqual(data['alias']['id'], child.pk)
        self.assertEqual(data['alias']['parent']['id'], root.pk)
        self.assertEqual(data['get_full_path'], context_tests.cms_path('/child/'))

        self.assertEqual(WebPathSerializer().validate_path('My Path/x'),
                         'my-pathx')

    def test_foreign_keys_querysets(self):
        site = context_tests.ContextUnitTest.create_website()
        other_site = context_tests.ContextUnitTest.create_website(name='other.org',
                                                    domain='other.org',
                                                    is_active=True)
        root = context_tests.ContextUnitTest.create_webpath(path='/')
        WebPath.objects.create(name='root', path='/', site=other_site)

        # without request
        serializer = WebPathSerializer(context={})
        self.assertIsNone(serializer.fields['site'].get_queryset())
        self.assertIsNone(serializer.fields['parent'].get_queryset())

        # with request: filtered by site_id url kwarg
        request = SimpleNamespace(parser_context={'kwargs': {'site_id': site.pk}})
        serializer = WebPathSerializer(context={'request': request})
        self.assertEqual(list(serializer.fields['site'].get_queryset()), [site])
        self.assertEqual(list(serializer.fields['parent'].get_queryset()), [root])

    def test_select_options_serializer(self):
        root = context_tests.ContextUnitTest.create_webpath(path='/')
        self.assertEqual(WebPathSelectOptionsSerializer(root).data,
                         {'value': root.pk, 'text': str(root)})

    def test_lock_user_serializer(self):
        user = context_tests.ContextUnitTest.create_user()
        webpath = context_tests.ContextUnitTest.create_webpath()
        ct = ContentType.objects.get_for_model(webpath)
        lock = EditorialBoardLock.objects.create(content_type=ct,
                                                 object_id=webpath.pk)
        lock_user = EditorialBoardLockUser.objects.create(lock=lock,
                                                          user=user)
        data = EditorialBoardLockUserSerializer(lock_user).data
        self.assertEqual(data['user'], str(user))
        self.assertEqual(data['lock']['object_id'], webpath.pk)


class TemplateTagsTest(SessionRequestMixin, TestCase):

    def test_language_menu(self):
        request = self.get_request('/?a=1&lang=it')
        data = language_menu({'request': request})
        self.assertEqual(data['en'], ('English', '?a=%5B%271%27%5D&lang=en'))

        data = language_menu({'request': self.get_request('/')})
        self.assertEqual(data['it'], ('Italian', '?lang=it'))

        # with template
        res = language_menu({'request': request}, template='not-existent.html')
        self.assertIn('Error', res)

    def test_breadcrumbs_leaf(self):
        root = context_tests.ContextUnitTest.create_webpath(path='/')
        child = WebPath.objects.create(name='child', path='child',
                                       parent=root)
        leaf = SimpleNamespace(breadcrumbs=[('/child/leaf/', 'the leaf')])
        res = breadcrumbs(child, leaf=leaf)
        self.assertIn('/child/', res)
        self.assertIn('the leaf', res)

    def test_get_site_path(self):
        webpath = context_tests.ContextUnitTest.create_webpath(path='/')
        request = RequestFactory().get('/', SERVER_PORT='8080')
        self.assertEqual(get_site_path({'request': request}, webpath),
                         f"//example.org:8080{context_tests.cms_path('/')}")


class UrlsTest(TestCase):

    def test_path_prefix_redirect(self):
        from . import urls
        try:
            with override_settings(CMS_PATH_PREFIX='portale/'):
                importlib.reload(urls)
            root = urls.urlpatterns[0]
            response = root.callback(RequestFactory().get('/'))
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, '/portale/')
        finally:
            importlib.reload(urls)
        # urls restored according to the real settings
        names = [i.name for i in urls.urlpatterns]
        self.assertIn('page-preview', names)
        self.assertIn('cms_dispatch', names)
