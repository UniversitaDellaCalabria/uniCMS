import logging


from . utils import detect_user_language, toggle_session_state

logger = logging.getLogger(__name__)


def detect_language_middleware(get_response):
    """
    get_response is a callable ...
    """
    def language_middleware(request):
        detect_user_language(request)
        response = get_response(request)
        return response

    return language_middleware


def show_template_blocks_sections(get_response):
    def blocks_sections_visibility(request):
        if request.user.is_staff:
            arg_name = 'show_template_blocks_sections'
            toggle_session_state(request, arg_name)
            response = get_response(request)
            return response
        else:
            return get_response(request)
    return blocks_sections_visibility


def show_cms_draft_mode(get_response):
    def draft_view_mode(request):
        if request.user.is_staff:
            arg_name = 'draft_view_mode'
            toggle_session_state(request, arg_name)
            response = get_response(request)
            return response
        else:
            return get_response(request)
    return draft_view_mode
