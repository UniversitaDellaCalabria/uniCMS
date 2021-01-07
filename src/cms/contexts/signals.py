from cms.contexts.utils import load_hooks
from django.db.models.signals import (pre_save, post_save,
                                      pre_delete, post_delete)


def cms_pre_save(instance, *args, **kwargs):
    load_hooks(instance, 'PRESAVE', *args, **kwargs)


def cms_post_save(instance, *args, **kwargs):
    load_hooks(instance, 'POSTSAVE', *args, **kwargs)


def cms_pre_delete(instance, *args, **kwargs):
    load_hooks(instance, 'PREDELETE', *args, **kwargs)


def cms_post_delete(instance, *args, **kwargs):
    load_hooks(instance, 'POSTDELETE', *args, **kwargs)


# all the models will send signals here but ... Only who have some hook
# registered will turn on the lights
pre_save.connect(cms_pre_save)
post_save.connect(cms_post_save)
pre_delete.connect(cms_pre_delete)
post_delete.connect(cms_post_delete)
