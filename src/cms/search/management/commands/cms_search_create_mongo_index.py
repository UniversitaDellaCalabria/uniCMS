from cms.search import mongo_collection

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.module_loading import import_string

from pymongo import TEXT


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
    help = 'uniCMS Search Pages Indexer'

    def add_arguments(self, parser):
        parser.epilog='Example: ./manage.py cms_search_create_mongo_index'
        parser.add_argument('-default_language', required=False,
                            default='italian',
                            help="default language for fulltext fields")
                            
    def handle(self, *args, **options):
        collection = mongo_collection()
        
        if confirm():
            # drop indexes
            print(f"Drop existing indexes in {collection}")
            collection.drop_indexes()
            
            # create index
            res2 = collection.create_index([('title', TEXT),
                             ('heading', TEXT),
                             ('content', TEXT),
                             ('translations.title', TEXT),
                             ('translations.heading', TEXT),
                             ('translations.content', TEXT),
                             ('year', 1)],
                             default_language=options["default_language"])
            
            print(f"Creating index: {res2}")
