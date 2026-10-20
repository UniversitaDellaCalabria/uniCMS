from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory, TestCase

from . exceptions import ReservedWordException
from . models import (EditorialBoardEditors,
                      EditorialBoardLock,
                      EditorialBoardLockUser,
                      EntryUsedBy,
                      WebPath,
                      WebSite)
from . import tests as context_tests


class WebSiteModelTest(TestCase):

    def setUp(self):
        self.site = context_tests.ContextUnitTest.create_website()
        self.user = context_tests.ContextUnitTest.create_user()

    def test_serialize_and_str(self):
        self.assertEqual(self.site.serialize(),
                         {'id': self.site.pk,
                          'name': 'example.org',
                          'domain': 'example.org',
                          'is_active': True})
        self.assertEqual(str(self.site), 'example.org')

    def test_is_managed_by(self):
        # no permissions at all
        self.assertFalse(self.site.is_managed_by(self.user))

        # superuser
        superuser = context_tests.ContextUnitTest.create_user(username='admin',
                                                is_superuser=True)
        self.assertTrue(self.site.is_managed_by(superuser))

        webpath = context_tests.ContextUnitTest.create_webpath()
        # zero permission doesn't count
        ebe = EditorialBoardEditors.objects.create(user=self.user,
                                                   webpath=webpath,
                                                   permission=0,
                                                   is_active=True)
        self.assertFalse(self.site.is_managed_by(self.user))

        # inactive permission doesn't count
        ebe.permission = 4
        ebe.is_active = False
        ebe.save()
        self.assertFalse(self.site.is_managed_by(self.user))

        ebe.is_active = True
        ebe.save()
        self.assertTrue(self.site.is_managed_by(self.user))

        # permission on a webpath of another site
        other_site = context_tests.ContextUnitTest.create_website(name='other.org',
                                                    domain='other.org',
                                                    is_active=True)
        self.assertFalse(other_site.is_managed_by(self.user))


