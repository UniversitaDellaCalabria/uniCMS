import importlib
import io
import os
import tempfile

from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest import mock

from django.conf import settings
from django.contrib.admin.models import CHANGE
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.test import TestCase, override_settings

from cms.contexts import tests as context_tests

from . import settings as app_settings
from . import tests as template_tests
from . import utils
from . management.commands import unicms_collect_templates as collect_cmd
from . models import Log
from . serializers import LogSerializer, TemplatesBlockSerializer
from . templatetags import unicms_templates as tags


class TemplatesModelsTest(TestCase):

    def test_str(self):
        ptb = template_tests.TemplateUnitTest.create_page_block_template()
        self.assertEqual(str(ptb.template), 'Bootstrap Italia (italia.html)')
        self.assertEqual(str(ptb.block), 'Carousel - Main Banner')
        self.assertEqual(str(ptb),
                         f'({ptb.template}) {ptb.block} 10:banner')
        ptb.order = None
        ptb.section = None
        self.assertEqual(str(ptb), f'({ptb.template}) {ptb.block} 0:')
        self.assertEqual(ptb.type, ptb.block.type)
        self.assertEqual(ptb.content, ptb.block.content)

    def test_image_as_html(self):
        block = template_tests.TemplateUnitTest.create_block_template()
        self.assertEqual(block.image_as_html(),
                         f'{settings.STATIC_URL}images/no-image.jpg')

        # an image is set: no file is written
        block.image.name = 'images/block_templates_previews/preview.png'
        self.assertEqual(block.image_as_html(),
                         f'<img width=280 src="{block.image.url}"/>')


class TemplatesSerializersTest(TestCase):

    def test_template_block_serializer(self):
        block = template_tests.TemplateUnitTest.create_block_template()
        data = TemplatesBlockSerializer(block).data
        self.assertEqual(data['type_friendly'], 'HTML Block')

        block.type = 'unknown.Block'
        self.assertNotIn('type_friendly', TemplatesBlockSerializer(block).data)

    def test_log_serializer(self):
        user = context_tests.ContextUnitTest.create_user()
        site = context_tests.ContextUnitTest.create_website()
        log = Log.objects.log_action(user_id=user.pk,
                                     content_type_id=ContentType.objects.get_for_model(site).pk,
                                     object_id=site.pk,
                                     object_repr=str(site),
                                     action_flag=CHANGE,
                                     change_message='changed')
        data = LogSerializer(log).data
        self.assertEqual(data['user'], str(user))
        self.assertEqual(data['object_id'], site.pk)


