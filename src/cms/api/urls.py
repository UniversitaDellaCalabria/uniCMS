from django.urls import path

from cms.menus.api_views import ApiMenu

from . views import (carousel, carousel_item, carousel_item_link,
                     carousel_item_link_localization,
                     carousel_item_localization,
                     media, media_collection, media_collection_item,
                     page, publication,
                     website, webpath)


urlpatterns = []

# Public API Resources
urlpatterns += path('api/contexts', publication.ApiContext.as_view(), name='api-contexts'),

# I would have preferred a regexp .. but openapi schema generator ...
# re_path('api/news/by-context/(?P<webpath_id>\d+)/?(?P<category_name>[a-zA-Z0-9]*)?'

urlpatterns += path('api/news/by-context/<int:webpath_id>', publication.ApiPublicationsByContext.as_view(), name='api-news-by-contexts'),
urlpatterns += path('api/news/by-context/<int:webpath_id>/<str:category_name>',
                    publication.ApiPublicationsByContext.as_view(), name='api-news-by-contexts-category'),
urlpatterns += path('api/news/view/<str:slug>', publication.PublicationDetail.as_view(), name='publication-detail'),

urlpatterns += path('api/menu/<int:menu_id>', ApiMenu.as_view(), name='api-menu'),
urlpatterns += path('api/menu', ApiMenu.as_view(), name='api-menu-post'),

urlpatterns += path('api/editorial-board/sites/', website.EditorWebsiteList.as_view(), name='editorial-board-sites'),
urlpatterns += path('api/editorial-board/sites/<int:site_id>/webpaths/',
                    webpath.EditorWebsiteWebpathList.as_view(), name='editorial-board-site-webpaths'),
urlpatterns += path('api/editorial-board/sites/<int:site_id>/webpaths/<int:pk>/',
                    webpath.EditorWebsiteWebpathView.as_view(), name='editorial-board-site-webpath'),

urlpatterns += path('api/medias/', media.MediaList.as_view(), name='medias'),
urlpatterns += path('api/medias/<int:pk>/', media.MediaView.as_view(), name='media'),

urlpatterns += path('api/media-collections/', media_collection.MediaCollectionList.as_view(), name='media-collections'),
urlpatterns += path('api/media-collections/<int:pk>/', media_collection.MediaCollectionView.as_view(), name='media-collection'),
urlpatterns += path('api/media-collections/<int:collection_id>/items/',
                    media_collection_item.MediaCollectionItemList.as_view(), name='media-collection-items'),
urlpatterns += path('api/media-collections/<int:collection_id>/items/<int:pk>/',
                    media_collection_item.MediaCollectionItemView.as_view(), name='media-collection-item'),

urlpatterns += path('api/carousels/', carousel.CarouselList.as_view(), name='carousels'),
urlpatterns += path('api/carousels/<int:pk>/', carousel.CarouselView.as_view(), name='carousel'),
urlpatterns += path('api/carousels/<int:carousel_id>/items/', carousel_item.CarouselItemList.as_view(), name='carousel-items'),
urlpatterns += path('api/carousels/<int:carousel_id>/items/<int:pk>/', carousel_item.CarouselItemView.as_view(), name='carousel-item'),
urlpatterns += path('api/carousels/<int:carousel_id>/items/<int:carousel_item_id>/localizations/',
                    carousel_item_localization.CarouselItemLocalizationList.as_view(), name='carousel-item-localizations'),
urlpatterns += path('api/carousels/<int:carousel_id>/items/<int:carousel_item_id>/localizations/<int:pk>/',
                    carousel_item_localization.CarouselItemLocalizationView.as_view(), name='carousel-item-localization'),
urlpatterns += path('api/carousels/<int:carousel_id>/items/<int:carousel_item_id>/links/',
                    carousel_item_link.CarouselItemLinkList.as_view(), name='carousel-item-links'),
urlpatterns += path('api/carousels/<int:carousel_id>/items/<int:carousel_item_id>/links/<int:pk>/',
                    carousel_item_link.CarouselItemLinkView.as_view(), name='carousel-item-link'),
urlpatterns += path('api/carousels/<int:carousel_id>/items/<int:carousel_item_id>/links/<int:carousel_item_link_id>/localizations/',
                    carousel_item_link_localization.CarouselItemLinkLocalizationList.as_view(), name='carousel-item-link-localizations'),
urlpatterns += path('api/carousels/<int:carousel_id>/items/<int:carousel_item_id>/links/<int:carousel_item_link_id>/localizations/<int:pk>/',
                    carousel_item_link_localization.CarouselItemLinkLocalizationView.as_view(), name='carousel-item-link-localization'),


# urlpatterns += path('api/editorial-board/site/<int:site_id>/page/list/',
# EditorWebsitePages.as_view(),
# name='editorial-board-site-page-list'),

# urlpatterns += path('api/editorial-board/site/<int:site_id>/page/<int:page_id>/view/',
# EditorWebsitePage.as_view(),
# name='editorial-board-site-page-view'),
