from django.urls import path

from cms.menus.api_views import ApiMenu

from . views import (carousel, carousel_item, carousel_item_link,
                     carousel_item_link_localization,
                     carousel_item_localization,
                     media, media_collection, media_collection_item,
                     publication, publication_attachment,
                     publication_link, publication_localization,
                     publication_gallery,
                     website, webpath, webpath_publications)


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


eb_prefix = 'api/editorial-board'


urlpatterns += path(f'{eb_prefix}/medias/', media.MediaList.as_view(),
                    name='medias'),
urlpatterns += path(f'{eb_prefix}/medias/<int:pk>/', media.MediaView.as_view(),
                    name='media'),

urlpatterns += path(f'{eb_prefix}/media-collections/',
                    media_collection.MediaCollectionList.as_view(),
                    name='media-collections'),
urlpatterns += path(f'{eb_prefix}/media-collections/<int:pk>/',
                    media_collection.MediaCollectionView.as_view(),
                    name='media-collection'),
urlpatterns += path(f'{eb_prefix}/media-collections/<int:collection_id>/items/',
                    media_collection_item.MediaCollectionItemList.as_view(),
                    name='media-collection-items'),
urlpatterns += path(f'{eb_prefix}/media-collections/<int:collection_id>/items/<int:pk>/',
                    media_collection_item.MediaCollectionItemView.as_view(),
                    name='media-collection-item'),

urlpatterns += path(f'{eb_prefix}/carousels/', carousel.CarouselList.as_view(),
                    name='carousels'),
urlpatterns += path(f'{eb_prefix}/carousels/<int:pk>/',
                    carousel.CarouselView.as_view(),
                    name='carousel'),
urlpatterns += path(f'{eb_prefix}/carousels/<int:carousel_id>/items/',
                    carousel_item.CarouselItemList.as_view(),
                    name='carousel-items'),
urlpatterns += path(f'{eb_prefix}/carousels/<int:carousel_id>/items/<int:pk>/',
                    carousel_item.CarouselItemView.as_view(),
                    name='carousel-item'),
urlpatterns += path(f'{eb_prefix}/carousels/<int:carousel_id>/items/<int:carousel_item_id>/localizations/',
                    carousel_item_localization.CarouselItemLocalizationList.as_view(),
                    name='carousel-item-localizations'),
urlpatterns += path(f'{eb_prefix}/carousels/<int:carousel_id>/items/<int:carousel_item_id>/localizations/<int:pk>/',
                    carousel_item_localization.CarouselItemLocalizationView.as_view(),
                    name='carousel-item-localization'),
urlpatterns += path(f'{eb_prefix}/carousels/<int:carousel_id>/items/<int:carousel_item_id>/links/',
                    carousel_item_link.CarouselItemLinkList.as_view(),
                    name='carousel-item-links'),
urlpatterns += path(f'{eb_prefix}/carousels/<int:carousel_id>/items/<int:carousel_item_id>/links/<int:pk>/',
                    carousel_item_link.CarouselItemLinkView.as_view(),
                    name='carousel-item-link'),
urlpatterns += path(f'{eb_prefix}/carousels/<int:carousel_id>/items/<int:carousel_item_id>/links/<int:carousel_item_link_id>/localizations/',
                    carousel_item_link_localization.CarouselItemLinkLocalizationList.as_view(),
                    name='carousel-item-link-localizations'),
urlpatterns += path(f'{eb_prefix}/carousels/<int:carousel_id>/items/<int:carousel_item_id>/links/<int:carousel_item_link_id>/localizations/<int:pk>/',
                    carousel_item_link_localization.CarouselItemLinkLocalizationView.as_view(),
                    name='carousel-item-link-localization'),

urlpatterns += path(f'{eb_prefix}/sites/',
                    website.EditorWebsiteList.as_view(),
                    name='editorial-board-sites'),
