import logging

from django.utils.translation import gettext_lazy as _

from rest_framework.exceptions import APIException, PermissionDenied, ValidationError


logger = logging.getLogger(__name__)


class UniCMSAPIException(APIException):
    status_code = 500

    def __init__(self, *args, **kwargs):
        original_exception = kwargs.get('original_exception')
        detail = str(original_exception)
        super().__init__(detail)
        if hasattr(original_exception, "status_code"):
            self.status_code = original_exception.status_code

            
class LoggedPermissionDenied(PermissionDenied):

    def __init__(self, *args, **kwargs):
        logger.warning(f'API {kwargs.get("classname")} {kwargs.get("resource")} permission denied')
        super().__init__(detail=kwargs.get('detail', _('You do not have permission to perform this action.')))


class LoggedValidationException(ValidationError):

    def __init__(self, detail, *args, **kwargs):
        logger.warning(f'API {kwargs.get("classname")} {kwargs.get("resource")}: {detail}')
        super().__init__(detail)
