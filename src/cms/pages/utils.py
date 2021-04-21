from django.utils import timezone


def copy_page_as_draft(obj):
    draft = obj.__dict__.copy()
    draft['state'] = 'draft'
    draft['draft_of'] = obj.pk
    for attr in "id pk _state created_by modified_by created modified".split(' '):
        if draft.get(attr):
            draft.pop(attr)

    # cleanup cached items
    data = {k:v for k,v in draft.items() if not k.startswith('_')}

    data['date_start'] = timezone.localtime()
    new_obj = obj.__class__.objects.create(**data)
    tags = [i for i in obj.tags.values_list('name', flat=1)]
    new_obj.tags.add(*tags)

    # now replicate all its childs and menus
    for i in ('pageblock_set', 'pagecarousel_set',
              'pagelink_set', 'pagemenu_set', 'pagepublication_set',
              'pagemedia_set', 'pagelocalization_set',
              'pageheading_set', 'pagemediacollection_set',
              # this is a related_name property on model
              'parent_page'):
        childs = getattr(obj, i).all()
        for child in childs:
            child.pk = None
            child.id = None
            child.page = new_obj
            child.save()
    return new_obj
