from django.urls import path

from . views import (carousel, carousel_item, carousel_item_link,
                     carousel_item_link_localization,
                     carousel_item_localization,
                     media, media_collection, media_collection_item,
                     publication, publication_attachment,
                     publication_link, publication_localization,
                     publication_media_collection, publication_block,
                     publication_related,
                     website, webpath, webpath_pub_context,
                     page, page_block, page_carousel, page_link,
                     page_media, page_media_collection,
                     page_menu, page_publication,
                     page_heading, page_heading_localization,
                     page_related, page_localization, page_template,
                     template_block, menu, menu_item,
                     menu_item_localization, locks, users)


urlpatterns = []

# Public API Resources
urlpatterns += path('api/contexts', publication.ApiContext.as_view(), name='api-contexts'),

# I would have preferred a regexp .. but openapi schema generator ...
# re_path('api/news/by-context/(?P<webpath_id>\d+)/?(?P<category_name>[a-zA-Z0-9]*)?'

urlpatterns += path('api/news/by-context/<int:webpath_id>', publication.ApiPublicationsByContext.as_view(), name='api-news-by-contexts'),
urlpatterns += path('api/news/by-context/<int:webpath_id>/<str:category_name>',
                    publication.ApiPublicationsByContextCategory.as_view(), name='api-news-by-contexts-category'),
urlpatterns += path('api/news/view/<str:slug>', publication.PublicationDetail.as_view(), name='publication-detail'),

urlpatterns += path('api/menu/<int:menu_id>', menu.ApiMenuId.as_view(), name='api-menu'),
urlpatterns += path('api/menu', menu.ApiMenu.as_view(), name='api-menu-post'),

# --------------EDITORIAL BOARD URLs------------------------ #

# editorial board prefix
eb_prefix = 'api/editorial-board'

# medias
m_prefix = f'{eb_prefix}/medias'
urlpatterns += path(f'{m_prefix}/', media.MediaList.as_view(), name='medias'),
urlpatterns += path(f'{m_prefix}/<int:pk>/', media.MediaView.as_view(), name='media'),
urlpatterns += path(f'{m_prefix}/<int:pk>/logs/', media.MediaLogsView.as_view(), name='media-logs'),
urlpatterns += path(f'{m_prefix}/form/', media.MediaFormView.as_view(), name='media-form'),
urlpatterns += path(f'{m_prefix}/options/', media.MediaOptionList.as_view(), name='media-options'),
urlpatterns += path(f'{m_prefix}/options/<int:pk>/', media.MediaOptionView.as_view(), name='media-option'),

# media collections
mc_prefix = f'{eb_prefix}/media-collections'
urlpatterns += path(f'{mc_prefix}/', media_collection.MediaCollectionList.as_view(), name='media-collections'),
urlpatterns += path(f'{mc_prefix}/<int:pk>/', media_collection.MediaCollectionView.as_view(), name='media-collection'),
urlpatterns += path(f'{mc_prefix}/<int:pk>/logs/', media_collection.MediaCollectionLogsView.as_view(), name='media-collection-logs'),
urlpatterns += path(f'{mc_prefix}/form/', media_collection.MediaCollectionFormView.as_view(), name='media-collection-form'),
urlpatterns += path(f'{mc_prefix}/options/', media_collection.MediaCollectionOptionList.as_view(), name='media-collection-options'),
urlpatterns += path(f'{mc_prefix}/options/<int:pk>/', media_collection.MediaCollectionOptionView.as_view(), name='media-collection-option'),

# media collection items
mci_prefix = f'{mc_prefix}/<int:collection_id>/items'
urlpatterns += path(f'{mci_prefix}/', media_collection_item.MediaCollectionItemList.as_view(), name='media-collection-items'),
urlpatterns += path(f'{mci_prefix}/<int:pk>/', media_collection_item.MediaCollectionItemView.as_view(), name='media-collection-item'),
urlpatterns += path(f'{mci_prefix}/<int:pk>/logs/', media_collection_item.MediaCollectionItemLogsView.as_view(), name='media-collection-item-logs'),
urlpatterns += path(f'{mci_prefix}/form/', media_collection_item.MediaCollectionItemFormView.as_view(), name='media-collection-item-form'),

