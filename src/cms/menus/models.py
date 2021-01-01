from copy import deepcopy

from django.db import models
from django.utils.translation import gettext_lazy as _

from cms.contexts.models import *
from cms.templates.models import (CMS_TEMPLATE_BLOCK_SECTIONS,
                                  ActivableModel,
                                  SectionAbstractModel,
                                  SortableModel,
                                  TimeStampedModel)

class AbstractImportableMenu(object):
    
    def import_childs(self, child_list) -> bool:
        """
        create menu items importing a dictionary
        """
        items = deepcopy(child_list)
        for item in child_list:
            if not item: continue
            
            for i in 'link', 'parent_id', 'menu_id':
                item.pop(i, None)
            item['menu'] = self.get_menu()
            childs = item.pop('childs', None)
            
            if item.get('webpath_id', None):
                item['webpath'] = WebPath.objects.get(pk=item['webpath_id'])
            
            if isinstance(self, NavigationBarItem):
                item['parent'] = self
            obj = NavigationBarItem.objects.create(**item)
            if childs:
                obj.import_childs(childs)
        return True


class NavigationBar(TimeStampedModel, ActivableModel, CreatedModifiedBy,
                    AbstractImportableMenu):
    name = models.CharField(max_length=33, blank=False, null=False)

    class Meta:
        verbose_name_plural = _("Context Navigation Menus")


    def get_items(self, lang=settings.LANGUAGE, **kwargs):
        items = []
        for i in NavigationBarItem.objects.filter(menu=self,
                                                  is_active=True,
                                                  **kwargs).\
                                           order_by('order'):
            items.append(i.localized(lang=lang))
        return items

    def serialize(self, lang=settings.LANGUAGE):
        data = []
        for child in NavigationBarItem.objects.filter(is_active=True,
                                                      menu = self,
                                                      parent = None):
            data.append(child.serialize(deep=True, lang=lang))
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
                             null=True, blank=True,
                             on_delete=models.CASCADE,
                             related_name="related_menu")
    name = models.CharField(max_length=60, blank=False, null=False)
    webpath = models.ForeignKey(WebPath,
                             null=True, blank=True,
                             on_delete=models.CASCADE,
                             related_name="linked_page")
    parent = models.ForeignKey('NavigationBarItem',
                               null=True, blank=True,
                               on_delete=models.CASCADE,
                               related_name="related_parent")
    url = models.CharField(help_text=_("url"),
                           null=True, blank=True, max_length=2048)
    publication = models.ForeignKey('cmspublications.Publication',
                                    null=True, blank=True,
                                    related_name='pub',
                                    on_delete=models.CASCADE)
    inherited_content = models.ForeignKey('cmspublications.Publication',
                                          null=True, blank=True,
                                          related_name='inherited_content',
                                          on_delete=models.CASCADE,
                                          help_text=_("Takes additional "
                                                      "contents from a "
                                                      "publication"))

    class Meta:
        verbose_name_plural = _("Context Navigation Menu Items")
        ordering = ('order',)


    @property
    def link(self):
        if self.url:
            return self.url
        elif self.webpath:
            if self.publication:
                return self.publication.get_publication_context(webpath=self.webpath).url
            else:
                return self.webpath.get_full_path()
        else: # pragma: no cover
            return ''
        
    def localized(self, lang=settings.LANGUAGE, **kwargs):
        i18n = NavigationBarItemLocalization.objects.filter(item=self,
                                                            language=lang).first()
        if i18n: # pragma: no cover
            self.name = i18n.name
            self.language = lang
        else:
            self.language = None
        return self

    def serialize(self, lang=settings.LANGUAGE, deep=False):
        data = dict(
                    menu_id = self.menu.pk,
                    parent_id = getattr(self.parent, 'pk', None),
                    name = self.name,
                    url = self.url,
                    publication_id = self.publication.pk if self.publication else None,
                    webpath_id = self.webpath.pk if self.webpath else None,
                    link = self.link,
                    is_active = self.is_active,
                    order = self.order
        )
        if deep:
            data['childs'] = []
            for child in self.get_childs(lang=lang):
                data['childs'].append(child.serialize(deep=deep))
        return data


    def get_childs(self, lang=settings.LANGUAGE):
        items = NavigationBarItem.objects.filter(is_active=True,
                                                 parent=self,
                                                 menu=self.menu).\
                                          order_by('order')
        if getattr(self, 'language', lang):
            for item in items:
                item.localized(lang)
        return items


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


    def __str__(self):
        return '{}: {} ({})'.format(self.menu,
                                    self.name,
                                    getattr(self.parent, 'name', ''))


class NavigationBarItemLocalization(CreatedModifiedBy):
    item = models.ForeignKey(NavigationBarItem,
                             on_delete=models.CASCADE)
    language   = models.CharField(choices=settings.LANGUAGES,
                                  max_length=12, null=False,blank=False,
                                  default='en')
    name = models.CharField(max_length=33, blank=False, null=False)

    class Meta:
        verbose_name_plural = _("Context Navigation Menu Item Localizations")

    def __str__(self):
        return '{} - {}'.format(self.item, self.language)
