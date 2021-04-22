import logging

from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)


class LoggedPermissionDenied(PermissionDenied):

    def __init__(self, *args, **kwargs):
        logger.warning(f'API {kwargs.get("classname")} {kwargs.get("resource")} permission denied')


class LoggedValidationException(ValidationError):

    def __init__(self, detail, *args, **kwargs):
        logger.warning(f'API {kwargs.get("classname")} {kwargs.get("resource")}: {detail}')
        super().__init__(detail)