# carousels
c_prefix = f'{eb_prefix}/carousels'
urlpatterns += path(f'{c_prefix}/', carousel.CarouselList.as_view(), name='carousels'),
urlpatterns += path(f'{c_prefix}/<int:pk>/', carousel.CarouselView.as_view(), name='carousel'),
urlpatterns += path(f'{c_prefix}/<int:pk>/logs/', carousel.CarouselLogsView.as_view(), name='carousel-logs'),
urlpatterns += path(f'{c_prefix}/form/', carousel.CarouselFormView.as_view(), name='carousel-form'),
urlpatterns += path(f'{c_prefix}/options/', carousel.CarouselOptionList.as_view(), name='carousel-options'),
urlpatterns += path(f'{c_prefix}/options/<int:pk>/', carousel.CarouselOptionView.as_view(), name='carousel-option'),

# carousel items
ci_prefix = f'{c_prefix}/<int:carousel_id>/items'
urlpatterns += path(f'{ci_prefix}/', carousel_item.CarouselItemList.as_view(), name='carousel-items'),
urlpatterns += path(f'{ci_prefix}/<int:pk>/', carousel_item.CarouselItemView.as_view(), name='carousel-item'),
urlpatterns += path(f'{ci_prefix}/<int:pk>/logs/', carousel_item.CarouselItemLogsView.as_view(), name='carousel-item-logs'),
urlpatterns += path(f'{ci_prefix}/form/', carousel_item.CarouselItemFormView.as_view(), name='carousel-item-form'),
urlpatterns += path(f'{c_prefix}/items/form/', carousel_item.CarouselItemGenericFormView.as_view(), name='carousel-item-form-generic'),

# carousel item localizations
cilo_prefix = f'{ci_prefix}/<int:carousel_item_id>/localizations'
urlpatterns += path(f'{cilo_prefix}/', carousel_item_localization.CarouselItemLocalizationList.as_view(), name='carousel-item-localizations'),
urlpatterns += path(f'{cilo_prefix}/<int:pk>/', carousel_item_localization.CarouselItemLocalizationView.as_view(),
                    name='carousel-item-localization'),
urlpatterns += path(f'{cilo_prefix}/<int:pk>/logs/', carousel_item_localization.CarouselItemLocalizationLogsView.as_view(),
                    name='carousel-item-localization-logs'),
urlpatterns += path(f'{cilo_prefix}/form/', carousel_item_localization.CarouselItemLocalizationFormView.as_view(),
                    name='carousel-item-localization-form'),

# carousel item links
cili_prefix = f'{ci_prefix}/<int:carousel_item_id>/links'
urlpatterns += path(f'{cili_prefix}/', carousel_item_link.CarouselItemLinkList.as_view(), name='carousel-item-links'),
urlpatterns += path(f'{cili_prefix}/<int:pk>/', carousel_item_link.CarouselItemLinkView.as_view(), name='carousel-item-link'),
urlpatterns += path(f'{cili_prefix}/<int:pk>/logs/', carousel_item_link.CarouselItemLinkLogsView.as_view(), name='carousel-item-link-logs'),
urlpatterns += path(f'{cili_prefix}/form/', carousel_item_link.CarouselItemLinksFormView.as_view(), name='carousel-item-link-form'),

# carousel item link localizations
cilil_prefix = f'{cili_prefix}/<int:carousel_item_link_id>/localizations'
urlpatterns += path(f'{cilil_prefix}/', carousel_item_link_localization.CarouselItemLinkLocalizationList.as_view(),
                    name='carousel-item-link-localizations'),
urlpatterns += path(f'{cilil_prefix}/<int:pk>/', carousel_item_link_localization.CarouselItemLinkLocalizationView.as_view(),
                    name='carousel-item-link-localization'),
