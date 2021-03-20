from django.contrib.contenttypes.models import ContentType

from cms.contexts.models import EditorialBoardLockUser
# from cms.contexts.lock_proxy import EditorialBoardLockProxy


def check_user_permission_on_object(user, obj, permission='change'):
    """
    check if user has a permission and has created an object
    """

    # @to-do redis-lock

    # superuser have all permissions
    if user.is_superuser: return {'granted': True}
    # if not staff, no permission
    if not user.is_staff: return {'granted': False}

    # check for locks on object
    content_type = ContentType.objects.get_for_model(obj)
    app_name = content_type.__dict__['app_label']
    model = content_type.__dict__['model']

    # get Django permissions on object
    permission = user.has_perm(f'{app_name}.{permission}_{model}')

    # Django permissions required
    if not permission: return {'granted': False}
    # obj owner has permissions
    if obj.created_by == user: return {'granted': True}

    # locks = EditorialBoardLockProxy.obj_is_locked(user=user,
    # content_type=content_type,
    # object_id=obj.pk)
    locks = EditorialBoardLockUser.get_object_locks(content_type=content_type,
                                                    object_id=obj.pk)
    # if there is not lock, no permission
    if not locks: return {'granted': False}
    # if user is in lock user list, has permissions
    if locks.filter(user=user): return {'granted': True, 'locked': True}
    # else no permissions but obj is locked
    return {'granted': False, 'locked':True}
