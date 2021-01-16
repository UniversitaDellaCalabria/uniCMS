from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models.fields.related import (ForeignKey, 
                                             OneToOneField,
                                             ManyToManyField)

from cms.contexts.models import EntryUsedBy
from taggit.managers import TaggableManager


def used_by(obj):
    user_model = get_user_model()
    excluded_types = (user_model, TaggableManager,)
    parents = []
    for field in obj._meta.fields:
        if type(field) in (ForeignKey, OneToOneField):
            parent = getattr(obj, field.name, None)
            if parent and parent.__class__ in excluded_types:
                parents.append(parent)
    for m2m in obj._meta.many_to_many:
        if m2m and m2m.__class__ not in excluded_types:
            entries = getattr(obj, m2m.name).all()
            for entry in entries:
                parents.append(entry)
    
    # TODO
    # inlines = []
    # for inline in obj._meta.related_objects:
        # if inline.model not in excluded_types:
            
    
    used_by_content_type = ContentType.objects.get_for_model(obj)
    already_used = EntryUsedBy.objects.filter(object_id=obj.pk,
                                              content_type=used_by_content_type)
    already_used.delete()
    for parent in parents:
        content_type = ContentType.objects.get_for_model(parent)
        entry_dict = dict(object_id=parent.pk,
                          content_type=content_type,
                          used_by_content_type=used_by_content_type,
                          used_by_object_id=obj.pk)
        
        already_used = EntryUsedBy.objects.filter(**entry_dict)
        if already_used: continue
        EntryUsedBy.objects.create(**entry_dict)
