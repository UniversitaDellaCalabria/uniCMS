import os
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from cms.templates.utils import get_unicms_templates
from cms.templates import settings as app_settings


CMS_TEMPLATES_FOLDER = getattr(settings, 'CMS_TEMPLATES_FOLDER',
                               app_settings.CMS_TEMPLATES_FOLDER)


def confirm():
    """
    Ask user to enter Y or N (case-insensitive).
    :return: True if the answer is Y.
    :rtype: bool
    """
    answer = ""
    while answer not in ["y", "n"]:
        answer = input("OK to push to continue [Y/N]? ").lower()
    return answer == "y"


class Command(BaseCommand):
    help = 'uniCMS symlink templates'

    def add_arguments(self, parser):
        parser.epilog='Example: ./manage.py unicms_symlink_templates'
        parser.add_argument('-renew', required=False, action="store_true",
                            help="clean up preexistent folders")
                                              
    def handle(self, *args, **options):
        if confirm():
            if options['renew'] and os.path.isdir(CMS_TEMPLATES_FOLDER):
                shutil.rmtree(CMS_TEMPLATES_FOLDER)
            if not os.path.isdir(CMS_TEMPLATES_FOLDER):
                os.mkdir(f'{CMS_TEMPLATES_FOLDER}')
                os.mkdir(f'{CMS_TEMPLATES_FOLDER}/blocks')
                os.mkdir(f'{CMS_TEMPLATES_FOLDER}/pages')
            
            for i in get_unicms_templates():
                dest = f"{CMS_TEMPLATES_FOLDER}/{''.join(i[1:])}"
                src = ''.join(i)
                print(f'Copying {src} -> {dest}')
                os.symlink(src, dest)
                # shutil.copyfile(src, dest)
