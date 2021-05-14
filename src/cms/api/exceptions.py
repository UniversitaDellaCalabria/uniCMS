import logging

from django.utils.translation import gettext_lazy as _

from rest_framework.exceptions import PermissionDenied, ValidationError


logger = logging.getLogger(__name__)


class LoggedPermissionDenied(PermissionDenied):

    def __init__(self, *args, **kwargs):
        logger.warning(f'API {kwargs.get("classname")} {kwargs.get("resource")} permission denied')
        super().__init__(detail=kwargs.get('detail', _('You do not have permission to perform this action.')))


class LoggedValidationException(ValidationError):

    def __init__(self, detail, *args, **kwargs):
        logger.warning(f'API {kwargs.get("classname")} {kwargs.get("resource")}: {detail}')
        super().__init__(detail)