class TemplatesUtilsTest(TestCase):

    def test_secure_url(self):
        with override_settings(DEBUG=True):
            self.assertEqual(utils.secure_url('http://a.org/http://'),
                             'http://a.org/http://')
        with override_settings(DEBUG=False):
            self.assertEqual(utils.secure_url('http://a.org/b'),
                             'https://a.org/b')

    def test_is_dir_usefull(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertFalse(utils.is_dir_usefull(tmp))
            self.assertFalse(utils.is_dir_usefull(f'{tmp}/not-existent'))
            open(f'{tmp}/file.html', 'w').close()
            self.assertTrue(utils.is_dir_usefull(tmp))

    def test_get_unicms_templates(self):
        with tempfile.TemporaryDirectory() as tmp:
            for folder in ('pages', 'blocks', 'admin', 'empty'):
                os.makedirs(f'{tmp}/{folder}')
            for fname in ('pages/p.html', 'blocks/b.html', 'blocks/b.txt',
                          'admin/a.html'):
                open(f'{tmp}/{fname}', 'w').close()
            templates = [{'BACKEND': 'django.template.backends.django.DjangoTemplates',
                          'DIRS': [tmp, f'{tmp}/empty', f'{tmp}/not-existent'],
                          'APP_DIRS': False,
                          'OPTIONS': {}}]
            with override_settings(TEMPLATES=templates):
                result = utils.get_unicms_templates()
        self.assertEqual(result, [(f'{tmp}/', 'admin/', 'a.html'),
                                  (f'{tmp}/', 'blocks/', 'b.html'),
                                  (f'{tmp}/', 'pages/', 'p.html')])


class TemplatesSettingsTest(TestCase):

    def test_templates_not_found(self):
        try:
            with mock.patch('glob.glob', return_value=[]):
                with self.assertLogs('cms.templates.settings',
                                     level='WARNING') as logs:
                    importlib.reload(app_settings)
            self.assertEqual(app_settings.CMS_BLOCK_TEMPLATES, [])
            self.assertEqual(app_settings.CMS_PAGE_TEMPLATES, [])
            self.assertIn('Block template files not found', logs.output[0])
            self.assertIn('Page template files not found', logs.output[1])
        finally:
            importlib.reload(app_settings)

    def test_templates_found(self):
        files = ['/x/templates/unicms/pages/b.html',
                 '/x/templates/unicms/pages/a.html']
        try:
            with mock.patch('glob.glob', return_value=files):
                with self.assertLogs('cms.templates.settings',
                                     level='INFO') as logs:
                    importlib.reload(app_settings)
            self.assertEqual(app_settings.CMS_PAGE_TEMPLATES,
                             [('a.html', 'a.html'), ('b.html', 'b.html')])
            self.assertEqual(len(logs.output), 2)
        finally:
            importlib.reload(app_settings)


class TemplateTagsTest(TestCase):

    def _context(self, sections, page=True, **kwargs):
        blocks = [SimpleNamespace(section=s) for s in sections]
        context = dict(**kwargs)
        if page:
            context['page'] = mock.Mock(get_blocks=mock.Mock(return_value=blocks))
        return context

    def test_supported_languages(self):
        self.assertEqual(tags.supported_languages(), settings.LANGUAGES)

    def test_blocks_in_position(self):
        # no page
        self.assertFalse(tags.blocks_in_position(self._context([], page=False),
                                                 section='banner'))
        # no blocks or no section
        self.assertFalse(tags.blocks_in_position(self._context([]),
                                                 section='banner'))
        self.assertFalse(tags.blocks_in_position(self._context(['banner'])))

        # simple sections
        context = self._context(['banner', '1-top-a'])
        self.assertTrue(tags.blocks_in_position(context, section='banner'))
        self.assertFalse(tags.blocks_in_position(context, section='menu-1'))

        # sections with sub-sections
        self.assertTrue(tags.blocks_in_position(context, section='section-1'))
        with self.assertLogs('cms.templates.templatetags.unicms_templates',
                             level='WARNING'):
            self.assertFalse(tags.blocks_in_position(context,
                                                     section='section-2'))

        # page_blocks in context are preferred
        context = self._context(['banner'],
                                page_blocks=[SimpleNamespace(section='menu-1')])
        self.assertTrue(tags.blocks_in_position(context, section='menu-1'))
        self.assertFalse(tags.blocks_in_position(context, section='banner'))

    def test_blocks_in_position_empty_sub_sections(self):
        sections = (('empty', ()),)
        with mock.patch.object(tags, 'CMS_TEMPLATE_BLOCK_SECTIONS', sections):
            with self.assertLogs('cms.templates.templatetags.unicms_templates',
                                 level='WARNING') as logs:
                self.assertFalse(tags.blocks_in_position(self._context(['empty']),
                                                         section='empty'))
        self.assertIn("Section empty hasn't sub-sections", logs.output[0])

    @override_settings(TEST_STR='hello {who}', TEST_LIST=[1, 2], TEST_EMPTY='')
    def test_settings_value(self):
        self.assertEqual(tags.settings_value('NOT_EXISTENT'), '')
        self.assertEqual(tags.settings_value('TEST_EMPTY'), '')
        self.assertEqual(tags.settings_value('TEST_STR'), 'hello {who}')
        self.assertEqual(tags.settings_value('TEST_STR', who='world'),
                         'hello world')
        self.assertEqual(tags.settings_value('TEST_LIST', who='world'), [1, 2])

    def test_random_id(self):
        self.assertEqual(tags.random_id('my-id'), 'my-id')
        self.assertRegex(tags.random_id(), r'^id_\d+$')

    def test_get_value(self):
        self.assertEqual(tags.get_value({'a': 1}, 'a'), 1)
        self.assertIsNone(tags.get_value({'a': 1}, 'b'))


class CollectTemplatesCommandTest(TestCase):

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.src = f'{tmp.name}/src/'
        self.dest = f'{tmp.name}/dest/unicms'
        for folder in ('pages', 'blocks', 'admin'):
            os.makedirs(f'{self.src}{folder}')
        for fname in ('pages/p.html', 'blocks/b.html', 'admin/a.html'):
            with open(f'{self.src}{fname}', 'w') as f:
                f.write(fname)
        self.templates = [(self.src, 'admin/', 'a.html'),
                          (self.src, 'blocks/', 'b.html'),
                          (self.src, 'pages/', 'p.html')]

        patcher = mock.patch.object(collect_cmd, 'CMS_TEMPLATES_FOLDER', self.dest)
        patcher.start()
        self.addCleanup(patcher.stop)
        patcher = mock.patch.object(collect_cmd, 'get_unicms_templates',
                                    side_effect=lambda: self.templates)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _call(self, *args, **kwargs):
        out = io.StringIO()
        with redirect_stdout(out):
            call_command('unicms_collect_templates', *args, **kwargs)
        return out.getvalue()

    def test_collect(self):
        output = self._call('-y')
        for folder, fname in (('pages', 'p.html'), ('blocks', 'b.html'),
                              ('admin', 'a.html')):
            dest = f'{self.dest}/{folder}/{fname}'
            self.assertTrue(os.path.islink(dest))
            self.assertEqual(os.readlink(dest), f'{self.src}{folder}/{fname}')
            self.assertIn(f'Copying {self.src}{folder}/{fname} -> {dest}', output)

        # run again: preexistent folders are cleaned up
        stale = f'{self.dest}/blocks/stale.html'
        open(stale, 'w').close()
        self._call(y=True)
        self.assertFalse(os.path.exists(stale))
        self.assertTrue(os.path.islink(f'{self.dest}/blocks/b.html'))

    def test_existent_destination(self):
        # the same destination twice: the first symlink is replaced
        self.templates = [(self.src, 'blocks/', 'b.html'),
                          (self.src, 'blocks/', 'b.html')]
        self._call('-y')
        self.assertTrue(os.path.islink(f'{self.dest}/blocks/b.html'))

        # broken symlinks are not seen by os.path.exists
        missing = f'{self.src}missing/'
        self.templates = [(missing, 'blocks/', 'b.html'),
                          (missing, 'blocks/', 'b.html')]
        output = self._call('-y')
        self.assertIn('ERROR', output)
        self.assertIn('File Already Exists', output)

    def test_confirm(self):
        with mock.patch('builtins.input', side_effect=['maybe', 'N']) as m:
            self._call()
        self.assertEqual(m.call_count, 2)
        self.assertFalse(os.path.exists(self.dest))

        with mock.patch('builtins.input', return_value='y'):
            self._call()
        self.assertTrue(os.path.islink(f'{self.dest}/pages/p.html'))
