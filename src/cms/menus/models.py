from copy import deepcopy

from django.utils.translation import gettext_lazy as _

from cms.api.utils import check_user_permission_on_object
from cms.contexts.models import WebPath, models, settings
from cms.contexts.models_abstract import AbstractLockable
from cms.templates.models import (ActivableModel,
                                  CreatedModifiedBy,
                                  SortableModel,
                                  TimeStampedModel)


class AbstractImportableMenu(object):

    def import_childs(self, child_list) -> bool:
        """
        create menu items importing a dictionary
        """
        items = deepcopy(child_list)
        for item in items:
            if not item: continue

            for i in 'link', 'parent_id', 'parent_name', 'menu_id', 'level':
                item.pop(i, None)
            item['menu'] = self.get_menu()
            childs = item.pop('childs', None)

            if item.get('webpath_id', None):
                item['webpath'] = WebPath.objects.get(pk=item['webpath_id'])

            obj = NavigationBarItem.objects.create(**item)
            if isinstance(self, NavigationBarItem):
                obj.parent = self
                obj.save()
            if childs:
                obj.import_childs(childs)
        return True


class NavigationBar(TimeStampedModel, ActivableModel, CreatedModifiedBy,
                    AbstractImportableMenu, AbstractLockable):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = _("Context Navigation Menus")

    def get_items(self, lang=settings.LANGUAGE, **kwargs):
        items = []
        for i in NavigationBarItem.objects.filter(menu=self,
                                                  is_active=True,
                                                  **kwargs).order_by('order'):
            items.append(i.localized(lang=lang))
        return items

    def serialize(self, lang=settings.LANGUAGE, only_active=True):
        data = []
        childs = NavigationBarItem.objects.filter(menu=self, parent=None)
        if only_active:
            childs = childs.filter(is_active=True)
        for child in childs:
            ser_child = child.serialize(deep=True, lang=lang, only_active=only_active)
            data.append(ser_child)
        return dict(name=self.name, is_active=self.is_active, childs=data)

    def get_menu(self):
        return self

    def __str__(self):
        return '{}'.format(self.name)


class NavigationBarItem(TimeStampedModel, SortableModel, ActivableModel,
                        CreatedModifiedBy, AbstractImportableMenu):
    """
    elements that builds up the navigation menu
    """
    menu = models.ForeignKey(NavigationBar,
                             on_delete=models.CASCADE,
                             related_name="related_menu")
    name = models.CharField(max_length=60)
    webpath = models.ForeignKey(WebPath,
                                null=True, blank=True,
                                on_delete=models.SET_NULL,
                                related_name="linked_page")
    parent = models.ForeignKey('NavigationBarItem',
                               null=True, blank=True,
                               on_delete=models.CASCADE,
                               related_name="related_parent")
    url = models.CharField(help_text=_("url"),
                           default='', blank=True, max_length=2048)
    publication = models.ForeignKey('cmspublications.Publication',
                                    null=True, blank=True,
                                    related_name='pub',
                                    on_delete=models.SET_NULL)
    inherited_content = models.ForeignKey('cmspublications.Publication',
                                          null=True, blank=True,
                                          related_name='inherited_content',
                                          on_delete=models.SET_NULL,
                                          help_text=_("Takes additional "
                                                      "contents from a "
                                                      "publication"))

    class Meta:
        verbose_name_plural = _("Context Navigation Menu Items")
        ordering = ('order',)

    def save(self, *args, **kwargs):
        if self.parent == self or self.item_in_childs(self.parent):
            raise Exception(_("Can't choose a child as parent!"))
        super(self.__class__, self).save(*args, **kwargs)

    # @property
    def link(self, request=None):
        if self.url:
            return self.url
        elif self.webpath:
            # does it have sense?
            # if self.publication:
                # ctx_webpath = self.publication.get_publication_context(webpath=self.webpath)
                # return ctx_webpath.url if ctx_webpath else ''
            # else:
            # return self.webpath.get_full_path()
            return self.webpath.get_site_path(request)
        else: # pragma: no cover
            return ''

    def localized(self, lang=settings.LANGUAGE, **kwargs):
        i18n = NavigationBarItemLocalization.objects.filter(item=self,
                                                            language=lang,
                                                            is_active=True)\
                                                    .first()
        if i18n: # pragma: no cover
            self.name = i18n.name
            self.language = lang
        else:
            self.language = None
        return self

    def serialize(self, lang=settings.LANGUAGE, deep=False,
                  level=0, only_active=True):
        data = dict(
            id=self.pk,
            menu_id=self.menu_id,
            parent_id=getattr(self.parent, 'pk', None),
            parent_name=getattr(self.parent, 'name', None),
            name=self.name,
            url=self.url,
            publication_id=self.publication_id if self.publication else None,
            webpath_id=self.webpath_id if self.webpath else None,
            link=self.link(),
            is_active=self.is_active,
            order=self.order,
            level=level,
        )
        if deep:
            data['childs'] = []
            for child in self.get_childs(lang=lang, only_active=only_active):
                ser_child = child.serialize(deep=deep, level=level + 1,
                                            only_active=only_active)
                data['childs'].append(ser_child)
        return data

    def get_childs(self,
                   lang=settings.LANGUAGE,
                   only_active=True,
                   exclude=None):
        if self.pk:
            items = NavigationBarItem.objects.filter(parent=self,
                                                     menu=self.menu).\
                                              order_by('order')
            if only_active:
                items = items.filter(is_active=True)
            if exclude:
                items = items.exclude(pk=exclude.pk)
            # if getattr(self, 'language', lang):
            for item in items:
                item.localized(lang)
            return items
        return None

    def item_in_childs(self, item):
        """
        tells us if a menu item is in self childs tree
        """
        if not item: return False
        childs = self.get_childs(only_active=False)
        if not childs: return False
        if item in childs:
            return True
        for child in childs:
            if child.item_in_childs(item): return True
        return False # pragma: no cover

    def get_menu(self):
        return self.menu

    def has_childs(self):
        return True if NavigationBarItem.objects.filter(is_active=True,
                                                        parent=self,
                                                        menu=self.menu) else False

    def childs_count(self):
        return NavigationBarItem.objects.filter(is_active=True,
                                                parent=self,
                                                menu=self.menu).count()

    def get_siblings_count(self):
        count = NavigationBarItem.objects.filter(parent=self.parent,
                                                 is_active=True).count()
        return count

    def is_lockable_by(self, user):
        item = self.menu
        permission = check_user_permission_on_object(user=user, obj=item)
        return permission['granted']

    def __str__(self):
        return '{}: {} ({})'.format(self.menu,
                                    self.name,
                                    getattr(self.parent, 'name', ''))


class NavigationBarItemLocalization(ActivableModel, TimeStampedModel,
                                    CreatedModifiedBy):
    item = models.ForeignKey(NavigationBarItem,
                             on_delete=models.CASCADE)
    language = models.CharField(choices=settings.LANGUAGES, max_length=12, default='en')
    name = models.CharField(max_length=33)

    class Meta:
        verbose_name_plural = _("Context Navigation Menu Item Localizations")

    def is_lockable_by(self, user):
        item = self.item.menu
        permission = check_user_permission_on_object(user=user, obj=item)
        return permission['granted']

    def __str__(self):
        return '{} - {}'.format(self.item, self.language)
