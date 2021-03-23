import logging

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase
from django.urls import reverse

from cms.carousels.models import Carousel
from cms.carousels.tests import CarouselUnitTest

from cms.contexts.tests import ContextUnitTest

from .. concurrency import (is_lock_cache_available,
                            get_lock_from_cache,
                            set_lock_to_cache)
from .. views.generics import check_locks


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class RedisLockTest(TestCase):

    def setUp(self):
        pass

    def test_redis_lock(self):
        """
        Redis Lock
        """
        req = Client()
        user1 = ContextUnitTest.create_user(username='user1',
                                            is_staff=True,
                                            is_superuser=True)
        user2 = ContextUnitTest.create_user(username='user2',
                                            is_staff=True,
                                            is_superuser=True)
        carousel = CarouselUnitTest.create_carousel()

        check_locks(user=user1, item=carousel, force=True)
        try:
            check_locks(user=user2, item=carousel, force=True)
        except:
            logger.info('Exception raised! right!')
