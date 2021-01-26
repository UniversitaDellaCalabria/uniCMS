from django.urls import path

from cms.menus.api_views import ApiMenu, ApiMenuId

from . views import (carousel, carousel_item, carousel_item_link,
                     carousel_item_link_localization,
                     carousel_item_localization,
                     media, media_collection, media_collection_item,
                     publication, publication_attachment,
                     publication_link, publication_localization,
                     publication_gallery, publication_block,
                     publication_related,
                     website, webpath, webpath_pub_context,
                     page, page_block, page_carousel, page_link,
                     page_media, page_menu, page_publication,
                     page_related, page_localization)


urlpatterns = []

# Public API Resources
urlpatterns += path('api/contexts', publication.ApiContext.as_view(), name='api-contexts'),

# I would have preferred a regexp .. but openapi schema generator ...
# re_path('api/news/by-context/(?P<webpath_id>\d+)/?(?P<category_name>[a-zA-Z0-9]*)?'

urlpatterns += path('api/news/by-context/<int:webpath_id>',
                    publication.ApiPublicationsByContext.as_view(), name='api-news-by-contexts'),
urlpatterns += path('api/news/by-context/<int:webpath_id>/<str:category_name>',
                    publication.ApiPublicationsByContextCategory.as_view(),
                    name='api-news-by-contexts-category'),
urlpatterns += path('api/news/view/<str:slug>',
                    publication.PublicationDetail.as_view(), name='publication-detail'),

urlpatterns += path('api/menu/<int:menu_id>', ApiMenuId.as_view(), name='api-menu'),
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

# pages
urlpatterns += path(f'{eb_prefix}/sites/<int:site_id>/webpaths/<int:webpath_id>/pages/',
                    page.EditorWebpathPageList.as_view(),
                    name='editorial-board-site-webpath-pages'),
urlpatterns += path(f'{eb_prefix}/sites/<int:site_id>/webpaths/<int:webpath_id>/pages/<int:pk>/',
                    page.EditorWebpathPageView.as_view(),
                    name='editorial-board-site-webpath-page'),
urlpatterns += path(f'{eb_prefix}/sites/<int:site_id>/webpaths/<int:webpath_id>/pages/<int:pk>/change-status/',
                    page.PageChangeStateView.as_view(),
                    name='editorial-board-site-webpath-page-change-status'),
urlpatterns += path(f'{eb_prefix}/sites/<int:site_id>/webpaths/<int:webpath_id>/pages/<int:pk>/change-publication-status/',
                    page.PageChangePublicationStatusView.as_view(),
                    name='editorial-board-site-webpath-page-change-publication-status'),

# page blocks
urlpatterns += path(f'{eb_prefix}/sites/<int:site_id>/webpaths/<int:webpath_id>/pages/<int:page_id>/blocks/',
                    page_block.PageBlockList.as_view(),
                    name='editorial-board-site-webpath-page-blocks'),
urlpatterns += path(f'{eb_prefix}/sites/<int:site_id>/webpaths/<int:webpath_id>/pages/<int:page_id>/blocks/<int:pk>/',
                    page_block.PageBlockView.as_view(),
                    name='editorial-board-site-webpath-page-block'),

# page links
urlpatterns += path(f'{eb_prefix}/sites/<int:site_id>/webpaths/<int:webpath_id>/pages/<int:page_id>/links/',
                    page_link.PageLinkList.as_view(),
                    name='editorial-board-site-webpath-page-links'),
urlpatterns += path(f'{eb_prefix}/sites/<int:site_id>/webpaths/<int:webpath_id>/pages/<int:page_id>/links/<int:pk>/',
                    page_link.PageLinkView.as_view(),
                    name='editorial-board-site-webpath-page-link'),

# page carousels
urlpatterns += path(f'{eb_prefix}/sites/<int:site_id>/webpaths/<int:webpath_id>/pages/<int:page_id>/carousels/',
                    page_carousel.PageCarouselList.as_view(),
                    name='editorial-board-site-webpath-page-carousels'),
urlpatterns += path(f'{eb_prefix}/sites/<int:site_id>/webpaths/<int:webpath_id>/pages/<int:page_id>/carousels/<int:pk>/',
                    page_carousel.PageCarouselView.as_view(),
                    name='editorial-board-site-webpath-page-carousel'),

# page localizations
urlpatterns += path(f'{eb_prefix}/sites/<int:site_id>/webpaths/<int:webpath_id>/pages/<int:page_id>/localizations/',
                    page_localization.PageLocalizationList.as_view(),
                    name='editorial-board-site-webpath-page-localizations'),
urlpatterns += path(f'{eb_prefix}/sites/<int:site_id>/webpaths/<int:webpath_id>/pages/<int:page_id>/localizations/<int:pk>/',
                    page_localization.PageLocalizationView.as_view(),
                    name='editorial-board-site-webpath-page-localization'),

# page medias
urlpatterns += path(f'{eb_prefix}/sites/<int:site_id>/webpaths/<int:webpath_id>/pages/<int:page_id>/medias/',
                    page_media.PageMediaList.as_view(),
                    name='editorial-board-site-webpath-page-medias'),
urlpatterns += path(f'{eb_prefix}/sites/<int:site_id>/webpaths/<int:webpath_id>/pages/<int:page_id>/medias/<int:pk>/',
                    page_media.PageMediaView.as_view(),
                    name='editorial-board-site-webpath-page-media'),

