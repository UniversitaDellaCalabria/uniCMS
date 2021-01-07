import logging

from django.http import HttpResponse

from . cache import (get_from_cache, set_to_cache,
                     is_cache_available,
                     is_request_cacheable,
                     is_response_cacheable)
from . utils import detect_user_language


logger = logging.getLogger(__name__)


def detect_language(func_to_decorate):
    """ store_params_in_session as a funcion decorator
    """
    def new_func(*original_args, **original_kwargs):
        request = original_args[0]
        request.LANGUAGE_CODE = detect_user_language(request)
        return func_to_decorate(*original_args, **original_kwargs)
    return new_func


def unicms_cache(func_to_decorate):
    def new_func(*original_args, **original_kwargs):
        request = original_args[0]
        if is_cache_available() and not request.user.is_staff:
            # check if the request would be cached ...
            cacheable = is_request_cacheable(request)
            if cacheable:
                cache_get = get_from_cache(request)
                if cache_get:
                    return HttpResponse(cache_get)

            # otherwise ...
            res = func_to_decorate(*original_args, **original_kwargs)
            if cacheable and is_response_cacheable(res):
                set_to_cache(request, res)
            return res
        else: # pragma: no cover
            return func_to_decorate(*original_args, **original_kwargs)
    return new_func
