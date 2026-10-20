import logging
import os

from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from glob import glob
from shutil import copyfile

from . models import Media, MediaCollection, MediaCollectionItem, ValidationError, validate_file_size, validate_image_size_ratio
from . validators import validate_file_extension
from . settings import FILE_MAX_SIZE

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MediaUnitTest(TestCase):

    def setUp(cls):
        pass

    @classmethod
    def create_media(cls, **kwargs):
        data = {'title': 'media1',
                'file': f'{settings.MEDIA_ROOT}/images/categories/eventi.jpg',
                'description': 'blah blah'}
        for k,v in kwargs.items():
            data[k] = v
        obj = Media.objects.create(**data)
        return obj

    @classmethod
    def create_media_collection(cls, **kwargs):
        data = {'name': 'media1',
                'tags': ['ciao', 'mamma'],
                'description': 'blah blah',
                'is_active': 1}
        for k,v in kwargs.items():
            data[k] = v
        obj = MediaCollection.objects.create(**data)

        item = MediaCollectionItem.objects.create(media=cls.create_media(),
                                                  collection=obj,
                                                  is_active=1)
        return obj

    @classmethod
    def test_delete_media(cls, **kwargs):
        fpath = f'{settings.MEDIA_ROOT}/unit_tests/download.jpeg'
        dest = f'{settings.MEDIA_ROOT}/unit_tests/download.webp'
        media = cls.create_media(file = fpath)
        copyfile(fpath, dest)

        media.__str__()
        assert isinstance(media.get_media_path(), str)

        # testing also file_size_X properties
        media.file_size_kb
        media.file_size_mb

        media.delete()

    @classmethod
    def test_create_faulty_media_ext(cls):
        data = {'title': 'media1',
                'file': f'{settings.MEDIA_ROOT}/unit_tests/icon_small.arj',
                'description': 'blah blah'}

        media = cls.create_media(**data)
        try:
            validate_file_extension(media.file)
        except Exception as e:
            assert isinstance(e, ValidationError)

    @classmethod
    def test_create_faulty_media_size(cls):
        fpath = f'{settings.MEDIA_ROOT}/garbage.img'
        os.system(f'dd if=/dev/zero of={fpath} bs={FILE_MAX_SIZE+1024} count=1' )
        data = {'title': 'media1',
                'file': fpath,
                'description': 'blah blah'}

        media = cls.create_media(**data)
        try:
            validate_file_size(media.file)
        except Exception as e:
            assert isinstance(e, ValidationError)

        os.remove(fpath)

    @classmethod
    def test_create_faulty_media_size_ratio(cls):
        data = {'title': 'media1',
                'file': f'{settings.MEDIA_ROOT}/unit_tests/faulty_size.jpg',
                'description': 'blah blah'}

        media = cls.create_media(**data)
        try:
            validate_image_size_ratio(media.file)
        except Exception as e:
            assert isinstance(e, ValidationError)

    def test_uuid_url(self):
        media = MediaUnitTest.create_media()
        response = self.client.get(reverse('unicms_medias:media-file',
                                   kwargs={'unique_code': media.uuid}))
        # redirect to media file
        self.assertEqual(response.status_code, 302)

    def tearDown(self):
        match = f'{settings.MEDIA_ROOT}/medias/{timezone.now().year}/eventi_*.*'
        for i in glob(match):
            os.remove(i)


# --- image helpers and tests on validators, utils, hooks, serializers ---

import shutil
import tempfile

from io import BytesIO
from types import SimpleNamespace
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image

from . import hooks as media_hooks
from . import utils as media_utils
from . import validators as media_validators
from . forms import MediaCollectionItemForm
from . models import context_media_path
from . serializers import (MediaCollectionForeignKey,
                           MediaCollectionItemSerializer,
                           MediaCollectionSelectOptionsSerializer,
                           MediaSelectOptionsSerializer,
                           MediaSerializer)