urlpatterns += path(f'{cilil_prefix}/<int:pk>/logs/',
                    carousel_item_link_localization.CarouselItemLinkLocalizationLogsView.as_view(), name='carousel-item-link-localization-logs'),
urlpatterns += path(f'{cilil_prefix}/form/', carousel_item_link_localization.CarouselItemLinkLocalizationFormView.as_view(),
                    name='carousel-item-link-localization-form'),

# websites
urlpatterns += path(f'{eb_prefix}/sites/', website.EditorWebsiteList.as_view(), name='editorial-board-sites'),
urlpatterns += path(f'{eb_prefix}/sites/<int:pk>/', website.EditorWebsiteView.as_view(), name='editorial-board-site'),

# webpaths
w_prefix = f'{eb_prefix}/sites/<int:site_id>/webpaths'
urlpatterns += path(f'{w_prefix}/', webpath.WebpathList.as_view(), name='editorial-board-site-webpaths'),
urlpatterns += path(f'{w_prefix}/<int:pk>/', webpath.WebpathView.as_view(), name='editorial-board-site-webpath'),
urlpatterns += path(f'{w_prefix}/<int:pk>/logs/', webpath.WebpathLogsView.as_view(), name='editorial-board-site-webpath-logs'),
urlpatterns += path(f'{w_prefix}/form/', webpath.WebpathFormView.as_view(), name='editorial-board-site-webpath-form'),
urlpatterns += path(f'{eb_prefix}/sites/webpaths/', webpath.WebpathAllList.as_view(), name='webpath-all'),
urlpatterns += path(f'{eb_prefix}/sites/webpaths/options/', webpath.WebpathAllOptionList.as_view(), name='webpath-all-options'),
urlpatterns += path(f'{w_prefix}/options/', webpath.WebpathOptionList.as_view(), name='webpath-options'),
urlpatterns += path(f'{w_prefix}/options/<int:pk>/', webpath.WebpathOptionView.as_view(), name='webpath-option'),
urlpatterns += path(f'{w_prefix}/<int:pk>/clone/', webpath.WebpathCloneView.as_view(), name='editorial-board-site-webpath-clone'),
urlpatterns += path(f'{w_prefix}/<int:pk>/clone/form/', webpath.WebpathCloneFormView.as_view(), name='editorial-board-site-webpath-clone-form'),

# pages
pa_prefix = f'{w_prefix}/<int:webpath_id>/pages'
urlpatterns += path(f'{pa_prefix}/', page.PageList.as_view(), name='editorial-board-site-webpath-pages'),
urlpatterns += path(f'{pa_prefix}/<int:pk>/', page.PageView.as_view(), name='editorial-board-site-webpath-page'),
urlpatterns += path(f'{pa_prefix}/<int:pk>/logs/', page.PageLogsView.as_view(), name='editorial-board-site-webpath-page-logs'),
urlpatterns += path(f'{pa_prefix}/<int:pk>/change-status/', page.PageChangeStateView.as_view(),
                    name='editorial-board-site-webpath-page-change-status'),
urlpatterns += path(f'{pa_prefix}/<int:pk>/change-publication-status/', page.PageChangePublicationStatusView.as_view(),
                    name='editorial-board-site-webpath-page-change-publication-status'),
urlpatterns += path(f'{pa_prefix}/form/', page.PageFormView.as_view(), name='editorial-board-site-webpath-page-form'),
urlpatterns += path(f'{w_prefix}/pages/form/', page.PageGenericFormView.as_view(), name='editorial-board-site-webpath-page-form-generic'),
urlpatterns += path(f'{pa_prefix}/<int:pk>/copy-as-draft/', page.PageCopyAsDraftView.as_view(),
                    name='editorial-board-site-webpath-page-copy-as-draft'),
urlpatterns += path(f'{eb_prefix}/sites/webpaths/pages/', page.PageAllList.as_view(), name='all-pages'),