class WebPathModelTest(TestCase):

    def setUp(self):
        self.site = context_tests.ContextUnitTest.create_website()
        self.root = context_tests.ContextUnitTest.create_webpath(name='root', path='/')

    def _child(self, parent, path, **kwargs):
        return WebPath.objects.create(name=path, parent=parent,
                                      path=path, is_active=True, **kwargs)

    def test_path_normalization(self):
        child = self._child(self.root, 'a//b')
        self.assertEqual(child.path, 'a/b/')
        self.assertEqual(child.fullpath, '/a/b/')
        self.assertEqual(child.site, self.site)
        self.assertEqual(child.split(), ['a', 'b', ''])
        self.assertEqual(child.get_parent_fullpath(), '/')
        self.assertEqual(self.root.get_parent_fullpath(), '')
        self.assertEqual(str(child), 'a//b @ example.org/a/b/')

        # empty path becomes '/'
        empty = WebPath(name='empty', path='', site=self.site, parent=self.root)
        with self.assertRaisesMessage(Exception, 'Existent path "/"'):
            empty.save()

    def test_get_site_path(self):
        child = self._child(self.root, 'news')
        self.assertEqual(child.get_absolute_url(), '//example.org/news/')

        request = RequestFactory().get('/', SERVER_PORT='8000')
        self.assertEqual(child.get_site_path(request),
                         '//example.org:8000/news/')
        for port in ('80', '443'):
            request = RequestFactory().get('/', SERVER_PORT=port)
            self.assertEqual(child.get_site_path(request),
                             '//example.org/news/')

        # aliases return their redirect url
        alias = self._child(self.root, 'alias', alias=child)
        self.assertEqual(alias.get_site_path(), '/news/')
        alias.alias = None
        alias.alias_url = 'https://other.org'
        self.assertEqual(alias.get_site_path(), 'https://other.org')

    def test_alias_and_alias_url(self):
        child = self._child(self.root, 'news')
        # alias_url wins over alias
        alias = self._child(self.root, 'alias', alias=child,
                            alias_url='https://other.org')
        alias.refresh_from_db()
        self.assertIsNone(alias.alias)
        self.assertEqual(alias.get_full_path(), 'https://other.org')

        with self.assertRaisesMessage(Exception, "Can't set himself as alias"):
            child.alias = child
            child.save()

    def test_reserved_words(self):
        with self.assertRaises(ReservedWordException):
            self._child(self.root, 'that/contents/news/view')
        self.assertFalse(WebPath.objects.filter(name='that/contents/news/view').exists())

        # check_fullpath alone
        self.assertIsNone(self.root.check_fullpath('/that/'))
        with self.assertRaises(ReservedWordException):
            self.root.check_fullpath('/a/contents/news/list/')

    def test_existent_fullpath(self):
        self._child(self.root, 'news')
        with self.assertRaisesMessage(Exception, 'Existent path "/news/"'):
            self._child(self.root, 'news/')
        # same path on a different site is allowed
        other_site = context_tests.ContextUnitTest.create_website(name='other.org',
                                                    domain='other.org',
                                                    is_active=True)
        other_root = WebPath.objects.create(name='root', path='/',
                                            site=other_site)
        other = self._child(other_root, 'news')
        self.assertEqual(other.site, other_site)

    def test_parent_loops(self):
        child = self._child(self.root, 'a')
        grandchild = self._child(child, 'b')

        with self.assertRaisesMessage(Exception, "Can't set himself as parent"):
            child.parent = child
            child.save()
        child.refresh_from_db()

        for node in (child, grandchild):
            self.root.parent = node
            with self.assertRaisesMessage(Exception,
                                          "Can't set one of its descendants as parent"):
                self.root.save()
        self.root.refresh_from_db()
        self.assertIsNone(self.root.parent)

        # saving again with the same parent doesn't run the loop check
        grandchild.name = 'renamed'
        grandchild.save()
        self.assertEqual(WebPath.objects.get(pk=grandchild.pk).name, 'renamed')

    def test_move_subtree(self):
        a = self._child(self.root, 'a')
        b = self._child(self.root, 'b')
        a1 = self._child(a, 'a1')
        a11 = self._child(a1, 'a11')

        # move a under b
        a.parent = b
        a.save()
        self.assertEqual(WebPath.objects.get(pk=a.pk).fullpath, '/b/a/')
        self.assertEqual(WebPath.objects.get(pk=a1.pk).fullpath, '/b/a/a1/')
        self.assertEqual(WebPath.objects.get(pk=a11.pk).fullpath, '/b/a/a1/a11/')

        # rename a
        a.path = 'renamed'
        a.save()
        self.assertEqual(WebPath.objects.get(pk=a11.pk).fullpath,
                         '/b/renamed/a1/a11/')

        # get_descendants is level ordered, is_descendant_of
        self.assertEqual(b.get_descendants(), [a, a1, a11])
        self.assertEqual(a11.get_descendants(), [])
        self.assertTrue(a11.is_descendant_of(b))
        self.assertTrue(a11.is_descendant_of(a11))
        self.assertFalse(b.is_descendant_of(a11))

    def test_move_subtree_to_another_site(self):
        a = self._child(self.root, 'a')
        a1 = self._child(a, 'a1')
        other_site = context_tests.ContextUnitTest.create_website(name='other.org',
                                                    domain='other.org',
                                                    is_active=True)
        # change the site of the root: all the subtree follows
        self.root.site = other_site
        self.root.save()
        self.assertEqual(WebPath.objects.get(pk=a.pk).site, other_site)
        self.assertEqual(WebPath.objects.get(pk=a1.pk).site, other_site)
        self.assertEqual(WebPath.objects.get(pk=a1.pk).fullpath, '/a/a1/')

    def test_save_without_path_changes(self):
        a = self._child(self.root, 'a')
        self.root.name = 'new name'
        self.root.save()
        self.assertEqual(WebPath.objects.get(pk=a.pk).fullpath, '/a/')

    def test_update_descendants_without_descendants(self):
        leaf = self._child(self.root, 'leaf')
        self.assertIsNone(leaf.update_descendants())
        # rename a leaf
        leaf.path = 'leaf2'
        leaf.save()
        self.assertEqual(WebPath.objects.get(pk=leaf.pk).fullpath, '/leaf2/')

    def test_descendant_conflict_rollback(self):
        a = self._child(self.root, 'a')
        a_z = self._child(a, 'z')
        a_z_k = self._child(a_z, 'k')
        b = self._child(self.root, 'b')
        # /b/y/z/ exists but /b/y/ does not
        b_yz = self._child(b, 'y/z')
        self.assertEqual(b_yz.fullpath, '/b/y/z/')

        # direct conflict on the node itself
        a.path = 'b'
        with self.assertRaisesMessage(Exception, 'Existent path "/b/"'):
            a.save()

        # moving 'a' under 'b' as 'y' is fine for 'a' (/b/y/)
        # but its child would become /b/y/z/ (taken)
        a.refresh_from_db()
        a.parent = b
        a.path = 'y'
        with self.assertRaisesMessage(Exception, 'Existent path "/b/y/z/"'):
            a.save()

        # atomic rollback: nothing changed
        a.refresh_from_db()
        self.assertEqual(a.fullpath, '/a/')
        self.assertEqual(a.parent, self.root)
        self.assertEqual(WebPath.objects.get(pk=a_z.pk).fullpath, '/a/z/')
        self.assertEqual(WebPath.objects.get(pk=a_z_k.pk).fullpath, '/a/z/k/')

        # without the conflicting node the move succeeds
        b_yz.delete()
        a.parent = b
        a.path = 'y'
        a.save()
        self.assertEqual(WebPath.objects.get(pk=a_z_k.pk).fullpath, '/b/y/z/k/')

    def test_descendant_reserved_word_rollback(self):
        contents = self._child(self.root, 'contents')
        tmp = self._child(self.root, 'tmp')
        tmp_view = self._child(tmp, 'view')
        tmp_view_leaf = self._child(tmp_view, 'leaf')

        # reserved word on the node itself
        tmp.path = 'contents/news/view'
        with self.assertRaises(ReservedWordException):
            tmp.save()

        # /contents/news/ is allowed, but its descendant would become
        # /contents/news/view/ (reserved)
        tmp.refresh_from_db()
        tmp.parent = contents
        tmp.path = 'news'
        with self.assertRaises(ReservedWordException):
            tmp.save()

        # atomic rollback
        tmp.refresh_from_db()
        self.assertEqual(tmp.fullpath, '/tmp/')
        self.assertEqual(tmp.parent, self.root)
        self.assertEqual(WebPath.objects.get(pk=tmp_view.pk).fullpath, '/tmp/view/')
        self.assertEqual(WebPath.objects.get(pk=tmp_view_leaf.pk).fullpath,
                         '/tmp/view/leaf/')

    def test_loops_in_data(self):
        a = self._child(self.root, 'a')
        b = self._child(a, 'b')
        # build a loop bypassing save()
        WebPath.objects.filter(pk=a.pk).update(parent=b)
        a.refresh_from_db()
        b.refresh_from_db()
        # traversals stop on loops
        self.assertEqual(a.get_descendants(), [b])
        self.assertFalse(b.is_descendant_of(self.root))
        self.assertTrue(b.is_descendant_of(a))

    def test_access_level(self):
        a = self._child(self.root, 'a')
        a1 = self._child(a, 'a1')
        # root inherits: public
        self.assertEqual(self.root.access, '1')
        self.assertEqual(a1.get_access_level(), '0')
        # registered users, inherited
        a.access = '2'
        a.save()
        a1.refresh_from_db()
        self.assertEqual(a1.get_access_level(), '2')
        # custom group (from settings.AUTH_USER_GROUPS)
        a1.access = 'matricola_studente'
        self.assertEqual(a1.get_access_level(), 'matricola_studente')
        # unknown values are public
        a1.access = 'unknown'
        self.assertEqual(a1.get_access_level(), '0')


