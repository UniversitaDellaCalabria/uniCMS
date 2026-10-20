import copy
import datetime
import io
import itertools
import logging

from contextlib import redirect_stdout
from unittest import mock

from django.conf import settings
from django.core.management import call_command
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from pymongo.errors import ServerSelectionTimeoutError

# import modules (not classes) to avoid running their tests twice
from cms.contexts import tests as contexts_tests
from cms.pages import tests as pages_tests
from cms.publications import tests as publications_tests
from cms.publications.models import PublicationContext

from . import MongoClientFactory, mongo_collection
from . hooks import (page_se_insert,
                     publication_context_se_delete,
                     publication_context_se_insert,
                     publication_se_insert,
                     searchengine_entry_remove,
                     webpath_se_update)
from . models import page_to_entry, publication_to_entry


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


MODEL_TO_MONGO_MAP = {
    'cmspages.Page': 'cms.search.models.page_to_entry',
    'cmspublications.Publication': 'cms.search.models.publication_to_entry'
}


def _match_value(value, cond):
    """
    minimal implementation of the MongoDB query operators used by uniCMS
    """
    if isinstance(cond, dict) and any(k.startswith('$') for k in cond):
        for op, arg in cond.items():
            if op == '$in':
                if isinstance(value, list):
                    ok = any(v in arg for v in value)
                else:
                    ok = value in arg
            elif op == '$all':
                ok = isinstance(value, list) and all(a in value for a in arg)
            elif op == '$gte':
                ok = value is not None and value >= arg
            elif op == '$lt':
                ok = value is not None and value < arg
            elif op == '$elemMatch':
                ok = isinstance(value, list) and \
                     any(_match_value(v, arg) for v in value)
            else:
                raise NotImplementedError(op)
            if not ok: return False
        return True
    if isinstance(value, list) and not isinstance(cond, list):
        return cond in value
    return value == cond


class FakeDeleteResult:
    def __init__(self, deleted_count):
        self.deleted_count = deleted_count


class FakeCursor:
    """
    in memory pymongo Cursor (only what uniCMS uses)
    """
    def __init__(self, collection, docs):
        self.collection = collection
        self.docs = docs

    def sort(self, key_or_list, direction=None):
        if isinstance(key_or_list, list):
            key_or_list, direction = key_or_list[0]
        # {'$meta': 'textScore'}: keep the natural order
        if isinstance(direction, dict):
            return self
        self.docs = sorted(self.docs,
                           key=lambda d: d.get(key_or_list),
                           reverse=direction == -1)
        return self

    def __getitem__(self, index):
        return self.docs[index]

    def __iter__(self):
        return iter(self.docs)


class FakeMongoCollection:
    """
    in memory pymongo Collection,
    to be used with unittest.mock.patch in place of mongo_collection
    """
    TEXT_FIELDS = ('title', 'heading', 'content')

    def __init__(self, docs=None):
        self.docs = []
        self.indexes = []
        self._ids = itertools.count(1)
        if docs: self.insert_many(docs)

    def __call__(self):
        # it can replace the mongo_collection() function too
        return self

    def _match(self, doc, query):
        for key, cond in (query or {}).items():
            if key == '$text':
                words = cond['$search'].lower().split()
                text = ' '.join(str(doc.get(f) or '')
                                for f in self.TEXT_FIELDS).lower()
                if not any(w in text for w in words):
                    return False
            elif not _match_value(doc.get(key), cond):
                return False
        return True

    def _filter(self, query):
        return [d for d in self.docs if self._match(d, query)]

    def find(self, query=None, projection=None):
        return FakeCursor(self, [copy.deepcopy(d) for d in self._filter(query)])

    def find_one(self, query=None):
        docs = self._filter(query)
        return copy.deepcopy(docs[0]) if docs else None

    def count_documents(self, query):
        return len(self._filter(query))

    def insert_one(self, doc):
        doc = copy.deepcopy(doc)
        doc['_id'] = next(self._ids)
        self.docs.append(doc)
        return doc

    def insert_many(self, docs, ordered=True):
        # same behaviour of pymongo
        if not docs:
            raise TypeError('documents must be a non-empty list')
        return [self.insert_one(d) for d in docs]

    def delete_many(self, query):
        to_delete = self._filter(query)
        self.docs = [d for d in self.docs if d not in to_delete]
        return FakeDeleteResult(len(to_delete))

    def drop_indexes(self):
        self.indexes = []

    def create_index(self, keys, **kwargs):
        self.indexes.append((keys, kwargs))
        return '_'.join(f'{k}_{v}' for k, v in keys)

    def __str__(self):
        return 'FakeMongoCollection'