def make_image_bytes(size=(100, 40), mode='RGB', fmt='PNG', **save_kwargs):
    """
    builds an image in memory and returns its bytes
    """
    buf = BytesIO()
    color = 0 if mode in ('P', 'L', '1') else None
    Image.new(mode, size, color=color).save(buf, format=fmt, **save_kwargs)
    return buf.getvalue()


def make_upload(name='image.png', content=None, content_type='image/png'):
    return SimpleUploadedFile(name,
                              content if content is not None else make_image_bytes(),
                              content_type=content_type)


# PNG header followed by garbage: detected as image/png, not readable by Pillow
CORRUPTED_PNG = make_image_bytes()[:16] + b'garbage' * 20
PDF_CONTENT = b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF\n'


class TemporaryMediaRootMixin:
    """
    every file saved during the test goes in a temporary MEDIA_ROOT
    """

    def setUp(self):
        super().setUp()
        self._media_root = tempfile.mkdtemp(prefix='unicms-test-media-')
        self._override = override_settings(MEDIA_ROOT=self._media_root)
        self._override.enable()

    def tearDown(self):
        self._override.disable()
        shutil.rmtree(self._media_root, ignore_errors=True)
        super().tearDown()


class MediaValidatorsUnitTest(TestCase):

    def test_validate_file_size(self):
        # objects without size are ignored
        self.assertIsNone(media_validators.validate_file_size(object()))
        # undetectable size
        with self.assertRaises(ValidationError):
            media_validators.validate_file_size(SimpleNamespace(size='abc'))
        # too big
        too_big = SimpleNamespace(size=media_validators.FILE_MAX_SIZE + 1)
        with self.assertRaises(ValidationError):
            media_validators.validate_file_size(too_big)
        # ok
        ok = SimpleNamespace(size=media_validators.FILE_MAX_SIZE)
        self.assertIsNone(media_validators.validate_file_size(ok))

    def test_validate_file_extension(self):
        # objects without file are ignored
        self.assertIsNone(media_validators.validate_file_extension(object()))
        # consistent name and content
        self.assertIsNone(media_validators.validate_file_extension(make_upload()))
        # pointer is reset after validation
        upload = make_upload()
        media_validators.validate_file_extension(upload)
        self.assertEqual(upload.file.tell(), 0)
        # extension not consistent with content (eg: png served as html)
        with self.assertRaises(ValidationError):
            media_validators.validate_file_extension(make_upload(name='image.html'))
        # file without extension
        with self.assertRaises(ValidationError):
            media_validators.validate_file_extension(make_upload(name='image'))
        # mimetype not allowed
        html = SimpleUploadedFile('page.html',
                                  b'<html><body><script>alert(1)</script></body></html>',
                                  content_type='text/html')
        with self.assertRaises(ValidationError):
            media_validators.validate_file_extension(html)

    def test_validate_image_and_media_file_extension(self):
        self.assertIsNone(media_validators.validate_image_file_extension(make_upload()))
        self.assertIsNone(media_validators.validate_media_file_extension(make_upload()))
        pdf = SimpleUploadedFile('doc.pdf', PDF_CONTENT,
                                 content_type='application/pdf')
        # pdf is an allowed file but not an image or a media
        self.assertIsNone(media_validators.validate_file_extension(pdf))
        with self.assertRaises(ValidationError):
            media_validators.validate_image_file_extension(pdf)
        with self.assertRaises(ValidationError):
            media_validators.validate_media_file_extension(pdf)

    @mock.patch('cms.medias.validators.FILETYPE_IMAGE_YX_RATIO_MIN', 0.3)
    @mock.patch('cms.medias.validators.FILETYPE_IMAGE_YX_RATIO_MAX', 0.6)
    def test_validate_image_size_ratio(self):
        # objects without content_type are ignored
        self.assertIsNone(media_validators.validate_image_size_ratio(object()))
        # valid ratio 40 / 100
        upload = make_upload(content=make_image_bytes(size=(100, 40)))
        self.assertIsNone(media_validators.validate_image_size_ratio(upload))
        self.assertEqual(upload.file.tell(), 0)
        # too low 10 / 100
        with self.assertRaises(ValidationError):
            media_validators.validate_image_size_ratio(
                make_upload(content=make_image_bytes(size=(100, 10))))
        # too high 100 / 100
        with self.assertRaises(ValidationError):
            media_validators.validate_image_size_ratio(
                make_upload(content=make_image_bytes(size=(100, 100))))
        # not an image: ignored
        pdf = SimpleUploadedFile('doc.pdf', PDF_CONTENT,
                                 content_type='application/pdf')
        self.assertIsNone(media_validators.validate_image_size_ratio(pdf))
        # corrupted image: ignored here, validate_image_max_pixels raises
        corrupted = make_upload(content=CORRUPTED_PNG)
        self.assertIsNone(media_validators.validate_image_size_ratio(corrupted))

    def test_validate_image_max_pixels(self):
        # objects without file are ignored
        self.assertIsNone(media_validators.validate_image_max_pixels(object()))
        # not an image: ignored
        pdf = SimpleUploadedFile('doc.pdf', PDF_CONTENT,
                                 content_type='application/pdf')
        self.assertIsNone(media_validators.validate_image_max_pixels(pdf))
        # small image
        upload = make_upload()
        self.assertIsNone(media_validators.validate_image_max_pixels(upload))
        self.assertEqual(upload.file.tell(), 0)
        # corrupted image
        with self.assertRaisesMessage(ValidationError, 'Invalid image file'):
            media_validators.validate_image_max_pixels(make_upload(content=CORRUPTED_PNG))

    @mock.patch('cms.medias.utils.CMS_IMAGE_MAX_PIXELS', 1000)
    def test_validate_image_max_pixels_exceeded(self):
        upload = make_upload(content=make_image_bytes(size=(100, 40)))
        with self.assertRaises(ValidationError):
            media_validators.validate_image_max_pixels(upload)
        # pointer is reset also on errors
        self.assertEqual(upload.file.tell(), 0)

    def test_validate_image_max_pixels_decompression_bomb(self):
        upload = make_upload(content=make_image_bytes(size=(100, 40)))
        # Pillow raises DecompressionBombError over 2 * MAX_IMAGE_PIXELS
        with mock.patch.object(Image, 'MAX_IMAGE_PIXELS', 100):
            with self.assertRaises(ValidationError):
                media_validators.validate_image_max_pixels(upload)


