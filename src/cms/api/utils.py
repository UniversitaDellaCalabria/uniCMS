

def check_if_user_has_created(user, obj):
    """
    check if user has created an object
    """
    return obj.created_by == user


def check_user_permission_on_object(user, obj, permission):
    """
    check if user has a permission and has created an object
    """
    if user.is_superuser: return True
    # has_perm caches permissions!
    # https://docs.djangoproject.com/en/3.1/topics/auth/default/#permission-caching
    return user.has_perm(permission) and check_if_user_has_created(user, obj)
