from unittest import mock

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

from cms.api.settings import FORM_SOURCE_LABEL
from cms.carousels.models import Carousel
from cms.pages import tests as pages_tests
from cms.pages.models import PageCarousel
from cms.publications.models import Category, Publication

from . import tests as context_tests
from . forms import (EditorialBoardLockUserForm,
                     PublicationContextForm,
                     WebPathCloneForm,
                     WebPathForm)
from . hooks import used_by
from . models import EntryUsedBy, WebPath


class UsedByHookTest(TestCase):

    def setUp(self):
        # no search engine updates on pages/publications save
        patcher = mock.patch('cms.search.hooks.mongo_collection')
        patcher.start()
        self.addCleanup(patcher.stop)

    def _entries(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        return EntryUsedBy.objects.filter(used_by_content_type=ct,
                                          used_by_object_id=obj.pk)

    def test_used_by_page(self):
        page = pages_tests.PageUnitTest.create_page()
        EntryUsedBy.objects.all().delete()
        used_by(page)

        entries = self._entries(page)
        used = [entry.object for entry in entries]
        # foreign keys
        self.assertIn(page.webpath, used)
        self.assertIn(page.base_template, used)
        # inlines
        self.assertIn(PageCarousel.objects.get(page=page), used)
        # users and tags are excluded
        self.assertNotIn(page.created_by, used)

        # no duplicates on next calls
        count = entries.count()
        used_by(page)
        self.assertEqual(self._entries(page).count(), count)

    def test_used_by_m2m(self):
        category = Category.objects.create(name='cat', description='desc')
        publication = Publication.objects.create(name='pub', title='title',
                                                 is_active=True)
        publication.category.add(category)
        EntryUsedBy.objects.all().delete()
        used_by(publication)
        self.assertEqual([e.object for e in self._entries(publication)],
                         [category])


class AbstractLockableTest(TestCase):

    def test_is_lockable_by(self):
        # Carousel doesn't override AbstractLockable.is_lockable_by
        carousel = Carousel.objects.create(name='carousel', is_active=True)
        superuser = context_tests.ContextUnitTest.create_user(username='admin',
                                                              is_superuser=True)
        user = context_tests.ContextUnitTest.create_user()
        self.assertTrue(carousel.is_lockable_by(superuser))
        self.assertFalse(carousel.is_lockable_by(user))


class FormsTest(TestCase):

    def setUp(self):
        self.site = context_tests.ContextUnitTest.create_website()
        self.other_site = context_tests.ContextUnitTest.create_website(
            name='other.org', domain='other.org', is_active=False)
        self.root = context_tests.ContextUnitTest.create_webpath(path='/')
        self.child = WebPath.objects.create(name='child', path='child',
                                            parent=self.root)
        self.other_root = WebPath.objects.create(name='root', path='/',
                                                 site=self.other_site)
        self.options_url = reverse('unicms_api:webpath-options',
                                   kwargs={'site_id': self.site.pk})

    def test_lock_user_form(self):
        staff = context_tests.ContextUnitTest.create_user(username='staff',
                                                          is_staff=True)
        context_tests.ContextUnitTest.create_user()
        form = EditorialBoardLockUserForm()
        self.assertEqual(list(form.fields['user'].queryset), [staff])

    def test_webpath_form(self):
        form = WebPathForm()
        self.assertEqual(form.fields['parent'].queryset.count(), 3)
        self.assertFalse(hasattr(form.fields['parent'], FORM_SOURCE_LABEL))

        form = WebPathForm(site_id=self.site.pk)
        self.assertEqual(list(form.fields['site'].queryset), [self.site])
        self.assertEqual(set(form.fields['parent'].queryset),
                         {self.root, self.child})
        self.assertEqual(getattr(form.fields['parent'], FORM_SOURCE_LABEL),
                         self.options_url)
        self.assertEqual(getattr(form.fields['alias'], FORM_SOURCE_LABEL),
                         self.options_url)

    def test_publication_context_form(self):
        pubs_url = reverse('unicms_api:editorial-board-publications-options')

        form = PublicationContextForm()
        self.assertEqual(getattr(form.fields['publication'], FORM_SOURCE_LABEL),
                         pubs_url)
        self.assertFalse(hasattr(form.fields['webpath'], FORM_SOURCE_LABEL))

        form = PublicationContextForm(site_id=self.site.pk)
        self.assertEqual(set(form.fields['webpath'].queryset),
                         {self.root, self.child})
        self.assertEqual(getattr(form.fields['webpath'], FORM_SOURCE_LABEL),
                         self.options_url)

        form = PublicationContextForm(site_id=self.site.pk,
                                      webpath_id=self.child.pk)
        self.assertEqual(list(form.fields['webpath'].queryset), [self.child])

        # webpath of another site
        form = PublicationContextForm(site_id=self.site.pk,
                                      webpath_id=self.other_root.pk)
        self.assertFalse(form.fields['webpath'].queryset.exists())

    def test_webpath_clone_form(self):
        form = WebPathCloneForm(site_id=self.site.pk)
        # only webpaths of active sites
        self.assertEqual(set(form.fields['parent'].queryset),
                         {self.root, self.child})
        self.assertEqual(getattr(form.fields['parent'], FORM_SOURCE_LABEL),
                         reverse('unicms_api:webpath-all-options'))
