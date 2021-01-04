import os
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand

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
        parser.epilog = 'Example: ./manage.py unicms_collect_templates'
        parser.add_argument('-y', required=False, action="store_true",
                            help="clean up preexistent folders")

    def handle(self, *args, **options):
        if options['y'] or confirm():
            # if options['renew'] and os.path.isdir(CMS_TEMPLATES_FOLDER):
            if not os.path.isdir(CMS_TEMPLATES_FOLDER):
                os.makedirs(f'{CMS_TEMPLATES_FOLDER}')
            for target in 'blocks', 'pages':
                if os.path.isdir(f'{CMS_TEMPLATES_FOLDER}/{target}'):
                    shutil.rmtree(f'{CMS_TEMPLATES_FOLDER}/{target}')
                os.makedirs(f'{CMS_TEMPLATES_FOLDER}/{target}')

            # admin templates
            if not os.path.isdir('templates/admin'):
                os.makedirs('templates/admin')

            for i in get_unicms_templates():
                if i[1] == 'admin/':
                    dest = f"templates/{''.join(i[1:])}"
                else:
                    dest = f"{CMS_TEMPLATES_FOLDER}/{''.join(i[1:])}"
                src = ''.join(i)
                print(f'Copying {src} -> {dest}')
                if os.path.exists(f"{dest}"):
                    os.remove(f"{dest}")
                try:
                    os.symlink(src, dest)
                except FileExistsError as e:
                    print(f'ERROR {e}: File Already Exists: {src} -> {dest}')
                # shutil.copyfile(src, dest)
