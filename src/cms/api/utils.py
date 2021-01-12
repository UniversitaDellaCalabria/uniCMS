def check_permission(user, permission):
    """
    check if user has a specific permission
    """
    if not user.has_perm(permission):
        return False
    return True


def check_if_user_has_created(user, obj):
    """
    check if user has created an object
    """
    if not obj.created_by == user:
        return False
    return True


def check_user_permission_on_object(user, obj, permission):
    """
    check if user has a permission and has created an object
    """
    if user.is_superuser: return True
    return check_permission(user, permission) and check_if_user_has_created(user, obj)
