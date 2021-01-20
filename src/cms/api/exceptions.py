import logging

from django.core.exceptions import PermissionDenied


logger = logging.getLogger(__name__)


class LoggedPermissionDenied(PermissionDenied):

    def __init__(self, *args, **kwargs):
        logger.warning(f'API {kwargs.get("classname")} {kwargs.get("resource")} permission denied')