# page blocks
pab_prefix = f'{pa_prefix}/<int:page_id>/blocks'
urlpatterns += path(f'{pab_prefix}/', page_block.PageBlockList.as_view(), name='editorial-board-site-webpath-page-blocks'),
urlpatterns += path(f'{pab_prefix}/<int:pk>/', page_block.PageBlockView.as_view(), name='editorial-board-site-webpath-page-block'),
urlpatterns += path(f'{pab_prefix}/<int:pk>/logs/', page_block.PageBlockLogsView.as_view(), name='editorial-board-site-webpath-page-block-logs'),
urlpatterns += path(f'{pab_prefix}/form/', page_block.PageBlockFormView.as_view(), name='editorial-board-site-webpath-page-block-form'),

# page headings
pah_prefix = f'{pa_prefix}/<int:page_id>/headings'
urlpatterns += path(f'{pah_prefix}/', page_heading.PageHeadingList.as_view(), name='editorial-board-site-webpath-page-headings'),
urlpatterns += path(f'{pah_prefix}/<int:pk>/', page_heading.PageHeadingView.as_view(), name='editorial-board-site-webpath-page-heading'),
urlpatterns += path(f'{pah_prefix}/<int:pk>/logs/', page_heading.PageHeadingLogsView.as_view(),
                    name='editorial-board-site-webpath-page-heading-logs'),
urlpatterns += path(f'{pah_prefix}/form/', page_heading.PageHeadingFormView.as_view(), name='editorial-board-site-webpath-page-heading-form'),

# page heading localizations
pahl_prefix = f'{pa_prefix}/<int:page_id>/headings/<int:heading_id>/localizations'
urlpatterns += path(f'{pahl_prefix}/', page_heading_localization.PageHeadingLocalizationList.as_view(),
                    name='editorial-board-site-webpath-page-heading-localizations'),
urlpatterns += path(f'{pahl_prefix}/<int:pk>/', page_heading_localization.PageHeadingLocalizationView.as_view(),
                    name='editorial-board-site-webpath-page-heading-localization'),
urlpatterns += path(f'{pahl_prefix}/<int:pk>/logs/', page_heading_localization.PageHeadingLocalizationLogsView.as_view(),
                    name='editorial-board-site-webpath-page-heading-localization-logs'),
urlpatterns += path(f'{pahl_prefix}/form/', page_heading_localization.PageHeadingLocalizationFormView.as_view(),
                    name='editorial-board-site-webpath-page-heading-localization-form'),

# page links
pali_prefix = f'{pa_prefix}/<int:page_id>/links'
urlpatterns += path(f'{pali_prefix}/', page_link.PageLinkList.as_view(), name='editorial-board-site-webpath-page-links'),
urlpatterns += path(f'{pali_prefix}/<int:pk>/', page_link.PageLinkView.as_view(), name='editorial-board-site-webpath-page-link'),
urlpatterns += path(f'{pali_prefix}/<int:pk>/logs/', page_link.PageLinkLogsView.as_view(), name='editorial-board-site-webpath-page-link-logs'),
urlpatterns += path(f'{pali_prefix}/form/', page_link.PageLinkFormView.as_view(), name='editorial-board-site-webpath-page-link-form'),

# page carousels
pac_prefix = f'{pa_prefix}/<int:page_id>/carousels'
urlpatterns += path(f'{pac_prefix}/', page_carousel.PageCarouselList.as_view(), name='editorial-board-site-webpath-page-carousels'),
urlpatterns += path(f'{pac_prefix}/<int:pk>/', page_carousel.PageCarouselView.as_view(), name='editorial-board-site-webpath-page-carousel'),
urlpatterns += path(f'{pac_prefix}/<int:pk>/logs/', page_carousel.PageCarouselLogsView.as_view(),
                    name='editorial-board-site-webpath-page-carousel-logs'),
urlpatterns += path(f'{pac_prefix}/form/', page_carousel.PageCarouselFormView.as_view(), name='editorial-board-site-webpath-page-carousel-form'),

# page localizations
palo_prefix = f'{pa_prefix}/<int:page_id>/localizations'
urlpatterns += path(f'{palo_prefix}/', page_localization.PageLocalizationList.as_view(), name='editorial-board-site-webpath-page-localizations'),
urlpatterns += path(f'{palo_prefix}/<int:pk>/', page_localization.PageLocalizationView.as_view(),
                    name='editorial-board-site-webpath-page-localization'),
