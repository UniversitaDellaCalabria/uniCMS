import logging
import random
import string

from django.utils.safestring import SafeString

from cms.contexts.utils import handle_faulty_templates


logger = logging.getLogger(__name__)


class AbstractPlaceholder(object):
    collection_name = 'entries'

    def __init__(self, context:dict, template:str):
        self.request = context['request']
        self.block = context.get('block', None)
        self.page = context['page']
        self.webpath = context['webpath']
        self.template = template

        # i18n
        self.language = getattr(self.request, 'LANGUAGE_CODE', '')

    @property
    def iam(self):
        return self.__class__.__name__

    def hook(self):
        pass

    @property
    def log_msg(self): # pragma: no cover
        return f'Template Tag {self.iam}'

    def get_entry(self, entry):
        return entry[1]

    def is_runnable(self):
        if not self.block: # pragma: no cover
            logger.warning(f'{self.iam} cannot get a block object')
            return SafeString('')
        if not getattr(self, self.collection_name, None):  # pragma: no cover
            return SafeString('')

        return self.get_placeholders()

    def have_valid_placeholders(self):
        if not self.ph: # pragma: no cover
            _msg = f"{self.log_msg} doesn't have any page {self.collection_name}"
            logger.warning(_msg)
            return SafeString('')
        return True

    def get_placeholders(self):
        blocks = self.page.get_blocks()
        self.ph = [i for i in blocks
                   if i.type == self.ph_name]
        return self.have_valid_placeholders()

    def __call__(self):
        is_runnable = self.is_runnable()
        if not is_runnable: # pragma: no cover
            return is_runnable

        # call optional customizations
        self.hook()

        for i in zip(self.ph, getattr(self, self.collection_name, [])):
            self.entry = self.get_entry(i)
            if self.block.__class__.__name__ == i[0].type.split('.')[-1]:
                # already rendered
                if getattr(self.entry, '_published', False): # pragma: no cover
                    continue

                data = self.build_data_dict()
                self.entry._published = True

                # return first occourrence
                return handle_faulty_templates(self.template, data, name=self.iam)


class CarouselPlaceHolder(AbstractPlaceholder):
    collection_name = 'carousels'
    ph_name = 'cms.templates.blocks.CarouselPlaceholderBlock'

    def __init__(self,
                 context:dict, template:str = 'italia_hero_slider.html'):
        super().__init__(context, template)
        self.carousels = self.page.get_carousels()

    def build_identifier(self):
        # random identifier using random.choices()
        N = 4
        # generating random strings
        choices = random.choices(string.ascii_lowercase + string.digits, k = N)
        self.identifier = ''.join(choices)

    def hook(self):
        self.build_identifier()

    def build_data_dict(self):
        return {'carousel_items': self.entry.carousel.get_items(self.language),
                'carousel_identifier': self.identifier}


class LinkPlaceHolder(AbstractPlaceholder):
    collection_name = 'links'
    ph_name = 'cms.templates.blocks.LinkPlaceholderBlock'

    def __init__(self,
                 context:dict, template:str = 'italia_iframe_16by9.html'):
        super().__init__(context, template)
        self.links = self.page.get_links()

    def build_data_dict(self):
        return {'link': self.entry.url}


class MediaPlaceHolder(AbstractPlaceholder):
    collection_name = 'medias'
    ph_name = 'cms.templates.blocks.MediaPlaceholderBlock'

    def __init__(self,
                 context:dict, template:str = 'italia_image.html'):
        super().__init__(context, template)
        self.medias = self.page.get_medias()

    def build_data_dict(self):
        return {'media': self.entry.media, 'url': self.entry.url}


class MenuPlaceHolder(AbstractPlaceholder):
    collection_name = 'menus'
    ph_name = 'cms.templates.blocks.MenuPlaceholderBlock'

    def __init__(self,
                 context:dict, template:str = 'italia_main_menu.html'):
        super().__init__(context, template)
        self.menus = self.page.get_menus()

    def build_data_dict(self):
        return {'items': self.entry.menu.get_items(lang=self.language,
                                                   parent__isnull=True)}


class PublicationPlaceHolder(AbstractPlaceholder):
    collection_name = 'publications'
    ph_name = 'cms.templates.blocks.PublicationContentPlaceholderBlock'

    def __init__(self,
                 context:dict, template:str = 'ph_publication_style_1.html'):
        super().__init__(context, template)
        self.publications = self.page.get_publications()

    def get_entry(self, entry):
        return entry[1].publication

    def build_data_dict(self):
        self.entry.translate_as(lang=self.language)
        return {'publication': self.entry, 'webpath': self.webpath}


def load_media_placeholder(*args, **kwargs):
    return MediaPlaceHolder(*args, **kwargs)()


def load_menu_placeholder(*args, **kwargs):
    return MenuPlaceHolder(*args, **kwargs)()


def load_carousel_placeholder(*args, **kwargs):
    return CarouselPlaceHolder(*args, **kwargs)()


def load_link_placeholder(*args, **kwargs):
    return LinkPlaceHolder(*args, **kwargs)()


def load_publication_content_placeholder(*args, **kwargs):
    return PublicationPlaceHolder(*args, **kwargs)()
