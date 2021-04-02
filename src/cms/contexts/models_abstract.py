from django.db import models

from cms.api.utils import check_user_permission_on_object


class AbstractLockable(models.Model):

    def is_lockable_by(self, user):
        permission = check_user_permission_on_object(user, self)
        return permission['granted']

    class Meta:
        abstract = True