# hooks are called explicitly: disable them while creating the objects
@override_settings(CMS_HOOKS={}, MODEL_TO_MONGO_MAP=MODEL_TO_MONGO_MAP)
class SearchBaseTest(TestCase):

    def setUp(self):
        self.fake = FakeMongoCollection()
        for target in ('cms.search.hooks.mongo_collection',):
            patcher = mock.patch(target, self.fake)
            patcher.start()
            self.addCleanup(patcher.stop)

    @staticmethod
    def create_page(**kwargs):
        return pages_tests.PageUnitTest.create_page(**kwargs)

    @staticmethod
    def create_pub(**kwargs):
        return publications_tests.PublicationUnitTest.create_pub(count=1,
                                                                **kwargs)

    def docs_of(self, obj):
        return [d for d in self.fake.docs
                if d['content_type'] == obj._meta.label and
                d['content_id'] == str(obj.pk)]


class SearchModelsTest(SearchBaseTest):

    def test_page_to_entry(self):
        page = self.create_page()
        entry = page_to_entry(page)
        self.assertEqual(entry['title'], page.name)
        self.assertEqual(entry['content_type'], 'cmspages.Page')
        self.assertEqual(entry['content_id'], str(page.pk))
        self.assertEqual(entry['sites'], [page.webpath.site.domain])
        self.assertEqual(entry['urls'],
                         [f'//{page.webpath.site.domain}{page.webpath.get_full_path()}'])
        self.assertEqual(entry['categories'], [page.get_type_display()])
        self.assertEqual(entry['year'], page.date_start.year)

    def test_page_to_entry_restricted_webpath(self):
        page = self.create_page()
        page.webpath.access = '2'
        page.webpath.save()
        self.assertIsNone(page_to_entry(page))

    def test_page_to_entry_inherited_access(self):
        parent = contexts_tests.ContextUnitTest.create_webpath(path='area')
        child = contexts_tests.ContextUnitTest.create_webpath(path='child',
                                                              parent=parent,
                                                              access='1')
        page = self.create_page(webpath=child)
        # public parent
        self.assertIsNotNone(page_to_entry(page))
        # restricted parent
        parent.access = '2'
        parent.save()
        child.refresh_from_db()
        page.refresh_from_db()
        self.assertIsNone(page_to_entry(page))

    def test_publication_to_entry(self):
        pub = self.create_pub()
        pub.tags.add('tag2')
        context = pub.get_publication_context()
        entry = publication_to_entry(pub)
        self.assertEqual(entry['title'], pub.title)
        self.assertEqual(entry['content_type'], 'cmspublications.Publication')
        self.assertEqual(entry['content_id'], str(pub.pk))
        self.assertEqual(entry['sites'], [context.webpath.site.domain])
        self.assertEqual(entry['urls'],
                         [f'//{context.webpath.site.domain}{context.url}'])
        self.assertEqual(entry['categories'], ['main'])
        self.assertEqual(sorted(entry['tags']), ['ciao', 'tag2'])
        self.assertEqual(entry['translations'][0]['language'], 'english')
        self.assertEqual(entry['translations'][0]['title'], 'pub eng')
        self.assertEqual(entry['published'], context.date_start)
        # explicit contexts
        entry = publication_to_entry(pub, pub.publicationcontext_set.all())
        self.assertEqual(entry['content_id'], str(pub.pk))

    def test_publication_to_entry_not_indexable_contexts(self):
        pub = self.create_pub()
        context = pub.get_publication_context()
        webpath = context.webpath

        # restricted webpath
        webpath.access = '2'
        webpath.save()
        self.assertIsNone(publication_to_entry(pub))

        # inactive webpath
        webpath.access = '0'
        webpath.is_active = False
        webpath.save()
        self.assertIsNone(publication_to_entry(pub))

        # expired context
        webpath.is_active = True
        webpath.save()
        context.date_end = timezone.localtime() - timezone.timedelta(minutes=1)
        context.save()
        self.assertIsNone(publication_to_entry(pub))

        # no contexts at all
        self.assertIsNone(publication_to_entry(pub, []))