class MediaUtilsUnitTest(TestCase):

    def test_get_file_type_size(self):
        content = make_image_bytes()
        data = media_utils.get_file_type_size(SimpleNamespace(file=BytesIO(content)))
        self.assertEqual(data, {'mime_type': 'image/png',
                                'file_size': len(content)})

    def test_get_image_width_height(self):
        self.assertEqual(media_utils.get_image_width_height(BytesIO(make_image_bytes(size=(30, 20)))),
                         (30, 20))
        # corrupted image
        self.assertIsNone(media_utils.get_image_width_height(BytesIO(CORRUPTED_PNG)))
        # not an image
        self.assertIsNone(media_utils.get_image_width_height(BytesIO(PDF_CONTENT)))

    def test_image_exceeds_max_pixels(self):
        im = Image.new('RGB', (100, 40))
        with mock.patch('cms.medias.utils.CMS_IMAGE_MAX_PIXELS', 4000):
            self.assertFalse(media_utils.image_exceeds_max_pixels(im))
        with mock.patch('cms.medias.utils.CMS_IMAGE_MAX_PIXELS', 3999):
            self.assertTrue(media_utils.image_exceeds_max_pixels(im))
        # check disabled
        with mock.patch('cms.medias.utils.CMS_IMAGE_MAX_PIXELS', 0):
            self.assertFalse(media_utils.image_exceeds_max_pixels(im))

    def test_image_exceeds_max_pixels_animated(self):
        # frames are counted too
        frames = [Image.new('RGB', (10, 10), color=c)
                  for c in ('red', 'green', 'blue')]
        buf = BytesIO()
        frames[0].save(buf, format='GIF', save_all=True,
                       append_images=frames[1:], duration=100, loop=0)
        buf.seek(0)
        im = Image.open(buf)
        self.assertEqual(im.n_frames, 3)
        with mock.patch('cms.medias.utils.CMS_IMAGE_MAX_PIXELS', 299):
            self.assertTrue(media_utils.image_exceeds_max_pixels(im))
        with mock.patch('cms.medias.utils.CMS_IMAGE_MAX_PIXELS', 300):
            self.assertFalse(media_utils.image_exceeds_max_pixels(im))

    def _webp(self, content):
        byte_io = media_utils.to_webp(BytesIO(content))
        self.assertIsNotNone(byte_io)
        self.assertEqual(byte_io.tell(), 0)
        return Image.open(byte_io)

    def test_to_webp_rgb(self):
        im = self._webp(make_image_bytes(size=(30, 20)))
        self.assertEqual(im.format, 'WEBP')
        self.assertEqual(im.size, (30, 20))

    def test_to_webp_converted_modes(self):
        # CMYK jpeg -> RGB
        im = self._webp(make_image_bytes(mode='CMYK', fmt='JPEG'))
        self.assertEqual(im.mode, 'RGB')
        # LA -> RGBA
        im = self._webp(make_image_bytes(mode='LA'))
        self.assertEqual(im.mode, 'RGBA')
        # P without transparency -> RGB
        im = self._webp(make_image_bytes(mode='P'))
        self.assertEqual(im.mode, 'RGB')
        # P with transparency -> RGBA
        im = self._webp(make_image_bytes(mode='P', transparency=0))
        self.assertEqual(im.mode, 'RGBA')
        # RGBA is kept
        im = self._webp(make_image_bytes(mode='RGBA'))
        self.assertEqual(im.mode, 'RGBA')

    def test_to_webp_exif_transpose(self):
        exif = Image.Exif()
        # orientation: rotated 90 degrees
        exif[0x0112] = 6
        content = make_image_bytes(size=(40, 20), fmt='JPEG', exif=exif.tobytes())
        im = self._webp(content)
        self.assertEqual(im.size, (20, 40))

    def test_to_webp_animated_gif(self):
        frames = [Image.new('RGB', (10, 10), color=c)
                  for c in ('red', 'green', 'blue')]
        buf = BytesIO()
        frames[0].save(buf, format='GIF', save_all=True,
                       append_images=frames[1:], duration=100, loop=0)
        im = self._webp(buf.getvalue())
        self.assertTrue(getattr(im, 'is_animated', False))
        self.assertEqual(im.n_frames, 3)

    def test_to_webp_failures(self):
        # too many pixels
        with mock.patch('cms.medias.utils.CMS_IMAGE_MAX_PIXELS', 10):
            self.assertIsNone(media_utils.to_webp(BytesIO(make_image_bytes())))
        # corrupted image
        self.assertIsNone(media_utils.to_webp(BytesIO(CORRUPTED_PNG)))