urlpatterns += path(f'{palo_prefix}/<int:pk>/logs/', page_localization.PageLocalizationLogsView.as_view(),
                    name='editorial-board-site-webpath-page-localization-logs'),
urlpatterns += path(f'{palo_prefix}/form/', page_localization.PageLocalizationFormView.as_view(),
                    name='editorial-board-site-webpath-page-localization-form'),

# page medias
pamed_prefix = f'{pa_prefix}/<int:page_id>/medias'
urlpatterns += path(f'{pamed_prefix}/', page_media.PageMediaList.as_view(), name='editorial-board-site-webpath-page-medias'),
urlpatterns += path(f'{pamed_prefix}/<int:pk>/', page_media.PageMediaView.as_view(), name='editorial-board-site-webpath-page-media'),
urlpatterns += path(f'{pamed_prefix}/<int:pk>/logs/', page_media.PageMediaLogsView.as_view(), name='editorial-board-site-webpath-page-media-logs'),
urlpatterns += path(f'{pamed_prefix}/form/', page_media.PageMediaFormView.as_view(), name='editorial-board-site-webpath-page-media-form'),

# page media collections
pamecol_prefix = f'{pa_prefix}/<int:page_id>/media-collections'
urlpatterns += path(f'{pamecol_prefix}/', page_media_collection.PageMediaCollectionList.as_view(),
                    name='editorial-board-site-webpath-page-media-collections'),
urlpatterns += path(f'{pamecol_prefix}/<int:pk>/', page_media_collection.PageMediaCollectionView.as_view(),
                    name='editorial-board-site-webpath-page-media-collection'),
urlpatterns += path(f'{pamecol_prefix}/<int:pk>/logs/', page_media_collection.PageMediaCollectionLogsView.as_view(),
                    name='editorial-board-site-webpath-page-media-collection-logs'),
urlpatterns += path(f'{pamecol_prefix}/form/', page_media_collection.PageMediaCollectionFormView.as_view(),
                    name='editorial-board-site-webpath-page-media-collection-form'),

# page menus
pamen_prefix = f'{pa_prefix}/<int:page_id>/menus'
urlpatterns += path(f'{pamen_prefix}/', page_menu.PageMenuList.as_view(), name='editorial-board-site-webpath-page-menus'),
urlpatterns += path(f'{pamen_prefix}/<int:pk>/', page_menu.PageMenuView.as_view(), name='editorial-board-site-webpath-page-menu'),
urlpatterns += path(f'{pamen_prefix}/<int:pk>/logs/', page_menu.PageMenuLogsView.as_view(), name='editorial-board-site-webpath-page-menu-logs'),
urlpatterns += path(f'{pamen_prefix}/form/', page_menu.PageMenuFormView.as_view(), name='editorial-board-site-webpath-page-menu-form'),

# page publications
pap_prefix = f'{pa_prefix}/<int:page_id>/publications'
urlpatterns += path(f'{pap_prefix}/', page_publication.PagePublicationList.as_view(), name='editorial-board-site-webpath-page-publications'),
urlpatterns += path(f'{pap_prefix}/<int:pk>/', page_publication.PagePublicationView.as_view(),
                    name='editorial-board-site-webpath-page-publication'),
urlpatterns += path(f'{pap_prefix}/<int:pk>/logs/', page_publication.PagePublicationLogsView.as_view(),
                    name='editorial-board-site-webpath-page-publication-logs'),
urlpatterns += path(f'{pap_prefix}/form/', page_publication.PagePublicationFormView.as_view(),
                    name='editorial-board-site-webpath-page-publication-form'),

# page related
par_prefix = f'{pa_prefix}/<int:page_id>/related'
urlpatterns += path(f'{par_prefix}/', page_related.PageRelatedList.as_view(), name='editorial-board-site-webpath-page-related-list'),
urlpatterns += path(f'{par_prefix}/<int:pk>/', page_related.PageRelatedView.as_view(), name='editorial-board-site-webpath-page-related'),
urlpatterns += path(f'{par_prefix}/<int:pk>/logs/', page_related.PageRelatedLogsView.as_view(),
                    name='editorial-board-site-webpath-page-related-logs'),
