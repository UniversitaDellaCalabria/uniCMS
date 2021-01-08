from cms.search import mongo_collection

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.module_loading import import_string
from django.apps import apps


class Command(BaseCommand):
    help = 'uniCMS Search Pages Indexer'

    def add_arguments(self, parser):
        parser.epilog = 'Example: ./manage.py cms_search -y 2020 [-m N] [-d N]'
        parser.add_argument('-type', type=str, required=False,
                            help="eg: cmspages.Page")
        parser.add_argument('-y', type=int, required=True,
                            help="Year, eg: 2020")
        parser.add_argument('-m', type=int, required=False,
                            help="Month, eg: 4")
        parser.add_argument('-d', type=int, required=False,
                            help="Day, eg: 12")
        parser.add_argument('-show', required=False, action="store_true",
                            help="it only print out the entries")
        parser.add_argument('-purge', required=False, action="store_true",
                            help="purge all the entries")
        parser.add_argument('-insert', required=False, action="store_true",
                            help="build entries indexes")
        parser.add_argument('-debug', required=False, action="store_true",
                            help="see debug messages")

    def handle(self, *args, **options):
        collection = mongo_collection()
        content_type = options['type']
        query = {'content_type': content_type} if content_type else {}

        for i in 'day', 'month', 'year':
            opt = i[0]
            if options.get(opt):
                query[i] = options[opt]

        # purge
        if options['purge']:
            del_res = collection.find(query)
            del_count = del_res.count()
            to_be_deleted = [i['_id'] for i in del_res]

        # rebuild
        data = []
        if options['insert']:
            app_label, model_name = content_type.split('.')
            # model = import_string(f'{app_label}.{model_name}')
            model = apps.get_model(app_label=app_label, model_name=model_name)
            _func = import_string(settings.MODEL_TO_MONGO_MAP[content_type])
            for obj in model.objects.filter(is_active=True):
                if obj.is_publicable:
                    entry = _func(obj)
                    data.append(entry)
            collection.insert_many(data, ordered=False)
            count = collection.find(query).count()
            print(f'-- Inserted {len(data)} elements. --')

        # purge
        if options['purge']:
            del_query = query.copy()
            del_query.update({"_id": {"$in" : to_be_deleted}})
            collection.delete_many(del_query)
            print(f'-- Deleted {del_count} elements. --')

        # show
        if options['show']:
            count = collection.find(query).count()
            for i in collection.find(query):
                print(i)
            print(f'-- {count} elements. --')
