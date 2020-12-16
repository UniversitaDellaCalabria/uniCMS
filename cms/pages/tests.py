import logging
import urllib

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.test.client import RequestFactory
from django.urls import reverse
from django.utils import timezone

from . forms import *
from . models import *
from . settings import *


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
