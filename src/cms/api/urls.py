from django.urls import path

from cms.menus.api_views import ApiMenu
from . import api_views

urlpatterns = []

# Public API Resources
urlpatterns += path('api/contexts', api_views.ApiContext.as_view(), name='api-contexts'),

# I would have preferred a regexp .. but openapi schema generator ...
# re_path('api/news/by-context/(?P<webpath_id>\d+)/?(?P<category_name>[a-zA-Z0-9]*)?'

urlpatterns += path('api/news/by-context/<int:webpath_id>', api_views.ApiPublicationsByContext.as_view(), name='api-news-by-contexts'),
urlpatterns += path('api/news/by-context/<int:webpath_id>/<str:category_name>', api_views.ApiPublicationsByContext.as_view(), name='api-news-by-contexts-category'),
urlpatterns += path('api/news/view/<str:slug>', api_views.PublicationDetail.as_view(), name='publication-detail'),

urlpatterns += path('api/menu/<int:menu_id>', ApiMenu.as_view(), name='api-menu'),
urlpatterns += path('api/menu', ApiMenu.as_view(), name='api-menu-post'),

urlpatterns += path('api/editorial-board/site/list/', api_views.EditorWebsiteList.as_view(), name='editorial-board-site-list'),
urlpatterns += path('api/editorial-board/site/<int:site_id>/webpath/list/', api_views.EditorWebsiteWebpathList.as_view(), name='editorial-board-site-webpath-list'),
urlpatterns += path('api/editorial-board/site/<int:site_id>/webpath/<int:pk>/view/', api_views.EditorWebsiteWebpathView.as_view(), name='editorial-board-site-webpath-view'),

urlpatterns += path('api/medias/', api_views.MediaList.as_view(), name='media-list'),
urlpatterns += path('api/medias/<int:pk>/', api_views.MediaView.as_view(), name='media-view'),

urlpatterns += path('api/carousels/', api_views.CarouselList.as_view(),  name='carousels'),
urlpatterns += path('api/carousels/<int:pk>/', api_views.CarouselView.as_view(), name='carousel'),
urlpatterns += path('api/carousels/<int:carousel_id>/items/', api_views.CarouselItemList.as_view(), name='carousel-items'),
urlpatterns += path('api/carousels/<int:carousel_id>/items/<int:pk>/', api_views.CarouselItemView.as_view(), name='carousel-item'),
urlpatterns += path('api/carousels/<int:carousel_id>/items/<int:carousel_item_id>/localizations/', api_views.CarouselItemLocalizationList.as_view(), name='carousel-item-localizations'),
urlpatterns += path('api/carousels/<int:carousel_id>/items/<int:carousel_item_id>/localizations/<int:pk>/', api_views.CarouselItemLocalizationView.as_view(), name='carousel-item-localization'),
urlpatterns += path('api/carousels/<int:carousel_id>/items/<int:carousel_item_id>/links/', api_views.CarouselItemLinkList.as_view(), name='carousel-item-links'),
urlpatterns += path('api/carousels/<int:carousel_id>/items/<int:carousel_item_id>/links/<int:pk>/', api_views.CarouselItemLinkView.as_view(), name='carousel-item-link'),
urlpatterns += path('api/carousels/<int:carousel_id>/items/<int:carousel_item_id>/links/<int:carousel_item_link_id>/localizations/', api_views.CarouselItemLinkLocalizationList.as_view(), name='carousel-item-link-localizations'),
urlpatterns += path('api/carousels/<int:carousel_id>/items/<int:carousel_item_id>/links/<int:carousel_item_link_id>/localizations/<int:pk>/', api_views.CarouselItemLinkLocalizationView.as_view(), name='carousel-item-link-localization'),




# urlpatterns += path('api/editorial-board/site/<int:site_id>/page/list/',
# api_views.EditorWebsitePages.as_view(),
# name='editorial-board-site-page-list'),

# urlpatterns += path('api/editorial-board/site/<int:site_id>/page/<int:page_id>/view/',
# api_views.EditorWebsitePage.as_view(),
# name='editorial-board-site-page-view'),