urlpatterns += path(f'{par_prefix}/form/', page_related.PageRelatedFormView.as_view(), name='editorial-board-site-webpath-page-related-form'),

# publication-contexts
pc_prefix = f'{w_prefix}/<int:webpath_id>/publication-contexts'
urlpatterns += path(f'{pc_prefix}/', webpath_pub_context.PublicationContextList.as_view(),
                    name='editorial-board-site-webpath-publication-contexts'),
urlpatterns += path(f'{pc_prefix}/<int:pk>/', webpath_pub_context.PublicationContextView.as_view(),
                    name='editorial-board-site-webpath-publication-context'),
urlpatterns += path(f'{pc_prefix}/<int:pk>/logs/', webpath_pub_context.PublicationContextLogsView.as_view(),
                    name='editorial-board-site-webpath-publication-context-logs'),
urlpatterns += path(f'{pc_prefix}/form/', webpath_pub_context.PublicationContextFormView.as_view(),
                    name='editorial-board-site-webpath-publication-context-form'),
urlpatterns += path(f'{w_prefix}/publication-contexts/form/', webpath_pub_context.PublicationContextGenericFormView.as_view(),
                    name='editorial-board-site-webpath-publication-context-form-generic'),

# publications
pu_prefix = f'{eb_prefix}/publications'
urlpatterns += path(f'{pu_prefix}/', publication.PublicationList.as_view(), name='editorial-board-publications'),
urlpatterns += path(f'{pu_prefix}/<int:pk>/', publication.PublicationView.as_view(), name='editorial-board-publication'),
urlpatterns += path(f'{pu_prefix}/<int:pk>/logs/', publication.PublicationLogsView.as_view(), name='editorial-board-publication-logs'),
urlpatterns += path(f'{pu_prefix}/<int:pk>/change-status/', publication.PublicationChangeStateView.as_view(),
                    name='editorial-board-publication-change-status'),
urlpatterns += path(f'{pu_prefix}/form/', publication.PublicationFormView.as_view(), name='editorial-board-publication-form'),
urlpatterns += path(f'{pu_prefix}/options/', publication.PublicationOptionList.as_view(), name='editorial-board-publications-options'),
urlpatterns += path(f'{pu_prefix}/options/<int:pk>/', publication.PublicationOptionView.as_view(), name='editorial-board-publications-option'),

# publication attachments
pua_prefix = f'{pu_prefix}/<int:publication_id>/attachments'
urlpatterns += path(f'{pua_prefix}/', publication_attachment.PublicationAttachmentList.as_view(), name='editorial-board-publication-attachments'),
urlpatterns += path(f'{pua_prefix}/<int:pk>/', publication_attachment.PublicationAttachmentView.as_view(),
                    name='editorial-board-publication-attachment'),
urlpatterns += path(f'{pua_prefix}/<int:pk>/logs/', publication_attachment.PublicationAttachmentLogsView.as_view(),
                    name='editorial-board-publication-attachment-logs'),
urlpatterns += path(f'{pua_prefix}/form/', publication_attachment.PublicationAttachmentFormView.as_view(),
                    name='editorial-board-publication-attachment-form'),

# publication blocks
pub_prefix = f'{pu_prefix}/<int:publication_id>/blocks'
urlpatterns += path(f'{pub_prefix}/', publication_block.PublicationBlockList.as_view(), name='editorial-board-publication-blocks'),
urlpatterns += path(f'{pub_prefix}/<int:pk>/', publication_block.PublicationBlockView.as_view(), name='editorial-board-publication-block'),
urlpatterns += path(f'{pub_prefix}/<int:pk>/logs/', publication_block.PublicationBlockLogsView.as_view(),
                    name='editorial-board-publication-block-logs'),

