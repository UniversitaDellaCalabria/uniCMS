import logging
import os

from django.conf import settings
from django.test import TestCase
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
                'description': 'blah blah',
                'is_active': 1}
        for k,v in kwargs.items():
            data[k] = v
        obj = Media.objects.create(**data)
        return obj

    @classmethod
    def create_media_collection(cls, **kwargs):
        data = {'name': 'media1',
                'tags': 'ciao,mamma',
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
                'description': 'blah blah',
                'is_active': 1}

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
                'description': 'blah blah',
                'is_active': 1}

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
                'description': 'blah blah',
                'is_active': 1}

        media = cls.create_media(**data)
        try:
            validate_image_size_ratio(media.file)
        except Exception as e:
            assert isinstance(e, ValidationError)
    
    def tearDown(self):
        match = f'{settings.MEDIA_ROOT}/medias/{timezone.now().year}/eventi_*.*'
        for i in glob(match):
            os.remove(i)
