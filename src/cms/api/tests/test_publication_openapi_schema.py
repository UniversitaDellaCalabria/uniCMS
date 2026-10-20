import logging

from django.test import RequestFactory, TestCase

from cms.api.views import (publication, publication_attachment,
                           publication_block, publication_link,
                           publication_localization,
                           publication_media_collection,
                           publication_related, webpath_pub_context)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PublicationOpenAPISchemaUnitTest(TestCase):
    """
    OpenAPI schema generation calls get_queryset() of the API views
    without url kwargs and the custom AutoSchema operation ids.
    The full schema view requires `inflection` (not in requirements),
    so these parts are tested directly.
    """

    def test_list_views_without_kwargs(self):
        request = RequestFactory().get('/')
        views = (publication_attachment.PublicationAttachmentList,
                 publication_block.PublicationBlockList,
                 publication_link.PublicationLinkList,
                 publication_localization.PublicationLocalizationList,
                 publication_media_collection.PublicationMediaCollectionList,
                 publication_related.PublicationRelatedList,
                 webpath_pub_context.PublicationContextList)
        for view_class in views:
            view = view_class()
            view.request = request
            view.kwargs = {}
            queryset = view.get_queryset()
            # empty queryset of the right model
            assert queryset.model == view_class.serializer_class.Meta.model
            assert not queryset.exists()
            if hasattr(view, 'publication'):
                assert view.publication is None

    def test_operation_ids(self):
        expected = (
            # public API
            (publication.ApiPublicationsByContext, 'GET',
             'retrievePublicPublicationContext'),
            (publication.ApiPublicationsByContextCategory, 'GET',
             'retrievePublicPublicationContextCategory'),
            # publications
            (publication.PublicationList, 'GET',
             'listEditorialBoardPublications'),
            (publication.PublicationList, 'POST',
             'createEditorialBoardPublication'),
            (publication.PublicationView, 'GET',
             'retrieveEditorialBoardPublication'),
            (publication.PublicationView, 'PATCH',
             'partialUpdateEditorialBoardPublication'),
            (publication.PublicationView, 'PUT',
             'updateEditorialBoardPublication'),
            (publication.PublicationView, 'DELETE',
             'deleteEditorialBoardPublication'),
            (publication.PublicationChangeStateView, 'GET',
             'updateEditorialBoardPublicationStatus'),
            (publication.PublicationOptionList, 'GET',
             'listPublicationSelectOptions'),
            (publication.PublicationLogsView, 'GET',
             'listPublicationLogs'),
            # publication related objects logs
            (publication_attachment.PublicationAttachmentLogsView, 'GET',
             'listPublicationAttachmentLogs'),
            (publication_block.PublicationBlockLogsView, 'GET',
             'listPublicationBlockLogs'),
            (publication_link.PublicationLinkLogsView, 'GET',
             'listPublicationLinkLogs'),
            (publication_localization.PublicationLocalizationLogsView, 'GET',
             'listPublicationLocalizationLogs'),
            (publication_media_collection.PublicationMediaCollectionLogsView, 'GET',
             'listPublicationMediaCollectionLogs'),
            (publication_related.PublicationRelatedLogsView, 'GET',
             'listPublicationRelatedLogs'),
            # publication contexts
            (webpath_pub_context.AllPublicationContextOptionList, 'GET',
             'listAllPublicationContextSelectOptions'),
            (webpath_pub_context.PublicationContextLogsView, 'GET',
             'lisPublicationContextLogs'),
        )
        for view_class, method, operation_id in expected:
            schema = view_class.schema
            assert schema.get_operation_id('/path', method) == operation_id
