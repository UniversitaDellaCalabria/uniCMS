
from . models import EditorialBoardLockUser


class EditorialBoardLockProxy():

    @classmethod
    def obj_is_locked(cls, user, content_type, object_id):
        # check on redis first
        # check here...

        locks = EditorialBoardLockUser.get_object_locks(content_type=content_type,
                                                        object_id=object_id)
        if not locks: return {}
        if locks.filter(user=user): return {'locked_by_user': True}
        return {'locked_by_user': False}