urlpatterns += path(f'{eb_prefix}/sites/<int:site_id>/webpaths/',
                    webpath.EditorWebsiteWebpathList.as_view(),
                    name='editorial-board-site-webpaths'),
urlpatterns += path(f'{eb_prefix}/sites/<int:site_id>/webpaths/<int:pk>/',
                    webpath.EditorWebsiteWebpathView.as_view(),
                    name='editorial-board-site-webpath'),

# publication_contexts with publication data
urlpatterns += path(f'{eb_prefix}/sites/<int:site_id>/webpaths/<int:webpath_id>/publications/',
                    webpath_publications.EditorWebpathPublicationList.as_view(),
                    name='editorial-board-site-webpath-publications'),
urlpatterns += path(f'{eb_prefix}/sites/<int:site_id>/webpaths/<int:webpath_id>/publications/<int:pk>/',
                    webpath_publications.EditorWebpathPublicationView.as_view(),
                    name='editorial-board-site-webpath-publication'),
# end publication_contexts with publication data

urlpatterns += path(f'{eb_prefix}/sites/<int:site_id>/webpaths/<int:webpath_id>/publication-contexts/',
                    webpath_publications.EditorWebpathPublicationContextList.as_view(),
                    name='editorial-board-site-webpath-publication-contexts'),
urlpatterns += path(f'{eb_prefix}/sites/<int:site_id>/webpaths/<int:webpath_id>/publication-contexts/<int:pk>/',
                    webpath_publications.EditorWebpathPublicationContextView.as_view(),
                    name='editorial-board-site-webpath-publication-context'),

urlpatterns += path(f'{eb_prefix}/publications/',
                    publication.PublicationList.as_view(),
                    name='editorial-board-publications'),
urlpatterns += path(f'{eb_prefix}/publications/<int:pk>/',
                    publication.PublicationView.as_view(),
                    name='editorial-board-publication'),
urlpatterns += path(f'{eb_prefix}/publications/<int:publication_id>/attachments/',
                    publication_attachment.PublicationAttachmentList.as_view(),
                    name='editorial-board-publication-attachments'),
urlpatterns += path(f'{eb_prefix}/publications/<int:publication_id>/attachments/<int:pk>/',
                    publication_attachment.PublicationAttachmentView.as_view(),
                    name='editorial-board-publication-attachment'),
urlpatterns += path(f'{eb_prefix}/publications/<int:publication_id>/links/',
                    publication_link.PublicationLinkList.as_view(),
                    name='editorial-board-publication-links'),
urlpatterns += path(f'{eb_prefix}/publications/<int:publication_id>/links/<int:pk>/',
                    publication_link.PublicationLinkView.as_view(),
                    name='editorial-board-publication-link'),
urlpatterns += path(f'{eb_prefix}/publications/<int:publication_id>/galleries/',
                    publication_gallery.PublicationGalleryList.as_view(),
                    name='editorial-board-publication-galleries'),
urlpatterns += path(f'{eb_prefix}/publications/<int:publication_id>/galleries/<int:pk>/',
                    publication_gallery.PublicationGalleryView.as_view(),
                    name='editorial-board-publication-gallery'),
urlpatterns += path(f'{eb_prefix}/publications/<int:publication_id>/localizations/',
                    publication_localization.PublicationLocalizationList.as_view(),
                    name='editorial-board-publication-localizations'),
urlpatterns += path(f'{eb_prefix}/publications/<int:publication_id>/localizations/<int:pk>/',
                    publication_localization.PublicationLocalizationView.as_view(),
                    name='editorial-board-publication-localization'),


# urlpatterns += path(f'{eb_prefix}/site/<int:site_id>/page/list/',
# EditorWebsitePages.as_view(),
# name='editorial-board-site-page-list'),

# urlpatterns += path(f'{eb_prefix}/site/<int:site_id>/page/<int:page_id>/view/',
# EditorWebsitePage.as_view(),
# name='editorial-board-site-page-view'),