# publication links
puli_prefix = f'{pu_prefix}/<int:publication_id>/links'
urlpatterns += path(f'{puli_prefix}/', publication_link.PublicationLinkList.as_view(), name='editorial-board-publication-links'),
urlpatterns += path(f'{puli_prefix}/<int:pk>/', publication_link.PublicationLinkView.as_view(), name='editorial-board-publication-link'),
urlpatterns += path(f'{puli_prefix}/<int:pk>/logs/', publication_link.PublicationLinkLogsView.as_view(),
                    name='editorial-board-publication-link-logs'),
urlpatterns += path(f'{puli_prefix}/form/', publication_link.PublicationLinkFormView.as_view(), name='editorial-board-publication-link-form'),

# publication media collections
pug_prefix = f'{pu_prefix}/<int:publication_id>/media-collections'
urlpatterns += path(f'{pug_prefix}/', publication_media_collection.PublicationMediaCollectionList.as_view(), name='editorial-board-publication-media-collections'),
urlpatterns += path(f'{pug_prefix}/<int:pk>/', publication_media_collection.PublicationMediaCollectionView.as_view(), name='editorial-board-publication-media-collection'),
urlpatterns += path(f'{pug_prefix}/<int:pk>/logs/', publication_media_collection.PublicationMediaCollectionLogsView.as_view(),
                    name='editorial-board-publication-media-collection-logs'),
urlpatterns += path(f'{pug_prefix}/form/', publication_media_collection.PublicationMediaCollectionFormView.as_view(),
                    name='editorial-board-publication-media-collection-form'),

# publication localizations
pulo_prefix = f'{pu_prefix}/<int:publication_id>/localizations'
urlpatterns += path(f'{pulo_prefix}/', publication_localization.PublicationLocalizationList.as_view(),
                    name='editorial-board-publication-localizations'),
urlpatterns += path(f'{pulo_prefix}/<int:pk>/', publication_localization.PublicationLocalizationView.as_view(),
                    name='editorial-board-publication-localization'),
urlpatterns += path(f'{pulo_prefix}/<int:pk>/logs/', publication_localization.PublicationLocalizationLogsView.as_view(),
                    name='editorial-board-publication-localization-logs'),
urlpatterns += path(f'{pulo_prefix}/form/', publication_localization.PublicationLocalizationFormView.as_view(),
                    name='editorial-board-publication-localization-form'),

# publication related
pur_prefix = f'{pu_prefix}/<int:publication_id>/related'
urlpatterns += path(f'{pur_prefix}/', publication_related.PublicationRelatedList.as_view(), name='editorial-board-publication-related-list'),
urlpatterns += path(f'{pur_prefix}/<int:pk>/', publication_related.PublicationRelatedView.as_view(), name='editorial-board-publication-related'),
urlpatterns += path(f'{pur_prefix}/<int:pk>/logs/', publication_related.PublicationRelatedLogsView.as_view(),
                    name='editorial-board-publication-related-logs'),
urlpatterns += path(f'{pur_prefix}/form/', publication_related.PublicationRelatedFormView.as_view(),
                    name='editorial-board-publication-related-form'),

# all template blocks
tb_prefix = f'{eb_prefix}/templates'
urlpatterns += path(f'{tb_prefix}/blocks/', template_block.TemplatesBlockList.as_view(), name='editorial-board-templates-blocks'),
urlpatterns += path(f'{tb_prefix}/blocks/<int:pk>/', template_block.TemplatesBlockView.as_view(), name='editorial-board-templates-block'),

# single template blocks
tb_id_prefix = f'{eb_prefix}/templates/<int:template_id>'
urlpatterns += path(f'{tb_id_prefix}/blocks/', template_block.TemplateBlockList.as_view(), name='editorial-board-template-blocks'),
urlpatterns += path(f'{tb_id_prefix}/blocks/<int:pk>/', template_block.TemplateBlockView.as_view(), name='editorial-board-template-block'),