class MediaHooksUnitTest(TemporaryMediaRootMixin, TestCase):

    def _media(self, upload):
        return Media(title='media', description='desc', file=upload)

    def test_set_file_meta(self):
        content = make_image_bytes()
        media = self._media(make_upload(content=content))
        media_hooks.set_file_meta(media)
        self.assertEqual(media.file_type, 'image/png')
        self.assertEqual(media.file_size, len(content))

    def test_webp_image_optimizer(self):
        media = self._media(make_upload(name='my.image.png'))
        self.assertTrue(media_hooks.webp_image_optimizer(media))
        self.assertEqual(media.file.name, 'my.image.webp')
        self.assertEqual(media.file_type, 'image/webp')
        self.assertEqual(media.file_size, media.file._file.size)
        self.assertEqual(media.file._file.content_type, 'image/webp')

    def test_webp_image_optimizer_image_field(self):
        # objects with an 'image' field (eg: categories)
        upload = make_upload(name='cat.png')
        obj = SimpleNamespace(image=SimpleNamespace(_file=upload, name='cat.png'))
        self.assertTrue(media_hooks.webp_image_optimizer(obj))
        self.assertEqual(obj.image.name, 'cat.webp')
        self.assertEqual(obj.file_type, 'image/webp')

    def test_webp_image_optimizer_skipped(self):
        # no uploaded file
        self.assertIsNone(media_hooks.webp_image_optimizer(SimpleNamespace()))
        media = Media(title='media', description='desc', file='medias/a.png')
        self.assertIsNone(media_hooks.webp_image_optimizer(media))
        # not an image
        pdf = SimpleUploadedFile('doc.pdf', PDF_CONTENT,
                                 content_type='application/pdf')
        media = self._media(pdf)
        self.assertIsNone(media_hooks.webp_image_optimizer(media))
        self.assertEqual(media.file.name, 'doc.pdf')

    def test_webp_image_optimizer_conversion_failed(self):
        # the original image is kept
        media = self._media(make_upload(content=CORRUPTED_PNG))
        self.assertIsNone(media_hooks.webp_image_optimizer(media))
        self.assertEqual(media.file.name, 'image.png')
        self.assertEqual(media.file._file.tell(), 0)

    def test_save_media_upload(self):
        media = Media.objects.create(title='media', description='desc',
                                     file=make_upload())
        path = media.file.path
        self.assertTrue(path.startswith(self._media_root))
        self.assertTrue(os.path.exists(path))
        # file is removed after delete
        media_hooks.remove_file(media)
        self.assertFalse(os.path.exists(path))

    def test_remove_replaced_file(self):
        media = Media.objects.create(title='media', description='desc',
                                     file=make_upload(name='first.png'))
        first_path = media.file.path
        self.assertTrue(os.path.exists(first_path))

        # new object: nothing to store
        new_media = self._media(make_upload())
        media_hooks.store_previous_file(new_media)
        self.assertIsNone(getattr(new_media, '_previous_file', None))

        media.file = make_upload(name='second.png')
        media_hooks.store_previous_file(media)
        self.assertEqual(media._previous_file, os.path.relpath(first_path, self._media_root))
        media.save()
        media_hooks.remove_replaced_file(media)
        self.assertIsNone(media._previous_file)
        self.assertFalse(os.path.exists(first_path))
        self.assertTrue(os.path.exists(media.file.path))

        # same file: nothing is removed
        media_hooks.store_previous_file(media)
        media_hooks.remove_replaced_file(media)
        self.assertTrue(os.path.exists(media.file.path))

    def test_remove_file_edge_cases(self):
        # objects without file fields
        self.assertIsNone(media_hooks.remove_file(SimpleNamespace()))
        self.assertIsNone(media_hooks.store_previous_file(SimpleNamespace(pk=1)))
        # empty file name
        storage = mock.MagicMock()
        media_hooks.remove_file(SimpleNamespace(file=SimpleNamespace(name='', storage=storage)))
        storage.exists.assert_not_called()
        # storage errors are logged, not raised
        storage = mock.MagicMock()
        storage.exists.side_effect = OSError('storage down')
        with self.assertLogs('cms.medias.hooks', level='ERROR'):
            media_hooks.remove_file(SimpleNamespace(file=SimpleNamespace(name='a.png',
                                                                         storage=storage)))
        storage.delete.assert_not_called()


