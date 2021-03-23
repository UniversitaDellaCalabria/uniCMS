import logging

from django.test import TestCase

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
        except: # pragma: no cover
            logger.info('Exception raised! right!')
