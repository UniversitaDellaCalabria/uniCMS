import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from cms.carousels.tests import CarouselUnitTest
from cms.contexts.tests import ContextUnitTest
from cms.medias.tests import MediaUnitTest
from cms.menus.tests import MenuUnitTest
from cms.pages.tests import PageUnitTest
from cms.templates.tests import TemplateUnitTest


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