class SearchHooksTest(SearchBaseTest):

    def test_page_se_insert(self):
        page = self.create_page()
        page_se_insert(page)
        docs = self.docs_of(page)
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0]['title'], page.name)

        # reindex replaces the old entry
        page.name = 'new name'
        page_se_insert(page)
        docs = self.docs_of(page)
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0]['title'], 'new name')

        # not publicable page is removed
        page.state = 'draft'
        page_se_insert(page)
        self.assertEqual(self.docs_of(page), [])

    def test_page_se_insert_restricted(self):
        page = self.create_page()
        page.webpath.access = '2'
        page.webpath.save()
        page_se_insert(page)
        self.assertEqual(self.docs_of(page), [])

    def test_publication_se_insert(self):
        pub = self.create_pub()
        publication_se_insert(pub)
        docs = self.docs_of(pub)
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0]['title'], pub.title)

        # reindex replaces the old entry
        pub.title = 'new title'
        publication_se_insert(pub)
        docs = self.docs_of(pub)
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0]['title'], 'new title')

        # inactive publication is removed
        pub.is_active = False
        publication_se_insert(pub)
        self.assertEqual(self.docs_of(pub), [])

    def test_publication_se_insert_no_published_contexts(self):
        pub = self.create_pub()
        pub.publicationcontext_set.update(
            date_start=timezone.localtime() + timezone.timedelta(days=1),
            date_end=timezone.localtime() + timezone.timedelta(days=2))
        publication_se_insert(pub)
        self.assertEqual(self.docs_of(pub), [])

    def test_publication_context_hooks(self):
        pub = self.create_pub()
        context = pub.get_publication_context()
        publication_context_se_insert(context)
        self.assertEqual(len(self.docs_of(pub)), 1)

        # deleting its only context removes the publication from the index
        publication_context_se_delete(context)
        self.assertEqual(self.docs_of(pub), [])

    def test_publication_context_delete_with_other_contexts(self):
        pub = self.create_pub()
        context = pub.get_publication_context()
        other_webpath = contexts_tests.ContextUnitTest.create_webpath(path='other')
        PublicationContext.objects.create(publication=pub,
                                          webpath=other_webpath,
                                          date_start=timezone.localtime(),
                                          date_end=timezone.localtime() + timezone.timedelta(hours=1),
                                          is_active=True)
        publication_se_insert(pub)
        self.assertEqual(len(self.docs_of(pub)[0]['urls']), 2)

        publication_context_se_delete(context)
        docs = self.docs_of(pub)
        self.assertEqual(len(docs), 1)
        self.assertEqual(len(docs[0]['urls']), 1)
        self.assertIn(other_webpath.get_full_path(), docs[0]['urls'][0])

    def test_searchengine_entry_remove(self):
        page = self.create_page()
        pub = self.create_pub()
        page_se_insert(page)
        publication_se_insert(pub)
        self.assertEqual(len(self.fake.docs), 2)

        searchengine_entry_remove(page)
        self.assertEqual(self.docs_of(page), [])
        self.assertEqual(len(self.docs_of(pub)), 1)

    def _subtree(self):
        pub = self.create_pub()
        webpath = pub.get_publication_context().webpath
        child = contexts_tests.ContextUnitTest.create_webpath(path='child',
                                                              parent=webpath)
        page = self.create_page(webpath=child)
        page_se_insert(page)
        publication_se_insert(pub)
        return webpath, page, pub

    def test_webpath_se_update(self):
        webpath, page, pub = self._subtree()
        webpath.path = 'renamed'
        webpath.save()

        with self.captureOnCommitCallbacks(execute=True) as callbacks:
            webpath_se_update(webpath)
        self.assertEqual(len(callbacks), 1)

        page_urls = self.docs_of(page)[0]['urls']
        pub_urls = self.docs_of(pub)[0]['urls']
        self.assertIn('/renamed/child/', page_urls[0])
        self.assertIn('/renamed/', pub_urls[0])
        self.assertEqual(len(self.fake.docs), 2)

    def test_webpath_se_update_restricted_subtree(self):
        webpath, page, pub = self._subtree()
        webpath.access = '2'
        webpath.save()
        with self.captureOnCommitCallbacks(execute=True):
            webpath_se_update(webpath)
        # restricted contents are removed from the index
        self.assertEqual(self.fake.docs, [])

    def test_webpath_se_update_nothing_to_do(self):
        # new webpath
        webpath = contexts_tests.ContextUnitTest.create_webpath(path='new')
        with self.captureOnCommitCallbacks() as callbacks:
            webpath_se_update(webpath)
        self.assertEqual(callbacks, [])

        # saved without tracked changes
        webpath.name = 'only the name changes'
        webpath.save()
        with self.captureOnCommitCallbacks() as callbacks:
            webpath_se_update(webpath)
        self.assertEqual(callbacks, [])

    def test_webpath_se_update_failure(self):
        webpath, page, pub = self._subtree()
        webpath.path = 'renamed'
        webpath.save()
        with mock.patch('cms.search.hooks.page_se_insert',
                        side_effect=Exception('boom')):
            with self.assertLogs('cms.search.hooks', level='ERROR') as logs:
                with self.captureOnCommitCallbacks(execute=True):
                    webpath_se_update(webpath)
        self.assertIn('search engine reindex failed with: boom',
                      logs.output[0])
        # old entries are still there
        self.assertNotIn('/renamed/', self.docs_of(page)[0]['urls'][0])

    @override_settings(CMS_HOOKS={
        'WebPath': {'POSTSAVE': ['cms.search.hooks.webpath_se_update']},
        'Page': {'POSTSAVE': ['cms.search.hooks.page_se_insert'],
                 'PREDELETE': ['cms.search.hooks.searchengine_entry_remove']},
    })
    def test_hooks_from_settings(self):
        page = self.create_page()
        self.assertEqual(len(self.docs_of(page)), 1)

        webpath = page.webpath
        webpath.path = 'renamed'
        with self.captureOnCommitCallbacks(execute=True):
            webpath.save()
        self.assertIn('/renamed/', self.docs_of(page)[0]['urls'][0])

        page.delete()
        self.assertEqual(self.fake.docs, [])


