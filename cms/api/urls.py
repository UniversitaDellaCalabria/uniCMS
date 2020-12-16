from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import re_path, path, include

from cms.menus.api_views import ApiMenu
from . import api_views

urlpatterns = []

# Public API Resources
urlpatterns += path(f'api/contexts',
                    api_views.ApiContext.as_view(),
                    name='api-contexts'),

# I would have preferred a regexp .. but openapi schema generator ...
# re_path('api/news/by-context/(?P<webpath_id>\d+)/?(?P<category_name>[a-zA-Z0-9]*)?'

urlpatterns += path(f'api/news/by-context/<int:webpath_id>',
                    api_views.ApiPublicationsByContext.as_view(),
                    name='api-news-by-contexts'),
urlpatterns += path(f'api/news/by-context/<int:webpath_id>/<str:catogory_name>',
                    api_views.ApiPublicationsByContext.as_view(),
                    name='api-news-by-contexts-category'),
urlpatterns += path(f'api/menu/<int:menu_id>',
                    ApiMenu.as_view(),
                    name='api-menu'),
urlpatterns += path(f'api/news/detail/<str:slug>',
                    api_views.PublicationDetail.as_view(),
                    name='publication-detail'),