# page templates
pt_prefix = f'{eb_prefix}/page-templates'
urlpatterns += path(f'{pt_prefix}/', page_template.PageTemplateList.as_view(), name='editorial-board-page-templates'),
urlpatterns += path(f'{pt_prefix}/<int:pk>/', page_template.PageTemplateView.as_view(), name='editorial-board-page-template'),

# menus
menu_prefix = f'{eb_prefix}/menus'
urlpatterns += path(f'{menu_prefix}/', menu.MenuList.as_view(), name='editorial-board-menus'),
urlpatterns += path(f'{menu_prefix}/<int:pk>/', menu.MenuView.as_view(), name='editorial-board-menu'),
urlpatterns += path(f'{menu_prefix}/<int:pk>/logs/', menu.MenuLogsView.as_view(), name='editorial-board-menu-logs'),
urlpatterns += path(f'{menu_prefix}/<int:pk>/clone/', menu.MenuCloneView.as_view(), name='editorial-board-menu-clone'),
urlpatterns += path(f'{menu_prefix}/form/', menu.MenuFormView.as_view(), name='editorial-board-menu-form'),
urlpatterns += path(f'{menu_prefix}/options/', menu.MenuOptionList.as_view(), name='editorial-board-menu-options'),
urlpatterns += path(f'{menu_prefix}/options/<int:pk>/', menu.MenuOptionView.as_view(), name='editorial-board-menu-option'),

# menu items
mei_prefix = f'{menu_prefix}/<int:menu_id>/items'
urlpatterns += path(f'{mei_prefix}/', menu_item.MenuItemList.as_view(), name='editorial-board-menu-items'),
urlpatterns += path(f'{mei_prefix}/<int:pk>/', menu_item.MenuItemView.as_view(), name='editorial-board-menu-item'),
urlpatterns += path(f'{mei_prefix}/<int:pk>/logs/', menu_item.MenuItemLogsView.as_view(), name='editorial-board-menu-item-logs'),
urlpatterns += path(f'{mei_prefix}/form/', menu_item.MenuItemFormView.as_view(), name='editorial-board-menu-item-form'),

# menu item localizations
meil_prefix = f'{mei_prefix}/<int:menu_item_id>/localizations'
urlpatterns += path(f'{meil_prefix}/', menu_item_localization.MenuItemLocalizationList.as_view(), name='menu-item-localizations'),
urlpatterns += path(f'{meil_prefix}/<int:pk>/', menu_item_localization.MenuItemLocalizationView.as_view(),
                    name='menu-item-localization'),
urlpatterns += path(f'{meil_prefix}/<int:pk>/logs/', menu_item_localization.MenuItemLocalizationLogsView.as_view(),
                    name='menu-item-localization-logs'),
urlpatterns += path(f'{meil_prefix}/form/', menu_item_localization.MenuItemLocalizationFormView.as_view(),
                    name='menu-item-localization-form'),

# locks
urlpatterns += path(f'{eb_prefix}/locks/<int:content_type_id>/<int:object_id>/', locks.ObjectUserLocksList.as_view(), name='editorial-board-locks'),
urlpatterns += path(f'{eb_prefix}/locks/<int:content_type_id>/<int:object_id>/<int:pk>/',
                    locks.ObjectUserLocksView.as_view(), name='editorial-board-lock-delete'),
urlpatterns += path(f'{eb_prefix}/users/form/', webpath_pub_context.EditorialBoardLockUserFormView.as_view(), name='users-form'),
urlpatterns += path(f'{eb_prefix}/redis-lock/<int:content_type_id>/<int:object_id>/',
                    locks.RedisLockView.as_view(), name='editorial-board-redis-lock'),
urlpatterns += path(f'{eb_prefix}/redis-lock/set/',
                    locks.RedisLockSetView.as_view(), name='editorial-board-redis-lock-set'),

# users
u_prefix = f'{eb_prefix}/users'
# urlpatterns += path(f'{u_prefix}/form/', webpath_pub_context.EditorialBoardLockUserFormView.as_view(), name='users-form'),
urlpatterns += path(f'{u_prefix}/current/', users.CurrentUserIDView.as_view(), name='users-current'),
