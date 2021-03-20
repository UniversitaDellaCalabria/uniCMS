
from django.db import models
from django.contrib.contenttypes.models import ContentType

from cms.api.utils import check_user_permission_on_object


class AbstractLockable(models.Model):

    def is_lockable_by(self, user):
        content_type = ContentType.objects.get_for_model(self)
        app_label = content_type.__dict__.get('app_label')
        model = content_type.__dict__.get('model')
        change_permission = f'{app_label}.change_{model}'
        permission = check_user_permission_on_object(user, self, change_permission)
        return permission['granted']

    class Meta:
        abstract = True