@override_settings(SEARCH_ELEMENTS_IN_PAGE=25)
class SearchApiTest(TestCase):

    def setUp(self):
        self.url = reverse('unicms_search:api-search-engine')
        self.client = Client()
        self.fake = FakeMongoCollection(self._docs())
        factory = mock.MagicMock()
        factory.return_value.unicms.search = self.fake
        patcher = mock.patch('cms.search.api_views.MongoClientFactory',
                             factory)
        patcher.start()
        self.addCleanup(patcher.stop)
        # search in all the sites (project settings could restrict them)
        patcher = mock.patch('cms.search.api_views.ALLOW_SEARCH_IN_SITES', ['*'])
        patcher.start()
        self.addCleanup(patcher.stop)

    @staticmethod
    def _date(year, month=1, day=1):
        return timezone.make_aware(datetime.datetime(year, month, day, 12))

    def _docs(self):
        def doc(title, published, sites, tags, categories, content=''):
            return {'title': title, 'heading': '', 'content': content,
                    'content_type': 'cmspublications.Publication',
                    'content_id': title,
                    'sites': sites, 'urls': [f'//{sites[0]}/{title}/'],
                    'tags': tags, 'categories': categories,
                    'published': published, 'year': published.year}
        return [
            doc('first', self._date(2020, 3, 1), ['a.org'], ['t1'], ['news']),
            doc('second', self._date(2021, 6, 1), ['a.org', 'b.org'],
                ['t1', 't2'], ['news', 'events'], content='lorem ipsum'),
            doc('third', self._date(2022, 9, 1), ['b.org'], ['t2'], ['events']),
            doc('fourth', self._date(2022, 10, 1), ['c.org'], [], ['news']),
            doc('fifth', self._date(2023, 1, 1), ['c.org'], ['t1'], []),
        ]

    def get(self, params=''):
        return self.client.get(f'{self.url}{params}')

    def titles(self, res):
        return [i['title'] for i in res.json()['results']]

    def test_all(self):
        res = self.get()
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['count'], 5)
        self.assertEqual(data['total_pages'], 1)
        self.assertEqual(data['per_page'], 25)
        self.assertEqual(data['page'], 1)
        # ordered by publication date, mongo _id is hidden
        self.assertEqual(self.titles(res),
                         ['fifth', 'fourth', 'third', 'second', 'first'])
        self.assertNotIn('_id', data['results'][0])

    def test_text_search(self):
        res = self.get('?search=lorem ipsum')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self.titles(res), ['second'])
        # not allowed chars truncate the search string
        res = self.get('?search=third;drop')
        self.assertEqual(self.titles(res), ['third'])

    def test_year(self):
        res = self.get('?year=2022')
        self.assertEqual(sorted(self.titles(res)), ['fourth', 'third'])

    def test_dates(self):
        res = self.get('?date_start=2022-01-01')
        self.assertEqual(self.titles(res), ['fifth', 'fourth', 'third'])
        res = self.get('?date_end=2021-12-31')
        self.assertEqual(self.titles(res), ['second', 'first'])
        res = self.get('?date_start=2021-01-01&date_end=2022-10-01')
        self.assertEqual(self.titles(res), ['third', 'second'])

    def test_tags(self):
        res = self.get('?tags=t1')
        self.assertEqual(self.titles(res), ['fifth', 'second', 'first'])
        res = self.get('?tags=t1, t2')
        self.assertEqual(self.titles(res), ['second'])

    def test_categories(self):
        res = self.get('?categories=news')
        self.assertEqual(self.titles(res), ['fourth', 'second', 'first'])
        res = self.get('?categories=news,events')
        self.assertEqual(self.titles(res), ['second'])

    def test_sites(self):
        res = self.get('?sites=b.org')
        self.assertEqual(self.titles(res), ['third', 'second'])
        res = self.get('?sites=a.org,b.org')
        self.assertEqual(self.titles(res), ['second'])

    @mock.patch('cms.search.api_views.ALLOW_SEARCH_IN_SITES', ['a.org', 'b.org'])
    def test_allowed_sites(self):
        res = self.get()
        self.assertEqual(self.titles(res), ['third', 'second', 'first'])
        # sites filter within the allowed ones
        res = self.get('?sites=b.org')
        self.assertEqual(self.titles(res), ['third', 'second'])
        res = self.get('?sites=c.org')
        self.assertEqual(self.titles(res), [])

    @override_settings(SEARCH_ELEMENTS_IN_PAGE=2)
    def test_pagination(self):
        res = self.get()
        data = res.json()
        self.assertEqual(data['total_pages'], 3)
        self.assertEqual(data['per_page'], 2)
        self.assertEqual(self.titles(res), ['fifth', 'fourth'])

        res = self.get('?page=3')
        self.assertEqual(res.json()['page'], 3)
        self.assertEqual(self.titles(res), ['first'])

        # invalid page values fall back to the first page
        for page in ('a', '0'):
            res = self.get(f'?page={page}')
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.json()['page'], 1)

        # page out of range
        res = self.get('?page=4')
        self.assertEqual(res.status_code, 404)

    @override_settings(SEARCH_ELEMENTS_IN_PAGE=5)
    def test_pagination_exact_page(self):
        data = self.get().json()
        self.assertEqual(data['total_pages'], 1)
        self.assertEqual(len(data['results']), 5)

    def test_no_results(self):
        res = self.get('?search=nothing')
        data = res.json()
        self.assertEqual(data['count'], 0)
        self.assertEqual(data['total_pages'], 1)
        self.assertEqual(data['results'], [])

    def test_mongo_unavailable(self):
        with mock.patch.object(self.fake, 'find',
                               side_effect=ServerSelectionTimeoutError('down')):
            with self.assertLogs('cms.search.api_views', level='CRITICAL'):
                res = self.get()
        self.assertEqual(res.status_code, 503)


