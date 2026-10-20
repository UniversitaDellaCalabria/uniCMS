import json
import logging
import types

from unittest import mock

from django.test import Client, TestCase
from django.urls import reverse

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.schemas import openapi


def _inflection():
    # DRF needs the optional `inflection` package to build operationIds:
    # use it if installed, otherwise a minimal stand-in
    if openapi.inflection:
        return openapi.inflection
    return types.SimpleNamespace(pluralize=lambda s: f'{s}s')


def _filter_schema_parameters(self, view):
    # django-filter >= 25 dropped DjangoFilterBackend schema support,
    # this mirrors the removed implementation (django-filter 23.x)
    try:
        queryset = view.get_queryset()
    except Exception:
        queryset = None
    filterset_class = self.get_filterset_class(view, queryset)
    if not filterset_class:
        return []
    return [{'name': name,
             'required': field.extra['required'],
             'in': 'query',
             'description': getattr(field, 'label', None) or name,
             'schema': {'type': 'string'}}
            for name, field in filterset_class.base_filters.items()]


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class OpenAPISchemaUnitTest(TestCase):
    """
    Schema generation calls get_queryset() without url kwargs
    and the custom AutoSchema get_operation_id/get_operation methods
    of every API view.
    """

    def setUp(self):
        patcher = mock.patch.object(openapi, 'inflection', _inflection())
        patcher.start()
        self.addCleanup(patcher.stop)
        if not hasattr(DjangoFilterBackend, 'get_schema_operation_parameters'):
            patcher = mock.patch.object(DjangoFilterBackend,
                                        'get_schema_operation_parameters',
                                        _filter_schema_parameters,
                                        create=True)
            patcher.start()
            self.addCleanup(patcher.stop)

    def _check_schema(self, schema):
        assert schema['openapi'].startswith('3.')
        assert 'paths' in schema and schema['paths']
        op_ids = set()
        for path, methods in schema['paths'].items():
            for method, operation in methods.items():
                assert operation['operationId']
                op_ids.add(operation['operationId'])
        # custom AutoSchema operationIds
        for op_id in ('listMenuLogs', 'cloneMenu', 'listMenuSelectOptions',
                      'listCarouselLogs', 'listCarouselItemLogs'):
            assert op_id in op_ids
        # api endpoints are included
        assert any('/api/' in path for path in schema['paths'])

    def test_openapi_json(self):
        req = Client()
        res = req.get(reverse('openapi-schema-json'))
        assert res.status_code == 200
        self._check_schema(json.loads(res.content))

    def test_openapi_yaml(self):
        req = Client()
        res = req.get(reverse('openapi-schema'),
                      HTTP_ACCEPT='application/vnd.oai.openapi')
        assert res.status_code == 200
        content = res.content.decode()
        assert content.startswith('openapi:')
        assert 'paths:' in content