class MediaModelsSerializersUnitTest(TemporaryMediaRootMixin, TestCase):

    def test_context_media_path(self):
        self.assertEqual(context_media_path(None, 'a.png'),
                         f'medias/{timezone.now().year}/a.png')

    def test_media_collection(self):
        collection = MediaUnitTest.create_media_collection()
        self.assertEqual(str(collection), 'media1')
        items = collection.get_items()
        self.assertEqual(items.count(), 1)
        item = items.first()
        self.assertEqual(str(item), f'[{collection}] {item.media}')
        superuser = get_user_model().objects.create(username='su',
                                                    is_superuser=True)
        user = get_user_model().objects.create(username='nobody')
        self.assertTrue(item.is_lockable_by(superuser))
        self.assertFalse(item.is_lockable_by(user))
        # inactive items are excluded
        item.is_active = False
        item.save()
        self.assertFalse(collection.get_items().exists())

    def test_media_file_size_properties(self):
        media = Media(title='t', file_size=3 * 1024 * 1024)
        self.assertEqual(media.file_size_kb, 3072)
        self.assertEqual(media.file_size_mb, 3)
        self.assertEqual(str(media), 't None')
        media.file_size = None
        self.assertIsNone(media.file_size_kb)
        self.assertIsNone(media.file_size_mb)

    def test_media_serializer(self):
        media = Media.objects.create(title='media', description='desc',
                                     file=make_upload(content=make_image_bytes(size=(100, 40))))
        data = MediaSerializer(media).data
        self.assertEqual(data['file_dimensions'], '100px*40px')
        self.assertEqual(data['static_path'],
                         reverse('unicms_medias:media-file',
                                 kwargs={'unique_code': media.uuid}))
        self.assertEqual(data['file_size'], media.file_size_kb)
        self.assertIn('object_content_type', data)

        # not an image
        pdf = Media.objects.create(title='pdf', description='desc',
                                   file=SimpleUploadedFile('doc.pdf', PDF_CONTENT,
                                                           content_type='application/pdf'))
        self.assertEqual(MediaSerializer(pdf).data['file_dimensions'], '')

        # file missing on storage
        os.remove(media.file.path)
        media = Media.objects.get(pk=media.pk)
        self.assertEqual(MediaSerializer(media).data['file_dimensions'], '')

    def test_media_collection_item_serializer(self):
        collection = MediaCollection.objects.create(name='coll', description='d')
        media = Media.objects.create(title='media', description='desc',
                                     file=make_upload())
        item = MediaCollectionItem.objects.create(media=media, collection=collection)
        data = MediaCollectionItemSerializer(item).data
        self.assertEqual(data['media']['id'], media.pk)
        self.assertEqual(data['media']['title'], 'media')

        # select options
        self.assertEqual(MediaSelectOptionsSerializer(media).data,
                         {'value': media.pk, 'text': 'media'})
        self.assertEqual(MediaCollectionSelectOptionsSerializer(collection).data,
                         {'value': collection.pk, 'text': 'coll'})

    def test_media_collection_foreign_key(self):
        collection = MediaCollection.objects.create(name='coll', description='d')
        MediaCollection.objects.create(name='other', description='d')
        field = MediaCollectionForeignKey()
        field.bind('collection', MediaCollectionItemSerializer())
        # without request
        self.assertIsNone(field.get_queryset())
        # with request
        request = SimpleNamespace(parser_context={'kwargs': {'collection_id': collection.pk}})
        field = MediaCollectionForeignKey()
        field.bind('collection',
                   MediaCollectionItemSerializer(context={'request': request}))
        self.assertEqual(list(field.get_queryset()), [collection])

    def test_media_collection_item_form(self):
        collection = MediaCollection.objects.create(name='coll', description='d')
        MediaCollection.objects.create(name='other', description='d')
        form = MediaCollectionItemForm(collection_id=collection.pk)
        self.assertEqual(list(form.fields['collection'].queryset), [collection])
        form = MediaCollectionItemForm()
        self.assertEqual(form.fields['collection'].queryset.count(), 2)
