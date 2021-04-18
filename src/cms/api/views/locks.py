from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.utils.translation import gettext_lazy as _

from cms.contexts.models import EditorialBoardLock, EditorialBoardLockUser
from cms.contexts.serializers import EditorialBoardLockUserSerializer

from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.views import APIView

from . generics import UniCMSListCreateAPIView
from .. concurrency import get_lock_from_cache, LOCK_MESSAGE
from .. exceptions import LoggedPermissionDenied


class ObjectUserLocksList(UniCMSListCreateAPIView):
    """
    """
    description = ""
    search_fields = ['user__first_name','user__last_name','user__email']
    filterset_fields = []
    serializer_class = EditorialBoardLockUserSerializer

    def get_queryset(self, **kwargs):
        """
        """
        object_id = self.kwargs.get('object_id', None)
        content_type_id = self.kwargs.get('content_type_id', None)
        if object_id and content_type_id:
            return EditorialBoardLockUser.get_object_locks(content_type=content_type_id,
                                                           object_id=object_id)
        return EditorialBoardLockUser.objects.none() # pragma: no cover

    def create(self, object_id, content_type, user):
        lock = EditorialBoardLock.objects.filter(content_type=content_type,
                                                 object_id=object_id).first()
        if not lock:
            lock = EditorialBoardLock.objects.create(content_type=content_type,
                                                     object_id=object_id)
        result = EditorialBoardLockUser.objects.create(lock=lock,
                                                       user=user)
        return result

    def post(self, request, *args, **kwargs):
        object_id = kwargs.get('object_id')
        content_type_id = kwargs.get('content_type_id')
        data = {'user': request.data.get('user'),
                'lock': {
                    'content_type': content_type_id,
                    'object_id': object_id
                }
            }
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data.get('user')
            content_type = ContentType.objects.get_for_id(content_type_id)
            obj = content_type.get_object_for_this_type(pk=object_id)

            if not hasattr(obj, 'is_lockable_by') or not obj.is_lockable_by(request.user):
                raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                             resource=request.method)
            existent = EditorialBoardLockUser.objects.filter(lock__content_type=content_type,
                                                             lock__object_id=object_id,
                                                             user=user).first()
            if existent:
                raise ValidationError({'Error message': _("This lock was already set")})
        new_lock = self.create(user=user,
                               content_type=content_type,
                               object_id=object_id)
        return Response(self.get_serializer(new_lock).data)


class ObjectUserLocksItemSchema(AutoSchema):
    def get_operation_id(self, path, method):# pragma: no cover
        if method == 'GET':
            return 'retrieveEditorialBoardLockUserItem'
        if method == 'DELETE':
            return 'deleteEditorialBoardLockUserItem'


class ObjectUserLocksView(generics.RetrieveDestroyAPIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]
    serializer_class = EditorialBoardLockUserSerializer
    schema = ObjectUserLocksItemSchema()

    def get_queryset(self):
        """
        """
        content_type_id = self.kwargs['content_type_id']
        object_id = self.kwargs['object_id']
        lock_id = self.kwargs['pk']
        locks = EditorialBoardLockUser.objects.filter(pk=lock_id,
                                                      lock__object_id=object_id,
                                                      lock__content_type__pk=content_type_id)
        return locks

    def delete(self, request, *args, **kwargs):
        items = self.get_queryset()
        if not items: raise Http404
        permission = False
        if request.user.is_superuser:
            permission = True
        else:
            user_lock = items.filter(user=request.user).first()
            if user_lock: permission = True
        if not permission:
            raise LoggedPermissionDenied(classname=self.__class__.__name__,
                                         resource=request.method)
        return super().delete(request, *args, **kwargs)


class RedisLockView(APIView):
    """
    """
    description = ""
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        content_type_id = self.kwargs['content_type_id']
        object_id = self.kwargs['object_id']
        lock = get_lock_from_cache(content_type_id, object_id)
        if lock[0] and not lock[0] == request.user.pk:
            owner_user = get_user_model().objects.filter(pk=lock[0]).first()
            return Response({'lock': lock,
                             'message': LOCK_MESSAGE.format(user=owner_user,
                                                            ttl=lock[1])})
        return Response({})
