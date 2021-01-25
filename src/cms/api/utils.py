from django.contrib.contenttypes.models import ContentType

# from cms.contexts.models import EditorialBoardLockUser
from cms.contexts.lock_proxy import EditorialBoardLockProxy


def check_if_user_has_created(user, obj):
    """
    check if user has created an object
    """
    return obj.created_by == user


def check_user_permission_on_object(user, obj, permission):
    """
    check if user has a permission and has created an object
    """
    # superuser have all permissions
    if user.is_superuser: return {'granted': True}
    # if not staff, no permission
    if not user.is_staff: return {'granted': False}

    # get Django permissions on object
    permission = user.has_perm(permission)

    # Django permissions required
    if not permission: return {'granted': False}
    # obj owner has permissions
    if check_if_user_has_created(user, obj): return {'granted': True}

    # check for locks on object
    content_type = ContentType.objects.get_for_model(obj.__class__)
    locks = EditorialBoardLockProxy.obj_is_locked(user=user,
                                                  content_type=content_type,
                                                  object_id=obj.pk)
    # if there is not lock, no permission
    if not locks: return {'granted': False}
    # if user is in lock user list, has permissions
    if locks['locked_by_user']: return {'granted': True, 'locked': True}
    # else no permissions but obj is locked
    return {'granted': False, 'locked':True}
