import logging
import os

from django.utils.translation import gettext_lazy as _

from glob import glob

logger = logging.getLogger(__name__)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = os.getcwd()

CMS_BLOCK_TYPES = (
                   ('cms.templates.blocks.HtmlBlock', 'HTML Block'),
                   ('cms.templates.blocks.JSONBlock', 'JSON Block'),
                   ('cms.templates.blocks.CarouselPlaceholderBlock', 'Carousel Placeholder Block'),
                   ('cms.templates.blocks.ContactPlaceholderBlock', 'Contact Placeholder Block'),
                   ('cms.templates.blocks.HeadingPlaceholderBlock', 'Headings Placeholder Block'),
                   ('cms.templates.blocks.LinkPlaceholderBlock', 'Link Placeholder Block'),
                   ('cms.templates.blocks.MediaPlaceholderBlock', 'Media Placeholder Block'),
                   ('cms.templates.blocks.MediaCollectionPlaceholderBlock', 'Media Collection Placeholder Block'),
                   ('cms.templates.blocks.MenuPlaceholderBlock', 'Menu Placeholder Block'),
                   ('cms.templates.blocks.PublicationContentPlaceholderBlock', 'Publication Content Placeholder Block'),
)

CMS_TEMPLATES_FOLDER = f'{BASE_DIR}/templates/unicms'
CMS_BLOCK_TEMPLATES = []
blocks_templates_files = [glob(f"{CMS_TEMPLATES_FOLDER}/blocks/*.html")]
for i in blocks_templates_files[0]:
    fname = i.split(os.path.sep)[-1]
    CMS_BLOCK_TEMPLATES.append((fname, fname))

CMS_PAGE_TEMPLATES = []
pages_templates_files = [glob(f"{CMS_TEMPLATES_FOLDER}/pages/*.html")]
for i in pages_templates_files[0]:
    fname = i.split(os.path.sep)[-1]
    CMS_PAGE_TEMPLATES.append((fname, fname))
CMS_PAGE_TEMPLATES = sorted(CMS_PAGE_TEMPLATES)

if CMS_BLOCK_TEMPLATES:
    _elements = '\n  '.join([i[1] for i in CMS_BLOCK_TEMPLATES])
    logger.info('Loading block template files:{}'.format(_elements))
else: # pragma: no cover
    logger.warning('Block template files not found')

if CMS_PAGE_TEMPLATES:
    _elements = ','.join([i[1] for i in CMS_PAGE_TEMPLATES])
    logger.info('Loading page template files: {}'.format(_elements))
else: # pragma: no cover
    logger.warning('Page template files not found')

CMS_LINKS_LABELS = (('view', _('View')),
                    ('open', _('Open')),
                    ('read more', _('Read More')),
                    ('more', _('More')),
                    ('get in', _('Get in')),
                    ('enter', _('Enter')),
                    ('submit', _('Submit')),
                    ('custom', _('custom'))
                  )