class WebPathPermissionsTest(TestCase):

    def setUp(self):
        self.root = context_tests.ContextUnitTest.create_webpath(path='/')
        self.webpath = WebPath.objects.create(name='child', path='child',
                                              parent=self.root)
        self.user = context_tests.ContextUnitTest.create_user()
        self.other = context_tests.ContextUnitTest.create_user(username='other')
        self.superuser = context_tests.ContextUnitTest.create_user(username='admin',
                                                     is_superuser=True)

    def _perm(self, permission, webpath=None, user=None):
        return EditorialBoardEditors.objects.create(user=user or self.user,
                                                    webpath=webpath or self.webpath,
                                                    permission=permission,
                                                    is_active=True)

    def _lock(self, user):
        ct = ContentType.objects.get_for_model(self.webpath)
        lock = EditorialBoardLock.objects.create(content_type=ct,
                                                 object_id=self.webpath.pk)
        return EditorialBoardLockUser.objects.create(lock=lock, user=user)

    def test_no_user_and_superuser(self):
        for method in ('is_localizable_by', 'is_editable_by',
                       'is_publicable_by'):
            self.assertFalse(getattr(self.webpath, method)())
            self.assertTrue(getattr(self.webpath, method)(self.superuser))
        self.assertTrue(self.webpath.is_lockable_by(self.superuser))

    def test_without_permissions_and_locks(self):
        self.assertFalse(self.webpath.is_localizable_by(self.user))
        self.assertFalse(self.webpath.is_editable_by(self.user))
        self.assertFalse(self.webpath.is_publicable_by(self.user))
        self.assertFalse(self.webpath.is_lockable_by(self.user))

    def test_with_locks(self):
        self._lock(self.user)
        self.assertTrue(self.webpath.is_localizable_by(self.user))
        self.assertTrue(self.webpath.is_editable_by(self.user))
        self.assertTrue(self.webpath.is_publicable_by(self.user))
        self.assertFalse(self.webpath.is_publicable_by(self.user,
                                                       allow_locks=False))
        self.assertTrue(self.webpath.is_lockable_by(self.user))
        # lock owned by another user
        self.assertFalse(self.webpath.is_editable_by(self.other))

    def test_zero_permission_ignores_locks(self):
        self._perm(0)
        self._lock(self.user)
        self.assertFalse(self.webpath.is_localizable_by(self.user))
        self.assertFalse(self.webpath.is_editable_by(self.user))
        self.assertFalse(self.webpath.is_publicable_by(self.user))

    def test_translator(self):
        self._perm(1)
        self.assertTrue(self.webpath.is_localizable_by(self.user))
        self.assertFalse(self.webpath.is_editable_by(self.user))
        self.assertFalse(self.webpath.is_publicable_by(self.user))

    def test_editor_only_created_by(self):
        self._perm(3)
        self.assertTrue(self.webpath.is_localizable_by(self.user))
        self.assertFalse(self.webpath.is_editable_by(self.user))
        self.webpath.created_by = self.user
        self.assertTrue(self.webpath.is_editable_by(self.user))
        self.assertFalse(self.webpath.is_publicable_by(self.user))

    def test_editor(self):
        self._perm(4)
        self.assertTrue(self.webpath.is_editable_by(self.user))
        self.assertFalse(self.webpath.is_publicable_by(self.user))

    def test_publisher(self):
        self._perm(6)
        self.assertTrue(self.webpath.is_editable_by(self.user))
        self.assertTrue(self.webpath.is_publicable_by(self.user))
        self.assertTrue(self.webpath.is_lockable_by(self.user))

    def test_get_permission(self):
        get = EditorialBoardEditors.get_permission
        self.assertEqual(get(None, self.user), -1)
        self.assertEqual(get(self.webpath, None), -1)
        self.assertEqual(get(self.webpath, self.superuser), 7)
        self.assertEqual(get(self.webpath, self.user), -1)

        # global permissions (webpath=None): the max one
        EditorialBoardEditors.objects.create(user=self.user, permission=1,
                                             is_active=True)
        EditorialBoardEditors.objects.create(user=self.user, permission=3,
                                             is_active=True)
        self.assertEqual(get(self.webpath, self.user), 3)
        self.assertEqual(get(self.webpath, self.user, check_all=False), -1)

        # parent permission not on descendants: ignored
        parent_perm = self._perm(4, webpath=self.root)
        self.assertEqual(get(self.webpath, self.user, check_all=False), -1)
        self.assertEqual(get(self.root, self.user), 4)
        # parent permission on descendants
        parent_perm.permission = 5
        parent_perm.save()
        self.assertEqual(get(self.webpath, self.user), 5)

        # webpath permission wins
        perm = self._perm(1)
        self.assertEqual(get(self.webpath, self.user), 1)
        # zero is considered...
        perm.permission = 0
        perm.save()
        self.assertEqual(get(self.webpath, self.user), 0)
        # ... except when consider_zero=False
        self.assertEqual(get(self.webpath, self.user, consider_zero=False), 5)

    def test_str_and_serialize(self):
        perm = self._perm(4)
        self.assertEqual(str(perm), f'{self.user} 4 in {self.webpath}')
        self.assertEqual(perm.serialize(), {'webpath': str(self.webpath),
                                            'permission': 4})
        perm.webpath = None
        self.assertEqual(str(perm), f'{self.user} 4')