# page menus
urlpatterns += path(f'{eb_prefix}/sites/<int:site_id>/webpaths/<int:webpath_id>/pages/<int:page_id>/menus/',
                    page_menu.PageMenuList.as_view(),
                    name='editorial-board-site-webpath-page-menus'),
urlpatterns += path(f'{eb_prefix}/sites/<int:site_id>/webpaths/<int:webpath_id>/pages/<int:page_id>/menus/<int:pk>/',
                    page_menu.PageMenuView.as_view(),
                    name='editorial-board-site-webpath-page-menu'),

# page publications
urlpatterns += path(f'{eb_prefix}/sites/<int:site_id>/webpaths/<int:webpath_id>/pages/<int:page_id>/publications/',
                    page_publication.PagePublicationList.as_view(),
                    name='editorial-board-site-webpath-page-publications'),
urlpatterns += path(f'{eb_prefix}/sites/<int:site_id>/webpaths/<int:webpath_id>/pages/<int:page_id>/publications/<int:pk>/',
                    page_publication.PagePublicationView.as_view(),
                    name='editorial-board-site-webpath-page-publication'),

# page related
urlpatterns += path(f'{eb_prefix}/sites/<int:site_id>/webpaths/<int:webpath_id>/pages/<int:page_id>/related/',
                    page_related.PageRelatedList.as_view(),
                    name='editorial-board-site-webpath-page-related-list'),
urlpatterns += path(f'{eb_prefix}/sites/<int:site_id>/webpaths/<int:webpath_id>/pages/<int:page_id>/related/<int:pk>/',
                    page_related.PageRelatedView.as_view(),
                    name='editorial-board-site-webpath-page-related'),

# publication-contexts
urlpatterns += path(f'{eb_prefix}/sites/<int:site_id>/webpaths/<int:webpath_id>/publication-contexts/',
                    webpath_pub_context.EditorWebpathPublicationContextList.as_view(),
                    name='editorial-board-site-webpath-publication-contexts'),
urlpatterns += path(f'{eb_prefix}/sites/<int:site_id>/webpaths/<int:webpath_id>/publication-contexts/<int:pk>/',
                    webpath_pub_context.EditorWebpathPublicationContextView.as_view(),
                    name='editorial-board-site-webpath-publication-context'),

# publications
urlpatterns += path(f'{eb_prefix}/publications/',
                    publication.PublicationList.as_view(),
                    name='editorial-board-publications'),
urlpatterns += path(f'{eb_prefix}/publications/<int:pk>/',
                    publication.PublicationView.as_view(),
                    name='editorial-board-publication'),
urlpatterns += path(f'{eb_prefix}/publications/<int:pk>/change-status/',
                    publication.PublicationChangeStateView.as_view(),
                    name='editorial-board-publication-change-status'),

# publication attachments
urlpatterns += path(f'{eb_prefix}/publications/<int:publication_id>/attachments/',
                    publication_attachment.PublicationAttachmentList.as_view(),
                    name='editorial-board-publication-attachments'),
urlpatterns += path(f'{eb_prefix}/publications/<int:publication_id>/attachments/<int:pk>/',
                    publication_attachment.PublicationAttachmentView.as_view(),
                    name='editorial-board-publication-attachment'),

# publication blocks
urlpatterns += path(f'{eb_prefix}/publications/<int:publication_id>/blocks/',
                    publication_block.PublicationBlockList.as_view(),
                    name='editorial-board-publication-blocks'),
urlpatterns += path(f'{eb_prefix}/publications/<int:publication_id>/blocks/<int:pk>/',
                    publication_block.PublicationBlockView.as_view(),
                    name='editorial-board-publication-block'),

# publication links
urlpatterns += path(f'{eb_prefix}/publications/<int:publication_id>/links/',
                    publication_link.PublicationLinkList.as_view(),
                    name='editorial-board-publication-links'),
urlpatterns += path(f'{eb_prefix}/publications/<int:publication_id>/links/<int:pk>/',
                    publication_link.PublicationLinkView.as_view(),
                    name='editorial-board-publication-link'),

# publication galleries
urlpatterns += path(f'{eb_prefix}/publications/<int:publication_id>/galleries/',
                    publication_gallery.PublicationGalleryList.as_view(),
                    name='editorial-board-publication-galleries'),
urlpatterns += path(f'{eb_prefix}/publications/<int:publication_id>/galleries/<int:pk>/',
                    publication_gallery.PublicationGalleryView.as_view(),
                    name='editorial-board-publication-gallery'),

# publication localizations
urlpatterns += path(f'{eb_prefix}/publications/<int:publication_id>/localizations/',
                    publication_localization.PublicationLocalizationList.as_view(),
                    name='editorial-board-publication-localizations'),
urlpatterns += path(f'{eb_prefix}/publications/<int:publication_id>/localizations/<int:pk>/',
                    publication_localization.PublicationLocalizationView.as_view(),
                    name='editorial-board-publication-localization'),

# publication related
urlpatterns += path(f'{eb_prefix}/publications/<int:publication_id>/related/',
                    publication_related.PublicationRelatedList.as_view(),
                    name='editorial-board-publication-related-list'),
urlpatterns += path(f'{eb_prefix}/publications/<int:publication_id>/related/<int:pk>/',
                    publication_related.PublicationRelatedView.as_view(),
                    name='editorial-board-publication-related'),