class SearchCommandsTest(SearchBaseTest):

    def setUp(self):
        super().setUp()
        for target in ('cms.search.management.commands.cms_search_content_sync.mongo_collection',
                       'cms.search.management.commands.cms_search_create_mongo_index.mongo_collection'):
            patcher = mock.patch(target, self.fake)
            patcher.start()
            self.addCleanup(patcher.stop)

    def call(self, *args):
        out = io.StringIO()
        with redirect_stdout(out):
            call_command(*args)
        return out.getvalue()

    def test_create_mongo_index(self):
        out = self.call('cms_search_create_mongo_index', '-y')
        self.assertIn('Drop existing indexes in FakeMongoCollection', out)
        self.assertIn('Creating index: title_text', out)
        self.assertEqual(len(self.fake.indexes), 1)
        self.assertEqual(self.fake.indexes[0][1],
                         {'default_language': 'italian'})

        # it replaces the previous indexes
        self.call('cms_search_create_mongo_index', '-y',
                  '-default_language', 'english')
        self.assertEqual(self.fake.indexes[0][1],
                         {'default_language': 'english'})

    @mock.patch('builtins.input', side_effect=['maybe', 'N'])
    def test_create_mongo_index_not_confirmed(self, mocked_input):
        out = self.call('cms_search_create_mongo_index')
        self.assertEqual(out, '')
        self.assertEqual(mocked_input.call_count, 2)
        self.assertEqual(self.fake.indexes, [])

    @mock.patch('builtins.input', return_value='y')
    def test_create_mongo_index_confirmed(self, mocked_input):
        self.call('cms_search_create_mongo_index')
        self.assertEqual(len(self.fake.indexes), 1)

    def test_content_sync_pages(self):
        page = self.create_page()
        draft = self.create_page(state='draft')
        restricted = self.create_page()
        restricted.webpath.access = '2'
        restricted.webpath.save()
        page_se_insert(page)
        stale = self.fake.docs[0]['_id']
        year = page.date_start.year

        out = self.call('cms_search_content_sync', '-y', str(year),
                        '-type', 'cmspages.Page', '-insert')
        self.assertIn('-- Inserted 1 elements. --', out)
        docs = self.docs_of(page)
        self.assertEqual(len(docs), 1)
        self.assertNotEqual(docs[0]['_id'], stale)
        self.assertEqual(self.docs_of(draft), [])
        self.assertEqual(self.docs_of(restricted), [])

        # show
        out = self.call('cms_search_content_sync', '-y', str(year),
                        '-m', str(page.date_start.month),
                        '-d', str(page.date_start.day),
                        '-type', 'cmspages.Page', '-show')
        self.assertIn('-- 1 elements. --', out)
        self.assertIn(page.name, out)

        # purge and insert: old entries are replaced
        out = self.call('cms_search_content_sync', '-y', str(year),
                        '-type', 'cmspages.Page', '-purge', '-insert')
        self.assertIn('-- Inserted 1 elements. --', out)
        self.assertIn('-- Deleted 1 elements. --', out)
        self.assertEqual(len(self.docs_of(page)), 1)

        # purge only
        out = self.call('cms_search_content_sync', '-y', str(year),
                        '-type', 'cmspages.Page', '-purge')
        self.assertIn('-- Deleted 1 elements. --', out)
        self.assertEqual(self.fake.docs, [])

    def test_content_sync_publications(self):
        pub = self.create_pub()
        year = pub.get_publication_context().date_start.year
        out = self.call('cms_search_content_sync', '-y', str(year),
                        '-type', 'cmspublications.Publication', '-insert')
        self.assertIn('-- Inserted 1 elements. --', out)
        self.assertEqual(self.docs_of(pub)[0]['title'], pub.title)

    def test_content_sync_purge_other_years(self):
        page = self.create_page()
        page_se_insert(page)
        # different year: nothing to purge
        out = self.call('cms_search_content_sync', '-y', '1999', '-purge')
        self.assertIn('-- Deleted 0 elements. --', out)
        self.assertEqual(len(self.fake.docs), 1)


class MongoClientFactoryTest(TestCase):

    def setUp(self):
        old_client = MongoClientFactory.mongo_client
        self.addCleanup(setattr, MongoClientFactory, 'mongo_client', old_client)
        MongoClientFactory.mongo_client = None

    @mock.patch('cms.search.pymongo.MongoClient')
    def test_mongo_collection(self, mongo_client):
        collection = mongo_collection()
        mongo_client.assert_called_with(settings.MONGO_URL,
                                        **settings.MONGO_CONNECTION_PARAMS)
        client = mongo_client.return_value
        self.assertIs(MongoClientFactory.mongo_client, client)
        db = getattr(client, settings.MONGO_DB_NAME)
        self.assertIs(collection, getattr(db, settings.MONGO_COLLECTION_NAME))