class LocksAndEntriesTest(TestCase):

    def test_locks(self):
        user = context_tests.ContextUnitTest.create_user()
        other = context_tests.ContextUnitTest.create_user(username='other')
        webpath = context_tests.ContextUnitTest.create_webpath()
        ct = ContentType.objects.get_for_model(webpath)
        lock = EditorialBoardLock.objects.create(content_type=ct,
                                                 object_id=webpath.pk)
        lock_user = EditorialBoardLockUser.objects.create(lock=lock,
                                                          user=user)
        self.assertEqual(str(lock), f'{ct} {webpath.pk}')
        self.assertEqual(str(lock_user), f'{lock} {user}')

        locks = EditorialBoardLockUser.get_object_locks(content_type=ct,
                                                        object_id=webpath.pk)
        self.assertEqual(list(locks), [lock_user])
        self.assertEqual(list(EditorialBoardLockUser.get_user_object_locks(
            user=user, content_type=ct, object_id=webpath.pk)), [lock_user])
        self.assertFalse(EditorialBoardLockUser.get_user_object_locks(
            user=other, content_type=ct, object_id=webpath.pk).exists())
        self.assertTrue(EditorialBoardLockUser.check_for_locks(webpath, user))
        self.assertFalse(EditorialBoardLockUser.check_for_locks(webpath, other))

    def test_entry_used_by(self):
        site = context_tests.ContextUnitTest.create_website()
        webpath = context_tests.ContextUnitTest.create_webpath()
        site_ct = ContentType.objects.get_for_model(site)
        webpath_ct = ContentType.objects.get_for_model(webpath)
        entry = EntryUsedBy.objects.create(content_type=site_ct,
                                           object_id=site.pk,
                                           used_by_content_type=webpath_ct,
                                           used_by_object_id=webpath.pk)
        self.assertEqual(entry.object, site)
        self.assertEqual(entry.used_by, webpath)
        self.assertEqual(str(entry),
                         f'{site_ct} {site.pk} used by {webpath_ct} {webpath.pk}')
